"""
================================================================================
MÓDULO 1: PANEL PRINCIPAL (INICIO)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Presenta la vista de bienvenida del software, descripción del anteproyecto,
indicadores de estado de subsistemas y accesos rápidos a los módulos de configuración.
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from interfaz.componentes import (
    Colores, TarjetaContenedor, TarjetaEstado, BotonPrimario, BotonSecundario, BadgeEstado
)


class PanelInicio(QWidget):
    """Pantalla inicial del simulador con resumen técnico y accesos directos."""

    # Señal para solicitar navegación hacia un módulo específico (por índice)
    solicitar_navegacion = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inicializar_ui()

    def _inicializar_ui(self):
        # Usamos QScrollArea para asegurar visualización perfecta en cualquier resolución
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        contenedor = QWidget()
        layout_principal = QVBoxLayout(contenedor)
        layout_principal.setContentsMargins(32, 28, 32, 32)
        layout_principal.setSpacing(24)

        # ----------------------------------------------------------------------
        # 1. ENCABEZADO Y PRESENTACIÓN INSTITUCIONAL
        # ----------------------------------------------------------------------
        tarjeta_banner = TarjetaContenedor()
        layout_banner = QVBoxLayout(tarjeta_banner)
        layout_banner.setContentsMargins(24, 20, 24, 20)
        layout_banner.setSpacing(8)

        lbl_inst = QLabel("UNIVERSIDAD NACIONAL DE ENTRE RÍOS | FACULTAD DE INGENIERÍA | TALLER DE BIOINGENIERÍA")
        lbl_inst.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_inst.setStyleSheet(f"color: {Colores.CELESTE_ACENTO}; letter-spacing: 0.8px;")
        layout_banner.addWidget(lbl_inst)

        lbl_titulo = QLabel("SIMULADOR ESWT")
        lbl_titulo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        layout_banner.addWidget(lbl_titulo)

        lbl_subtitulo = QLabel("Diseño y análisis computacional de un aplicador piezoeléctrico de ondas de choque extracorpóreas")
        lbl_subtitulo.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        lbl_subtitulo.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        layout_banner.addWidget(lbl_subtitulo)

        linea_div = QFrame()
        linea_div.setFrameShape(QFrame.Shape.HLine)
        linea_div.setStyleSheet(f"background-color: {Colores.BORDE_TARJETA}; max-height: 1px;")
        layout_banner.addWidget(linea_div)

        lbl_desc = QLabel(
            "Plataforma computacional para el modelado de la propagación acústica en tejido cutáneo con cicatrices "
            "hipertróficas postquemadura. Permite configurar la geometría del aplicador, evaluar la adaptabilidad "
            "en superficies planas y anatómicas curvas (articulaciones), gestionar las propiedades biofísicas de los "
            "estratos tisulares y validar la ventana terapéutica de baja intensidad (0.03 a 0.25 mJ/mm²)."
        )
        lbl_desc.setFont(QFont("Segoe UI", 9, QFont.Weight.Normal))
        lbl_desc.setStyleSheet(f"color: {Colores.TEXTO_NORMAL}; line-height: 1.4;")
        lbl_desc.setWordWrap(True)
        layout_banner.addWidget(lbl_desc)

        layout_principal.addWidget(tarjeta_banner)

        # ----------------------------------------------------------------------
        # 2. INDICADORES DE ESTADO DEL SISTEMA (DASHBOARD)
        # ----------------------------------------------------------------------
        lbl_sec_estado = QLabel("ESTADO GENERAL DEL SISTEMA")
        lbl_sec_estado.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_sec_estado.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO}; letter-spacing: 0.5px;")
        layout_principal.addWidget(lbl_sec_estado)

        layout_estados = QHBoxLayout()
        layout_estados.setSpacing(16)

        self.card_interfaz = TarjetaEstado(
            titulo="Software / Interfaz",
            valor="Operativo (PySide6)",
            subtitulo="Arquitectura modular desacoplada de la física",
            color_acento=Colores.ESTADO_OK
        )
        layout_estados.addWidget(self.card_interfaz)

        self.card_motor = TarjetaEstado(
            titulo="Motor de Simulación",
            valor="Desacoplado (En espera)",
            subtitulo="Pendiente de la formulación física del aplicador",
            color_acento=Colores.ESTADO_INFO
        )
        layout_estados.addWidget(self.card_motor)

        self.card_config = TarjetaEstado(
            titulo="Configuración Activa",
            valor="Anteproyecto UNER",
            subtitulo="Piezoeléctrico cóncavo • EFD 0.10 mJ/mm² • 4.0 Hz",
            color_acento=Colores.CELESTE_ACENTO
        )
        layout_estados.addWidget(self.card_config)

        self.card_tejido = TarjetaEstado(
            titulo="Modelo Tisular",
            valor="4 Estratos Definidos",
            subtitulo="Gel acople, Piel sana, Cicatriz 3er grado, Subcutáneo",
            color_acento="#8b5cf6"
        )
        layout_estados.addWidget(self.card_tejido)

        layout_principal.addLayout(layout_estados)

        # ----------------------------------------------------------------------
        # 3. ACCESOS RÁPIDOS A MÓDULOS DE TRABAJO
        # ----------------------------------------------------------------------
        lbl_sec_accesos = QLabel("FLUJO DE TRABAJO Y MÓDULOS DE CONFIGURACIÓN")
        lbl_sec_accesos.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_sec_accesos.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO}; letter-spacing: 0.5px;")
        layout_principal.addWidget(lbl_sec_accesos)

        grid_accesos = QGridLayout()
        grid_accesos.setSpacing(14)

        accesos_info = [
            ("1. Configuración del Aplicador", "Definir cabezal cóncavo, tecnología piezoeléctrica y acople acústico.", 1),
            ("2. Geometría y Anatomía", "Ajustar curvatura de piel (plana / mano), ángulo de incidencia y profundidad.", 2),
            ("3. Parámetros Operativos", "Configurar EFD (0.03-0.25 mJ/mm²), PRF (4-5 Hz) y dosificación de disparos.", 3),
            ("4. Propiedades de Tejidos", "Gestionar estratos tisulares, densidades, velocidades y coeficientes de atenuación.", 4),
            ("5. Malla y Modelo Numérico", "Configurar dimensiones del dominio cartesiano x-z, pasos espaciales y temporales.", 5),
            ("6. Resultados y Comparación", "Visualizar mapas de presión, perfiles axiales y comparar orientaciones del cabezal.", 7)
        ]

        for i, (tit, sub, mod_idx) in enumerate(accesos_info):
            card_acc = TarjetaContenedor()
            l_acc = QVBoxLayout(card_acc)
            l_acc.setContentsMargins(18, 14, 18, 14)
            l_acc.setSpacing(6)

            t = QLabel(tit)
            t.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
            t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
            l_acc.addWidget(t)

            s = QLabel(sub)
            s.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
            s.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
            s.setWordWrap(True)
            l_acc.addWidget(s)

            btn = BotonSecundario("Abrir Módulo")
            btn.setFixedHeight(30)
            btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
            # Captura de índice mediante closure por defecto
            btn.clicked.connect(lambda _, idx=mod_idx: self.solicitar_navegacion.emit(idx))
            l_acc.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)

            fila = i // 2
            col = i % 2
            grid_accesos.addWidget(card_acc, fila, col)

        layout_principal.addLayout(grid_accesos)

        # ----------------------------------------------------------------------
        # 4. AVISO TÉCNICO DE FASE DE DESARROLLO (INTEGRACIÓN)
        # ----------------------------------------------------------------------
        tarjeta_aviso = TarjetaContenedor()
        tarjeta_aviso.setStyleSheet(f"""
            TarjetaContenedor {{
                background-color: {Colores.CELESTE_FONDO};
                border: 1px solid {Colores.CELESTE_BORDE};
                border-radius: 8px;
            }}
        """)
        l_aviso = QHBoxLayout(tarjeta_aviso)
        l_aviso.setContentsMargins(20, 14, 20, 14)
        l_aviso.setSpacing(14)

        badge_aviso = BadgeEstado("INTEGRACIÓN MODULAR", "info")
        l_aviso.addWidget(badge_aviso, alignment=Qt.AlignmentFlag.AlignTop)

        lbl_aviso_txt = QLabel(
            "<b>Diseño desacoplado:</b> Esta interfaz gráfica permite gestionar todos los parámetros clínicos y "
            "preparar el entorno de simulación. La formulación física del transductor (casquete cóncavo y elementos "
            "piezoeléctricos) se conectará directamente a través del paquete <code>fisica/</code> sin requerir cambios "
            "estructurales en la aplicación."
        )
        lbl_aviso_txt.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
        lbl_aviso_txt.setStyleSheet(f"color: {Colores.AZUL_PRIMARIO}; line-height: 1.3;")
        lbl_aviso_txt.setWordWrap(True)
        l_aviso.addWidget(lbl_aviso_txt)

        layout_principal.addWidget(tarjeta_aviso)

        layout_principal.addStretch()

        scroll.setWidget(contenedor)
        layout_root = QVBoxLayout(self)
        layout_root.setContentsMargins(0, 0, 0, 0)
        layout_root.addWidget(scroll)

