import pygame
from python import speech
from queue import Empty as EmptyQueue
from python.memory import Memory
from python.config import Config
from python.app_cache import AppCache
from python.utils import bot_text_to_speech

def bot_text_to_speech_queue_func(config: Config, memory: Memory, app_cache: AppCache):
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


def play_recordings_queue_func(app_cache: AppCache):
    while not app_cache.stop_threads_event.is_set():
        try:
            filename = app_cache.play_recordings_queue.get(timeout=1)  # Wait for 1 second to get an item
            speech.play_mp3(filename)
            while pygame.mixer.music.get_busy():
                continue
        except EmptyQueue:
            continue
