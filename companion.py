import os
import sys
import json
import yaml
import signal
import argparse
from typing import Optional
from threading import Thread
from unidecode import unidecode
from flask import Flask, render_template, request, jsonify, url_for, redirect
from queue import Empty as EmptyQueue
from python import speech, language, utils
from python.memory import Memory
from python.config import Config
from python.chatbot import Chatbot
from python.app_cache import AppCache
from python.consts import TEMP_DIR_NAME, TEMP_DIR, LTM_DIR, SAVED_SESSION_FILE, MALE_TUTORS, FEMALE_TUTORS, INPUT_LANGUAGES


app = Flask(__name__)

config: Optional[Config] = None
memory: Optional[Memory] = None
chatbot: Optional[Chatbot] = None
app_cache = AppCache()
voices_by_features = dict()
audio_queue_reject_remaining_fragments = False


@app.template_filter('convert_special')
def convert_special_letters(input_str):
    return unidecode(input_str)


@app.route('/')
def home():
    """
    Homepage of web UI
    """
    global memory, chatbot, config

    should_restart = bool(request.args.get('restart', 0))
    if should_restart:
        restart()

    memory = Memory()
    try:
        chatbot = Chatbot(config=config, memory=memory)
        languages = [config.language.learning, config.language.native, 'A']
        auto_send_recording = int(config.behavior.auto_send_recording)
        user_profile_img = config.user.image
        bot_profile_img = config.bot.image
    except Exception as e:
        languages = ['A']
        auto_send_recording = 0
        app_cache.server_errors.append(utils.get_error_message_from_exception(e))
        user_profile_img = ''
        bot_profile_img = ''

    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))
    else:
        os.makedirs(TEMP_DIR)

    if not os.path.exists(LTM_DIR):
        os.makedirs(LTM_DIR)

    return render_template('index.html', languages=languages, auto_send_recording=auto_send_recording,
                           user_profile_img=user_profile_img, bot_profile_img=bot_profile_img)


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """
    Web page, setup page
    """
    if request.method == 'POST':
        filename = request.form.get('filename')
        app_cache.config_file = filename
        data = {
            "model": {
                "name": request.form.get('model-name'),
                "temperature": float(request.form.get('temperature'))
            },
            "user": {
                "name": request.form.get('user-name'),
                "image": request.form.get('profile-img-url'),
                "gender": request.form.get('gender')
            },
            "bot": {
                "name": request.form.get('tutor').split("-")[0],
                "image": f"/static/bots_profile/{request.form.get('tutor').split('-')[0].lower()}.png",
                "gender": request.form.get('tutor').split("-")[1].lower(),
                "voice": request.form.get('voices-dropdown')
            },
            "language": {
                "native": request.form.get('user-lang-dropdown').lower(),
                "learning": request.form.get('tutor-lang-dropdown').split("-")[0].lower(),
                "level": request.form.get('lang-level')
            },
            "behavior": {
                "auto_send_recording": bool(request.form.get('auto-send-switch'))
            }
        }
        with open(os.path.join(os.getcwd(), filename), 'w') as outfile:
            yaml.dump(data, outfile, allow_unicode=True)
        return jsonify({'status': 'success'})

    else:
        return render_template('setup.html', males=MALE_TUTORS, females=FEMALE_TUTORS,
                               input_languages_codes_and_names=[[language.language_name_to_iso6391(lang), lang]
                                                                for lang in INPUT_LANGUAGES],
                               output_languages_locales_and_names=[[k, language.locale_code_to_language(k, name_in_same_language=True)]
                                                                   for k in voices_by_features.keys()]
                               )

@app.route("/get_next_from_audio_queue", methods=['GET'])
def get_next_from_audio_queue():
    try:
        filename = app_cache.play_recordings_queue.get(timeout=1)
        filename = url_for('static', filename=f'{TEMP_DIR_NAME}/{filename.split("/")[-1]}')
        empty = False
    except EmptyQueue:
        filename = None
        empty = True
    return jsonify({'file_url': filename, 'empty': int(empty)})


@app.route("/clear_audio_queue", methods=['GET'])
def clear_audio_queue():
    global audio_queue_reject_remaining_fragments
    audio_queue_reject_remaining_fragments = True
    app_cache.play_recordings_queue.queue.clear()
    return jsonify({'message': 'Audio cache cleared'})


def put_in_audio_queue(filename: str) -> bool:
    """
    Helper function to put filename in audio queue

    :param filename: filename to put in queue
    """
    global audio_queue_reject_remaining_fragments
    if audio_queue_reject_remaining_fragments:
        fragment_index = int(filename.split('_')[-1].split('.')[0])
        if fragment_index > 0:
            return False
        else:
            audio_queue_reject_remaining_fragments = False
    app_cache.play_recordings_queue.put(filename)
    return True


@app.route('/upload_recording', methods=['POST'])
def upload_recording():
    return_json = dict()
    if 'file' in request.files:
        file = request.files['file']
        raw_recording_filename = os.path.join(TEMP_DIR, "raw_recording")
        file.save(raw_recording_filename)
        try:
            mp3_filename = os.path.join(TEMP_DIR, f"user_recording_{len(memory)}_0.mp3")
            utils.convert_file_and_save_as_mp3(raw_recording_filename, mp3_filename)
        except Exception as e:
            app_cache.server_errors.append(utils.get_error_message_from_exception(e))
            mp3_filename = None
        return_json['filename'] = mp3_filename
    else:
        return_json['filename'] = None
    return jsonify(return_json)


@app.route('/get_language_voices', methods=['POST'])
def get_language_voices():
    """
    Get supported voices by TTS
    """
    lang_locale = request.form['language']
    gender = request.form['gender'].lower()
    voices = voices_by_features.get(lang_locale, {}).get(gender, [])
    return jsonify({'voices': voices})


@app.route('/play_bot_test_text', methods=['POST'])
def play_bot_test_text():
    """
    Play testing text-to-speech text from setup page
    """
    text = request.form['text']
    lang_code = request.form['lang']
    voice_name = request.form['voice']
    voice = speech.get_voice_object(voice_name=voice_name, language_code=lang_code)
    filename = utils.bot_text_to_speech(text, 0, 0, voice=voice)
    return jsonify({'file_url': url_for('static', filename=f'{TEMP_DIR_NAME}/{filename.split("/")[-1]}')})


@app.route('/get_response', methods=['POST'])
def get_response():
    """
    Get response from chatbot
    """
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
    """
    Helper endpoint for '/get_response', to handle the generator yielded by the chatbot.
    It returns the next characters in generator till it is consumed.
    """
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


@app.route('/transcribe_recording', methods=['POST'])
def transcribe_recording():
    """
    Transcribe user recording using speech-to-text service
    """
    recorded_text = None
    error_message = None
    filename = request.form['filename']
    try:
        recorded_text = speech.speech2text(filename, language=app_cache.language)
    except Exception as e:
        error_message = utils.get_error_message_from_exception(e)
    finally:
        return jsonify({'recorded_text': recorded_text,
                        'error': error_message})


@app.route('/store_message', methods=['POST'])
def store_message(sender: Optional[str] = None, message: Optional[str] = None):
    """
    Save message in memory

    :param sender: role of message creator ("system", "user" or "assistant")
    :param message: message text
    """
    sender = sender or request.form['sender']
    message = message or request.form['message']
    memory.add(role=sender, message=message, user_recording=app_cache.user_recording,
               recording=app_cache.bot_recordings if sender == "assistant" else [])
    app_cache.user_recording = None
    return jsonify({'status': 'success'})


@app.route('/user_message_info', methods=['POST'])
def user_message_info():
    """
    Get metadata regarding user message. This is required for tbe frontend.
    """
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
    """
    Play selected message's bot recording if exists. If not, send text to TTS and play audio
    """
    index = int(request.form['message_id'].split('_')[1])
    recordings = memory[index]["recording"]
    if recordings is None or len(recordings) == 0:
        app_cache.text2speech_queue.put({"text": request.form["text"], "counter": 0,
                                         "message_index": index, 'skip_cache': True})
    else:
        for r in recordings:
            put_in_audio_queue(r)
    return jsonify({'message': 'Recordings inserted to queue'})


@app.route('/play_user_recording', methods=['POST'])
def play_user_message():
    """
    Play user recording if exists
    """
    message_id = int(request.form['message_id'].split('_')[1])
    user_recording = memory[message_id]['user_recording']
    if user_recording:
        put_in_audio_queue(user_recording)
    return jsonify({'message': 'User message played successfully'})


@app.route('/set_language', methods=['POST'])
def set_language():
    """
    Set user recording language
    """
    language = request.form['language']
    if language == 'A':
        language = None
    app_cache.language = language
    return jsonify({'message': f'Language set successfully to {request.form["language"]}'})


@app.route('/translate_text', methods=['POST'])
def translate_text():
    """
    Translate message
    """
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
    """
    Save current session as file
    """
    data = list()
    for m in memory.get_chat_history()[1:]:
        data.append({"role": m["role"], "content": m["content"]})

    json_data = json.dumps(data, indent=4)  # Convert the list of dictionaries to JSON format

    with open(SAVED_SESSION_FILE, "w") as f:
        f.write(json_data)

    return jsonify({"success": True})


@app.route('/load_session', methods=['GET'])
def load_session():
    """
    Load session from file
    """
    global memory, chatbot
    if os.path.isfile(SAVED_SESSION_FILE):
        with open(SAVED_SESSION_FILE, 'r') as f:
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
    """
    Check for errors saved in `app_cache`, and display on web UI
    """
    server_errors = app_cache.server_errors.copy()
    app_cache.server_errors = []
    return jsonify({'server_errors': server_errors})


@app.route('/memory', methods=['GET'])
def print_memory():
    """
    Helper endpoint for debugging. Print memory.
    """
    return json.dumps(memory.list, indent=4)


@app.route('/memory/updates', methods=['GET'])
def print_memory_updates():
    """
    Helper endpoint for debugging. Print memory updates.
    """
    return json.dumps(memory.updates, indent=4)


def exit_graceful(signum, frame) -> None:
    """
    Stop threads when app terminates.

    :param signum: required by `signal.signal`
    :param frame: required by `signal.signal`
    """
    app_cache.stop_threads_event.set()
    if app_cache.text2speech_thread is not None:
        app_cache.text2speech_thread.join()
    sys.exit(0)


def restart() -> None:
    """
    Restart app
    """
    global config
    try:
        config = Config.from_yml_file(app_cache.config_file)
    except FileNotFoundError:
        app_cache.server_errors.append("Config file not found. Go to /setup to configure the app.")
        config = Config({'bot': {'voice': 'xx-xx'}})

    if app_cache.keys_file:
        config.update_from_yml_file(app_cache.keys_file)

    openai_client = utils.init_openai(config)
    config.update(openai={'client': openai_client})
    
    gcs_creds = utils.get_gcs_credentials(config)
    language.init_language(credentials=gcs_creds)
    speech.init_speech(config=config, credentials=gcs_creds)


def run() -> None:
    """
    Run app
    """
    global voices_by_features
    restart()
    voices_by_features = speech.voices_by_features()
    app_cache.text2speech_thread = Thread(target=bot_text_to_speech_queue_func)
    app_cache.text2speech_thread.start()

    app.run()


########## THREADS ##########

def bot_text_to_speech_queue_func():
    """
    This function is meant to run on a parallel thread.
    It is responsible to send texts to the TTS service, and then place the filename in a different queue,
    in order to be played
    """
    global config, memory, app_cache
    while not app_cache.stop_threads_event.is_set():
        try:
            item = app_cache.text2speech_queue.get(timeout=1)  # Wait for 1 second to get an item
            idx = item["message_index"]
            filename = utils.bot_text_to_speech(text=item['text'], message_index=idx, counter=item['counter'])
            if item.get('skip_cache', False):
                memory.update(idx, recording=[filename])
            else:
                app_cache.bot_recordings.append(filename)
                memory.update(idx, recording=app_cache.bot_recordings)
            put_in_audio_queue(filename)

        except EmptyQueue:
            continue
        except Exception as e:
            app_cache.server_errors.append(utils.get_error_message_from_exception(e))


#############################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='config_file', default='config.yml', help='A config yml file.')
    parser.add_argument('-k', '--keys', dest='keys_file', help='A keys yml file [optional].')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, exit_graceful)
    signal.signal(signal.SIGTERM, exit_graceful)
    app_cache.config_file = args.config_file
    app_cache.keys_file = args.keys_file
    run()
