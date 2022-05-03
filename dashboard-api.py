from flask import Flask, request, jsonify
import pywerschool
import studentParser

app = Flask(__name__)

def get_student(base_url, username, password):
    client = pywerschool.Client(base_url)
    student = client.getStudent(username, password, toDict=True)
    return student

@app.route('/grade', methods=['GET', 'POST'])
def grade():
    base_url = request.args.get('base_url')
    username = request.args.get('username')
    password = request.args.get('password')
    term_name = request.args.get('term_name')
    section_name = request.args.get('section_name')

    student = get_student(base_url, username, password)
    parser = studentParser.StudentParser(student)

    grade = parser.getGrade(parser.convertNameAndSection(section_name), parser.convertTermNameToIds(term_name))

    return jsonify(grade), 200

if __name__ == '__main__':
    app.run()