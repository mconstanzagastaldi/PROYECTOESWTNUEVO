"""
================================================================================
GESTOR DE ALMACENAMIENTO Y PERSISTENCIA (JSON)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Gestiona el guardado, recuperación y registro de archivos de configuración (.json).
================================================================================
"""

import json
import os
from typing import List, Optional, Tuple
from modelos.configuracion import ConfiguracionGlobal
try:
    from .validador import ValidadorClinico, ResultadoValidacion
except ImportError:
    from servicios.validador import ValidadorClinico, ResultadoValidacion


class GestorConfiguracion:
    """Administra la persistencia de sesiones y configuraciones del simulador."""

    DIRECTORIO_POR_DEFECTO = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "datos",
        "configuraciones"
    )

    @classmethod
    def asegurar_directorio(cls) -> str:
        os.makedirs(cls.DIRECTORIO_POR_DEFECTO, exist_ok=True)
        return cls.DIRECTORIO_POR_DEFECTO

    @classmethod
    def guardar_archivo(cls, configuracion: ConfiguracionGlobal, ruta_destino: Optional[str] = None) -> Tuple[bool, str]:
        """
        Guarda la configuración actual en un archivo JSON estructurado.
        Retorna (éxito: bool, mensaje: str).
        """
        try:
            cls.asegurar_directorio()
            if not ruta_destino:
                nombre_limpio = configuracion.nombre_configuracion.strip().replace(" ", "_")
                ruta_destino = os.path.join(cls.DIRECTORIO_POR_DEFECTO, f"{nombre_limpio}.json")

            data = configuracion.to_dict()
            with open(ruta_destino, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            return True, f"Configuración guardada exitosamente en:\n{ruta_destino}"
        except Exception as e:
            return False, f"Error al guardar el archivo: {str(e)}"

    @classmethod
    def cargar_archivo(cls, ruta_origen: str) -> Tuple[Optional[ConfiguracionGlobal], ResultadoValidacion, str]:
        """
        Lee y valida una configuración almacenada en JSON.
        Retorna (config: Optional[ConfiguracionGlobal], validacion: ResultadoValidacion, mensaje: str).
        """
        val_res = ResultadoValidacion()
        if not os.path.isfile(ruta_origen):
            val_res.agregar_error("El archivo especificado no existe.")
            return None, val_res, "Archivo no encontrado."

        try:
            with open(ruta_origen, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                val_res.agregar_error("Formato JSON inválido: la raíz debe ser un objeto.")
                return None, val_res, "Estructura JSON inválida."

            cfg = ConfiguracionGlobal.from_dict(data)
            val_res = ValidadorClinico.validar_configuracion_completa(cfg)

            return cfg, val_res, "Configuración cargada correctamente."
        except Exception as e:
            val_res.agregar_error(f"Error de lectura o parseo: {str(e)}")
            return None, val_res, f"Error al abrir: {str(e)}"

    @classmethod
    def listar_configuraciones_locales(cls) -> List[str]:
        """Devuelve los nombres de los archivos .json disponibles en datos/configuraciones/."""
        cls.asegurar_directorio()
        try:
            archivos = [f for f in os.listdir(cls.DIRECTORIO_POR_DEFECTO) if f.endswith(".json")]
            return sorted(archivos)
        except Exception:
            return []

