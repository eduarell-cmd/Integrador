import pyodbc

def get_db_connection():
 try:
    conn = pyodbc.connect(
         'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-K3MNF88;'
        'DATABASE=INTEGRADORv1_LogInAndSign;'
        'UID=sa;'
        'PWD=1234;'

    )
    return conn
 except Exception as e:
    print(f"Error de conexion a la base de datos: {e}")
    return None