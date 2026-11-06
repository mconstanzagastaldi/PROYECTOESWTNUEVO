"""
================================================================================
INTERFAZ FÍSICA: FOCALIZACIÓN ACÚSTICA Y CASQUETE CÓNCAVO
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Contrato formal para el modelo de focalización geométrica por casquete cóncavo
y distribución espacial de cerámicas piezoeléctricas.
IMPORTANTE: Pendiente de formulación física de la integrante del equipo.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ModeloFocalizacion(ABC):
    """Interfaz abstracta para la focalización acústica del aplicador."""

    @abstractmethod
    def calcular_perfil_focal(self, radio_curvatura_mm: float, apertura_mm: float) -> Dict[str, Any]:
        """
        Calcula la convergencia del haz hacia la profundidad focal.
        Pendiente de definición física del transductor.
        """
        pass

    @abstractmethod
    def calcular_retardos_emision(self, elementos_piezo: int) -> Dict[str, Any]:
        """Calcula leyes de retardo para arreglos piezoeléctricos."""
        pass

