"""
Pruebas unitarias para la malla numérica y el motor de simulación.
"""

from modelos.configuracion import ConfiguracionGlobal, ParametrosMallaSimulacion
from simulacion.malla import Malla2D
from simulacion.motor_simulacion import MotorSimulacion


def test_malla_2d_cfl_estable():
    p = ParametrosMallaSimulacion(
        ancho_dominio_cm=2.0,
        profundidad_dominio_cm=2.0,
        resolucion_dx_um=80.0,
        resolucion_dz_um=80.0,
        paso_temporal_dt_ns=8.0
    )
    malla = Malla2D(p)
    assert malla.Nx > 100
    assert malla.Nz > 100
    cfl = malla.calcular_cfl(c_max_m_s=1750.0)
    assert cfl < 1.0
    assert malla.es_estable_cfl(c_max_m_s=1750.0) is True


def test_motor_simulacion_ejecucion():
    cfg = ConfiguracionGlobal()
    motor = MotorSimulacion(cfg)
    res = motor.ejecutar_simulacion()

    assert res is not None
    # Con el solver biofísico integrado, la simulación es convergente y disponible
    assert res.disponible is True
    assert "convergida con éxito" in res.mensaje_estado.lower()
    assert "cfl_calculado" in res.metricas
    assert res.mapa_presion_peak_mpa is not None
    assert res.perfil_axial_profundidad_mpa is not None

