from flask import Flask, request, redirect, url_for, render_template, flash, json
from werkzeug.security import generate_password_hash, check_password_hash
from conexionsql import get_db_connection
import secrets
from datetime import datetime
import requests
import googlemaps
import logging

app = Flask(__name__)

<<<<<<< HEAD
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT ID_Estado, Nombre_Estado FROM Estado"
    cursor.execute(query)
    estadosearch = cursor.fetchall()

    if request.method == 'POST':
        Name      = request.form['Name']
        PrimerApellido   = request.form['PrimerApellido']
        SegundoApellido   = request.form['SegundoApellido']
        Email       = request.form['Email']
        Password  = request.form['Password']
        print(f"Registrando: {Name}, {PrimerApellido}, {SegundoApellido}, {Email},")
        if register_user(Name, PrimerApellido, SegundoApellido, Email, Password,):
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
=======



>>>>>>> f9aa4c194b24f85cf8de6c063143ec45a0800e6d

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
def cart():
    return render_template('cart.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/myprofile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)