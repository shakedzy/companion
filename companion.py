import re
import os
import sys
import json
import signal
import pygame
import argparse
from typing import Optional
from queue import Empty as EmptyQueue
from threading import Thread
from flask import Flask, render_template, request, jsonify
from python import speech
from python.memory import Memory
from python.config import Config
from python.chatbot import Chatbot
from python.app_cache import AppCache
from python.language import translate, is_text_of_language


TEMP_DIR = os.path.join(os.getcwd(), "tmp")
LTM_DIR = os.path.join(os.getcwd(), "ltm")  # Long Term Memory
SAVED_SESSION_FILE = os.path.join(LTM_DIR, "last_session.json")

app = Flask(__name__)

config: Optional[Config] = None
memory: Optional[Memory] = None
chatbot: Optional[Chatbot] = None
app_cache = AppCache()


@app.route('/')
def home():
    global memory, chatbot
    memory = Memory()
    chatbot = Chatbot(config=config, memory=memory)

    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))
    else:
        os.makedirs(TEMP_DIR)

    if not os.path.exists(LTM_DIR):
        os.makedirs(LTM_DIR)

    languages = [config.language.learning, config.language.native, 'A']
    return render_template('index.html', languages=languages,
                           auto_send_recording=int(config.behavior.auto_send_recording),
                           user_profile_img=config.user.image, bot_profile_img=config.bot.image)


@app.route('/get_response', methods=['POST'])
def get_response():
    is_initial_message = bool(int(request.form['is_initial_message']))
    app_cache.message_generator = chatbot.get_response(is_initial_message)
    app_cache.last_sentence = ''
    app_cache.sentences_counter = 0
    app_cache.bot_recordings = list()
    first_message = next(app_cache.message_generator)
    app_cache.generated_message = first_message
    return jsonify({'message': first_message,
                    'message_index': len(memory)})


@app.route('/get_next_message', methods=['POST'])
def get_next_message():
    index = int(request.form['message_index'])
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
                                             "message_index": index})
            app_cache.sentences_counter += 1
            app_cache.last_sentence = split_sentence[1]
        return jsonify({'message': app_cache.generated_message})
    except StopIteration:
        if app_cache.last_sentence.strip() != '':
            app_cache.text2speech_queue.put({"text": app_cache.last_sentence,
                                             "counter": app_cache.sentences_counter,
                                             "message_index": index})
        store_message(sender="assistant", message=app_cache.generated_message)
        app_cache.message_generator = None
        app_cache.generated_message = ''
        return jsonify({'message': None})


def split_to_sentences(text):
    """
    This function MUST return a list of only one or two elements
    """
    characters = [c+' ' for c in ['.', '!', "?", ":", ";"]]
    escaped_characters = [re.escape(c) for c in characters]
    if any([c in text for c in characters]):
        pattern = '|'.join(escaped_characters)
        split_list = re.split(pattern, text)
    elif '\n' in text:
        lst = text.split('\n')
        lst = [s for s in lst if len(s.strip()) > 0]
        if len(lst) > 1:
            split_list = [lst[0], "\n".join(lst[1:])]
        else:
            split_list = lst
    elif ', ' in text and len(text) > 100:
        lst = re.split(re.escape(',') + r'\s', text)
        split_list = [lst[0], ", ".join(lst[1:])]
    else:
        split_list = [text]
    return split_list


@app.route('/start_recording', methods=['POST'])
def start_recording():
    filename = os.path.join(TEMP_DIR, f"user_recording_{len(memory)}.mp3")
    app_cache.user_recording = filename
    app_cache.recording_thread = Thread(target=speech.record, args=(filename,))
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
               recording=app_cache.bot_recordings if sender == "assistant" else [])
    app_cache.user_recording = None
    return jsonify({'status': 'success'})


@app.route('/user_message_info', methods=['POST'])
def user_message_info():
    message = request.form['message']
    is_language_learning = is_text_of_language(message, config.language.learning)
    return jsonify({'user_recording': app_cache.user_recording,
                    'is_language_learning': is_language_learning})


@app.route('/play_bot_recording', methods=['POST'])
def play_bot_message():
    index = int(request.form['message_id'].split('_')[1])
    recordings = memory[index]["recording"]
    if recordings is None or len(recordings) == 0:
        app_cache.text2speech_queue.put({"text": request.form["text"], "counter": 0,
                                         "message_index": index, 'skip_cache': True})
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
    sender = request.form["sender"]
    lang = config.language.native if sender == "assistant" else config.language.learning
    translated = translate(message, to=lang)
    return jsonify({'message': translated})


@app.route('/save_session', methods=['GET'])
def save_session():
    data = list()
    for m in memory.get_chat_history()[1:]:
        data.append({"role": m["role"], "content": m["content"]})

    json_data = json.dumps(data, indent=4)  # Convert the list of dictionaries to JSON format

    with open(SAVED_SESSION_FILE, "w") as f:
        f.write(json_data)

    return jsonify({"message": "session saved successfully"})


@app.route('/load_session', methods=['GET'])
def load_session():
    global memory, chatbot
    if os.path.isfile(SAVED_SESSION_FILE):
        with open(SAVED_SESSION_FILE, 'r') as f:
            messages = json.load(f)

            memory = Memory()
            chatbot = Chatbot(config=config, memory=memory)

            for message in messages:
                memory.add(role=message["role"], message=message["content"])
                if message["role"] == "user":
                    message["is_language_learning"] = is_text_of_language(message["content"], config.language.learning)
                else:
                    message["is_language_learning"] = True

    else:
        messages = []

    return jsonify({"messages": messages})


@app.route('/memory', methods=['GET'])
def print_memory():
    return json.dumps(memory.list, indent=4)


@app.route('/memory/updates', methods=['GET'])
def print_memory_updates():
    return json.dumps(memory._updates, indent=4)


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
            if item.get('skip_cache', False):
                memory.update(idx, recording=[filename])
            else:
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


def exit_graceful(signum, frame):
    app_cache.stop_threads_event.set()
    speech.stop_recording()
    for thread in [app_cache.text2speech_thread, app_cache.recording_thread, app_cache.play_recordings_thread]:
        if thread is not None:
            thread.join()
    sys.exit(0)


def run(config_file):
    global config
    config = Config.from_yml_file(config_file)

    speech.init_google_text_to_speech(config=config)

    app_cache.text2speech_thread = Thread(target=bot_text_to_speech_queue_func)
    app_cache.text2speech_thread.start()
    app_cache.play_recordings_thread = Thread(target=play_recordings_queue_func)
    app_cache.play_recordings_thread.start()

    app.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='config_file', default='config.yml', help='The config yaml file.')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, exit_graceful)
    signal.signal(signal.SIGTERM, exit_graceful)
    run(args.config_file)
