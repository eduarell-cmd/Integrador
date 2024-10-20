import pyodbc

def get_db_connection(): 
   try:
      conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=EDUPC;'
        #'SERVER=DESKTOP-K3MNF88;'
        'DATABASE=INTEGRADORv1_LogInAndSign;'
        'UID=sa;'
        'PWD=1234;') 
      print(f"Hola")
      return conn
   except Exception as e :
      print(f"Valio vergota: {e}")


connection = get_db_connection()

