from flask import Flask, request, redirect, url_for, render_template, flash, json, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from conexionsql import get_db_connection
import secrets
import os
import pathlib
from datetime import datetime
import requests
import googlemaps
import logging
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol 


app = Flask(__name__)
app.secret_key = "AvVoMrDAFRBiPNO8o9guscemWcgP"  
gmaps = googlemaps.Client(key='AIzaSyAjSN96XTz_okE3SwueGbWlk0w4is1TwiM')

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" #permite que haya trafico al local dev

GOOGLE_CLIENT_ID = "293860019099-619jug09l9s17q2jqtre8t4vid0mnhk3.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret_.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email","https://googleapis.com/auth/userinfo." "openid"],
    redirect_uri="http://localhost/callback"
)


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
    
    secret = "6LdSIWwqAAAAAAyR8FoP1i0-21eU5iNC0A6FxVnq"
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

#A PARTIR DE AQUI COMIENZAN LAS RUTAS 

@app.route("/callback_google")
def callback_google():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    Google_ID = id_info.get("sub")
    Full_Name = id_info.get("name")
    Email = id.info.get("email")
    name, middlename, lastname = Full_Name.split("",1) if " " in Full_Name else (Full_Name,"")
    return redirect("/login")

@app.route("/signup_google")
def signup_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)
@app.route("/login_google")
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/logout_google")
def logout_google():
    session.clear()
    return redirect("/")


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
    return render_template('signin.html',)
    

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

@app.route('/shop')
def shop():
    return render_template('shop.html')



if __name__ == '__main__':
    app.run(debug=True)