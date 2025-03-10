from flask import Flask, jsonify
from google.cloud import storage
from werkzeug.utils import secure_filename  
import os
import logging
from conexionsql import connection
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    """Verificar que el archivo sea de un tipo permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file_to_bucket(file, destination_blob_name):
    if file and allowed_file(file.filename):
        print("si agarro la funcion")
        filename = secure_filename(file.filename)

        print(filename)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        storage_client = storage.Client()

        
        bucket_name = 'farm_to_table'
        bucket = storage_client.bucket(bucket_name)

        
        blob = bucket.blob(destination_blob_name)

        
        blob.upload_from_file(file)

        
        
        file_url = blob.public_url
        if not file_url:
            print("No agarra el public url")
        print(file_url)
        return file_url
    else:
        raise ValueError("Tipo de archivo no permitido")
    
def get_extension(ine_file,addres_prof,license_A,license_T):
    print("Estoy en get_extension")
    ine_filename = ine_file.filename
    addres_prof_filename = addres_prof.filename
    license_A_filename = license_A.filename
    license_T_filename = license_T.filename

    format_ine = os.path.splitext(ine_filename)[1][1:]
    format_addres_prof = os.path.splitext(addres_prof_filename)[1][1:]
    format_license_A = os.path.splitext(license_A_filename)[1][1:]
    format_license_T = os.path.splitext(license_T_filename)[1][1:]
    file_extensions = {
        'ine_extension': format_ine,
        'addres_prof_extension': format_addres_prof,
        'license_A_extension': format_license_A,
        'license_T_extension': format_license_T
    }
    print(file_extensions)
    print(f"Si esta agarrando:{ file_extensions['ine_extension']}")
    return file_extensions

def get_extension_for_img(imagenpr):
    productimg_filename = imagenpr.filename
    format_productimg = os.path.splitext(productimg_filename)[1][1:]
    img_extension = {
        'product_extension': format_productimg
    }
    return img_extension
def get_product_by_id(product_id):
    conn = None
    product = None
    try:
        cursor = connection.cursor()
        
        # Ejecuta la consulta para obtener los datos del producto
        cursor.execute("SELECT Nombre_Producto, Punto_Venta_ID_Punto_Venta, Categoria_ID_Categoria, Precio, Disponible, Foto_Producto FROM Producto WHERE ID_Producto = ?", (product_id,))
        
        result = cursor.fetchone()
        
        # Si se encuentra un producto, convertirlo en un diccionario
        if result:
            product = {
                'name': result[0],  # Nombre del producto
                'point': result[1],  # Punto de venta
                'category': result[2],  # Categoría
                'price': result[3],  # Precio
                'stock': result[4],  # Disponibilidad
                'image': result[5]  # Foto del producto
            }
    except Exception as e:
        print(f"Ocurrió un error al obtener el producto: {e}")
    finally:
        if conn:
            connection.close()
    return product

def get_seller_by_id(seller_id):
    cursor = connection.cursor()
    query = "SELECT ID_Vendedor From Vendedor WHERE Persona_ID_Persona = ?"
    try:
        cursor.execute(query, (seller_id))
        result = cursor.fetchone()
        if not result:
            print("No se encontró vendedor")
            return False
        return result
    except Exception as e:
        print(f"Ocurrio un error al buscar vendedor: {e}")

def get_all_states():
    cursor = connection.cursor()
    query = "SELECT ID_Estado, Nombre_Estado FROM Estado"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def get_all_cities_by_state(estado_id):
    cursor = connection.cursor()
    query = "SELECT ID_Ciudad, Nombre_Ciudad FROM Ciudad WHERE Estado_ID_Estado = ?"
    cursor.execute(query, (estado_id,))
    rows = cursor.fetchall()
    ciudades = [{"ID_Ciudad": row[0], "Nombre_Ciudad": row[1]} for row in rows]
    return ciudades

def get_consumer_by_id(user_id):
    cursor = connection.cursor()
    query = "SELECT ID_Consumidor FROM Consumidor WHERE Persona_ID_Persona = ?"
    cursor.execute(query, (user_id))
    consumer_id = cursor.fetchone()
    if not consumer_id:
        print("No se encontro consumidor")
        return False
    print(consumer_id)
    return consumer_id[0]

def get_request_by_consumer(consumer_id):
    cursor = connection.cursor()
    query = "SELECT ID_Solicitud_Vendedor FROM Solicitud_Vendedor WHERE Consumidor_ID_Consumidor = ? AND Estado_Solicitud = 'Pendiente'"
    cursor.execute(query, (consumer_id))
    request_pendiente = cursor.fetchone()
    if not request_pendiente:
        querynot = "SELECT ID_Solicitud_Vendedor, Comentario_Admin FROM Solicitud_Vendedor WHERE Consumidor_ID_Consumidor = ? AND Estado_Solicitud = 'Rechazado'"
        cursor.execute(querynot, (consumer_id))
        request_rechazada = cursor.fetchone()
        print (request_rechazada)
        if not request_rechazada:
            print("No se encontró ninguna solicitud")
            return 0
        request_rechazada = {
            'result': -2,
            'id': request_rechazada[0],
            'comentario' : request_rechazada[1]
        }
        print(f"Request rechazada{request_rechazada }")
        return request_rechazada
    request_pendiente = -1
    return request_pendiente

def get_temporary_by_consumer_id(consumer_id):
    cursor = connection.cursor()
    query = "SELECT Temporal_Registro_ID_Temporal_Registro FROM Solicitud_Vendedor WHERE Consumidor_ID_Consumidor = ?"
    cursor.execute(query,(consumer_id))
    temporary_id = cursor.fetchone()
    if not temporary_id:
        print("No se encontro temporary")
        return False
    return temporary_id
def get_info_request_by_temporary_id(temporary_id):
    try:
        cursor = connection.cursor()

        query = "SELECT TelefonoT, Fecha_NacimientoT, INET, Comprobante_DomicilioT, Licencia_AgricultorT, Tenencia_TierraT, Estado_ID_Estado, Ciudad_ID_Ciudad FROM Temporal_Registro_Vendedor WHERE ID_Temporal_Registro = ?" 
        
        cursor.execute(query, (temporary_id))
        
        result = cursor.fetchone()
        if result:
            request = {
                'phone': result[0],  # Nombre del producto
                'birthdate': result[1],  # Punto de venta
                'ine': result[2],  # Categoría
                'comprobante': result[3],  # Precio
                'LicenciaA': result[4],  # Disponibilidad
                'Tenencia': result[5],  # Foto del producto
                'Estado': result[6],
                'Ciudad': result[7]
            }
        return request
    except Exception as e:
        print(f"Ocurrió un error al obtener el producto: {e}")

def send_request_seller(phone, birthdate, estado, ciudad, INE, ComprobanteDomicilio, LicenciaA, LicenciaT, IDConsumer):
    cursor = connection.cursor()
    query = "EXEC Registrar_Solicitud_Vendedor ?,?,?,?,?,?,?,?,?"
    try:
        cursor.execute(query,(phone, birthdate, estado, ciudad, INE, ComprobanteDomicilio, LicenciaA, LicenciaT, IDConsumer))
        result = cursor.fetchone()
        if not result:
            print("No se encontró resultado")
        print (result)
        if result and result[0] == 0:
            connection.commit()
            logging.info("Solicitud registrada con éxito.")
            return True
        elif result and result[0] == -1:
            connection.rollback()
            print("Error dentro del procedimiento.")
            return False
        elif result and result[0] == -2:
            connection.rollback()
            print("El telefono ya está en uso")
            return False
        else:
            print("Error en el registro de la solicitud o resultado inesperado.")
            return False
    except Exception as e:
        logging.error(f"Error durante la inserción de solicitud: {e}")
        return False
    
def edit_request_seller_db(id_solicitud,phone, birthdate, estado, ciudad, INE, ComprobanteDomicilio, LicenciaA, LicenciaT, IDConsumer):
    cursor = connection.cursor()
    query = "EXEC Editar_Solicitud_Vendedor ?,?,?,?,?,?,?,?,?,?"
    try:
        cursor.execute(query,(id_solicitud, phone, birthdate, estado, ciudad, INE, ComprobanteDomicilio, LicenciaA, LicenciaT, IDConsumer))
        result = cursor.fetchone()
        if not result:
            print("No se encontró resultado")
        print (result)
        if result and result[0] == 0:
            connection.commit()
            logging.info("Solicitud actualizada con éxito.")
            return True
        elif result and result[0] == -1:
            connection.rollback()
            print("Error dentro del procedimiento.")
            return False
        elif result and result[0] == -2:
            connection.rollback()
            print("El telefono ya está en uso o no existe una solicitud")
            return False
        else:
            print("Error en el registro de la solicitud o resultado inesperado.")
            return False
    except Exception as e:
        logging.error(f"Error durante la inserción de solicitud: {e}")
        return False
def get_sellerinfo_by_user_id(user_id):
    try:
        cursor = connection.cursor()
        query= "EXEC MostrarInfoVendedor ?"

        cursor.execute(query, (user_id,))
        
        result = cursor.fetchone()
        posicion0 = result[0]
        print(f"Telefono:{posicion0}")
        if result:
            return result
        return None
    except Exception as e:
        print(f"Ocurrió un error al obtener el telefono: {e}")
        return None
    
def exec_muestra():
    cursor = connection.cursor()
    query = "EXEC MuestraTienda"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def get_info_pv(seller_id):
    cursor = connection.cursor()
    query = "EXEC VerPuntoVenta ?"

    cursor.execute(query, (seller_id))

    result = cursor.fetchone()
    print(f"Info de punto de venta: {result}")
    return result