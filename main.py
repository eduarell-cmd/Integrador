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
from profilee import update_user_name
from seller import *
from products import *
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from conexionsql import connection
from profilee import update_user_name
from mail import *
from admin import *
import pyodbc
admin_key = os.getenv("ADMIN_KEY")
client_id = os.getenv("GOOGLE_CLIENT_ID", "admin_dashboard")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
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
        if register_user(Name, PrimerApellido, SegundoApellido, Email, Password,) and is_human(captcha_response): #Nomas para que me deje pushear
            flash("¡Se ha registrado exitosamente! Ahora puede iniciar sesion.", "success")
            return redirect(url_for('login'))
        else:
            flash("Ha habido un error durante el registro, el correo ya está en uso.","error")
    return render_template('signin.html',)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Estoy en login")
    sitekey = "6LdSIWwqAAAAAI4hs5hE33Y_-vH_pbX6xzo"
    if request.method == "POST":
        print("hola buenos días")
        Email      = request.form['Email']
        Contraseña = request.form['Password']
        captcha_response = request.form['g-recaptcha-response']
        print(f"No está agarrando{captcha_response}")
        if not captcha_response:
            return render_template('login.html')
        if login_user(Email, Contraseña) and is_human(captcha_response):
            print(login_user(Email, Contraseña), is_human(captcha_response))
            return redirect(url_for('perfil',))
        else:
            flash("¡Inicio de sesión fallido! Porfavor revisa que tu Email y Contraseña sean correctas")
        return render_template('login.html', sitekey=sitekey)
    return render_template('login.html', sitekey=sitekey)
@app.route('/logout')
def logout():
    ID_Persona = session.get('user_id')
    if not ID_Persona:
        print("Aqui falla /logout")
        return redirect(url_for('login'))
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
    query = "Exec Vendedormuestra"
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

@app.route('/locationvp', methods=['GET'])
def ubicacion_pv():
    conn = connection
    cursor = conn.cursor()
    query = "EXEC MuestraTienda"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Obtener el índice del producto desde el parámetro de consulta
    productid = int(request.args.get('productid', 0))  # Por defecto, 0
    producto_seleccionado = rows[productid]

    return render_template('seller_location.html', productos=rows, Producto=producto_seleccionado)



@app.route('/perfilvend', methods=['GET', 'POST'])
def perfilvend():
    user_id = session.get('user_id')
    seller_id = get_seller_by_id(user_id)
    point_id = get_point_by_id(seller_id)
    products = get_products_by_point_id(point_id)
    phone = get_phone_by_seller_id(seller_id)

    if not user_id:
        return redirect(url_for('login'))  # Redirige a login si no hay usuario en sesión
    if not seller_id:
        return redirect(url_for('perfil'))
    # Consulta los datos del usuario desde la base de datos
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    if not point_id:
        flash("No tienes productos asignados a un punto de venta.",)

    return render_template('profile-vendedor.html', user=user, products=products, phone=phone)

@app.route('/addproduct', methods=['GET', 'POST'])
def add_product():
    user = session.get('user_id')
    if not user:
        return redirect(url_for('login'))
    seller_id = get_seller_by_id(user)
    if not seller_id:
        return redirect(url_for('perfil'))
    point_id = get_point_by_id(seller_id)
    if not point_id:
        flash("No tienes productos asignados a un punto de venta.",)
        return redirect(url_for('perfil'))
    if request.method == 'POST':
        nombre_producto = request.form['nombre']
        categoria_id = request.form['categoria']  # 'frutas' o 'verduras'
        precio = request.form['precio']
        stock = request.form['stock']
        disponibilidad = request.form['disponible']
        imagenpr = request.files['imagenpr']

        extensionimg = get_extension_for_img(imagenpr)
        user = get_user_by_id(session['user_id'])
        Gimagen_file = upload_file_to_bucket(imagenpr, f"img/products/{user['name'], user['lastname'], user['slastname']}/{"product[3]", "product[4]"}_Imgproduct.{extensionimg['product_extension']}")
        product = get_products_by_point_id(point_id)

        id_punto_venta = get_point_by_id(seller_id)
        added_product = add_producto(nombre_producto, id_punto_venta, categoria_id, precio, stock, disponibilidad, Gimagen_file)
        if added_product:
            print("Se ha añadido punto de venta")
            return redirect(url_for('add_product'))
        return redirect (url_for('add_product'))
    return render_template('add-product.html', user=user)

@app.route('/editproduct', methods=['GET','POST'])
def edit_product():   
    product_id=request.args.get("product_id")
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirige a login si no hay usuario en sesión
    seller_id = get_seller_by_id(user_id)   
    product ={"Esta es el producto que tenemos hasta el momento"}
     
    if not seller_id:
        return redirect(url_for('perfil'))
    # Consulta los datos del usuario desde la base de datos
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))

    point_id = get_point_by_id(seller_id)
    if not point_id:
        flash("No tienes productos asignados a un punto de venta.", "error")
        return redirect(url_for('perfilvend'))
    # Obtener los productos del punto de venta
    product = get_products_by_point_id(point_id)
    if request.method == 'POST':
        # Actualización del producto
        product_id = request.form['product_id']
        nombre_producto = request.form['nombre']
        categoria_id = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']
        disponibilidad = request.form['disponible']
        if disponibilidad == 'True' or disponibilidad == '1':
            disponibilidad = 1
        else:
            disponibilidad = 0
        imagenpr = request.files.get('imagenpr')
        print(f"El valor de imagen{imagenpr}")
        
        if imagenpr and imagenpr.filename != '':
            # Obtener extensión y subir la nueva imagen
            extensionimg = get_extension_for_img(imagenpr)
            Gimagen_file = upload_file_to_bucket(imagenpr, f"img/products/{user['name'], user['lastname'], user['slastname']}/{"product[3], product[4]"}_Imgproduct.{extensionimg['product_extension']}")
        else:
            conn = connection
            cursor = conn.cursor()
            cursor.execute("SELECT Foto_Producto FROM Producto WHERE ID_Producto = ?",(product_id,))
            result = cursor.fetchone()

            if result:
                Gimagen_file = result[0]
            else:
                Gimagen_file = ""
        # Actualizar producto
        id_punto_venta = get_point_by_id(seller_id)
        print(f"estos son tus datos{int(product_id), id_punto_venta, nombre_producto, int(categoria_id), int(precio), int(stock), disponibilidad, Gimagen_file}")
        updated = editar_producto(int(product_id), id_punto_venta, nombre_producto, int(categoria_id), int(precio), int(stock), disponibilidad, Gimagen_file)
        if updated:
            flash("Producto actualizado con éxito", "success")
            return redirect(url_for('perfilvend'))
        else:
            flash("Error al actualizar el producto", "error")
        return redirect(url_for('edit_product'))
    if request.args.get("product_id"):
            for producto in product:
                if(producto['id'] == int(request.args.get("product_id"))):
                    product = producto
        #        print(product['id'])
        #print(product)
    return render_template('edit-product.html', user=user, products=product)


@app.route('/delproduct', methods=['POST'])
def delete_product():
    conn=connection
    cursor = conn.cursor()
    id_producto = request.form.get('ID_Producto')
    try:
        cursor.execute("DELETE FROM Producto WHERE ID_Producto = ?", (id_producto))
        conn.commit()
        print("Registro eliminado exitosamente.")
        flash(f"Registro eliminado exitosamente.")
    except pyodbc.Error as error:
        print("Error al eliminar el registro:", error)
        flash(f"Error al eliminar el registro: {str(error)}")
    return redirect(url_for('perfilvend'))

    
@app.route('/cart')
def carro():
    return render_template('cart.html')

@app.route('/shop', methods=['GET'])
def shop():
    conn=connection
    cursor = conn.cursor()
    consulta = request.args.get('q', None) or ''
    query = "EXEC MuestraTienda @consulta = ?"
    cursor.execute(query, (consulta,))
    rows=cursor.fetchall()
    return render_template('shop.html',Productos=rows,consulta=consulta)

@app.route('/shop/frutas')
def shopfrutas():
    conn=connection
    cursor = conn.cursor()
    consulta = request.args.get('q', None) or ''
    query = "EXEC OnlyFrutas @consulta = ?"
    cursor.execute(query, (consulta,))
    rows=cursor.fetchall()
    return render_template('shop.html',Productos=rows,consulta=consulta)

@app.route('/shop/verduras')
def shopverduras():
    conn=connection
    cursor = conn.cursor()
    consulta = request.args.get('q', None) or ''
    query = "EXEC OnlyVerduras @consulta = ?"
    cursor.execute(query, (consulta,))
    rows=cursor.fetchall()
    return render_template('shop.html',Productos=rows,consulta=consulta)




@app.route('/perfil')
def perfil():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirige a login si no hay usuario en sesión
    
    seller_id = get_seller_by_id(user_id)
    if seller_id:
        return redirect(url_for('perfilvend'))
    # Consulta los datos del usuario desde la base de datos
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    consumer_id = get_consumer_by_id(user_id)
    request = get_request_by_consumer(consumer_id)
    print(f"El valor de request:{request}")
        
    return render_template('profile.html', user=user, request=request)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    seller_id = get_seller_by_id(user_id)
    if seller_id:
        return redirect(url_for('perfilvend'))
    if not user_id:
         return redirect(url_for('login'))
    
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

@app.route(f'/{admin_key}', methods=['GET', 'POST'])
def admin_dashboard():
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    admin = get_admin_by_id(user_id)
    if not admin:
        print("No hay admin")
        return redirect(url_for('index'))
    requests = get_pending_requests()
    if request.method == 'POST':
        ID_Solicitud = request.form.get('ID_Solicitud')
        
        comentario = request.form.get('comentario')
        
        accion = request.form.get('accion')
        print(f"Vaya cagada:{ID_Solicitud}{comentario}{accion}")
        parametros =(int(ID_Solicitud),comentario,admin[0])

        
        if accion == 'rechazar':
            reject = reject_seller_request_db(*parametros)
            if reject:
                flash("Soliciud rechazada")
        elif accion == 'aceptar':
            accept = accept_request_seller(*parametros)
            if not accept:
                flash("No se pudo aceptar")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin.html', admin=admin, solicitudes=requests)

@app.route(f'/{admin_key}/reject_seller', methods=['POST'])
def reject_seller():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    admin = get_admin_by_id(user_id)
    if not admin:
        print("No hay admin")
        return redirect(url_for('index'))
    
    
    return redirect (url_for('admin_dashboard'))


@app.route(f'/{admin_key}/accept_seller', methods=['POST'])
def accept_seller():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    admin = get_admin_by_id(user_id)
    if not admin:
        print("No hay admin")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        ID_Solicitud = request.form.get('ID_Solicitud')
        
        comentario = request.form.get('comentario')
        
        print(f"Vaya cagada:{ID_Solicitud}{comentario}")
        parametros =(int(ID_Solicitud),comentario,admin[0])

        accept = accept_request_seller(*parametros)
        if not accept:
            flash("Error no se pudo acept solicitud")
        flash("Soliciud aceptada")
    return redirect (url_for('admin_dashboard'))

@app.route('/register_seller', methods=['GET','POST'])
def register_seller():
    #DATA 
    print("Register ruta")
    user_id = session.get('user_id')
    if not user_id:
         return redirect(url_for('login'))
    seller_id = get_seller_by_id(user_id)
    if seller_id:
        return redirect(url_for('perfilvend'))
    
    ID_Consumer = get_consumer_by_id(user_id)
    Seller_Point = get_request_by_consumer(ID_Consumer)
    rowstates = get_all_states()
    Temporary_ID = get_temporary_by_consumer_id(ID_Consumer)
    info_request = get_info_request_by_temporary_id(Temporary_ID)
    if info_request:
        return redirect (url_for('edit_request_seller'))
    if Seller_Point == -1:
        flash("Ya tienes una solicitud pendiente, espera a que sea aceptada o rechazada")
        return redirect(url_for('perfil'))
    
    try:
        if request.method == 'POST':
            print("Estoy en POST (registerseller)")
            #DATOS
            phone = request.form['phone']
            birthdate = request.form['birthdate']
            estado = request.form['estado']
            ciudad = request.form['ciudad']
            #FILES
            ine_file = request.files['ine']
            address_prof = request.files['comprobante']
            licenceA = request.files['licenciaA']
            licenceT = request.files['licenciaT']
            
            print(f"Registrando: {phone}, {birthdate}, {ine_file}, {address_prof}, {licenceA}, {licenceT}")
            user = get_user_by_id(session['user_id'])
            #Google Cloud Storage (Upload)
            if not user:
                print("Error no agarro user")
            print(user['name'])
            print("Si agarro el user")
            
            extension = get_extension(ine_file, address_prof, licenceA, licenceT)
            print("Esta en extension")
            Gine_file = upload_file_to_bucket(ine_file, f"docs/INE/{user['name'], user['lastname'], user['slastname']}_INE.{extension['ine_extension']}")
            Gaddress_prof = upload_file_to_bucket(address_prof, f"docs/Comprobante Domicilio/{user['name'], user['lastname'], user['slastname']}_addressprof.{extension['addres_prof_extension']}")
            GlicenceA = upload_file_to_bucket(licenceA, f"docs/Licencia Agricultor/{user['name'], user['lastname'], user['slastname']}_licenseA.{extension['license_A_extension']}")
            GlicenceT = upload_file_to_bucket(licenceT, f"docs/Licencia Tenencia/{user['name'], user['lastname'], user['slastname']}_licenseT.{extension['license_T_extension']}")
            if send_request_seller(phone, birthdate, estado, ciudad, Gine_file, Gaddress_prof, GlicenceA, GlicenceT, ID_Consumer):
                flash('¡Solicitud enviada!', 'success')
                return redirect(url_for('perfilvend'))
            else:
                flash('Ha habido un error, el telefono ya está en uso')
                
            return redirect(url_for('perfilvend'))  # Va a redirigir al perfil o seccion de solicitudes pendientes nc
    except ValueError as e:
                flash(str(e), 'error')  # Manejo de error si el tipo de archivo no es válido
                return redirect(url_for('register_seller'))
    except Exception as e:
                flash(f'Ocurrió un error: {str(e)}', 'error')  # Manejo de otros errores
                return redirect(url_for('register_seller'))
        
    return render_template('register_seller.html',estados=rowstates, infotemporary=info_request)


@app.route('/edit_request_seller', methods=['GET','POST'])
def edit_request_seller():
    print("Register ruta")
    user_id = session.get('user_id')
    seller_id = get_seller_by_id(user_id)
    if seller_id:
        return redirect(url_for('perfilvend'))
    if not user_id:
         return redirect(url_for('login'))
    ID_Consumer = get_consumer_by_id(user_id)
    request = get_request_by_consumer(ID_Consumer)
    Temporary_ID = get_temporary_by_consumer_id(ID_Consumer)
    info_request = get_info_request_by_temporary_id(Temporary_ID)
    rowstates = get_all_states()
    if request == -1:

        try:
            if request.method == 'POST':
                print("Estoy en POST (registerseller)")
                #DATOS
                phone = request.form['phone']
                birthdate = request.form['birthdate']
                estado = request.form['estado']
                ciudad = request.form['ciudad']
                #FILES
                ine_file = request.files['ine']
                address_prof = request.files['comprobante']
                licenceA = request.files['licenciaA']
                licenceT = request.files['licenciaT']
                
                print(f"Registrando: {phone}, {birthdate}, {ine_file}, {address_prof}, {licenceA}, {licenceT}")
                user = get_user_by_id(session['user_id'])
                #Google Cloud Storage (Upload)
                if not user:
                    print("Error no agarro user")
                print(user['name'])
                print("Si agarro el user")
                
                extension = get_extension(ine_file, address_prof, licenceA, licenceT)
                print("Esta en extension")
                Gine_file = upload_file_to_bucket(ine_file, f"docs/INE/{user['name'], user['lastname'], user['slastname']}_INE.{extension['ine_extension']}")
                Gaddress_prof = upload_file_to_bucket(address_prof, f"docs/Comprobante Domicilio/{user['name'], user['lastname'], user['slastname']}_addressprof.{extension['addres_prof_extension']}")
                GlicenceA = upload_file_to_bucket(licenceA, f"docs/Licencia Agricultor/{user['name'], user['lastname'], user['slastname']}_licenseA.{extension['license_A_extension']}")
                GlicenceT = upload_file_to_bucket(licenceT, f"docs/Licencia Tenencia/{user['name'], user['lastname'], user['slastname']}_licenseT.{extension['license_T_extension']}")
                if edit_request_seller(phone, birthdate, estado, ciudad, Gine_file, Gaddress_prof, GlicenceA, GlicenceT, ID_Consumer):
                    flash('¡Solicitud enviada!', 'success')
                    return redirect(url_for('perfilvend'))
                else:
                    flash('Ha habido un error, el telefono ya está en uso')
                    
                return redirect(url_for('perfilvend'))  # Va a redirigir al perfil o seccion de solicitudes pendientes nc
        except ValueError as e:
                    flash(str(e), 'error')  # Manejo de error si el tipo de archivo no es válido
                    return redirect(url_for('register_seller'))
        except Exception as e:
                    flash(f'Ocurrió un error: {str(e)}', 'error')  # Manejo de otros errores
                    return redirect(url_for('register_seller'))
            
    return render_template('edit_request_seller.html',estados=rowstates, infotemporary=info_request, request=request)    
        

    
@app.route((f'/{admin_key}/accept_request_seller'), methods=['GET', 'POST'])
def accept_request_seller():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    admin = get_admin_by_id(user_id)
    if not admin:
        print("No hay admin")
        return redirect(url_for('index'))
    
    
    

@app.route('/get_cities') 
def get_cities(): 
    estado_id = request.args.get('estado_id') 
    ciudades = get_all_cities_by_state(estado_id) 
    return jsonify(ciudades)
if __name__ == '__main__':
    app.run(debug=True)