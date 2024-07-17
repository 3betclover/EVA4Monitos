import mysql.connector
from mysql.connector import Error
from datetime import datetime

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
            return "Nuevo día de ventas abierto correctamente."
        except Exception as e:
            self.conexion.rollback()
            return f"Error al abrir día de ventas: {e}"
        finally:
            cursor.close()
    
    def cerrar_dia_de_ventas(self, id_jefe_de_ventas):
        try:
            cursor = self.conexion.cursor()
            
            # Verificar si hay un día de ventas abierto para cerrar
            query_verificar = "SELECT id FROM dias_de_ventas WHERE estado = 'abierto' ORDER BY fecha_abierto DESC LIMIT 1"
            cursor.execute(query_verificar)
            resultado = cursor.fetchone()
            
            if not resultado:
                return "No hay un día de ventas abierto para cerrar."
            
            id_dia_de_ventas = resultado[0]
            
            # Actualizar el estado del día de ventas a 'cerrado', la fecha de cierre y el id del jefe de ventas
            fecha_cerrado = datetime.now()
            query_update = """
            UPDATE dias_de_ventas SET estado = 'cerrado', fecha_cerrado = %s, id_jefe_de_ventas = %s WHERE id = %s
            """
            cursor.execute(query_update, (fecha_cerrado, id_jefe_de_ventas, id_dia_de_ventas))
            self.conexion.commit()
            
            return "Día de ventas cerrado correctamente."
        
        except Exception as e:
            self.conexion.rollback()
            return f"Error al cerrar día de ventas: {e}"
        finally:
            cursor.close()







        