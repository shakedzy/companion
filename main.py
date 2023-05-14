import yaml
from flask import Flask, render_template, request, jsonify
from memory import Memory
from config import Config
from chatbot import Chatbot

app = Flask(__name__)

with open("config.yml", "r") as yml_file:
    config: Config = Config(yaml.safe_load(yml_file))
memory = Memory()
chatbot = Chatbot(config=config, memory=memory)

class AppCache:
    message_generator = None
    generated_message = ''

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
        app_cache.message_generator = None
        app_cache.generated_message = ''
        return jsonify({'message': None})

@app.route('/start_recording', methods=['POST'])
def start_recording():
    print("recording")
    return jsonify({'message': 'Recording started'})

@app.route('/end_recording', methods=['POST'])
def end_recording():
    recorded_text = 'RECORDED TEXT'  # Replace with your own recording logic
    return jsonify({'recorded_text': recorded_text})

@app.route('/print_message', methods=['POST'])
def print_message():
    message = request.form['message']
    print(message)
    return jsonify({'status': 'success'})

@app.route('/store_message', methods=['POST'])
def store_message():
    sender = request.form['sender']
    message = request.form['message']
    global memory
    memory.add(role=sender, message=message)
    return jsonify({'status': 'success'})

@app.route('/toggle_loading_icon', methods=['POST'])
def toggle_loading_icon():
    action = request.form.get('action')
    return jsonify({'action': action})

@app.route('/record_user_message', methods=['POST'])
def record_user_message():
    message = request.form['message']
    print(f"Recording user message: {message}")
    return jsonify({'message': 'User message recorded successfully'})

@app.route('/set_language', methods=['POST'])
def set_language():
    language = request.form['language']
    print("Setting language to:", language)
    # Replace with your own logic
    return jsonify({'message': 'Language set successfully'})

if __name__ == '__main__':
    app.run(debug=True)
