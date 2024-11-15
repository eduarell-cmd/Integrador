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
    
