from flask import Flask, json, session, abort, flash, redirect
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

    
def register_user(Nombre, PrimerApellido, SegundoApellido, Email, Password):
    conn = get_db_connection()
    cursor = conn.cursor()

    password_hash = generate_password_hash(Password)
    register_user = "EXEC Registrar_Usuario ?, ?, ?, ?, ?" 
    try:
        cursor.execute(register_user, (Nombre, PrimerApellido, SegundoApellido, Email, password_hash,))
        result = cursor.fetchone()
        print(f"Resultado del procedimiento almacenado: {result}")
        
        if result and result[0] == 0:
            conn.commit()
            logging.info("Usuario registrado con éxito.")
            return True
        elif result and result[0] == 1:
            conn.rollback()
            print("El correo ya existe.")
            return False
        else:
            print("Error en el registro del usuario o resultado inesperado.")
            return False
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
def get_user_by_email_and_password(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID_Persona, Email, Password FROM Persona WHERE Email = ?", email)
    user = cursor.fetchone()
    # Verifica si se encontró un usuario y si la contraseña coincide
    if user and check_password_hash(user.Password, password):  # Utiliza una función de hashing para verificar la contraseña
        return {'ID_Persona': user.ID_Persona, 'Email': user.Email}
    else:
        print("El Email y la contraseña no coinciden")
        return None

def login_user(email, password):
    user = get_user_by_email_and_password(email, password)
    if user:
        session['user_id'] = user['ID_Persona']
        return True
    else:
        print("Aqui falla")
        return False
def get_user_by_id(user_id):
    conn = None
    user = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Nombre, Email FROM Persona WHERE ID_Persona = ?", (user_id,))
        result = cursor.fetchone()
        
        # Si se encuentra un usuario, convertirlo en un diccionario
        if result:
            user = {
                'name': result[0],  # Nombre
                'email': result[1]  # Email
            }
    except Exception as e:
        print(f"Ocurrió un error al obtener el usuario: {e}")
    finally:
        if conn:
            conn.close()
    
    return user