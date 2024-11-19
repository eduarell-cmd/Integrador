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


def get_point_by_id(point_id):
    cursor = connection.cursor()
    query = "SELECT ID_Punto_Venta From Punto_Venta WHERE Vendedor_ID_Vendedor = ?"
    try:
        cursor.execute(query, (point_id))
        result = cursor.fetchone()
        print(result)
        if not result:
            print("No se encontró punto de venta")
            return False
        point_id = result[0]
        return point_id
    except Exception as e:
        print(f"Ocurrio un error al buscar punto de venta: {e}")

def get_products_by_point_id(point_id):
    conn = None
    products = []
    try:
        cursor = connection.cursor()
        
        # Consulta para obtener los productos del punto de venta específico
        query = "SELECT ID_Producto, Punto_Venta_ID_Punto_Venta, Nombre_Producto, Precio, Stock FROM Producto WHERE Punto_Venta_ID_Punto_Venta = ?"
        cursor.execute(query, (point_id,))
        
        results = cursor.fetchall()
        
        # Convertir cada fila en un diccionario
        for row in results:
            product = {
                'id': row[0],  # ID del producto
                'point_id': row[1],  # ID del punto de venta
                'name': row[2],  # Nombre del producto
                'price': row[3],  # Precio
                'stock': row[4]  # Stock
            }
            products.append(product)
    except Exception as e:
        print(f"Error al recuperar productos: {e}")
    finally:
        if conn:
            connection.close()
    return products

def editar_producto(product_id, nombre_producto, categoria_id, precio, stock, disponibilidad, imagen):
    conn = connection
    cursor = conn.cursor()
    try:
        if categoria_id == 'frutas':
            categoria_id = 1
        elif categoria_id == 'verduras':
            categoria_id = 2
        else:
            categoria_id = None

        if categoria_id is not None:
            update_product_query = "EXEC Actualizar_Producto ?, ?, ?, ?, ?, ?, ?"
            cursor.execute(update_product_query,(product_id, nombre_producto, categoria_id, precio, stock, disponibilidad, imagen))
            result = cursor.fetchone()

            if result and result[0] == 0:
                conn.commit()
                logging.info("Producto actualizado con éxito")
                return True
            elif result and result[0] == 1:
                conn.rollback()
                print("Error en la actualización del producto")
                return False
            else:
                print("Error inesperado al actualizar producto.")
                return False
        else:
            return 'Categoría no válida'
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        return False