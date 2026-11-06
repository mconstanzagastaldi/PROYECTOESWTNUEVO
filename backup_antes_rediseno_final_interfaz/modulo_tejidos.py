"""
================================================================================
MÓDULO 5: PROPIEDADES DE LOS TEJIDOS
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Permite gestionar la estratificación anatómica y las propiedades acústicas:
espesor, densidad, velocidad del sonido, impedancia y coeficiente de atenuación.
================================================================================
"""

from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QFrame, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from interfaz.componentes import (
    Colores, TarjetaContenedor, BotonPrimario, BotonSecundario, BadgeEstado
)
from modelos.tejido import CapaTejido, obtener_capas_predeterminadas_literatura
from servicios.validador import ValidadorClinico


class DialogoEditarCapa(QDialog):
    """Ventana modal para agregar o editar un estrato tisular individual."""

    def __init__(self, capa: CapaTejido = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Definición de Estrato Tisular")
        self.resize(380, 320)
        self.capa = capa

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)

        self.edit_nombre = QLineEdit(capa.nombre if capa else "Nuevo Estrato")
        form.addRow("Nombre del Tejido:", self.edit_nombre)

        self.spin_espesor = QDoubleSpinBox()
        self.spin_espesor.setRange(0.1, 50.0)
        self.spin_espesor.setSingleStep(0.5)
        self.spin_espesor.setValue(capa.espesor_mm if capa else 2.0)
        self.spin_espesor.setSuffix(" mm")
        form.addRow("Espesor:", self.spin_espesor)

        self.spin_densidad = QDoubleSpinBox()
        self.spin_densidad.setRange(500.0, 3000.0)
        self.spin_densidad.setSingleStep(50.0)
        self.spin_densidad.setValue(capa.densidad_kg_m3 if capa else 1050.0)
        self.spin_densidad.setSuffix(" kg/m³")
        self.spin_densidad.valueChanged.connect(self._recalcular_z)
        form.addRow("Densidad (ρ):", self.spin_densidad)

        self.spin_velocidad = QDoubleSpinBox()
        self.spin_velocidad.setRange(1000.0, 3000.0)
        self.spin_velocidad.setSingleStep(25.0)
        self.spin_velocidad.setValue(capa.velocidad_m_s if capa else 1580.0)
        self.spin_velocidad.setSuffix(" m/s")
        self.spin_velocidad.valueChanged.connect(self._recalcular_z)
        form.addRow("Velocidad Sonido (c):", self.spin_velocidad)

        self.lbl_impedancia = QLabel(f"{(capa.impedancia_rayl/1e6):.2f} MRayl" if capa else "1.66 MRayl")
        self.lbl_impedancia.setStyleSheet(f"font-weight: bold; color: {Colores.CELESTE_ACENTO};")
        form.addRow("Impedancia (Z = ρ·c):", self.lbl_impedancia)

        self.spin_atenuacion = QDoubleSpinBox()
        self.spin_atenuacion.setRange(0.001, 10.0)
        self.spin_atenuacion.setSingleStep(0.1)
        self.spin_atenuacion.setDecimals(3)
        self.spin_atenuacion.setValue(capa.atenuacion_db_cm_mhz if capa else 0.700)
        self.spin_atenuacion.setSuffix(" dB/cm·MHz")
        form.addRow("Atenuación (α):", self.spin_atenuacion)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _recalcular_z(self):
        rho = self.spin_densidad.value()
        c = self.spin_velocidad.value()
        z_mrayl = (rho * c) / 1.0e6
        self.lbl_impedancia.setText(f"{z_mrayl:.2f} MRayl")

    def obtener_capa(self) -> CapaTejido:
        rho = self.spin_densidad.value()
        c = self.spin_velocidad.value()
        return CapaTejido(
            nombre=self.edit_nombre.text().strip() or "Estrato Tisular",
            espesor_mm=self.spin_espesor.value(),
            densidad_kg_m3=rho,
            velocidad_m_s=c,
            impedancia_rayl=rho * c,
            atenuacion_db_cm_mhz=self.spin_atenuacion.value(),
            es_editable=True
        )


class ModuloTejidos(QWidget):
    """Gestor de capas tisulares y propiedades bioacústicas de literatura."""

    tejidos_modificados = Signal(list)

    def __init__(self, capas: List[CapaTejido] = None, parent=None):
        super().__init__(parent)
        self.capas = capas or obtener_capas_predeterminadas_literatura()
        self._inicializar_ui()
        self.cargar_datos(self.capas)

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

        badge = BadgeEstado("MEDIO HETEROGÉNEO TISULAR", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Propiedades de los Estratos Tisulares y Acoplamiento")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Configure las propiedades acústicas y mecánicas de cada capa biológica. Los valores predeterminados "
            "se sustentan estrictamente en mediciones de literatura científica (Duck 1990; IT'IS Foundation) "
            "para garantizar la validez del modelo sin inventar parámetros."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. TABLA DE ESTRATOS TISULARES
        # ----------------------------------------------------------------------
        tarjeta_tabla = TarjetaContenedor()
        l_tab = QVBoxLayout(tarjeta_tabla)
        l_tab.setContentsMargins(20, 18, 20, 18)
        l_tab.setSpacing(14)

        t_tab = QLabel("ESTRATIFICACIÓN ANATÓMICA EN PROFUNDIDAD (ORDEN DE ENTRADA)")
        t_tab.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_tab.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_tab.addWidget(t_tab)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Estrato / Capa", "Espesor [mm]", "Densidad [kg/m³]",
            "Velocidad c [m/s]", "Impedancia Z [MRayl]", "Atenuación [dB/cm·MHz]"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 6):
            self.tabla.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.setStyleSheet(f"""
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
        l_tab.addWidget(self.tabla)

        # Botonera de Gestión de Capas
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_agregar = BotonSecundario("➕ Agregar Estrato")
        self.btn_agregar.clicked.connect(self._agregar_capa)
        btn_layout.addWidget(self.btn_agregar)

        self.btn_editar = BotonSecundario("✏️ Modificar Seleccionado")
        self.btn_editar.clicked.connect(self._editar_capa)
        btn_layout.addWidget(self.btn_editar)

        self.btn_eliminar = BotonSecundario("🗑️ Eliminar Estrato")
        self.btn_eliminar.clicked.connect(self._eliminar_capa)
        btn_layout.addWidget(self.btn_eliminar)

        btn_layout.addStretch()

        self.btn_restablecer = BotonSecundario("Restablecer Valores Bibliográficos")
        self.btn_restablecer.clicked.connect(self._restablecer_literatura)
        btn_layout.addWidget(self.btn_restablecer)

        l_tab.addLayout(btn_layout)
        layout.addWidget(tarjeta_tabla)

        # Botón Guardar Cambios
        btn_save_box = QHBoxLayout()
        btn_save_box.addStretch()
        self.btn_guardar = BotonPrimario("Guardar y Validar Estratos Tisulares")
        self.btn_guardar.clicked.connect(self._guardar_cambios)
        btn_save_box.addWidget(self.btn_guardar)
        layout.addLayout(btn_save_box)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

    def cargar_datos(self, capas: List[CapaTejido]):
        self.capas = capas
        self.tabla.setRowCount(len(capas))

        for row, c in enumerate(capas):
            item_nom = QTableWidgetItem(c.nombre)
            item_esp = QTableWidgetItem(f"{c.espesor_mm:.1f}")
            item_den = QTableWidgetItem(f"{c.densidad_kg_m3:.0f}")
            item_vel = QTableWidgetItem(f"{c.velocidad_m_s:.0f}")
            item_imp = QTableWidgetItem(f"{(c.impedancia_rayl / 1e6):.2f}")
            item_ate = QTableWidgetItem(f"{c.atenuacion_db_cm_mhz:.3f}")

            item_esp.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_den.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_vel.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_imp.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_ate.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.tabla.setItem(row, 0, item_nom)
            self.tabla.setItem(row, 1, item_esp)
            self.tabla.setItem(row, 2, item_den)
            self.tabla.setItem(row, 3, item_vel)
            self.tabla.setItem(row, 4, item_imp)
            self.tabla.setItem(row, 5, item_ate)

    def _agregar_capa(self):
        diag = DialogoEditarCapa(parent=self)
        if diag.exec():
            nueva = diag.obtener_capa()
            self.capas.append(nueva)
            self.cargar_datos(self.capas)

    def _editar_capa(self):
        row = self.tabla.currentRow()
        if row < 0 or row >= len(self.capas):
            QMessageBox.warning(self, "Selección requerida", "Por favor seleccione un estrato para editar.")
            return

        diag = DialogoEditarCapa(self.capas[row], parent=self)
        if diag.exec():
            self.capas[row] = diag.obtener_capa()
            self.cargar_datos(self.capas)

    def _eliminar_capa(self):
        row = self.tabla.currentRow()
        if row < 0 or row >= len(self.capas):
            QMessageBox.warning(self, "Selección requerida", "Por favor seleccione un estrato para eliminar.")
            return

        if len(self.capas) <= 1:
            QMessageBox.critical(self, "Acción Inválida", "El modelo debe contener al menos un estrato tisular.")
            return

        nombre = self.capas[row].nombre
        self.capas.pop(row)
        self.cargar_datos(self.capas)
        QMessageBox.information(self, "Estrato Eliminado", f"Se eliminó '{nombre}' del modelo.")

    def _restablecer_literatura(self):
        self.capas = obtener_capas_predeterminadas_literatura()
        self.cargar_datos(self.capas)
        QMessageBox.information(
            self,
            "Valores Restablecidos",
            "Se han restaurado los estratos tisulares de referencia bibliográfica (Duck / IT'IS)."
        )

    def _guardar_cambios(self):
        val = ValidadorClinico.validar_capas_tejido(self.capas)
        if not val.es_valido:
            QMessageBox.critical(self, "Error de Validación", "\n".join(val.errores))
            return

        self.tejidos_modificados.emit(self.capas)
        msg = f"Se han guardado correctamente {len(self.capas)} estratos tisulares."
        if val.advertencias:
            msg += "\n\nAdvertencias:\n" + "\n".join(f"• {a}" for a in val.advertencias)
        QMessageBox.information(self, "Tejidos Actualizados", msg)
