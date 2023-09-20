from queue import Queue
from threading import Thread, Event
from typing import Generator, List, Optional


class AppCache:
    """
    Used to save data which needs to transfer between different threads and endpoints
    """
    message_generator: Optional[Generator] = None
    language: Optional[str] = None
    user_recording: Optional[str] = None
    bot_recordings: List[str] = list()
    server_errors: List[str] = list()
    keys_file: Optional[str] = None
    config_file: str = ''
    sentences_counter: int = 0
    generated_message: str = ''
    last_sentence: str = ''
    text2speech_thread: Optional[Thread] = None
    stop_threads_event: Event = Event()
    text2speech_queue: Queue = Queue()
    play_recordings_queue: Queue = Queue()
