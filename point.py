from conexionsql import get_db_connection, connection
import logging

def add_punto_venta(VendedorID, DireccionID, DescripcionPunto, TipoPuntoVentaID, Horario, Estado):    
    conn = connection
    cursor = conn.cursor()
    try: 
            add_punto_query = "EXEC Agregar_Punto_Venta ?, ?, ?, ?, ?, ?"
            # Llamada al procedimiento almacenado
            cursor.execute(add_punto_query,(VendedorID, DireccionID, DescripcionPunto, TipoPuntoVentaID, Horario, Estado))
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