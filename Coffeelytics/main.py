"""
Punto de entrada de Coffeelytics.

Ejecutar desde la carpeta Coffeelytics:
    python3 main.py        (Linux / macOS)
    python main.py         (Windows)

La carpeta del archivo se agrega a sys.path para que los paquetes
(config, entidades, repositorios, servicios, documentos, interfaz) se
resuelvan igual sin importar desde donde se lance el programa.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from interfaz.app_coffeelytics import AppCoffeelytics  # noqa: E402


if __name__ == "__main__":
    AppCoffeelytics().ejecutar()
