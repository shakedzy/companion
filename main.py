from flask import Flask, render_template, request, jsonify
#from flask_socketio import SocketIO
from chatbot import MyChatbot
from functools import wraps
import time


app = Flask(__name__)
chatbot = MyChatbot()

messages_dict = {}

# def toggle_loading_icon(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         socketio.emit('loading_icon', {'status': 'show'})
#         result = func(*args, **kwargs)
#         socketio.emit('loading_icon', {'status': 'hide'})
#         return result
#     return wrapper

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    message = request.form['message']
    responses = chatbot.get_response(message)
    return jsonify({'messages': responses})

#@toggle_loading_icon
@app.route('/record_message', methods=['POST'])
def record_message():
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
    message_id = len(messages_dict) + 1
    messages_dict[message_id] = {'sender': sender, 'message': message}
    return jsonify({'status': 'success', 'message_id': message_id})

@app.route('/toggle_loading_icon', methods=['POST'])
def toggle_loading_icon():
    action = request.form.get('action')
    return jsonify({'action': action})

@app.route('/start_recording', methods=['POST'])
def start_recording():
    print("recording")
    return jsonify({'message': 'Recording started'})

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
