"""
================================================================================
MODELO DE DATOS: CONFIGURACIÓN GLOBAL DEL SIMULADOR
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Estructura raíz que agrupa la totalidad de los subsistemas y permite
la persistencia íntegra de sesiones en formato JSON.
================================================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

try:
    from .aplicador import ConfiguracionAplicador
    from .geometria import ConfiguracionGeometria
    from .parametros import ParametrosOperativos
    from .tejido import CapaTejido, obtener_capas_predeterminadas_literatura
except ImportError:
    from modelos.aplicador import ConfiguracionAplicador
    from modelos.geometria import ConfiguracionGeometria
    from modelos.parametros import ParametrosOperativos
    from modelos.tejido import CapaTejido, obtener_capas_predeterminadas_literatura


@dataclass
class ParametrosMallaSimulacion:
    """Parámetros de discretización del dominio numérico cartesiano x-z."""
    ancho_dominio_cm: float = 2.0
    profundidad_dominio_cm: float = 2.0
    resolucion_dx_um: float = 80.0
    resolucion_dz_um: float = 80.0
    paso_temporal_dt_ns: float = 8.0
    tiempo_total_us: float = 14.5
    tipo_medio: str = "Heterogéneo (Estratificado)"
    condicion_frontera: str = "Absorbente (Sponge ABC)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ancho_dominio_cm": self.ancho_dominio_cm,
            "profundidad_dominio_cm": self.profundidad_dominio_cm,
            "resolucion_dx_um": self.resolucion_dx_um,
            "resolucion_dz_um": self.resolucion_dz_um,
            "paso_temporal_dt_ns": self.paso_temporal_dt_ns,
            "tiempo_total_us": self.tiempo_total_us,
            "tipo_medio": self.tipo_medio,
            "condicion_frontera": self.condicion_frontera
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParametrosMallaSimulacion":
        return cls(
            ancho_dominio_cm=float(data.get("ancho_dominio_cm", 2.0)),
            profundidad_dominio_cm=float(data.get("profundidad_dominio_cm", 2.0)),
            resolucion_dx_um=float(data.get("resolucion_dx_um", 80.0)),
            resolucion_dz_um=float(data.get("resolucion_dz_um", 80.0)),
            paso_temporal_dt_ns=float(data.get("paso_temporal_dt_ns", 8.0)),
            tiempo_total_us=float(data.get("tiempo_total_us", 14.5)),
            tipo_medio=data.get("tipo_medio", "Heterogéneo (Estratificado)"),
            condicion_frontera=data.get("condicion_frontera", "Absorbente (Sponge ABC)")
        )


@dataclass
class ConfiguracionGlobal:
    """Contenedor maestro del estado completo del simulador."""
    nombre_configuracion: str = "Configuracion_Nominal_Anteproyecto"
    fecha_creacion: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    aplicador: ConfiguracionAplicador = field(default_factory=ConfiguracionAplicador)
    geometria: ConfiguracionGeometria = field(default_factory=ConfiguracionGeometria)
    parametros: ParametrosOperativos = field(default_factory=ParametrosOperativos)
    tejidos: List[CapaTejido] = field(default_factory=obtener_capas_predeterminadas_literatura)
    malla: ParametrosMallaSimulacion = field(default_factory=ParametrosMallaSimulacion)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre_configuracion": self.nombre_configuracion,
            "fecha_creacion": self.fecha_creacion,
            "aplicador": self.aplicador.to_dict(),
            "geometria": self.geometria.to_dict(),
            "parametros": self.parametros.to_dict(),
            "tejidos": [t.to_dict() for t in self.tejidos],
            "malla": self.malla.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfiguracionGlobal":
        tejidos_data = data.get("tejidos", [])
        tejidos = [CapaTejido.from_dict(t) for t in tejidos_data] if tejidos_data else obtener_capas_predeterminadas_literatura()

        return cls(
            nombre_configuracion=data.get("nombre_configuracion", "Configuracion_Restaurada"),
            fecha_creacion=data.get("fecha_creacion", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            aplicador=ConfiguracionAplicador.from_dict(data.get("aplicador", {})),
            geometria=ConfiguracionGeometria.from_dict(data.get("geometria", {})),
            parametros=ParametrosOperativos.from_dict(data.get("parametros", {})),
            tejidos=tejidos,
            malla=ParametrosMallaSimulacion.from_dict(data.get("malla", {}))
        )

