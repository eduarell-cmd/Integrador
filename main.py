from flask import Flask, request, redirect, url_for, render_template, flash, session, abort
from auth import register_user, verify_user, is_human, login_user, get_user_by_id
from dotenv import load_dotenv
load_dotenv()
import os
import requests
import googlemaps
import logging
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol 
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

admin_key = os.getenv("ADMIN_KEY")

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

@app.route("/signup_google")
def signup_google():
    authorization_url, state = flow.authorization_url(prompt='consent')
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback_google")
def callback_google():
    try:
        # Step 1: Fetch token
        flow.fetch_token(authorization_response=request.url)
        logging.info("Step 1: Fetched token successfully.")
        
        # Step 2: Validate state
        if session.get("state") != request.args.get("state"):
            logging.error("Session state does not match.")
            abort(500)  # State does not match

        # Step 3: Retrieve credentials and initialize token request
        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)
        logging.info("Step 3: Credentials and token request initialized.")
        
        # Step 4: Verify the ID token
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=client_id
        )
        logging.info("Step 4: ID token verified.")

        # Step 5: Extract user information
        google_ID = id_info.get("sub")
        full_name = id_info.get("name")
        email = id_info.get("email")
        name_parts = full_name.split(" ")
        nombre = name_parts[0]
        primer_apellido = name_parts[1] if len(name_parts) > 1 else ""
        segundo_apellido = name_parts[2] if len(name_parts) > 2 else ""
        logging.info(f"Step 5: User info - Name: {nombre}, Email: {email}")

        # Step 6: Register or log in the user
        if register_user(nombre, primer_apellido, segundo_apellido, email):
            session["google_id"] = google_ID
            session["name"] = full_name
            flash("Registro exitoso con Google.", "success")
            logging.info("Step 6: User registered successfully.")
            return redirect(url_for('index'))
        else:
            flash("El usuario ya existe o hubo un error", "error")
            logging.error("Step 6: User registration failed.")
            return render_template("signin.html")
    
    except ValueError as e:
        logging.error(f"ValueError during ID token verification: {e}")
        return "Error de autenticación.", 401
    except Exception as e:
        logging.error(f"Unexpected error in callback_google: {e}")
        return "Internal server error.", 500



@app.route("/logout_google")
def logout_google():
    session.clear()
    return redirect("/")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
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
    return render_template('signin.html',)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    sitekey = "6Ldyi2AqAAAAAEJrfFUi_p05WKVJNk8n_n2M2fYn"

    if request.method == 'POST':
        Email      = request.form['Email']
        Contraseña = request.form['Password']
        captcha_response = request.form['g-recaptcha-response']
        if login_user(Email, Contraseña) and is_human(captcha_response):
            return redirect(url_for('dashboard',))
        else:
            flash("¿Inicio de sesión fallido! Porfavor revisa que tu Email y Contraseña sean correctas")
    return render_template('login.html', sitekey=sitekey)

@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
    

    return render_template('reset_request.html')
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/protectedarea')
def protected_area():
    return "Protected!"

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


@app.route('/perfil')
def perfil():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirige a login si no hay usuario en sesión
    
    # Consulta los datos del usuario desde la base de datos
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))

    return render_template('profile.html', user=user)


@app.route(f'/{admin_key}')
def admin_dashboard():
     return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)