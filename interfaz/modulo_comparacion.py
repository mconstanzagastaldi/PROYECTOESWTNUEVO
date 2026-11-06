"""
================================================================================
MÓDULO 9: COMPARACIÓN DE CONFIGURACIONES Y ESCENARIOS
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Permite contrastar dos configuraciones del aplicador (superficie plana vs curva,
orientaciones angulares, dosimetría y tipo de quemadura).
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from interfaz.componentes import (
    Colores, TarjetaContenedor, BadgeEstado
)
from modelos.configuracion import ConfiguracionGlobal


class ModuloComparacion(QWidget):
    """Herramienta de análisis comparativo entre escenarios clínicos."""

    def __init__(self, config_actual: ConfiguracionGlobal = None, parent=None):
        super().__init__(parent)
        self.config_a = config_actual or ConfiguracionGlobal()
        # Generar una configuración alternativa B para comparación inmediata
        self.config_b = ConfiguracionGlobal()
        self.config_b.nombre_configuracion = "Escenario_Comparativo_B"
        self.config_b.geometria.tipo_superficie = "Plana (Tronco / Muslo)"
        self.config_b.aplicador.cabezal.angulo_orientacion_deg = 15.0
        self.config_b.parametros.efd_nominal_mj_mm2 = 0.150

        self._inicializar_ui()

    def _inicializar_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(20)

        # ----------------------------------------------------------------------
        # 1. ENCABEZADO
        # ----------------------------------------------------------------------
        header = TarjetaContenedor()
        l_head = QVBoxLayout(header)
        l_head.setContentsMargins(22, 18, 22, 18)
        l_head.setSpacing(6)

        badge = BadgeEstado("ANÁLISIS COMPARATIVO", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Comparación de Escenarios de Aplicación y Parámetros")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Permite contrastar el comportamiento del equipo ante diferentes condiciones de tratamiento: "
            "superficie plana frente a curva (articulación), variaciones angulares del cabezal y dosimetría."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. SELECTORES DE ESCENARIOS
        # ----------------------------------------------------------------------
        tarjeta_sel = TarjetaContenedor()
        l_s = QHBoxLayout(tarjeta_sel)
        l_s.setContentsMargins(20, 14, 20, 14)
        l_s.setSpacing(18)

        # Escenario A
        l_a = QVBoxLayout()
        lbl_a = QLabel("CONFIGURACIÓN A (ACTIVA):")
        lbl_a.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_a.setStyleSheet(f"color: {Colores.CELESTE_ACENTO};")
        self.combo_escenario_a = QComboBox()
        self.combo_escenario_a.addItems(["Configuración Actual (Sesión)", "Nominal (0° • Curva • 0.10 mJ/mm²)"])
        l_a.addWidget(lbl_a)
        l_a.addWidget(self.combo_escenario_a)
        l_s.addLayout(l_a)

        # Escenario B
        l_b = QVBoxLayout()
        lbl_b = QLabel("CONFIGURACIÓN B (CONTRASTE):")
        lbl_b.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_b.setStyleSheet(f"color: #8b5cf6;")
        self.combo_escenario_b = QComboBox()
        self.combo_escenario_b.addItems([
            "Escenario 1: Superficie Plana (Tronco)",
            "Escenario 2: Superficie Curva (Mano/Dedos)",
            "Escenario 3: EFD Elevada (0.20 mJ/mm²)",
            "Escenario 4: Foco Profundo (2.0 cm)"
        ])
        self.combo_escenario_b.currentIndexChanged.connect(self._cambiar_escenario_b)
        l_b.addWidget(lbl_b)
        l_b.addWidget(self.combo_escenario_b)
        l_s.addLayout(l_b)

        layout.addWidget(tarjeta_sel)

        # ----------------------------------------------------------------------
        # 3. TABLA COMPARATIVA PARALELA
        # ----------------------------------------------------------------------
        tarjeta_comp = TarjetaContenedor()
        l_c = QVBoxLayout(tarjeta_comp)
        l_c.setContentsMargins(20, 18, 20, 18)
        l_c.setSpacing(12)

        t_c = QLabel("TABLA COMPARATIVA DE PARÁMETROS CLÍNICOS Y GEOMÉTRICOS")
        t_c.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_c.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_c.addWidget(t_c)

        self.tabla_comp = QTableWidget()
        self.tabla_comp.setColumnCount(3)
        self.tabla_comp.setHorizontalHeaderLabels([
            "Parámetro Evaluado", "Configuración A (Activa)", "Configuración B (Contraste)"
        ])
        self.tabla_comp.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_comp.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_comp.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_comp.setStyleSheet(f"""
            QTableWidget {{
                background-color: #ffffff;
                gridline-color: {Colores.BORDE_TARJETA};
                border: 1px solid {Colores.BORDE_TARJETA};
                border-radius: 6px;
            }}
            QHeaderView::section {{
                background-color: {Colores.AZUL_SECUNDARIO};
                color: #ffffff;
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
        """)
        l_c.addWidget(self.tabla_comp)
        layout.addWidget(tarjeta_comp)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

        self._actualizar_tabla()

    def _cambiar_escenario_b(self, idx: int):
        if idx == 0:
            self.config_b.geometria.tipo_superficie = "Plana (Tronco / Muslo)"
            self.config_b.parametros.efd_nominal_mj_mm2 = 0.100
            self.config_b.parametros.profundidad_focal_objetivo_cm = 1.0
        elif idx == 1:
            self.config_b.geometria.tipo_superficie = "Curva (Articulación / Mano)"
            self.config_b.parametros.efd_nominal_mj_mm2 = 0.100
            self.config_b.parametros.profundidad_focal_objetivo_cm = 1.0
        elif idx == 2:
            self.config_b.parametros.efd_nominal_mj_mm2 = 0.200
        elif idx == 3:
            self.config_b.parametros.profundidad_focal_objetivo_cm = 2.0

        self._actualizar_tabla()

    def _actualizar_tabla(self):
        a = self.config_a
        b = self.config_b

        parametros_comp = [
            ("Geometría de Superficie", a.geometria.tipo_superficie, b.geometria.tipo_superficie),
            ("Orientación y Contacto", "Normal Fija (0.0°)", "Normal Fija (0.0°)"),
            ("Densidad de Flujo de Energía (EFD)", f"{a.parametros.efd_nominal_mj_mm2:.3f} mJ/mm²", f"{b.parametros.efd_nominal_mj_mm2:.3f} mJ/mm²"),
            ("Frecuencia de Repetición (PRF)", f"{a.parametros.frecuencia_repeticion_hz:.1f} Hz", f"{b.parametros.frecuencia_repeticion_hz:.1f} Hz"),
            ("Profundidad Focal Objetivo", f"{a.parametros.profundidad_focal_objetivo_cm:.2f} cm", f"{b.parametros.profundidad_focal_objetivo_cm:.2f} cm"),
            ("Densidad de Dosificación", f"{a.parametros.densidad_disparos_pcm2:.0f} pulsos/cm²", f"{b.parametros.densidad_disparos_pcm2:.0f} pulsos/cm²"),
            ("Disparos Totales Programados", f"{a.parametros.numero_pulsos_total} pulsos", f"{b.parametros.numero_pulsos_total} pulsos"),
            ("Duración Estimada de Sesión", f"{a.parametros.tiempo_tratamiento_minutos:.2f} min", f"{b.parametros.tiempo_tratamiento_minutos:.2f} min"),
            ("Estratos Tisulares Modelados", f"{len(a.tejidos)} estratos", f"{len(b.tejidos)} estratos"),
            ("Consistencia Bioacústica", "Modelo Computacional Acoplado", "Modelo Computacional Acoplado")
        ]

        self.tabla_comp.setRowCount(len(parametros_comp))
        for row, (param, val_a, val_b) in enumerate(parametros_comp):
            it_p = QTableWidgetItem(param)
            it_a = QTableWidgetItem(str(val_a))
            it_b = QTableWidgetItem(str(val_b))

            it_a.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_b.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Destacar visualmente diferencias
            if str(val_a) != str(val_b):
                it_b.setForeground(Qt.GlobalColor.darkBlue)
                it_b.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))

            self.tabla_comp.setItem(row, 0, it_p)
            self.tabla_comp.setItem(row, 1, it_a)
            self.tabla_comp.setItem(row, 2, it_b)
