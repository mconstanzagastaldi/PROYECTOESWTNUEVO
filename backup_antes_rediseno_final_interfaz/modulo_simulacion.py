"""
================================================================================
MÓDULO 6: CONFIGURACIÓN DEL MODELO DE SIMULACIÓN
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Permite configurar el dominio numérico cartesiano 2D (x, z), resoluciones espaciales,
paso temporal dt, tiempo total de análisis y verificación de la estabilidad CFL.
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QScrollArea, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from interfaz.componentes import (
    Colores, TarjetaContenedor, TarjetaEstado, BotonPrimario, BadgeEstado
)
from modelos.configuracion import ParametrosMallaSimulacion
from simulacion.malla import Malla2D


class ModuloSimulacion(QWidget):
    """Pantalla interactiva de discretización y malla numérica."""

    malla_modificada = Signal(ParametrosMallaSimulacion)

    def __init__(self, malla_params: ParametrosMallaSimulacion = None, parent=None):
        super().__init__(parent)
        self.malla_params = malla_params or ParametrosMallaSimulacion()
        self._inicializar_ui()
        self.cargar_datos(self.malla_params)

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

        badge = BadgeEstado("MODELO NUMÉRICO 2D", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Parámetros del Dominio Computacional y Malla")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Configure la discretización espacio-temporal del dominio. La resolución debe ser suficiente "
            "para representar frentes de onda impulsivos (tiempos de subida de 5 a 10 ns) garantizando "
            "la condición de estabilidad numérica de Courant-Friedrichs-Lewy (CFL < 1.0)."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. CONTROLES DE LA MALLA NUMÉRICA
        # ----------------------------------------------------------------------
        tarjeta_malla = TarjetaContenedor()
        l_malla = QVBoxLayout(tarjeta_malla)
        l_malla.setContentsMargins(24, 20, 24, 20)
        l_malla.setSpacing(18)

        t_malla = QLabel("DISCRETIZACIÓN ESPACIAL Y TEMPORAL")
        t_malla.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_malla.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_malla.addWidget(t_malla)

        grid = QGridLayout()
        grid.setSpacing(14)

        # Dimensiones Dominio
        lbl_ancho = QLabel("Ancho Lateral del Dominio (x):")
        lbl_ancho.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_ancho = QDoubleSpinBox()
        self.spin_ancho.setRange(1.0, 10.0)
        self.spin_ancho.setSingleStep(0.5)
        self.spin_ancho.setValue(2.0)
        self.spin_ancho.setSuffix(" cm")
        self.spin_ancho.valueChanged.connect(self._recalcular_cfl)
        grid.addWidget(lbl_ancho, 0, 0)
        grid.addWidget(self.spin_ancho, 0, 1)

        lbl_prof = QLabel("Profundidad del Dominio (z):")
        lbl_prof.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_prof = QDoubleSpinBox()
        self.spin_prof.setRange(1.0, 10.0)
        self.spin_prof.setSingleStep(0.5)
        self.spin_prof.setValue(2.0)
        self.spin_prof.setSuffix(" cm")
        self.spin_prof.valueChanged.connect(self._recalcular_cfl)
        grid.addWidget(lbl_prof, 0, 2)
        grid.addWidget(self.spin_prof, 0, 3)

        # Resoluciones dx, dz
        lbl_dx = QLabel("Paso Espacial dx:")
        lbl_dx.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_dx = QDoubleSpinBox()
        self.spin_dx.setRange(20.0, 250.0)
        self.spin_dx.setSingleStep(10.0)
        self.spin_dx.setValue(80.0)
        self.spin_dx.setSuffix(" μm")
        self.spin_dx.valueChanged.connect(self._recalcular_cfl)
        grid.addWidget(lbl_dx, 1, 0)
        grid.addWidget(self.spin_dx, 1, 1)

        lbl_dz = QLabel("Paso Espacial dz:")
        lbl_dz.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_dz = QDoubleSpinBox()
        self.spin_dz.setRange(20.0, 250.0)
        self.spin_dz.setSingleStep(10.0)
        self.spin_dz.setValue(80.0)
        self.spin_dz.setSuffix(" μm")
        self.spin_dz.valueChanged.connect(self._recalcular_cfl)
        grid.addWidget(lbl_dz, 1, 2)
        grid.addWidget(self.spin_dz, 1, 3)

        # Paso temporal y tiempo total
        lbl_dt = QLabel("Paso Temporal dt:")
        lbl_dt.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_dt = QDoubleSpinBox()
        self.spin_dt.setRange(1.0, 50.0)
        self.spin_dt.setSingleStep(1.0)
        self.spin_dt.setValue(8.0)
        self.spin_dt.setSuffix(" ns")
        self.spin_dt.valueChanged.connect(self._recalcular_cfl)
        grid.addWidget(lbl_dt, 2, 0)
        grid.addWidget(self.spin_dt, 2, 1)

        lbl_ttotal = QLabel("Tiempo Total de Análisis:")
        lbl_ttotal.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_ttotal = QDoubleSpinBox()
        self.spin_ttotal.setRange(2.0, 50.0)
        self.spin_ttotal.setSingleStep(1.0)
        self.spin_ttotal.setValue(14.5)
        self.spin_ttotal.setSuffix(" μs")
        self.spin_ttotal.valueChanged.connect(self._recalcular_cfl)
        grid.addWidget(lbl_ttotal, 2, 2)
        grid.addWidget(self.spin_ttotal, 2, 3)

        # Medio y Frontera
        lbl_medio = QLabel("Tipo de Medio Tisular:")
        lbl_medio.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.combo_medio = QComboBox()
        self.combo_medio.addItems(["Heterogéneo (Estratificado por Capas)", "Homogéneo Equivalente"])
        grid.addWidget(lbl_medio, 3, 0)
        grid.addWidget(self.combo_medio, 3, 1)

        lbl_borde = QLabel("Condición de Frontera:")
        lbl_borde.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.combo_borde = QComboBox()
        self.combo_borde.addItems(["Absorbente (Sponge ABC)", "Perfectamente Adaptada (PML)", "Rígida Reflectante"])
        grid.addWidget(lbl_borde, 3, 2)
        grid.addWidget(self.combo_borde, 3, 3)

        l_malla.addLayout(grid)
        layout.addWidget(tarjeta_malla)

        # ----------------------------------------------------------------------
        # 3. ESTABILIDAD NUMÉRICA (CFL) Y NODOS COMPUTACIONALES
        # ----------------------------------------------------------------------
        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(16)

        self.card_nodos = TarjetaEstado(
            titulo="Dimensión de la Malla",
            valor="251 x 251 nodos",
            subtitulo="Total: ~63.000 puntos de cálculo",
            color_acento=Colores.CELESTE_ACENTO
        )
        layout_cards.addWidget(self.card_nodos)

        self.card_pasos_t = TarjetaEstado(
            titulo="Pasos Temporales",
            valor="1812 iteraciones",
            subtitulo="dt = 8.0 ns • t_total = 14.5 μs",
            color_acento="#8b5cf6"
        )
        layout_cards.addWidget(self.card_pasos_t)

        self.card_cfl = TarjetaEstado(
            titulo="Criterio de Estabilidad CFL",
            valor="CFL = 0.247 (ESTABLE)",
            subtitulo="Cumple condición CFL < 1.0",
            color_acento=Colores.ESTADO_OK
        )
        layout_cards.addWidget(self.card_cfl)

        layout.addLayout(layout_cards)

        # Botón Guardar
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_guardar = BotonPrimario("Guardar Configuración Numérica")
        self.btn_guardar.clicked.connect(self._guardar_cambios)
        btn_box.addWidget(self.btn_guardar)
        layout.addLayout(btn_box)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

        self._recalcular_cfl()

    def _recalcular_cfl(self):
        temp_params = ParametrosMallaSimulacion(
            ancho_dominio_cm=self.spin_ancho.value(),
            profundidad_dominio_cm=self.spin_prof.value(),
            resolucion_dx_um=self.spin_dx.value(),
            resolucion_dz_um=self.spin_dz.value(),
            paso_temporal_dt_ns=self.spin_dt.value(),
            tiempo_total_us=self.spin_ttotal.value()
        )
        m = Malla2D(temp_params)
        cfl = m.calcular_cfl(c_max_m_s=1750.0) # Velocidad máxima en cicatriz fibrótica

        self.card_nodos.actualizar(
            f"{m.Nz} x {m.Nx} nodos",
            f"Total: {(m.Nz * m.Nx):,} puntos de cálculo".replace(",", ".")
        )
        self.card_pasos_t.actualizar(
            f"{m.pasos_tiempo} pasos",
            f"dt = {temp_params.paso_temporal_dt_ns:.1f} ns • {temp_params.tiempo_total_us:.1f} μs"
        )

        if cfl < 0.5:
            self.card_cfl.actualizar(f"CFL = {cfl:.3f} (ÓPTIMO)", "Condición CFL < 1.0 cumplida con holgura")
            self.card_cfl.setStyleSheet(f"""
                TarjetaEstado {{
                    background-color: #ffffff;
                    border: 1px solid {Colores.BORDE_TARJETA};
                    border-left: 5px solid {Colores.ESTADO_OK};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
        elif cfl < 1.0:
            self.card_cfl.actualizar(f"CFL = {cfl:.3f} (ESTABLE)", "Estable pero cercano al umbral límite")
            self.card_cfl.setStyleSheet(f"""
                TarjetaEstado {{
                    background-color: #ffffff;
                    border: 1px solid {Colores.BORDE_TARJETA};
                    border-left: 5px solid {Colores.ESTADO_ALERTA};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
        else:
            self.card_cfl.actualizar(f"CFL = {cfl:.3f} (INESTABLE)", "¡Riesgo de divergencia numérica! Reduzca dt.")
            self.card_cfl.setStyleSheet(f"""
                TarjetaEstado {{
                    background-color: #ffffff;
                    border: 1px solid {Colores.BORDE_TARJETA};
                    border-left: 5px solid #dc2626;
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)

    def cargar_datos(self, m: ParametrosMallaSimulacion):
        self.malla_params = m
        self.spin_ancho.setValue(m.ancho_dominio_cm)
        self.spin_prof.setValue(m.profundidad_dominio_cm)
        self.spin_dx.setValue(m.resolucion_dx_um)
        self.spin_dz.setValue(m.resolucion_dz_um)
        self.spin_dt.setValue(m.paso_temporal_dt_ns)
        self.spin_ttotal.setValue(m.tiempo_total_us)
        self.combo_medio.setCurrentText(m.tipo_medio)
        self.combo_borde.setCurrentText(m.condicion_frontera)
        self._recalcular_cfl()

    def _guardar_cambios(self):
        self.malla_params.ancho_dominio_cm = self.spin_ancho.value()
        self.malla_params.profundidad_dominio_cm = self.spin_prof.value()
        self.malla_params.resolucion_dx_um = self.spin_dx.value()
        self.malla_params.resolucion_dz_um = self.spin_dz.value()
        self.malla_params.paso_temporal_dt_ns = self.spin_dt.value()
        self.malla_params.tiempo_total_us = self.spin_ttotal.value()
        self.malla_params.tipo_medio = self.combo_medio.currentText()
        self.malla_params.condicion_frontera = self.combo_borde.currentText()

        m = Malla2D(self.malla_params)
        cfl = m.calcular_cfl()
        if cfl >= 1.0:
            QMessageBox.critical(
                self,
                "Inestabilidad Numérica",
                f"El paso temporal dt seleccionado produce CFL = {cfl:.3f} >= 1.0.\n"
                "Reduzca dt antes de guardar."
            )
            return

        self.malla_modificada.emit(self.malla_params)
        QMessageBox.information(
            self,
            "Malla Actualizada",
            f"Parámetros numéricos guardados exitosamente.\nFactor de estabilidad: CFL = {cfl:.3f}"
        )
