import mysql.connector
from mysql.connector import Error
from datetime import datetime  # Importa datetime para trabajar con fechas y horas

class DAO:
    def __init__(self):
        self.conexion = None
        try:
            self.conexion = mysql.connector.connect(
                host='dhdatabase.c9mc42yoi1fs.us-east-2.rds.amazonaws.com',
                port=3306,
                user='admin1',
                password='Digital2024',
                database='db_monitos'
            )
            print("Conexión exitosa a la base de datos.")
        except Error as ex:
            print("Error de conexión: ", ex)
    
    def conectar(self):
        return self.conexion
    
    def abrir_dia_de_ventas(self, id_jefe_de_ventas):
        try:
            cursor = self.conexion.cursor()
            fecha_abierto = datetime.now()
            query = """
            INSERT INTO dias_de_ventas (fecha_abierto, id_jefe_de_ventas)
            VALUES (%s, %s)
            """
            cursor.execute(query, (fecha_abierto, id_jefe_de_ventas))
            self.conexion.commit()
            print("Nuevo día de ventas abierto correctamente.")
        except Exception as e:
            print(f"Error al abrir día de ventas: {e}")
            self.conexion.rollback()
        finally:
            cursor.close()





        