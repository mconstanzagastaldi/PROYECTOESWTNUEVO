"""
================================================================================
MODELO DE DATOS: APLICADOR PIEZOELÉCTRICO (ESWT)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Representa el aplicador completo: tecnología de generación piezoeléctrica,
cabezal cóncavo de orientación fija normal y sistema de acoplamiento acústico
adaptable (gel/almohadilla) para superficies tanto planas como articulaciones/manos.
================================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, Any
try:
    from .cabezal import ConfiguracionCabezal
except ImportError:
    from modelos.cabezal import ConfiguracionCabezal


@dataclass
class ConfiguracionAplicador:
    """Especificaciones técnicas y funcionales del aplicador de ondas de choque."""
    tipo_generacion: str = "Piezoeléctrica"               # Piezoeléctrica (Anteproyecto UNER)
    sistema_acoplamiento: str = "Gel Acústico Adaptable (Z ≈ 1.50 MRayl)" # Interfaz de contacto íntimo piel-aplicador
    impedancia_acoplamiento_rayl: float = 1.50e6         # Z ≈ 1.50 MRayl (Agua / Gel desgasificado)
    espesor_gel_mm: float = 1.5                          # Espesor nominal de la capa de gel
    espesor_gel_nominal_mm: float = 1.5                  # Alias para espesor de la capa de acoplamiento
    distanciador_seleccionado_mm: float = 15.0           # Distanciador acústico intercambiable (0.0=D0, 10.0=D10, 15.0=D15 nominal, 20.0=D20)
    modo_adaptacion: str = "Conformable"                 # Se deforma para ajustarse a curvaturas anatómicas
    cabezal: ConfiguracionCabezal = field(default_factory=ConfiguracionCabezal)

    # Campos definidos y justificados para la Tarea 4.1:
    especificaciones_hardware: Dict[str, Any] = field(default_factory=lambda: {
        "tecnologia_transductor": "Monoelemento piezoeléctrico sobre casquete esférico cóncavo (PZT-4 / PZT-8)",
        "mecanismo_orientacion": "Fijo normal (sin piezas móviles articuladas, 0.0°)",
        "ergonomia": "Diseño tipo wand (empuñadura cilíndrica) diámetro exterior 38 mm (<= 40 mm, RF8)",
        "material_piezoelectrico": "Cerámica PZT-4 / PZT-8 de alta potencia mecánica y bajo factor de disipación",
        "cantidad_elementos": "1 elemento esférico autofocalizante de apertura 30 mm y radio 30 mm",
        "voltaje_excitacion_v": "2.5 kV a 4.0 kV de pulso ultracorto",
        "frecuencia_resonancia_mhz": "1.0 MHz a 1.5 MHz",
        "distanciadores_compatibles": "Set de polímero/almohadilla D10 (10 mm), D15 (15 mm, nominal), D20 (20 mm)"
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo_generacion": self.tipo_generacion,
            "sistema_acoplamiento": self.sistema_acoplamiento,
            "impedancia_acoplamiento_rayl": self.impedancia_acoplamiento_rayl,
            "espesor_gel_nominal_mm": self.espesor_gel_nominal_mm,
            "distanciador_seleccionado_mm": self.distanciador_seleccionado_mm,
            "modo_adaptacion": self.modo_adaptacion,
            "cabezal": self.cabezal.to_dict(),
            "especificaciones_hardware": self.especificaciones_hardware
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfiguracionAplicador":
        cabezal_data = data.get("cabezal", {})
        return cls(
            tipo_generacion=data.get("tipo_generacion", "Piezoeléctrica"),
            sistema_acoplamiento=data.get("sistema_acoplamiento", "Gel Acústico Adaptable (Z ≈ 1.50 MRayl)"),
            impedancia_acoplamiento_rayl=float(data.get("impedancia_acoplamiento_rayl", 1.50e6)),
            espesor_gel_nominal_mm=float(data.get("espesor_gel_nominal_mm", data.get("espesor_gel_mm", 1.5))),
            distanciador_seleccionado_mm=float(data.get("distanciador_seleccionado_mm", 15.0)),
            modo_adaptacion=data.get("modo_adaptacion", "Conformable"),
            cabezal=ConfiguracionCabezal.from_dict(cabezal_data),
            especificaciones_hardware=data.get("especificaciones_hardware", {})
        )
