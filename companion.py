import os
import sys
import json
import signal
import argparse
from typing import Optional
from threading import Thread
from flask import Flask, render_template, request, jsonify
from python import speech, language, utils, threads
from python.memory import Memory
from python.config import Config
from python.chatbot import Chatbot
from python.app_cache import AppCache


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

    if os.path.exists(utils.TEMP_DIR):
        for f in os.listdir(utils.TEMP_DIR):
            os.remove(os.path.join(utils.TEMP_DIR, f))
    else:
        os.makedirs(utils.TEMP_DIR)

    if not os.path.exists(utils.LTM_DIR):
        os.makedirs(utils.LTM_DIR)

    languages = [config.language.learning, config.language.native, 'A']
    return render_template('index.html', languages=languages,
                           auto_send_recording=int(config.behavior.auto_send_recording),
                           user_profile_img=config.user.image, bot_profile_img=config.bot.image)


@app.route('/get_response', methods=['POST'])
def get_response():
    error_message = None
    first_message = ''
    try:
        is_initial_message = bool(int(request.form['is_initial_message']))
        app_cache.message_generator = chatbot.get_response(is_initial_message)
        app_cache.last_sentence = ''
        app_cache.sentences_counter = 0
        app_cache.bot_recordings = list()
        first_message = next(app_cache.message_generator)
        app_cache.generated_message = first_message
    except Exception as e:
        error_message = utils.get_error_message_from_exception(e)
    finally:
        return jsonify({'message': first_message,
                        'message_index': len(memory),
                        'error': error_message})


@app.route('/get_next_message', methods=['POST'])
def get_next_message():
    index = int(request.form['message_index'])
    if app_cache.message_generator is None:
        return jsonify({'message': None})
    try:
        next_message = next(app_cache.message_generator)
        app_cache.generated_message += next_message
        app_cache.last_sentence += next_message
        split_sentence = utils.split_to_sentences(app_cache.last_sentence)
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


@app.route('/start_recording', methods=['POST'])
def start_recording():
    filename = os.path.join(utils.TEMP_DIR, f"user_recording_{len(memory)}.mp3")
    app_cache.user_recording = filename
    app_cache.recording_thread = Thread(target=speech.record, args=(filename,))
    app_cache.recording_thread.start()
    return jsonify({'message': 'Recording started'})


@app.route('/end_recording', methods=['POST'])
def end_recording():
    speech.stop_recording()
    app_cache.recording_thread.join()

    recorded_text = None
    error_message = None
    try:
        recorded_text = speech.speech2text(app_cache.user_recording, language=app_cache.language)
    except Exception as e:
        error_message = utils.get_error_message_from_exception(e)
    finally:
        return jsonify({'recorded_text': recorded_text,
                        'error': error_message})


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
    error_message = None
    message = request.form['message']
    try:
        is_language_learning = language.is_text_of_language(message, config.language.learning)
    except Exception as e:
        is_language_learning = False
        error_message = utils.get_error_message_from_exception(e)
    return jsonify({'user_recording': app_cache.user_recording,
                    'is_language_learning': is_language_learning,
                    'error': error_message})


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
    try:
        translated = language.translate(message, to=lang)
    except Exception as e:
        app_cache.server_errors.append(utils.get_error_message_from_exception(e))
        translated = None
    return jsonify({'message': translated})


@app.route('/save_session', methods=['GET'])
def save_session():
    data = list()
    for m in memory.get_chat_history()[1:]:
        data.append({"role": m["role"], "content": m["content"]})

    json_data = json.dumps(data, indent=4)  # Convert the list of dictionaries to JSON format

    with open(utils.SAVED_SESSION_FILE, "w") as f:
        f.write(json_data)

    return jsonify({"success": True})


@app.route('/load_session', methods=['GET'])
def load_session():
    global memory, chatbot
    if os.path.isfile(utils.SAVED_SESSION_FILE):
        with open(utils.SAVED_SESSION_FILE, 'r') as f:
            messages = json.load(f)

            memory = Memory()
            chatbot = Chatbot(config=config, memory=memory)

            for message in messages:
                memory.add(role=message["role"], message=message["content"])
                if message["role"] == "user":
                    try:
                        message["is_language_learning"] = language.is_text_of_language(message["content"], config.language.learning)
                    except Exception as e:
                        message["is_language_learning"] = False
                        app_cache.server_errors.append(utils.get_error_message_from_exception(e))
                else:
                    message["is_language_learning"] = True

    else:
        messages = []

    return jsonify({"messages": messages})


@app.route('/check_server_errors', methods=['GET'])
def check_server_errors():
    server_errors = app_cache.server_errors.copy()
    app_cache.server_errors = []
    return jsonify({'server_errors': server_errors})


@app.route('/memory', methods=['GET'])
def print_memory():
    return json.dumps(memory.list, indent=4)


@app.route('/memory/updates', methods=['GET'])
def print_memory_updates():
    return json.dumps(memory._updates, indent=4)


def exit_graceful(signum, frame):
    app_cache.stop_threads_event.set()
    speech.stop_recording()
    for thread in [app_cache.text2speech_thread, app_cache.recording_thread, app_cache.play_recordings_thread]:
        if thread is not None:
            thread.join()
    sys.exit(0)


def refresh():
    global memory, chatbot
    memory = Memory()
    chatbot = Chatbot(config=config, memory=memory)

    if os.path.exists(utils.TEMP_DIR):
        for f in os.listdir(utils.TEMP_DIR):
            os.remove(os.path.join(utils.TEMP_DIR, f))
    else:
        os.makedirs(utils.TEMP_DIR)


def run(config_file, keys_file=None):
    global config
    config = Config.from_yml_file(config_file)
    if keys_file:
        config.update_from_yml_file(keys_file)

    utils.init_openai(config)
    gcs_creds = utils.get_gcs_credentials(config)
    language.init_language(credentials=gcs_creds)
    speech.init_speech(config=config, credentials=gcs_creds)

    threads.init_threads(config, memory, app_cache)

    app.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='config_file', default='config.yml', help='A config yml file.')
    parser.add_argument('-k', '--keys', dest='keys_file', help='A keys yml file [optional].')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, exit_graceful)
    signal.signal(signal.SIGTERM, exit_graceful)
    run(args.config_file, args.keys_file)
