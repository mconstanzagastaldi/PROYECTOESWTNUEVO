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
from typing import Tuple
from modelos.configuracion import ConfiguracionGlobal


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
    def exportar_resumen_operativo_csv(config: ConfiguracionGlobal, ruta_csv: str) -> Tuple[bool, str]:
        """Exporta los parámetros de funcionamiento y dosimetría a CSV estándar."""
        try:
            with open(ruta_csv, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Parametro", "Valor"])
                filas = [
                    ("Configuración", config.nombre_configuracion),
                    ("Tipo de Generación", config.aplicador.tipo_generacion),
                    ("Geometría Cabezal", config.aplicador.cabezal.tipo_geometria),
                    ("Ángulo Orientación (°)", config.aplicador.cabezal.angulo_orientacion_deg),
                    ("Superficie Anatómica", config.geometria.tipo_superficie),
                    ("EFD Nominal (mJ/mm²)", config.parametros.efd_nominal_mj_mm2),
                    ("Frecuencia PRF (Hz)", config.parametros.frecuencia_repeticion_hz),
                    ("Profundidad Focal Objetivo (cm)", config.parametros.profundidad_focal_objetivo_cm),
                    ("Densidad de Disparos (pulsos/cm²)", config.parametros.densidad_disparos_pcm2),
                    ("Área de Tratamiento (cm²)", config.parametros.area_tratamiento_cm2),
                    ("Pulsos Totales Programados", config.parametros.numero_pulsos_total),
                    ("Tiempo de Sesión (min)", round(config.parametros.tiempo_tratamiento_minutos, 2))
                ]
                for p, v in filas:
                    writer.writerow([p, v])
            return True, f"Resumen operativo exportado exitosamente a:\n{ruta_csv}"
        except Exception as e:
            return False, f"Error al exportar parámetros a CSV: {str(e)}"

    @staticmethod
    def generar_reporte_texto(config: ConfiguracionGlobal) -> str:
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

        lineas.extend([
            "-" * 95,
            "",
            "5. ESTADO DEL MOTOR COMPUTACIONAL:",
            " - Arquitectura: Modular desacoplada.",
            " - Modelo físico definitivo: Pendiente de formulación física del casquete y componentes piezoeléctricos.",
            "=" * 78
        ])

        return "\n".join(lineas)
