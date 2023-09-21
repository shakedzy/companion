import os

TEMP_DIR_NAME = "tmp"
TEMP_DIR = os.path.join(os.getcwd(), f"static/{TEMP_DIR_NAME}")
LTM_DIR = os.path.join(os.getcwd(), "ltm")  # Long Term Memory
SAVED_SESSION_FILE = os.path.join(LTM_DIR, "last_session.json")

MALE_TUTORS = [
    "Nicolas",
    "James",
    "Michael",
    "Mario",
    "Henry"
]

FEMALE_TUTORS = [
    "Renée",
    "Charlotte",
    "Sofia",
    "Kate",
    "Marie"
]

INPUT_LANGUAGES = [  # Supported languages by OpenAI Whisper
    "Afrikaans",
    "Arabic",
    "Armenian",
    "Azerbaijani",
    "Belarusian",
    "Bosnian",
    "Bulgarian",
    "Catalan",
    "Chinese",
    "Croatian",
    "Czech",
    "Danish",
    "Dutch",
    "English",
    "Estonian",
    "Finnish",
    "French",
    "Galician",
    "German",
    "Greek",
    "Hebrew",
    "Hindi",
    "Hungarian",
    "Icelandic",
    "Indonesian",
    "Italian",
    "Japanese",
    "Kannada",
    "Kazakh",
    "Korean",
    "Latvian",
    "Lithuanian",
    "Macedonian",
    "Malay",
    "Marathi",
    "Maori",
    "Nepali",
    "Norwegian",
    "Persian",
    "Polish",
    "Portuguese",
    "Romanian",
    "Russian",
    "Serbian",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swahili",
    "Swedish",
    "Tagalog",
    "Tamil",
    "Thai",
    "Turkish",
    "Ukrainian",
    "Urdu",
    "Vietnamese",
    "Welsh"
]