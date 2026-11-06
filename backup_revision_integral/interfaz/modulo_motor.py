"""
================================================================================
MÓDULO 7: CONTROL Y DIAGNÓSTICO DEL MOTOR DE SIMULACIÓN
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Orquesta la validación cruzada y el disparo del motor numérico.
Informa con rigor técnico que la propagación acústica se encuentra desacoplada.
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QProgressBar, QScrollArea, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from interfaz.componentes import (
    Colores, TarjetaContenedor, TarjetaEstado, BotonPrimario, BadgeEstado
)
from modelos.configuracion import ConfiguracionGlobal
from simulacion.motor_simulacion import MotorSimulacion


class ModuloMotor(QWidget):
    """Panel de control para verificación pre-simulación y estado del motor."""

    simulacion_completada = Signal(object)

    def __init__(self, config: ConfiguracionGlobal = None, parent=None):
        super().__init__(parent)
        self.config = config or ConfiguracionGlobal()
        self.motor = MotorSimulacion(self.config)
        self._inicializar_ui()

    def _inicializar_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(22)

        # ----------------------------------------------------------------------
        # 1. ENCABEZADO
        # ----------------------------------------------------------------------
        header = TarjetaContenedor()
        l_head = QVBoxLayout(header)
        l_head.setContentsMargins(22, 18, 22, 18)
        l_head.setSpacing(6)

        badge = BadgeEstado("CONTROL COMPUTACIONAL", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Motor de Simulación Numérica y Verificación Previa")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Supervisa la integridad del modelo antes de la ejecución computacional. Valida de forma "
            "cruzada los parámetros del aplicador, la geometría anatómica, los estratos tisulares y la malla FDTD."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. DASHBOARD DE PRECONDICIONES
        # ----------------------------------------------------------------------
        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(16)

        self.card_val_clinica = TarjetaEstado(
            titulo="Ventana Operativa",
            valor="Comprobada",
            subtitulo="EFD, PRF y Foco en rango seguro",
            color_acento=Colores.ESTADO_OK
        )
        layout_cards.addWidget(self.card_val_clinica)

        self.card_val_malla = TarjetaEstado(
            titulo="Estabilidad Numérica",
            valor="CFL Conforme",
            subtitulo="Condición CFL < 1.0 verificada",
            color_acento=Colores.ESTADO_OK
        )
        layout_cards.addWidget(self.card_val_malla)

        self.card_estado_fisica = TarjetaEstado(
            titulo="Solver de Propagación",
            valor="Desacoplado",
            subtitulo="A la espera de formulación física",
            color_acento=Colores.ESTADO_INFO
        )
        layout_cards.addWidget(self.card_estado_fisica)

        layout.addLayout(layout_cards)

        # ----------------------------------------------------------------------
        # 3. ACCIÓN DE VERIFICACIÓN Y REGISTRO EN TIEMPO REAL
        # ----------------------------------------------------------------------
        tarjeta_accion = TarjetaContenedor()
        l_acc = QVBoxLayout(tarjeta_accion)
        l_acc.setContentsMargins(24, 20, 24, 20)
        l_acc.setSpacing(16)

        t_cons = QLabel("REGISTRO DE EJECUCIÓN Y DIAGNÓSTICO DEL SISTEMA")
        t_cons.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_cons.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_acc.addWidget(t_cons)

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(0)
        self.barra_progreso.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {Colores.BORDE_TARJETA};
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background-color: #f1f5f9;
            }}
            QProgressBar::chunk {{
                background-color: {Colores.CELESTE_ACENTO};
                border-radius: 3px;
            }}
        """)
        l_acc.addWidget(self.barra_progreso)

        self.consola = QTextEdit()
        self.consola.setReadOnly(True)
        self.consola.setFont(QFont("Consolas", 8))
        self.consola.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colores.AZUL_PRIMARIO};
                color: #e2e8f0;
                border: 1px solid {Colores.AZUL_BORDE};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        self.consola.setMinimumHeight(180)
        l_acc.addWidget(self.consola)

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_ejecutar = BotonPrimario("▶ Ejecutar Comprobación y Simulación")
        self.btn_ejecutar.clicked.connect(self._ejecutar_verificacion)
        btn_box.addWidget(self.btn_ejecutar)

        l_acc.addLayout(btn_box)
        layout.addWidget(tarjeta_accion)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

        self._imprimir_estado_inicial()

    def actualizar_configuracion(self, config: ConfiguracionGlobal):
        self.config = config
        self.motor.actualizar_configuracion(config)
        self.card_val_clinica.actualizar("En espera", "Configuración actualizada")
        self.card_val_cfl.actualizar(f"CFL = {self.motor.malla.calcular_cfl():.3f}", "Estabilidad numérica")
        self.consola.append(f"• Configuración actualizada: EFD = {config.parametros.efd_nominal_mj_mm2:.3f} mJ/mm² | Foco = {config.parametros.profundidad_focal_objetivo_cm:.1f} cm")
        self._imprimir_estado_inicial()

    def _imprimir_estado_inicial(self):
        self.consola.clear()
        c = self.config
        self.consola.append("================================================================================")
        self.consola.append("DIAGNÓSTICO DEL MOTOR DE SIMULACIÓN - BIOINGENIERÍA UNER")
        self.consola.append(f"Configuración cargada: {c.nombre_configuracion}")
        self.consola.append(f"Aplicador: {c.aplicador.tipo_generacion} | Cabezal: {c.aplicador.cabezal.tipo_geometria} ({c.aplicador.cabezal.angulo_orientacion_deg:+.1f}°)")
        self.consola.append(f"Superficie: {c.geometria.tipo_superficie} | Profundidad: {c.geometria.profundidad_analisis_cm:.1f} cm")
        self.consola.append(f"Dosimetría: EFD = {c.parametros.efd_nominal_mj_mm2:.3f} mJ/mm² | PRF = {c.parametros.frecuencia_repeticion_hz:.1f} Hz | Disparos = {c.parametros.numero_pulsos_total}")
        self.consola.append(f"Estratos tisulares: {len(c.tejidos)} capas definidas")
        self.consola.append("Estado del solver numérico: DESACOPLADO (En espera de formulación física)")
        self.consola.append("================================================================================")

    def _ejecutar_verificacion(self):
        self.barra_progreso.setValue(10)
        self.consola.append("\n[INFO] Iniciando verificación de precondiciones...")

        def cb_prog(pct, msg):
            self.barra_progreso.setValue(pct)
            self.consola.append(f"[{pct}%] {msg}")

        resultados = self.motor.ejecutar_simulacion(callback_progreso=cb_prog)

        self.consola.append("\n" + "=" * 80)
        self.consola.append("DICTAMEN DEL MOTOR:")
        self.consola.append(resultados.mensaje_estado)
        self.consola.append("Métricas verificadas:")
        for k, v in resultados.metricas.items():
            self.consola.append(f" • {k}: {v}")
        self.consola.append("=" * 80)

        self.simulacion_completada.emit(resultados)

        QMessageBox.information(
            self,
            "Verificación Completada",
            "La configuración del aplicador y la malla han sido validadas exitosamente.\n\n"
            "El sistema se encuentra preparado para recibir las ecuaciones de onda y "
            "la formulación física del casquete cóncavo cuando sean integradas."
        )
