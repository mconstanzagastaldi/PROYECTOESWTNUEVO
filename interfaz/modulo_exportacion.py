"""
================================================================================
MÓDULO 10: EXPORTACIÓN, ALMACENAMIENTO Y REGISTRO (JSON / CSV)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Permite guardar y cargar sesiones en formato JSON, exportar tablas a CSV
y generar un informe técnico imprimible con validador de integridad.
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QListWidget, QFileDialog, QScrollArea, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

import os

from interfaz.componentes import (
    Colores, TarjetaContenedor, BotonPrimario, BotonSecundario, BadgeEstado
)
from modelos.configuracion import ConfiguracionGlobal
from servicios.gestor_configuracion import GestorConfiguracion
from servicios.exportacion import ServicioExportacion


class ModuloExportacion(QWidget):
    """Gestión de almacenamiento en disco, exportaciones CSV y reportes técnicos."""

    configuracion_cargada = Signal(ConfiguracionGlobal)

    def __init__(self, config: ConfiguracionGlobal = None, parent=None):
        super().__init__(parent)
        self.config = config or ConfiguracionGlobal()
        self.resultados = None
        self._inicializar_ui()
        self._refrescar_lista_archivos()
        self._actualizar_vista_previa()

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

        badge = BadgeEstado("GESTIÓN DE DATOS", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Almacenamiento de Configuraciones y Exportación de Datos")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Guarde y recupere configuraciones del aplicador y tejidos en formato estándar JSON. "
            "Exporte tablas de datos en formato CSV para análisis externo y genere reportes técnicos estructurados."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. ACCIONES DE ALMACENAMIENTO Y EXPORTACIÓN
        # ----------------------------------------------------------------------
        tarjeta_acciones = TarjetaContenedor()
        l_acc = QVBoxLayout(tarjeta_acciones)
        l_acc.setContentsMargins(20, 18, 20, 18)
        l_acc.setSpacing(14)

        t_acc = QLabel("OPERACIONES DE PERSISTENCIA Y EXPORTACIÓN")
        t_acc.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_acc.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_acc.addWidget(t_acc)

        grid_btn = QGridLayout()
        grid_btn.setSpacing(12)

        self.btn_guardar_json = BotonPrimario("💾 Guardar Configuración Actual (JSON)")
        self.btn_guardar_json.clicked.connect(self._guardar_json)
        grid_btn.addWidget(self.btn_guardar_json, 0, 0)

        self.btn_cargar_json = BotonSecundario("📂 Cargar Configuración desde Archivo...")
        self.btn_cargar_json.clicked.connect(self._cargar_json_dialogo)
        grid_btn.addWidget(self.btn_cargar_json, 0, 1)

        self.btn_exportar_resumen_csv = BotonSecundario("📊 Exportar Parámetros a CSV")
        self.btn_exportar_resumen_csv.clicked.connect(self._exportar_resumen_csv)
        grid_btn.addWidget(self.btn_exportar_resumen_csv, 1, 0)

        self.btn_exportar_tejidos_csv = BotonSecundario("🧬 Exportar Tejidos a CSV")
        self.btn_exportar_tejidos_csv.clicked.connect(self._exportar_tejidos_csv)
        grid_btn.addWidget(self.btn_exportar_tejidos_csv, 1, 1)

        l_acc.addLayout(grid_btn)
        layout.addWidget(tarjeta_acciones)

        # ----------------------------------------------------------------------
        # 3. HISTORIAL LOCAL Y REPORTE ESTRUCTURADO
        # ----------------------------------------------------------------------
        fila_detalles = QHBoxLayout()
        fila_detalles.setSpacing(18)

        # Columna Izquierda: Archivos Guardados
        tarjeta_hist = TarjetaContenedor()
        tarjeta_hist.setFixedWidth(340)
        l_h = QVBoxLayout(tarjeta_hist)
        l_h.setContentsMargins(18, 16, 18, 16)
        l_h.setSpacing(10)

        t_h = QLabel("CONFIGURACIONES EN DISCO")
        t_h.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_h.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_h.addWidget(t_h)

        self.lista_archivos = QListWidget()
        self.lista_archivos.setStyleSheet(f"""
            QListWidget {{
                background-color: #ffffff;
                border: 1px solid {Colores.BORDE_TARJETA};
                border-radius: 6px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 6px;
                border-bottom: 1px solid #f1f5f9;
            }}
            QListWidget::item:selected {{
                background-color: #e0f2fe;
                color: {Colores.AZUL_PRIMARIO};
                font-weight: bold;
            }}
        """)
        l_h.addWidget(self.lista_archivos)

        self.btn_cargar_sel = BotonSecundario("Cargar Seleccionada")
        self.btn_cargar_sel.clicked.connect(self._cargar_seleccionada)
        l_h.addWidget(self.btn_cargar_sel)

        fila_detalles.addWidget(tarjeta_hist)

        # Columna Derecha: Vista Previa del Informe
        tarjeta_rep = TarjetaContenedor()
        l_r = QVBoxLayout(tarjeta_rep)
        l_r.setContentsMargins(18, 16, 18, 16)
        l_r.setSpacing(10)

        t_r = QLabel("VISTA PREVIA DEL REPORTE TÉCNICO FORMAL")
        t_r.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_r.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_r.addWidget(t_r)

        self.txt_reporte = QTextEdit()
        self.txt_reporte.setReadOnly(True)
        self.txt_reporte.setFont(QFont("Consolas", 8))
        self.txt_reporte.setStyleSheet(f"""
            QTextEdit {{
                background-color: #f8fafc;
                border: 1px solid {Colores.BORDE_TARJETA};
                border-radius: 6px;
                padding: 10px;
                color: {Colores.TEXTO_NORMAL};
            }}
        """)
        l_r.addWidget(self.txt_reporte)

        fila_detalles.addWidget(tarjeta_rep, stretch=1)
        layout.addLayout(fila_detalles)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

    def sincronizar_configuracion(self, config: ConfiguracionGlobal):
        self.config = config
        self._actualizar_vista_previa()

    def sincronizar_resultados(self, resultados):
        """Almacena la última simulación física para su inclusión en reportes y CSV."""
        self.resultados = resultados
        self._actualizar_vista_previa()

    def _actualizar_vista_previa(self):
        rep = ServicioExportacion.generar_reporte_texto(self.config, getattr(self, "resultados", None))
        self.txt_reporte.setPlainText(rep)

    def _refrescar_lista_archivos(self):
        self.lista_archivos.clear()
        archivos = GestorConfiguracion.listar_configuraciones_locales()
        for f in archivos:
            self.lista_archivos.addItem(f)

    def _guardar_json(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Configuración JSON",
            os.path.join(GestorConfiguracion.DIRECTORIO_POR_DEFECTO, f"{self.config.nombre_configuracion}.json"),
            "Archivos JSON (*.json)"
        )
        if ruta:
            ok, msg = GestorConfiguracion.guardar_archivo(self.config, ruta)
            if ok:
                QMessageBox.information(self, "Almacenamiento Exitoso", msg)
                self._refrescar_lista_archivos()
            else:
                QMessageBox.critical(self, "Error al Guardar", msg)

    def _cargar_json_dialogo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Configuración JSON",
            GestorConfiguracion.DIRECTORIO_POR_DEFECTO,
            "Archivos JSON (*.json)"
        )
        if ruta:
            self._procesar_carga_archivo(ruta)

    def _cargar_seleccionada(self):
        item = self.lista_archivos.currentItem()
        if not item:
            QMessageBox.warning(self, "Selección Requerida", "Seleccione un archivo de la lista.")
            return

        ruta = os.path.join(GestorConfiguracion.DIRECTORIO_POR_DEFECTO, item.text())
        self._procesar_carga_archivo(ruta)

    def _procesar_carga_archivo(self, ruta: str):
        cfg, val, msg = GestorConfiguracion.cargar_archivo(ruta)
        if cfg is None:
            QMessageBox.critical(self, "Error al Cargar", f"No se pudo cargar la configuración:\n{msg}")
            return

        self.config = cfg
        self._actualizar_vista_previa()
        self.configuracion_cargada.emit(self.config)

        res_msg = f"Configuración '{cfg.nombre_configuracion}' cargada exitosamente."
        if val.advertencias:
            res_msg += "\n\nAdvertencias:\n" + "\n".join(f"• {a}" for a in val.advertencias)
        QMessageBox.information(self, "Carga Completada", res_msg)

    def _exportar_resumen_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Parámetros y Resultados a CSV",
            "parametros_operativos_eswt.csv",
            "Archivos CSV (*.csv)"
        )
        if ruta:
            ok, msg = ServicioExportacion.exportar_resumen_operativo_csv(
                self.config, ruta, resultados=getattr(self, "resultados", None)
            )
            if ok:
                QMessageBox.information(self, "Exportación Exitosa", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    def _exportar_tejidos_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Estratos Tisulares a CSV",
            "estratos_tisulares_eswt.csv",
            "Archivos CSV (*.csv)"
        )
        if ruta:
            ok, msg = ServicioExportacion.exportar_tejidos_a_csv(self.config, ruta)
            if ok:
                QMessageBox.information(self, "Exportación Exitosa", msg)
            else:
                QMessageBox.critical(self, "Error", msg)
