from conexionsql import get_db_connection, connection
import logging

def add_producto(nombre_producto, punto_venta, categoria_nombre, precio, stock, disponibilidad, imagen):    
    try: 
        # Mapear las categorías
        if categoria_nombre == 'frutas':
            categoria_id = 1
        elif categoria_nombre == 'verduras':
            categoria_id = 2
        else:
            categoria_id = None

        # Verificar que la categoría es válida
        if categoria_id is not None:
            # Conexión a la base de datos (ajustar detalles de conexión)
            conn = get_db_connection()
            cursor = conn.cursor()

            update_user_query = "EXEC Registrar_Producto ?, ?, ?, ?, ?, ?, ?"
            # Llamada al procedimiento almacenado
            cursor.execute(update_user_query,(nombre_producto, punto_venta, categoria_nombre, precio, stock, disponibilidad, imagen))
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
            # Confirmar el éxito
            conn.commit()
            conn.close()
            print(f"Resultado del procedimiento almacenado: {result}")
            return True
        else:
            return 'Categoría no válida'
    except Exception as e:
                print(f"Ocurrio un error al agregar un producto: {e}")

def get_point_by_id(point_id,):
    cursor = connection.cursor()
    query = "SELECT ID_Punto_Venta From Punto_Venta WHERE Vendedor_ID_Vendedor = ?"
    try:
        cursor.execute(query, (point_id))
        result = cursor.fetchone()
        if not result:
            print("No se encontró punto de venta")
            return False
        return result
    except Exception as e:
        print(f"Ocurrio un error al buscar punto de venta: {e}")