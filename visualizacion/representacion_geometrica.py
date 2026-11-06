"""
================================================================================
MÓDULO DE VISUALIZACIÓN CIENTÍFICA: REPRESENTACIÓN GEOMÉTRICA TISULAR
SIMULADOR ESWT - TALLER DE BIOINGENIERÍA (UNER)
================================================================================
Autores del proyecto:
- Gastaldi, María Constanza
- Gerstner Soltermann, Marthina
- Kessel, Florencia
Asesor: Zapata, Daniel
================================================================================
Dibujo a escala del aplicador piezoeléctrico rígido de orientación fija normal
(sin mecanismo de inclinación) con casquete cóncavo (apertura 16 mm, curvatura 20 mm,
chasis <= 40 mm) acoplado acústicamente mediante gel conformable (Z = 1.50 MRayl)
sobre superficies irregulares (articulaciones/manos) o planas (tronco/muslos).
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from visualizacion.graficos import graficar_esquema_tisular


def generar_figura_esquema_tisular(
    tipo_superficie: str = "Curva",
    profundidad_focal_mm: float = 10.0,
    tipo_quemadura: str = "3er Grado",
    estilo_oscuro: bool = True
) -> Figure:
    """Crea y retorna una Figure independiente de Matplotlib con el esquema geométrico."""
    fig = Figure(figsize=(7.5, 5.0), dpi=100, facecolor="#040711" if estilo_oscuro else "#ffffff")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#040711" if estilo_oscuro else "#ffffff")

    for spine in ax.spines.values():
        spine.set_color("#334155" if estilo_oscuro else "#cbd5e1")
    ax.tick_params(colors="#94a3b8" if estilo_oscuro else "#475569", labelsize=8)
    ax.grid(True, linestyle=":", alpha=0.3, color="#475569" if estilo_oscuro else "#cbd5e1")

    graficar_esquema_tisular(
        ax=ax,
        tipo_superficie=tipo_superficie,
        profundidad_focal_mm=profundidad_focal_mm,
        tipo_quemadura=tipo_quemadura,
        estilo_oscuro=estilo_oscuro
    )
    fig.tight_layout()
    return fig
