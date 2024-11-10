from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com.'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'farmtable79@gmail.com'
app.config['MAIL_PASSWORD'] = 'saqd joaj qzop jbae'
  
mail = Mail(app)
