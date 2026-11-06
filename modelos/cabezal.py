"""
================================================================================
MODELO DE DATOS: CABEZAL ACÚSTICO
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Modela las características físicas y constructivas del cabezal piezoeléctrico.
Diseño estricto según anteproyecto:
- Orientación fija normal (sin mecanismo de articulación o inclinación angular).
- Adaptación a superficies irregulares (articulaciones/manos) y planas mediante
  diseño ergonómico compacto (chasis <= 40 mm) y acoplamiento acústico deformable.
- Casquete cóncavo para focalización acústica de ondas de choque de baja intensidad.
================================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ConfiguracionCabezal:
    """Configuración geométrica y mecánica del cabezal de ondas de choque."""
    tipo_geometria: str = "Cóncavo"                  # Cóncavo para focalización acústica
    orientacion_ajustable: bool = False              # Fijo normal sin inclinación según directiva de diseño
    orientacion_fija_normal: bool = True             # Emisión perpendicular directa (sin mecanismo de orientación móvil)
    angulo_orientacion_deg: float = 0.0              # Fijo en 0.0° (normal a la interfaz tisular)
    radio_curvatura_mm: float = 30.0                 # Radio del casquete cóncavo seleccionado [mm] (Tarea 4.1)
    apertura_diametro_mm: float = 30.0               # Diámetro de apertura del casquete [mm] (F-number = 1.0)
    diametro_exterior_chasis_mm: float = 38.0        # Diámetro exterior compacto <= 40 mm (ergonomía wand para manos)
    distancia_focal_geometrica_mm: float = 15.0      # Distancia focal nominal en tejido (con distanciador D15)

    # Parámetros reservados para futura integración con la formulación física de tu compañera
    datos_adicionales: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo_geometria": self.tipo_geometria,
            "orientacion_ajustable": self.orientacion_ajustable,
            "orientacion_fija_normal": self.orientacion_fija_normal,
            "angulo_orientacion_deg": self.angulo_orientacion_deg,
            "radio_curvatura_mm": self.radio_curvatura_mm,
            "apertura_diametro_mm": self.apertura_diametro_mm,
            "diametro_exterior_chasis_mm": self.diametro_exterior_chasis_mm,
            "distancia_focal_geometrica_mm": self.distancia_focal_geometrica_mm,
            "datos_adicionales": self.datos_adicionales
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfiguracionCabezal":
        return cls(
            tipo_geometria=data.get("tipo_geometria", "Cóncavo"),
            orientacion_ajustable=data.get("orientacion_ajustable", False),
            orientacion_fija_normal=data.get("orientacion_fija_normal", True),
            angulo_orientacion_deg=float(data.get("angulo_orientacion_deg", 0.0)),
            radio_curvatura_mm=float(data.get("radio_curvatura_mm", 30.0)),
            apertura_diametro_mm=float(data.get("apertura_diametro_mm", 30.0)),
            diametro_exterior_chasis_mm=float(data.get("diametro_exterior_chasis_mm", 38.0)),
            distancia_focal_geometrica_mm=float(data.get("distancia_focal_geometrica_mm", 15.0)),
            datos_adicionales=data.get("datos_adicionales", {})
        )
