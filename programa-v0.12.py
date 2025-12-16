# ==============================
# SISTEMA DE INVENTARIO (CSV)
# ==============================
# Este programa permite:
# 1) Mostrar inventario en formato tabla
# 2) Buscar productos por código o nombre
# 3) Agregar productos
# 4) Editar productos (nombre / precio / stock)
# 5) Eliminar productos
# 6) Registrar venta 
# 7) Generar un reporte 
# 8) salir
# Los datos se guardan en un archivo CSV llamado "inventario.csv"
# con las columnas: codigo, nombre, precio, stock
# ==============================

import os
import csv
from typing import List, Dict, Optional 
import time

# Nombre del archivo CSV que guarda el inventario
ARCHIVO_CSV = "inventario.csv"

# Columnas que usará el CSV (encabezados)
CAMPOS = ["codigo", "nombre", "precio", "stock","vendidos"]

# ------------------------------
# MENÚ PRINCIPAL
# ------------------------------
def mostrar_menu():
    """Muestra las opciones disponibles del sistema."""

    print("=== SISTEMA DE INVENTARIO ===")
    print("1. Mostrar Inventario")
    print("2. Buscar producto")
    print("3. Agregar producto nuevo")
    print("4. Editar producto")
    print("5. Eliminar producto")
    print("6. Registrar venta")
    print("7. Generar reporte")
    print("8. Salir")
    print("=== === === === === === ===")

def main():
    """
    Función principal del programa.
    - Carga el inventario desde el CSV.
    - Muestra el menú en un bucle (while).
    - Ejecuta la opción seleccionada por el usuario.
    """
    inventario = cargar_inventario()  # Cargamos productos desde el CSV (lista de diccionarios)

    menu_abierto = True
    while menu_abierto:
        mostrar_menu()
        print("\n")
        opcion = input("Introduce la opción:")
        
        # Identificamos qué función vamos a ejecutar
        funcion_actual = None
        
        match opcion:
            case '1': funcion_actual = mostrar_inventario
            case '2': funcion_actual = buscar_producto
            case '3': funcion_actual = agregar_producto
            case '4': funcion_actual = editar_producto
            case '5': funcion_actual = eliminar_producto
            case '6': funcion_actual = registrar_venta
            case '7': funcion_actual = generar_reporte
            case '8': 
                print('Salir')
                menu_abierto = False
            case _:
                print("Opción inválida")
                input("Enter para continuar")

        # 2. Si se seleccionó una función válida, entramos al ciclo de "Reintento"
        if funcion_actual:
            while True:
                limpiar()
                repetir = funcion_actual(inventario)
                if not repetir:
                    limpiar()
                    break

# ------------------------------
# LECTURA Y ESCRITURA DEL CSV
# ------------------------------
def cargar_inventario():
    """
    Lee el archivo CSV y carga los productos en memoria.
    Retorna una lista de diccionarios:
    [
      {"codigo": "...", "nombre": "...", "precio": 0.0, "stock": 0},
      ...
    ]

    Detalles importantes:
    - Si el archivo no existe, lo crea con encabezados y devuelve lista vacía.
    - Usa encoding 'utf-8-sig' para manejar BOM (Excel a veces lo agrega).
    - Usa delimiter ';' porque Excel en Chile suele exportar con punto y coma.
    """
    inventario = []

    # Si el CSV no existe, se crea con encabezados
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS)
            writer.writeheader()
        return inventario

    # Abrimos el CSV con utf-8-sig para quitar BOM automáticamente
    with open(ARCHIVO_CSV, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            # Normalizamos claves: "Codigo" -> "codigo" (minúscula) y sin espacios
            row = {k.strip().lower(): v for k, v in row.items() if k}

            # Convertimos precio a float
            try:
                precio_raw = str(row.get("precio", "")).strip().replace("$", "").replace(" ", "")
                if "," in precio_raw and "." not in precio_raw:
                    precio_raw = precio_raw.replace(",", ".")
                elif "." in precio_raw and "," in precio_raw:
                    precio_raw = precio_raw.replace(".", "").replace(",", ".")

                row["precio"] = float(precio_raw) if precio_raw else 0.0
            except ValueError:
                row["precio"] = 0.0

            # Convertimos stock a int
            try:
                row["stock"] = int(row.get("stock", 0))
            except ValueError:
                row["stock"] = 0

            try:
                row["vendidos"] = int(row.get("vendidos",0))
            except ValueError:
                row["vendidos"] = 0
            # Aseguramos que exista "codigo"
            if "codigo" not in row:
                row["codigo"] = ""

            inventario.append(row)

    return inventario

def guardar_inventario(inventario):
    """
    Guarda la lista de productos en el CSV.
    Retorna True si guardó bien, False si hubo error.

    Se guarda con:
    - encoding 'utf-8-sig' (compatible con Excel)
    - delimiter ';'
    """
    try:
        with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
            writer.writeheader()

            for p in inventario:
                writer.writerow({
                    "codigo": p["codigo"],
                    "nombre": p["nombre"],
                    "precio": p["precio"],
                    "stock": p["stock"],
                    "vendidos": p.get("vendidos",0)
                })
        return True
    except Exception as e:
        print("ERROR al guardar:", e)
        return False

# ------------------------------
# MOSTRAR / BUSCAR
# ------------------------------
def mostrar_inventario(inventario):
    """
    Muestra todos los productos en formato tabla.
    """
    if len(inventario) == 0:
        print("No hay productos registrados.")
        return

    print("\n--- Inventario ---")
    print("\n" + "-" * 60)
    print(f"{'CÓDIGO':<10} {'NOMBRE':<20} {'PRECIO':<10} {'STOCK':<10} {'VENDIDOS':<10}")
    print("-" * 60)

    for producto in inventario:
        print(
            f"{producto['codigo']:<10} "
            f"{producto['nombre']:<20} "
            f"{producto['precio']:<10.2f} "
            f"{producto['stock']:<10} "
            f"{producto['vendidos']:<10} "
        )

    print("-" * 60)

    return decidir_continuar("volver a mostrar el inventario")

def buscar_producto(inventario):
    """
    Busca productos por:
    - Código exacto
    - Parte del nombre (contiene el texto)
    Muestra resultados en una tabla.
    """
    print("\n--- Buscar producto ---")
    termino = input("Ingrese código o nombre del producto: ").strip().lower()

    encontrados = []

    for producto in inventario:
        if (
            termino == str(producto["codigo"]).lower()
            or termino in producto["nombre"].lower()
        ):
            encontrados.append(producto)

    if len(encontrados) == 0:
        print("\nNo se encontró ningún producto.\n")
        return

    print("\n" + "-" * 60)
    print(f"{'CÓDIGO':<10} {'NOMBRE':<20} {'PRECIO':<10} {'STOCK':<10}")
    print("-" * 60)

    for producto in encontrados:
        print(
            f"{producto['codigo']:<10} "
            f"{producto['nombre']:<20} "
            f"{producto['precio']:<10} "
            f"{producto['stock']:<10}"
        )

    print("-" * 60)

    return decidir_continuar("volver a buscar producto")

# ------------------------------
# AGREGAR / EDITAR / ELIMINAR
# ------------------------------
def agregar_producto(inventario):
    while True:
        print("\n--- Agregar producto ---")

        pcodigo = input("Código: ").strip()
        if any(p["codigo"] == pcodigo for p in inventario):
            print("Error: ya existe un producto con ese código.")
            continue

        nombre = input("Nombre: ").strip()

        while True:
            try:
                precio = float(input("Precio: ").strip())
                if precio < 0:
                    raise ValueError
                break
            except ValueError:
                print("Error: el precio debe ser un número positivo.")

        while True:
            try:
                stock = int(input("Stock: ").strip())
                if stock < 0:
                    raise ValueError
                break
            except ValueError:
                print("Error: el stock debe ser un entero positivo.")

        print("\nProducto a agregar:")
        print(f"  Código : {pcodigo}")
        print(f"  Nombre : {nombre}")
        print(f"  Precio : {precio}")
        print(f"  Stock  : {stock}")

        confirmar = input("\n¿Confirmar agregado? (s/n): ").strip().lower()

        if confirmar != "s":
            print("\nPresiona [Enter] para volver al menú")
            print("Escribe [Espacio] y [Enter] para volver a ingresar datos")
            respuesta = input("> ")

            if respuesta == " ":
                limpiar()
                continue
            else:
                return False   # ← VOLVER AL MENÚ

        producto = {
            "codigo": pcodigo,
            "nombre": nombre,
            "precio": precio,
            "stock": stock,
            "vendidos": 0
        }

        inventario.append(producto)

        if guardar_inventario(inventario):
            print("Producto agregado y guardado correctamente.")
            time.sleep(1)
        else:
            print("Error al guardar el producto.")
            time.sleep(1)

        return False  # ← después de agregar, volver al menú


def eliminar_producto(inventario):
    """
    Elimina un producto según su código.
    - Si existe, lo remueve de la lista y actualiza el CSV.
    """
    print("\n--- Eliminar producto ---")
    pcodigo = input("Ingrese codigo: ").strip()

    for producto in inventario:
        if producto["codigo"] == pcodigo:
            inventario.remove(producto)
            guardar_inventario(inventario)
            print("Producto eliminado del inventario")
            time.sleep(1)
            return decidir_continuar("volver a borrar producto")

    print("Producto no encontrado")
    return decidir_continuar("volver a borrar producto")

def editar_producto(inventario):
    """
    Edita un producto según su código:
    - Muestra el producto actual en tabla.
    - Permite editar: nombre / precio / stock.
    - Guarda cambios en CSV.
    """
    print("\n--- Editar producto ---")
    pid = input("Ingrese código del producto a editar: ").strip()

    for producto in inventario:
        if producto["codigo"] == pid:
            # Mostrar producto actual en formato tabla
            print("\nProducto actual:")
            print("-" * 60)
            print(f"{'CÓDIGO':<10} {'NOMBRE':<20} {'PRECIO':<10} {'STOCK':<10}")
            print("-" * 60)
            print(
                f"{producto['codigo']:<10} "
                f"{producto['nombre']:<20} "
                f"{producto['precio']:<10} "
                f"{producto['stock']:<10}"
            )
            print("-" * 60)

            # Submenú de edición
            print("\n¿Qué dato deseas editar?")
            print("1. Nombre")
            print("2. Precio")
            print("3. Stock")
            print("4. Cancelar")

            opcion = input("Selecciona una opción (1-4): ").strip()

            if opcion == "1":
                nuevo_nombre = input("Nuevo nombre: ").strip()
                producto["nombre"] = nuevo_nombre
                print(f"Nombre actualizado a: {nuevo_nombre}")

            elif opcion == "2":
                try:
                    nuevo_precio = float(input("Nuevo precio: ").strip())
                    producto["precio"] = nuevo_precio
                    print(f"Precio actualizado a: {nuevo_precio}")
                except ValueError:
                    print("Error: precio inválido.")

            elif opcion == "3":
                try:
                    nuevo_stock = int(input("Nuevo stock: ").strip())
                    producto["stock"] = nuevo_stock
                    print(f"Stock actualizado a: {nuevo_stock}")
                except ValueError:
                    print("Error: stock inválido.")

            elif opcion == "4":
                print("Operación cancelada.")

            else:
                print("Opción no válida.")

            # Guardar los cambios después de la edición
            if guardar_inventario(inventario):
                print("Producto actualizado y guardado correctamente ")
            else:
                print("Error al guardar los cambios")
            return decidir_continuar("volver a editar producto")

    print("Producto no encontrado ")
    time.sleep(1)
    return decidir_continuar("volver a editar producto")

def registrar_venta(inventario):
    print("\n--- Registrar venta ---")
    codigo = input("Ingrese código: ").strip()

    for producto in inventario:
        if producto["codigo"] == codigo:
            print(f"Producto: {producto['nombre']} | Stock actual: {producto['stock']}")

            try:
                cantidad = int(input("Cantidad vendida: ").strip())
            except ValueError:
                print("Cantidad inválida.")
                time.sleep(1)
                return

            if cantidad <= 0:
                print("La cantidad debe ser mayor a 0.")
                time.sleep(1)
                return

            if cantidad > producto["stock"]:
                print("No hay stock suficiente.")
                time.sleep(1)
                return

            producto["stock"] -= cantidad
            producto["vendidos"] = producto.get("vendidos", 0) + cantidad

            if guardar_inventario(inventario):
                print("Venta registrada ")
                time.sleep(1)
            else:
                print("Error al guardar ")
                time.sleep(1)

            return

    print("Producto no encontrado")
    
# ------------------------------
# REPORTE 
# ------------------------------

def generar_reporte(inventario):
    print("\n=== REPORTE DE INVENTARIO ===")

    if len(inventario) == 0:
        print("No hay productos registrados.")
        return

    total_productos = len(inventario)
    total_unidades_stock = 0
    valor_total_inventario = 0
    total_unidades_vendidas = 0
    valor_total_vendido = 0

    for p in inventario:
        total_unidades_stock += p["stock"]
        valor_total_inventario += p["stock"] * p["precio"]

        vendidos = p.get("vendidos", 0)
        total_unidades_vendidas += vendidos
        valor_total_vendido += vendidos * p["precio"]

    # Resumen general
    print("\n--- Resumen General ---")
    print(f"Total de productos distintos : {total_productos}")
    print(f"Total de unidades en stock   : {total_unidades_stock}")
    print(f"Valor total del inventario   : ${valor_total_inventario:.2f}")
    print(f"Total de unidades vendidas   : {total_unidades_vendidas}")
    print(f"Valor total vendido          : ${valor_total_vendido:.2f}")

    # Productos con stock bajo
    umbral = 5
    print(f"\n--- Productos con stock bajo (<= {umbral}) ---")
    stock_bajo = [p for p in inventario if p["stock"] <= umbral]

    if len(stock_bajo) == 0:
        print("No hay productos con stock bajo.")
    else:
        print("-" * 60)
        print(f"{'CÓDIGO':<10} {'NOMBRE':<20} {'STOCK':<10}")
        print("-" * 60)
        for p in stock_bajo:
            print(f"{p['codigo']:<10} {p['nombre']:<20} {p['stock']:<10}")
        print("-" * 60)

    # Top productos más vendidos
    print("\n--- Top 3 productos más vendidos ---")
    top = sorted(inventario, key=lambda x: x.get("vendidos", 0), reverse=True)[:3]

    print("-" * 80)
    print(f"{'CÓDIGO':<10} {'NOMBRE':<20} {'VENDIDOS':<10} {'TOTAL VENDIDO ($)':<20}")
    print("-" * 80)

    for p in top:
        vendidos = p.get("vendidos", 0)
        total_vendido = vendidos * p.get("precio", 0)

        print(
            f"{p['codigo']:<10} "
            f"{p['nombre']:<20} "
            f"{vendidos:<10} "
            f"{total_vendido:<20.2f}"
        )

    print("-" * 80)

    return decidir_continuar("volver a generar reporte")

# ------------------------------
# LIMPIAR PANTALLA (opcional)
# ------------------------------
def limpiar():
    """Limpia la consola."""
    os.system("cls" if os.name == "nt" else "clear")

# ------------------------------
# Volver al menu o repetir
# ------------------------------
def decidir_continuar(mensaje_repetir="Repetir esta acción"):
    print("\n" + "-" * 60)
    print("Presiona [Enter] para volver al menú")
    print(f"Escribe [Espacio] y [Enter] para {mensaje_repetir}")
    return input("> ") == " "

# Ejecutar programa
main()
