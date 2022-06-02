from flask import Flask, request # webhook
import pywerschool # gets student info
import studentParser # parses the pywerschool response
import json
import os # for loading the .env file
from dotenv import load_dotenv # for loading the .env file
from google.auth import jwt # for decoding the token
import sqlite3 as sql # for database
import urllib.request # for getting PEM certs
import logging

# Get environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

GOOGLE_CLIENT_ID = os.environ.get("DASHBOARD_API_URL_CLIENT_ID") # for audience when decoding token
WEB_INTERFACE_URL = os.environ.get("DASHBOARD_API_WEB_INTERFACE_URL") # for card responses with link to web interface
DATABASE_PATH = os.environ.get("DATABASE_PATH") # for accessing the database which is in a higher shared directory

PEM_CERTS_URL = 'https://www.googleapis.com/oauth2/v1/certs' # URL to get the PEM certs from

LOG_LEVEL = os.environ.get("DASHBOARD_API_LOG_LEVEL", 'WARNING') # setting the log level based on the environment variable

logging.basicConfig(filename='log.log', level=LOG_LEVEL) # setting the log level based on the environment variable

app = Flask(__name__) # Create a flask app to handle the webhook

# ---------------------------------------------------------------------------- #
#                                  App routes                                  #
# ---------------------------------------------------------------------------- #

# Google Actions webhook
@app.route('/endpoint', methods=['POST'])
def endpoint():
    header = request.headers # Get the header for decoding the token for the email
    content = request.get_json() # Get the content of the POST request for finding what class the user wants
    response = handleRequest(content, header) # Handle the request
    return response, 200 # Return the response

# Wake route is leftover from Glitch, kept to test if the server is online
@app.route('/wake', methods=['GET'])
def wake():
    logging.debug("Wake route called")
    return "Woken", 200

# In case the /endpoint route needs to do multiple things, this function can be used to handle them based on the handler entered in the Actions Console
def handleRequest(content, header):
    handler = content['handler']['name']
    if handler == "get_grade":
        return get_grade(content, header)

def get_student(username, password, base_url):
    """Gets the student object from the pywerschool module

    Args:
        username (str): Username of the user
        password (str): Password of the user
        base_url (str): URL of the user's school to log into

    Returns:
        OrderedDict: Student information
    """    
    client = pywerschool.Client(base_url)
    student = client.getStudent(username, password, toDict=True)
    return student

def get_grade(content, header):
    """Returns a JSON response with a card that includes text, an image, and a button.

    Args:
        content (dict): The content of the POST request
        header (str?/dict?): The header of the POST request obtained by request.headers

    Returns:
        str: JSON response string
    """    
    # Try to get the email of the user from the Google Actions header
    try: email = get_email(header)
    except Exception: return simple_response("Sorry, I couldn't verify your email address. Please try again later.")

    # Get the user's information from the database
    username, password, base_url = get_user_from_database(email) # Get the user's email address from Google's header

    # Ensure the user has already entered their information, if not, direct them to the web interface
    if username == None or password == None or base_url == None: # If the user's registration is incomplete, prompt them to sign up
        logging.warning("User registration is incomplete. Returning link to web interface.")
        register_card = card_response_button("Finish Account Linking", "Please register", "Go to {} to enter your login information.".format(WEB_INTERFACE_URL), "https://img.icons8.com/fluency/96/000000/urgent-property.png", "Register warning icon", "Finish", WEB_INTERFACE_URL)
        return register_card
    
    # Try to identify the class the user is trying to get the grade for
    try: synonym = content['intent']['params']['class']['resolved']
    except KeyError:
        logging.error("No class was found in the POST request. Returning error response.")
        return simple_response("Sorry, something went wrong while interpreting your request. Please try again later.")

    section_name = evaluate_class_from_synonym(email, synonym) # Convert the general class synonym to the specific section name

    # Now get the student's information (slow so do it late)
    student = get_student(username, password, base_url)
    parser = studentParser.StudentParser(student)

    # Get the current term from the database
    term_name = get_term_from_database(email)

    # Get the grade for the class
    grade = parser.getGrade(parser.convertNameAndSection(section_name), parser.convertTermNameToIds(term_name))

    # grade looks like: ['letter', 'percent']
    percent = str(int(grade[1]))
    letter = grade[0]

    # Get the right image based on the grade letter
    if letter in ["A", "B", "C", "D", "E"]: letter_name = letter
    else:
        logging.warning("Grade letter is not A, B, C, D, or E. Using question mark image instead.")
        letter_name = "unknown"
    letter_image_url = f"https://raw.githubusercontent.com/PicoPlanetDev/dashboard-api/master/grade_letters/{letter_name}.png"

    # Create the card response
    responseText = f"You have a {percent} percent in {section_name}."
    jsonResponse = card_response_nobutton(section_name, f"{percent} percent", responseText, letter_image_url, letter, responseText, responseText)

    return jsonResponse

def get_pem_certs():
    """Fetches the current Google OAuth2 PEM certs.

    Returns:
        dict: dictionary of current Google OAuth2 PEM certs.
    """    
    with urllib.request.urlopen(PEM_CERTS_URL) as response:
        return json.loads(response.read())

def get_email(header):
    """Gets the email address of the user by decrypting the token in the header.

    Args:
        header (str?/dict?): The header of the POST request obtained by request.headers

    Returns:
        str: User's email address
    """    
    try:
        authorization = header['Authorization']
        claims = jwt.decode(authorization, certs=get_pem_certs(), audience=GOOGLE_CLIENT_ID)
        return claims['email']
    except: # Normally you would just return None here
        try:
            logging.warning("Failed to decode token, trying to get debug email from header")
            return header['Email'] # But because I can't generate Google tokens for my email and they expire, I'll allow this
        except:
            logging.error("Email address could not be decrypted from the token, and no debug email was found in the header.")
            raise Exception("Email address could not be decrypted from the token.")

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
def get_user_from_database(email):
    """Gets the user's information from the database.

    Args:
        email (str): User's email address

    Returns:
        tuple: (username, password, base_url)
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM users WHERE email = ?", (email,))
        for row in data: return row[1], row[2], row[3] # There should only be one row that matches the email
    # If we get here, the email was not found in the database
    logging.warning(f"Email {email} was not found in the database.")
    return None, None, None # If there is no user, return None, None, None which should ask the user to create an account

# Email and password verification function
def verify_email_and_password(email, password):
    """Checks the email against the password in the database to ensure that the user is allowed to perform an action

    Args:
        email (str): Email address of the user trying to perform an action
        password (str): Password of the user trying to perform an action

    Returns:
        bool: Whether the user is allowed to perform an action
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        for row in data: return True # If a row exists where the email and password match, return True
    # If we get here, the email and password do not match
    logging.warning(f"Email {email} and password {password} do not match in the database.")
    return False # If no row exists, return False

def get_term_from_database(email):
    """Returns the term set for the user with the given email

    Args:
        email (str): Email address of the user

    Returns:
        str: Term set for the user
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM terms WHERE email = ?", (email,))
        for row in data: return row[1]

def evaluate_class_from_synonym(email, synonym):
    """Returns the user's class name as it appears in PowerSchool for the given synonym

    Args:
        email (str): Email address of the user
        synonym (str): Class name synonym to evaluate

    Returns:
        str: Class name as it appears in PowerSchool
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM classes WHERE email = ? AND synonym = ?", (email, synonym))
        for row in data: return row[1] # If a row exists where the email and synonym match, return the class
