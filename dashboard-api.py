from flask import Flask, request#, jsonify
import pywerschool
import studentParser
import json
import os
from dotenv import load_dotenv

# Get environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

BASE_URL = os.environ.get("BASE_URL")
LOGIN = os.environ.get("LOGIN")
PASSWORD = os.environ.get("PASSWORD")

app = Flask(__name__)

def get_student():
    client = pywerschool.Client(BASE_URL)
    student = client.getStudent(LOGIN, PASSWORD, toDict=True)
    return student

@app.route('/grade', methods=['GET', 'POST'])
def grade():
    content = request.get_json()
    response = determineRequestPurpose(content)

    return response, 200

def determineRequestPurpose(content):
    handler = content['handler']['name']
    if handler == "get_grade":
        return get_grade(content)
    else:
        return wake()

def wake():
    responseText = "I'm ready to help check your grades!"
    jsonResponse = json.dumps({"prompt": {"firstSimple": {"speech": responseText,"text": responseText}}})

    return jsonResponse

def get_grade(content):
    section_name = content['intent']['params']['class']['resolved']

    student = get_student()
    parser = studentParser.StudentParser(student)

    term_name = "S2"
    grade = parser.getGrade(parser.convertNameAndSection(section_name), parser.convertTermNameToIds(term_name))

    percent = str(int(grade[1]))

    responseText = "You have a {} percent in {}.".format(percent, section_name)
    jsonResponse = json.dumps({"prompt": {"firstSimple": {"speech": responseText,"text": responseText}}})

    return jsonResponse

if __name__ == '__main__':
    app.run()