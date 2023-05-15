import os
import yaml
import speech
import threading
from flask import Flask, render_template, request, jsonify
from memory import Memory
from config import Config
from chatbot import Chatbot

TEMP_DIR = os.path.join(os.getcwd(), "tmp")

app = Flask(__name__)

with open("config.yml", "r") as yml_file:
    config: Config = Config(yaml.safe_load(yml_file))
memory = Memory()
chatbot = Chatbot(config=config, memory=memory)

class AppCache:
    message_generator = None
    generated_message = ''
    user_recording = None
    recording_thread: threading.Thread = None

app_cache = AppCache()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global app_cache
    message = request.form['message']
    app_cache.message_generator = chatbot.get_response(message)
    first_message = next(app_cache.message_generator)
    app_cache.generated_message = first_message
    return jsonify({'message': first_message})

@app.route('/get_next_message', methods=['GET'])
def get_next_message():
    global app_cache
    if app_cache.message_generator is None:
        return jsonify({'message': None})
    try:
        next_message = next(app_cache.message_generator)
        app_cache.generated_message += next_message
        return jsonify({'message': app_cache.generated_message})
    except StopIteration:
        store_message(sender="assistant", message=app_cache.generated_message)
        app_cache.message_generator = None
        app_cache.generated_message = ''
        return jsonify({'message': None})

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global memory, app_cache
    filename = os.path.join(TEMP_DIR, f"user_recording_{len(memory)}.mp3")
    app_cache.user_recording = filename
    app_cache.recording_thread = threading.Thread(target=speech.record, args=(filename, ))
    app_cache.recording_thread.start()
    return jsonify({'message': 'Recording started'})

@app.route('/end_recording', methods=['POST'])
def end_recording():
    speech.stop_recording()
    app_cache.recording_thread.join()
    recorded_text = speech.speech2text(app_cache.user_recording)
    return jsonify({'recorded_text': recorded_text})

# @app.route('/print_message', methods=['POST'])
# def print_message():
#     message = request.form['message']
#     print(message)
#     return jsonify({'status': 'success'})

@app.route('/store_message', methods=['POST'])
def store_message(sender=None, message=None):
    global memory, app_cache
    sender = sender or request.form['sender']
    message = message or request.form['message']
    memory.add(role=sender, message=message, user_recording=app_cache.user_recording)
    app_cache.user_recording = None
    return jsonify({'status': 'success'})

@app.route('/toggle_loading_icon', methods=['POST'])
def toggle_loading_icon():
    action = request.form.get('action')
    return jsonify({'action': action})

@app.route('/play_user_message', methods=['POST'])
def play_user_message():
    message = request.form['message']
    print(f"Playing user message: {message}")
    return jsonify({'message': 'User message played successfully'})

@app.route('/set_language', methods=['POST'])
def set_language():
    language = request.form['language']
    print("Setting language to:", language)
    # Replace with your own logic
    return jsonify({'message': 'Language set successfully'})

@app.route('/play_bot', methods=['GET'])
def play_bot():
    global memory
    filename = os.path.join(TEMP_DIR, f"bot_speech_{len(memory)-1}.mp3")
    speech.text2speech(memory[len(memory)-1]["content"], filename)
    speech.play_mp3(filename)
    return jsonify({'message': 'Bot sound played'})

if __name__ == '__main__':
    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))
    else:
        os.makedirs(TEMP_DIR)

    app.run(debug=True)
