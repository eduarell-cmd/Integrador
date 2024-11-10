from flask import Flask, request, redirect, url_for, jsonify, render_template
from google.cloud import storage
import os

app = Flask(__name__)

def upload_file_to_bucket(file, filename):
    client = storage.Client()
    bucket = client.bucket('farm_to_table')
    blob = bucket.blob(filename)
    blob.upload_from_file(file)
    return blob.public.url
    
@app.route('/register_seller', methods=['POST'])
def register_seller():
    #DATA 
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

    #Google Cloud Storage (Upload)
    ine_url = upload_file_to_bucket(ine_file, f"docs/{name}_INE.jpg")
    address_prof = upload_file_to_bucket(address_prof, f"docs/{name}_addressprof.jpg")
    licenceA = upload_file_to_bucket(licenceA, f"docs/{name}_licenseA.jpg")
    licenceT = upload_file_to_bucket(licenceT, f"docs/{name}_licenseT.jpg")

        
    return render_template('registerseller.html')