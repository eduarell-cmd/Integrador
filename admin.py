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

def get_all_requests():
    cursor = connection.cursor()
    query = "EXEC MuestraSolicitudes"
    cursor.execute(query)
    requests = cursor.fetchall()
    #requestlol = []
    #for row in requests:
        #request = {
         #   'ID_Solicitud': row[0],
          #  'Nombre': row[2],
           # 'Apelldo': row[3],
            #'Telefono': row[4],
            #'INE': row[5],
            #'Comprobante_D': row[6],
            #'Licencia_A': row[7],
            #'Tenencia': row[8],
            #'Estado_Solicitud': row[9],
            #'Fecha': row[10],
            #'Comentario': row[11]
       # }
        #requestlol.append(request)
    return requests
