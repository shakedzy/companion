import json
from flask import Flask, render_template, request
from python.language import language_name_to_iso6391

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'image_url': request.form.get('image_url'),
            'selected_chip': request.form.get('selected_chip'),
            'dropdown_selection': request.form.get('dropdown_selection')
        }
        with open('data.txt', 'w') as outfile:
            json.dump(data, outfile)
        return 'Data saved successfully'
    return render_template('setup.html', males=MALE_TUTORS, females=FEMALE_TUTORS,
                           input_languages_codes_and_names=[[language_name_to_iso6391(lang), lang] for lang in INPUT_LANGUAGES],
                           output_languages_locales_and_names=[],
                           voices=[])


if __name__ == '__main__':
    app.run(debug=True)
