from conexionsql import connection
import logging
import os
import requests

api_keyLIAM=os.getenv("API_KEYLIAM")
def add_punto_venta(VendedorID, DireccionID, DescripcionPunto, TipoPuntoVentaID, Horario, Estado, Latitud, Longitud, Direccion_Exacta):    
    conn = connection
    cursor = conn.cursor()
    try: 
            add_punto_query = "EXEC Agregar_Punto_Venta ?, ?, ?, ?, ?, ?, ?, ?, ?"
            # Llamada al procedimiento almacenado
            cursor.execute(add_punto_query,(VendedorID, DireccionID, DescripcionPunto, TipoPuntoVentaID, Horario, Estado, Latitud, Longitud, Direccion_Exacta))
            result = cursor.fetchone()

            if result and result[0] == 0:
                conn.commit()
                logging.info("Punto añadido con éxito")
                return True
            elif result and result[0] == 1:
                conn.rollback()
                print("Punto hubo error")
                return False
            else:
                print("Error en el registro del punto o resultado inesperado.")
                return False
    except Exception as e:
                print(f"Ocurrio un error al agregar un punto: {e}")
                print(VendedorID, DireccionID, DescripcionPunto, TipoPuntoVentaID, Horario, Estado)

def get_direccion_by_id(direccion_id):
    cursor = connection.cursor()
    query = "SELECT Direccion_ID_Direccion From Vendedor WHERE ID_Vendedor = ?"
    try:
        cursor.execute(query, (direccion_id))
        result = cursor.fetchone()
        print(result)
        if not result:
            print("No se encontró dirección")
            return False
        direccion_id = result[0]
        return direccion_id
    except Exception as e:
        print(f"Ocurrio un error al buscar dirección: {e}")


def get_address_from_coordinates(latitude, longitude):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_keyLIAM}"
    response = requests.get(url)
    data = response.json()
    print(f"Data de address:{data}")

    if data['status'] == 'OK':
        address = data['results'][0]['formatted_address']
        return address
    else:
        return None


def get_ubicacion_by_product_id_and_nombre_producto(product_id, nombre_producto):
    cursor = connection.cursor()
    query="SELECT ID_Producto FROM Producto WHERE ID_Producto AND Nombre_Producto"
    cursor.execute(query,(product_id,nombre_producto))
    result = cursor.fetchall()
    if not result:
         print("No se encontro la ubicacion por el producto")
    return result
# Ejemplo de uso
#latitude = 19.432608
#longitude = -99.133209
#api_key=os.getenv("API_KEY")

#address = get_address_from_coordinates(latitude, longitude, api_key)
#if address:
 #   print(f"La dirección es: {address}")
#else:
 #   print("No se pudo obtener la dirección.")
