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


def test_consola_distanciadores_secuencia(qapp, monkeypatch):
    """Verifica la conmutación repetida de distanciadores sin reinicios ni valor cero (Error 4.1)."""
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    consola = ConsolaESWT()

    # Secuencia crítica de conmutación: D20 (1.0cm) -> D15 (1.5cm) -> D20 -> D10 -> D25 -> D15
    secuencia = [
        (1.0, 20.0, "D20"),
        (1.5, 15.0, "D15"),
        (1.0, 20.0, "D20"),
        (2.0, 10.0, "D10"),
        (0.5, 25.0, "D25"),
        (1.5, 15.0, "D15")
    ]

    for foco_esperado, dist_esperado, etiqueta in secuencia:
        consola._fijar_foco(foco_esperado)
        assert consola._foco_cm == foco_esperado
        assert consola.config.parametros.profundidad_focal_objetivo_cm == foco_esperado
        assert consola.config.aplicador.distanciador_seleccionado_mm == dist_esperado
        assert etiqueta in consola.disp_foco.text()
        assert "0.0 cm" not in consola.disp_foco.text()
        # Comprobar que el solver biofísico calcula foco > 0
        res = consola._ultimo_resultado
        assert res.metricas["profundidad_focal_cm"] == foco_esperado
        assert res.metricas["espesor_distanciador_mm"] == dist_esperado


def test_consola_dosificacion_y_disparos(qapp, monkeypatch):
    """Verifica que la densidad (p/cm²) y disparos totales se distingan y sincronicen correctamente (Errores 4.2 y 4.3)."""
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    consola = ConsolaESWT()

    # Modificaciones sucesivas de dosificación dentro del rango 10 - 500 p/cm²
    for dens in [50.0, 100.0, 150.0, 250.0, 500.0]:
        consola._fijar_densidad_pulsos(dens)
        assert consola.config.parametros.densidad_disparos_pcm2 == dens
        assert f"{int(dens)}" in consola.disp_densidad.text()
        # Verificar relación física con área de 10 cm² por defecto
        total_esperado = int(dens * consola._area_cm2)
        assert consola.disp_disparos.text().replace(".", "") == str(total_esperado)

    # Modificación de área y recálculo de duración de emisión
    consola._fijar_prf(4.0)
    consola._fijar_densidad_pulsos(150.0)
    consola._fijar_area(20.0)
    assert consola._area_cm2 == 20.0
    # Total = 150 p/cm² * 20 cm² = 3000 pulsos
    total_esperado = 3000
    duracion_min_esperada = (total_esperado / 4.0) / 60.0 # 12.5 min
    assert consola.disp_disparos.text().replace(".", "") == "3000"
    assert "12.50 min" in consola.lbl_info_sesion.text()

    # Ajuste directo de disparos totales
    consola._fijar_disparos_totales(1000)
    assert consola.disp_disparos.text().replace(".", "") == "1000"
    # Densidad recalculada = 1000 / 20 = 50 p/cm²
    assert consola.config.parametros.densidad_disparos_pcm2 == 50.0


def test_consola_interaccion_completa_sin_bloqueos(qapp, monkeypatch):
    """Verifica que todos los botones de presets y ajustes interactúen sucesivamente sin bloqueos."""
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    consola = ConsolaESWT()

    # 1. Probar cada uno de los 5 presets de EFD
    for preset in [0.05, 0.08, 0.10, 0.15, 0.20]:
        btn = consola._botones_efd_map[preset]
        btn.click()
        assert abs(consola._efd - preset) < 1e-4
        assert f"{preset:.2f}" in consola.disp_efd.text() or f"{preset:.3f}" in consola.disp_efd.text()

    # 2. Modificaciones sucesivas de EFD con incremento/decremento
    btns = consola.disp_efd.parent().findChildren(consola._botones_efd_map[0.10].__class__)
    btn_plus = [b for b in btns if "+0.01" in b.text()][0]
    btn_minus = [b for b in btns if "-0.01" in b.text()][0]
    btn_plus.click()
    assert abs(consola._efd - 0.21) < 1e-4
    btn_minus.click()
    assert abs(consola._efd - 0.20) < 1e-4

    # 3. Cambios sucesivos de profundidad focal y distanciador
    for fc in [0.5, 1.0, 1.5, 2.0, 1.0, 0.5]:
        btn = consola._botones_foco_map[fc]
        btn.click()
        assert abs(consola._foco_cm - fc) < 1e-3
        dist_esp = max(10.0, min(25.0, 30.0 - fc * 10.0))
        assert abs(consola.config.aplicador.distanciador_seleccionado_mm - dist_esp) < 1e-3

    # 4. Modificaciones de dosificación y área
    for dens in [50, 100, 150, 250, 500]:
        consola._botones_dens_map[dens].click()
        assert abs(consola.config.parametros.densidad_disparos_pcm2 - dens) < 1e-3

    for a in [5, 10, 15, 20]:
        consola._botones_area_map[a].click()
        assert abs(consola._area_cm2 - a) < 1e-3

    # 5. Combinación múltiple y verificación de resultados del solver
    consola._botones_efd_map[0.15].click()
    consola._botones_foco_map[1.5].click()
    consola._botones_dens_map[250].click()
    consola._botones_area_map[15].click()

    res = consola._ultimo_resultado
    assert abs(res.metricas["efd_positiva_mj_mm2"] - 0.15) < 1e-4
    assert abs(res.metricas["presion_p_positiva_mpa"] - 92.86) < 0.1
    assert abs(res.metricas["profundidad_focal_cm"] - 1.5) < 1e-3



