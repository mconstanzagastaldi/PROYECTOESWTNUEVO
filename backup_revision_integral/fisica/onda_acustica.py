"""
================================================================================
INTERFAZ FÍSICA: ECUACIÓN DE ONDA ACÚSTICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Contrato formal para el modelo de propagación acústica en medios biológicos.
IMPORTANTE: En esta etapa no se implementan ecuaciones definitivas.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class ModeloOndaAcustica(ABC):
    """Interfaz abstracta para modelos de propagación de ondas de choque."""

    @abstractmethod
    def calcular_campo_presion(self, malla, fuentes, propiedades_medio) -> np.ndarray:
        """
        Calcula la evolución o distribución de presión acústica.
        Pendiente de implementación según formulación física definitiva.
        """
        pass

    @abstractmethod
    def obtener_descripcion(self) -> Dict[str, Any]:
        """Retorna información del modelo físico utilizado."""
        pass

