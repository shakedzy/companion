import re
import os
import openai
from google.oauth2.service_account import Credentials
from python import speech
from python.config import Config
from python.consts import TEMP_DIR


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


def bot_text_to_speech(text, message_index, counter):
    filename = os.path.join(TEMP_DIR, f"bot_speech_{message_index}_{counter}.mp3")
    speech.text2speech(text, filename)
    return filename


def init_openai(config: Config):
    openai_config = config.get("openai", None)
    if openai_config and "api_key" in openai_config:
        openai.api_key = openai_config["api_key"]


def get_gcs_credentials(config: Config) -> Credentials:
    sa = config.get("google_sa", None)
    if sa:
        credentials = Credentials.from_service_account_info(sa)
    else:
        credentials = None
    return credentials


def get_error_message_from_exception(e: Exception):
    return f"{e.__class__.__name__}: {e}"
