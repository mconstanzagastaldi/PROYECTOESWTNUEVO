"""
Pruebas unitarias para los modelos de datos del simulador ESWT.
"""

from modelos.cabezal import ConfiguracionCabezal
from modelos.aplicador import ConfiguracionAplicador
from modelos.geometria import ConfiguracionGeometria
from modelos.tejido import CapaTejido, obtener_capas_predeterminadas_literatura
from modelos.parametros import ParametrosOperativos
from modelos.configuracion import ConfiguracionGlobal, ParametrosMallaSimulacion


def test_modelo_cabezal_por_defecto():
    cab = ConfiguracionCabezal()
    assert cab.tipo_geometria == "Cóncavo"
    assert cab.orientacion_fija_normal is True
    assert cab.angulo_orientacion_deg == 0.0
    d = cab.to_dict()
    cab_rec = ConfiguracionCabezal.from_dict(d)
    assert cab_rec.tipo_geometria == cab.tipo_geometria


def test_modelo_aplicador_serializacion():
    app = ConfiguracionAplicador()
    assert app.tipo_generacion == "Piezoeléctrica"
    assert app.cabezal.tipo_geometria == "Cóncavo"
    d = app.to_dict()
    app_rec = ConfiguracionAplicador.from_dict(d)
    assert app_rec.tipo_generacion == "Piezoeléctrica"


def test_modelo_parametros_calculos():
    p = ParametrosOperativos(
        efd_nominal_mj_mm2=0.10,
        frecuencia_repeticion_hz=4.0,
        densidad_disparos_pcm2=150.0,
        area_tratamiento_cm2=10.0
    )
    assert p.numero_pulsos_total == 1500
    assert abs(p.tiempo_tratamiento_minutos - 6.25) < 1e-3


def test_modelo_capas_tejidos_literatura():
    capas = obtener_capas_predeterminadas_literatura()
    assert len(capas) == 4
    # Verificar nombres clave
    nombres = [c.nombre for c in capas]
    assert any("Gel" in n for n in nombres)
    assert any("Piel" in n for n in nombres)
    assert any("Cicatriz" in n for n in nombres)
    assert any("Subcutáneo" in n for n in nombres)

    # Verificar que Z = rho * c se calcule coherentemente
    for c in capas:
        z_calc = c.densidad_kg_m3 * c.velocidad_m_s
        assert abs(c.impedancia_rayl - z_calc) < 1e-1


def test_configuracion_global_serializacion():
    cfg = ConfiguracionGlobal()
    d = cfg.to_dict()
    assert "aplicador" in d
    assert "geometria" in d
    assert "parametros" in d
    assert "tejidos" in d
    assert "malla" in d

    cfg_rec = ConfiguracionGlobal.from_dict(d)
    assert cfg_rec.nombre_configuracion == cfg.nombre_configuracion
    assert len(cfg_rec.tejidos) == len(cfg.tejidos)

