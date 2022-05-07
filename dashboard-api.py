from flask import Flask, request#, jsonify
import pywerschool
import studentParser
import json
import os
from dotenv import load_dotenv
from google.auth import jwt
import csv


# Get environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# BASE_URL = os.environ.get("BASE_URL")
# LOGIN = os.environ.get("LOGIN")
# PASSWORD = os.environ.get("PASSWORD")
GOOGLE_CLIENT_ID = os.environ.get("CLIENT_ID")

GOOGLE_PUBLIC_CERTS = {
  "fcbd7f481a825d113e0d03dd94e60b69ff1665a2": "-----BEGIN CERTIFICATE-----\nMIIDJzCCAg+gAwIBAgIJAJCNvVzIrySKMA0GCSqGSIb3DQEBBQUAMDYxNDAyBgNV\nBAMMK2ZlZGVyYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20w\nHhcNMjIwNDI5MTUyMTUxWhcNMjIwNTE2MDMzNjUxWjA2MTQwMgYDVQQDDCtmZWRl\ncmF0ZWQtc2lnbm9uLnN5c3RlbS5nc2VydmljZWFjY291bnQuY29tMIIBIjANBgkq\nhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoz7Gb9oYt/sq8Z37LDAcfSqQBuTtD669\n+tjg+/hTVyXPRslIg6qPPLlVthRkXZYjhwnc85CXO9TW1C1ItJjX70vSQPvQ1wAL\nWMOd306BPIYRkkKSa3APtidaM6ZmR2HosWRUf/03luhfkk9QUyVaCP2WJTFxENuJ\ni5yyggE0cDT7MJGqn9VvYCv/+LUjiQ4v8jvc+dH881HeBDtwpsucXGCmx4ZcjEBc\nrNXqJiQHPo1I3OIXxxtsLxujU8f0QVRjdSQDr8KgeSdic8kk4iJp8DISWSU1hQSC\nbXUCG465L6I1iytO6iNQp+rfjpBt9jx0TA6VqIteglWhu5gfcKb9YQIDAQABozgw\nNjAMBgNVHRMBAf8EAjAAMA4GA1UdDwEB/wQEAwIHgDAWBgNVHSUBAf8EDDAKBggr\nBgEFBQcDAjANBgkqhkiG9w0BAQUFAAOCAQEAANlfZ6OYj/Wy951dSx7f7xxmleeW\neDPhWqpL4J+8ljHB2HRbBi5EjdJInHNquL/wCDw46nJhTIQ13dh7YJhJhgLarLcq\nd6DcBMeFTBZUFBoaHZNy7hZxZ1ggvonHGTpzPw68wW0Cx5erfswstwE7QPYBEHJf\nOlj6zwNQgvSEC8rEMIKfVuB9g0OWdzduPnwyoGOhDixP9pAjlV0MfYc/rMUGGpKw\npdg4kTBkx9XLYfiCfQJmsVz5CyQV9Q0VfdeIp5qKYWRutIQGTYPc0M0bgDSNpbRD\nd/QbikaqP5Q54ag8wdyr4SPiGIKlWkQRfAYcdVqFOI/uGLqsGbaNCAl7bg==\n-----END CERTIFICATE-----\n",
  "861649e450315383f6b9d510b7cd4e9226c3cd88": "-----BEGIN CERTIFICATE-----\nMIIDJzCCAg+gAwIBAgIJANCP0rP/R41vMA0GCSqGSIb3DQEBBQUAMDYxNDAyBgNV\nBAMMK2ZlZGVyYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20w\nHhcNMjIwNDIxMTUyMTUwWhcNMjIwNTA4MDMzNjUwWjA2MTQwMgYDVQQDDCtmZWRl\ncmF0ZWQtc2lnbm9uLnN5c3RlbS5nc2VydmljZWFjY291bnQuY29tMIIBIjANBgkq\nhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqR7fa5Gb2rhy+RJCJwSFn7J2KiKs/WgM\nXVR+23Z6OfX89/utHGkM+Qk27abDGPXa0u9OKzwOU2JZx7yNye7LH4kKX1PEAEz0\np9XGbfF3yFyiD5JkziOfQyYj9ERKWfxKatpk+oi9D/p2leQKzTfEZWIfLVZkgNXF\nkUdhzCG68j5kFhZ1Ys9bRRDo3Q1BkLXmP/Y6PW1g74/rvAYCiQ6hJVvyyXYnqHco\nawedgO6/MQihaSeAW25AhY8MXVo4+MdNvboahOlJg280YuxkCZiRqxyQEqd5HKCP\nzP49TDQbdAxDa900ewCQK9gkbHiNKFbOBv/b94YfMh93NUoEa+jCnwIDAQABozgw\nNjAMBgNVHRMBAf8EAjAAMA4GA1UdDwEB/wQEAwIHgDAWBgNVHSUBAf8EDDAKBggr\nBgEFBQcDAjANBgkqhkiG9w0BAQUFAAOCAQEAY2ficho0B/tfCt2QtQPEYVQ6FPfa\nuw8IhQHA12RgRcTLKNOhe9wYH4gYzCYbs08N/nX0UuoCI0ND1TgoUZT2BV9qY/Q3\nztSCGHU0SeHore1u/vQVf5qpoeZapWohCXE/tMJP3nKkDfXyZHfTfo1wMQqprR8W\nc3ZWH/jG49MBGURIkrmuP3AjjfXIK0tNcrUofWU/z2eXNIUTBxwE/Lgk8Ieb11j3\nTjM9v0b2KqBOLcaZ0+0JuYRawC2EkdEOlhprF8ssREun3Syjx6bJA9g4NgMWveZ9\nWQGthW7MggT5erMS/03e+h04FtaEaRygwtIUj0nGir2p0HqQ9FQDUnflHg==\n-----END CERTIFICATE-----\n",
  "b1a8259eb07660ef23781c85b7849bfa0a1c806c": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIIUTMZCaJBU1IwDQYJKoZIhvcNAQEFBQAwNjE0MDIGA1UE\nAwwrZmVkZXJhdGVkLXNpZ25vbi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTAe\nFw0yMjA1MDcxNTIxNTNaFw0yMjA1MjQwMzM2NTNaMDYxNDAyBgNVBAMMK2ZlZGVy\nYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wggEiMA0GCSqG\nSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDJjQhhNqM5Yh17B5AHlkye9eq65K7Z4MM6\n7W7a7D3/bdgx7SdPvaj6MGccviobxS4TNgd4TpKavyH6TvlapELZpI6Vo8UCh5/1\ndgnwIUUGAM/JYNYCrCag5l4AjDdr8XpiYEDcJTQ1whhuuAUNXH5lCbCPtUZRklSe\njsy5p8wreV6ZwfHnTmPRM+Z2s18gkHeFXAUrsK83GRHIT2VzObQdJsWefwlcrFeK\nYdRSoNrdeHi/nyDLaqzJQDwFZp++uswnk11M5ZTmA3YvLsjhZw5P+fLYayZC9RJ2\nf3743JkrelAg+vXnzLowUbEtm9iUI3hiqQchOJqXdYnveXocQjEHAgMBAAGjODA2\nMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBYGA1UdJQEB/wQMMAoGCCsG\nAQUFBwMCMA0GCSqGSIb3DQEBBQUAA4IBAQB780bStZ1R7/8imPQi0ZaExBTeZL65\nMdiVb19yvpYSkyAu4xGx3aUGJzWSQ2ou4tX1gSHeh+fC2Qxef9lcmRONUNmWYoEO\nOk1/mqNPJ6U7BXuYu+RjkI/GjSRsyLbx0nseWtlUolAMsjNPYtrNp47t38jn9JAs\nrKFx6DpOpz5X7CjOTnh8YAuvb6PVMLzKB6XTPFub9UKGgZmENrnYOMCaPizOqkQ+\nu5+x5qpELmNy5lYeYE1yDJBj5wE7uOeIkLgF0NAm9MQ8ASaPxYgBMlrdmbHJXs1A\nUL3+1HENYsCOW6/RSV6q3Yc+ASqkyOfk2KSTIvZytZeGTiq7sxCgKboi\n-----END CERTIFICATE-----\n"
}

app = Flask(__name__)

def get_student(username, password, base_url):
    client = pywerschool.Client(base_url)
    student = client.getStudent(username, password, toDict=True)
    return student

@app.route('/endpoint', methods=['POST'])
def grade():
    header = request.headers
    content = request.get_json()
    response = handleRequest(content, header)

    return response, 200

def handleRequest(content, header):
    handler = content['handler']['name']
    if handler == "wake":
        return wake()
    elif handler == "get_grade":
        return get_grade(content)
    elif handler == "create_user":
        return create_user(header)
    else:
        return None

def wake():
    responseText = "Ok, I'm ready. Ask me about your grades."
    jsonResponse = simple_response(responseText)

    return jsonResponse

def get_grade(content, header):
    username, password, base_url = lookup_user(get_email(header))

    section_name = content['intent']['params']['class']['resolved']

    student = get_student(username, password, base_url)
    parser = studentParser.StudentParser(student)

    term_name = "S2"
    grade = parser.getGrade(parser.convertNameAndSection(section_name), parser.convertTermNameToIds(term_name))

    percent = str(int(grade[1]))

    responseText = "You have a {} percent in {}.".format(percent, section_name)
    jsonResponse = simple_response(responseText)

    return jsonResponse

def simple_response(text):
    jsonResponse = json.dumps({"prompt": {"firstSimple": {"speech": text,"text": text}}})
    return jsonResponse

@app.route('/create_user', methods=['POST'])
def create_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    base_url = request.form['base_url']
    add_user(email, username, password, base_url)
    return "User created", 200

# def create_user(header):
#     authorization = header['Authorization']
#     claims = jwt.decode(authorization, certs=GOOGLE_PUBLIC_CERTS, audience=GOOGLE_CLIENT_ID)
#     return claims

def get_email(header):
    authorization = header['Authorization']
    claims = jwt.decode(authorization, certs=GOOGLE_PUBLIC_CERTS, audience=GOOGLE_CLIENT_ID)
    return claims['email']

def lookup_user(email):
    with open('.data/storage.csv', 'r') as csvfile:
        dictionary = csv.DictReader(csvfile)
        csvfile.close()
        return dictionary[email]

def add_user(email, username, password, base_url):
    with open('.data/storage.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([email, username, password, base_url])
    csvfile.close()

def create_csv_storage():
    with open('.data/storage.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['email', 'username', 'password', 'base_url'])
    csvfile.close()


if __name__ == '__main__':
    app.run()
    if not os.path.isfile('.data/storage.csv'): create_csv_storage()