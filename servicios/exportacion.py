"""
================================================================================
SERVICIO DE EXPORTACIÓN Y GENERACIÓN DE REPORTES (CSV / TEXTO)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Permite exportar datos tabulares (tejidos, parámetros y dosimetría) a archivos CSV
mediante la biblioteca estándar y generar informes legibles del experimento.
================================================================================
"""

import os
import csv
from typing import Tuple, Optional
from modelos.configuracion import ConfiguracionGlobal
from modelos.resultados import ResultadosSimulacion


class ServicioExportacion:
    """Exporta las configuraciones y parámetros a formatos tabulares y legibles."""

    @staticmethod
    def exportar_tejidos_a_csv(config: ConfiguracionGlobal, ruta_csv: str) -> Tuple[bool, str]:
        """Exporta la estratificación tisular a formato CSV estándar."""
        try:
            with open(ruta_csv, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Estrato",
                    "Espesor_mm",
                    "Densidad_kg_m3",
                    "Velocidad_Sonido_m_s",
                    "Impedancia_Rayl",
                    "Atenuacion_dB_cm_MHz"
                ])
                for c in config.tejidos:
                    writer.writerow([
                        c.nombre,
                        c.espesor_mm,
                        c.densidad_kg_m3,
                        c.velocidad_m_s,
                        c.impedancia_rayl,
                        c.atenuacion_db_cm_mhz
                    ])
            return True, f"Estratos tisulares exportados exitosamente a:\n{ruta_csv}"
        except Exception as e:
            return False, f"Error al exportar capas tisulares a CSV: {str(e)}"

    @staticmethod
    def exportar_barrido_geometrico_csv(ruta_csv: str) -> Tuple[bool, str]:
        """Exporta los resultados del barrido paramétrico de casquetes a formato CSV (Tarea 4.1)."""
        try:
            from fisica.barrido_geometrico import EvaluadorGeometriaESWT
            resultados = EvaluadorGeometriaESWT.ejecutar_barrido_completo()
            with open(ruta_csv, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Apertura_mm",
                    "Radio_Curvatura_mm",
                    "F_number",
                    "Factible",
                    "Pmax_Tejido_MPa",
                    "Z_Foco_Tejido_mm",
                    "Longitud_Focal_mm",
                    "Cumple_Rango_5_20mm"
                ])
                for r in resultados:
                    if r.get("valida", False):
                        writer.writerow([
                            r["apertura_mm"],
                            r["radio_curvatura_mm"],
                            f"{r['f_number']:.2f}",
                            "SI",
                            f"{r['p_max_tejido_mpa']:.2f}",
                            f"{r['z_pico_simulado_tejido_mm']:.2f}",
                            f"{r['longitud_focal_axial_mm']:.2f}",
                            "SI" if r["cumple_rango_terapeutico_5_20mm"] else "NO"
                        ])
                    else:
                        writer.writerow([
                            r.get("apertura_mm", ""),
                            r.get("radio_curvatura_mm", ""),
                            "-",
                            "NO (Incompatible)",
                            "-",
                            "-",
                            "-",
                            "NO"
                        ])
            return True, f"Barrido paramétrico exportado exitosamente a:\n{ruta_csv}"
        except Exception as e:
            return False, f"Error al exportar barrido paramétrico a CSV: {str(e)}"

    @staticmethod
    def exportar_resumen_operativo_csv(
        config: ConfiguracionGlobal,
        ruta_csv: str,
        resultados: Optional[ResultadosSimulacion] = None
    ) -> Tuple[bool, str]:
        """Exporta los parámetros de configuración y los resultados numéricos de la simulación a CSV estándar."""
        try:
            with open(ruta_csv, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Parametro", "Valor", "Unidad", "Categoria"])

                # 1. Parámetros de Configuración del Tratamiento
                filas_config = [
                    ("Configuración", config.nombre_configuracion, "-", "Configuración General"),
                    ("Tipo de Generación", config.aplicador.tipo_generacion, "-", "Aplicador"),
                    ("Geometría Cabezal", config.aplicador.cabezal.tipo_geometria, "-", "Aplicador"),
                    ("Distanciador en Uso", f"D{getattr(config.aplicador, 'distanciador_seleccionado_mm', 15.0):.0f} ({getattr(config.aplicador, 'distanciador_seleccionado_mm', 15.0):.1f} mm)", "mm", "Aplicador"),
                    ("Ángulo Orientación (°)", config.aplicador.cabezal.angulo_orientacion_deg, "°", "Aplicador"),
                    ("Superficie Anatómica", config.geometria.tipo_superficie, "-", "Geometría del Paciente"),
                    ("EFD Nominal (mJ/mm²)", config.parametros.efd_nominal_mj_mm2, "mJ/mm²", "Dosimetría"),
                    ("Frecuencia PRF (Hz)", config.parametros.frecuencia_repeticion_hz, "Hz", "Dosimetría"),
                    ("Profundidad Focal Objetivo (cm)", config.parametros.profundidad_focal_objetivo_cm, "cm", "Dosimetría"),
                    ("Densidad de Disparos (pulsos/cm²)", config.parametros.densidad_disparos_pcm2, "pulsos/cm²", "Dosimetría"),
                    ("Área de Tratamiento (cm²)", config.parametros.area_tratamiento_cm2, "cm²", "Dosimetría"),
                    ("Pulsos Totales Programados", config.parametros.numero_pulsos_total, "pulsos", "Dosimetría"),
                    ("Tiempo de Sesión (min)", round(config.parametros.tiempo_tratamiento_minutos, 2), "min", "Dosimetría")
                ]

                # 2. Resultados Numéricos de la Simulación Física
                sim_disponible = resultados is not None and getattr(resultados, "disponible", False)
                m = resultados.metricas if (sim_disponible and hasattr(resultados, "metricas")) else {}

                if sim_disponible:
                    p_pos = m.get("presion_p_positiva_mpa", "N/D")
                    p_neg = m.get("presion_p_negativa_mpa", "N/D")
                    efd_pos = m.get("efd_positiva_mj_mm2", m.get("efd_calculada_mj_mm2", "N/D"))
                    efd_neg = m.get("efd_negativa_mj_mm2", "N/D")
                    efd_tot = m.get("efd_total_mj_mm2", "N/D")
                    p_dermis = m.get("presion_dermis_profunda_mpa", "N/D")

                    zf_mm = m.get("profundidad_focal_mm")
                    if zf_mm is None and "profundidad_focal_cm" in m:
                        zf_mm = round(m["profundidad_focal_cm"] * 10.0, 2)
                    zf_mm_str = zf_mm if zf_mm is not None else "N/D"

                    ancho_focal = m.get("ancho_focal_menos_6db_mm", 3.6)
                    long_focal = m.get("longitud_focal_menos_6db_mm", 9.0)
                    dim_focal = m.get("dimensiones_zona_focal_mm", f"{ancho_focal:.1f} mm x {long_focal:.1f} mm (-6 dB)")

                    delta_t = m.get("delta_t_absorcion_c", "N/D")
                    ispta = m.get("ispta_w_cm2", "N/D")
                    media_p = m.get("media_p_peak_mpa", "N/D")
                    sd_p = m.get("sd_p_peak_mpa", "N/D")
                    cv_pct = m.get("cv_porcentaje", "N/D")

                    n_mc = m.get("iteraciones_monte_carlo")
                    if n_mc is None and hasattr(resultados, "muestras_p_peak_iteraciones") and resultados.muestras_p_peak_iteraciones is not None:
                        n_mc = len(resultados.muestras_p_peak_iteraciones)
                    if n_mc is None:
                        n_mc = 50

                    filas_res = [
                        ("Presión Positiva Máxima P+ (MPa)", p_pos, "MPa", "Resultados de Simulación"),
                        ("Presión Negativa P- (MPa)", p_neg, "MPa", "Resultados de Simulación"),
                        ("EFD Positiva (mJ/mm²)", efd_pos, "mJ/mm²", "Resultados de Simulación"),
                        ("EFD Negativa (mJ/mm²)", efd_neg, "mJ/mm²", "Resultados de Simulación"),
                        ("EFD Total (mJ/mm²)", efd_tot, "mJ/mm²", "Resultados de Simulación"),
                        ("Presión Estimada en Dermis/Cicatriz (MPa)", p_dermis, "MPa", "Resultados de Simulación"),
                        ("Profundidad Focal Estimada (mm)", zf_mm_str, "mm", "Resultados de Simulación"),
                        ("Dimensiones Zona Focal (-6 dB)", dim_focal, "mm", "Resultados de Simulación"),
                        ("Ancho Focal Lateral (-6 dB)", ancho_focal, "mm", "Resultados de Simulación"),
                        ("Longitud Focal Axial (-6 dB)", long_focal, "mm", "Resultados de Simulación"),
                        ("Incremento Térmico Estimado ΔT (°C)", delta_t, "°C", "Resultados de Simulación"),
                        ("Intensidad Acústica ISPTA (W/cm²)", ispta, "W/cm²", "Resultados de Simulación"),
                        ("Media Monte Carlo P+ (MPa)", media_p, "MPa", "Resultados de Simulación"),
                        ("Desviación Estándar Monte Carlo P+ (MPa)", sd_p, "MPa", "Resultados de Simulación"),
                        ("Coeficiente de Variación CV (%)", cv_pct, "%", "Resultados de Simulación"),
                        ("Iteraciones Monte Carlo", n_mc, "iteraciones", "Resultados de Simulación")
                    ]
                else:
                    filas_res = [
                        ("Presión Positiva Máxima P+ (MPa)", "No calculado", "MPa", "Resultados de Simulación"),
                        ("Presión Negativa P- (MPa)", "No calculado", "MPa", "Resultados de Simulación"),
                        ("EFD Positiva (mJ/mm²)", "No calculado", "mJ/mm²", "Resultados de Simulación"),
                        ("EFD Negativa (mJ/mm²)", "No calculado", "mJ/mm²", "Resultados de Simulación"),
                        ("EFD Total (mJ/mm²)", "No calculado", "mJ/mm²", "Resultados de Simulación"),
                        ("Presión Estimada en Dermis/Cicatriz (MPa)", "No calculado", "MPa", "Resultados de Simulación"),
                        ("Profundidad Focal Estimada (mm)", "No calculado", "mm", "Resultados de Simulación"),
                        ("Dimensiones Zona Focal (-6 dB)", "No calculado", "mm", "Resultados de Simulación"),
                        ("Ancho Focal Lateral (-6 dB)", "No calculado", "mm", "Resultados de Simulación"),
                        ("Longitud Focal Axial (-6 dB)", "No calculado", "mm", "Resultados de Simulación"),
                        ("Incremento Térmico Estimado ΔT (°C)", "No calculado", "°C", "Resultados de Simulación"),
                        ("Intensidad Acústica ISPTA (W/cm²)", "No calculado", "W/cm²", "Resultados de Simulación"),
                        ("Media Monte Carlo P+ (MPa)", "No calculado", "MPa", "Resultados de Simulación"),
                        ("Desviación Estándar Monte Carlo P+ (MPa)", "No calculado", "MPa", "Resultados de Simulación"),
                        ("Coeficiente de Variación CV (%)", "No calculado", "%", "Resultados de Simulación"),
                        ("Iteraciones Monte Carlo", "No calculado", "iteraciones", "Resultados de Simulación")
                    ]

                for p, v, u, cat in (filas_config + filas_res):
                    writer.writerow([p, v, u, cat])

            return True, f"Resumen operativo y resultados exportados exitosamente a:\n{ruta_csv}"
        except Exception as e:
            return False, f"Error al exportar parámetros y resultados a CSV: {str(e)}"

    @staticmethod
    def generar_reporte_texto(config: ConfiguracionGlobal, resultados: Optional[ResultadosSimulacion] = None) -> str:
        """Genera un reporte técnico estructurado en texto plano."""
        p = config.parametros
        a = config.aplicador
        g = config.geometria

        lineas = [
            "=" * 78,
            "SIMULADOR ESWT - REPORTE DE CONFIGURACIÓN DEL APLICADOR Y DOSIMETRÍA",
            "Proyecto de Bioingeniería - Universidad Nacional de Entre Ríos (UNER)",
            "=" * 78,
            f"Configuración:          {config.nombre_configuracion}",
            f"Fecha de Registro:      {config.fecha_creacion}",
            "",
            "1. ESPECIFICACIONES DEL APLICADOR:",
            f" - Tipo de Generación:   {a.tipo_generacion}",
            f" - Geometría Cabezal:    {a.cabezal.tipo_geometria}",
            f" - Modo de Emisión:      Normal Fija (0.0° - Sin ángulo de inclinación)",
            f" - Radio Curvatura (R):  {a.cabezal.radio_curvatura_mm:.1f} mm (Geometría Seleccionada Tarea 4.1)",
            f" - Diámetro Apertura (2a):{a.cabezal.apertura_diametro_mm:.1f} mm (F-number = {a.cabezal.radio_curvatura_mm/a.cabezal.apertura_diametro_mm:.2f})",
            f" - Distanciador en uso:  D{getattr(a, 'distanciador_seleccionado_mm', 15.0):.0f} ({getattr(a, 'distanciador_seleccionado_mm', 15.0):.1f} mm)",
            f" - Chasis Ergonómico:    Ø {a.cabezal.diametro_exterior_chasis_mm:.1f} mm (≤ 40 mm, Wand)",
            f" - Acoplamiento:         {a.sistema_acoplamiento} (Espesor: {a.espesor_gel_mm:.1f} mm)",
            "",
            "2. GEOMETRÍA ANATÓMICA Y ADAPTABILIDAD:",
            f" - Tipo de Superficie:   {g.tipo_superficie}",
            f" - Contacto Asegurado:   {g.contacto_acustico_garantizado}",
            f" - Profundidad Análisis: {g.profundidad_analisis_cm:.2f} cm",
            f" - Ancho Lateral:        {g.ancho_lateral_cm:.2f} cm",
            "",
            "3. PARÁMETROS OPERATIVOS Y DOSIMETRÍA:",
            f" - EFD Nominal:          {p.efd_nominal_mj_mm2:.3f} mJ/mm² (Rango: 0.03 a 0.25)",
            f" - Frecuencia PRF:       {p.frecuencia_repeticion_hz:.1f} Hz (Rango: 4.0 a 5.0)",
            f" - Foco Objetivo:        {p.profundidad_focal_objetivo_cm:.2f} cm (Rango: 0.5 a 2.0)",
            f" - Disparos / cm²:       {p.densidad_disparos_pcm2:.0f} pulsos/cm²",
            f" - Área Lesión:          {p.area_tratamiento_cm2:.1f} cm²",
            f" - Total Disparos:       {p.numero_pulsos_total} pulsos",
            f" - Duración Estimada:    {p.tiempo_tratamiento_minutos:.2f} minutos",
            "",
            "4. ESTRATIFICACIÓN TISULAR:",
            f"{'Estrato':<28} {'Espesor [mm]':<14} {'Densidad [kg/m³]':<18} {'Velocidad [m/s]':<16} {'Atenuación [dB/cm·MHz]'}",
            "-" * 95
        ]

        for c in config.tejidos:
            lineas.append(
                f"{c.nombre:<28} {c.espesor_mm:<14.1f} {c.densidad_kg_m3:<18.0f} {c.velocidad_m_s:<16.0f} {c.atenuacion_db_cm_mhz:.3f}"
            )

        lineas.append("-" * 95)

        if resultados is not None and getattr(resultados, "disponible", False):
            m = resultados.metricas
            lineas.extend([
                "",
                "5. RESULTADOS DE LA ÚLTIMA SIMULACIÓN BIOACÚSTICA:",
                f" - Presión positiva máxima P+:  {m.get('presion_p_positiva_mpa', 'N/D')} MPa",
                f" - Presión negativa P-:         {m.get('presion_p_negativa_mpa', 'N/D')} MPa",
                f" - EFD positiva / total:        {m.get('efd_positiva_mj_mm2', 'N/D')} / {m.get('efd_total_mj_mm2', 'N/D')} mJ/mm²",
                f" - Presión en dermis (1.8 cm):  {m.get('presion_dermis_profunda_mpa', 'N/D')} MPa",
                f" - Profundidad focal estimada:  {m.get('profundidad_focal_mm', 'N/D')} mm",
                f" - Zona focal (-6 dB):          {m.get('dimensiones_zona_focal_mm', '3.6 mm x 9.0 mm (-6 dB)')}",
                f" - Incremento térmico ΔT:       {m.get('delta_t_absorcion_c', 'N/D')} °C",
                f" - Intensidad ISPTA:            {m.get('ispta_w_cm2', 'N/D')} W/cm²",
                f" - Monte Carlo P+ (media ± sd): {m.get('media_p_peak_mpa', 'N/D')} ± {m.get('sd_p_peak_mpa', 'N/D')} MPa (CV = {m.get('cv_porcentaje', 'N/D')}%, n={m.get('iteraciones_monte_carlo', 50)})",
                "",
                "6. ESTADO DEL MOTOR COMPUTACIONAL:",
                " - Solver: Modelo acústico analítico-computacional de focalización y atenuación multicapa.",
                "=" * 78
            ])
        else:
            lineas.extend([
                "",
                "5. RESULTADOS DE SIMULACIÓN:",
                " - Estado: No ejecutada en la sesión actual.",
                "",
                "6. ESTADO DEL MOTOR COMPUTACIONAL:",
                " - Solver: Modelo acústico analítico-computacional de focalización y atenuación multicapa.",
                "=" * 78
            ])

        return "\n".join(lineas)
