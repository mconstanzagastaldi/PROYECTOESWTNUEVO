"""
Prueba unitaria de la consola electromédica y sus botoneras de hardware.
"""

import os
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from interfaz.consola_eswt import ConsolaESWT


@pytest.fixture(scope="session")
def qapp():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_consola_inicializacion_y_botones(qapp, monkeypatch):
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)

    consola = ConsolaESWT()
    assert consola is not None
    assert "CONSOLA" in consola.windowTitle()

    # Probar ajuste de EFD con botones físicos
    consola._fijar_efd(0.150)
    assert consola.disp_efd.text() == "0.150"
    assert consola.config.parametros.efd_nominal_mj_mm2 == 0.150

    # Probar botón de frecuencia
    consola._fijar_prf(5.0)
    assert consola.disp_prf.text() == "5.0"
    assert consola.config.parametros.frecuencia_repeticion_hz == 5.0

    # Probar selector de superficie y acoplamiento acústico adaptable
    consola._fijar_superficie("Plana")
    assert "Plana" in consola.config.geometria.tipo_superficie
    consola._fijar_acople("Almohadilla")
    assert "Almohadilla" in consola.config.aplicador.sistema_acoplamiento

    # Probar cambio de gráficos (0: pulso, 1: mapa 2D, 2: presión vs prof, 3: esquema, 4: boxplot)
    for i in range(5):
        consola._cambiar_vista_grafica(i)
        assert consola.vista_grafica_actual == i

    # Probar disparo
    consola._ejecutar_disparo_equipo()
    consola._finalizar_disparo()

