"""
================================================================================
INTERFAZ FÍSICA: ATENUACIÓN Y DISIPACIÓN TISULAR
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Contrato formal para el modelado de la disipación acústica viscoelástica
y ley de potencias alpha(f) = alpha_0 * f^y en capas biológicas.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import List
from modelos.tejido import CapaTejido


class ModeloAtenuacion(ABC):
    """Interfaz abstracta para la atenuación de ondas acústicas en estratos biológicos."""

    @abstractmethod
    def calcular_perdidas_estratos(self, capas: List[CapaTejido], frecuencia_mhz: float) -> List[float]:
        """
        Calcula el decaimiento de amplitud en decibelios o factores de transmisión.
        Pendiente de implementación de ecuaciones definitivas.
        """
        pass

