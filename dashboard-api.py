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
    term_name = "S2"

    content = request.get_json()
    section_name = content['queryResult']['parameters']['param-name']

    student = get_student()
    parser = studentParser.StudentParser(student)

    grade = parser.getGrade(parser.convertNameAndSection(section_name), parser.convertTermNameToIds(term_name))

    percent = str(int(grade[1]))

    jsonResponse = json.dumps({"payload":{"google":{"expectUserResponse":False,"richResponse":{"items":[{"simpleResponse":{"textToSpeech":"You have a {} percent in {}.".format(percent, section_name)}}]}}}})

    return jsonResponse, 200

def test():
    percent = "50"
    section_name = "Math"
    setup = {"payload":{"google":{"expectUserResponse":False,"richResponse":{"items":[{"simpleResponse":{"textToSpeech":"You have a {} percent in {}.".format(percent, section_name)}}]}}}}
    jsonResponse = json.dumps(setup)
    return jsonResponse

if __name__ == '__main__':
    app.run()