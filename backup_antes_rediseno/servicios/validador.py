"""
================================================================================
SERVICIO DE VALIDACIÓN DE PARÁMETROS CLÍNICOS Y FÍSICOS
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Comprueba que los datos ingresados por el usuario se encuentren dentro de la
ventana terapéutica de partida del anteproyecto y respeten la consistencia física.
================================================================================
"""

from dataclasses import dataclass, field
from typing import List
from modelos.configuracion import ConfiguracionGlobal
from modelos.parametros import ParametrosOperativos
from modelos.tejido import CapaTejido


@dataclass
class ResultadoValidacion:
    """Resultado de la inspección de parámetros con listas de errores y advertencias."""
    es_valido: bool = True
    errores: List[str] = field(default_factory=list)
    advertencias: List[str] = field(default_factory=list)

    def agregar_error(self, mensaje: str):
        self.es_valido = False
        self.errores.append(mensaje)

    def agregar_advertencia(self, mensaje: str):
        self.advertencias.append(mensaje)


class ValidadorClinico:
    """Valida los rangos operativos y biofísicos según el anteproyecto UNER."""

    # Rangos de referencia de partida (Anteproyecto)
    EFD_MIN, EFD_MAX = 0.03, 0.25              # mJ/mm²
    PRF_MIN, PRF_MAX = 4.0, 5.0                # Hz
    FOCO_MIN, FOCO_MAX = 0.5, 2.0              # cm
    DISPAROS_MIN, DISPAROS_MAX = 10.0, 500.0   # pulsos/cm²
    ANGULO_MIN, ANGULO_MAX = -45.0, 45.0       # grados

    @classmethod
    def validar_parametros_operativos(cls, p: ParametrosOperativos) -> ResultadoValidacion:
        res = ResultadoValidacion()

        # Validación de Densidad de Flujo de Energía (EFD)
        if p.efd_nominal_mj_mm2 <= 0:
            res.agregar_error("La EFD debe ser un valor estrictamente positivo.")
        elif p.efd_nominal_mj_mm2 < cls.EFD_MIN:
            res.agregar_advertencia(
                f"EFD ({p.efd_nominal_mj_mm2:.3f} mJ/mm²) por debajo del umbral clínico del anteproyecto ({cls.EFD_MIN} mJ/mm²)."
            )
        elif p.efd_nominal_mj_mm2 > cls.EFD_MAX:
            res.agregar_advertencia(
                f"EFD ({p.efd_nominal_mj_mm2:.3f} mJ/mm²) supera el límite superior de baja intensidad ({cls.EFD_MAX} mJ/mm²)."
            )

        # Validación de Frecuencia de Repetición (PRF)
        if p.frecuencia_repeticion_hz <= 0:
            res.agregar_error("La frecuencia PRF debe ser mayor a 0 Hz.")
        elif not (cls.PRF_MIN <= p.frecuencia_repeticion_hz <= cls.PRF_MAX):
            res.agregar_advertencia(
                f"Frecuencia ({p.frecuencia_repeticion_hz:.1f} Hz) fuera de la ventana nominal ({cls.PRF_MIN} a {cls.PRF_MAX} Hz)."
            )

        # Validación de Profundidad Focal
        if p.profundidad_focal_objetivo_cm <= 0:
            res.agregar_error("La profundidad focal objetivo debe ser mayor a 0 cm.")
        elif not (cls.FOCO_MIN <= p.profundidad_focal_objetivo_cm <= cls.FOCO_MAX):
            res.agregar_advertencia(
                f"Profundidad focal ({p.profundidad_focal_objetivo_cm:.2f} cm) fuera del espesor diana ({cls.FOCO_MIN} a {cls.FOCO_MAX} cm)."
            )

        # Validación de Densidad de Disparos
        if p.densidad_disparos_pcm2 <= 0:
            res.agregar_error("La densidad de disparos debe ser positiva.")
        elif not (cls.DISPAROS_MIN <= p.densidad_disparos_pcm2 <= cls.DISPAROS_MAX):
            res.agregar_advertencia(
                f"Densidad de disparos ({p.densidad_disparos_pcm2:.0f} p/cm²) fuera del rango recomendado ({cls.DISPAROS_MIN:.0f} a {cls.DISPAROS_MAX:.0f} p/cm²)."
            )

        return res

    @classmethod
    def validar_capas_tejido(cls, capas: List[CapaTejido]) -> ResultadoValidacion:
        res = ResultadoValidacion()
        if not capas:
            res.agregar_error("El modelo debe contener al menos un estrato tisular.")
            return res

        for c in capas:
            if c.espesor_mm <= 0:
                res.agregar_error(f"El estrato '{c.nombre}' tiene un espesor inválido (<= 0 mm).")
            if c.densidad_kg_m3 < 500 or c.densidad_kg_m3 > 3000:
                res.agregar_advertencia(f"Densidad de '{c.nombre}' ({c.densidad_kg_m3:.0f} kg/m³) atípica para tejidos blandos.")
            if c.velocidad_m_s < 1000 or c.velocidad_m_s > 2500:
                res.agregar_advertencia(f"Velocidad de '{c.nombre}' ({c.velocidad_m_s:.0f} m/s) atípica para tejidos blandos.")
            if c.atenuacion_db_cm_mhz < 0:
                res.agregar_error(f"Coeficiente de atenuación de '{c.nombre}' no puede ser negativo.")

        return res

    @classmethod
    def validar_configuracion_completa(cls, cfg: ConfiguracionGlobal) -> ResultadoValidacion:
        res = cls.validar_parametros_operativos(cfg.parametros)
        res_tej = cls.validar_capas_tejido(cfg.tejidos)

        res.errores.extend(res_tej.errores)
        res.advertencias.extend(res_tej.advertencias)
        res.es_valido = len(res.errores) == 0

        # Validar ángulo de inclinación del cabezal
        ang = cfg.aplicador.cabezal.angulo_orientacion_deg
        if not (cls.ANGULO_MIN <= ang <= cls.ANGULO_MAX):
            res.agregar_advertencia(f"Ángulo de orientación ({ang:.1f}°) excede el límite recomendado (±45°).")

        return res

