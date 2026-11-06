"""
================================================================================
MÓDULO 4: PARÁMETROS OPERATIVOS Y DOSIMETRÍA
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Permite ingresar y validar los parámetros de funcionamiento del aplicador:
EFD (0.03 a 0.25 mJ/mm²), PRF (4 a 5 Hz), Foco (0.5 a 2 cm) y dosificación.
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
    QScrollArea, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from interfaz.componentes import (
    Colores, TarjetaContenedor, TarjetaEstado, BotonPrimario, BotonSecundario, BadgeEstado
)
from modelos.parametros import ParametrosOperativos
from servicios.validador import ValidadorClinico


class ModuloParametros(QWidget):
    """Pantalla interactiva de dosimetría y parámetros operativos de partida."""

    parametros_modificados = Signal(ParametrosOperativos)

    def __init__(self, parametros: ParametrosOperativos = None, parent=None):
        super().__init__(parent)
        self.parametros = parametros or ParametrosOperativos()
        self._inicializar_ui()
        self.cargar_datos(self.parametros)

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

        badge = BadgeEstado("VENTANA TERAPÉUTICA CLÍNICA", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Parámetros Operativos del Tratamiento")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Configure la ventana de trabajo clínico establecida en el anteproyecto de Bioingeniería (UNER). "
            "El sistema valida en tiempo real que los parámetros permanezcan dentro de los límites de seguridad "
            "y eficacia reportados en la literatura."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. CONTROLES NUMÉRICOS CON UNIDADES Y VALIDACIÓN
        # ----------------------------------------------------------------------
        tarjeta_form = TarjetaContenedor()
        l_form = QVBoxLayout(tarjeta_form)
        l_form.setContentsMargins(24, 20, 24, 20)
        l_form.setSpacing(18)

        t_form = QLabel("CONFIGURACIÓN DE DISPARO Y ENERGÍA")
        t_form.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_form.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_form.addWidget(t_form)

        grid = QGridLayout()
        grid.setSpacing(16)

        # EFD
        lbl_efd = QLabel("Densidad de Flujo de Energía (EFD):")
        lbl_efd.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_efd = QDoubleSpinBox()
        self.spin_efd.setRange(0.01, 0.50)
        self.spin_efd.setSingleStep(0.005)
        self.spin_efd.setDecimals(3)
        self.spin_efd.setValue(0.100)
        self.spin_efd.setSuffix(" mJ/mm²")
        self.spin_efd.valueChanged.connect(self._al_cambiar_parametro)
        grid.addWidget(lbl_efd, 0, 0)
        grid.addWidget(self.spin_efd, 0, 1)

        lbl_ref_efd = QLabel("Referencia anteproyecto: 0.03 a 0.25 mJ/mm² (Nominal: 0.10)")
        lbl_ref_efd.setFont(QFont("Segoe UI", 7))
        lbl_ref_efd.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
        grid.addWidget(lbl_ref_efd, 0, 2)

        # PRF
        lbl_prf = QLabel("Frecuencia de Repetición de Pulsos (PRF):")
        lbl_prf.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_prf = QDoubleSpinBox()
        self.spin_prf.setRange(1.0, 10.0)
        self.spin_prf.setSingleStep(0.5)
        self.spin_prf.setDecimals(1)
        self.spin_prf.setValue(4.0)
        self.spin_prf.setSuffix(" Hz")
        self.spin_prf.valueChanged.connect(self._al_cambiar_parametro)
        grid.addWidget(lbl_prf, 1, 0)
        grid.addWidget(self.spin_prf, 1, 1)

        lbl_ref_prf = QLabel("Referencia anteproyecto: 4.0 a 5.0 Hz")
        lbl_ref_prf.setFont(QFont("Segoe UI", 7))
        lbl_ref_prf.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
        grid.addWidget(lbl_ref_prf, 1, 2)

        # Profundidad Focal
        lbl_foco = QLabel("Profundidad Focal Objetivo:")
        lbl_foco.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_foco = QDoubleSpinBox()
        self.spin_foco.setRange(0.2, 4.0)
        self.spin_foco.setSingleStep(0.1)
        self.spin_foco.setDecimals(2)
        self.spin_foco.setValue(1.00)
        self.spin_foco.setSuffix(" cm")
        self.spin_foco.valueChanged.connect(self._al_cambiar_parametro)
        grid.addWidget(lbl_foco, 2, 0)
        grid.addWidget(self.spin_foco, 2, 1)

        lbl_ref_foco = QLabel("Referencia anteproyecto: 0.5 a 2.0 cm (Dermis profunda)")
        lbl_ref_foco.setFont(QFont("Segoe UI", 7))
        lbl_ref_foco.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
        grid.addWidget(lbl_ref_foco, 2, 2)

        # Densidad de Disparos
        lbl_dens = QLabel("Densidad de Dosificación:")
        lbl_dens.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_densidad = QDoubleSpinBox()
        self.spin_densidad.setRange(5.0, 1000.0)
        self.spin_densidad.setSingleStep(25.0)
        self.spin_densidad.setDecimals(0)
        self.spin_densidad.setValue(150.0)
        self.spin_densidad.setSuffix(" pulsos/cm²")
        self.spin_densidad.valueChanged.connect(self._al_cambiar_parametro)
        grid.addWidget(lbl_dens, 3, 0)
        grid.addWidget(self.spin_densidad, 3, 1)

        lbl_ref_dens = QLabel("Referencia anteproyecto: 10 a 500 pulsos/cm²")
        lbl_ref_dens.setFont(QFont("Segoe UI", 7))
        lbl_ref_dens.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
        grid.addWidget(lbl_ref_dens, 3, 2)

        # Área de la Quemadura
        lbl_area = QLabel("Área Estimada de la Quemadura:")
        lbl_area.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.spin_area = QDoubleSpinBox()
        self.spin_area.setRange(1.0, 100.0)
        self.spin_area.setSingleStep(1.0)
        self.spin_area.setDecimals(1)
        self.spin_area.setValue(10.0)
        self.spin_area.setSuffix(" cm²")
        self.spin_area.valueChanged.connect(self._al_cambiar_parametro)
        grid.addWidget(lbl_area, 4, 0)
        grid.addWidget(self.spin_area, 4, 1)

        lbl_ref_area = QLabel("Área típica de mano / dedos / articulación")
        lbl_ref_area.setFont(QFont("Segoe UI", 7))
        lbl_ref_area.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
        grid.addWidget(lbl_ref_area, 4, 2)

        l_form.addLayout(grid)
        layout.addWidget(tarjeta_form)

        # ----------------------------------------------------------------------
        # 3. ESTIMACIÓN DOSIMÉTRICA EN TIEMPO REAL
        # ----------------------------------------------------------------------
        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(16)

        self.card_total_pulsos = TarjetaEstado(
            titulo="Disparos Programados",
            valor="1500 pulsos",
            subtitulo="Total de frentes de onda en la sesión",
            color_acento=Colores.CELESTE_ACENTO
        )
        layout_cards.addWidget(self.card_total_pulsos)

        self.card_tiempo_sesion = TarjetaEstado(
            titulo="Duración Estimada",
            valor="6.25 minutos",
            subtitulo="Tiempo continuo a 4.0 Hz",
            color_acento="#8b5cf6"
        )
        layout_cards.addWidget(self.card_tiempo_sesion)

        self.card_estado_clinico = TarjetaEstado(
            titulo="Validación de Ventana",
            valor="Dentro de Rango Clínico",
            subtitulo="Cumple con los 4 criterios de partida",
            color_acento=Colores.ESTADO_OK
        )
        layout_cards.addWidget(self.card_estado_clinico)

        layout.addLayout(layout_cards)

        # Botonera inferior
        btn_bar = QHBoxLayout()
        self.btn_reset = BotonSecundario("Restablecer Valores de Partida (Anteproyecto)")
        self.btn_reset.clicked.connect(self._restablecer_valores)
        btn_bar.addWidget(self.btn_reset)

        btn_bar.addStretch()

        self.btn_guardar = BotonPrimario("Guardar Parámetros Operativos")
        self.btn_guardar.clicked.connect(self._guardar_cambios)
        btn_bar.addWidget(self.btn_guardar)

        layout.addLayout(btn_bar)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

    def _al_cambiar_parametro(self):
        """Actualiza en vivo las tarjetas dosimétricas y el estado de validación."""
        efd = self.spin_efd.value()
        prf = self.spin_prf.value()
        foco = self.spin_foco.value()
        dens = self.spin_densidad.value()
        area = self.spin_area.value()

        total_p = int(round(dens * area))
        minutos = (total_p / prf) / 60.0 if prf > 0 else 0.0

        self.card_total_pulsos.actualizar(f"{total_p:,} pulsos".replace(",", "."))
        self.card_tiempo_sesion.actualizar(f"{minutos:.2f} minutos", f"A frecuencia PRF de {prf:.1f} Hz")

        # Emitir la actualización para sincronizar el estado global en tiempo real
        self.parametros.efd_nominal_mj_mm2 = efd
        self.parametros.frecuencia_repeticion_hz = prf
        self.parametros.profundidad_focal_objetivo_cm = foco
        self.parametros.densidad_disparos_pcm2 = dens
        self.parametros.area_tratamiento_cm2 = area
        self.parametros_modificados.emit(self.parametros)

        temp_p = ParametrosOperativos(
            efd_nominal_mj_mm2=efd,
            frecuencia_repeticion_hz=prf,
            profundidad_focal_objetivo_cm=foco,
            densidad_disparos_pcm2=dens,
            area_tratamiento_cm2=area
        )
        res = ValidadorClinico.validar_parametros_operativos(temp_p)

        if not res.es_valido:
            self.card_estado_clinico.actualizar("Inválido", res.errores[0])
            self.card_estado_clinico.setStyleSheet(f"""
                TarjetaEstado {{
                    background-color: #ffffff;
                    border: 1px solid {Colores.BORDE_TARJETA};
                    border-left: 5px solid #dc2626;
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
        elif res.advertencias:
            self.card_estado_clinico.actualizar("Advertencia", res.advertencias[0])
            self.card_estado_clinico.setStyleSheet(f"""
                TarjetaEstado {{
                    background-color: #ffffff;
                    border: 1px solid {Colores.BORDE_TARJETA};
                    border-left: 5px solid {Colores.ESTADO_ALERTA};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
        else:
            self.card_estado_clinico.actualizar("Dentro de Rango", "Cumple ventana segura (Anteproyecto)")
            self.card_estado_clinico.setStyleSheet(f"""
                TarjetaEstado {{
                    background-color: #ffffff;
                    border: 1px solid {Colores.BORDE_TARJETA};
                    border-left: 5px solid {Colores.ESTADO_OK};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)

    def _restablecer_valores(self):
        self.parametros.restablecer_valores_nominales()
        self.cargar_datos(self.parametros)
        QMessageBox.information(
            self,
            "Valores Restablecidos",
            "Se han cargado los valores de partida recomendados por el anteproyecto."
        )

    def cargar_datos(self, p: ParametrosOperativos):
        self.parametros = p
        self.spin_efd.setValue(p.efd_nominal_mj_mm2)
        self.spin_prf.setValue(p.frecuencia_repeticion_hz)
        self.spin_foco.setValue(p.profundidad_focal_objetivo_cm)
        self.spin_densidad.setValue(p.densidad_disparos_pcm2)
        self.spin_area.setValue(p.area_tratamiento_cm2)
        self._al_cambiar_parametro()

    def _guardar_cambios(self):
        self.parametros.efd_nominal_mj_mm2 = self.spin_efd.value()
        self.parametros.frecuencia_repeticion_hz = self.spin_prf.value()
        self.parametros.profundidad_focal_objetivo_cm = self.spin_foco.value()
        self.parametros.densidad_disparos_pcm2 = self.spin_densidad.value()
        self.parametros.area_tratamiento_cm2 = self.spin_area.value()

        val = ValidadorClinico.validar_parametros_operativos(self.parametros)
        if not val.es_valido:
            QMessageBox.critical(self, "Error de Validación", "\n".join(val.errores))
            return

        self.parametros_modificados.emit(self.parametros)
        msg = "Parámetros operativos validados y guardados exitosamente."
        if val.advertencias:
            msg += "\n\nAdvertencias:\n" + "\n".join(f"• {a}" for a in val.advertencias)
        QMessageBox.information(self, "Parámetros Guardados", msg)
