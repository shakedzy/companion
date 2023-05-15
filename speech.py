import os
import openai
import pyaudio
import wave
import logging
import pygame
from pydub import AudioSegment
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

_is_recording = False
watson_authenticator = IAMAuthenticator(os.environ["WATSON_API_KEY"])


def stop_recording():
    global _is_recording
    _is_recording = False

def record(filename):
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


def play_mp3(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()


def speech2text(filename, language):
    audio_file = open(filename, "rb")
    if language is None:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    else:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, language=language)
    return transcript["text"]


def text2speech(text, filename):
    text_to_speech = TextToSpeechV1(authenticator=watson_authenticator)
    text_to_speech.set_service_url(
        'https://api.eu-de.text-to-speech.watson.cloud.ibm.com/instances/80347f4c-b1e8-49c0-860a-164e8ae575b4')
    speech = text_to_speech.synthesize(text, voice='fr-FR_ReneeV3Voice',
                                             accept='audio/mp3').get_result().content
    with open(filename, "wb") as mp3_file:
        mp3_file.write(speech)
    return filename




