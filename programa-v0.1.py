import os
import csv
from typing import List, Dict, Optional

ARCHIVO_CSV = "inventario.csv"
CAMPOS = ["codigo", "nombre", "precio", "stock"]

def mostrar_menu():
    print("=== SISTEMA DE INVENTARIO ===")
    print("1. Mostrar Inventario")
    print("2. Buscar producto")
    print("3. Agregar producto")
    print("4. Editar información de un producto")
    print("5. Eliminar producto")
    print("6. Generar reporte")
    print("7. Salir")


def main():
    inventario = cargar_inventario() 
    menu_abierto = True
    while menu_abierto:
        mostrar_menu()
        opcion = input("Introduce la opción:" )
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
                generar_reporte(inventario)
            case '7':
                print('Salir')
                menu_abierto = False
            case _:
                print("Vuelva a introducir una opción")

def cargar_inventario():
    inventario = []
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS)
            writer.writeheader()
        return inventario

    with open(ARCHIVO_CSV, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            # normalizar claves: Codigo -> codigo, Nombre -> nombre, etc.
            row = {k.strip().lower(): v for k, v in row.items() if k}

            # limpiar y convertir precio
            try:
                precio_txt = str(row.get("precio", "")).replace("$", "").replace(".", "").replace(",", ".")
                row["precio"] = float(precio_txt) if precio_txt else 0.0
            except ValueError:
                row["precio"] = 0.0

            # limpiar y convertir stock
            try:
                row["stock"] = int(row.get("stock", 0))
            except ValueError:
                row["stock"] = 0

            inventario.append(row)

    return inventario
def guardar_inventario(inventario):
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

def mostrar_inventario(inventario):
    if len(inventario) == 0:
        print("No hay productos registrados.")
        return

    print("\n--- Inventario ---")
    print(inventario)
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
    print("\n--- Buscar producto ---")
    termino = input("Ingrese código o nombre del producto: ").strip().lower()
    encontrados=[]

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

def agregar_producto(inventario):
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
        print("Producto agregado y guardado")
    else:
        print("Error al guardar el inventario ")
  

def eliminar_producto(inventario):
    print("\n--- Eliminar producto ---")
    pcodigo = input("Ingrese codigo: ").strip()

    for producto in inventario:
        if producto["codigo"] == pcodigo:
            inventario.remove(producto)
            guardar_inventario(inventario)
            print("Producto eliminado y CSV actualizado ✅")
            return

    print("Producto no encontrado ❌")

def editar_producto(inventario):
    print("\n--- Editar producto ---")
    pid = input("Ingrese código del producto a editar: ").strip()

    for producto in inventario:
        if producto["codigo"] == pid:
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
                print("Producto actualizado y guardado correctamente ✅")
            else:
                print("Error al guardar los cambios ❌")
            return

    print("Producto no encontrado ❌")

def generar_reporte():
    print("Ten tu reporte")
    
def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

main()