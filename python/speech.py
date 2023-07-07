import os
import openai
import pyaudio
import wave
import logging
import pygame
from typing import Dict, List
from pydub import AudioSegment
from google.oauth2.service_account import Credentials
from google.cloud import texttospeech
from python.config import Config


_is_recording = False

t2s_audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
t2s_client = texttospeech.TextToSpeechClient()
t2s_voice = None


def init_speech(config: Config, credentials: Credentials) -> None:
    """
    Initialize Google text-to-speech client

    :param config: Config
    :param credentials: a Google Credentials object
    """
    global t2s_client, t2s_voice

    t2s_client = texttospeech.TextToSpeechClient(credentials=credentials)

    l = config.bot.voice.split("-")
    t2s_voice = texttospeech.VoiceSelectionParams(name=config.bot.voice, language_code=f"{l[0]}-{l[1]}")


def stop_recording() -> None:
    """
    Stop recording loop (as it happens on a parallel thread)
    """
    global _is_recording
    _is_recording = False


def record(filename: str) -> str:
    """
    Record user audio

    :param filename: filename to save recording to (a mp3 file)
    :return: filename of mp3
    """
    global _is_recording
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    audio = pyaudio.PyAudio()

    # Start recording
    _is_recording = True
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    logging.info(f"Recording started ({filename})")
    frames = []

    while _is_recording:
        data = stream.read(CHUNK)
        frames.append(data)
    logging.info("Recording ended")

    # Stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio as a WAV file
    wav_filename = f"{filename}_TEMP.wav"
    wf = wave.open(wav_filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    # Convert the WAV file to an MP3 file
    mp3_filename = filename
    wav_audio = AudioSegment.from_wav(wav_filename)
    wav_audio.export(mp3_filename, format="mp3")

    # Remove the temporary WAV file
    os.remove(wav_filename)
    logging.info(f"Saved recording as {mp3_filename}")
    return mp3_filename


def play_mp3(filename: str) -> None:
    """
    play a mp3 file

    :param filename: file to play
    """
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()


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
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    else:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, language=language)
    return transcript["text"]


def text2speech(text: str, filename: str) -> str:
    """
    Convert text to speech

    :param text: text to be converted
    :param filename: mp3 file with saved speech audio
    :return: filename
    """
    synthesis_input = texttospeech.SynthesisInput(text=text)
    speech = t2s_client.synthesize_speech(
        input=synthesis_input, voice=t2s_voice, audio_config=t2s_audio_config
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
