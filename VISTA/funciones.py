from DB.conexion import DAO
from datetime import datetime

def bienvenido():
    mensaje = "Bienvenido al sistema de ventas \"Los monitos de la nona\""
    ancho_total = len(mensaje) + 6

    print("*" * ancho_total)
    print(f"* {mensaje.center(ancho_total - 4)} *")
    print("*" * ancho_total)

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
                    if not submenu_jefe_ventas(conexion, usuario_id):
                        break
                elif rol == 'vendedor':
                    print("Bienvenido, vendedor.")
                    if not menu_vendedor(usuario_id, conexion):
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
        print("4. Ver día de ventas")
        print("5. Filtrar día de ventas por vendedor")
        print("0. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            mensaje = abrir_dia_de_ventas(conexion, id_jefe_de_ventas)
            print(mensaje)
        elif opcion == '2':
            mensaje = cerrar_dia_de_ventas(conexion, id_jefe_de_ventas)
            print(mensaje)
        elif opcion == '3':
            agregar_productos(conexion)
        elif opcion == '4':
            ver_dia_de_ventas(conexion)
        elif opcion == '5':
            filtrar_dia_de_ventas_por_vendedor(conexion)
        elif opcion == '0':
            print("Saliendo del menú de Jefe de Ventas.")
            return True
        else:
            print("Opción no válida. Intente nuevamente.")

def abrir_dia_de_ventas(conexion, id_jefe_de_ventas):
    try:
        cursor = conexion.cursor()
        
        # Verificar si ya hay un día de ventas abierto
        query = "SELECT id FROM dias_de_ventas WHERE estado = 'abierto'"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado:
            return "Ya hay un día de ventas abierto. Cierre el día de ventas actual antes de abrir uno nuevo."
        
        # Abrir un nuevo día de ventas
        query = "INSERT INTO dias_de_ventas (id_jefe_de_ventas, fecha_abierto, estado) VALUES (%s, %s, %s)"
        fecha_abierto = datetime.now()
        cursor.execute(query, (id_jefe_de_ventas, fecha_abierto, 'abierto'))
        conexion.commit()
        
        return "Día de ventas abierto exitosamente."
    except Exception as e:
        conexion.rollback()
        return f"Error al abrir día de ventas: {e}"
    finally:
        cursor.close()

def cerrar_dia_de_ventas(conexion, id_jefe_de_ventas):
    try:
        cursor = conexion.cursor()
        
        # Verificar si hay un día de ventas abierto
        query = "SELECT id FROM dias_de_ventas WHERE estado = 'abierto'"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if not resultado:
            return "No hay un día de ventas abierto."
        
        id_dia_de_ventas = resultado[0]
        
        # Cerrar el día de ventas
        query = "UPDATE dias_de_ventas SET fecha_cerrado = %s, estado = %s WHERE id = %s"
        fecha_cerrado = datetime.now()
        cursor.execute(query, (fecha_cerrado, 'cerrado', id_dia_de_ventas))
        conexion.commit()
        
        return "Día de ventas cerrado exitosamente."
    except Exception as e:
        conexion.rollback()
        return f"Error al cerrar día de ventas: {e}"
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

def filtrar_dia_de_ventas_por_vendedor(conexion):
    nombre_usuario = input("Ingrese el nombre de usuario del vendedor: ")
    
    try:
        cursor = conexion.cursor()
        query = """
        SELECT DISTINCT d.id, d.fecha_abierto, d.fecha_cerrado, d.estado
        FROM dias_de_ventas d
        JOIN ventas v ON d.id = v.id_dia_de_ventas
        JOIN usuarios u ON v.id_usuario = u.id
        WHERE u.nombre_usuario = %s
        """
        cursor.execute(query, (nombre_usuario,))
        resultados = cursor.fetchall()

        if resultados:
            print("Días de ventas del vendedor:")
            for row in resultados:
                id_dia_de_ventas, fecha_abierto, fecha_cerrado, estado = row
                print(f"ID: {id_dia_de_ventas}, Fecha Abierto: {fecha_abierto}, Fecha Cerrado: {fecha_cerrado}, Estado: {estado}")
        else:
            print("No se encontraron días de ventas para el vendedor con nombre de usuario:", nombre_usuario)
    
    except Exception as e:
        print(f"Error al filtrar días de ventas por vendedor: {e}")
    finally:
        cursor.close()



def ver_dia_de_ventas(conexion):
    try:
        cursor = conexion.cursor()

        # Obtener el ID del día de ventas abierto
        query = "SELECT id, fecha_abierto FROM dias_de_ventas WHERE estado = 'abierto' ORDER BY fecha_abierto DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()

        if not resultado:
            print("No hay un día de ventas abierto para generar un informe.")
            return

        id_dia_de_ventas, fecha_abierto = resultado
        print(f"\nInforme del Día de Ventas (ID: {id_dia_de_ventas}, Fecha: {fecha_abierto}):")

        # Obtener la cantidad de ventas con boleta y el monto total de esas ventas
        query_boletas = """
        SELECT COUNT(*), SUM(precio_total)
        FROM ventas
        WHERE id_dia_de_ventas = %s AND tipo_documento = 'boleta'
        """
        cursor.execute(query_boletas, (id_dia_de_ventas,))
        cantidad_boletas, total_boletas = cursor.fetchone()

        print(f"Cantidad de ventas con boleta: {cantidad_boletas}")
        print(f"Monto total de ventas con boleta: {total_boletas if total_boletas else 0}")

        # Obtener la cantidad de ventas con factura y el monto total de esas ventas
        query_facturas = """
        SELECT COUNT(*), SUM(precio_total)
        FROM ventas
        WHERE id_dia_de_ventas = %s AND tipo_documento = 'factura'
        """
        cursor.execute(query_facturas, (id_dia_de_ventas,))
        cantidad_facturas, total_facturas = cursor.fetchone()

        print(f"Cantidad de ventas con factura: {cantidad_facturas}")
        print(f"Monto total de ventas con factura: {total_facturas if total_facturas else 0}")

    except Exception as e:
        print(f"Error al generar el informe del día de ventas: {e}")
    finally:
        cursor.close()


def menu_vendedor(usuario_id, conexion):
    while True:
        print("\nMenú de Vendedor:")
        print("1. Realizar venta")
        print("2. Consultar producto por SKU")
        print("0. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            realizar_venta(usuario_id, conexion)
        elif opcion == '2':
            consultar_producto(conexion)
        elif opcion == '0':
            print("Saliendo del menú de Vendedor.")
            return True  # Regresar a la pantalla de login
        else:
            print("Opción no válida. Intente nuevamente.")


def realizar_venta(usuario_id, conexion):
    try:
        cursor = conexion.cursor()
        
        # Obtener el ID del día de ventas abierto
        query = "SELECT id FROM dias_de_ventas WHERE estado = 'abierto' ORDER BY fecha_abierto DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if not resultado:
            print("No hay un día de ventas abierto.")
            return
        
        id_dia_de_ventas = resultado[0]
        total_venta = 0
        productos_vendidos = []
        
        while True:
            codigo_producto = input("Ingrese el código del producto: ").strip()
            cantidad = int(input("Ingrese la cantidad: ").strip())
            
            # Buscar el producto por SKU
            query = "SELECT id, precio FROM productos WHERE sku = %s"
            cursor.execute(query, (codigo_producto,))
            producto = cursor.fetchone()
            
            if producto:
                producto_id, precio = producto
                total_producto = precio * cantidad
                total_venta += total_producto
                
                productos_vendidos.append((producto_id, cantidad, total_producto))
            else:
                print("Producto no encontrado. Verifique el código SKU ingresado.")
            
            while True:
                continuar = input("¿Desea agregar otro producto? (s/n): ").strip().lower()
                if continuar == 's':
                    break
                elif continuar == 'n':
                    break
                else:
                    print("Entrada no válida. Por favor, ingrese 's' para sí o 'n' para no.")
            
            if continuar == 'n':
                break
        
        if total_venta > 0:
            while True:
                tipo_documento = input("Seleccione la forma de pago (1 para Boleta, 2 para Factura): ").strip()
                
                if tipo_documento == '1':
                    tipo_documento_str = 'boleta'
                    break
                elif tipo_documento == '2':
                    tipo_documento_str = 'factura'
                    break
                else:
                    print("Opción no válida. Por favor, ingrese '1' para Boleta o '2' para Factura.")
            
            # Insertar la venta
            query = "INSERT INTO ventas (id_usuario, id_dia_de_ventas, precio_total, tipo_documento) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (usuario_id, id_dia_de_ventas, total_venta, tipo_documento_str))
            id_venta = cursor.lastrowid
            
            # Insertar los productos vendidos
            for producto_id, cantidad, total_producto in productos_vendidos:
                query = "INSERT INTO ventas_productos (id_venta, id_producto, cantidad) VALUES (%s, %s, %s)"
                cursor.execute(query, (id_venta, producto_id, cantidad))
            
            conexion.commit()
            print(f"Venta registrada exitosamente. ID de la venta: {id_venta}")
            
            # Generar boleta o factura
            if tipo_documento_str == 'boleta':
                generar_boleta(id_venta, conexion)
                print("Boleta generada exitosamente.")
            elif tipo_documento_str == 'factura':
                generar_factura(id_venta, conexion)
                print("Factura generada exitosamente.")
        else:
            print("No se registraron productos válidos para la venta.")
            conexion.rollback()
    
    except Exception as e:
        conexion.rollback()
        print(f"Error al registrar la venta: {e}")
    finally:
        cursor.close()



def generar_boleta(id_venta, conexion):
    try:
        cursor = conexion.cursor()
        
        # Insertar boleta
        query = "INSERT INTO boletas (id_venta) VALUES (%s)"
        cursor.execute(query, (id_venta,))
        id_boleta = cursor.lastrowid
        
        # Insertar detalles de la boleta
        query = """
        INSERT INTO detalles_boleta (id_boleta, id_producto, cantidad, total_pagar)
        SELECT %s, id_producto, cantidad, cantidad * (SELECT precio FROM productos WHERE id = id_producto)
        FROM ventas_productos
        WHERE id_venta = %s
        """
        cursor.execute(query, (id_boleta, id_venta))
        conexion.commit()
        
        # Mostrar detalle de la boleta
        query = """
        SELECT p.nombre, vb.cantidad, vb.total_pagar
        FROM detalles_boleta vb
        JOIN productos p ON vb.id_producto = p.id
        WHERE vb.id_boleta = %s
        """
        cursor.execute(query, (id_boleta,))
        detalles = cursor.fetchall()
        
        print(f"Boleta generada exitosamente. ID de la boleta: {id_boleta}")
        print("Detalles de la boleta:")
        for detalle in detalles:
            nombre_producto, cantidad, total_pagar = detalle
            print(f"Producto: {nombre_producto}, Cantidad: {cantidad}, Total a Pagar: {total_pagar}")
    
    except Exception as e:
        conexion.rollback()
        print(f"Error al generar la boleta: {e}")
    finally:
        cursor.close()


def generar_factura(id_venta, conexion):
    try:
        cursor = conexion.cursor()
        
        razon_social = input("Ingrese razón social del cliente: ")
        rut = input("Ingrese RUT del cliente: ")
        giro = input("Ingrese giro del cliente (opcional): ")
        direccion = input("Ingrese dirección del cliente: ")
        
        # Insertar factura
        query = "INSERT INTO facturas (id_venta, razon_social, rut, giro, direccion) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (id_venta, razon_social, rut, giro, direccion))
        id_factura = cursor.lastrowid
        
        # Insertar detalles de la factura
        query = """
        INSERT INTO detalles_factura (id_factura, id_producto, cantidad, total_neto, iva, total_final)
        SELECT %s, id_producto, cantidad, cantidad * (SELECT precio FROM productos WHERE id = id_producto) AS total_neto,
               cantidad * (SELECT precio FROM productos WHERE id = id_producto) * 0.19 AS iva,
               cantidad * (SELECT precio FROM productos WHERE id = id_producto) * 1.19 AS total_final
        FROM ventas_productos
        WHERE id_venta = %s
        """
        cursor.execute(query, (id_factura, id_venta))
        conexion.commit()
        print(f"Factura generada exitosamente. ID de la factura: {id_factura}")
    except Exception as e:
        conexion.rollback()
        print(f"Error al generar la factura: {e}")
    finally:
        cursor.close()


def consultar_producto(conexion):
    sku = input("Ingrese el SKU del producto: ")
    
    try:
        cursor = conexion.cursor()
        query = "SELECT nombre, precio, cantidad FROM productos WHERE sku = %s"
        cursor.execute(query, (sku,))
        resultado = cursor.fetchone()

        if resultado:
            nombre_producto, precio, cantidad = resultado
            print(f"Nombre: {nombre_producto}, Precio: {precio}, Cantidad: {cantidad}")
        else:
            print("Producto no encontrado.")
    
    except Exception as e:
        print(f"Error al consultar producto: {e}")
    finally:
        cursor.close()

def obtener_id_dia_de_ventas(conexion):
    try:
        cursor = conexion.cursor()
        query = "SELECT id FROM dias_de_ventas WHERE estado = 'abierto' ORDER BY fecha_abierto DESC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()

        if resultado:
            id_dia_de_ventas = resultado[0]
            return id_dia_de_ventas
        else:
            print("No se encontró un día de ventas abierto.")
            return None
    
    except Exception as e:
        print(f"Error al obtener ID del día de ventas: {e}")
        return None
    finally:
        cursor.close()
