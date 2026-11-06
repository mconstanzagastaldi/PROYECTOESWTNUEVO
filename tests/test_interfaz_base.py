"""
Prueba unitaria para verificar la inicialización de la interfaz y la navegación.
"""

import os
import pytest
from PySide6.QtWidgets import QApplication
from interfaz.ventana_principal import VentanaPrincipal


@pytest.fixture(scope="session")
def qapp():
    # Ejecutar Qt en modo headless / offscreen para pruebas continuas sin monitor
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_inicializacion_ventana_principal(qapp):
    ventana = VentanaPrincipal()
    assert ventana is not None
    assert ventana.windowTitle().startswith("SIMULADOR ESWT")
    assert ventana.stack.count() == 10


def test_navegacion_entre_modulos(qapp):
    ventana = VentanaPrincipal()
    # Navegar por los 10 módulos y verificar que el stack cambia correctamente
    for i in range(10):
        ventana.navegar_a_modulo(i)
        assert ventana.stack.currentIndex() == i
        assert ventana.botones_nav[i].isChecked()

