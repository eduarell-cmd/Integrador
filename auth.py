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
gmaps = googlemaps.Client(key='AIzaSyD7CFCehn95fEwY_NvsjADekfUaXDmBE4Y')


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
def verify_user(Email, contraseña):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT Contraseña FROM Usuario WHERE Email = ?"
    cursor.execute(query, (Email,))
    result = cursor.fetchone()

    if result and  check_password_hash(result[0], contraseña):
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT ID_Estado, Nombre_Estado FROM Estado"
    cursor.execute(query)
    estadosearch = cursor.fetchall()

    if request.method == 'POST':
        Nombre      = request.form['Nombre']
        ApellidoP   = request.form['ApellidoP']
        ApellidoM   = request.form['ApellidoM']
        Email       = request.form['Email']
        Contraseña  = request.form['Contraseña']
        Estado_ID_Estado = request.form['Estado_ID_Estado']
        Ciudad      = request.form['Ciudad']
        Latitud     = request.form['Latitude']
        Longitud    = request.form['Longitude']
    
        print(f"Registrando: {Nombre}, {ApellidoP}, {ApellidoM}, {Email}, {Ciudad}, {Latitud}, {Longitud}")
        if register_user(Nombre, ApellidoP, ApellidoM, Email, Contraseña, Estado_ID_Estado, Ciudad, Latitud, Longitud):
            flash("¡Se ha registrado exitosamente! Ahora puede iniciar sesion.", "success")
            return redirect(url_for('login'))
        else:
            flash("Ha habido un error durante el registro, el correo ya está en uso.","error")
    
    conn.close()
    return render_template('signin.html', estado=estadosearch)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    sitekey = "6Ldyi2AqAAAAAEJrfFUi_p05WKVJNk8n_n2M2fYn"

    if request.method == 'POST':
        Email      = request.form['Email']
        Contraseña = request.form['Contraseña']
        captcha_response = request.form['g-recaptcha-response']
        if verify_user(Email, Contraseña) and is_human(captcha_response):
            return redirect(url_for('dashboard',))
        else:
            flash("¿Inicio de sesión fallido! Porfavor revisa que tu Email y Contraseña sean correctas")
    return render_template('login.html', sitekey=sitekey)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contactus')
def contacto():
    return render_template('contact.html')

@app.route('/checkout')
def checkout():
    return render_template('chackout.html')

@app.route('/cart')
def carro():
    return render_template('cart.html')



if __name__ == '__main__':
    app.run(debug=True)