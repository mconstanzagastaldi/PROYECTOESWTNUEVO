"""
================================================================================
MÓDULO 2: CONFIGURACIÓN DEL APLICADOR
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Permite definir las características generales del aplicador piezoeléctrico:
- Emisión normal fija (sin ángulo ni mecanismos de articulación móvil).
- Adaptabilidad a superficies anatómicas irregulares (articulaciones/manos)
  y planas mediante diseño ergonómico compacto (chasis <= 40 mm) y gel conformable.
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QScrollArea, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from interfaz.componentes import (
    Colores, TarjetaContenedor, BotonPrimario, BadgeEstado
)
from modelos.aplicador import ConfiguracionAplicador


class ModuloAplicador(QWidget):
    """Pantalla interactiva de configuración del aplicador piezoeléctrico."""

    configuracion_modificada = Signal(ConfiguracionAplicador)

    def __init__(self, aplicador: ConfiguracionAplicador = None, parent=None):
        super().__init__(parent)
        self.aplicador = aplicador or ConfiguracionAplicador()
        self._inicializar_ui()
        self.cargar_datos(self.aplicador)

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
        # 1. ENCABEZADO DEL MÓDULO
        # ----------------------------------------------------------------------
        header = TarjetaContenedor()
        l_head = QVBoxLayout(header)
        l_head.setContentsMargins(22, 18, 22, 18)
        l_head.setSpacing(6)

        badge = BadgeEstado("DISEÑO Y ESPECIFICACIÓN DEL APLICADOR", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Configuración del Aplicador Piezoeléctrico")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Definición técnica del equipo: transductor piezoeléctrico focalizado sobre casquete cóncavo rígido. "
            "El aplicador opera con orientación normal fija (0°), adaptándose a superficies anatómicas curvas e "
            "irregulares (como articulaciones de manos y dedos) o planas mediante acoplamiento acústico conformado."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. CARACTERÍSTICAS MECÁNICAS Y ACÚSTICAS
        # ----------------------------------------------------------------------
        tarjeta_params = TarjetaContenedor()
        l_params = QVBoxLayout(tarjeta_params)
        l_params.setContentsMargins(24, 20, 24, 20)
        l_params.setSpacing(16)

        t_sec1 = QLabel("1. ESPECIFICACIONES CONSTRUCTIVAS DEL CABEZAL")
        t_sec1.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_sec1.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_params.addWidget(t_sec1)

        grid1 = QGridLayout()
        grid1.setSpacing(14)

        # Tecnología de Generación
        lbl_gen = QLabel("Tecnología de Generación:")
        lbl_gen.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.combo_generacion = QComboBox()
        self.combo_generacion.addItems(["Piezoeléctrica (Anteproyecto UNER)"])
        self.combo_generacion.setStyleSheet("padding: 6px;")
        grid1.addWidget(lbl_gen, 0, 0)
        grid1.addWidget(self.combo_generacion, 0, 1)

        # Geometría del Cabezal
        lbl_cab = QLabel("Geometría del Cabezal:")
        lbl_cab.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.combo_cabezal = QComboBox()
        self.combo_cabezal.addItems(["Casquete Cóncavo Rígido (Focalización Acústica)"])
        self.combo_cabezal.setStyleSheet("padding: 6px;")
        grid1.addWidget(lbl_cab, 1, 0)
        grid1.addWidget(self.combo_cabezal, 1, 1)

        # Sistema de Acoplamiento Acústico
        lbl_acople = QLabel("Sistema de Acoplamiento Acústico:")
        lbl_acople.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.combo_acople = QComboBox()
        self.combo_acople.addItems([
            "Gel Acústico Adaptable (Z ≈ 1.50 MRayl)",
            "Almohadilla de Gel Conformable (Z ≈ 1.48 MRayl)"
        ])
        self.combo_acople.setStyleSheet("padding: 6px;")
        grid1.addWidget(lbl_acople, 2, 0)
        grid1.addWidget(self.combo_acople, 2, 1)

        # Distanciador Acústico Intercambiable (Tarea 4.1)
        lbl_dist = QLabel("Distanciador Acústico Intercambiable:")
        lbl_dist.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.combo_distanciador = QComboBox()
        self.combo_distanciador.addItems([
            "D15: 15 mm (Nominal - Foco en tejido a 13.5 mm) [Recomendado]",
            "D10: 10 mm (Foco en tejido a 18.5 mm)",
            "D20: 20 mm (Foco en tejido a 8.5 mm)",
            "D0: Sin distanciador (Contacto directo - Foco natural a 28.5 mm)"
        ])
        self.combo_distanciador.setStyleSheet("padding: 6px;")
        grid1.addWidget(lbl_dist, 3, 0)
        grid1.addWidget(self.combo_distanciador, 3, 1)

        l_params.addLayout(grid1)

        # Divisor
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"background-color: {Colores.BORDE_TARJETA}; max-height: 1px;")
        l_params.addWidget(div)

        # Orientación y Adaptabilidad
        t_sec2 = QLabel("2. ORIENTACIÓN Y ADAPTABILIDAD ANATÓMICA")
        t_sec2.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_sec2.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_params.addWidget(t_sec2)

        lbl_orientacion_desc = QLabel(
            "• Modo de Emisión: Orientación normal fija (0.0° - perpendicular a la piel).\n"
            "• Sin mecanismos articulados ni piezas móviles: se garantiza la máxima durabilidad y estabilidad acústica.\n"
            "• Adaptabilidad tisular: Lograda mediante el diámetro ergonómico wand (Ø ≤ 40 mm) y la deformabilidad del gel."
        )
        lbl_orientacion_desc.setFont(QFont("Segoe UI", 8))
        lbl_orientacion_desc.setStyleSheet(f"color: {Colores.TEXTO_NORMAL}; background-color: {Colores.FONDO_VENTANA}; padding: 10px; border-radius: 6px;")
        l_params.addWidget(lbl_orientacion_desc)

        layout.addWidget(tarjeta_params)

        # ----------------------------------------------------------------------
        # 3. ESPECIFICACIONES RESERVADAS PARA FORMULACIÓN FÍSICA
        # ----------------------------------------------------------------------
        tarjeta_fisica = TarjetaContenedor()
        l_fis = QVBoxLayout(tarjeta_fisica)
        l_fis.setContentsMargins(24, 20, 24, 20)
        l_fis.setSpacing(12)

        t_fis = QLabel("3. REGISTRO DE COMPONENTES DEL EQUIPO (INTEGRACIÓN EN CURSO)")
        t_fis.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_fis.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_fis.addWidget(t_fis)

        grid_hw = QGridLayout()
        grid_hw.setSpacing(10)

        hw_items = [
            ("Radio de curvatura del casquete:", "30.0 mm (Geometría seleccionada Tarea 4.1)"),
            ("Diámetro de apertura acústica:", "30.0 mm (F-number = 1.00)"),
            ("Diámetro exterior de carcasa:", "38.0 mm (Cumple límite estricto Ø ≤ 40 mm, RF8)"),
            ("Disposición piezoeléctrica:", "Monoelemento cóncavo autofocalizante"),
            ("Material de los transductores:", "Cerámica PZT-4 / PZT-8 de alta potencia mecánica"),
            ("Frecuencia nominal:", "1.0 a 1.5 MHz"),
            ("Distanciadores intercambiables:", "Set D10, D15 (nominal) y D20")
        ]

        for i, (k, v) in enumerate(hw_items):
            lk = QLabel(f"• {k}")
            lk.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
            lk.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
            lv = QLabel(v)
            lv.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
            lv.setStyleSheet(f"color: {Colores.CELESTE_ACENTO};")
            grid_hw.addWidget(lk, i, 0)
            grid_hw.addWidget(lv, i, 1)

        l_fis.addLayout(grid_hw)
        layout.addWidget(tarjeta_fisica)

        # Botón Guardar / Aplicar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_guardar = BotonPrimario("Guardar Configuración del Aplicador")
        self.btn_guardar.clicked.connect(self._guardar_cambios)
        btn_layout.addWidget(self.btn_guardar)
        layout.addLayout(btn_layout)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

    def cargar_datos(self, app: ConfiguracionAplicador):
        self.aplicador = app
        self.combo_acople.setCurrentText(app.sistema_acoplamiento)
        dist_val = getattr(app, "distanciador_seleccionado_mm", 15.0)
        if dist_val == 10.0:
            self.combo_distanciador.setCurrentIndex(1)
        elif dist_val == 20.0:
            self.combo_distanciador.setCurrentIndex(2)
        elif dist_val == 0.0:
            self.combo_distanciador.setCurrentIndex(3)
        else:
            self.combo_distanciador.setCurrentIndex(0)

    def _guardar_cambios(self):
        self.aplicador.sistema_acoplamiento = self.combo_acople.currentText()
        idx = self.combo_distanciador.currentIndex()
        dist_map = {0: 15.0, 1: 10.0, 2: 20.0, 3: 0.0}
        self.aplicador.distanciador_seleccionado_mm = dist_map.get(idx, 15.0)
        self.configuracion_modificada.emit(self.aplicador)
        QMessageBox.information(
            self,
            "Configuración Guardada",
            "La configuración del aplicador ha sido actualizada exitosamente."
        )
