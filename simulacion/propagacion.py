"""
================================================================================
INTERFAZ NUMÉRICA: SOLVER DE PROPAGACIÓN ACÚSTICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Contrato formal abstracto reservado para eventuales motores numéricos en dominio
temporal. El cálculo del campo y dosimetría se realiza mediante el modelo
analítico-computacional cuasi-gaussiano focalizado con atenuación estratificada
(SolverFisicoESWT en simulacion/solver_fisico.py).
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

