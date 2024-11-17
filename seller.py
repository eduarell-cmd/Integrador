from flask import Flask, request, redirect, url_for, jsonify, render_template, flash
from google.cloud import storage
from werkzeug.utils import secure_filename  
import os
import json

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    """Verificar que el archivo sea de un tipo permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file_to_bucket(file, destination_blob_name):
    if file and allowed_file(file.filename):
        print("si agarro la funcion")
        filename = secure_filename(file.filename)

        print(filename)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        storage_client = storage.Client()

        
        bucket_name = 'farm_to_table'
        bucket = storage_client.bucket(bucket_name)

        
        blob = bucket.blob(destination_blob_name)

        
        blob.upload_from_file(file)

        
        if not file_url:
            print("No agarra el public url")
        print("Lol")
        file_url = blob.public_url
        print(file_url)
        return file_url
    else:
        raise ValueError("Tipo de archivo no permitido")
    
def get_extension(ine_file,addres_prof,license_A,license_T):
    print("Estoy en get_extension")
    ine_filename = ine_file.filename
    addres_prof_filename = addres_prof.filename
    license_A_filename = license_A.filename
    license_T_filename = license_T.filename

    format_ine = os.path.splitext(ine_filename)[1][1:]
    format_addres_prof = os.path.splitext(addres_prof_filename)[1][1:]
    format_license_A = os.path.splitext(license_A_filename)[1][1:]
    format_license_T = os.path.splitext(license_T_filename)[1][1:]
    file_extensions = {
        'ine_extension': format_ine,
        'addres_prof_extension': format_addres_prof,
        'license_A_extension': format_license_A,
        'license_T_extension': format_license_T
    }
    print(file_extensions)
    print(f"Si esta agarrando:{ file_extensions['ine_extension']}")
    return file_extensions