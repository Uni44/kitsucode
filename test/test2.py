# -*- coding: utf-8 -*-
import time

def saludo(nombre):
    print(f"Hola {nombre}, bienvenido a tu editor personalizado.")
    time.sleep(0.5)

def prueba_colores():
    print("Colores (modo seguro):")
    print("\033[92m[OK] Verde (Éxito)\033[0m")
    print("\033[93m[!] Amarillo (Advertencia)\033[0m")
    print("\033[91m[X] Rojo (Error)\033[0m")
    print("\033[96m[i] Cian (Info)\033[0m")

def calcular(a, b):
    return a + b, a * b

def lanzar_error():
    raise ValueError("Esto es un error de prueba (boom!)")

if __name__ == "__main__":
    print("== Test del editor en ejecución ==")
    try:
        nombre = input("¿Cómo te llamás?: ")
    except Exception:
        nombre = "Desconocido"
    saludo(nombre)

    print("\n== Colores de terminal ==")
    prueba_colores()

    print("\n== Operaciones básicas ==")
    suma, producto = calcular(5, 3)
    print(f"5 + 3 = {suma}")
    print(f"5 * 3 = {producto}")

    print("\n== Prueba de error ==")
    try:
        lanzar_error()
    except Exception as e:
        print(f"\033[91m[ERROR]: {e}\033[0m")

    print("\n== Fin del test ==")