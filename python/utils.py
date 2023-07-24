import re
import os
import openai
from typing import List, Optional
from google.oauth2.service_account import Credentials
from google.cloud.texttospeech import VoiceSelectionParams
from python import speech
from python.config import Config
from python.consts import TEMP_DIR


def split_to_sentences(text: str) -> List[str]:
    """
    Split a text to two parts. If a full sentence is found in the text, split it from the rest of the text.
    If no full sentences are in the text, but the text is too long, split by first comma.
    This is a helper function to the text-to-speech mechanism, meant to assist sending full sentences to be
    converted to speech as the message is being written by the tutor.

    This function MUST return a list of only one or two elements!

    :param text: the text to split
    """
    characters = [c+' ' for c in ['.', '!', "?", ":", ";"]]
    escaped_characters = [re.escape(c) for c in characters]
    text = re.sub('_+', 'mmm', text)  # see issue #39
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


def bot_text_to_speech(text: str, message_index: int, counter: int, voice: Optional[VoiceSelectionParams] = None) -> str:
    """
    Helper function to create a mp3 file with recording and logical name.

    :param text: text to be converted to speech
    :param message_index: index of message in memory
    :param counter: number of this file from all speech files created for this message (as messages are split as
                    they are been written, and fill sentences are sent to be converted to speech)
    :param voice: an optional alternative voice, instead of the default one
    :return: file name of speech recording
    """
    filename = os.path.join(TEMP_DIR, f"bot_speech_{message_index}_{counter}.mp3")
    speech.text2speech(text, filename, voice=voice)
    return filename


def init_openai(config: Config) -> None:
    """
    Initialize OpenAI configurations from Config

    :param config: Config
    """
    openai_config = config.get("openai", None)
    if openai_config and "api_key" in openai_config:
        openai.api_key = openai_config["api_key"]


def get_gcs_credentials(config: Config) -> Credentials:
    """
    Ger Google Credentials object from Config configurations

    :param config: Config
    :return: Credentials
    """
    sa = config.get("google_sa", None)
    if sa:
        credentials = Credentials.from_service_account_info(sa)
    else:
        credentials = None
    return credentials


def get_error_message_from_exception(e: Exception) -> str:
    """
    Get full exception error message

    :param e: an Exception raised
    :return: error message
    """
    return f"{e.__class__.__name__}: {e}"
