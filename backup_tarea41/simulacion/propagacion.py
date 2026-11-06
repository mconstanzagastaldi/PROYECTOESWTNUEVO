"""
================================================================================
INTERFAZ NUMÉRICA: SOLVER DE PROPAGACIÓN ACÚSTICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Contrato formal para el algoritmo de diferencias finitas en dominio temporal (FDTD)
o algoritmos pseudo-espectrales tipo k-Wave.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from simulacion.malla import Malla2D
from modelos.configuracion import ConfiguracionGlobal


class SolverPropagacion(ABC):
    """Interfaz abstracta para el motor numérico de avance temporal."""

    @abstractmethod
    def inicializar_campos(self, malla: Malla2D, config: ConfiguracionGlobal):
        """Prepara las matrices de memoria y asignación de estratos."""
        pass

    @abstractmethod
    def ejecutar_paso_temporal(self) -> Dict[str, Any]:
        """Avanza un paso de tiempo dt en el dominio."""
        pass

