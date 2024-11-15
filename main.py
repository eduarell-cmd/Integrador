from flask import Flask, request, redirect, url_for, render_template, flash, session, abort
from auth import *
from dotenv import load_dotenv
import mail
load_dotenv()
import os
import requests
import googlemaps
import logging
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol 
from flask_mail import Message
from seller import *
#from conexionsql.models import User
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
from conexionsql import connection
admin_key = os.getenv("ADMIN_KEY")
from mail import *
app = Flask(__name__)
app.secret_key = "AvVoMrDAFRBiPNO8o9guscemWcgP"  
gmaps = googlemaps.Client(key='AIzaSyCtOf_oaXQJd9iO83RzKtdWBsRk8R3EqYA')
s = URLSafeTimedSerializer(app.secret_key)
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
        captcha_response = request.form['g-recaptcha-response']
        print(f"Registrando: {Name}, {PrimerApellido}, {SegundoApellido}, {Email},")
        if register_user(Name, PrimerApellido, SegundoApellido, Email, Password,) and is_human(captcha_response): #Lo mismo que login
            flash("¡Se ha registrado exitosamente! Ahora puede iniciar sesion.", "success")
            return redirect(url_for('login'))
        else:
            flash("Ha habido un error durante el registro, el correo ya está en uso.","error")
    return render_template('signin.html',)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Estoy en login")
    sitekey = "6LdSIWwqAAAAAI4hs5hE33Y_-vH_aRy79pbX6xzo"
    if request.method == "POST":
        print("hola buenos días")
        Email      = request.form['Email']
        Contraseña = request.form['Password']
        captcha_response = request.form['g-recaptcha-response']
        print(f"No está agarrando{captcha_response}")
        if login_user(Email, Contraseña) and is_human(captcha_response):
            print(login_user(Email, Contraseña), is_human(captcha_response))
            return redirect(url_for('perfil',))
        else:
            flash("¿Inicio de sesión fallido! Porfavor revisa que tu Email y Contraseña sean correctas")
        return render_template('login.html', sitekey=sitekey)
    return render_template('login.html', sitekey=sitekey)
@app.route('/logout')
def logout():
    ID_Persona = session.get('user_id')
    if ID_Persona:
        user = get_user_by_email(ID_Persona)
        email = user['email'] if user else None
        session.pop('user_id', None)
        session.clear()
        flash("Has cerrado sesión exitosamente", "info")
        return redirect(url_for('index'))     

@app.route('/reset_request')
def reset_request():
    conn=connection 
    cursor = conn.cursor()
    Mail()
    if request.args.get("Email"):
        Email = request.args.get('Email')
        sqlquery= "SELECT Password FROM Persona WHERE Email = '"+Email+"'"
        user = cursor.execute(sqlquery)
        if user:
            token = s.dumps(Email, salt='password-reset-salt')
            link = url_for('reset_password', token=token, _external=True)
            class _MailMixin:
                def send(self,Message):
                    print("ya estoy lleno")
                    msg = Message(subject="Password Reset Request",
                          sender="farmtable79@gmail.com",
                          recipients=[Email],
                          body=f'Click the link to reset your password: {link}')
                    with app.app_context():
                        try:
                            mail.send(msg)
                           
                        except Exception as e:
                            print(e)

                flash('An email with instructions to reset your password has been sent.', 'info')
            return render_template('login.html')

        flash('This email is not registered with us.', 'danger')

    return render_template('reset_request.html')

@app.route('/reset_request/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn=connection
    try:
        # Validar el token y obtener el correo electrónico
        Email = s.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hora de validez
    except:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        cursor = conn.cursor()
        Password = request.form['Password']
        user = "SELECT Contraseña FROM Usuario WHERE Email = ?"
        cursor.execute(user, (Password,Email))
        if user:
            # Cambiar la contraseña del usuario
            query = "UPDATE Persona SET Password = ? WHERE Email = ?"
            user.password = generate_password_hash(Password)
            params = (user.password, Email)
            cursor.execute(query, (params))
            conn.session.commit()

            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/')
def index():
    conn=connection
    cursor = conn.cursor()
    query = "SELECT Foto_Vendedor from Vendedor WHERE ID_Vendedor <= 6"
    cursor.execute(query)
    rows=cursor.fetchall()
    return render_template('index.html',Vendedores=rows)

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

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        # Recibe los datos del formulario
        nombre = request.form.get('Name')
        primer_apellido = request.form.get('PrimerApellido')
        segundo_apellido = request.form.get('SegundoApellido')
        
        # Llama a la función para actualizar los datos en la base de datos
        success = update_user_name(user_id, nombre, primer_apellido, segundo_apellido)
        
        # Si la actualización es exitosa, redirige o muestra un mensaje
        if success:
            flash('Perfil actualizado con éxito', 'success')
            return redirect(url_for('perfil'))
        else:
            flash('Error al actualizar el perfil', 'error')
    
    # Si es una solicitud GET, carga los datos del usuario
    user = get_user_by_id(user_id)
    return render_template('edit-profile.html', user=user)

@app.route(f'/{admin_key}')
def admin_dashboard():
     return render_template('admin.html')

@app.route('/register_seller', methods=['GET','POST'])
def register_seller():
    #DATA 
    if request.method == 'POST':
        try:
            name = request.form['name']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            phone = request.form['phone']
            birthdate = request.form['birthdate']
            #FILES
            ine_file = request.files['ine']
            address_prof = request.files['comprobante']
            licenceA = request.files['licenciaA']
            licenceT = request.files['licenciaT']

            if ine_file:
                print("INE file received")
            if address_prof:
                print("Comprobante file received")
            if licenceA:
                print("Licencia A file received")
            if licenceT:
                print("Licencia T file received")

            #Google Cloud Storage (Upload)
            ine_file = upload_file_to_bucket(ine_file, f"docs/{name}_INE.jpg")
            address_prof = upload_file_to_bucket(address_prof, f"docs/{name}_addressprof.jpg")
            licenceA = upload_file_to_bucket(licenceA, f"docs/{name}_licenseA.jpg")
            licenceT = upload_file_to_bucket(licenceT, f"docs/{name}_licenseT.jpg")

            flash('Vendedor registrado exitosamente!', 'success')
            return redirect(url_for('some_success_page'))  # Redirigir después del registro exitoso

        except ValueError as e:
            flash(str(e), 'error')  # Manejo de error si el tipo de archivo no es válido
            return redirect(url_for('register_seller'))

        except Exception as e:
            flash(f'Ocurrió un error: {str(e)}', 'error')  # Manejo de otros errores
            return redirect(url_for('register_seller'))
        
    return render_template('register_seller.html')

if __name__ == '__main__':
    app.run(debug=True)