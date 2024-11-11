from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables de entorno desde el archivo .env

# Acceder a las variables
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
admin_key = os.getenv('ADMIN_KEY')
google_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

print(client_id, client_secret, admin_key, google_credentials)
