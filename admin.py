from conexionsql import connection
import logging
def get_admin_by_id(session_id):
    cursor = connection.cursor()
    query="SELECT ID_Admin FROM Admin WHERE Persona_ID_Persona = ?"
    try:
        cursor.execute(query, (session_id))
        admin = cursor.fetchone()
        if not admin:
            print("Este usuario no es administrador")
            return False
        return admin
    except Exception as e:
        logging.error(f"Error durante la busqueda de un administrador:{e}")
    finally:
            connection.close()

def get_all_request_seller():
     cursor = connection.cursor()
     query = "SELECT"