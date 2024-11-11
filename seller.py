from flask import Flask, request, redirect, url_for, jsonify, render_template, flash
from google.cloud import storage
from werkzeug.utils import secure_filename  
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    """Verificar que el archivo sea de un tipo permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file_to_bucket(file, destination_blob_name):
    if file and allowed_file(file.filename):
        
        filename = secure_filename(file.filename)

        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        storage_client = storage.Client()

        
        bucket_name = 'farm_to_table'
        bucket = storage_client.bucket(bucket_name)

        
        blob = bucket.blob(destination_blob_name)

        
        blob.upload_from_file(file)

        
        file_url = blob.public_url
        return file_url
    else:
        raise ValueError("Tipo de archivo no permitido")
    
@app.route('/register_seller', methods=['POST'])
def register_seller():
    #DATA 
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

        #(Upload)
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
    