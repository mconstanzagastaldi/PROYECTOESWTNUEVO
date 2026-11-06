"""
================================================================================
MODELO DE DATOS: GEOMETRÍA Y SUPERFICIE ANATÓMICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Modela la interfaz anatómica a tratar:
- Superficie Irregular / Curva (zonas de difícil acceso: dedos, manos, articulaciones)
- Superficie Plana / Lisa (zonas regulares: tronco, muslos)
El aplicador opera de forma normal a la superficie asegurando contacto íntimo
mediante la capa de acoplamiento acústico sin mecanismos de articulación móvil.
================================================================================
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ConfiguracionGeometria:
    """Parámetros de la interfaz anatómica y zona de contacto de tratamiento."""
    tipo_superficie: str = "Curva (Articulación / Mano)"  # "Plana (Tronco / Muslo)" o "Curva (Articulación / Mano)"
    profundidad_analisis_cm: float = 2.0                 # Profundidad de evaluación (0.5 a 2.5 cm)
    ancho_lateral_cm: float = 2.0                        # Extensión lateral del dominio (x)
    radio_curvatura_superficie_mm: float = 25.0          # Radio anatómico de la articulación/mano [mm]
    posicion_x_aplicador_mm: float = 0.0                 # Centrado sobre la lesión cutánea
    contacto_acustico_garantizado: bool = True           # Acoplamiento total mediante gel conformable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo_superficie": self.tipo_superficie,
            "profundidad_analisis_cm": self.profundidad_analisis_cm,
            "ancho_lateral_cm": self.ancho_lateral_cm,
            "radio_curvatura_superficie_mm": self.radio_curvatura_superficie_mm,
            "posicion_x_aplicador_mm": self.posicion_x_aplicador_mm,
            "contacto_acustico_garantizado": self.contacto_acustico_garantizado
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfiguracionGeometria":
        return cls(
            tipo_superficie=data.get("tipo_superficie", "Curva (Articulación / Mano)"),
            profundidad_analisis_cm=float(data.get("profundidad_analisis_cm", 2.0)),
            ancho_lateral_cm=float(data.get("ancho_lateral_cm", 2.0)),
            radio_curvatura_superficie_mm=float(data.get("radio_curvatura_superficie_mm", 25.0)),
            posicion_x_aplicador_mm=float(data.get("posicion_x_aplicador_mm", 0.0)),
            contacto_acustico_garantizado=data.get("contacto_acustico_garantizado", True)
        )
