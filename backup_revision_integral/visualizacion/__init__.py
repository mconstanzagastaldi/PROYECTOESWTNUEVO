"""
Módulo de visualización gráfica del simulador ESWT.
"""

from .graficos import (
    graficar_pulso_temporal,
    graficar_mapa_2d,
    graficar_perfil_axial,
    graficar_esquema_tisular,
    graficar_boxplot_confiabilidad
)
from .representacion_geometrica import generar_figura_esquema_tisular

__all__ = [
    "graficar_pulso_temporal",
    "graficar_mapa_2d",
    "graficar_perfil_axial",
    "graficar_esquema_tisular",
    "graficar_boxplot_confiabilidad",
    "generar_figura_esquema_tisular"
]
