"""
Pruebas unitarias para el almacenamiento en disco JSON y exportaciones.
"""

import os
import csv
import tempfile
from modelos.configuracion import ConfiguracionGlobal
from servicios.gestor_configuracion import GestorConfiguracion
from servicios.exportacion import ServicioExportacion
from simulacion.solver_fisico import SolverFisicoESWT


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

        # Verificar contenido sin simulación previa: métricas marcadas como "No calculado"
        with open(ruta_csv, mode="r", encoding="utf-8-sig") as f:
            lector = list(csv.reader(f))
            assert len(lector) > 10
            encabezado = lector[0]
            assert "Parametro" in encabezado and "Valor" in encabezado
            mapa_datos = {fila[0]: fila[1] for fila in lector[1:] if len(fila) >= 2}
            assert mapa_datos["Presión Positiva Máxima P+ (MPa)"] == "No calculado"
            assert mapa_datos["Presión Negativa P- (MPa)"] == "No calculado"
            assert mapa_datos["EFD Total (mJ/mm²)"] == "No calculado"

        ruta_tej = os.path.join(tmpdir, "tejidos.csv")
        ok_t, msg_t = ServicioExportacion.exportar_tejidos_a_csv(cfg, ruta_tej)
        assert ok_t is True
        assert os.path.exists(ruta_tej)


def test_exportar_csv_con_resultados_simulacion():
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_csv = os.path.join(tmpdir, "resumen_con_resultados.csv")
        cfg = ConfiguracionGlobal()
        cfg.parametros.efd_nominal_mj_mm2 = 0.10
        cfg.aplicador.distanciador_seleccionado_mm = 15.0

        # Ejecución real del solver físico
        res = SolverFisicoESWT.simular(cfg)
        assert res.disponible is True

        ok, msg = ServicioExportacion.exportar_resumen_operativo_csv(cfg, ruta_csv, resultados=res)
        assert ok is True
        assert os.path.exists(ruta_csv)

        # Lectura y validación de correspondencia biunívoca con el solver
        with open(ruta_csv, mode="r", encoding="utf-8-sig") as f:
            lector = list(csv.reader(f))
            mapa_datos = {fila[0]: fila[1] for fila in lector[1:] if len(fila) >= 2}

            # Presiones
            p_pos_csv = float(mapa_datos["Presión Positiva Máxima P+ (MPa)"])
            assert abs(p_pos_csv - res.metricas["presion_p_positiva_mpa"]) < 1e-2

            p_neg_csv = float(mapa_datos["Presión Negativa P- (MPa)"])
            assert abs(p_neg_csv - res.metricas["presion_p_negativa_mpa"]) < 1e-2

            # EFDs
            efd_pos_csv = float(mapa_datos["EFD Positiva (mJ/mm²)"])
            assert abs(efd_pos_csv - res.metricas["efd_positiva_mj_mm2"]) < 1e-4

            efd_neg_csv = float(mapa_datos["EFD Negativa (mJ/mm²)"])
            assert abs(efd_neg_csv - res.metricas["efd_negativa_mj_mm2"]) < 1e-4

            efd_tot_csv = float(mapa_datos["EFD Total (mJ/mm²)"])
            assert abs(efd_tot_csv - res.metricas["efd_total_mj_mm2"]) < 1e-4

            # Dermis
            p_dermis_csv = float(mapa_datos["Presión Estimada en Dermis/Cicatriz (MPa)"])
            assert abs(p_dermis_csv - res.metricas["presion_dermis_profunda_mpa"]) < 1e-3

            # Foco y dimensiones
            zf_csv = float(mapa_datos["Profundidad Focal Estimada (mm)"])
            assert abs(zf_csv - res.metricas["profundidad_focal_mm"]) < 1e-2
            assert "3.6 mm x 9.0 mm" in mapa_datos["Dimensiones Zona Focal (-6 dB)"]

            # Térmico e ISPTA
            dt_csv = float(mapa_datos["Incremento Térmico Estimado ΔT (°C)"])
            assert abs(dt_csv - res.metricas["delta_t_absorcion_c"]) < 1e-4

            ispta_csv = float(mapa_datos["Intensidad Acústica ISPTA (W/cm²)"])
            assert abs(ispta_csv - res.metricas["ispta_w_cm2"]) < 1e-4

            # Monte Carlo
            media_mc_csv = float(mapa_datos["Media Monte Carlo P+ (MPa)"])
            assert abs(media_mc_csv - res.metricas["media_p_peak_mpa"]) < 1e-2

            sd_mc_csv = float(mapa_datos["Desviación Estándar Monte Carlo P+ (MPa)"])
            assert abs(sd_mc_csv - res.metricas["sd_p_peak_mpa"]) < 1e-2

            cv_mc_csv = float(mapa_datos["Coeficiente de Variación CV (%)"])
            assert abs(cv_mc_csv - res.metricas["cv_porcentaje"]) < 1e-2

            iter_mc_csv = int(mapa_datos["Iteraciones Monte Carlo"])
            assert iter_mc_csv == 50


def test_generar_reporte_texto_con_y_sin_resultados():
    cfg = ConfiguracionGlobal()
    # Sin resultados
    rep_sin = ServicioExportacion.generar_reporte_texto(cfg)
    assert "No ejecutada en la sesión actual" in rep_sin

    # Con resultados
    res = SolverFisicoESWT.simular(cfg)
    rep_con = ServicioExportacion.generar_reporte_texto(cfg, resultados=res)
    assert "Presión positiva máxima P+:" in rep_con
    assert "Monte Carlo P+" in rep_con


