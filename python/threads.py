import pygame
from threading import Thread
from typing import Optional
from python import speech
from queue import Empty as EmptyQueue
from python.memory import Memory
from python.config import Config
from python.app_cache import AppCache
from python.utils import bot_text_to_speech, get_error_message_from_exception


config: Optional[Config] = None
memory: Optional[Memory] = None
app_cache: Optional[AppCache] = None


def init_threads(conf: Config, mem: Memory, cache: AppCache):
    global config, memory, app_cache
    config = conf
    memory = mem
    app_cache = cache

    app_cache.text2speech_thread = Thread(target=bot_text_to_speech_queue_func)
    app_cache.text2speech_thread.start()
    app_cache.play_recordings_thread = Thread(target=play_recordings_queue_func)
    app_cache.play_recordings_thread.start()


def bot_text_to_speech_queue_func():
    while not app_cache.stop_threads_event.is_set():
        try:
            item = app_cache.text2speech_queue.get(timeout=1)  # Wait for 1 second to get an item
            idx = item["message_index"]
            filename = bot_text_to_speech(text=item['text'], message_index=idx, counter=item['counter'], config=config)
            if item.get('skip_cache', False):
                memory.update(idx, recording=[filename])
            else:
                app_cache.bot_recordings.append(filename)
                memory.update(idx, recording=app_cache.bot_recordings)
            app_cache.play_recordings_queue.put(filename)
        except EmptyQueue:
            continue
        except Exception as e:
            app_cache.server_errors.append(get_error_message_from_exception(e))


def play_recordings_queue_func():
    while not app_cache.stop_threads_event.is_set():
        try:
            filename = app_cache.play_recordings_queue.get(timeout=1)  # Wait for 1 second to get an item
            speech.play_mp3(filename)
            while pygame.mixer.music.get_busy():
                continue
        except EmptyQueue:
            continue
        except Exception as e:
            app_cache.server_errors.append(get_error_message_from_exception(e))
