from flask import Flask, render_template, request
import json

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
    return render_template('setup.html', males=MALE_TUTORS, females=FEMALE_TUTORS)


if __name__ == '__main__':
    app.run(debug=True)
