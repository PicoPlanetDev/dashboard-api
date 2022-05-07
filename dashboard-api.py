from flask import Flask, request#, jsonify
import pywerschool
import studentParser
import json
import os
from dotenv import load_dotenv
from google.auth import jwt
import sqlite3 as sql

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
    if handler == "get_grade":
        return get_grade(content, header)
    if handler == "add_user":
        return add_user_from_actions(content, header)


def get_grade(content, header):
    username, password, base_url = get_user_from_database(get_email(header))
    if username == None or password == None or base_url == None:
        return json.dumps({"prompt":{"content":{"card":{"title":"Finish Account Linking","subtitle":"Please register","text":"Go to https://dashboard-api-web.glitch.me/ to enter your login information.","image":{"url":"https://img.icons8.com/fluency/96/000000/urgent-property.png","alt":"Register logo"},"button":{"name":"Sign Up","open":{"url":"https://dashboard-api-web.glitch.me/"}}}},"firstSimple":{"speech":"Don't forget, you need to enter your Dashboard information online.","text":"Don't forget, you need to enter your Dashboard information at https://dashboard-api-web.glitch.me/"}}})

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

def add_user_from_actions(content, header):
    email = get_email(header)
    username = content['intent']['params']['username']['resolved']
    password = content['intent']['params']['password']['resolved']
    base_url = content['intent']['params']['base_url']['resolved']
    add_user_to_database(email, username, password, base_url)
    return simple_response("You are now registered.")

@app.route('/create_user', methods=['POST'])
def create_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    base_url = request.form['base_url']
    create_database()
    add_user_to_database(email, username, password, base_url)
    return "User created successfully", 200

@app.route('/delete_user', methods=['POST'])
def delete_user():
    email = request.form['email']
    password = request.form['password']
    delete_user_from_database(email, password)
    return "User deleted successfully", 200

def get_email(header):
    authorization = header['Authorization']
    claims = jwt.decode(authorization, certs=GOOGLE_PUBLIC_CERTS, audience=GOOGLE_CLIENT_ID)
    return claims['email']

def create_database():
    con = sql.connect('.data/database.db')
    # Right now just trying to replicate the old functionality
    # TODO: Allow adding dictionaries so classes can be officially mapped
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT,
            password TEXT,
            base_url TEXT
        );
        """)

def add_user_to_database(email, username, password, base_url):
    con = sql.connect('.data/database.db')
    # Add user to database
    with con:
        con.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (email, username, password, base_url))

def get_user_from_database(email):
    con = sql.connect('.data/database.db')
    with con:
        data = con.execute("SELECT * FROM users WHERE email = ?", (email,))
        for row in data: return row[1], row[2], row[3] # Hopefully there is just one email
    return None, None, None # If there is no user, return None, None, None which should ask the user to create an account

def delete_user_from_database(email, password):
    con = sql.connect('.data/database.db')
    # Password must also be provided to delete a user
    with con:
        con.execute("DELETE FROM users WHERE email = ? AND password = ?", (email, password))

@app.route('/wake', methods=['GET'])
def wake():
    return "Woken", 200

if __name__ == '__main__':
    app.run()
    create_database()