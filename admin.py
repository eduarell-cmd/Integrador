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
    

def get_pending_requests():
    cursor = connection.cursor()
    query = "EXEC MostrarSolicitudesPendientes"
    cursor.execute(query)
    requests = cursor.fetchall()
    requestlol = []
    for row in requests:
        request = {
            'ID_Solicitud': row[0],
            'Nombre': row[1],
            'Apelldo': row[2],
            'Telefono': row[3],
            'INE': row[4],
            'Comprobante_D': row[5],
            'Licencia_A': row[6],
            'Tenencia': row[7],
            'Estado_Solicitud': row[8],
            'Fecha': row[9],
            'Comentario': row[10]
        }
        requestlol.append(request)
 
    return requestlol

def accept_seller_request_db(IDSolicitud,Comentario_Admin,AdminID):
    cursor = connection.cursor()
    query = "EXEC AceptarSolicitudVendedor ?,?,?"
    parameters = IDSolicitud, Comentario_Admin, AdminID
    cursor.execute(query, (parameters))
    result = cursor.fetchone()
    return result