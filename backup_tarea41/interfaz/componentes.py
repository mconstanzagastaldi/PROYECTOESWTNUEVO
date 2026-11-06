"""
================================================================================
SISTEMA DE DISEÑO VISUAL Y COMPONENTES REUTILIZABLES (PySide6)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Define la paleta de colores corporativa y técnica (estilo ingeniería biomédica),
las hojas de estilo QSS y componentes personalizados (tarjetas, botones, badges).
================================================================================
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont


# ==============================================================================
# PALETA CROMÁTICA - INGENIERÍA BIOMÉDICA
# ==============================================================================
class Colores:
    # Azules oscuros técnicos (Header, Sidebar, Marcos)
    AZUL_PRIMARIO = "#0f172a"      # Navy profundo (Sidebar / Fondo oscuro)
    AZUL_SECUNDARIO = "#1e293b"    # Navy medio (Encabezados / Contenedores)
    AZUL_BORDE = "#334155"         # Divisores y bordes sutiles

    # Celestes y Azules Médicos (Acentos, Selección, Foco)
    CELESTE_ACENTO = "#0284c7"     # Azul médico principal (Botones, Selección)
    CELESTE_BRILLANTE = "#38bdf8"  # Cyan claro (Hover, Indicadores activos)
    CELESTE_FONDO = "#f0f9ff"      # Fondo suave para áreas destacadas
    CELESTE_BORDE = "#bae6fd"      # Borde de alerta o tarjeta médica

    # Fondos y Superficies de Trabajo
    FONDO_VENTANA = "#f8fafc"      # Slate ultraclaro (Fondo general de paneles)
    SUPERFICIE_TARJETA = "#ffffff" # Blanco puro para tarjetas y formularios
    BORDE_TARJETA = "#e2e8f0"      # Gris claro neutro para bordes limpios

    # Tipografía y Textos
    TEXTO_TITULO = "#0f172a"       # Máximo contraste
    TEXTO_NORMAL = "#334155"       # Texto estándar de lectura
    TEXTO_SECUNDARIO = "#64748b"   # Subtítulos, descripciones y unidades
    TEXTO_BLANCO = "#ffffff"       # Sobre fondos oscuros
    TEXTO_MUTED = "#94a3b8"        # Textos deshabilitados o decorativos

    # Estados del Sistema
    ESTADO_OK = "#10b981"          # Verde esmeralda (Listo / Conectado)
    ESTADO_ALERTA = "#f59e0b"      # Ámbar (Pendiente / Advertencia)
    ESTADO_INFO = "#0284c7"        # Celeste (Informativo / Desacoplado)


# ==============================================================================
# HOJAS DE ESTILO GLOBALES (QSS)
# ==============================================================================
ESTILO_GLOBAL = f"""
QMainWindow {{
    background-color: {Colores.FONDO_VENTANA};
}}

QWidget {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
    color: {Colores.TEXTO_NORMAL};
}}

/* ScrollBars estilizadas y sutiles */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: #cbd5e1;
    min-height: 24px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: #94a3b8;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""


# ==============================================================================
# COMPONENTES VISUALES REUTILIZABLES
# ==============================================================================

class TarjetaContenedor(QFrame):
    """Contenedor tipo tarjeta blanca con borde limpio para agrupar controles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            TarjetaContenedor {{
                background-color: {Colores.SUPERFICIE_TARJETA};
                border: 1px solid {Colores.BORDE_TARJETA};
                border-radius: 8px;
            }}
        """)


class TarjetaEstado(QFrame):
    """Tarjeta informativa con título, valor destacado, subtítulo e icono de estado."""
    def __init__(self, titulo: str, valor: str, subtitulo: str = "", color_acento: str = Colores.CELESTE_ACENTO, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            TarjetaEstado {{
                background-color: {Colores.SUPERFICIE_TARJETA};
                border: 1px solid {Colores.BORDE_TARJETA};
                border-left: 5px solid {color_acento};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        lbl_tit = QLabel(titulo.upper())
        lbl_tit.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_tit.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO}; letter-spacing: 0.5px;")
        layout.addWidget(lbl_tit)

        self.lbl_val = QLabel(valor)
        self.lbl_val.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.lbl_val.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        layout.addWidget(self.lbl_val)

        if subtitulo:
            self.lbl_sub = QLabel(subtitulo)
            self.lbl_sub.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
            self.lbl_sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
            self.lbl_sub.setWordWrap(True)
            layout.addWidget(self.lbl_sub)

    def actualizar(self, valor: str, subtitulo: str = ""):
        self.lbl_val.setText(valor)
        if subtitulo and hasattr(self, "lbl_sub"):
            self.lbl_sub.setText(subtitulo)


class BotonNavegacion(QPushButton):
    """Botón lateral del menú con feedback visual de selección y hover."""
    def __init__(self, texto: str, icono_letra: str = "•", parent=None):
        super().__init__(f"  {icono_letra}   {texto}", parent)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setFixedHeight(44)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._aplicar_estilo(activo=False)

    def _aplicar_estilo(self, activo: bool):
        if activo:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colores.AZUL_SECUNDARIO};
                    color: {Colores.CELESTE_BRILLANTE};
                    border: none;
                    border-left: 4px solid {Colores.CELESTE_BRILLANTE};
                    border-radius: 0px;
                    padding-left: 14px;
                    text-align: left;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Colores.TEXTO_MUTED};
                    border: none;
                    border-left: 4px solid transparent;
                    border-radius: 0px;
                    padding-left: 14px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: #172554;
                    color: {Colores.TEXTO_BLANCO};
                }}
            """)


class BotonPrimario(QPushButton):
    """Botón de acción principal en celeste biomédico."""
    def __init__(self, texto: str, parent=None):
        super().__init__(texto, parent)
        self.setFixedHeight(38)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colores.CELESTE_ACENTO};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }}
            QPushButton:hover {{
                background-color: #0369a1;
            }}
            QPushButton:pressed {{
                background-color: #075985;
            }}
            QPushButton:disabled {{
                background-color: #cbd5e1;
                color: #64748b;
            }}
        """)


class BotonSecundario(QPushButton):
    """Botón secundario neutro con borde limpio."""
    def __init__(self, texto: str, parent=None):
        super().__init__(texto, parent)
        self.setFixedHeight(38)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #ffffff;
                color: {Colores.TEXTO_NORMAL};
                border: 1px solid {Colores.BORDE_TARJETA};
                border-radius: 6px;
                padding: 8px 18px;
            }}
            QPushButton:hover {{
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }}
            QPushButton:pressed {{
                background-color: #e2e8f0;
            }}
        """)


class BadgeEstado(QFrame):
    """Etiqueta compacta con color de fondo y borde para indicar estado de subsistemas."""
    def __init__(self, texto: str, tipo: str = "ok", parent=None):
        super().__init__(parent)
        self.tipo = tipo
        colores_map = {
            "ok": ("#ecfdf5", "#10b981", "#065f46"),
            "alerta": ("#fffbeb", "#f59e0b", "#92400e"),
            "info": ("#f0f9ff", "#0284c7", "#075985"),
            "espera": ("#f8fafc", "#94a3b8", "#475569")
        }
        bg, border, text_col = colores_map.get(tipo, colores_map["info"])
        self.setStyleSheet(f"""
            BadgeEstado {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 3, 10, 3)
        self.lbl = QLabel(texto)
        self.lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        self.lbl.setStyleSheet(f"color: {text_col};")
        layout.addWidget(self.lbl)

    def set_estado(self, texto: str, tipo: str):
        colores_map = {
            "ok": ("#ecfdf5", "#10b981", "#065f46"),
            "alerta": ("#fffbeb", "#f59e0b", "#92400e"),
            "info": ("#f0f9ff", "#0284c7", "#075985"),
            "espera": ("#f8fafc", "#94a3b8", "#475569")
        }
        bg, border, text_col = colores_map.get(tipo, colores_map["info"])
        self.setStyleSheet(f"""
            BadgeEstado {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)
        self.lbl.setText(texto)
        self.lbl.setStyleSheet(f"color: {text_col};")

