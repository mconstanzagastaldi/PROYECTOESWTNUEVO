"""
================================================================================
PUNTO DE ENTRADA PRINCIPAL (MAIN.PY)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Lanza la Consola Clínica Electromédica de Ondas de Choque (PySide6).
================================================================================
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en sys.path
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRECTORIO_RAIZ)

from PySide6.QtWidgets import QApplication
from interfaz.ventana_principal import VentanaPrincipal
from interfaz.consola_eswt import ConsolaESWT


def main():
    # Habilitar soporte para pantallas de alta densidad de píxeles (High DPI)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("SIMULADOR ESWT - SISTEMA INTEGRAL")
    app.setOrganizationName("UNER - Facultad de Ingenieria")
    app.setApplicationVersion("1.0.0")

    # Si se pasa el argumento --consola se abre la consola médica, por defecto la ventana de 10 módulos
    if len(sys.argv) > 1 and "--consola" in sys.argv:
        ventana = ConsolaESWT()
    else:
        ventana = VentanaPrincipal()

    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
