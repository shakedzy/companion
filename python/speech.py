from openai import OpenAI
from typing import Dict, List, Optional
from google.oauth2.service_account import Credentials
from google.cloud import texttospeech
from python.config import Config


t2s_audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
t2s_client: Optional[texttospeech.TextToSpeechClient] = None
t2s_voice: Optional[texttospeech.VoiceSelectionParams] = None
openai_client: Optional[OpenAI] = None


def init_speech(config: Config, credentials: Optional[Credentials]) -> None:
    """
    Initialize Google text-to-speech client and OpenAI client

    :param config: Config
    :param credentials: a Google Credentials object
    """
    global t2s_client, t2s_voice, openai_client

    openai_client = config.openai.client
    t2s_client = texttospeech.TextToSpeechClient(credentials=credentials)

    l = config.bot.voice.split("-")
    t2s_voice = get_voice_object(voice_name=config.bot.voice, language_code=f"{l[0]}-{l[1]}")


def get_voice_object(voice_name: str, language_code: str) -> texttospeech.VoiceSelectionParams:
    """
    Create a VoiceSelectionParams object

    :param voice_name: voice name
    :param language_code: language code and locale (i.e. 'en-US')
    :return: a VoiceSelectionParams object
    """
    return texttospeech.VoiceSelectionParams(name=voice_name, language_code=language_code)


def speech2text(filename: str, language: str) -> str:
    """
    Convert mp3 filename containing recording to text

    :param filename: mp3 filename with recording
    :param language: ISO 639-1 code of the language spoken in the recording.
                     If None, STT service will try to figure it out, by it might hurt performances
    :return: transcribed text
    """
    audio_file = open(filename, "rb")
    if language is None:
        transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
    else:
        transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text", language=language)
    return transcript


def text2speech(text: str, filename: str, voice: Optional[texttospeech.VoiceSelectionParams] = None) -> str:
    """
    Convert text to speech

    :param text: text to be converted
    :param filename: mp3 file with saved speech audio
    :param voice: an optional alternative voice, instead of the default one
    :return: filename
    """
    voice = voice or t2s_voice
    synthesis_input = texttospeech.SynthesisInput(text=text)
    speech = t2s_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=t2s_audio_config
    ).audio_content
    with open(filename, "wb") as mp3_file:
        mp3_file.write(speech)
    return filename


def voices_by_features() -> Dict[str, Dict[str, List[str]]]:
    """
    Return voices supported by TTS, by language and gender

    :return: Dict: {lang: {gender: [list of voices]}}
    """
    voices_dict = dict()
    voices = t2s_client.list_voices().voices

    for voice in voices:
        language_codes = voice.language_codes
        name = voice.name
        gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name.lower()

        for language_code in language_codes:
            if language_code not in voices_dict:
                voices_dict[language_code] = dict()

            lang_dict = voices_dict[language_code]
            if gender not in lang_dict:
                lang_dict[gender] = list()

            lang_dict[gender].append(name)

    return voices_dict
