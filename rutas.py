from flask import Flask, request, redirect, url_for, render_template, flash, json
from werkzeug.security import generate_password_hash, check_password_hash
from conexionsql import get_db_connection
import secrets
from datetime import datetime
import requests
import googlemaps
import logging

app = Flask(__name__)





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