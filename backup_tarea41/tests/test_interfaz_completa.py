"""
Prueba de integración de la interfaz completa con todos los módulos activos.
"""

import os
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from interfaz.ventana_principal import VentanaPrincipal


@pytest.fixture(scope="session")
def qapp():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_interfaz_completa_modulos_activos(qapp, monkeypatch):
    # Evitar bloqueos de popups modales en entorno headless
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)

    ventana = VentanaPrincipal()
    assert ventana is not None

    # Verificar que los 10 módulos se hayan instanciado correctamente
    assert ventana.modulo_aplicador is not None
    assert ventana.modulo_geometria is not None
    assert ventana.modulo_parametros is not None
    assert ventana.modulo_tejidos is not None
    assert ventana.modulo_simulacion is not None
    assert ventana.modulo_motor is not None
    assert ventana.modulo_resultados is not None
    assert ventana.modulo_comparacion is not None
    assert ventana.modulo_exportacion is not None

    # Simular cambios en parámetros y verificar sincronización
    ventana.modulo_parametros.spin_efd.setValue(0.120)
    ventana.modulo_parametros._guardar_cambios()
    assert ventana.config_global.parametros.efd_nominal_mj_mm2 == 0.120

    # Simular ejecución del motor
    ventana.modulo_motor._ejecutar_verificacion()
    assert ventana.stack.currentIndex() == 7  # Debe navegar a resultados automáticamente
