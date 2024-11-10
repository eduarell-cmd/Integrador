from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp-relay.gmail.com.'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'farmtable79@gmail.com'
app.config['MAIL_PASSWORD'] = 'papuesprolge'
  
mail = Mail(app)
