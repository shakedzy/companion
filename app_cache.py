from queue import Queue
from threading import Thread

class AppCache:
    message_generator = None
    language = None
    user_recording = None
    bot_recordings = list()
    sentences_counter: int = 0
    generated_message: str = ''
    last_sentence: str = ''
    recording_thread: Thread = None
    text2speech_thread: Thread = None
    play_recordings_thread: Thread = None
    text2speech_queue = Queue()
    play_recordings_queue = Queue()