"""
Pruebas automáticas de verificación bioacústica y física del modelo ESWT (Tarea 4.1).
Valida las integrales temporales de EFD, la relación EFD-presión, el desplazamiento
focal por distanciadores, la atenuación tisular y la formulación térmica de Nyborg.
"""

import numpy as np
import pytest
from modelos.configuracion import ConfiguracionGlobal
from simulacion.solver_fisico import SolverFisicoESWT
from fisica.barrido_geometrico import EvaluadorGeometriaESWT


def test_integrales_temporales_analiticas():
    """Comprueba las integrales temporales analíticas de cada tramo de la forma de onda."""
    t_rise = 8e-9
    t_cero = 75e-9
    t_total = 300e-9
    P_neg = -10e6
    Z = 1050.0 * 1540.0 # 1.617e6 Rayl

    # Tramo 1 y 2 (Fase positiva): factor = 3/8 * t_cero
    I_pos_factor = (3.0 / 8.0) * t_cero
    assert abs(I_pos_factor - 2.8125e-8) < 1e-12

    # Tramo 3 (Fase negativa): factor = 0.5 * (t_total - t_cero)
    I_neg_factor = 0.5 * (t_total - t_cero)
    assert abs(I_neg_factor - 1.125e-7) < 1e-12

    # Energía de la fase negativa fija: EFD_neg = I_neg / Z
    efd_neg_J_m2 = (P_neg**2 * I_neg_factor) / Z
    efd_neg_mJ_mm2 = efd_neg_J_m2 * 1e-3
    assert abs(efd_neg_mJ_mm2 - 0.006957) < 1e-5


def test_relacion_efd_presion_positiva():
    """Comprueba la derivación de P+ a partir de EFD_pos sin recortes artificiales."""
    Z = 1050.0 * 1540.0
    I_pos_factor = 2.8125e-8

    # Para EFD = 0.10 mJ/mm² = 100 J/m²
    p_pos_calculado = np.sqrt(100.0 * Z / I_pos_factor) * 1e-6
    assert abs(p_pos_calculado - 75.82) < 0.05

    # En el solver para 0.03 y 0.25 mJ/mm²
    cfg = ConfiguracionGlobal()
    cfg.parametros.efd_nominal_mj_mm2 = 0.03
    r_min = SolverFisicoESWT.simular(cfg)
    assert abs(r_min.metricas["presion_p_positiva_mpa"] - 41.53) < 0.1

    cfg.parametros.efd_nominal_mj_mm2 = 0.25
    r_max = SolverFisicoESWT.simular(cfg)
    assert abs(r_max.metricas["presion_p_positiva_mpa"] - 119.88) < 0.1


def test_desplazamiento_focal_distanciadores():
    """Verifica que los distanciadores desplacen el foco con consistencia física."""
    cfg = ConfiguracionGlobal()
    cfg.aplicador.distanciador_seleccionado_mm = 10.0
    r10 = SolverFisicoESWT.simular(cfg)

    cfg.aplicador.distanciador_seleccionado_mm = 20.0
    r20 = SolverFisicoESWT.simular(cfg)

    # D10 focaliza más profundo (20 mm) que D20 (10 mm)
    assert r10.metricas["profundidad_focal_cm"] == 2.0
    assert r20.metricas["profundidad_focal_cm"] == 1.0
    assert r10.perfil_axial_profundidad_mpa.argmax() > r20.perfil_axial_profundidad_mpa.argmax()


def test_sensibilidad_atenuacion_tisular():
    """Verifica que un aumento en el coeficiente de atenuación reduzca la presión propagada."""
    cfg = ConfiguracionGlobal()
    cfg.aplicador.distanciador_seleccionado_mm = 15.0
    r_base = SolverFisicoESWT.simular(cfg)

    for t in cfg.tejidos:
        if "cicatriz" in t.nombre.lower():
            t.atenuacion_db_cm_mhz = 3.5
    r_atenuado = SolverFisicoESWT.simular(cfg)

    assert r_atenuado.metricas["presion_dermis_profunda_mpa"] < r_base.metricas["presion_dermis_profunda_mpa"]


def test_estimacion_termica_nyborg():
    """Verifica el cálculo analítico de absorción térmica con energía total (Nyborg 1988, NCRP 113)."""
    cfg = ConfiguracionGlobal()
    cfg.parametros.efd_nominal_mj_mm2 = 0.10
    cfg.parametros.frecuencia_repeticion_hz = 4.0
    res = SolverFisicoESWT.simular(cfg)

    # EFD_total = EFD_pos + EFD_neg = 0.10 + 0.00696 mJ/mm² = 0.10696 mJ/mm²
    efd_total = 0.10 + 0.00696
    # alpha cicatriz = 2.1 dB/cm·MHz -> 24.18 Np/m
    alpha_np = (2.1 * 100.0) / 8.686
    i_spta_total = (efd_total * 1000.0) * 4.0 # W/m²
    w_foco = 1.8e-3 # m
    kappa = 0.51 # W/(m·K)
    dt_esperado = (alpha_np * i_spta_total * (w_foco**2)) / (2.0 * kappa)

    assert abs(res.metricas["delta_t_absorcion_c"] - dt_esperado) < 1e-4


def test_energia_ambas_fases_en_calculo_termico():
    """Verifica que la energía de ambas fases (compresión y tracción) se considere en la dosimetría térmica."""
    cfg = ConfiguracionGlobal()
    cfg.parametros.efd_nominal_mj_mm2 = 0.10
    res = SolverFisicoESWT.simular(cfg)

    assert res.metricas["efd_positiva_mj_mm2"] == 0.10
    assert abs(res.metricas["efd_negativa_mj_mm2"] - 0.00696) < 1e-5
    assert abs(res.metricas["efd_total_mj_mm2"] - 0.10696) < 1e-5
    # La intensidad total debe ser mayor que la puramente positiva
    i_pos = (0.10 * 1000.0 * 4.0) / 10000.0
    assert res.metricas["ispta_w_cm2"] > i_pos


