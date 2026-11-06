"""
================================================================================
MODELO DE DATOS: RESULTADOS DE SIMULACIÓN ACÚSTICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Estructura unificada de resultados del Prototipado Virtual y Simulación:
- Matrices de campo acústico 2D y perfiles axiales calculados por el solver numérico.
- Métricas dosimétricas: EFD, P+, P-, mecanotransducción, VEGF.
- Estadísticas del bucle iterativo (n=50): Media, Desvío Estándar (SD),
  Coeficiente de Variación (CV < 5%) y distribución para Boxplot.
================================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class ResultadosSimulacion:
    """Contenedor de resultados numéricos, dosimétricos y de validación estadística."""
    disponible: bool = False
    mensaje_estado: str = "Simulación pendiente de ejecución."

    # Ejes de coordenadas físicas [cm y mm]
    eje_x_cm: Optional[np.ndarray] = None
    eje_z_cm: Optional[np.ndarray] = None

    # Matrices de presión acústica [MPa] y densidad de flujo de energía [mJ/mm²]
    mapa_presion_peak_mpa: Optional[np.ndarray] = None
    perfil_axial_profundidad_mpa: Optional[np.ndarray] = None
    perfil_radial_focal_mpa: Optional[np.ndarray] = None

    # Señal temporal del pulso focal
    eje_tiempo_ns: Optional[np.ndarray] = None
    senal_pulso_fuente_mpa: Optional[np.ndarray] = None

    # Muestras de iteraciones Monte Carlo / análisis de sensibilidad (n=50)
    muestras_p_peak_iteraciones: Optional[np.ndarray] = None
    muestras_efd_iteraciones: Optional[np.ndarray] = None

    # Métricas dosimétricas y de validación técnica
    metricas: Dict[str, Any] = field(default_factory=lambda: {
        "efd_calculada_mj_mm2": 0.0,
        "efd_positiva_mj_mm2": 0.0,
        "efd_negativa_mj_mm2": 0.0,
        "efd_total_mj_mm2": 0.0,
        "presion_p_positiva_mpa": 0.0,
        "presion_p_negativa_mpa": 0.0,
        "presion_dermis_profunda_mpa": 0.0,
        "profundidad_focal_cm": 0.0,
        "profundidad_focal_mm": 0.0,
        "espesor_distanciador_mm": 0.0,
        "ancho_focal_menos_6db_mm": 0.0,
        "longitud_focal_menos_6db_mm": 0.0,
        "dimensiones_zona_focal_mm": "",
        "energia_total_joules": 0.0,
        "ispta_w_cm2": 0.0,
        "delta_t_absorcion_c": 0.0,
        "criterio_foco_conforme": True,
        "criterio_bioseguridad_cavitacion_cumplido": True,
        "criterio_seguridad_termica_cumplido": True,
        # Validación estadística (Bucle iterativo de confiabilidad)
        "iteraciones_monte_carlo": 0,
        "media_p_peak_mpa": 0.0,
        "sd_p_peak_mpa": 0.0,
        "cv_porcentaje": 0.0,
        "confiabilidad_conforme": True
    })
