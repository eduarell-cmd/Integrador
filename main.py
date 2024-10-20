from conexionsql import get_db_connection
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = 'secrets.token_hex(16)'