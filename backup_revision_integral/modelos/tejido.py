"""
================================================================================
MODELO DE DATOS: CAPAS TISULARES Y BIOACÚSTICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Define la estructura de cada estrato tisular (densidad, velocidad, impedancia,
atenuación) con valores basados en literatura de bioingeniería (Duck 1990 / IT'IS).
================================================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class CapaTejido:
    """Propiedades físicas y bioacústicas de un estrato tisular individual."""
    nombre: str
    espesor_mm: float
    densidad_kg_m3: float
    velocidad_m_s: float
    impedancia_rayl: float
    atenuacion_db_cm_mhz: float
    es_editable: bool = True

    def recalcular_impedancia(self) -> float:
        """Calcula la impedancia acústica característica Z = rho * c."""
        self.impedancia_rayl = self.densidad_kg_m3 * self.velocidad_m_s
        return self.impedancia_rayl

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "espesor_mm": self.espesor_mm,
            "densidad_kg_m3": self.densidad_kg_m3,
            "velocidad_m_s": self.velocidad_m_s,
            "impedancia_rayl": self.impedancia_rayl,
            "atenuacion_db_cm_mhz": self.atenuacion_db_cm_mhz,
            "es_editable": self.es_editable
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapaTejido":
        return cls(
            nombre=data.get("nombre", "Estrato"),
            espesor_mm=float(data.get("espesor_mm", 1.0)),
            densidad_kg_m3=float(data.get("densidad_kg_m3", 1000.0)),
            velocidad_m_s=float(data.get("velocidad_m_s", 1500.0)),
            impedancia_rayl=float(data.get("impedancia_rayl", 1.50e6)),
            atenuacion_db_cm_mhz=float(data.get("atenuacion_db_cm_mhz", 0.5)),
            es_editable=data.get("es_editable", True)
        )


def obtener_capas_predeterminadas_literatura() -> List[CapaTejido]:
    """
    Retorna la estratificación anatómica estándar reportada en literatura científica
    (Duck 1990; IT'IS Database for Thermal and Acoustical Properties).
    """
    return [
        CapaTejido(
            nombre="Gel de Acoplamiento",
            espesor_mm=1.5,
            densidad_kg_m3=1000.0,
            velocidad_m_s=1500.0,
            impedancia_rayl=1.50e6,
            atenuacion_db_cm_mhz=0.002,
            es_editable=True
        ),
        CapaTejido(
            nombre="Epidermis / Piel Sana",
            espesor_mm=2.5,
            densidad_kg_m3=1090.0,
            velocidad_m_s=1625.0,
            impedancia_rayl=1090.0 * 1625.0,
            atenuacion_db_cm_mhz=0.800,
            es_editable=True
        ),
        CapaTejido(
            nombre="Cicatriz Fibrótica (3er Grado)",
            espesor_mm=9.0,
            densidad_kg_m3=1200.0,
            velocidad_m_s=1750.0,
            impedancia_rayl=1200.0 * 1750.0,
            atenuacion_db_cm_mhz=2.100,
            es_editable=True
        ),
        CapaTejido(
            nombre="Tejido Celular Subcutáneo",
            espesor_mm=7.0,
            densidad_kg_m3=920.0,
            velocidad_m_s=1450.0,
            impedancia_rayl=920.0 * 1450.0,
            atenuacion_db_cm_mhz=0.600,
            es_editable=True
        )
    ]
