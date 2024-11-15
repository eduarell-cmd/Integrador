from conexionsql import get_db_connection
import logging

def update_user_name(ID_Persona, Nombre, PrimerApellido, SegundoApellido):
    conn = get_db_connection()
    cursor = conn.cursor()

    update_user_query = "EXEC Actualizar_Nombre_Apellidos ?, ?, ?, ?"
    try:
        cursor.execute(update_user_query, (ID_Persona, Nombre, PrimerApellido, SegundoApellido))
        result = cursor.fetchone()
        print(f"Resultado del procedimiento almacenado: {result}")

        if result and result[0] == 0:
            conn.commit()
            logging.info("Datos del usuario actualizados con éxito.")
            return True
        elif result and result[0] == 1:
            conn.rollback()
            print("El ID de usuario no existe.")
            return False
        else:
            print("Error en la actualización del usuario o resultado inesperado.")
            return False
    except Exception as e:
        logging.error(f"Error durante la actualización del usuario: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()