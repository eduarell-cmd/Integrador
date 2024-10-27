from flask import Flask, request, redirect, url_for, render_template, flash, json
from werkzeug.security import generate_password_hash, check_password_hash
from conexionsql import get_db_connection
import secrets
from datetime import datetime
import requests
import googlemaps
import logging

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
gmaps = googlemaps.Client(key='AIzaSyAjSN96XTz_okE3SwueGbWlk0w4is1TwiM')


logging.basicConfig(level=logging.DEBUG)

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
    
    secret = "6Ldyi2AqAAAAAD2CKEoOADOlBpkmNmZ7A1f9jAhb"
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']


#A PARTIR DE AQUI COMIENZAN LAS RUTAS 

