from DB.conexion import DAO
from datetime import datetime
import re
from itertools import cycle
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

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
        print("6. Ver días cerrados con vendedores")
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
        elif opcion == '6':
            ver_dias_cerrados_con_vendedores(conexion)
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
        
        # Solicitar al usuario que ingrese la fecha deseada
        dia = input("Ingrese el día (DD): ")
        mes = input("Ingrese el mes (MM): ")
        anio = input("Ingrese el año (YYYY): ")
        
        # Formatear la fecha
        fecha_deseada = f"{anio}-{mes}-{dia}"
        
        # Obtener todos los IDs de días de ventas correspondientes a la fecha ingresada
        query_id_dias = """
        SELECT id, fecha_abierto, fecha_cerrado
        FROM dias_de_ventas
        WHERE DATE(fecha_abierto) = %s OR DATE(fecha_cerrado) = %s
        """
        cursor.execute(query_id_dias, (fecha_deseada, fecha_deseada))
        resultados = cursor.fetchall()

        if not resultados:
            print("No se encontró un día de ventas para la fecha ingresada.")
            return
        
        for resultado in resultados:
            id_dia_de_ventas, fecha_abierto, fecha_cerrado = resultado
            print(f"\nInforme del Día de Ventas (ID: {id_dia_de_ventas}, Fecha Abierto: {fecha_abierto}, Fecha Cerrado: {fecha_cerrado}):")

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

            # Leer los resultados pendientes del cursor
            cursor.fetchall()
    
    except Exception as e:
        print(f"Error al generar el informe del día de ventas: {e}")
    finally:
        cursor.close()


def ver_dias_cerrados_con_vendedores(conexion):
    try:
        cursor = conexion.cursor()
        
        # Consultar días de ventas cerrados con los nombres de los vendedores y el conteo de ventas
        query = """
        SELECT d.id AS dia_id, d.fecha_abierto, d.fecha_cerrado, d.estado, u.nombre_usuario, COUNT(v.id) AS cantidad_ventas
        FROM dias_de_ventas d
        JOIN ventas v ON d.id = v.id_dia_de_ventas
        JOIN usuarios u ON v.id_usuario = u.id
        WHERE d.estado = 'cerrado'
        GROUP BY d.id, u.nombre_usuario
        ORDER BY d.fecha_cerrado DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        if resultados:
            dias_cerrados = {}
            for row in resultados:
                dia_id, fecha_abierto, fecha_cerrado, estado, nombre_usuario, cantidad_ventas = row
                if dia_id not in dias_cerrados:
                    dias_cerrados[dia_id] = {
                        'fecha_abierto': fecha_abierto,
                        'fecha_cerrado': fecha_cerrado,
                        'estado': estado,
                        'vendedores': {}
                    }
                dias_cerrados[dia_id]['vendedores'][nombre_usuario] = cantidad_ventas
            
            # Mostrar los días cerrados con los vendedores
            print("\nDías de ventas cerrados con vendedores:")
            for dia_id, info in dias_cerrados.items():
                print(f"ID Día de Ventas: {dia_id}")
                print(f"Fecha Abierto: {info['fecha_abierto']}")
                print(f"Fecha Cerrado: {info['fecha_cerrado']}")
                print(f"Estado: {info['estado']}")
                
                vendedores_info = [f"{nombre} ({cantidad})" for nombre, cantidad in info['vendedores'].items()]
                print(f"Vendedores: {', '.join(vendedores_info)}")
                print("-" * 40)
        else:
            print("No hay días de ventas cerrados.")
    
    except Exception as e:
        print(f"Error al consultar días cerrados con vendedores: {e}")
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
            query = "SELECT id, precio, cantidad FROM productos WHERE sku = %s"
            cursor.execute(query, (codigo_producto,))
            producto = cursor.fetchone()
            
            if producto:
                producto_id, precio, cantidad_disponible = producto
                if cantidad <= cantidad_disponible:
                    total_producto = precio * cantidad
                    total_venta += total_producto
                    productos_vendidos.append((producto_id, cantidad, total_producto))
                else:
                    print("No hay suficiente cantidad disponible para el producto.")
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
                
                # Actualizar la cantidad del producto en la base de datos
                query = "UPDATE productos SET cantidad = cantidad - %s WHERE id = %s"
                cursor.execute(query, (cantidad, producto_id))
            
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
        
        # Insertar la boleta
        query = "INSERT INTO boletas (id_venta) VALUES (%s)"
        cursor.execute(query, (id_venta,))
        id_boleta = cursor.lastrowid
        
        # Obtener detalles de la venta
        query = """
        SELECT p.nombre, vp.cantidad, p.precio
        FROM ventas_productos vp
        JOIN productos p ON vp.id_producto = p.id
        WHERE vp.id_venta = %s
        """
        cursor.execute(query, (id_venta,))
        detalles = cursor.fetchall()
        
        # Calcular totales
        total_venta = 0
        nombre_archivo = f"boleta_{id_boleta}.pdf"
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        c.drawString(1 * inch, 10 * inch, f"Boleta de Venta ID: {id_venta}")
        c.drawString(1 * inch, 9.5 * inch, f"ID Boleta: {id_boleta}")
        c.drawString(1 * inch, 9 * inch, "Detalles de productos:")
        c.drawString(1 * inch, 8.5 * inch, f"{'Producto':<20} {'Cantidad':<10} {'Precio Unitario':<15} {'Total Producto':<15}")
        
        y_position = 8 * inch
        
        for detalle in detalles:
            nombre_producto, cantidad, precio = detalle
            total_producto = cantidad * precio
            total_venta += total_producto
            
            # Mostrar detalles en el PDF
            nombre_producto_corto = nombre_producto[:20]
            c.drawString(1 * inch, y_position, f"{nombre_producto_corto:<20} {cantidad:<10} {precio:<15.2f} {total_producto:<15.2f}")
            y_position -= 0.5 * inch
        
        # Mostrar total
        c.drawString(1 * inch, y_position, f"Total a pagar: {total_venta:.2f}")
        c.save()
        
        conexion.commit()
        print(f"Boleta generada exitosamente. Archivo: {nombre_archivo}")
    
    except Exception as e:
        conexion.rollback()
        print(f"Error al generar la boleta: {e}")
    finally:
        cursor.close()





def digito_verificador(rut):
    """
    Calcula el dígito verificador para un RUT dado.
    """
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    dv = (-s) % 11
    return 'K' if dv == 10 else str(dv)

def validar_rut(rut):
    """
    Valida un RUT en el formato tradicional chileno.
    """
    # Eliminar caracteres no numéricos y letras
    rut = re.sub(r'[^0-9Kk]', '', rut)
    
    if len(rut) < 2:
        return False

    # Extraer el dígito verificador y el cuerpo del RUT
    rut_cuerpo = rut[:-1]
    digito_verificador_ingresado = rut[-1].upper()

    if not rut_cuerpo.isdigit():
        return False

    # Calcular el dígito verificador
    digito_calculado = digito_verificador(rut_cuerpo)
    
    # Verificar que el dígito verificador coincida con el calculado
    return digito_verificador_ingresado == digito_calculado

def ingresar_rut():
    while True:
        rut = input("Ingrese RUT del cliente (solo números y dígito verificador, sin puntos ni guiones): ").strip()
        rut = rut.upper()  # Asegurarse de que el RUT ingresado esté en mayúscula
        if validar_rut(rut):
            return rut
        else:
            print("RUT inválido. Por favor, ingrese un RUT válido.")

def formatear_rut(rut):
    """
    Formatea un RUT para incluir puntos y guiones.
    """
    rut = rut.upper()
    rut = re.sub(r'[^0-9K]', '', rut)
    rut_cuerpo = rut[:-1]
    digito_verificador = rut[-1]
    
    # Formatear el RUT
    rut_formateado = '{:,.0f}-{}'.format(float(rut_cuerpo), digito_verificador)
    rut_formateado = rut_formateado.replace(',', '.').replace(' ', '')
    
    return rut_formateado


def generar_factura(id_venta, conexion):
    try:
        cursor = conexion.cursor()
        
        razon_social = input("Ingrese razón social del cliente: ").strip()
        rut = ingresar_rut()  # Usa la función para ingresar el RUT validado
        giro = input("Ingrese giro del cliente (opcional): ").strip()
        direccion = input("Ingrese dirección del cliente: ").strip()
        
        # Formatear el RUT antes de insertarlo en la base de datos
        rut_formateado = formatear_rut(rut)
        
        # Insertar la factura
        query = """
        INSERT INTO facturas (id_venta, razon_social, rut, giro, direccion)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_venta, razon_social, rut_formateado, giro, direccion))
        id_factura = cursor.lastrowid
        
        # Obtener detalles de la venta para calcular totales
        query = """
        SELECT p.id, p.nombre, vp.cantidad, p.precio
        FROM ventas_productos vp
        JOIN productos p ON vp.id_producto = p.id
        WHERE vp.id_venta = %s
        """
        cursor.execute(query, (id_venta,))
        detalles = cursor.fetchall()

        total_compra = 0
        total_iva = 0
        total_final_compra = 0
        
        nombre_archivo = f"factura_{id_factura}.pdf"
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        c.drawString(1 * inch, 10 * inch, f"Factura de Venta ID: {id_venta}")
        c.drawString(1 * inch, 9.5 * inch, f"Razón social: {razon_social}")
        c.drawString(1 * inch, 9 * inch, f"RUT: {rut_formateado}")
        c.drawString(1 * inch, 8.5 * inch, f"Giro: {giro}")
        c.drawString(1 * inch, 8 * inch, f"Dirección: {direccion}")
        c.drawString(1 * inch, 7.5 * inch, "Detalles de productos:")
        c.drawString(1 * inch, 7 * inch, f"{'Producto':<20} {'Cantidad':<10} {'Total Neto':<10} {'IVA':<10} {'Total Final':<10}")

        y_position = 6.5 * inch

        for detalle in detalles:
            id_producto, nombre_producto, cantidad, precio = detalle
            total_neto = cantidad * precio
            iva = total_neto * 0.19
            total_final = total_neto + iva
            
            # Acumular los totales
            total_compra += total_neto
            total_iva += iva
            total_final_compra += total_final

            # Mostrar detalles en el PDF
            nombre_producto_corto = nombre_producto[:20]
            c.drawString(1 * inch, y_position, f"{nombre_producto_corto:<20} {cantidad:<10} {total_neto:<10.2f} {iva:<10.2f} {total_final:<10.2f}")
            y_position -= 0.5 * inch
            
            # Insertar detalles de la factura
            query = """
            INSERT INTO detalles_factura (id_factura, id_producto, cantidad, total_neto, iva, total_final)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_factura, id_producto, cantidad, total_neto, iva, total_final))
        
        c.drawString(1 * inch, y_position, f"Total Neto: {total_compra:.2f}")
        c.drawString(1 * inch, y_position - 0.5 * inch, f"Total IVA (19%): {total_iva:.2f}")
        c.drawString(1 * inch, y_position - 1 * inch, f"Total Final (Total Neto + IVA): {total_final_compra:.2f}")
        
        c.save()
        
        conexion.commit()
        print(f"Factura generada exitosamente. Archivo: {nombre_archivo}")
    
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





def generar_pdf_boleta(id_venta, productos, total):
    nombre_archivo = f"Boleta_ID_{id_venta}.pdf"
    ruta_archivo = os.path.join(os.getcwd(), nombre_archivo)

    c = canvas.Canvas(ruta_archivo, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "Boleta")

    c.setFont("Helvetica", 12)
    y = height - 100
    c.drawString(72, y, f"ID de Venta: {id_venta}")
    y -= 20
    c.drawString(72, y, f"Fecha: {fecha_actual()}")

    c.drawString(72, y - 20, "Productos:")
    y -= 40

    for producto in productos:
        c.drawString(72, y, f"Producto: {producto['nombre']}, Cantidad: {producto['cantidad']}, Precio Unitario: {producto['precio_unitario']}, Total: {producto['total']}")
        y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y - 20, f"Total a Pagar: {total}")

    c.showPage()
    c.save()

    print(f"PDF de Boleta generado exitosamente: {ruta_archivo}")

def generar_pdf_factura(id_venta, productos, total, numero_factura, neto, iva):
    nombre_archivo = f"Factura_ID_{id_venta}.pdf"
    ruta_archivo = os.path.join(os.getcwd(), nombre_archivo)

    c = canvas.Canvas(ruta_archivo, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "Factura")

    c.setFont("Helvetica", 12)
    y = height - 100
    c.drawString(72, y, f"ID de Venta: {id_venta}")
    y -= 20
    c.drawString(72, y, f"Fecha: {fecha_actual()}")
    y -= 20
    c.drawString(72, y, f"Número de Factura: {numero_factura}")

    c.drawString(72, y - 20, "Productos:")
    y -= 40

    for producto in productos:
        c.drawString(72, y, f"Producto: {producto['nombre']}, Cantidad: {producto['cantidad']}, Precio Unitario: {producto['precio_unitario']}, Total: {producto['total']}")
        y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y - 20, f"Subtotal: {neto}")
    y -= 20
    c.drawString(72, y - 20, f"IVA: {iva}")
    y -= 20
    c.drawString(72, y - 20, f"Total a Pagar: {total}")

    c.showPage()
    c.save()

    print(f"PDF de Factura generado exitosamente: {ruta_archivo}")

def fecha_actual():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



