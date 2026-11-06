"""
================================================================================
MODELO DE DATOS: PARÁMETROS OPERATIVOS Y DOSIMETRÍA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Centraliza la ventana terapéutica de partida especificada en el anteproyecto.
================================================================================
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ParametrosOperativos:
    """Parámetros de dosificación y funcionamiento del aplicador ESWT."""
    # Ventana terapéutica de referencia del anteproyecto
    efd_nominal_mj_mm2: float = 0.10          # Rango anteproyecto: 0.03 a 0.25 mJ/mm²
    frecuencia_repeticion_hz: float = 4.0     # Rango anteproyecto: 4.0 a 5.0 Hz
    profundidad_focal_objetivo_cm: float = 1.0# Rango anteproyecto: 0.5 a 2.0 cm
    densidad_disparos_pcm2: float = 150.0     # Rango anteproyecto: 10 a 500 pulsos/cm²
    area_tratamiento_cm2: float = 10.0        # Área estimada de la quemadura [cm²]

    @property
    def numero_pulsos_total(self) -> int:
        """Calcula la cantidad total de disparos programados para la sesión."""
        return int(round(self.area_tratamiento_cm2 * self.densidad_disparos_pcm2))

    @property
    def tiempo_tratamiento_minutos(self) -> float:
        """Tiempo estimado de sesión en minutos en función de la PRF."""
        if self.frecuencia_repeticion_hz <= 0:
            return 0.0
        return (self.numero_pulsos_total / self.frecuencia_repeticion_hz) / 60.0

    def restablecer_valores_nominales(self):
        """Restablece los parámetros a los valores de diseño del anteproyecto."""
        self.efd_nominal_mj_mm2 = 0.10
        self.frecuencia_repeticion_hz = 4.0
        self.profundidad_focal_objetivo_cm = 1.0
        self.densidad_disparos_pcm2 = 150.0
        self.area_tratamiento_cm2 = 10.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "efd_nominal_mj_mm2": self.efd_nominal_mj_mm2,
            "frecuencia_repeticion_hz": self.frecuencia_repeticion_hz,
            "profundidad_focal_objetivo_cm": self.profundidad_focal_objetivo_cm,
            "densidad_disparos_pcm2": self.densidad_disparos_pcm2,
            "area_tratamiento_cm2": self.area_tratamiento_cm2,
            "numero_pulsos_total": self.numero_pulsos_total,
            "tiempo_tratamiento_minutos": round(self.tiempo_tratamiento_minutos, 2)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParametrosOperativos":
        return cls(
            efd_nominal_mj_mm2=float(data.get("efd_nominal_mj_mm2", 0.10)),
            frecuencia_repeticion_hz=float(data.get("frecuencia_repeticion_hz", 4.0)),
            profundidad_focal_objetivo_cm=float(data.get("profundidad_focal_objetivo_cm", 1.0)),
            densidad_disparos_pcm2=float(data.get("densidad_disparos_pcm2", 150.0)),
            area_tratamiento_cm2=float(data.get("area_tratamiento_cm2", 10.0))
        )

