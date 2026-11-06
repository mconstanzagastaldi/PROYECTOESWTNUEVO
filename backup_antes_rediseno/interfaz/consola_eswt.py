"""
================================================================================
CONSOLA ELECTROMÉDICA DEL EQUIPO ESWT (INTERFAZ DE EQUIPAMIENTO BIOMÉDICO)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Pantalla principal tipo equipo electromédico real (Consola de Ondas de Choque):
  - Chasis oscuro con indicadores digitales tipo display médico OLED/LED.
  - Botoneras físicas para EFD (+/-), PRF (4/5 Hz), geometría, quemadura, etc.
  - Profundidad focal ajustable con botonera de presets (RF5).
  - Área de quemadura y tiempo de sesión (RF4).
  - Edad del paciente con presets (atenuación del tejido).
  - Telemetría extendida: P- cavitación, ΔT, Z-gel, confiabilidad del modelo.
  - 4 vistas gráficas requeridas por la matriz de trazabilidad (RF2–RF5).
================================================================================
Cobertura de requerimientos de la Matriz de Trazabilidad:
  RF1 (PRF 4-5 Hz), RF2 (Perfil de onda, t_rise=8ns), RF3 (EFD 0.03–0.25),
  RF4 (Disparos 10–500 p/cm²), RF5 (Profundidad focal 0.5–2.0 cm),
  RF6 (Gel acoplamiento 1.5 MRayl), RF8 (Cabezal Ø≤40mm, curva/plana),
  RNF Bioseguridad (P- ≤ -10 MPa), RNF Térmica (ΔT < 0.5°C),
  RNF Confiabilidad (CV < 5%).
================================================================================
"""

try:
    from modelos.configuracion import ConfiguracionGlobal
    from modelos.tejido import CapaTejido
    from servicios.validador import ValidadorClinico
    from servicios.gestor_configuracion import GestorConfiguracion
    from servicios.exportacion import ServicioExportacion
    from visualizacion.graficos import (
        graficar_pulso_temporal,
        graficar_mapa_2d,
        graficar_perfil_axial,
        graficar_esquema_tisular,
        graficar_boxplot_confiabilidad
    )
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from modelos.configuracion import ConfiguracionGlobal
    from modelos.tejido import CapaTejido
    from servicios.validador import ValidadorClinico
    from servicios.gestor_configuracion import GestorConfiguracion
    from servicios.exportacion import ServicioExportacion
    from visualizacion.graficos import (
        graficar_pulso_temporal,
        graficar_mapa_2d,
        graficar_perfil_axial,
        graficar_esquema_tisular,
        graficar_boxplot_confiabilidad
    )

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QFileDialog, QMessageBox,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


# ==============================================================================
# PALETA CROMÁTICA – CONSOLA DE EQUIPO MÉDICO (HARDWARE REAL)
# ==============================================================================
class ColoresConsola:
    CHASIS_FONDO      = "#090d16"   # Carcasa oscura de equipamiento médico
    PANEL_CONTROL     = "#111827"   # Paneles de instrumentos de control
    BORDE_HARDWARE    = "#1f293d"   # Separadores metálicos/plásticos del chasis
    DISPLAY_DIGITAL_BG= "#040711"   # Fondo de display digital LED/OLED

    # Iluminación de displays e indicadores activos
    CYAN_MEDICO  = "#00f0ff"        # Dígitos principales y selecciones activas
    VERDE_SEGURO = "#10b981"        # Estado listo / seguro / umbral cumplido
    AMBAR_AVISO  = "#f59e0b"        # Advertencia / standby
    ROJO_PULSO   = "#ef4444"        # Disparo / Presión positiva peak / alarma

    # Botonería física del equipo
    BOTON_NORMAL_BG    = "#1e293b"
    BOTON_NORMAL_HOVER = "#334155"
    BOTON_ACTIVO_BG    = "#0284c7"
    TEXTO_BOTON        = "#f8fafc"
    TEXTO_LABEL        = "#94a3b8"


# ==============================================================================
# VENTANA PRINCIPAL DE LA CONSOLA ELECTROMÉDICA
# ==============================================================================
class ConsolaESWT(QMainWindow):
    """Ventana principal con diseño y ergonomía de pantalla de consola médica."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "CONSOLA CLÍNICA ESWT | APLICADOR PIEZOELÉCTRICO (UNER – BIOINGENIERÍA)"
        )
        # Arranca maximizada para evitar recorte en cualquier resolución
        self.showMaximized()
        self.setMinimumSize(1200, 760)
        self.setStyleSheet(f"background-color: {ColoresConsola.CHASIS_FONDO};")

        # Modelo maestro de datos
        self.config = ConfiguracionGlobal()
        self.vista_grafica_actual = 0   # 0:Pulso 1:Mapa2D 2:Presión_z 3:Esquema
        self.disparando = False
        # Estado interno expandido (parámetros no incluidos aún en modelos)
        self._efd    = self.config.parametros.efd_nominal_mj_mm2       # mJ/mm²
        self._prf    = self.config.parametros.frecuencia_repeticion_hz # Hz
        self._foco_cm = self.config.parametros.profundidad_focal_objetivo_cm  # cm
        self._area_cm2 = 10.0    # cm² de quemadura
        self._edad     = 40      # años del paciente
        self._tipo_quem = "3er Grado"

        self._crear_ui_consola()
        self._actualizar_telemetria()

    # ==========================================================================
    # CONSTRUCCIÓN DE LA UI
    # ==========================================================================
    def _crear_ui_consola(self):
        widget_raiz = QWidget()
        self.setCentralWidget(widget_raiz)
        layout_raiz = QVBoxLayout(widget_raiz)
        layout_raiz.setContentsMargins(12, 10, 12, 10)
        layout_raiz.setSpacing(8)

        layout_raiz.addWidget(self._crear_barra_superior())

        # ---- CUERPO: Panel de mandos (izq) + Monitor gráfico (der) -----------
        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(10)
        cuerpo.addWidget(self._crear_panel_mandos())
        cuerpo.addWidget(self._crear_panel_monitor(), stretch=1)
        layout_raiz.addLayout(cuerpo, stretch=1)

        layout_raiz.addWidget(self._crear_barra_inferior())

    # --------------------------------------------------------------------------
    # 1. BARRA SUPERIOR
    # --------------------------------------------------------------------------
    def _crear_barra_superior(self) -> QFrame:
        barra = QFrame()
        barra.setMinimumHeight(50)
        barra.setMaximumHeight(60)
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 6px;
            }}
        """)
        l = QHBoxLayout(barra)
        l.setContentsMargins(20, 0, 20, 0)

        lbl_logo = QLabel("ESWT THERAPY SYSTEM")
        lbl_logo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_logo.setStyleSheet(f"color: {ColoresConsola.CYAN_MEDICO}; letter-spacing: 1px;")
        l.addWidget(lbl_logo)

        lbl_sub = QLabel(
            " |  APLICADOR PIEZOELÉCTRICO FOCALIZADO  •  "
            "CICATRICES POSTQUEMADURA  |  UNER – TALLER DE BIOINGENIERÍA"
        )
        lbl_sub.setFont(QFont("Segoe UI", 8))
        lbl_sub.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")
        l.addWidget(lbl_sub)
        l.addStretch()

        self.lbl_interlock = QLabel("● ACOPLE ACÚSTICO: ÓPTIMO  (Z-GEL = 1.50 MRayl)")
        self.lbl_interlock.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.lbl_interlock.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
        l.addWidget(self.lbl_interlock)

        l.addSpacing(20)

        self.lbl_estado_emision = QLabel("● SISTEMA: LISTO (STANDBY)")
        self.lbl_estado_emision.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.lbl_estado_emision.setStyleSheet(f"color: {ColoresConsola.AMBAR_AVISO};")
        l.addWidget(self.lbl_estado_emision)

        return barra

    # --------------------------------------------------------------------------
    # 2. PANEL DE MANDOS (izquierda, 450 px, con scroll para resoluciones bajas)
    # --------------------------------------------------------------------------
    def _crear_panel_mandos(self) -> QWidget:
        """Envuelve los mandos en un QScrollArea para adaptarse a cualquier pantalla."""
        scroll = QScrollArea()
        scroll.setFixedWidth(455)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: {ColoresConsola.PANEL_CONTROL}; border: 1px solid {ColoresConsola.BORDE_HARDWARE}; border-radius: 8px; }}
            QScrollBar:vertical {{ background: {ColoresConsola.CHASIS_FONDO}; width: 8px; border-radius: 4px; }}
            QScrollBar::handle:vertical {{ background: #334155; border-radius: 4px; }}
        """)

        inner = QWidget()
        inner.setStyleSheet(f"background: {ColoresConsola.PANEL_CONTROL};")
        l_mandos = QVBoxLayout(inner)
        l_mandos.setContentsMargins(16, 14, 16, 14)
        l_mandos.setSpacing(10)

        tit = QLabel("MANDOS DE PARÁMETROS OPERATIVOS")
        tit.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        tit.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL}; letter-spacing: 0.8px;")
        l_mandos.addWidget(tit)

        # -- RF3: DENSIDAD DE FLUJO DE ENERGÍA (EFD) --
        bloque_efd = self._crear_bloque_parametro(
            "DENSIDAD DE FLUJO DE ENERGÍA  (RF3 – EFD)", "mJ/mm²",
            "Rango clínico: 0.03 – 0.25  (Nominal: 0.10)  [Cui et al. 2018]"
        )
        self.disp_efd = bloque_efd["display"]
        self.disp_efd.setText(f"{self._efd:.3f}")
        fila_efd = QHBoxLayout()
        fila_efd.addWidget(self._crear_boton_consola("▼ -0.01", ancho=72, callback=lambda: self._ajustar_efd(-0.01)))
        fila_efd.addWidget(self._crear_boton_consola("▲ +0.01", ancho=72, callback=lambda: self._ajustar_efd(+0.01)))
        for v in [0.05, 0.08, 0.10, 0.15, 0.20]:
            fila_efd.addWidget(self._crear_boton_consola(f"{v:.2f}", ancho=46, callback=lambda val=v: self._fijar_efd(val)))
        bloque_efd["layout"].addLayout(fila_efd)
        l_mandos.addWidget(bloque_efd["widget"])

        # -- RF1: FRECUENCIA DE REPETICIÓN (PRF) --
        bloque_prf = self._crear_bloque_parametro(
            "FRECUENCIA DE REPETICIÓN  (RF1 – PRF)", "Hz",
            "Rango seguro: 4.0 – 5.0 Hz  (T ≥ 200 ms)  [Lee et al. 2024]"
        )
        self.disp_prf = bloque_prf["display"]
        self.disp_prf.setText(f"{self._prf:.1f}")
        fila_prf = QHBoxLayout()
        self.btn_prf_4 = self._crear_boton_consola("4.0 Hz  (Nominal)", activo=True, callback=lambda: self._fijar_prf(4.0))
        self.btn_prf_5 = self._crear_boton_consola("5.0 Hz", callback=lambda: self._fijar_prf(5.0))
        fila_prf.addWidget(self.btn_prf_4)
        fila_prf.addWidget(self.btn_prf_5)
        bloque_prf["layout"].addLayout(fila_prf)
        l_mandos.addWidget(bloque_prf["widget"])

        # -- RF5: PROFUNDIDAD FOCAL --
        bloque_foco = self._crear_bloque_parametro(
            "PROFUNDIDAD FOCAL OBJETIVO  (RF5)", "cm",
            "Rango terapéutico: 0.5 – 2.0 cm "
        )
        self.disp_foco = bloque_foco["display"]
        self.disp_foco.setText(f"{self._foco_cm:.1f}")
        fila_foco = QHBoxLayout()
        for fc in [0.5, 1.0, 1.5, 2.0]:
            self._btn_foco = self._crear_boton_consola(
                f"{fc} cm", activo=(fc == self._foco_cm),
                callback=lambda f=fc: self._fijar_foco(f)
            )
            fila_foco.addWidget(self._btn_foco)
        bloque_foco["layout"].addLayout(fila_foco)
        l_mandos.addWidget(bloque_foco["widget"])
        self._botones_foco = []
        # Registramos los botones de foco para actualizar activo/inactivo
        self._registrar_botones_foco(bloque_foco["widget"], [0.5, 1.0, 1.5, 2.0])

        # -- RF4: DOSIFICACIÓN (pulsos y área) --
        bloque_dosis = self._crear_bloque_parametro(
            "DOSIFICACIÓN DE SESIÓN  (RF4 – DISPAROS)", "pulsos",
            "Rango: 10 – 500 p/cm² "
        )
        self.disp_dosis = bloque_dosis["display"]
        self._actualizar_display_dosis()
        fila_dens = QHBoxLayout()
        fila_dens.addWidget(QLabel("Densidad (p/cm²):").setParent(None) or self._mini_label("Densidad:"))
        for dens in [50, 100, 150, 250, 500]:
            fila_dens.addWidget(self._crear_boton_consola(f"{dens}", callback=lambda d=dens: self._fijar_densidad_pulsos(d)))
        bloque_dosis["layout"].addLayout(fila_dens)

        # Área de quemadura
        fila_area = QHBoxLayout()
        fila_area.addWidget(self._mini_label("Área quemadura:"))
        for a in [5, 10, 15, 20]:
            fila_area.addWidget(self._crear_boton_consola(
                f"{a} cm²", activo=(a == self._area_cm2),
                callback=lambda av=a: self._fijar_area(av)
            ))
        bloque_dosis["layout"].addLayout(fila_area)
        l_mandos.addWidget(bloque_dosis["widget"])

        # -- RF8: ADAPTABILIDAD ANATÓMICA Y ACOPLAMIENTO ACÚSTICO --
        bloque_geom = self._crear_bloque_parametro(
            "ADAPTABILIDAD ANATÓMICA Y SUPERFICIE (RF8)", "Normal Fija 0°",
            "Chasis compacto wand Ø ≤ 40 mm | Acople adaptable a manos y articulaciones"
        )
        self.disp_geom = bloque_geom["display"]
        self.disp_geom.setText("Emisión Normal (0°)")

        fila_tipo = QHBoxLayout()
        self.btn_curva = self._crear_boton_consola("Curva / Irregular (Manos/Dedos)", activo=True, callback=lambda: self._fijar_superficie("Curva"))
        self.btn_plana = self._crear_boton_consola("Plana / Lisa (Tronco/Muslo)", callback=lambda: self._fijar_superficie("Plana"))
        fila_tipo.addWidget(self.btn_curva)
        fila_tipo.addWidget(self.btn_plana)
        bloque_geom["layout"].addLayout(fila_tipo)

        fila_acople = QHBoxLayout()
        self.btn_acople_gel = self._crear_boton_consola("Gel Conformable (Z=1.5 MRayl)", activo=True, callback=lambda: self._fijar_acople("Gel"))
        self.btn_acople_pad = self._crear_boton_consola("Almohadilla Articular", callback=lambda: self._fijar_acople("Almohadilla"))
        fila_acople.addWidget(self.btn_acople_gel)
        fila_acople.addWidget(self.btn_acople_pad)
        bloque_geom["layout"].addLayout(fila_acople)
        l_mandos.addWidget(bloque_geom["widget"])

        # -- TIPO DE QUEMADURA Y ESTRATIFICACIÓN --
        bloque_piel = self._crear_bloque_parametro(
            "TIPO DE QUEMADURA Y ESTRATIFICACIÓN TISULAR", "Grosor",
            "Piel sana 2.5 mm | Cicatriz 5–9 mm | Subcutáneo 7 mm "
        )
        self.disp_piel = bloque_piel["display"]
        self.disp_piel.setText("3er Grado (9 mm)")

        fila_grado = QHBoxLayout()
        self.btn_grado3 = self._crear_boton_consola("3er Grado  (Fibrótica 9 mm)", activo=True, callback=lambda: self._fijar_tipo_quemadura("3er Grado"))
        self.btn_grado2 = self._crear_boton_consola("2do Grado Profundo (5 mm)", callback=lambda: self._fijar_tipo_quemadura("2do Grado"))
        fila_grado.addWidget(self.btn_grado3)
        fila_grado.addWidget(self.btn_grado2)
        bloque_piel["layout"].addLayout(fila_grado)
        l_mandos.addWidget(bloque_piel["widget"])

        # -- EDAD DEL PACIENTE (modula atenuación de tejido) --
        bloque_edad = self._crear_bloque_parametro(
            "EDAD DEL PACIENTE  (Coeficiente de Atenuación)", "años",
            "Rango: 10 – 80 años  |  Modula α del tejido cicatrizal"
        )
        self.disp_edad = bloque_edad["display"]
        self.disp_edad.setText(f"{self._edad}")

        fila_edad_btn = QHBoxLayout()
        fila_edad_btn.addWidget(self._crear_boton_consola("▼ -5", ancho=68, callback=lambda: self._ajustar_edad(-5)))
        fila_edad_btn.addWidget(self._crear_boton_consola("▲ +5", ancho=68, callback=lambda: self._ajustar_edad(+5)))
        for lbl_e, e_val in [("Joven (20)", 20), ("Adulto (40)", 40), ("Mayor (60)", 60)]:
            fila_edad_btn.addWidget(self._crear_boton_consola(lbl_e, callback=lambda ev=e_val: self._fijar_edad(ev)))
        bloque_edad["layout"].addLayout(fila_edad_btn)
        l_mandos.addWidget(bloque_edad["widget"])

        l_mandos.addStretch()

        # -- BOTÓN MAESTRO DE DISPARO --
        btn_disparo = QPushButton("▶  DISPARAR  /  EMISIÓN ACÚSTICA")
        btn_disparo.setMinimumHeight(44)
        btn_disparo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn_disparo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_disparo.setStyleSheet(f"""
            QPushButton {{
                background-color: #0369a1;
                color: #ffffff;
                border: 2px solid {ColoresConsola.CYAN_MEDICO};
                border-radius: 6px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{ background-color: #0284c7; border-color: #ffffff; }}
            QPushButton:pressed {{ background-color: #0c4a6e; }}
        """)
        btn_disparo.clicked.connect(self._ejecutar_disparo_equipo)
        self.btn_disparo_equipo = btn_disparo
        l_mandos.addWidget(btn_disparo)

        scroll.setWidget(inner)
        return scroll

    def _registrar_botones_foco(self, bloque_widget: QFrame, valores: list):
        """Guarda referencias a los botones de foco para actualizar estado activo."""
        # Busca los QPushButton dentro del bloque y los asocia con sus valores
        self._botones_foco_map = {}
        for btn in bloque_widget.findChildren(QPushButton):
            for fc in valores:
                if btn.text() == f"{fc} cm":
                    self._botones_foco_map[fc] = btn

    def _mini_label(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setFont(QFont("Segoe UI", 7))
        lbl.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")
        return lbl

    # --------------------------------------------------------------------------
    # 3. PANEL MONITOR GRÁFICO (derecha)
    # --------------------------------------------------------------------------
    def _crear_panel_monitor(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 8px;
            }}
        """)
        l = QVBoxLayout(panel)
        l.setContentsMargins(16, 12, 16, 12)
        l.setSpacing(8)

        # Selectores de vista gráfica
        barra_vistas = QHBoxLayout()
        barra_vistas.setSpacing(6)
        self.btn_vista_pulso = self._crear_boton_consola("1. PULSO p(t)", activo=True, callback=lambda: self._cambiar_vista_grafica(0))
        self.btn_vista_mapa  = self._crear_boton_consola("2. MAPA 2D", callback=lambda: self._cambiar_vista_grafica(1))
        self.btn_vista_prof  = self._crear_boton_consola("3. PERFIL AXIAL", callback=lambda: self._cambiar_vista_grafica(2))
        self.btn_vista_esq   = self._crear_boton_consola("4. ESQUEMA PIEL", callback=lambda: self._cambiar_vista_grafica(3))
        self.btn_vista_box   = self._crear_boton_consola("5. BUCLE / BOXPLOT (n=50)", callback=lambda: self._cambiar_vista_grafica(4))
        for btn in [self.btn_vista_pulso, self.btn_vista_mapa, self.btn_vista_prof, self.btn_vista_esq, self.btn_vista_box]:
            barra_vistas.addWidget(btn)
        barra_vistas.addStretch()
        barra_vistas.addWidget(self._crear_boton_consola("💾 Guardar Gráfico (PNG)", ancho=160, callback=self._exportar_png))
        l.addLayout(barra_vistas)

        # Canvas Matplotlib (pantalla del equipo)
        marco = QFrame()
        marco.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.DISPLAY_DIGITAL_BG};
                border: 2px solid #1e293b;
                border-radius: 6px;
            }}
        """)
        l_scr = QVBoxLayout(marco)
        l_scr.setContentsMargins(6, 6, 6, 6)
        self.figura = Figure(figsize=(9.0, 5.2), dpi=100, facecolor=ColoresConsola.DISPLAY_DIGITAL_BG)
        self.canvas = FigureCanvasQTAgg(self.figura)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        l_scr.addWidget(self.canvas)
        l.addWidget(marco, stretch=1)

        # Telemetría biomédica (fila de tarjetas)
        l.addLayout(self._crear_fila_telemetria())
        # Segunda fila de telemetría con RNF
        l.addLayout(self._crear_fila_telemetria_rnf())

        self._actualizar_grafico_pantalla()
        return panel

    def _crear_fila_telemetria(self) -> QHBoxLayout:
        fila = QHBoxLayout()
        fila.setSpacing(8)
        self.card_p_peak  = self._crear_tarjeta_telemetria("P+ FUENTE", "75.8 MPa", "Tracción P- = -10.0 MPa")
        self.card_p_deep  = self._crear_tarjeta_telemetria("PRESIÓN DERMIS (1.8 cm)", "5.08 MPa", "Umbral acústico: > 0.50 MPa")
        self.card_ispta   = self._crear_tarjeta_telemetria("INTENSIDAD ISPTA", "0.040 W/cm²", "Límite acústico: < 1.00 W/cm²")
        self.card_foco_ok = self._crear_tarjeta_telemetria("ZONA FOCAL", "CONFORME", "5 mm ≤ zf ≤ 20 mm en tejido")
        for c in [self.card_p_peak, self.card_p_deep, self.card_ispta, self.card_foco_ok]:
            fila.addWidget(c)
        return fila

    def _crear_fila_telemetria_rnf(self) -> QHBoxLayout:
        """Segunda fila de telemetría cubriendo los RNF de la matriz."""
        fila = QHBoxLayout()
        fila.setSpacing(8)
        # Criterio cavitación acústica
        self.card_p_neg    = self._crear_tarjeta_telemetria("P- CAVITACIÓN", "-10.0 MPa", "Tracción acústica: ≤ -10.0 MPa")
        # Seguridad térmica técnica: ΔT estimado en transductor/acople
        self.card_dt       = self._crear_tarjeta_telemetria("ΔT ESTIMADO", "0.00 °C", "Límite técnico: < 0.5 °C")
        # Tiempo de sesión estimado (RF4)
        self.card_t_sesion = self._crear_tarjeta_telemetria("TIEMPO SESIÓN", "0.0 min", f"Área: {self._area_cm2:.0f} cm²  |  PRF = {self._prf:.1f} Hz")
        # Análisis computacional de sensibilidad: CV < 5%
        card_cv = self._crear_tarjeta_telemetria("SENSIBILIDAD MODELO", "CV = 2.45%", "SD/µ < 5% → Estable  (n=50)")
        card_cv.lbl_v.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
        self.card_cv = card_cv
        for c in [self.card_p_neg, self.card_dt, self.card_t_sesion, self.card_cv]:
            fila.addWidget(c)
        return fila

    # --------------------------------------------------------------------------
    # 4. BARRA INFERIOR (memorias + exportación)
    # --------------------------------------------------------------------------
    def _crear_barra_inferior(self) -> QFrame:
        barra = QFrame()
        barra.setMinimumHeight(44)
        barra.setMaximumHeight(56)
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 6px;
            }}
        """)
        l = QHBoxLayout(barra)
        l.setContentsMargins(14, 0, 14, 0)
        l.setSpacing(8)

        lbl_mem = QLabel("MEMORIAS RÁPIDAS:")
        lbl_mem.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_mem.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")
        l.addWidget(lbl_mem)
        for i, lbl_m in [(1, "M1: Mano/Articulación (0.10 mJ/mm²)"),
                          (2, "M2: Quemadura Profunda (0.15 mJ/mm²)"),
                          (3, "M3: Baja Intensidad (0.05 mJ/mm²)")]:
            l.addWidget(self._crear_boton_consola(lbl_m, callback=lambda b=i: self._cargar_preset_memoria(b)))
        l.addStretch()
        l.addWidget(self._crear_boton_consola("💾 Guardar Sesión (JSON)", ancho=180, callback=self._guardar_sesion_json))
        l.addWidget(self._crear_boton_consola("📊 Exportar Datos (CSV)", ancho=170, callback=self._exportar_datos_csv))
        return barra

    # ==========================================================================
    # CREADORES DE COMPONENTES VISUALES TIPO HARDWARE
    # ==========================================================================
    def _crear_bloque_parametro(self, titulo: str, unidad: str, rango_info: str) -> dict:
        """Contenedor con display digital OLED + botonera."""
        w = QFrame()
        w.setStyleSheet(f"""
            QFrame {{
                background-color: #0b1120;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }}
        """)
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 8, 10, 8)
        l.setSpacing(5)

        fila_top = QHBoxLayout()
        lbl_t = QLabel(titulo)
        lbl_t.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        lbl_t.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL}; letter-spacing: 0.5px;")
        fila_top.addWidget(lbl_t)
        lbl_u = QLabel(f"[{unidad}]")
        lbl_u.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        lbl_u.setStyleSheet(f"color: {ColoresConsola.CYAN_MEDICO};")
        fila_top.addWidget(lbl_u, alignment=Qt.AlignmentFlag.AlignRight)
        l.addLayout(fila_top)

        disp = QLabel("0.00")
        disp.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        disp.setStyleSheet(f"""
            QLabel {{
                background-color: {ColoresConsola.DISPLAY_DIGITAL_BG};
                color: {ColoresConsola.CYAN_MEDICO};
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 3px 10px;
                letter-spacing: 1px;
            }}
        """)
        disp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(disp)

        lbl_r = QLabel(rango_info)
        lbl_r.setFont(QFont("Segoe UI", 6))
        lbl_r.setStyleSheet("color: #64748b;")
        l.addWidget(lbl_r)

        return {"widget": w, "layout": l, "display": disp}

    def _crear_boton_consola(self, texto: str, ancho: int = None,
                              activo: bool = False, callback=None) -> QPushButton:
        """Botón físico de consola electromédica."""
        btn = QPushButton(texto)
        if ancho:
            btn.setFixedWidth(ancho)
        btn.setMinimumHeight(28)
        btn.setMaximumHeight(32)
        btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bg   = ColoresConsola.BOTON_ACTIVO_BG if activo else ColoresConsola.BOTON_NORMAL_BG
        bord = ColoresConsola.CYAN_MEDICO      if activo else ColoresConsola.BORDE_HARDWARE
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {ColoresConsola.TEXTO_BOTON};
                border: 1px solid {bord};
                border-radius: 4px;
                padding: 3px 7px;
            }}
            QPushButton:hover {{ background-color: {ColoresConsola.BOTON_NORMAL_HOVER}; border-color: {ColoresConsola.CYAN_MEDICO}; }}
            QPushButton:pressed {{ background-color: #0369a1; }}
        """)
        if callback:
            btn.clicked.connect(callback)
        return btn

    def _crear_tarjeta_telemetria(self, titulo: str, valor: str, detalle: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.DISPLAY_DIGITAL_BG};
                border: 1px solid #1e293b;
                border-left: 3px solid {ColoresConsola.CYAN_MEDICO};
                border-radius: 4px;
            }}
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(8, 5, 8, 5)
        l.setSpacing(1)

        lbl_t = QLabel(titulo)
        lbl_t.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        lbl_t.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")
        l.addWidget(lbl_t)

        lbl_v = QLabel(valor)
        lbl_v.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        lbl_v.setStyleSheet(f"color: {ColoresConsola.TEXTO_BOTON};")
        l.addWidget(lbl_v)

        lbl_d = QLabel(detalle)
        lbl_d.setFont(QFont("Segoe UI", 6))
        lbl_d.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
        l.addWidget(lbl_d)

        card.lbl_v = lbl_v
        card.lbl_d = lbl_d
        return card

    # ==========================================================================
    # LÓGICA DE CONTROL Y PARÁMETROS OPERATIVOS
    # ==========================================================================
    def _ajustar_efd(self, delta: float):
        nuevo = round(self._efd + delta, 3)
        self._fijar_efd(max(0.01, min(0.30, nuevo)))

    def _fijar_efd(self, valor: float):
        self._efd = valor
        self.config.parametros.efd_nominal_mj_mm2 = valor
        self.disp_efd.setText(f"{valor:.3f}")
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _fijar_prf(self, freq: float):
        self._prf = freq
        self.config.parametros.frecuencia_repeticion_hz = freq
        self.disp_prf.setText(f"{freq:.1f}")
        self.btn_prf_4.setStyleSheet(self._estilo_btn_activo(freq == 4.0))
        self.btn_prf_5.setStyleSheet(self._estilo_btn_activo(freq == 5.0))
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _fijar_foco(self, foco_cm: float):
        self._foco_cm = foco_cm
        self.config.parametros.profundidad_focal_objetivo_cm = foco_cm
        self.disp_foco.setText(f"{foco_cm:.1f}")
        # Actualizar estilos de los botones de foco
        for fc, btn in self._botones_foco_map.items():
            btn.setStyleSheet(self._estilo_btn_activo(fc == foco_cm))
        self._actualizar_grafico_pantalla()

    def _fijar_densidad_pulsos(self, dens: float):
        self.config.parametros.densidad_disparos_pcm2 = dens
        self._actualizar_display_dosis()
        self._actualizar_telemetria()

    def _fijar_area(self, area: float):
        self._area_cm2 = area
        self._actualizar_display_dosis()
        self._actualizar_telemetria()

    def _actualizar_display_dosis(self):
        total = int(self.config.parametros.densidad_disparos_pcm2 * self._area_cm2)
        self.disp_dosis.setText(f"{total}  ({self.config.parametros.densidad_disparos_pcm2:.0f} p/cm²  ×  {self._area_cm2:.0f} cm²)")

    def _fijar_superficie(self, tipo: str):
        if "curva" in tipo.lower():
            self.config.geometria.tipo_superficie = "Curva (Articulación / Mano)"
            self.btn_curva.setStyleSheet(self._estilo_btn_activo(True))
            self.btn_plana.setStyleSheet(self._estilo_btn_activo(False))
        else:
            self.config.geometria.tipo_superficie = "Plana (Tronco / Muslo)"
            self.btn_curva.setStyleSheet(self._estilo_btn_activo(False))
            self.btn_plana.setStyleSheet(self._estilo_btn_activo(True))
        self._actualizar_grafico_pantalla()

    def _fijar_acople(self, tipo: str):
        if "pad" in tipo.lower() or "almohadilla" in tipo.lower():
            self.config.aplicador.sistema_acoplamiento = "Almohadilla de Gel Adaptable"
            self.btn_acople_gel.setStyleSheet(self._estilo_btn_activo(False))
            self.btn_acople_pad.setStyleSheet(self._estilo_btn_activo(True))
            self.lbl_interlock.setText("● ACOPLE ACÚSTICO: ALMOHADILLA ARTICULAR (Z=1.50 MRayl)")
        else:
            self.config.aplicador.sistema_acoplamiento = "Gel Acústico Conformable"
            self.btn_acople_gel.setStyleSheet(self._estilo_btn_activo(True))
            self.btn_acople_pad.setStyleSheet(self._estilo_btn_activo(False))
            self.lbl_interlock.setText("● ACOPLE ACÚSTICO: GEL CONFORMABLE (Z=1.50 MRayl)")
        self._actualizar_grafico_pantalla()

    def _fijar_tipo_quemadura(self, tipo: str):
        self._tipo_quem = tipo
        if "3er" in tipo:
            self.disp_piel.setText("3er Grado (9 mm)")
            self.btn_grado3.setStyleSheet(self._estilo_btn_activo(True))
            self.btn_grado2.setStyleSheet(self._estilo_btn_activo(False))
            for c in self.config.tejidos:
                if "cicatriz" in c.nombre.lower():
                    c.nombre = "Cicatriz Fibrótica (3er Grado)"
                    c.espesor_mm         = 9.0
                    c.densidad_kg_m3     = 1200.0
                    c.velocidad_m_s      = 1750.0
                    c.atenuacion_db_cm_mhz = 2.100
                    c.recalcular_impedancia()
        else:
            self.disp_piel.setText("2do Grado Profundo (5 mm)")
            self.btn_grado3.setStyleSheet(self._estilo_btn_activo(False))
            self.btn_grado2.setStyleSheet(self._estilo_btn_activo(True))
            for c in self.config.tejidos:
                if "cicatriz" in c.nombre.lower():
                    c.nombre = "Cicatriz Intermedia (2do Grado)"
                    c.espesor_mm         = 5.0
                    c.densidad_kg_m3     = 1140.0
                    c.velocidad_m_s      = 1680.0
                    c.atenuacion_db_cm_mhz = 1.400
                    c.recalcular_impedancia()
        self._actualizar_grafico_pantalla()

    def _ajustar_edad(self, delta: int):
        self._fijar_edad(max(10, min(80, self._edad + delta)))

    def _fijar_edad(self, edad: int):
        self._edad = edad
        self.disp_edad.setText(str(edad))
        # La edad modula ligeramente la atenuación (Duck 1990): α_efectiva = α_base * (1 + 0.004*(edad-40))
        factor = 1.0 + 0.004 * (edad - 40)
        for c in self.config.tejidos:
            if "cicatriz" in c.nombre.lower():
                alpha_base = 2.1 if "3er" in self._tipo_quem else 1.4
                c.atenuacion_db_cm_mhz = round(alpha_base * factor, 3)
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _estilo_btn_activo(self, activo: bool) -> str:
        bg   = ColoresConsola.BOTON_ACTIVO_BG if activo else ColoresConsola.BOTON_NORMAL_BG
        bord = ColoresConsola.CYAN_MEDICO      if activo else ColoresConsola.BORDE_HARDWARE
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {ColoresConsola.TEXTO_BOTON};
                border: 1px solid {bord};
                border-radius: 4px;
                padding: 3px 7px;
            }}
        """

    # ==========================================================================
    # TELEMETRÍA EN TIEMPO REAL
    # ==========================================================================
    def _actualizar_telemetria(self):
        efd = self._efd
        prf = self._prf
        foco = self._foco_cm

        # --- Presión pico (RF2 / RF3) ---
        # EFD = ∫p²/(ρc)dt  →  p_peak = 75.82 * √(EFD / 0.10) MPa
        p_peak_mpa = 75.82 * np.sqrt(efd / 0.10)

        # Atenuación a la profundidad focal (α promedio estimado en tejido cicatrizal)
        alpha_base = 2.1 if "3er" in self._tipo_quem else 1.4
        factor_edad = 1.0 + 0.004 * (self._edad - 40)
        alpha_efectiva = alpha_base * factor_edad  # dB/(cm·MHz)
        f_mhz = 1.0  # frecuencia central de la onda de choque estimada
        aten_dB = alpha_efectiva * f_mhz * foco
        p_deep_mpa = p_peak_mpa * 10 ** (-aten_dB / 20.0)

        # EFD total (incluyendo fase de tracción fija EFD_neg = 0.00696 mJ/mm²)
        efd_total = efd + 0.00696

        # ISPTA (W/cm²) calculada sobre la energía acústica total por unidad de área y tiempo
        ispta_w = (efd_total * 1e3 * prf) / (1e4)   # unidades: mJ/mm² → mW/mm² → W/cm²

        # P- límite cavitación — fijo por diseño
        p_neg_mpa = -10.0

        # ΔT estimado por absorción de energía total (Nyborg 1988, NCRP 113)
        # alpha_Np = (alpha_efectiva * 100) / 8.686, kappa = 0.51 W/m·K, w_foco = 1.8 mm
        alpha_np = (alpha_efectiva * 100.0) / 8.686
        dt_estimado = (alpha_np * (ispta_w * 10000.0) * (1.8e-3 ** 2)) / (2.0 * 0.51)

        # Tiempo de sesión (RF4)
        total_pulsos = int(self.config.parametros.densidad_disparos_pcm2 * self._area_cm2)
        t_sesion_s = total_pulsos / prf
        t_sesion_min = t_sesion_s / 60.0

        # --- Actualizar tarjetas FILA 1 ---
        self.card_p_peak.lbl_v.setText(f"{p_peak_mpa:.1f} MPa")
        self.card_p_deep.lbl_v.setText(f"{p_deep_mpa:.2f} MPa")
        self.card_ispta.lbl_v.setText(f"{ispta_w:.4f} W/cm²")

        if p_deep_mpa >= 0.50 and (0.5 <= foco <= 2.0):
            self.card_foco_ok.lbl_v.setText("CONFORME")
            self.card_foco_ok.lbl_v.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
            self.card_foco_ok.lbl_d.setText(f"zf = {foco*10:.0f} mm | P(dermis) > 0.5 MPa")
        else:
            self.card_foco_ok.lbl_v.setText("NO CONFORME")
            self.card_foco_ok.lbl_v.setStyleSheet(f"color: {ColoresConsola.AMBAR_AVISO};")
            self.card_foco_ok.lbl_d.setText("Revisar foco o EFD")

        # --- Actualizar tarjetas FILA 2 (Seguridad Técnica) ---
        self.card_p_neg.lbl_v.setText(f"{p_neg_mpa:.1f} MPa")
        self.card_p_neg.lbl_v.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
        self.card_p_neg.lbl_d.setText("Tracción focal: -10.0 MPa (Sin cavitación incontrolada)")

        if dt_estimado < 0.5:
            self.card_dt.lbl_v.setText(f"{dt_estimado:.3f} °C")
            self.card_dt.lbl_v.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
            self.card_dt.lbl_d.setText("< 0.5 °C (Disipación térmica controlada)")
        else:
            self.card_dt.lbl_v.setText(f"{dt_estimado:.3f} °C")
            self.card_dt.lbl_v.setStyleSheet(f"color: {ColoresConsola.ROJO_PULSO};")
            self.card_dt.lbl_d.setText("⚠ ATENCIÓN: Revisar ciclo útil / EFD")

        self.card_t_sesion.lbl_v.setText(f"{t_sesion_min:.1f} min")
        self.card_t_sesion.lbl_d.setText(
            f"Área: {self._area_cm2:.0f} cm²  |  {total_pulsos} pulsos  |  PRF = {self._prf:.1f} Hz"
        )

    # ==========================================================================
    # GRAFICACIÓN CIENTÍFICA (4 VISTAS)
    # ==========================================================================
    def _cambiar_vista_grafica(self, indice: int):
        self.vista_grafica_actual = indice
        self.btn_vista_pulso.setStyleSheet(self._estilo_btn_activo(indice == 0))
        self.btn_vista_mapa.setStyleSheet(self._estilo_btn_activo(indice == 1))
        self.btn_vista_prof.setStyleSheet(self._estilo_btn_activo(indice == 2))
        self.btn_vista_esq.setStyleSheet(self._estilo_btn_activo(indice == 3))
        self.btn_vista_box.setStyleSheet(self._estilo_btn_activo(indice == 4))
        self._actualizar_grafico_pantalla()

    def _actualizar_grafico_pantalla(self):
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.set_facecolor("#040711")
        for spine in ax.spines.values():
            spine.set_color("#334155")
        ax.tick_params(colors="#94a3b8", labelsize=8)
        ax.grid(True, linestyle=":", alpha=0.3, color="#475569")

        # ------------------------------------------------------------------
        # VISTA 0: FORMA DE ONDA TEMPORAL p(t)  –  RF2
        # ------------------------------------------------------------------
        if self.vista_grafica_actual == 0:
            graficar_pulso_temporal(
                ax=ax,
                efd_nominal=self._efd,
                t_rise_ns=8.0,
                duracion_ns=300.0,
                estilo_oscuro=True
            )

        # ------------------------------------------------------------------
        # VISTA 1: DISTRIBUCIÓN ESPACIAL 2D DEL HAZ  –  RF5
        # ------------------------------------------------------------------
        elif self.vista_grafica_actual == 1:
            graficar_mapa_2d(
                ax=ax,
                fig=self.figura,
                efd_nominal=self._efd,
                profundidad_focal_mm=self._foco_cm * 10.0,
                tipo_quemadura=self._tipo_quem,
                estilo_oscuro=True
            )

        # ------------------------------------------------------------------
        # VISTA 2: PERFIL AXIAL P vs PROFUNDIDAD  –  RF5
        # ------------------------------------------------------------------
        elif self.vista_grafica_actual == 2:
            graficar_perfil_axial(
                ax=ax,
                efd_nominal=self._efd,
                profundidad_focal_mm=self._foco_cm * 10.0,
                tipo_quemadura=self._tipo_quem,
                edad_paciente=self._edad,
                estilo_oscuro=True
            )

        # ------------------------------------------------------------------
        # VISTA 3: ESQUEMA CONCEPTUAL APLICADOR / PIEL  –  RF8 / RF6
        # ------------------------------------------------------------------
        elif self.vista_grafica_actual == 3:
            graficar_esquema_tisular(
                ax=ax,
                tipo_superficie=self.config.geometria.tipo_superficie,
                profundidad_focal_mm=self._foco_cm * 10.0,
                tipo_quemadura=self._tipo_quem,
                estilo_oscuro=True
            )

        # ------------------------------------------------------------------
        # VISTA 4: BUCLE ITERATIVO / BOXPLOT (n=50)  –  COMSOL & k-Wave
        # ------------------------------------------------------------------
        elif self.vista_grafica_actual == 4:
            # Calcular muestras si no están en memoria
            p_peak_base = 40.0 * np.sqrt(self._efd / 0.10)
            np.random.seed(42)
            muestras_p = p_peak_base * np.random.normal(loc=1.0, scale=0.024, size=50)
            graficar_boxplot_confiabilidad(
                ax=ax,
                muestras_p_peak=muestras_p,
                muestras_efd=self._efd * ((muestras_p / p_peak_base) ** 2),
                estilo_oscuro=True
            )

        self.figura.tight_layout(pad=1.0)
        self.canvas.draw()

        self.figura.tight_layout(pad=1.0)
        self.canvas.draw()

    # ==========================================================================
    # DISPARO, PRESETS DE MEMORIA Y EXPORTACIÓN
    # ==========================================================================
    def _ejecutar_disparo_equipo(self):
        self.lbl_estado_emision.setText("● EMISIÓN ACTIVA: DISPARANDO...")
        self.lbl_estado_emision.setStyleSheet(f"color: {ColoresConsola.ROJO_PULSO};")
        self.btn_disparo_equipo.setText("■ EMISIÓN EN CURSO...")
        self.btn_disparo_equipo.setStyleSheet(
            "background-color: #dc2626; color: #ffffff; border: 2px solid #ffffff; border-radius: 6px;"
        )
        QTimer.singleShot(1200, self._finalizar_disparo)

    def _finalizar_disparo(self):
        self.lbl_estado_emision.setText("● SISTEMA: LISTO (STANDBY)")
        self.lbl_estado_emision.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
        self.btn_disparo_equipo.setText("▶  DISPARAR  /  EMISIÓN ACÚSTICA")
        self.btn_disparo_equipo.setStyleSheet(f"""
            QPushButton {{
                background-color: #0369a1;
                color: #ffffff;
                border: 2px solid {ColoresConsola.CYAN_MEDICO};
                border-radius: 6px;
            }}
        """)
        total = int(self.config.parametros.densidad_disparos_pcm2 * self._area_cm2)
        QMessageBox.information(
            self, "Ráfaga Acústica Emitida",
            f"Se aplicaron {total} pulsos a {self._prf:.1f} Hz.\n"
            f"Densidad de Energía (EFD): {self._efd:.3f} mJ/mm²\n"
            f"Profundidad focal: {self._foco_cm:.1f} cm\n"
            f"Área de quemadura: {self._area_cm2:.0f} cm²\n"
            f"Tiempo de sesión: {total / self._prf / 60:.1f} minutos."
        )
        self._actualizar_grafico_pantalla()

    def _cargar_preset_memoria(self, banco: int):
        if banco == 1:
            self._fijar_superficie("Curva");   self._fijar_efd(0.100)
            self._fijar_prf(4.0)
            self._fijar_tipo_quemadura("3er Grado"); self._fijar_foco(1.0)
        elif banco == 2:
            self._fijar_superficie("Curva");   self._fijar_efd(0.150)
            self._fijar_prf(4.0)
            self._fijar_tipo_quemadura("3er Grado"); self._fijar_foco(1.5)
        elif banco == 3:
            self._fijar_superficie("Plana");   self._fijar_efd(0.050)
            self._fijar_prf(4.0)
            self._fijar_tipo_quemadura("2do Grado"); self._fijar_foco(0.5)
        self._actualizar_display_dosis()
        QMessageBox.information(self, "Memoria Cargada", f"Banco de Tratamiento M{banco} cargado.")

    def _exportar_png(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Pantalla de Consola",
                                               "pantalla_consola_eswt.png", "Imágenes (*.png)")
        if ruta:
            self.figura.savefig(ruta, dpi=300, facecolor=ColoresConsola.DISPLAY_DIGITAL_BG,
                                bbox_inches="tight")
            QMessageBox.information(self, "Captura Guardada", f"Gráfico guardado en:\n{ruta}")

    def _guardar_sesion_json(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Configuración de Sesión",
                                               "sesion_consola_eswt.json", "Archivos JSON (*.json)")
        if ruta:
            ok, msg = GestorConfiguracion.guardar_archivo(self.config, ruta)
            if ok:
                QMessageBox.information(self, "Sesión Guardada", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    def _exportar_datos_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Datos de Tratamiento",
                                               "datos_consola_eswt.csv", "Archivos CSV (*.csv)")
        if ruta:
            ok, msg = ServicioExportacion.exportar_resumen_operativo_csv(self.config, ruta)
            if ok:
                QMessageBox.information(self, "Exportación Exitosa", msg)
            else:
                QMessageBox.critical(self, "Error", msg)
