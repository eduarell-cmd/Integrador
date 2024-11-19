from conexionsql import get_db_connection, connection
import logging

def add_producto(nombre_producto, punto_venta, categoria_id, precio, stock, disponibilidad, imagen):    
    conn = connection
    cursor = conn.cursor()
    try: 
        # Mapear las categorías
        if categoria_id == 'frutas':
            categoria_id = 1
        elif categoria_id == 'verduras':
            categoria_id = 2
        else:
            categoria_id = None

        # Verificar que la categoría es válida
        if categoria_id is not None:
            # Conexión a la base de datos (ajustar detalles de conexión)

            update_user_query = "EXEC Agregar_Producto ?, ?, ?, ?, ?, ?, ?"
            # Llamada al procedimiento almacenado
            cursor.execute(update_user_query,(nombre_producto, punto_venta, categoria_id, precio, stock, disponibilidad, imagen))
            result = cursor.fetchone()

            if result and result[0] == 0:
                conn.commit()
                logging.info("Producto añadido con éxito")
                return True
            elif result and result[0] == 1:
                conn.rollback()
                print("Producto hubo error")
                return False
            else:
                print("Error en el registro del usuario o resultado inesperado.")
                return False

        else:
            return 'Categoría no válida'
    except Exception as e:
                print(f"Ocurrio un error al agregar un producto: {e}")
                print(nombre_producto, punto_venta, categoria_id, precio, stock, disponibilidad, imagen)


def get_point_by_id(point_id,):
    cursor = connection.cursor()
    query = "SELECT ID_Punto_Venta From Punto_Venta WHERE Vendedor_ID_Vendedor = ?"
    try:
        cursor.execute(query, (point_id))
        result = cursor.fetchone()
        if not result:
            print("No se encontró punto de venta")
            return False
        point_id = result[0]
        return point_id
    except Exception as e:
        print(f"Ocurrio un error al buscar punto de venta: {e}")