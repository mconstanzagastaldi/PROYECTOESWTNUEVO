"""
================================================================================
FACHADA DEL MOTOR DE SIMULACIÓN NUMÉRICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Orquesta la ejecución de la simulación acústica de forma desacoplada de la UI.
Informa el estado de integración sin generar resultados inventados o ficticios.
================================================================================
"""

from typing import Dict, Any, Callable, Optional
from modelos.configuracion import ConfiguracionGlobal
from modelos.resultados import ResultadosSimulacion
from servicios.validador import ValidadorClinico, ResultadoValidacion
from simulacion.malla import Malla2D


class MotorSimulacion:
    """Coordinador del motor computacional."""

    def __init__(self, config: Optional[ConfiguracionGlobal] = None):
        self.config = config or ConfiguracionGlobal()
        self.malla = Malla2D(self.config.malla)

    def actualizar_configuracion(self, config: ConfiguracionGlobal):
        self.config = config
        self.malla = Malla2D(config.malla)

    def verificar_precondiciones(self) -> ResultadoValidacion:
        """Comprueba validación clínica y estabilidad CFL antes de simular."""
        val = ValidadorClinico.validar_configuracion_completa(self.config)

        # Determinar la velocidad máxima en los estratos tisulares
        c_max = max([c.velocidad_m_s for c in self.config.tejidos], default=1750.0)
        cfl = self.malla.calcular_cfl(c_max)

        if cfl >= 1.0:
            val.agregar_error(f"Inestabilidad numérica CFL detectada: CFL = {cfl:.3f} >= 1.0. Reduzca dt o incremente dx.")
        elif cfl > 0.5:
            val.agregar_advertencia(f"CFL = {cfl:.3f} cercano al límite de estabilidad (se recomienda CFL <= 0.3 para discretización explícita).")

        return val

    def ejecutar_simulacion(self, callback_progreso: Optional[Callable[[int, str], None]] = None) -> ResultadosSimulacion:
        """
        Ejecuta el flujo computacional de acuerdo a las directivas del anteproyecto.
        Genera la solución computacional completa del campo de presión y dosimetría.
        """
        if callback_progreso:
            callback_progreso(10, "Verificando precondiciones y estabilidad numérica CFL...")

        val = self.verificar_precondiciones()
        if not val.es_valido:
            res = ResultadosSimulacion(
                disponible=False,
                mensaje_estado=f"No se puede iniciar la simulación: {'; '.join(val.errores)}"
            )
            return res

        if callback_progreso:
            callback_progreso(50, "Malla inicializada. Ejecutando solver biofísico de ondas de choque...")

        # Ejecución computacional con el solver físico integrado
        from simulacion.solver_fisico import SolverFisicoESWT
        resultados = SolverFisicoESWT.simular(self.config)
        resultados.metricas["cfl_calculado"] = self.malla.calcular_cfl()
        resultados.metricas["dimensiones_malla"] = f"{self.malla.Nz} x {self.malla.Nx} nodos"

        if callback_progreso:
            callback_progreso(100, "Simulación computacional completada con éxito.")

        return resultados
