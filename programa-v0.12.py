# ==============================
# SISTEMA DE INVENTARIO (CSV)
# ==============================
# Este programa permite:
# 1) Mostrar inventario en formato tabla
# 2) Buscar productos por código o nombre
# 3) Agregar productos
# 4) Editar productos (nombre / precio / stock)
# 5) Eliminar productos
# 6) Generar un reporte (pendiente de implementar)
#
# Los datos se guardan en un archivo CSV llamado "inventario.csv"
# con las columnas: codigo, nombre, precio, stock
# ==============================

import os
import csv
from typing import List, Dict, Optional 

# Nombre del archivo CSV que guarda el inventario
ARCHIVO_CSV = "inventario.csv"

# Columnas que usará el CSV (encabezados)
CAMPOS = ["codigo", "nombre", "precio", "stock"]


# ------------------------------
# MENÚ PRINCIPAL
# ------------------------------
def mostrar_menu():
    """Muestra las opciones disponibles del sistema."""

    print("=== SISTEMA DE INVENTARIO ===")
    print("1. Mostrar Inventario")
    print("2. Buscar producto")
    print("3. Agregar producto")
    print("4. Editar información de un producto")
    print("5. Eliminar producto")
    print("6. Generar reporte")
    print("7. Salir")


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
        opcion = input("Introduce la opción:")

        # match/case requiere
        match opcion:
            case '1':
                mostrar_inventario(inventario)
            case '2':
                buscar_producto(inventario)
            case '3':
                agregar_producto(inventario)
            case '4':
                editar_producto(inventario)
            case '5':
                eliminar_producto(inventario)
            case '6':
                # falta crear esta funcion
                generar_reporte()
            case '7':
                print('Salir')
                menu_abierto = False
            case _:
                print("Vuelva a introducir una opción")


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
                precio_txt = str(row.get("precio", "")).replace("$", "").replace(".", "").replace(",", ".")
                row["precio"] = float(precio_txt) if precio_txt else 0.0
            except ValueError:
                row["precio"] = 0.0

            # Convertimos stock a int
            try:
                row["stock"] = int(row.get("stock", 0))
            except ValueError:
                row["stock"] = 0

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
                    "stock": p["stock"]
                })
        return True
    except Exception:
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
    print(f"{'CÓDIGO':<10} {'NOMBRE':<20} {'PRECIO':<10} {'STOCK':<10}")
    print("-" * 60)

    for producto in inventario:
        print(
            f"{producto['codigo']:<10} "
            f"{producto['nombre']:<20} "
            f"{producto['precio']:<10} "
            f"{producto['stock']:<10}"
        )

    print("-" * 60)


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


# ------------------------------
# AGREGAR / EDITAR / ELIMINAR
# ------------------------------
def agregar_producto(inventario):
    """
    Agrega un producto al inventario:
    - Pide código, nombre, precio, stock.
    - Valida que el código no exista.
    - Guarda cambios en CSV.
    """
    print("\n--- Agregar producto ---")
    pcodigo = input("codigo: ").strip()

    # Validar que no exista el codigo
    for p in inventario:
        if p["codigo"] == pcodigo:
            print("Error: ya existe un producto con ese codigo.")
            return

    nombre = input("Nombre: ").strip()

    try:
        precio = float(input("Precio: ").strip())
        stock = int(input("Stock: ").strip())
    except ValueError:
        print("Error: precio debe ser número y stock debe ser entero.")
        return

    producto = {"codigo": pcodigo, "nombre": nombre, "precio": precio, "stock": stock}
    inventario.append(producto)

    ok = guardar_inventario(inventario)

    if ok:
        print("Producto agregado y guardado correctametn")
    else:
        print("Error al guardar producto en el inventario ")


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
            return

    print("Producto no encontrado")


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
            return

    print("Producto no encontrado ")


# ------------------------------
# REPORTE (pendiente)
# ------------------------------
def generar_reporte():
    """
    Genera un reporte del inventario.
    """
    print("Ten tu reporte")


# ------------------------------
# LIMPIAR PANTALLA (opcional)
# ------------------------------
def limpiar():
    """Limpia la consola."""
    os.system("cls" if os.name == "nt" else "clear")


# Ejecutar programa
main()