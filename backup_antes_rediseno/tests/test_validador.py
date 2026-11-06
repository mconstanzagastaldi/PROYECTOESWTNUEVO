"""
Pruebas unitarias para el servicio de validación clínica de parámetros.
"""

from servicios.validador import ValidadorClinico
from modelos.parametros import ParametrosOperativos
from modelos.tejido import CapaTejido
from modelos.configuracion import ConfiguracionGlobal


def test_validador_parametros_nominales_ok():
    p = ParametrosOperativos(efd_nominal_mj_mm2=0.10, frecuencia_repeticion_hz=4.0, profundidad_focal_objetivo_cm=1.0)
    res = ValidadorClinico.validar_parametros_operativos(p)
    assert res.es_valido is True
    assert len(res.errores) == 0
    assert len(res.advertencias) == 0


def test_validador_efd_invalida():
    p = ParametrosOperativos(efd_nominal_mj_mm2=-0.05)
    res = ValidadorClinico.validar_parametros_operativos(p)
    assert res.es_valido is False
    assert len(res.errores) > 0


def test_validador_efd_fuera_de_ventana_advertencia():
    p = ParametrosOperativos(efd_nominal_mj_mm2=0.35)
    res = ValidadorClinico.validar_parametros_operativos(p)
    assert res.es_valido is True
    assert len(res.advertencias) > 0
    assert any("supera el límite superior" in a for a in res.advertencias)


def test_validador_tejidos_vacio():
    res = ValidadorClinico.validar_capas_tejido([])
    assert res.es_valido is False
    assert len(res.errores) > 0


def test_validador_tejidos_espesor_invalido():
    capas = [CapaTejido("Test", espesor_mm=-1.0, densidad_kg_m3=1000, velocidad_m_s=1500, impedancia_rayl=1.5e6, atenuacion_db_cm_mhz=0.5)]
    res = ValidadorClinico.validar_capas_tejido(capas)
    assert res.es_valido is False
    assert any("espesor inválido" in e for e in res.errores)

