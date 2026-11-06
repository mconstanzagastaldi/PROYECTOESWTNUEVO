"""
================================================================================
MÓDULO 3: GEOMETRÍA Y SUPERFICIE ANATÓMICA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Configura la interfaz cutánea (plana vs curva/articulación/manos) y la adaptación
del cabezal cóncavo mediante acoplamiento acústico en posición normal (0° fija).
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QScrollArea, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from interfaz.componentes import (
    Colores, TarjetaContenedor, BotonPrimario, BadgeEstado
)
from modelos.geometria import ConfiguracionGeometria
from visualizacion.graficos import graficar_esquema_tisular


class ModuloGeometria(QWidget):
    """Configuración de la superficie anatómica y visualización 2D conceptual."""

    geometria_modificada = Signal(ConfiguracionGeometria)

    def __init__(self, geometria: ConfiguracionGeometria = None, parent=None):
        super().__init__(parent)
        self.geometria = geometria or ConfiguracionGeometria()
        self._inicializar_ui()
        self.cargar_datos(self.geometria)

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

        badge = BadgeEstado("ADAPTABILIDAD ANATÓMICA", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Geometría de Aplicación y Superficie Tisular")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Configure la anatomía de la zona afectada por quemadura: zonas planas regulares (tronco o muslos) "
            "o superficies curvas e irregulares (manos, dedos y articulaciones). El aplicador opera con emisión "
            "normal fija (0.0°), garantizando el contacto íntimo a través del acoplamiento acústico conformable."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. CONTROLES Y GRÁFICO 2D
        # ----------------------------------------------------------------------
        fila_central = QHBoxLayout()
        fila_central.setSpacing(18)

        # Formulario de parámetros
        tarjeta_ctrl = TarjetaContenedor()
        l_ctrl = QVBoxLayout(tarjeta_ctrl)
        l_ctrl.setContentsMargins(20, 18, 20, 18)
        l_ctrl.setSpacing(16)

        t_ctrl = QLabel("PARÁMETROS ANATÓMICOS")
        t_ctrl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_ctrl.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_ctrl.addWidget(t_ctrl)

        grid = QGridLayout()
        grid.setSpacing(12)

        # Selector Superficie
        lbl_sup = QLabel("Superficie Anatómica:")
        lbl_sup.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.combo_superficie = QComboBox()
        self.combo_superficie.addItems(["Curva (Articulación / Mano)", "Plana (Tronco / Muslo)"])
        self.combo_superficie.currentTextChanged.connect(self._actualizar_grafico)
        grid.addWidget(lbl_sup, 0, 0)
        grid.addWidget(self.combo_superficie, 0, 1)

        # Curvatura Superficie
        lbl_curv = QLabel("Radio de Curvatura (mm):")
        lbl_curv.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_curvatura = QDoubleSpinBox()
        self.spin_curvatura.setRange(10.0, 100.0)
        self.spin_curvatura.setSingleStep(5.0)
        self.spin_curvatura.setValue(25.0)
        self.spin_curvatura.setSuffix(" mm")
        self.spin_curvatura.valueChanged.connect(self._actualizar_grafico)
        grid.addWidget(lbl_curv, 1, 0)
        grid.addWidget(self.spin_curvatura, 1, 1)

        # Profundidad de Análisis
        lbl_prof = QLabel("Profundidad de Análisis (z):")
        lbl_prof.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_profundidad = QDoubleSpinBox()
        self.spin_profundidad.setRange(0.5, 3.0)
        self.spin_profundidad.setSingleStep(0.2)
        self.spin_profundidad.setValue(2.0)
        self.spin_profundidad.setSuffix(" cm")
        self.spin_profundidad.valueChanged.connect(self._actualizar_grafico)
        grid.addWidget(lbl_prof, 2, 0)
        grid.addWidget(self.spin_profundidad, 2, 1)

        # Información de Orientación Normal
        lbl_modo = QLabel("Modo de Emisión:")
        lbl_modo.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        lbl_modo_val = QLabel("Normal Fija (0.0° - Contacto Total)")
        lbl_modo_val.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_modo_val.setStyleSheet(f"color: {Colores.CELESTE_ACENTO};")
        grid.addWidget(lbl_modo, 3, 0)
        grid.addWidget(lbl_modo_val, 3, 1)

        l_ctrl.addLayout(grid)
        l_ctrl.addStretch()

        btn_guardar = BotonPrimario("Guardar Geometría")
        btn_guardar.clicked.connect(self._guardar_cambios)
        l_ctrl.addWidget(btn_guardar)

        fila_central.addWidget(tarjeta_ctrl, stretch=1)

        # Lienzo Gráfico Matplotlib 2D
        tarjeta_canvas = TarjetaContenedor()
        l_can = QVBoxLayout(tarjeta_canvas)
        l_can.setContentsMargins(16, 14, 16, 14)
        l_can.setSpacing(8)

        t_can = QLabel("ESQUEMA 2D DE CONTACTO Y ACOPLAMIENTO TISULAR")
        t_can.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_can.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_can.addWidget(t_can)

        self.figura = Figure(figsize=(6.2, 4.4), dpi=100, facecolor="#ffffff")
        self.canvas = FigureCanvasQTAgg(self.figura)
        l_can.addWidget(self.canvas)

        fila_central.addWidget(tarjeta_canvas, stretch=2)
        layout.addLayout(fila_central)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

        self._actualizar_grafico()

    def _actualizar_grafico(self):
        """Dibuja el esquema 2D del aplicador normal sobre la superficie anatómica."""
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.set_facecolor("#ffffff")
        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")
        ax.tick_params(colors="#475569", labelsize=8)
        ax.grid(True, linestyle=":", alpha=0.4, color="#cbd5e1")

        tipo_sup = self.combo_superficie.currentText()
        graficar_esquema_tisular(
            ax=ax,
            tipo_superficie=tipo_sup,
            profundidad_focal_mm=10.0,
            tipo_quemadura="3er Grado",
            estilo_oscuro=False
        )

        self.figura.tight_layout()
        self.canvas.draw()

    def cargar_datos(self, geo: ConfiguracionGeometria):
        self.geometria = geo
        self.combo_superficie.setCurrentText(geo.tipo_superficie)
        self.spin_curvatura.setValue(geo.radio_curvatura_superficie_mm)
        self.spin_profundidad.setValue(geo.profundidad_analisis_cm)
        self._actualizar_grafico()

    def _guardar_cambios(self):
        self.geometria.tipo_superficie = self.combo_superficie.currentText()
        self.geometria.radio_curvatura_superficie_mm = self.spin_curvatura.value()
        self.geometria.profundidad_analisis_cm = self.spin_profundidad.value()
        self.geometria.contacto_acustico_garantizado = True

        self.geometria_modificada.emit(self.geometria)
        QMessageBox.information(
            self,
            "Geometría Actualizada",
            "La configuración anatómica y de contacto cutáneo ha sido guardada exitosamente."
        )
