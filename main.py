import re
import os
import yaml
import json
import atexit
import speech
import pygame
from queue import Empty as EmptyQueue
from threading import Thread
from flask import Flask, Response, render_template, request, jsonify
from memory import Memory
from config import Config
from chatbot import Chatbot
from app_cache import AppCache
from translate import translate
from datetime import datetime

TEMP_DIR = os.path.join(os.getcwd(), "tmp")

app = Flask(__name__)

with open("config.yml", "r") as yml_file:
    config: Config = Config(yaml.safe_load(yml_file))
memory = Memory()
chatbot = Chatbot(config=config, memory=memory)
app_cache = AppCache()


@app.route('/')
def home():
    languages = [config.language.learning, config.language.native, 'A']
    return render_template('index.html', page_title=config.title, languages=languages)


@app.route('/get_response', methods=['POST'])
def get_response():
    app_cache.message_generator = chatbot.get_response()
    app_cache.last_sentence = ''
    app_cache.sentences_counter = 0
    app_cache.bot_recordings = list()
    first_message = next(app_cache.message_generator)
    app_cache.generated_message = first_message
    return jsonify({'message': first_message})


@app.route('/get_next_message', methods=['GET'])
def get_next_message():
    if app_cache.message_generator is None:
        return jsonify({'message': None})
    try:
        next_message = next(app_cache.message_generator)
        app_cache.generated_message += next_message
        app_cache.last_sentence += next_message
        split_sentence = split_to_sentences(app_cache.last_sentence)
        if len(split_sentence) > 1:
            app_cache.text2speech_queue.put({"text": split_sentence[0],
                                             "counter": app_cache.sentences_counter,
                                             "message_index": len(memory)})
            app_cache.sentences_counter += 1
            app_cache.last_sentence = split_sentence[1]
        return jsonify({'message': app_cache.generated_message})
    except StopIteration:
        if app_cache.last_sentence.strip() != '':
            app_cache.text2speech_queue.put({"text": app_cache.last_sentence,
                                             "counter": app_cache.sentences_counter,
                                             "message_index": len(memory)})
        store_message(sender="assistant", message=app_cache.generated_message)
        app_cache.message_generator = None
        app_cache.generated_message = ''
        return jsonify({'message': None})


def split_to_sentences(text):
    characters = ['.', '!', "?", ":", ";"]
    escaped_characters = [re.escape(c) for c in characters]
    if any([c+' ' in text for c in characters]):
        pattern = '|'.join(escaped_characters)
        split_list = re.split(pattern + r'\s', text)
    elif ', ' in text and len(text) > 100:
        print(f"<{text}>")
        split_list = re.split(re.escape(',') + r'\s', text)
    else:
        split_list = [text]
    return split_list


@app.route('/start_recording', methods=['POST'])
def start_recording():
    filename = os.path.join(TEMP_DIR, f"user_recording_{len(memory)}.mp3")
    app_cache.user_recording = filename
    app_cache.recording_thread = Thread(target=speech.record, args=(filename, ))
    app_cache.recording_thread.start()
    return jsonify({'message': 'Recording started'})

@app.route('/end_recording', methods=['POST'])
def end_recording():
    speech.stop_recording()
    app_cache.recording_thread.join()
    recorded_text = speech.speech2text(app_cache.user_recording, language=app_cache.language)
    return jsonify({'recorded_text': recorded_text})

@app.route('/store_message', methods=['POST'])
def store_message(sender=None, message=None):
    sender = sender or request.form['sender']
    message = message or request.form['message']
    memory.add(role=sender, message=message, user_recording=app_cache.user_recording,
               recording=app_cache.bot_recordings)
    app_cache.user_recording = None
    return jsonify({'status': 'success'})


@app.route('/has_user_recording', methods=['GET'])
def has_user_recording():
    return jsonify({'user_recording': app_cache.user_recording})


@app.route('/toggle_loading_icon', methods=['POST'])
def toggle_loading_icon():
    action = request.form.get('action')
    return jsonify({'action': action})


@app.route('/play_bot_recording', methods=['POST'])
def play_bot_message():
    index = int(request.form['message_id'].split('_')[1])
    recordings = memory[index]["recording"]
    if recordings is None or len(recordings) == 0:
        app_cache.text2speech_queue.put({"text": request.form["text"], "counter": 0,
                                         "message_index": index})
    else:
        for r in recordings:
            app_cache.play_recordings_queue.put(r)
    return jsonify({'message': 'Recordings inserted to queue'})


@app.route('/play_user_recording', methods=['POST'])
def play_user_message():
    message_id = int(request.form['message_id'].split('_')[1])
    user_recording = memory[message_id]['user_recording']
    if user_recording:
        app_cache.play_recordings_queue.put(user_recording)
    return jsonify({'message': 'User message played successfully'})


@app.route('/set_language', methods=['POST'])
def set_language():
    language = request.form['language']
    if language == 'A':
        language = None
    app_cache.language = language
    return jsonify({'message': f'Language set successfully to {request.form["language"]}'})


@app.route('/translate_text', methods=['POST'])
def translate_text():
    message = request.form["text"]
    translated = translate(message, to=config.language.native)
    print(translated)
    return jsonify({'message': translated})


@app.route('/download_chat', methods=['GET'])
def download_chat():
    filename = f"chat_history_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"
    data = list()
    for i, m in enumerate(memory.get_chat_history()[1:]):
        data.append({"index": i+1, "sender": m["role"], "message": m["content"]})

    json_data = json.dumps(data, indent=4)  # Convert the list of dictionaries to JSON format

    response = Response(
        response=json_data,
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

    return response


@app.route('/memory', methods=['GET'])
def print_memory():
    return str(memory)

@app.route('/memory/updates', methods=['GET'])
def print_memory_updates():
    return str(memory._updates)


def bot_text_to_speech(text, message_index, counter):
    filename = os.path.join(TEMP_DIR, f"bot_speech_{message_index}_{counter}.mp3")
    speech.text2speech(text, filename, config=config)
    return filename


def bot_text_to_speech_queue_func():
    while not app_cache.stop_threads_event.is_set():
        try:
            item = app_cache.text2speech_queue.get(timeout=1)  # Wait for 1 second to get an item
            idx = item["message_index"]
            filename = bot_text_to_speech(text=item['text'], message_index=idx, counter=item['counter'])
            app_cache.bot_recordings.append(filename)
            memory.update(idx, recording=app_cache.bot_recordings)
            app_cache.play_recordings_queue.put(filename)
        except EmptyQueue:
            continue


def play_recordings_queue_func():
    while not app_cache.stop_threads_event.is_set():
        try:
            filename = app_cache.play_recordings_queue.get(timeout=1)  # Wait for 1 second to get an item
            speech.play_mp3(filename)
            while pygame.mixer.music.get_busy():
                continue
        except EmptyQueue:
            continue


@atexit.register
def on_exit():
    print("Terminating...")
    app_cache.stop_threads_event.set()
    speech.stop_recording()
    for thread in [app_cache.text2speech_thread, app_cache.recording_thread, app_cache.play_recordings_thread]:
        thread.join()


if __name__ == '__main__':
    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))
    else:
        os.makedirs(TEMP_DIR)

    app_cache.text2speech_thread = Thread(target=bot_text_to_speech_queue_func)
    app_cache.text2speech_thread.start()
    app_cache.play_recordings_thread = Thread(target=play_recordings_queue_func)
    app_cache.play_recordings_thread.start()

    app.run(debug=True)
