"""
================================================================================
MALLA Y DISCRETIZACIÓN NUMÉRICA 2D
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Gestiona la cuadrícula espacial (x, z) y temporal (t), asegurando la condición
de estabilidad de Courant-Friedrichs-Lewy (CFL).
================================================================================
"""

import numpy as np
from modelos.configuracion import ParametrosMallaSimulacion


class Malla2D:
    """Discretización del dominio cartesiano x-z para el método numérico."""

    def __init__(self, parametros: ParametrosMallaSimulacion):
        self.params = parametros

        # Conversión a unidades del Sistema Internacional (SI)
        self.ancho_m = parametros.ancho_dominio_cm * 1.0e-2
        self.profundidad_m = parametros.profundidad_dominio_cm * 1.0e-2
        self.dx_m = parametros.resolucion_dx_um * 1.0e-6
        self.dz_m = parametros.resolucion_dz_um * 1.0e-6
        self.dt_s = parametros.paso_temporal_dt_ns * 1.0e-9
        self.tiempo_total_s = parametros.tiempo_total_us * 1.0e-6

        # Vectores de coordenadas físicas
        self.x = np.arange(0, self.ancho_m + self.dx_m, self.dx_m)
        self.z = np.arange(0, self.profundidad_m + self.dz_m, self.dz_m)
        self.Nx = len(self.x)
        self.Nz = len(self.z)

        # Pasos temporales
        self.pasos_tiempo = int(round(self.tiempo_total_s / self.dt_s)) if self.dt_s > 0 else 0
        self.t = np.arange(self.pasos_tiempo) * self.dt_s

    def calcular_cfl(self, c_max_m_s: float = 1750.0) -> float:
        """
        Calcula el número de Courant-Friedrichs-Lewy (CFL):
        CFL = c_max * dt * sqrt( (1/dx^2) + (1/dz^2) )
        Para estabilidad numérica explícita se requiere CFL < 1.0.
        """
        if self.dx_m <= 0 or self.dz_m <= 0:
            return 999.0
        termino_espacial = np.sqrt((1.0 / (self.dx_m ** 2)) + (1.0 / (self.dz_m ** 2)))
        return float(c_max_m_s * self.dt_s * termino_espacial)

    def es_estable_cfl(self, c_max_m_s: float = 1750.0) -> bool:
        """Verifica si la malla cumple la condición estricta de estabilidad CFL."""
        return self.calcular_cfl(c_max_m_s) < 1.0

