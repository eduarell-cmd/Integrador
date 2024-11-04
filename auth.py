from flask import Flask, request, redirect, url_for, render_template, flash, json, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from conexionsql import get_db_connection
from dotenv import load_dotenv
load_dotenv()
import os
import pathlib
from datetime import datetime
import requests
import googlemaps
import logging
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol 

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")


app = Flask(__name__)
app.secret_key = "AvVoMrDAFRBiPNO8o9guscemWcgP"  
gmaps = googlemaps.Client(key='AIzaSyCtOf_oaXQJd9iO83RzKtdWBsRk8R3EqYA')

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" #permite que haya trafico al local dev

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

flow = Flow.from_client_config(
    client_config={
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "http://localhost:5000/callback_google", 
                "http://127.0.0.1:5000/callback_google"
            ],
            "userinfo_uri": "https://openidconnect.googleapis.com/v1/userinfo",
            "scopes": [
                "openid", 
                "https://www.googleapis.com/auth/userinfo.email", 
                "https://www.googleapis.com/auth/userinfo.profile"
            ]
        }
    },
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_uri="http://localhost:5000/callback_google"  
)


def register_usergoogle(GoogleID, Nombre, PrimerApellido, SegundoApellido):
    conn = get_db_connection()
    cursor = conn.cursor()

    
def register_user(Nombre, PrimerApellido, SegundoApellido, Email, Password,):
    conn = get_db_connection()
    cursor = conn.cursor()

    password_hash = generate_password_hash(Password)
    register_user = "EXEC Registrar_Usuario ?, ?, ?, ?, ?, ?" 
    Fecha_Registro = datetime.now()
    try:
        cursor.execute(register_user, (Nombre, PrimerApellido, SegundoApellido, Email, password_hash, Fecha_Registro))
        result = cursor.fetchone()
        if  result == 0:
            conn.commit()
            logging.info("Usuario registrado con éxito.")
            return True
        if result == -1:
            conn.rollback()
            print(f"El correo ya existe.")
    except Exception as e:
        logging.error(f"Error durante la inserción de usuario: {e}")
        return False
    finally:
        conn.close()
def verify_user(Email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT Contraseña FROM Usuario WHERE Email = ?"
    cursor.execute(query, (Email,))
    result = cursor.fetchone()

    if result and  check_password_hash(result[0], password):
        return True
    conn.close()
    return False

def is_human(captcha_response):
    
    secret = "6LdSIWwqAAAAAI4hs5hE33Y_-vH_aRy79pbX6xzo"
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper