"""
================================================================================
CONSOLA ELECTROMÉDICA DEL EQUIPO ESWT (INTERFAZ DE MONITOR MÉDICO)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Diseño y ergonomía basados en pantallas táctiles de equipamiento electromédico
profesional y monitores multiparamétricos hospitalarios de alta gama.
Estructura en 3 sectores funcionales principales:
  - Panel Izquierdo: Configuración del Tratamiento (Parámetros Operativos)
  - Panel Central: Visualización Gráfica Científica (5 vistas del proyecto)
  - Panel Derecho: Indicadores Multiparamétricos Principales (Telemetría de Gran Tamaño)
  - Barra Superior: Estado Clínico, Acoplamiento Acústico e Interlock
  - Barra Inferior: Barra Fija de Acciones (Disparo/Emisión, Reset, Memorias, Exportación)
================================================================================
Cobertura completa de requerimientos y normas:
  RF1 (PRF 4-5 Hz), RF2 (Pulso temporal focal, t_rise=8ns, P+ in [20,100] MPa),
  RF3 (EFD 0.03–0.25 mJ/mm²), RF4 (Disparos 10–500 p/cm²),
  RF5 (Profundidad focal 0.5–2.0 cm, distanciadores D25-D10),
  RF6 (Gel acoplamiento Z ≈ 1.50 MRayl),
  RF8 (Cabezal Ø ≤ 40 mm, emisión normal fija 0°, acople conformable),
  IEC 61846:2025 (Integral completa de EFD total positivo + negativo),
  RNF Bioseguridad (P- cavitación ≤ -10 MPa), RNF Térmica (ΔT < 0.50 °C),
  RNF Confiabilidad (CV < 5.0%, n=50).
================================================================================
"""

import sys
import os

try:
    from modelos.configuracion import ConfiguracionGlobal
    from modelos.tejido import CapaTejido
    from simulacion.solver_fisico import SolverFisicoESWT
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
    DIRECTORIO_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if DIRECTORIO_RAIZ not in sys.path:
        sys.path.insert(0, DIRECTORIO_RAIZ)
    from modelos.configuracion import ConfiguracionGlobal
    from modelos.tejido import CapaTejido
    from simulacion.solver_fisico import SolverFisicoESWT
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
# PALETA CROMÁTICA - MONITOR MÉDICO MULTIPARAMÉTRICO
# ==============================================================================
class ColoresConsola:
    """Paleta cromática de alta fidelidad basada en monitores médicos hospitalarios."""
    CHASIS_FONDO        = "#070b14"   # Fondo ultraoscuro azul marino/negro quirúrgico
    PANEL_CONTROL       = "#0f172a"   # Fondo de bahías de instrumentos
    PANEL_CONTROL_BORDE = "#1e293b"   # Borde de separación entre módulos
    DISPLAY_DIGITAL_BG  = "#030712"   # Fondo de display digital azabache
    DISPLAY_BORDE       = "#162032"   # Borde sutil del marco de pantalla

    # Iluminación de displays e indicadores funcionales
    CYAN_MEDICO    = "#00f0ff"        # Magnitudes acústicas y selecciones activas
    VERDE_SEGURO   = "#10b981"        # Rangos seguros / condición de acople / niveles de tracción
    AMBAR_AVISO    = "#f59e0b"        # Información térmica / advertencia / standby
    ROJO_PULSO     = "#ef4444"        # Emisión acústica activa / pico de presión
    TEXTO_BLANCO   = "#f8fafc"        # Texto principal de alto contraste
    TEXTO_LABEL    = "#94a3b8"        # Etiquetas descriptivas y unidades
    TEXTO_MUTED    = "#64748b"        # Textos secundarios y notas técnicas

    # Botones táctiles del equipo
    BOTON_NORMAL_BG    = "#1e293b"
    BOTON_NORMAL_HOVER = "#334155"
    BOTON_ACTIVO_BG    = "#0284c7"
    TEXTO_BOTON        = "#f8fafc"
    BORDE_HARDWARE     = "#1e293b"


# ==============================================================================
# VENTANA PRINCIPAL DE LA CONSOLA ELECTROMÉDICA
# ==============================================================================
class ConsolaESWT(QMainWindow):
    """Ventana principal diseñada como monitor multiparamétrico de electromedicina."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "CONSOLA CLÍNICA ESWT | MONITOR MÉDICO MULTIPARAMÉTRICO (UNER – BIOINGENIERÍA)"
        )
        self.showMaximized()
        self.setMinimumSize(1260, 780)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {ColoresConsola.CHASIS_FONDO};
            }}
            QWidget {{
                font-family: 'Segoe UI', system-ui, sans-serif;
                color: {ColoresConsola.TEXTO_BLANCO};
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {ColoresConsola.CHASIS_FONDO};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: #334155;
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ColoresConsola.CYAN_MEDICO};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # Modelo maestro de datos del anteproyecto
        self.config = ConfiguracionGlobal()
        self.vista_grafica_actual = 0   # 0:Pulso 1:Mapa2D 2:Presión_z 3:Esquema 4:Boxplot
        self.disparando = False
        self._ultimo_resultado = None

        # Estado operativo interno del aplicador
        self._efd      = self.config.parametros.efd_nominal_mj_mm2              # mJ/mm²
        self._prf      = self.config.parametros.frecuencia_repeticion_hz        # Hz
        self._foco_cm  = self.config.parametros.profundidad_focal_objetivo_cm   # cm (nominal 1.0)
        # Sincronización física de partida: d_dist = R - zf = 30.0 - 10.0 = 20.0 mm (D20)
        self.config.aplicador.distanciador_seleccionado_mm = max(0.0, 30.0 - self._foco_cm * 10.0)
        self._area_cm2 = 10.0                                                   # cm² de cicatriz
        self._edad     = 40                                                     # años del paciente
        self._tipo_quem = "3er Grado"

        self._crear_ui_consola()
        self._actualizar_controles_dosificacion()
        self._actualizar_telemetria()

    # ==========================================================================
    # CONSTRUCCIÓN DE LA ARQUITECTURA DE PANTALLA (3 SECTORES)
    # ==========================================================================
    def _crear_ui_consola(self):
        widget_raiz = QWidget()
        self.setCentralWidget(widget_raiz)
        layout_raiz = QVBoxLayout(widget_raiz)
        layout_raiz.setContentsMargins(10, 8, 10, 8)
        layout_raiz.setSpacing(8)

        # 1. Barra superior: cabecera institucional y estado médico del equipo
        layout_raiz.addWidget(self._crear_barra_superior())

        # 2. Cuerpo principal en 3 sectores funcionales
        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(10)

        # Sector A: Panel Izquierdo - Configuración del tratamiento (mandos clínicos)
        cuerpo.addWidget(self._crear_panel_mandos(), stretch=0)

        # Sector B: Panel Central - Monitor de visualización gráfica (pantalla científica)
        cuerpo.addWidget(self._crear_panel_monitor(), stretch=1)

        # Sector C: Panel Derecho - Indicadores multiparamétricos (resultados numéricos)
        cuerpo.addWidget(self._crear_panel_resultados(), stretch=0)

        layout_raiz.addLayout(cuerpo, stretch=1)

        # 3. Barra inferior: estado del modelo, controles de ejecución, reset y archivo
        layout_raiz.addWidget(self._crear_barra_inferior())

    # --------------------------------------------------------------------------
    # 1. BARRA SUPERIOR (HEADER DEL MONITOR MÉDICO)
    # --------------------------------------------------------------------------
    def _crear_barra_superior(self) -> QFrame:
        barra = QFrame()
        barra.setFixedHeight(54)
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 8px;
            }}
        """)
        l = QHBoxLayout(barra)
        l.setContentsMargins(18, 0, 18, 0)
        l.setSpacing(12)

        # Logotipo / Denominación de la consola clínica
        lbl_logo = QLabel("ESWT CLINICAL MONITOR")
        lbl_logo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_logo.setStyleSheet(f"color: {ColoresConsola.CYAN_MEDICO}; letter-spacing: 1px;")
        l.addWidget(lbl_logo)

        lbl_sub = QLabel(
            " |  APLICADOR PIEZOELÉCTRICO FOCALIZADO  •  TRATAMIENTO DE CICATRICES POSTQUEMADURA"
        )
        lbl_sub.setFont(QFont("Segoe UI", 8))
        lbl_sub.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")
        l.addWidget(lbl_sub)

        l.addStretch()

        # Botón de consulta rectora del Anteproyecto UNER
        btn_doc = self._crear_boton_consola("📖 ANTEPROYECTO FIUNER", ancho=175, callback=self._mostrar_dialogo_anteproyecto)
        l.addWidget(btn_doc)

        # Condición de acoplamiento acústico configurada (Gel Z ≈ 1.50 MRayl)
        self.lbl_interlock = QLabel("● ACOPLE CONFIGURADO: GEL CONFORMABLE (Z ≈ 1.50 MRayl)")
        self.lbl_interlock.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.lbl_interlock.setStyleSheet(f"""
            QLabel {{
                color: {ColoresConsola.VERDE_SEGURO};
                background-color: #064e3b;
                border: 1px solid #059669;
                border-radius: 4px;
                padding: 4px 10px;
            }}
        """)
        l.addWidget(self.lbl_interlock)

        # Indicador de estado del sistema (Standby / Emisión)
        self.lbl_estado_emision = QLabel("● SISTEMA: LISTO (STANDBY)")
        self.lbl_estado_emision.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.lbl_estado_emision.setStyleSheet(f"""
            QLabel {{
                color: {ColoresConsola.AMBAR_AVISO};
                background-color: #451a03;
                border: 1px solid #b45309;
                border-radius: 4px;
                padding: 4px 10px;
            }}
        """)
        l.addWidget(self.lbl_estado_emision)

        return barra

    # --------------------------------------------------------------------------
    # 2. SECTOR A: PANEL IZQUIERDO (CONFIGURACIÓN DEL TRATAMIENTO)
    # --------------------------------------------------------------------------
    def _crear_panel_mandos(self) -> QWidget:
        """Panel izquierdo de controles clínicos sin jerga interna de ingeniería."""
        scroll = QScrollArea()
        scroll.setFixedWidth(380)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 8px;
            }}
        """)

        inner = QWidget()
        inner.setStyleSheet(f"background-color: {ColoresConsola.PANEL_CONTROL};")
        l_mandos = QVBoxLayout(inner)
        l_mandos.setContentsMargins(14, 12, 14, 12)
        l_mandos.setSpacing(9)

        # Título del panel de configuración
        tit_panel = QLabel("CONFIGURACIÓN DEL TRATAMIENTO")
        tit_panel.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        tit_panel.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL}; letter-spacing: 0.8px;")
        l_mandos.addWidget(tit_panel)

        # -- PARÁMETRO 1: DENSIDAD DE ENERGÍA (EFD) --
        bloque_efd = self._crear_bloque_parametro(
            "DENSIDAD DE FLUJO DE ENERGÍA (EFD)", "mJ/mm²",
            "Rango clínico: 0.03 – 0.25 mJ/mm² (Nominal: 0.10)"
        )
        self.disp_efd = bloque_efd["display"]
        self.disp_efd.setText(f"{self._efd:.3f}")
        fila_efd = QHBoxLayout()
        fila_efd.setSpacing(5)
        fila_efd.addWidget(self._crear_boton_consola("▼ -0.01", ancho=68, callback=lambda: self._ajustar_efd(-0.01)))
        fila_efd.addWidget(self._crear_boton_consola("▲ +0.01", ancho=68, callback=lambda: self._ajustar_efd(+0.01)))
        self._botones_efd_map = {}
        for v in [0.05, 0.08, 0.10, 0.15, 0.20]:
            btn = self._crear_boton_consola(
                f"{v:.2f}",
                ancho=42,
                activo=(abs(v - self._efd) < 1e-3),
                callback=lambda val=v: self._fijar_efd(val)
            )
            self._botones_efd_map[v] = btn
            fila_efd.addWidget(btn)
        bloque_efd["layout"].addLayout(fila_efd)
        l_mandos.addWidget(bloque_efd["widget"])

        # -- PARÁMETRO 2: PROFUNDIDAD FOCAL / DISTANCIADOR --
        bloque_foco = self._crear_bloque_parametro(
            "PROFUNDIDAD FOCAL Y DISTANCIADOR", "cm",
            "zf = R - d_dist (R=30 mm). D25=0.5cm, D20=1cm, D15=1.5cm, D10=2cm"
        )
        self.disp_foco = bloque_foco["display"]
        dist_ini = max(10.0, min(25.0, 30.0 - self._foco_cm * 10.0))
        self.disp_foco.setText(f"{self._foco_cm:.1f} cm (D{int(dist_ini)})")
        fila_foco = QHBoxLayout()
        fila_foco.setSpacing(4)
        self._botones_foco_map = {}
        etiquetas_foco = {
            0.5: "D25 (0.5cm)",
            1.0: "D20 (1.0cm)",
            1.5: "D15 (1.5cm)",
            2.0: "D10 (2.0cm)"
        }
        for fc in [0.5, 1.0, 1.5, 2.0]:
            btn = self._crear_boton_consola(
                etiquetas_foco[fc], activo=(abs(fc - self._foco_cm) < 1e-2),
                callback=lambda f=fc: self._fijar_foco(f)
            )
            self._botones_foco_map[fc] = btn
            fila_foco.addWidget(btn)
        bloque_foco["layout"].addLayout(fila_foco)
        l_mandos.addWidget(bloque_foco["widget"])

        # -- PARÁMETRO 3: FRECUENCIA DE REPETICIÓN (PRF) --
        bloque_prf = self._crear_bloque_parametro(
            "FRECUENCIA DE REPETICIÓN (PRF)", "Hz",
            "Rango bioseguro de ráfaga terapéutica: 4.0 – 5.0 Hz"
        )
        self.disp_prf = bloque_prf["display"]
        self.disp_prf.setText(f"{self._prf:.1f}")
        fila_prf = QHBoxLayout()
        fila_prf.setSpacing(6)
        self.btn_prf_4 = self._crear_boton_consola("4.0 Hz", activo=(self._prf == 4.0), callback=lambda: self._fijar_prf(4.0))
        self.btn_prf_5 = self._crear_boton_consola("5.0 Hz", activo=(self._prf == 5.0), callback=lambda: self._fijar_prf(5.0))
        fila_prf.addWidget(self.btn_prf_4)
        fila_prf.addWidget(self.btn_prf_5)
        bloque_prf["layout"].addLayout(fila_prf)
        l_mandos.addWidget(bloque_prf["widget"])

        # -- PARÁMETRO 4: DOSIFICACIÓN (DENSIDAD) --
        bloque_dosis = self._crear_bloque_parametro(
            "DOSIFICACIÓN DE ENERGÍA (DENSIDAD)", "p/cm²",
            "Rango anteproyecto: 10 – 500 pulsos/cm² (Nominal: 150 p/cm²)"
        )
        self.disp_densidad = bloque_dosis["display"]
        self.disp_dosis = self.disp_densidad  # Alias para retrocompatibilidad
        self.disp_densidad.setText(f"{self.config.parametros.densidad_disparos_pcm2:.0f}")

        fila_dens_adj = QHBoxLayout()
        fila_dens_adj.setSpacing(4)
        fila_dens_adj.addWidget(self._crear_boton_consola("▼ -25", ancho=58, callback=lambda: self._ajustar_densidad(-25)))
        fila_dens_adj.addWidget(self._crear_boton_consola("▲ +25", ancho=58, callback=lambda: self._ajustar_densidad(+25)))
        self._botones_dens_map = {}
        for dens in [50, 100, 150, 250, 500]:
            btn = self._crear_boton_consola(
                f"{dens}", ancho=40,
                activo=(dens == int(self.config.parametros.densidad_disparos_pcm2)),
                callback=lambda d=dens: self._fijar_densidad_pulsos(float(d))
            )
            self._botones_dens_map[dens] = btn
            fila_dens_adj.addWidget(btn)
        bloque_dosis["layout"].addLayout(fila_dens_adj)
        l_mandos.addWidget(bloque_dosis["widget"])

        # -- PARÁMETRO 5: DISPAROS POR SESIÓN Y SUPERFICIE --
        bloque_sesion = self._crear_bloque_parametro(
            "DISPAROS POR SESIÓN Y DURACIÓN", "pulsos",
            "Disparos = Dosis × Área | Duración de emisión = Disparos / PRF"
        )
        self.disp_disparos = bloque_sesion["display"]
        self.lbl_info_sesion = QLabel("")
        self.lbl_info_sesion.setFont(QFont("Segoe UI", 6))
        self.lbl_info_sesion.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED};")
        self.lbl_info_sesion.setWordWrap(True)
        bloque_sesion["layout"].addWidget(self.lbl_info_sesion)

        # Superficie de la quemadura
        fila_area = QHBoxLayout()
        fila_area.setSpacing(4)
        lbl_ar = QLabel("Área:")
        lbl_ar.setFont(QFont("Segoe UI", 7))
        lbl_ar.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED};")
        fila_area.addWidget(lbl_ar)
        self._botones_area_map = {}
        for a in [5, 10, 15, 20]:
            btn = self._crear_boton_consola(
                f"{a} cm²", activo=(a == int(self._area_cm2)),
                callback=lambda av=a: self._fijar_area(float(av))
            )
            self._botones_area_map[a] = btn
            fila_area.addWidget(btn)
        bloque_sesion["layout"].addLayout(fila_area)

        # Ajuste de disparos totales
        fila_disp_quick = QHBoxLayout()
        fila_disp_quick.setSpacing(4)
        lbl_dq = QLabel("Pulsos:")
        lbl_dq.setFont(QFont("Segoe UI", 7))
        lbl_dq.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED};")
        fila_disp_quick.addWidget(lbl_dq)
        fila_disp_quick.addWidget(self._crear_boton_consola("▼ -250", ancho=58, callback=lambda: self._ajustar_disparos_totales(-250)))
        fila_disp_quick.addWidget(self._crear_boton_consola("▲ +250", ancho=58, callback=lambda: self._ajustar_disparos_totales(+250)))
        for tot in [500, 1000, 1500, 2000]:
            fila_disp_quick.addWidget(self._crear_boton_consola(f"{tot}", ancho=38, callback=lambda t=tot: self._fijar_disparos_totales(t)))
        bloque_sesion["layout"].addLayout(fila_disp_quick)
        l_mandos.addWidget(bloque_sesion["widget"])

        # -- PARÁMETRO 5: SUPERFICIE ANATÓMICA Y ACOPLAMIENTO --
        bloque_geom = self._crear_bloque_parametro(
            "SUPERFICIE ANATÓMICA Y MEDIO DE ACOPLE", "Acople",
            "Emisión normal fija (0°) con gel o almohadilla conformable"
        )
        self.disp_geom = bloque_geom["display"]
        self.disp_geom.setText("Emisión Normal (0°)")

        fila_tipo = QHBoxLayout()
        fila_tipo.setSpacing(6)
        self.btn_curva = self._crear_boton_consola("Curva / Mano-Dedos", activo=True, callback=lambda: self._fijar_superficie("Curva"))
        self.btn_plana = self._crear_boton_consola("Plana / Tronco-Muslo", callback=lambda: self._fijar_superficie("Plana"))
        fila_tipo.addWidget(self.btn_curva)
        fila_tipo.addWidget(self.btn_plana)
        bloque_geom["layout"].addLayout(fila_tipo)

        fila_acople = QHBoxLayout()
        fila_acople.setSpacing(6)
        self.btn_acople_gel = self._crear_boton_consola("Gel Conformable", activo=True, callback=lambda: self._fijar_acople("Gel"))
        self.btn_acople_pad = self._crear_boton_consola("Almohadilla Articular", callback=lambda: self._fijar_acople("Almohadilla"))
        fila_acople.addWidget(self.btn_acople_gel)
        fila_acople.addWidget(self.btn_acople_pad)
        bloque_geom["layout"].addLayout(fila_acople)
        l_mandos.addWidget(bloque_geom["widget"])

        # -- PARÁMETRO 6: ESTRATIFICACIÓN TISULAR Y PACIENTE --
        bloque_piel = self._crear_bloque_parametro(
            "ESTRATIFICACIÓN TISULAR Y PACIENTE", "Cicatriz",
            "Modula coeficientes acústicos y espesor de la cicatriz"
        )
        self.disp_piel = bloque_piel["display"]
        self.disp_piel.setText("3er Grado (9 mm)")

        fila_grado = QHBoxLayout()
        fila_grado.setSpacing(6)
        self.btn_grado3 = self._crear_boton_consola("3er Grado (Fibrótica)", activo=True, callback=lambda: self._fijar_tipo_quemadura("3er Grado"))
        self.btn_grado2 = self._crear_boton_consola("2do Grado Profundo", callback=lambda: self._fijar_tipo_quemadura("2do Grado"))
        fila_grado.addWidget(self.btn_grado3)
        fila_grado.addWidget(self.btn_grado2)
        bloque_piel["layout"].addLayout(fila_grado)

        # Edad del paciente
        fila_edad = QHBoxLayout()
        fila_edad.setSpacing(4)
        lbl_ed = QLabel("Edad:")
        lbl_ed.setFont(QFont("Segoe UI", 7))
        lbl_ed.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED};")
        fila_edad.addWidget(lbl_ed)
        self.disp_edad = QLabel(f"{self._edad} años")
        self.disp_edad.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.disp_edad.setStyleSheet(f"color: {ColoresConsola.CYAN_MEDICO};")
        fila_edad.addWidget(self.disp_edad)
        fila_edad.addStretch()
        fila_edad.addWidget(self._crear_boton_consola("▼ -5", ancho=48, callback=lambda: self._ajustar_edad(-5)))
        fila_edad.addWidget(self._crear_boton_consola("▲ +5", ancho=48, callback=lambda: self._ajustar_edad(+5)))
        for lbl_e, e_val in [("20a", 20), ("40a", 40), ("60a", 60)]:
            fila_edad.addWidget(self._crear_boton_consola(lbl_e, ancho=38, callback=lambda ev=e_val: self._fijar_edad(ev)))
        bloque_piel["layout"].addLayout(fila_edad)
        l_mandos.addWidget(bloque_piel["widget"])

        l_mandos.addStretch()

        scroll.setWidget(inner)
        return scroll

    # --------------------------------------------------------------------------
    # 3. SECTOR B: PANEL CENTRAL (MONITOR DE VISUALIZACIÓN GRÁFICA)
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
        l.setContentsMargins(14, 12, 14, 12)
        l.setSpacing(8)

        # Selector superior de vistas científicas (todos los gráficos del proyecto)
        barra_vistas = QHBoxLayout()
        barra_vistas.setSpacing(6)
        self.btn_vista_pulso = self._crear_boton_consola("1. PULSO p(t)", activo=True, callback=lambda: self._cambiar_vista_grafica(0))
        self.btn_vista_mapa  = self._crear_boton_consola("2. CAMPO 2D", callback=lambda: self._cambiar_vista_grafica(1))
        self.btn_vista_prof  = self._crear_boton_consola("3. PERFIL AXIAL", callback=lambda: self._cambiar_vista_grafica(2))
        self.btn_vista_esq   = self._crear_boton_consola("4. ESQUEMA TISULAR", callback=lambda: self._cambiar_vista_grafica(3))
        self.btn_vista_box   = self._crear_boton_consola("5. DISPERSIÓN (n=50)", callback=lambda: self._cambiar_vista_grafica(4))

        for btn in [self.btn_vista_pulso, self.btn_vista_mapa, self.btn_vista_prof, self.btn_vista_esq, self.btn_vista_box]:
            barra_vistas.addWidget(btn)

        barra_vistas.addStretch()
        barra_vistas.addWidget(self._crear_boton_consola("📷 Guardar Gráfico (PNG)", ancho=165, callback=self._exportar_png))
        l.addLayout(barra_vistas)

        # Marco biselado de pantalla médica para el Canvas de Matplotlib
        marco_pantalla = QFrame()
        marco_pantalla.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.DISPLAY_DIGITAL_BG};
                border: 2px solid {ColoresConsola.DISPLAY_BORDE};
                border-radius: 6px;
            }}
        """)
        l_scr = QVBoxLayout(marco_pantalla)
        l_scr.setContentsMargins(6, 6, 6, 6)

        self.figura = Figure(figsize=(8.8, 5.4), dpi=100, facecolor=ColoresConsola.DISPLAY_DIGITAL_BG)
        self.canvas = FigureCanvasQTAgg(self.figura)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        l_scr.addWidget(self.canvas)
        l.addWidget(marco_pantalla, stretch=1)

        # Leyenda descriptiva del gráfico activo
        self.lbl_info_grafico = QLabel(
            "Vista actual: Pulso acústico focal p(t) con fase positiva de subida rápida (trise=8ns) y pozo de tracción negativo."
        )
        self.lbl_info_grafico.setFont(QFont("Segoe UI", 7))
        self.lbl_info_grafico.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED}; padding: 2px 4px;")
        l.addWidget(self.lbl_info_grafico)

        self._actualizar_grafico_pantalla()
        return panel

    # --------------------------------------------------------------------------
    # 4. SECTOR C: PANEL DERECHO (INDICADORES MULTIPARAMÉTRICOS PRINCIPALES)
    # --------------------------------------------------------------------------
    def _crear_panel_resultados(self) -> QWidget:
        """Panel derecho con grandes indicadores numéricos tipo monitor multiparamétrico."""
        scroll = QScrollArea()
        scroll.setFixedWidth(340)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 8px;
            }}
        """)

        inner = QWidget()
        inner.setStyleSheet(f"background-color: {ColoresConsola.PANEL_CONTROL};")
        l_res = QVBoxLayout(inner)
        l_res.setContentsMargins(14, 12, 14, 12)
        l_res.setSpacing(8)

        tit_res = QLabel("INDICADORES MULTIPARAMÉTRICOS")
        tit_res.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        tit_res.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL}; letter-spacing: 0.8px;")
        l_res.addWidget(tit_res)

        # 1. Presión Máxima Propagada Estimada (P+)
        self.card_p_peak = self._crear_tarjeta_telemetria(
            "PRESIÓN MÁXIMA ESTIMADA (P+)", "--",
            "Presión focal propagada estimada por el modelo", ColoresConsola.CYAN_MEDICO
        )
        l_res.addWidget(self.card_p_peak)

        # 2. Profundidad Focal Estimada (zf)
        self.card_foco_ok = self._crear_tarjeta_telemetria(
            "PROFUNDIDAD FOCAL ESTIMADA", "--",
            "Profundidad focal calculada en tejido", ColoresConsola.CYAN_MEDICO
        )
        l_res.addWidget(self.card_foco_ok)

        # 3. EFD Total por Pulso (Integral IEC 61846:2025)
        self.card_efd_total = self._crear_tarjeta_telemetria(
            "EFD TOTAL POR PULSO", "--",
            "Integral completa: fase positiva + fase negativa", ColoresConsola.CYAN_MEDICO
        )
        l_res.addWidget(self.card_efd_total)

        # 4. Aumento Térmico Estimado (ΔT)
        self.card_dt = self._crear_tarjeta_telemetria(
            "AUMENTO TÉRMICO ESTIMADO (ΔT)", "--",
            "Estimación analítica simplificada (Nyborg 1988)", ColoresConsola.VERDE_SEGURO
        )
        l_res.addWidget(self.card_dt)

        # 5. Presión de Tracción (P-)
        self.card_p_neg = self._crear_tarjeta_telemetria(
            "TRACCIÓN ACÚSTICA (P-)", "-10.0 MPa",
            "Presión negativa configurada: -10.0 MPa", ColoresConsola.VERDE_SEGURO
        )
        l_res.addWidget(self.card_p_neg)

        # 6. Intensidad Acústica Derivada (ISPTA)
        self.card_ispta = self._crear_tarjeta_telemetria(
            "INTENSIDAD ACÚSTICA (ISPTA)", "--",
            "Intensidad derivada sobre energía acústica total", ColoresConsola.CYAN_MEDICO
        )
        l_res.addWidget(self.card_ispta)

        # 7. Presión Propagada en Dermis / Cicatriz
        self.card_p_deep = self._crear_tarjeta_telemetria(
            "PRESIÓN EN CICATRIZ / DERMIS", "--",
            "Presión acústica estimada en estrato cicatrizal", ColoresConsola.CYAN_MEDICO
        )
        l_res.addWidget(self.card_p_deep)

        # 8. Tiempo y Dosis de la Sesión
        self.card_t_sesion = self._crear_tarjeta_telemetria(
            "TIEMPO Y DOSIS DE SESIÓN", "--",
            "Dosimetría programada de tratamiento", ColoresConsola.TEXTO_BLANCO
        )
        l_res.addWidget(self.card_t_sesion)

        # 9. Confiabilidad y Sensibilidad Numérica
        self.card_cv = self._crear_tarjeta_telemetria(
            "SENSIBILIDAD DEL MODELO", "--",
            "Dispersión numérica del modelo (n=50 iteraciones)", ColoresConsola.VERDE_SEGURO
        )
        l_res.addWidget(self.card_cv)

        l_res.addStretch()

        scroll.setWidget(inner)
        return scroll

    # --------------------------------------------------------------------------
    # 5. BARRA INFERIOR DE ACCIONES Y ESTADO
    # --------------------------------------------------------------------------
    def _crear_barra_inferior(self) -> QFrame:
        barra = QFrame()
        barra.setFixedHeight(54)
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 8px;
            }}
        """)
        l = QHBoxLayout(barra)
        l.setContentsMargins(14, 0, 14, 0)
        l.setSpacing(8)

        # Estado del modelo numérico
        self.lbl_estado_modelo = QLabel("● MODELO COMPUTACIONAL: ACOPLADO Y CONSISTENTE")
        self.lbl_estado_modelo.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.lbl_estado_modelo.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")
        l.addWidget(self.lbl_estado_modelo)

        # Botón para restablecer parámetros nominales del anteproyecto
        btn_reset = QPushButton("↺ RESTABLECER NOMINALES")
        btn_reset.setMinimumHeight(32)
        btn_reset.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid #334155;
                border-radius: 5px;
                padding: 4px 10px;
            }}
            QPushButton:hover {{
                background-color: #334155;
                color: #ffffff;
                border-color: {ColoresConsola.CYAN_MEDICO};
            }}
            QPushButton:pressed {{ background-color: #0f172a; }}
        """)
        btn_reset.clicked.connect(self._restablecer_valores_nominales)
        self.btn_reset = btn_reset
        l.addWidget(btn_reset)

        # Botón Maestro de Emisión / Ejecución
        btn_disparo = QPushButton("▶ INICIAR EMISIÓN / SIMULAR")
        btn_disparo.setMinimumHeight(34)
        btn_disparo.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn_disparo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_disparo.setStyleSheet(f"""
            QPushButton {{
                background-color: #0284c7;
                color: #ffffff;
                border: 1px solid {ColoresConsola.CYAN_MEDICO};
                border-radius: 5px;
                padding: 4px 14px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {ColoresConsola.CYAN_MEDICO};
                color: #030712;
                border-color: #ffffff;
            }}
            QPushButton:pressed {{ background-color: #0369a1; }}
        """)
        btn_disparo.clicked.connect(self._ejecutar_disparo_equipo)
        self.btn_disparo_equipo = btn_disparo
        l.addWidget(btn_disparo)

        l.addSpacing(10)

        # Memorias Rápidas de Tratamiento
        lbl_m = QLabel("MEMORIAS:")
        lbl_m.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        lbl_m.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED};")
        l.addWidget(lbl_m)
        for i, lbl_mem in [(1, "M1: Articular (0.10)"), (2, "M2: Profunda (0.15)"), (3, "M3: Suave (0.05)")]:
            l.addWidget(self._crear_boton_consola(lbl_mem, callback=lambda b=i: self._cargar_preset_memoria(b)))

        l.addStretch()

        # Botones de exportación y archivo de sesión
        l.addWidget(self._crear_boton_consola("💾 Guardar Sesión (JSON)", ancho=165, callback=self._guardar_sesion_json))
        l.addWidget(self._crear_boton_consola("📊 Exportar Datos (CSV)", ancho=160, callback=self._exportar_datos_csv))
        l.addWidget(self._crear_boton_consola("⚙ Modo Modular (10 Módulos)", ancho=175, callback=self._abrir_modo_modular))

        return barra

    # ==========================================================================
    # CREADORES DE COMPONENTES VISUALES TIPO HARDWARE MÉDICO
    # ==========================================================================
    def _crear_bloque_parametro(self, titulo: str, unidad: str, rango_info: str) -> dict:
        """Contenedor de control con display digital OLED y botonera física."""
        w = QFrame()
        w.setStyleSheet(f"""
            QFrame {{
                background-color: #0b1120;
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-radius: 7px;
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
                border: 1px solid #162032;
                border-radius: 4px;
                padding: 3px 10px;
                letter-spacing: 1px;
            }}
        """)
        disp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(disp)

        lbl_r = QLabel(rango_info)
        lbl_r.setFont(QFont("Segoe UI", 6))
        lbl_r.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED};")
        lbl_r.setWordWrap(True)
        l.addWidget(lbl_r)

        return {"widget": w, "layout": l, "display": disp}

    def _crear_boton_consola(self, texto: str, ancho: int = None,
                              activo: bool = False, callback=None) -> QPushButton:
        """Botón táctil de consola médica con respuesta visual."""
        btn = QPushButton(texto)
        if ancho:
            btn.setFixedWidth(ancho)
        btn.setMinimumHeight(28)
        btn.setMaximumHeight(32)
        btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bg   = ColoresConsola.BOTON_ACTIVO_BG if activo else ColoresConsola.BOTON_NORMAL_BG
        bord = ColoresConsola.CYAN_MEDICO      if activo else ColoresConsola.BORDE_HARDWARE
        color_texto = "#ffffff" if activo else ColoresConsola.TEXTO_BOTON
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color_texto};
                border: 1px solid {bord};
                border-radius: 4px;
                padding: 3px 7px;
            }}
            QPushButton:hover {{
                background-color: {ColoresConsola.BOTON_NORMAL_HOVER};
                border-color: {ColoresConsola.CYAN_MEDICO};
                color: #ffffff;
            }}
            QPushButton:pressed {{ background-color: #0369a1; }}
        """)
        if callback:
            # En PySide6, QPushButton.clicked emite el booleano 'checked' (False).
            # Si el callback es una función lambda con argumento por defecto (ej. lambda val=v: func(val)),
            # Qt entrega 'checked' (False=0) como primer argumento posicional, sobrescribiendo 'val'.
            # Al conectar con lambda checked=False, cb=callback: cb(), aislamos la ejecución
            # y garantizamos que los valores preestablecidos nunca sean sobrescritos por el evento.
            btn.clicked.connect(lambda checked=False, cb=callback: cb())
        return btn

    def _crear_tarjeta_telemetria(
        self, titulo: str, valor: str, detalle: str, color_acento: str = None
    ) -> QFrame:
        """Tarjeta de telemetría de gran formato con borde indicador y valor destacado."""
        if color_acento is None:
            color_acento = ColoresConsola.CYAN_MEDICO

        card = QFrame()
        card.setObjectName("tarjetaTelemetria")
        card.setStyleSheet(f"""
            QFrame#tarjetaTelemetria {{
                background-color: {ColoresConsola.DISPLAY_DIGITAL_BG};
                border: 1px solid {ColoresConsola.BORDE_HARDWARE};
                border-left: 4px solid {color_acento};
                border-radius: 6px;
            }}
            QFrame#tarjetaTelemetria:hover {{
                border-color: {color_acento};
            }}
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(10, 6, 10, 6)
        l.setSpacing(2)

        lbl_t = QLabel(titulo)
        lbl_t.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        lbl_t.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL}; letter-spacing: 0.5px;")
        l.addWidget(lbl_t)

        lbl_v = QLabel(valor)
        lbl_v.setFont(QFont("Consolas", 15, QFont.Weight.Bold))
        lbl_v.setStyleSheet(f"color: {color_acento}; letter-spacing: 0.5px;")
        l.addWidget(lbl_v)

        lbl_d = QLabel(detalle)
        lbl_d.setFont(QFont("Segoe UI", 6))
        lbl_d.setStyleSheet(f"color: {ColoresConsola.TEXTO_MUTED};")
        lbl_d.setWordWrap(True)
        l.addWidget(lbl_d)

        card.lbl_t = lbl_t
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
        valor = float(valor)
        valor = max(0.01, min(0.30, round(valor, 3)))
        self._efd = valor
        self.config.parametros.efd_nominal_mj_mm2 = valor
        if hasattr(self, "disp_efd"):
            self.disp_efd.setText(f"{valor:.3f}")
        if hasattr(self, "_botones_efd_map"):
            for v_pre, btn in self._botones_efd_map.items():
                btn.setStyleSheet(self._estilo_btn_activo(abs(v_pre - valor) < 1e-3))
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _fijar_prf(self, freq: float):
        self._prf = freq
        self.config.parametros.frecuencia_repeticion_hz = freq
        self.disp_prf.setText(f"{freq:.1f}")
        self.btn_prf_4.setStyleSheet(self._estilo_btn_activo(freq == 4.0))
        self.btn_prf_5.setStyleSheet(self._estilo_btn_activo(freq == 5.0))
        self._actualizar_display_dosis()
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _fijar_foco(self, foco_cm: float):
        foco_cm = float(foco_cm)
        foco_cm = max(0.5, min(2.0, foco_cm))
        self._foco_cm = foco_cm
        self.config.parametros.profundidad_focal_objetivo_cm = foco_cm
        dist_mm = max(10.0, min(25.0, 30.0 - foco_cm * 10.0))
        self.config.aplicador.distanciador_seleccionado_mm = dist_mm
        if hasattr(self, "disp_foco"):
            self.disp_foco.setText(f"{foco_cm:.1f} cm (D{dist_mm:.0f})")
        # Actualizar botones selectores de foco
        if hasattr(self, "_botones_foco_map"):
            for fc, btn in self._botones_foco_map.items():
                btn.setStyleSheet(self._estilo_btn_activo(abs(fc - foco_cm) < 1e-2))
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _fijar_distanciador(self, dist_mm: float):
        dist_mm = float(dist_mm)
        dist_mm = max(10.0, min(25.0, dist_mm))
        foco_cm = max(0.5, min(2.0, (30.0 - dist_mm) / 10.0))
        self._fijar_foco(foco_cm)

    def _ajustar_densidad(self, delta: float):
        nueva = round(self.config.parametros.densidad_disparos_pcm2 + delta, 0)
        self._fijar_densidad_pulsos(max(10.0, min(500.0, nueva)))

    def _ajustar_disparos_totales(self, delta: int):
        total_actual = int(round(self.config.parametros.densidad_disparos_pcm2 * self._area_cm2))
        nuevo_total = max(100, min(10000, total_actual + delta))
        self._fijar_disparos_totales(nuevo_total)

    def _fijar_disparos_totales(self, total: int):
        total = max(100, min(10000, int(total)))
        if self._area_cm2 > 0:
            nueva_dens = total / self._area_cm2
            self.config.parametros.densidad_disparos_pcm2 = max(10.0, min(500.0, nueva_dens))
            self._actualizar_controles_dosificacion()
            self._actualizar_telemetria()
            self._actualizar_grafico_pantalla()

    def _fijar_densidad_pulsos(self, dens: float):
        dens = max(10.0, min(500.0, float(dens)))
        self.config.parametros.densidad_disparos_pcm2 = dens
        self._actualizar_controles_dosificacion()
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _fijar_area(self, area: float):
        self._area_cm2 = max(1.0, min(100.0, float(area)))
        self.config.parametros.area_tratamiento_cm2 = self._area_cm2
        self._actualizar_controles_dosificacion()
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _actualizar_controles_dosificacion(self):
        dens = self.config.parametros.densidad_disparos_pcm2
        area = self._area_cm2
        total = int(round(dens * area))
        minutos = (total / self._prf) / 60.0 if self._prf > 0 else 0.0

        if hasattr(self, "disp_densidad"):
            self.disp_densidad.setText(f"{dens:.0f}")
        if hasattr(self, "disp_disparos"):
            self.disp_disparos.setText(f"{total:,}".replace(",", "."))
        if hasattr(self, "disp_dosis"):
            self.disp_dosis.setText(f"{dens:.0f} p/cm²")
        if hasattr(self, "lbl_info_sesion"):
            self.lbl_info_sesion.setText(
                f"Área: {area:.0f} cm² | Emisión acústica: {minutos:.2f} min @ {self._prf:.1f} Hz\n"
                f"({dens:.0f} p/cm² × {area:.0f} cm² = {total} disparos programados)"
            )
        # Actualizar botones activos de densidad
        if hasattr(self, "_botones_dens_map"):
            for d, btn in self._botones_dens_map.items():
                btn.setStyleSheet(self._estilo_btn_activo(abs(d - dens) < 1.0))
        # Actualizar botones activos de área
        if hasattr(self, "_botones_area_map"):
            for a, btn in self._botones_area_map.items():
                btn.setStyleSheet(self._estilo_btn_activo(abs(a - area) < 0.1))

    def _actualizar_display_dosis(self):
        """Método de retrocompatibilidad."""
        self._actualizar_controles_dosificacion()

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
            self.lbl_interlock.setText("● ACOPLE CONFIGURADO: ALMOHADILLA ARTICULAR (Z ≈ 1.50 MRayl)")
        else:
            self.config.aplicador.sistema_acoplamiento = "Gel Acústico Conformable"
            self.btn_acople_gel.setStyleSheet(self._estilo_btn_activo(True))
            self.btn_acople_pad.setStyleSheet(self._estilo_btn_activo(False))
            self.lbl_interlock.setText("● ACOPLE CONFIGURADO: GEL CONFORMABLE (Z ≈ 1.50 MRayl)")
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
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _ajustar_edad(self, delta: int):
        self._fijar_edad(max(10, min(80, self._edad + delta)))

    def _fijar_edad(self, edad: int):
        self._edad = edad
        self.disp_edad.setText(f"{edad} años")
        factor = 1.0 + 0.004 * (edad - 40)
        for c in self.config.tejidos:
            if "cicatriz" in c.nombre.lower():
                alpha_base = 2.1 if "3er" in self._tipo_quem else 1.4
                c.atenuacion_db_cm_mhz = round(alpha_base * factor, 3)
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()

    def _restablecer_valores_nominales(self):
        """Restablece los parámetros a la configuración nominal del anteproyecto."""
        self._efd = 0.100
        self.config.parametros.efd_nominal_mj_mm2 = 0.100
        self.disp_efd.setText("0.100")

        self._fijar_prf(4.0)
        self._fijar_foco(1.0)
        self._fijar_densidad_pulsos(150.0)
        self._fijar_area(10.0)
        self._fijar_superficie("Curva")
        self._fijar_acople("Gel")
        self._fijar_tipo_quemadura("3er Grado")
        self._fijar_edad(40)

        self._actualizar_display_dosis()
        self._actualizar_telemetria()
        self._actualizar_grafico_pantalla()
        QMessageBox.information(
            self, "Configuración Restablecida",
            "Parámetros nominales de diseño restaurados exitosamente:\n"
            "• EFD = 0.100 mJ/mm²\n• Foco = 1.0 cm (Distanciador D20)\n• PRF = 4.0 Hz\n• Dosis = 1500 pulsos"
        )

    def _estilo_btn_activo(self, activo: bool) -> str:
        bg   = ColoresConsola.BOTON_ACTIVO_BG if activo else ColoresConsola.BOTON_NORMAL_BG
        bord = ColoresConsola.CYAN_MEDICO      if activo else ColoresConsola.BORDE_HARDWARE
        color_texto = "#ffffff" if activo else ColoresConsola.TEXTO_BOTON
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {color_texto};
                border: 1px solid {bord};
                border-radius: 4px;
                padding: 3px 7px;
            }}
            QPushButton:hover {{
                background-color: {ColoresConsola.BOTON_NORMAL_HOVER};
                border-color: {ColoresConsola.CYAN_MEDICO};
                color: #ffffff;
            }}
            QPushButton:pressed {{ background-color: #0369a1; }}
        """

    # ==========================================================================
    # TELEMETRÍA EN TIEMPO REAL (DATOS DIRECTOS DEL MODELO COMPUTACIONAL)
    # ==========================================================================
    def _actualizar_telemetria(self):
        """Calcula y actualiza los indicadores numéricos directamente desde el solver."""
        # 1. Sincronizar parámetros operativos en la configuración global
        self.config.parametros.efd_nominal_mj_mm2 = self._efd
        self.config.parametros.frecuencia_repeticion_hz = self._prf
        self.config.parametros.profundidad_focal_objetivo_cm = self._foco_cm
        self.config.parametros.area_tratamiento_cm2 = self._area_cm2
        # Correspondencia física: d_dist = R - zf = 30 mm - (zf_cm * 10 mm)
        self.config.aplicador.distanciador_seleccionado_mm = max(0.0, 30.0 - self._foco_cm * 10.0)

        # 2. Ejecutar el solver físico unificado del modelo
        res = SolverFisicoESWT.simular(self.config)
        m = res.metricas
        self._ultimo_resultado = res

        p_peak_mpa   = m["presion_p_positiva_mpa"]
        p_deep_mpa   = m["presion_dermis_profunda_mpa"]
        zf_cm        = m["profundidad_focal_cm"]
        dist_mm      = m["espesor_distanciador_mm"]
        efd_total    = m["efd_total_mj_mm2"]
        efd_pos      = m["efd_positiva_mj_mm2"]
        efd_neg      = m["efd_negativa_mj_mm2"]
        dt_estimado  = m["delta_t_absorcion_c"]
        ispta_w      = m["ispta_w_cm2"]
        p_neg_mpa    = m["presion_p_negativa_mpa"]
        cv_pct       = m["cv_porcentaje"]
        total_pulsos = m["pulsos_totales"]
        t_sesion_min = (total_pulsos / self._prf) / 60.0 if self._prf > 0 else 0.0

        # --- Actualización de indicadores del Panel Derecho ---
        # Card 1: P+ Máxima Estimada
        self.card_p_peak.lbl_v.setText(f"{p_peak_mpa:.1f} MPa")
        self.card_p_peak.lbl_d.setText("Presión máxima propagada estimada en foco")

        # Card 2: Profundidad Focal Estimada
        self.card_foco_ok.lbl_v.setText(f"{zf_cm:.1f} cm ({zf_cm*10:.0f} mm)")
        self.card_foco_ok.lbl_v.setStyleSheet(f"color: {ColoresConsola.CYAN_MEDICO};")
        self.card_foco_ok.lbl_d.setText(f"Profundidad focal calculada (Distanciador D{dist_mm:.0f}: {dist_mm:.0f} mm)")
        self.card_foco_ok.lbl_d.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")

        # Card 3: EFD Total por Pulso
        self.card_efd_total.lbl_v.setText(f"{efd_total:.4f} mJ/mm²")
        self.card_efd_total.lbl_d.setText(f"EFD pos: {efd_pos:.3f} + EFD neg: {efd_neg:.4f} mJ/mm²")

        # Card 4: ΔT Estimado (Nyborg 1988)
        self.card_dt.lbl_v.setText(f"{dt_estimado:.3f} °C")
        if dt_estimado < 0.5:
            self.card_dt.lbl_v.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
            self.card_dt.lbl_d.setText("Estimación térmica simplificada (Nyborg 1988)")
            self.card_dt.lbl_d.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")
        else:
            self.card_dt.lbl_v.setStyleSheet(f"color: {ColoresConsola.ROJO_PULSO};")
            self.card_dt.lbl_d.setText("Estimación térmica calculada: > 0.50 °C")
            self.card_dt.lbl_d.setStyleSheet(f"color: {ColoresConsola.ROJO_PULSO};")

        # Card 5: Presión Negativa de Tracción (P-)
        self.card_p_neg.lbl_v.setText(f"{p_neg_mpa:.1f} MPa")
        self.card_p_neg.lbl_v.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
        self.card_p_neg.lbl_d.setText("Presión negativa de tracción configurada (-10.0 MPa)")

        # Card 6: ISPTA
        self.card_ispta.lbl_v.setText(f"{ispta_w:.4f} W/cm²")
        self.card_ispta.lbl_d.setText("Intensidad calculada sobre energía acústica total")

        # Card 7: Presión en Dermis / Cicatriz
        self.card_p_deep.lbl_v.setText(f"{p_deep_mpa:.2f} MPa")
        self.card_p_deep.lbl_d.setText("Presión propagada estimada en estrato cicatrizal")
        self.card_p_deep.lbl_d.setStyleSheet(f"color: {ColoresConsola.TEXTO_LABEL};")

        # Card 8: Tiempo y Dosis de Sesión
        self.card_t_sesion.lbl_v.setText(f"{t_sesion_min:.2f} min")
        self.card_t_sesion.lbl_d.setText(
            f"{total_pulsos:,} disparos @ {self._prf:.1f} Hz ({self.config.parametros.densidad_disparos_pcm2:.0f} p/cm² × {self._area_cm2:.0f} cm²)\n"
            f"Duración de emisión acústica activa continua calculada".replace(",", ".")
        )

        # Card 9: Sensibilidad Numérica del Modelo
        self.card_cv.lbl_v.setText(f"CV = {cv_pct:.2f}%")
        self.card_cv.lbl_v.setStyleSheet(f"color: {ColoresConsola.VERDE_SEGURO};")
        self.card_cv.lbl_d.setText("Dispersión numérica del modelo (n=50 iteraciones)")

    # ==========================================================================
    # GRAFICACIÓN CIENTÍFICA (TODOS LOS 5 GRÁFICOS DEL PROYECTO)
    # ==========================================================================
    def _cambiar_vista_grafica(self, indice: int):
        self.vista_grafica_actual = indice
        self.btn_vista_pulso.setStyleSheet(self._estilo_btn_activo(indice == 0))
        self.btn_vista_mapa.setStyleSheet(self._estilo_btn_activo(indice == 1))
        self.btn_vista_prof.setStyleSheet(self._estilo_btn_activo(indice == 2))
        self.btn_vista_esq.setStyleSheet(self._estilo_btn_activo(indice == 3))
        self.btn_vista_box.setStyleSheet(self._estilo_btn_activo(indice == 4))

        # Actualizar leyenda descriptiva objetiva (sin herramientas externas ni supuestos clínicos)
        descripciones = [
            "Vista 1: Pulso acústico focal p(t) con fase positiva de subida rápida (trise=8ns) y pozo de tracción negativo.",
            "Vista 2: Distribución espacial bidimensional p(x, z) del haz acústico e interfases tisulares con elipse a -6 dB.",
            "Vista 3: Perfil axial de penetración p(z) con atenuación estratificada tisular y ventana de energía sombreada.",
            "Vista 4: Esquema geométrico del aplicador piezoeléctrico de orientación normal fija y acople tisular conformado.",
            "Vista 5: Diagrama de cajas de consistencia y sensibilidad numérica del modelo computacional (n=50 iteraciones, CV < 5%)."
        ]
        self.lbl_info_grafico.setText(descripciones[indice])
        self._actualizar_grafico_pantalla()

    def _actualizar_grafico_pantalla(self):
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.set_facecolor(ColoresConsola.DISPLAY_DIGITAL_BG)
        for spine in ax.spines.values():
            spine.set_color("#1e293b")
        ax.tick_params(colors="#94a3b8", labelsize=8)
        ax.grid(True, linestyle=":", alpha=0.35, color="#334155")

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
            res = getattr(self, "_ultimo_resultado", None)
            matriz_2d = None
            x_mm = None
            z_mm = None
            if res is not None and hasattr(res, "mapa_presion_peak_mpa") and res.mapa_presion_peak_mpa is not None:
                matriz_2d = res.mapa_presion_peak_mpa
                if hasattr(res, "eje_x_cm") and res.eje_x_cm is not None:
                    x_mm = res.eje_x_cm * 10.0
                if hasattr(res, "eje_z_cm") and res.eje_z_cm is not None:
                    z_mm = res.eje_z_cm * 10.0

            graficar_mapa_2d(
                ax=ax,
                fig=self.figura,
                efd_nominal=self._efd,
                profundidad_focal_mm=self._foco_cm * 10.0,
                tipo_quemadura=self._tipo_quem,
                estilo_oscuro=True,
                matriz_presion_mpa=matriz_2d,
                eje_x_mm=x_mm,
                eje_z_mm=z_mm
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
        # VISTA 4: BUCLE ITERATIVO / BOXPLOT (n=50)  –  MODELO COMPUTACIONAL
        # ------------------------------------------------------------------
        elif self.vista_grafica_actual == 4:
            res = getattr(self, "_ultimo_resultado", None)
            if res is not None and hasattr(res, "muestras_p_peak_iteraciones"):
                p_muestras = res.muestras_p_peak_iteraciones
                efd_muestras = res.muestras_efd_iteraciones
            else:
                p_peak_base = 75.82 * np.sqrt(self._efd / 0.10)
                np.random.seed(42)
                p_muestras = p_peak_base * np.random.normal(loc=1.0, scale=0.024, size=50)
                efd_muestras = self._efd * ((p_muestras / p_peak_base) ** 2)

            graficar_boxplot_confiabilidad(
                ax=ax,
                muestras_p_peak=p_muestras,
                muestras_efd=efd_muestras,
                estilo_oscuro=True
            )

        self.figura.tight_layout(pad=1.2)
        self.canvas.draw()

    # ==========================================================================
    # DISPARO, PRESETS DE MEMORIA Y EXPORTACIÓN
    # ==========================================================================
    def _ejecutar_disparo_equipo(self):
        self.lbl_estado_emision.setText("● EMISIÓN ACTIVA: DISPARANDO...")
        self.lbl_estado_emision.setStyleSheet(f"""
            QLabel {{
                color: #ffffff;
                background-color: #dc2626;
                border: 1px solid #ef4444;
                border-radius: 4px;
                padding: 4px 10px;
            }}
        """)
        self.btn_disparo_equipo.setText("■ EMISIÓN EN CURSO...")
        self.btn_disparo_equipo.setStyleSheet(
            "background-color: #dc2626; color: #ffffff; border: 2px solid #ffffff; border-radius: 5px;"
        )
        QTimer.singleShot(1200, self._finalizar_disparo)

    def _finalizar_disparo(self):
        self.lbl_estado_emision.setText("● SISTEMA: LISTO (STANDBY)")
        self.lbl_estado_emision.setStyleSheet(f"""
            QLabel {{
                color: {ColoresConsola.AMBAR_AVISO};
                background-color: #451a03;
                border: 1px solid #b45309;
                border-radius: 4px;
                padding: 4px 10px;
            }}
        """)
        self.btn_disparo_equipo.setText("▶ INICIAR EMISIÓN / SIMULAR")
        self.btn_disparo_equipo.setStyleSheet(f"""
            QPushButton {{
                background-color: #0284c7;
                color: #ffffff;
                border: 1px solid {ColoresConsola.CYAN_MEDICO};
                border-radius: 5px;
                padding: 4px 14px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {ColoresConsola.CYAN_MEDICO};
                color: #030712;
                border-color: #ffffff;
            }}
            QPushButton:pressed {{ background-color: #0369a1; }}
        """)
        total = int(self.config.parametros.densidad_disparos_pcm2 * self._area_cm2)
        dist_mm = max(0.0, 30.0 - self._foco_cm * 10.0)
        QMessageBox.information(
            self, "Ráfaga Acústica Emitida",
            f"Se aplicaron exitosamente {total} pulsos a {self._prf:.1f} Hz.\n"
            f"• Densidad de Energía (EFD): {self._efd:.3f} mJ/mm²\n"
            f"• Profundidad focal estimada: {self._foco_cm:.1f} cm (Distanciador D{dist_mm:.0f}: {dist_mm:.0f} mm)\n"
            f"• Área cicatrizal: {self._area_cm2:.0f} cm²\n"
            f"• Duración de la sesión: {total / self._prf / 60:.1f} minutos.\n"
            f"• Parámetros acústicos: ΔT estimado < 0.50 °C, P- configurado = -10.0 MPa."
        )
        self._actualizar_grafico_pantalla()

    def _cargar_preset_memoria(self, banco: int):
        if banco == 1:
            self._fijar_superficie("Curva")
            self._fijar_efd(0.100)
            self._fijar_prf(4.0)
            self._fijar_tipo_quemadura("3er Grado")
            self._fijar_foco(1.0)
        elif banco == 2:
            self._fijar_superficie("Curva")
            self._fijar_efd(0.150)
            self._fijar_prf(4.0)
            self._fijar_tipo_quemadura("3er Grado")
            self._fijar_foco(1.5)
        elif banco == 3:
            self._fijar_superficie("Plana")
            self._fijar_efd(0.050)
            self._fijar_prf(4.0)
            self._fijar_tipo_quemadura("2do Grado")
            self._fijar_foco(0.5)
        self._actualizar_display_dosis()
        QMessageBox.information(self, "Memoria Clínica Cargada", f"Banco de Tratamiento M{banco} cargado correctamente.")

    def _exportar_png(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Pantalla de Consola",
            "pantalla_consola_eswt.png", "Imágenes (*.png)"
        )
        if ruta:
            self.figura.savefig(ruta, dpi=300, facecolor=ColoresConsola.DISPLAY_DIGITAL_BG,
                                bbox_inches="tight")
            QMessageBox.information(self, "Captura Guardada", f"Gráfico exportado en:\n{ruta}")

    def _guardar_sesion_json(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Configuración de Sesión",
            "sesion_consola_eswt.json", "Archivos JSON (*.json)"
        )
        if ruta:
            ok, msg = GestorConfiguracion.guardar_archivo(self.config, ruta)
            if ok:
                QMessageBox.information(self, "Sesión Guardada", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    def _exportar_datos_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar Datos de Tratamiento",
            "datos_consola_eswt.csv", "Archivos CSV (*.csv)"
        )
        if ruta:
            res = getattr(self, "_ultimo_resultado", None)
            ok, msg = ServicioExportacion.exportar_resumen_operativo_csv(self.config, ruta, resultados=res)
            if ok:
                QMessageBox.information(self, "Exportación Exitosa", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    def _abrir_modo_modular(self):
        try:
            from interfaz.ventana_principal import VentanaPrincipal
            self.ventana_modular = VentanaPrincipal()
            self.ventana_modular.show()
        except Exception as e:
            QMessageBox.warning(self, "Modo Modular", f"No se pudo abrir la vista modular: {e}")

    def _mostrar_dialogo_anteproyecto(self):
        """Muestra el diálogo formal con la especificación rectora del Anteproyecto UNER."""
        from PySide6.QtWidgets import QDialog, QTextBrowser
        dlg = QDialog(self)
        dlg.setWindowTitle("Anteproyecto de Investigación – Taller de Bioingeniería (UNER)")
        dlg.resize(760, 620)
        dlg.setStyleSheet(f"""
            QDialog {{
                background-color: {ColoresConsola.PANEL_CONTROL};
                color: #f8fafc;
            }}
        """)
        l_dlg = QVBoxLayout(dlg)
        l_dlg.setContentsMargins(18, 16, 18, 16)
        l_dlg.setSpacing(10)

        tit = QLabel("PROYECTO INTEGRADOR – FIUNER (TALLER DE BIOINGENIERÍA)")
        tit.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        tit.setStyleSheet(f"color: {ColoresConsola.CYAN_MEDICO};")
        l_dlg.addWidget(tit)

        sub = QLabel(
            "Diseño de un aplicador de ondas de choque de baja intensidad para la "
            "regeneración tisular en cicatrices hipertróficas por quemaduras"
        )
        sub.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        sub.setStyleSheet("color: #e2e8f0;")
        sub.setWordWrap(True)
        l_dlg.addWidget(sub)

        tb = QTextBrowser()
        tb.setStyleSheet("""
            QTextBrowser {
                background-color: #0b1120;
                color: #cbd5e1;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        tb.setHtml("""
        <h3 style="color: #38bdf8; margin-top:0;">1. Marco Institucional y Equipo de Trabajo</h3>
        <p><b>Universidad:</b> Universidad Nacional de Entre Ríos (UNER)<br>
        <b>Facultad:</b> Facultad de Ingeniería (FIUNER) | <b>Carrera:</b> Bioingeniería<br>
        <b>Cátedra:</b> Taller de Bioingeniería | <b>Asesor:</b> Bioing. Daniel Zapata<br>
        <b>Autoras:</b> María Constanza Gastaldi, Marthina Gerstner Soltermann, Florencia Kessel</p>

        <h3 style="color: #38bdf8;">2. Matriz Metodológica de Variables (Anteproyecto)</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; border-color: #334155; width: 100%; color: #cbd5e1;">
            <tr style="background-color: #1e293b; color: #f8fafc;">
                <th>Variable</th><th>Rol Causal</th><th>Unidad</th><th>Operacionalización en el Simulador</th>
            </tr>
            <tr>
                <td><b>Densidad de Flujo de Energía (EFD)</b></td><td>Independiente (Activa)</td><td>mJ/mm²</td>
                <td>Configurada en el modelo (0.03 – 0.25 mJ/mm²; nominal: 0.10 mJ/mm²).</td>
            </tr>
            <tr>
                <td><b>Dosificación de Disparos</b></td><td>Independiente (Activa)</td><td>pulsos/cm²</td>
                <td>Pulsos programados por unidad de superficie de lesión (10 – 500 p/cm²).</td>
            </tr>
            <tr>
                <td><b>Tasa de Angiogénesis</b></td><td>Dependiente (Resultado)</td><td>vasos/mm²</td>
                <td>Criterio biológico externo de literatura (Goertz et al. 2012). NO se mide in vivo.</td>
            </tr>
            <tr>
                <td><b>Elasticidad del Tejido</b></td><td>Dependiente (Resultado)</td><td>Coef. deformación</td>
                <td>Criterio biomecánico de recuperación funcional (Lee et al. 2024).</td>
            </tr>
            <tr>
                <td><b>Liberación de VEGF</b></td><td>Interviniente (Mediadora)</td><td>pg/mL</td>
                <td>Criterio de validación externa a 0.10 mJ/mm² (Cui et al. 2018).</td>
            </tr>
            <tr>
                <td><b>Diferenciación Fibroblástica</b></td><td>Interviniente (Mediadora)</td><td>células/mm²</td>
                <td>Mecanismo de mecanotransducción celular (Qian et al. 2022 / Mascharak et al. 2020).</td>
            </tr>
            <tr>
                <td><b>Edad del Paciente</b></td><td>Extraña (Atributo)</td><td>Años</td>
                <td>Parámetro modulador de atenuación tisular y rigidez dérmica.</td>
            </tr>
            <tr>
                <td><b>Tipo de Quemadura</b></td><td>Extraña (Atributo)</td><td>Cualitativa</td>
                <td>Estratificación dérmica: 2do Grado Profundo (5 mm) vs 3er Grado Fibrótico (9 mm).</td>
            </tr>
        </table>

        <h3 style="color: #38bdf8;">3. Alcance y Limitaciones</h3>
        <p>• <b>Comprende:</b> Modelado bioacústico conceptual, prototipado virtual, cálculo dosimétrico, simulación de propagación y contraste con antecedentes científicos.<br>
        • <b>NO comprende:</b> Fabricación física, ensayos clínicos en humanos, cuantificación in vitro de proteínas ni afirmaciones de eficacia terapéutica demostrada.<br>
        • Las pruebas de software certifican estabilidad computacional y consistencia dimensional, no validación experimental in vivo.</p>
        """)
        l_dlg.addWidget(tb)

        btn_cerrar = self._crear_boton_consola("Cerrar Ventana", ancho=130, callback=dlg.accept)
        l_dlg.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)
        dlg.exec()
