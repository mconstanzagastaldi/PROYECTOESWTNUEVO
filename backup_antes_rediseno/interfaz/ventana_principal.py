"""
================================================================================
VENTANA PRINCIPAL DE LA APLICACIÓN (PySide6)
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Integra y sincroniza los 10 módulos técnicos, el menú lateral y el estado global.
================================================================================
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QStackedWidget, QFrame, QButtonGroup
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from modelos.configuracion import ConfiguracionGlobal

try:
    from .componentes import Colores, BotonNavegacion, BadgeEstado, ESTILO_GLOBAL
    from .panel_inicio import PanelInicio
    from .modulo_aplicador import ModuloAplicador
    from .modulo_geometria import ModuloGeometria
    from .modulo_parametros import ModuloParametros
    from .modulo_tejidos import ModuloTejidos
    from .modulo_simulacion import ModuloSimulacion
    from .modulo_motor import ModuloMotor
    from .modulo_resultados import ModuloResultados
    from .modulo_comparacion import ModuloComparacion
    from .modulo_exportacion import ModuloExportacion
except ImportError:
    from interfaz.componentes import Colores, BotonNavegacion, BadgeEstado, ESTILO_GLOBAL
    from interfaz.panel_inicio import PanelInicio
    from interfaz.modulo_aplicador import ModuloAplicador
    from interfaz.modulo_geometria import ModuloGeometria
    from interfaz.modulo_parametros import ModuloParametros
    from interfaz.modulo_tejidos import ModuloTejidos
    from interfaz.modulo_simulacion import ModuloSimulacion
    from interfaz.modulo_motor import ModuloMotor
    from interfaz.modulo_resultados import ModuloResultados
    from interfaz.modulo_comparacion import ModuloComparacion
    from interfaz.modulo_exportacion import ModuloExportacion


class VentanaPrincipal(QMainWindow):
    """Ventana principal del software SIMULADOR ESWT con sincronización global."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIMULADOR ESWT | Aplicador Piezoeléctrico de Ondas de Choque (UNER)")
        self.resize(1340, 860)
        self.setMinimumSize(1100, 680)

        self.setStyleSheet(ESTILO_GLOBAL)

        # Estado global maestro
        self.config_global = ConfiguracionGlobal()

        # Definición de módulos y sus títulos formales
        self.modulos_info = [
            ("Inicio", "Panel Principal", "🏠"),
            ("Aplicador", "Configuración del Aplicador Piezoeléctrico", "⚡"),
            ("Geometría", "Geometría y Superficie Anatómica", "📐"),
            ("Parámetros", "Parámetros Operativos y Dosimetría", "⚙️"),
            ("Tejidos", "Propiedades y Estratificación Tisular", "🧬"),
            ("Simulación", "Configuración del Modelo de Simulación", "🖩"),
            ("Motor", "Motor Numérico de Simulación", "🚀"),
            ("Resultados", "Visualización de Resultados Acústicos", "📊"),
            ("Comparación", "Comparación de Escenarios y Orientaciones", "🔄"),
            ("Exportación", "Gestión de Archivos y Almacenamiento", "💾")
        ]

        self._crear_ui()
        self._conectar_senales_sincronizacion()
        self.navegar_a_modulo(0)

    def _crear_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_raiz = QHBoxLayout(widget_central)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # ----------------------------------------------------------------------
        # 1. BARRA LATERAL DE NAVEGACIÓN (SIDEBAR)
        # ----------------------------------------------------------------------
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.AZUL_PRIMARIO};
                border-right: 1px solid {Colores.AZUL_BORDE};
            }}
        """)
        l_side = QVBoxLayout(sidebar)
        l_side.setContentsMargins(0, 0, 0, 16)
        l_side.setSpacing(0)

        # Cabecera de la Barra Lateral
        cabecera_side = QFrame()
        cabecera_side.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.AZUL_SECUNDARIO};
                border-bottom: 1px solid {Colores.AZUL_BORDE};
            }}
        """)
        l_cab = QVBoxLayout(cabecera_side)
        l_cab.setContentsMargins(20, 22, 20, 20)
        l_cab.setSpacing(4)

        t_app = QLabel("SIMULADOR ESWT")
        t_app.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t_app.setStyleSheet(f"color: {Colores.TEXTO_BLANCO}; letter-spacing: 0.5px;")
        l_cab.addWidget(t_app)

        sub_app = QLabel("Bioingeniería UNER")
        sub_app.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        sub_app.setStyleSheet(f"color: {Colores.CELESTE_BRILLANTE};")
        l_cab.addWidget(sub_app)

        l_side.addWidget(cabecera_side)

        # Contenedor de Botones de Navegación
        self.btn_grupo = QButtonGroup(self)
        self.btn_grupo.setExclusive(True)
        self.botones_nav = []

        c_botones = QWidget()
        l_botones = QVBoxLayout(c_botones)
        l_botones.setContentsMargins(0, 12, 0, 12)
        l_botones.setSpacing(2)

        for idx, (nombre_corto, _, icono) in enumerate(self.modulos_info):
            btn = BotonNavegacion(nombre_corto, icono)
            self.btn_grupo.addButton(btn, idx)
            self.botones_nav.append(btn)
            btn.clicked.connect(lambda _, i=idx: self.navegar_a_modulo(i))
            l_botones.addWidget(btn)

        l_side.addWidget(c_botones)
        l_side.addStretch()

        # Pie de la barra lateral (Información Académica)
        pie_side = QFrame()
        pie_side.setStyleSheet("background: transparent; border: none; padding: 0 16px;")
        l_pie = QVBoxLayout(pie_side)
        l_pie.setSpacing(2)

        lbl_catedra = QLabel("Taller de Bioingeniería")
        lbl_catedra.setFont(QFont("Segoe UI", 7, QFont.Weight.DemiBold))
        lbl_catedra.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
        l_pie.addWidget(lbl_catedra)

        lbl_anteproy = QLabel("Cicatrices Hipertróficas")
        lbl_anteproy.setFont(QFont("Segoe UI", 7))
        lbl_anteproy.setStyleSheet(f"color: {Colores.AZUL_BORDE};")
        l_pie.addWidget(lbl_anteproy)

        l_side.addWidget(pie_side)
        layout_raiz.addWidget(sidebar)

        # ----------------------------------------------------------------------
        # 2. ÁREA DE TRABAJO DERECHA (ENCABEZADO + STACK + STATUS)
        # ----------------------------------------------------------------------
        area_derecha = QWidget()
        l_derecha = QVBoxLayout(area_derecha)
        l_derecha.setContentsMargins(0, 0, 0, 0)
        l_derecha.setSpacing(0)

        # Encabezado Dinámico Superior
        encabezado = QFrame()
        encabezado.setFixedHeight(64)
        encabezado.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.SUPERFICIE_TARJETA};
                border-bottom: 1px solid {Colores.BORDE_TARJETA};
            }}
        """)
        l_enc = QHBoxLayout(encabezado)
        l_enc.setContentsMargins(28, 0, 28, 0)

        self.lbl_titulo_modulo = QLabel("Panel Principal")
        self.lbl_titulo_modulo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_titulo_modulo.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_enc.addWidget(self.lbl_titulo_modulo)

        l_enc.addStretch()

        # Badges de Diagnóstico en el Encabezado
        self.badge_conexion = BadgeEstado("SISTEMA LISTO", "ok")
        l_enc.addWidget(self.badge_conexion)

        self.badge_motor = BadgeEstado("MOTOR: DESACOPLADO", "info")
        l_enc.addWidget(self.badge_motor)

        l_derecha.addWidget(encabezado)

        # Contenedor Central Apilado (QStackedWidget)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {Colores.FONDO_VENTANA};")

        # Instanciar las vistas de los 10 módulos con la configuración activa
        self.panel_inicio = PanelInicio()
        self.panel_inicio.solicitar_navegacion.connect(self.navegar_a_modulo)
        self.stack.addWidget(self.panel_inicio)                               # 0

        self.modulo_aplicador = ModuloAplicador(self.config_global.aplicador)
        self.stack.addWidget(self.modulo_aplicador)                           # 1

        self.modulo_geometria = ModuloGeometria(self.config_global.geometria)
        self.stack.addWidget(self.modulo_geometria)                           # 2

        self.modulo_parametros = ModuloParametros(self.config_global.parametros)
        self.stack.addWidget(self.modulo_parametros)                         # 3

        self.modulo_tejidos = ModuloTejidos(self.config_global.tejidos)
        self.stack.addWidget(self.modulo_tejidos)                             # 4

        self.modulo_simulacion = ModuloSimulacion(self.config_global.malla)
        self.stack.addWidget(self.modulo_simulacion)                         # 5

        self.modulo_motor = ModuloMotor(self.config_global)
        self.stack.addWidget(self.modulo_motor)                               # 6

        self.modulo_resultados = ModuloResultados()
        self.stack.addWidget(self.modulo_resultados)                         # 7

        self.modulo_comparacion = ModuloComparacion(self.config_global)
        self.stack.addWidget(self.modulo_comparacion)                       # 8

        self.modulo_exportacion = ModuloExportacion(self.config_global)
        self.stack.addWidget(self.modulo_exportacion)                       # 9

        l_derecha.addWidget(self.stack)

        # Barra de Estado Inferior
        barra_estado = QFrame()
        barra_estado.setFixedHeight(30)
        barra_estado.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.SUPERFICIE_TARJETA};
                border-top: 1px solid {Colores.BORDE_TARJETA};
            }}
        """)
        l_status = QHBoxLayout(barra_estado)
        l_status.setContentsMargins(20, 0, 20, 0)

        self.lbl_status_msg = QLabel("Entorno preparado para la configuración de parámetros y simulación.")
        self.lbl_status_msg.setFont(QFont("Segoe UI", 7, QFont.Weight.Normal))
        self.lbl_status_msg.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        l_status.addWidget(self.lbl_status_msg)

        l_status.addStretch()

        lbl_version = QLabel("SIMULADOR ESWT v1.0.0 | UNER - Bioingeniería")
        lbl_version.setFont(QFont("Segoe UI", 7, QFont.Weight.Medium))
        lbl_version.setStyleSheet(f"color: {Colores.TEXTO_MUTED};")
        l_status.addWidget(lbl_version)

        l_derecha.addWidget(barra_estado)

        layout_raiz.addWidget(area_derecha)

    def _conectar_senales_sincronizacion(self):
        """Conecta eventos para mantener los módulos sincronizados con el estado maestro."""
        self.modulo_aplicador.configuracion_modificada.connect(self._al_actualizar_aplicador)
        self.modulo_geometria.geometria_modificada.connect(self._al_actualizar_geometria)
        self.modulo_parametros.parametros_modificados.connect(self._al_actualizar_parametros)
        self.modulo_tejidos.tejidos_modificados.connect(self._al_actualizar_tejidos)
        self.modulo_simulacion.malla_modificada.connect(self._al_actualizar_malla)
        self.modulo_motor.simulacion_completada.connect(self._al_completar_simulacion)
        self.modulo_exportacion.configuracion_cargada.connect(self._al_cargar_configuracion_global)

    def _al_actualizar_aplicador(self, app):
        self.config_global.aplicador = app
        self._sincronizar_modulos_dependientes()

    def _al_actualizar_geometria(self, geo):
        self.config_global.geometria = geo
        self._sincronizar_modulos_dependientes()

    def _al_actualizar_parametros(self, p):
        self.config_global.parametros = p
        self._sincronizar_modulos_dependientes()

    def _al_actualizar_tejidos(self, tej):
        self.config_global.tejidos = tej
        self._sincronizar_modulos_dependientes()

    def _al_actualizar_malla(self, m):
        self.config_global.malla = m
        self._sincronizar_modulos_dependientes()

    def _al_completar_simulacion(self, resultados):
        self.modulo_resultados.actualizar_resultados(resultados)
        self.navegar_a_modulo(7) # Navegar automáticamente a Resultados

    def _al_cargar_configuracion_global(self, config_nueva):
        self.config_global = config_nueva
        self.modulo_aplicador.cargar_datos(config_nueva.aplicador)
        self.modulo_geometria.cargar_datos(config_nueva.geometria)
        self.modulo_parametros.cargar_datos(config_nueva.parametros)
        self.modulo_tejidos.cargar_datos(config_nueva.tejidos)
        self.modulo_simulacion.cargar_datos(config_nueva.malla)
        self._sincronizar_modulos_dependientes()

    def _sincronizar_modulos_dependientes(self):
        self.modulo_motor.actualizar_configuracion(self.config_global)
        self.modulo_exportacion.sincronizar_configuracion(self.config_global)
        self.modulo_comparacion.config_a = self.config_global
        self.modulo_comparacion._actualizar_tabla()

        # Actualizar tarjetas de panel inicio
        c = self.config_global
        self.panel_inicio.card_config.actualizar(
            c.nombre_configuracion,
            f"{c.aplicador.cabezal.tipo_geometria} • EFD {c.parametros.efd_nominal_mj_mm2:.2f} mJ/mm² • {c.parametros.frecuencia_repeticion_hz:.1f} Hz"
        )
        self.panel_inicio.card_tejido.actualizar(
            f"{len(c.tejidos)} Estratos Definidos",
            ", ".join([t.nombre for t in c.tejidos[:2]]) + "..."
        )

    def navegar_a_modulo(self, indice: int):
        """Cambia fluidamente el módulo visualizado y actualiza títulos e indicadores."""
        if 0 <= indice < self.stack.count():
            self.stack.setCurrentIndex(indice)
            _, titulo_largo, _ = self.modulos_info[indice]
            self.lbl_titulo_modulo.setText(titulo_largo)

            # Actualizar estilos del botón seleccionado
            for idx, btn in enumerate(self.botones_nav):
                btn.setChecked(idx == indice)
                btn._aplicar_estilo(activo=(idx == indice))

            self.lbl_status_msg.setText(f"Módulo activo: {titulo_largo}")
