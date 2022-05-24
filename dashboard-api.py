from flask import Flask, request
import pywerschool
import studentParser
import json
import os
from dotenv import load_dotenv
from google.auth import jwt
import sqlite3 as sql
import random
import yagmail

# Get environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

EMAIL_OAUTH_CREDS_PATH = os.environ.get("DASHBOARD_API_EMAIL_OAUTH_CREDS_PATH")
GOOGLE_CLIENT_ID = os.environ.get("DASHBOARD_API_URL_CLIENT_ID")
WEB_INTERFACE_URL = os.environ.get("DASHBOARD_API_WEB_INTERFACE_URL")

GOOGLE_PUBLIC_CERTS = {
  "38f3883468fc659abb4475f36313d22585c2d7ca": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIIBeMWhXdsJrkwDQYJKoZIhvcNAQEFBQAwNjE0MDIGA1UE\nAwwrZmVkZXJhdGVkLXNpZ25vbi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTAe\nFw0yMjA1MjMxNTIxNTVaFw0yMjA2MDkwMzM2NTVaMDYxNDAyBgNVBAMMK2ZlZGVy\nYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wggEiMA0GCSqG\nSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCHQbiedBzf2CfTh9O5IkHqXUmET2CAb5Ie\ntz3J+vzm3NASPEbnmOKmaeZbXH4gdLU+9aC01ul4QPJr0hTOQLwHGcGG3tZUNX2Y\nsFkryzOsKuPqXtLC9A4zpzDT4qAaCbPAT8gaSfjnbCaVVjP0ghj561qyuSy0nQba\nyZAncNvdhtl7fYWhiddtsrfw7aEh/ht996Bxyt+awQRtKKyrT3TcgRsKLSqkluGu\nCq9iDr/LQp47HFfm778mD4ozQC5vhgZPYtGyIT/KCyRpu6iHqdAOvwz35IML9sSK\nd3YVSTvrVlLD9AyT381z2iuWVoxmlDgWkpG/ktcdRrDP96vw/dzTAgMBAAGjODA2\nMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBYGA1UdJQEB/wQMMAoGCCsG\nAQUFBwMCMA0GCSqGSIb3DQEBBQUAA4IBAQBeHPTmiLMnZO6Ov+4L4nX8TvGdRC6S\n6GGwRlOI8Ddw8no3yWQFE4kbVAowFei4rey9FyjRieUznZYU6zMvvSPweIl+kZij\n5lzGb03VyF11b5KaIkJfamcG3df+1LbYrtnsxbJ9yCNJd4O5apmDOPnUWsmrrARX\nCwF/j1I5M15wwKKMWfTIwvUgcEuXbrsDEpODu0QykU50nN1WxDXcIyd5of9HKgIw\nXeOysW0RIytUvOpdYq+LASQ0FNEgPBxaEnj+m2QXscFvuF3evcO4x6nlkWz5vJaI\n539aY44tR5hn3+9wijkA3VMTS+ucTt3O/JY9TXRi+SkdKrhDjaTF/x4T\n-----END CERTIFICATE-----\n",
  "486f16482005a2cdaf26d9214018d029ca46fb56": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIIGx/tdofCUK0wDQYJKoZIhvcNAQEFBQAwNjE0MDIGA1UE\nAwwrZmVkZXJhdGVkLXNpZ25vbi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTAe\nFw0yMjA1MTUxNTIxNTRaFw0yMjA2MDEwMzM2NTRaMDYxNDAyBgNVBAMMK2ZlZGVy\nYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wggEiMA0GCSqG\nSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCkoUouYOc2jM+7bj6cKtu9sGM7SCK2HtWb\nE+bWnH2WQl/Bc5YRs3PJ8OF3dKPKUpPIfmWrrMy0m828oKvZPJBPDKm+ZkGl4wrb\n1nPRa+A8EUnocey71qlrbWGAT2I9/QDWU0bk13aQ/2bYpzx6QrLg6uyEOnqCzWe0\nc9aJbaJKO22u4WNMHbQ/unkZN2XHODosKsnTcTsUmWt9dwQQpEPNniHdvqE3Zpn+\nF45nFFJnpTDHz+1sVF7ZMh/D0hdpde6h0cxGi21IhkG10l05qdsgUC6ER6/1v6UV\nOSwVBcO+JxSLP+uLgkOWIa4QCAg0eMjqlw2ja+RjHc26lE6aQNEhAgMBAAGjODA2\nMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBYGA1UdJQEB/wQMMAoGCCsG\nAQUFBwMCMA0GCSqGSIb3DQEBBQUAA4IBAQB4W1ozPYUniciHt8vSt1pGM6el5xrW\nXPpvtmTdlc2Ex2suv5SAsJGCvHOh1C2VdcxnCWhqIzaikwawvCHnrfQOUGIpxzVw\nQLolDKb+lWSkhV1Loa3eF1W4MjDp5R6GB7xDWbusejKUH7hGzVV8gMFhA/HOicFT\ngo/OZT8UJkTpsQ69YxdAIzuJ2RZ+bMjpvx+iuODLUDzh+M4oaI7mqdmcRf9AdlkN\n0SU0nr3qyonLbThceGHENu07mK7Pm/MovHjeGdqRLI/cWCLtc8W49F6XyTpk+QUz\nwlkL7eJ1krpAv1ax/8jECJQ4ckH1JeL3on19znKBoCi4xat3HZZuuc0c\n-----END CERTIFICATE-----\n",
  "b1a8259eb07660ef23781c85b7849bfa0a1c806c": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIIUTMZCaJBU1IwDQYJKoZIhvcNAQEFBQAwNjE0MDIGA1UE\nAwwrZmVkZXJhdGVkLXNpZ25vbi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTAe\nFw0yMjA1MDcxNTIxNTNaFw0yMjA1MjQwMzM2NTNaMDYxNDAyBgNVBAMMK2ZlZGVy\nYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wggEiMA0GCSqG\nSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDJjQhhNqM5Yh17B5AHlkye9eq65K7Z4MM6\n7W7a7D3/bdgx7SdPvaj6MGccviobxS4TNgd4TpKavyH6TvlapELZpI6Vo8UCh5/1\ndgnwIUUGAM/JYNYCrCag5l4AjDdr8XpiYEDcJTQ1whhuuAUNXH5lCbCPtUZRklSe\njsy5p8wreV6ZwfHnTmPRM+Z2s18gkHeFXAUrsK83GRHIT2VzObQdJsWefwlcrFeK\nYdRSoNrdeHi/nyDLaqzJQDwFZp++uswnk11M5ZTmA3YvLsjhZw5P+fLYayZC9RJ2\nf3743JkrelAg+vXnzLowUbEtm9iUI3hiqQchOJqXdYnveXocQjEHAgMBAAGjODA2\nMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBYGA1UdJQEB/wQMMAoGCCsG\nAQUFBwMCMA0GCSqGSIb3DQEBBQUAA4IBAQB780bStZ1R7/8imPQi0ZaExBTeZL65\nMdiVb19yvpYSkyAu4xGx3aUGJzWSQ2ou4tX1gSHeh+fC2Qxef9lcmRONUNmWYoEO\nOk1/mqNPJ6U7BXuYu+RjkI/GjSRsyLbx0nseWtlUolAMsjNPYtrNp47t38jn9JAs\nrKFx6DpOpz5X7CjOTnh8YAuvb6PVMLzKB6XTPFub9UKGgZmENrnYOMCaPizOqkQ+\nu5+x5qpELmNy5lYeYE1yDJBj5wE7uOeIkLgF0NAm9MQ8ASaPxYgBMlrdmbHJXs1A\nUL3+1HENYsCOW6/RSV6q3Yc+ASqkyOfk2KSTIvZytZeGTiq7sxCgKboi\n-----END CERTIFICATE-----\n"
}

app = Flask(__name__)

# ---------------------------------------------------------------------------- #
#                                  App routes                                  #
# ---------------------------------------------------------------------------- #

# Google Actions webhook
@app.route('/endpoint', methods=['POST'])
def endpoint():
    header = request.headers
    content = request.get_json()
    response = handleRequest(content, header)
    return response, 200

# Add a user with the required information from the webpage form
@app.route('/create_user', methods=['POST'])
def create_user():
    # Get the information from the form
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    base_url = request.form['base_url']
    # Add the user to the database
    add_user_to_database(email, username, password, base_url)
    # Return a response to the user with a success message and a link back to the homepage
    return "User created successfully. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 200

@app.route('/edit_classes', methods=['POST'])
def edit_classes():
    email = request.form['email']
    password = request.form['password']
    # The user's identity must be checked before make any modifications
    if not verify_email_and_password(email, password): return "Invalid email or password. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 401

    classes_form = request.form.to_dict()
    # Remove the email and password from the dictionary TODO: This is a hacky way to do this
    classes_form.pop('email')
    classes_form.pop('password')

    # Everything else in the form is either a class or a synonym, so we need to differentiate based on the field name
    # Because each field gets a new number after the name, we check the first 10 or 13 characters of the field name to see if it starts with 
    # class_name or class_synonym.
    class_names = [classes_form[class_name] for class_name in classes_form if class_name[0:10] == "class_name"] # Get all the class names from their keys
    # Get all the class synonyms from their keys and use split to make them a list
    class_synonyms = [classes_form[class_synonym].split(',') for class_synonym in classes_form if class_synonym[0:13] == "class_synonym"]
    classes = dict(zip(class_names, class_synonyms))

    # This replaces the old classes with the new ones, so we need to delete the old ones
    remove_classes_from_database(email)
    add_classes_to_database(email, classes) # Add the new classes to the database
    return "Classes added successfully. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 200

@app.route('/set_term', methods=['POST'])
def set_term():
    email = request.form['email']
    password = request.form['password']
    # The user's identity must be checked before make any modifications
    if not verify_email_and_password(email, password): return "Invalid email or password. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 401

    term = request.form['term']
    delete_term_from_database(email) # This replaces the old term with the new one
    add_term_to_database(email, term)
    return "Term set successfully. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 200

# Delete all information with the user's email if their password also matches
@app.route('/delete_user', methods=['POST'])
def delete_user():
    email = request.form['email']
    password = request.form['password']
    # The user's identity must be checked before make any modifications
    if not verify_email_and_password(email, password): return "Invalid email or password. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 401

    # Make sure to delete all information with the user's email
    delete_user_from_database(email)
    remove_classes_from_database(email)
    delete_term_from_database(email)
    return "User deleted successfully. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 200

@app.route('/wake', methods=['GET'])
def wake():
    return "Woken", 200

@app.route('/generate_recovery_code', methods=['POST'])
def generate_recovery_code():
    email = request.form['email']
    recovery_code = random.randint(100000, 999999)
    add_recovery_to_database(email, recovery_code)
    yag = yagmail.SMTP('noreply.dashboard.api', oauth2_file=EMAIL_OAUTH_CREDS_PATH)
    contents = [
        "<h1>Grades Dashboard Recovery Code</h1>",
        "Your recovery code is <code>{}</code>".format(recovery_code),
        "Please enter this code in the password recovery form on the <a href={}>Grades Dashboard web interface</a>.".format(WEB_INTERFACE_URL),
        "This code will eventually expire. If you don't use before it expires, you will need to generate a new code.",
        "<br><br>Not you? Don't worry - this code will expire soon.",
        "<br><br>Thanks for using Grades Dashboard!"
    ]
    yag.send(email, 'Grades Dashboard Password Reset', contents)
    return "Recovery code generated. Please <a href={}>Return</a> then enter the code from your email.".format(WEB_INTERFACE_URL), 200

@app.route('/recover', methods=['POST'])
def recover():
    email = request.form['email']
    recovery_code = request.form['recovery_code']
    new_password = request.form['new_password']
    new_password_conf = request.form['new_password_conf']
    if new_password != new_password_conf: return "Passwords do not match. Please <a href={}>Return</a> and try again.".format(WEB_INTERFACE_URL), 401
    if not verify_recovery(email, recovery_code): return "Invalid recovery code. Please <a href={}>Return</a> and check for typos.".format(WEB_INTERFACE_URL), 401
    else:
        delete_recovery_from_database(email)
        old_user = get_user_from_database(email)
        delete_user_from_database(email)
    new_user = [email, old_user[1], new_password, old_user[2]]
    add_user_to_database(new_user[0], new_user[1], new_user[2], new_user[3])
    return "Password reset successfully. <a href={}>Return</a>".format(WEB_INTERFACE_URL), 200

# In case we want to do other things from the webhook, we can figure out what to do here
# based on the handler that we enter in the Actions Console
def handleRequest(content, header):
    handler = content['handler']['name']
    if handler == "get_grade":
        return get_grade(content, header)

def get_student(username, password, base_url):
    client = pywerschool.Client(base_url)
    student = client.getStudent(username, password, toDict=True)
    return student

def get_grade(content, header):
    try: email = get_email(header)
    except: return simple_response("Sorry, I couldn't verify your email address. Please try again later.")
    username, password, base_url = get_user_from_database(email) # Get the user's email address from Google's header
    if username == None or password == None or base_url == None: # If the user's registration is incomplete, prompt them to sign up
        register_card = card_response_button("Finish Account Linking", "Please register", "Go to {} to enter your login information.".format(WEB_INTERFACE_URL), "https://img.icons8.com/fluency/96/000000/urgent-property.png", "Register warning icon", "Finish", WEB_INTERFACE_URL)
        return register_card
    
    # Try to idenify the class the user is trying to get the grade for
    try: synonym = content['intent']['params']['class']['resolved']
    except KeyError: return simple_response("Sorry, something went wrong while interpreting your request. Please try again later.")

    section_name = evaluate_class_from_synonym(email, synonym) # Convert the general class synonym to the specific section name

    student = get_student(username, password, base_url)
    parser = studentParser.StudentParser(student)

    term_name = get_term_from_database(email)
    grade = parser.getGrade(parser.convertNameAndSection(section_name), parser.convertTermNameToIds(term_name))

    percent = str(int(grade[1]))
    letter = grade[0]
    if letter in ["A", "B", "C", "D", "E"]: letter_name = letter
    else: letter_name = "unknown"
    letter_image_url = "https://raw.githubusercontent.com/PicoPlanetDev/dashboard-api/master/grade_letters/{}.png".format(letter_name)

    responseText = "You have a {} percent in {}.".format(percent, section_name)
    # jsonResponse = simple_response(responseText)
    jsonResponse = card_response_nobutton(section_name, "{} percent".format(percent), responseText, letter_image_url, letter, responseText, responseText)

    return jsonResponse

def get_email(header):
    """Gets the email address of the user by decrypting the token in the header.

    Args:
        header (str?/dict?): The header of the POST request obtained by request.headers

    Returns:
        str: User's email address
    """    
    try:
        authorization = header['Authorization']
        claims = jwt.decode(authorization, certs=GOOGLE_PUBLIC_CERTS, audience=GOOGLE_CLIENT_ID)
        return claims['email']
    except: # Normally you would just return None here
        try:
            return header['Email'] # But because I can't generate Google tokens for my email and they expire, I'll allow this
        except: raise Exception("Sorry, I couldn't verify your email address. Please try again later.")

# ----------------------------- Webhook responses ---------------------------- #
def simple_response(text):
    """Returns a JSON response with speech and text.

    Args:
        text (str): Text used for both speech and text output

    Returns:
        str: JSON response string
    """    
    jsonResponse = json.dumps({"prompt": {"firstSimple": {"speech": text,"text": text}}})
    return jsonResponse

def card_response_button(title, subtitle, text, image_url, image_alt, button_name, button_url, first_simple_speech, first_simple_text):
    """Returns a JSON response with a card that includes text, an image, and a button.

    Args:
        title (str): Title text
        subtitle (str): Subtitle text under the title
        text (str): Paragraph text under the subtitle
        image_url (str): Small icon image URL
        image_alt (str): Alt text for the image
        button_name (str): Text that goes on the button
        button_url (str): Button click redirect URL
        first_simple_speech (str): Speech text for the simple response
        first_simple_text (str): Text for the simple response

    Returns:
        str: JSON response string
    """    
    card = {
            "prompt": {
                "content": {
                    "card": {
                        "title": title,
                        "subtitle": subtitle,
                        "text": text,
                        "image": {
                            "url": image_url,
                            "alt": image_alt
                        },
                        "button": {
                            "name": button_name,
                            "open": {
                                "url": button_url
                            }
                        }
                    }
                },
                "firstSimple": {
                    "speech": first_simple_speech,
                    "text": first_simple_text
                }
            }
        }
    return json.dumps(card)

def card_response_nobutton(title, subtitle, text, image_url, image_alt, first_simple_speech, first_simple_text):
    """Returns a JSON response with a card that includes text and an image

    Args:
        title (str): Title text
        subtitle (str): Subtitle text under the title
        text (str): Paragraph text under the subtitle
        image_url (str): Small icon image URL
        image_alt (str): Alt text for the image
        first_simple_speech (str): Speech text for the simple response
        first_simple_text (str): Text for the simple response

    Returns:
        str: JSON response string
    """    
    card = {
            "prompt": {
                "content": {
                    "card": {
                        "title": title,
                        "subtitle": subtitle,
                        "text": text,
                        "image": {
                            "url": image_url,
                            "alt": image_alt
                        }
                    }
                },
                "firstSimple": {
                    "speech": first_simple_speech,
                    "text": first_simple_text
                }
            }
        }
    return json.dumps(card)

# ---------------------------------------------------------------------------- #
#                              Database functions                              #
# ---------------------------------------------------------------------------- #

# ------------------------------- Create tables ------------------------------ #
def create_users_table():
    """Create a users table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect('.data/database.db')
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT,
            password TEXT,
            base_url TEXT
        );
        """)

def create_classes_table():
    """Create a classes table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect('.data/database.db')
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            email TEXT,
            class TEXT,
            synonym TEXT
        );
        """)

def create_terms_table():
    """Create a terms table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect('.data/database.db')
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            email TEXT,
            term TEXT
        );
        """)

def create_recovery_table():
    """Create a recovery codes table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect('.data/database.db')
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS recovery (
            email TEXT,
            recovery_code TEXT
        );
        """)

def create_tables():
    """Create tables for users, classes, and terms table if they don't exist"""
    create_users_table()
    create_classes_table()
    create_terms_table()
    create_recovery_table()

# -------------------------------- User table -------------------------------- #
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

def delete_user_from_database(email):
    con = sql.connect('.data/database.db')
    # Password must also be provided to delete a user
    with con:
        con.execute("DELETE FROM users WHERE email = ?", (email,))

# Email and password verification function
def verify_email_and_password(email, password):
    """Checks the email against the password in the database to ensure that the user is allowed to perform an action

    Args:
        email (str): Email address of the user trying to perform an action
        password (str): Password of the user trying to perform an action

    Returns:
        bool: Whether the user is allowed to perform an action
    """    
    con = sql.connect('.data/database.db')
    with con:
        data = con.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        for row in data: return True # If a row exists where the email and password match, return True

# -------------------------------- Term table -------------------------------- #
def add_term_to_database(email, term):
    """Adds a term to the terms database for the user with the given email

    Args:
        email (str): Email address of the user
        term (str): Term from the form
    """    
    con = sql.connect('.data/database.db')
    with con:
        con.execute("INSERT INTO terms VALUES (?, ?)", (email, term))

def delete_term_from_database(email):
    """Removes any terms from the terms database if they exist for the user with the given email

    Args:
        email (str): Email to delete terms for
    """    
    con = sql.connect('.data/database.db')
    with con:
        con.execute("DELETE FROM terms WHERE email = ?", (email,))

def get_term_from_database(email):
    """Returns the term set for the user with the given email

    Args:
        email (str): Email address of the user

    Returns:
        str: Term set for the user
    """    
    con = sql.connect('.data/database.db')
    with con:
        data = con.execute("SELECT * FROM terms WHERE email = ?", (email,))
        for row in data: return row[1]

# ------------------------------- Classes table ------------------------------ #
def add_classes_to_database(email, classes):
    """Adds classes and synonyms to the classes database for the user with the given email

    Args:
        email (str): Email address of the user to add classes to
        classes (dict): Classes to be added to the user
    """    
    con = sql.connect('.data/database.db')
    with con:
        for class_name in classes:
            for synonym in classes[class_name]:
                con.execute("INSERT INTO classes VALUES (?, ?, ?)", (email, class_name, synonym))

def remove_classes_from_database(email):
    """Removes all classes and synonyms from the classes database for the user with the given email

    Args:
        email (str): Email address of the user to remove classes from
    """    
    con = sql.connect('.data/database.db')
    with con:
        con.execute("DELETE FROM classes WHERE email = ?", (email,))

def evaluate_class_from_synonym(email, synonym):
    """Returns the user's class name as it appears in PowerSchool for the given synonym

    Args:
        email (str): Email address of the user
        synonym (str): Class name synonym to evaluate

    Returns:
        str: Class name as it appears in PowerSchool
    """    
    con = sql.connect('.data/database.db')
    with con:
        data = con.execute("SELECT * FROM classes WHERE email = ? AND synonym = ?", (email, synonym))
        for row in data: return row[1] # If a row exists where the email and synonym match, return the class

# ------------------------------ Recovery table ------------------------------ #
def add_recovery_to_database(email, recovery_code):
    """Adds a term to the terms database for the user with the given email

    Args:
        email (str): Email address of the user
        recovery_code (int): Term from the form
    """    
    con = sql.connect('.data/database.db')
    with con:
        con.execute("INSERT INTO recovery VALUES (?, ?)", (email, recovery_code))

def delete_recovery_from_database(email):
    """Removes any recovery codes from the terms database if they exist for the user with the given email

    Args:
        email (str): Email to delete terms for
    """    
    con = sql.connect('.data/database.db')
    with con:
        con.execute("DELETE FROM recovery WHERE email = ?", (email,))

def get_code_from_database(email):
    """Returns the recovery code for the user with the given email

    Args:
        email (str): Email address of the user

    Returns:
        int: Recovery code for the user
    """    
    con = sql.connect('.data/database.db')
    with con:
        data = con.execute("SELECT * FROM recovery WHERE email = ?", (email,))
        for row in data: return row[1]

def verify_recovery(email, code):
    """Checks the recovery code for the user with the given email against the given code

    Args:
        email (str): Email address of the user
    """    
    con = sql.connect('.data/database.db')
    with con:
        data = con.execute("SELECT * FROM recovery WHERE email = ? AND recovery_code = ?", (email, code))
        for row in data: return True # If a row exists where the email and recovery code match, return True

# ----------------------------------- Main ----------------------------------- #
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)

create_tables()