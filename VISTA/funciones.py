from DB.conexion import DAO
from datetime import datetime

def login():
    dao = DAO()
    conexion = dao.conectar()
    
    if conexion is None:
        print("No se pudo conectar a la base de datos.")
        return
    
    while True:
        # Solicitar credenciales al usuario
        nombre_usuario = input("Ingrese su nombre de usuario: ")
        contrasenia = input("Ingrese su contraseña: ")
        
        try:
            # Consultar la base de datos
            cursor = conexion.cursor()
            query = "SELECT id, rol FROM usuarios WHERE nombre_usuario = %s AND contrasenia = %s"
            cursor.execute(query, (nombre_usuario, contrasenia))
            resultado = cursor.fetchone()
            
            # Verificar si se encontró un usuario
            if resultado:
                usuario_id, rol = resultado
                if rol == 'jefe de ventas':
                    print("Bienvenido, jefe de ventas.")
                    submenu_jefe_ventas(conexion, usuario_id)
                    break
                elif rol == 'vendedor':
                    print("Bienvenido, vendedor.")
                    generar_venta(usuario_id, conexion)
                    break
                else:
                    print("Rol no reconocido.")
            else:
                print("Usuario o contraseña incorrectos. Por favor, ingrese datos válidos.")
        except Exception as e:
            print(f"Ocurrió un error al intentar ingresar: {e}")
        finally:
            cursor.close()
    
    conexion.close()

def submenu_jefe_ventas(conexion, id_jefe_de_ventas):
    while True:
        print("\nMenú de Jefe de Ventas:")
        print("1. Abrir día de ventas")
        print("2. Cerrar día de ventas")
        print("3. Agregar producto")
        print("0. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            abrir_dia_de_ventas(conexion)
        elif opcion == '2':
            cerrar_dia_de_ventas(conexion, id_jefe_de_ventas)
        elif opcion == '3':
            agregar_productos(conexion)
        elif opcion == '0':
            print("Saliendo del menú de Jefe de Ventas.")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

def abrir_dia_de_ventas(conexion):
    try:
        cursor = conexion.cursor()
        
        # Verificar si ya hay un día de ventas abierto
        query_verificar = "SELECT id, fecha_abierto FROM dias_de_ventas WHERE estado = 'abierto' ORDER BY fecha_abierto DESC LIMIT 1"
        cursor.execute(query_verificar)
        resultado = cursor.fetchone()
        
        if resultado:
            id_dia_abierto, fecha_abierto = resultado
            print(f"Ya hay un día de ventas abierto desde {fecha_abierto.strftime('%d/%m/%Y %H:%M:%S')}. No se puede abrir otro día.")
            return
        
        # Si no hay un día abierto, procedemos a abrir uno nuevo
        fecha_abierto = datetime.now()
        query_insertar = """
        INSERT INTO dias_de_ventas (fecha_abierto, estado)
        VALUES (%s, 'abierto')
        """
        cursor.execute(query_insertar, (fecha_abierto,))
        conexion.commit()
        print("Nuevo día de ventas abierto correctamente.")
    
    except Exception as e:
        print(f"Error al abrir día de ventas: {e}")
        conexion.rollback()
    
    finally:
        cursor.close()

def cerrar_dia_de_ventas(conexion, id_jefe_de_ventas):
    try:
        cursor = conexion.cursor()
        
        # Verificar si hay un día de ventas abierto para cerrar
        query_verificar = "SELECT id FROM dias_de_ventas WHERE estado = 'abierto' ORDER BY fecha_abierto DESC LIMIT 1"
        cursor.execute(query_verificar)
        resultado = cursor.fetchone()
        
        if not resultado:
            print("No hay un día de ventas abierto para cerrar.")
            return
        
        id_dia_de_ventas = resultado[0]
        
        # Actualizar el estado del día de ventas a 'cerrado', la fecha de cierre y el id del jefe de ventas
        fecha_cerrado = datetime.now()
        query_update = """
        UPDATE dias_de_ventas SET estado = 'cerrado', fecha_cerrado = %s, id_jefe_de_ventas = %s WHERE id = %s
        """
        cursor.execute(query_update, (fecha_cerrado, id_jefe_de_ventas, id_dia_de_ventas))
        conexion.commit()
        
        print("Día de ventas cerrado correctamente.")
    
    except Exception as e:
        print(f"Error al cerrar día de ventas: {e}")
        conexion.rollback()
    
    finally:
        cursor.close()

def agregar_productos(conexion):
    while True:
        try:
            cursor = conexion.cursor()
            nombre = input("Ingrese el nombre del producto: ")
            codigo_producto = input("Ingrese el código del producto: ")
            sku = input("Ingrese el SKU del producto: ")
            precio = int(input("Ingrese el precio unitario del producto: "))
            cantidad = int(input("Ingrese la cantidad del producto: "))
            
            query = """
            INSERT INTO productos (nombre, codigo_producto, sku, precio, cantidad)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nombre, codigo_producto, sku, precio, cantidad))
            conexion.commit()
            
            print("Producto agregado exitosamente.")
            
            otra = input("¿Desea agregar otro producto? (s/n): ")
            if otra.lower() != 's':
                break
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            conexion.rollback()
        finally:
            cursor.close()

def generar_venta(usuario_id, conexion):
    try:
        cursor = conexion.cursor()
        
        # Obtener el ID del día de ventas abierto
        query = "SELECT id FROM dias_de_ventas WHERE estado = 'abierto' ORDER BY fecha_abierto DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if not resultado:
            print("No hay un día de ventas abierto. Por favor, contacte al jefe de ventas.")
            return
        
        id_dia_de_ventas = resultado[0]
        
        productos_vendidos = []
        total_venta = 0
        
        while True:
            sku_producto = input("Ingrese el SKU del producto: ")
            cantidad = int(input("Ingrese la cantidad del producto: "))
            
            # Buscar el producto por SKU
            query = "SELECT id, precio FROM productos WHERE sku = %s"
            cursor.execute(query, (sku_producto,))
            resultado = cursor.fetchone()
            
            if not resultado:
                print("Producto no encontrado. Intente nuevamente.")
                continue
            
            producto_id, precio_unitario = resultado
            total_producto = precio_unitario * cantidad
            total_venta += total_producto
            
            productos_vendidos.append((producto_id, cantidad, total_producto))
            
            otra = input("¿Desea agregar otro producto a la venta? (s/n): ")
            if otra.lower() != 's':
                break
        
        iva = total_venta * 0.19
        total_final = total_venta + iva
        
        # Insertar la venta en la base de datos
        query = """
        INSERT INTO ventas (id_usuario, id_dia_de_ventas, precio_total)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (usuario_id, id_dia_de_ventas, total_final))
        id_venta = cursor.lastrowid
        
        # Insertar los productos de la venta
        for producto_id, cantidad, total_producto in productos_vendidos:
            query = """
            INSERT INTO ventas_productos (id_venta, id_producto, cantidad)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (id_venta, producto_id, cantidad))
        
        conexion.commit()
        
        print(f"Venta generada exitosamente. Total a pagar (incluido IVA): {total_final}")
    
    except Exception as e:
        print(f"Error al generar la venta: {e}")
        conexion.rollback()
    finally:
        cursor.close()

def mi_funcion():
    print("Esta es mi_funcion en VISTA.funciones")






