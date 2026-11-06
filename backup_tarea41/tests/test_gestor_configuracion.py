"""
Pruebas unitarias para el almacenamiento en disco JSON y exportaciones.
"""

import os
import tempfile
from modelos.configuracion import ConfiguracionGlobal
from servicios.gestor_configuracion import GestorConfiguracion
from servicios.exportacion import ServicioExportacion


def test_guardar_y_cargar_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "test_config.json")
        cfg_original = ConfiguracionGlobal(nombre_configuracion="Test_Session")
        cfg_original.parametros.efd_nominal_mj_mm2 = 0.125

        ok, msg = GestorConfiguracion.guardar_archivo(cfg_original, ruta)
        assert ok is True
        assert os.path.exists(ruta)

        cfg_cargada, val, msg_load = GestorConfiguracion.cargar_archivo(ruta)
        assert cfg_cargada is not None
        assert val.es_valido is True
        assert cfg_cargada.nombre_configuracion == "Test_Session"
        assert abs(cfg_cargada.parametros.efd_nominal_mj_mm2 - 0.125) < 1e-4


def test_exportar_csv():
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_csv = os.path.join(tmpdir, "resumen.csv")
        cfg = ConfiguracionGlobal()

        ok, msg = ServicioExportacion.exportar_resumen_operativo_csv(cfg, ruta_csv)
        assert ok is True
        assert os.path.exists(ruta_csv)

        ruta_tej = os.path.join(tmpdir, "tejidos.csv")
        ok_t, msg_t = ServicioExportacion.exportar_tejidos_a_csv(cfg, ruta_tej)
        assert ok_t is True
        assert os.path.exists(ruta_tej)

