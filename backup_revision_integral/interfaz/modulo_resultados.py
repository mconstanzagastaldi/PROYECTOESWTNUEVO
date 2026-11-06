"""
================================================================================
MÓDULO 8: VISUALIZACIÓN DE RESULTADOS ACÚSTICOS
SIMULADOR ESWT - PROYECTO BIOINGENIERÍA (UNER)
================================================================================
Integra lienzos de Matplotlib preparados para las 8 representaciones técnicas
requeridas por el anteproyecto sin generar gráficos con datos ficticios.
================================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QScrollArea, QFrame, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from interfaz.componentes import (
    Colores, TarjetaContenedor, BotonSecundario, BadgeEstado
)
from modelos.resultados import ResultadosSimulacion


class ModuloResultados(QWidget):
    """Visualizador científico de resultados acústicos en Matplotlib."""

    def __init__(self, resultados: ResultadosSimulacion = None, parent=None):
        super().__init__(parent)
        self.resultados = resultados or ResultadosSimulacion()
        self._inicializar_ui()

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

        badge = BadgeEstado("VISUALIZACIÓN CIENTÍFICA", "info")
        l_head.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        t = QLabel("Representación Gráfica de Campos y Presión Acústica")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Colores.TEXTO_TITULO};")
        l_head.addWidget(t)

        sub = QLabel(
            "Lienzo gráfico integrado con Matplotlib preparado para representar las 8 vistas del campo "
            "acústico cuando se conecte el motor numérico. No genera simulaciones falsas ni curvas inventadas."
        )
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {Colores.TEXTO_SECUNDARIO};")
        sub.setWordWrap(True)
        l_head.addWidget(sub)

        layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. SELECTOR DE VISTA Y CONTROLES DE LIENZO
        # ----------------------------------------------------------------------
        barra_ctrl = TarjetaContenedor()
        l_b = QHBoxLayout(barra_ctrl)
        l_b.setContentsMargins(18, 12, 18, 12)
        l_b.setSpacing(14)

        lbl_sel = QLabel("Seleccionar Vista Científica:")
        lbl_sel.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        l_b.addWidget(lbl_sel)

        self.combo_vistas = QComboBox()
        self.combo_vistas.addItems([
            "1. Mapa Bidimensional de Presión p(x, z)",
            "2. Distribución Espacial de Presión Máxima (Isoclinas)",
            "3. Presión Máxima vs Profundidad (Eje Axial)",
            "4. Distribución Lateral de Presión en Región Focal",
            "5. Evolución Temporal del Pulso Acústico (t_rise, P+, P-)",
            "6. Atenuación de Señal por Estrato Tisular",
            "7. Comparación entre Superficies Planas y Curvas",
            "8. Bucle Iterativo y Boxplot de Confiabilidad (n=50)",
            "9. Barrido Paramétrico de Geometrías (Tarea 4.1)",
            "10. Plano Técnico Acotado del Aplicador (2D)"
        ])
        self.combo_vistas.setStyleSheet("padding: 6px; font-weight: 500;")
        self.combo_vistas.currentIndexChanged.connect(self._actualizar_grafico)
        l_b.addWidget(self.combo_vistas, stretch=1)

        self.btn_exportar_fig = BotonSecundario("💾 Guardar Gráfico (PNG)")
        self.btn_exportar_fig.clicked.connect(self._exportar_png)
        l_b.addWidget(self.btn_exportar_fig)

        layout.addWidget(barra_ctrl)

        # ----------------------------------------------------------------------
        # 3. CANVAS DE MATPLOTLIB
        # ----------------------------------------------------------------------
        tarjeta_canvas = TarjetaContenedor()
        l_can = QVBoxLayout(tarjeta_canvas)
        l_can.setContentsMargins(16, 14, 16, 14)
        l_can.setSpacing(8)

        self.figura = Figure(figsize=(8.0, 4.6), dpi=110, facecolor="#ffffff")
        self.canvas = FigureCanvasQTAgg(self.figura)
        l_can.addWidget(self.canvas)

        layout.addWidget(tarjeta_canvas)

        layout.addStretch()
        scroll.setWidget(contenedor)

        l_root = QVBoxLayout(self)
        l_root.setContentsMargins(0, 0, 0, 0)
        l_root.addWidget(scroll)

        self._actualizar_grafico(0)

    def actualizar_resultados(self, resultados: ResultadosSimulacion):
        self.resultados = resultados
        self._actualizar_grafico(self.combo_vistas.currentIndex())

    def _actualizar_grafico(self, indice: int):
        self.figura.clear()
        ax = self.figura.add_subplot(111)

        nombre_vista = self.combo_vistas.currentText()

        # Si tenemos resultados disponibles calculados por el motor
        if self.resultados and self.resultados.disponible:
            ax.set_facecolor("#ffffff")
            ax.set_title(nombre_vista, fontsize=10, fontweight='bold', color=Colores.AZUL_PRIMARIO, pad=12)

            res = self.resultados
            if indice in [0, 1]:  # 1. Mapa 2D de Presión / 2. Isoclinas
                X = res.eje_x_cm
                Z = res.eje_z_cm
                mapa = res.mapa_presion_peak_mpa
                im = ax.imshow(
                    mapa,
                    extent=[X[0], X[-1], Z[-1], Z[0]],
                    aspect='auto',
                    cmap='inferno'
                )
                cbar = self.figura.colorbar(im, ax=ax, pad=0.02)
                cbar.set_label('Presión Peak (MPa)', fontsize=8)

                if indice == 1: # Isoclinas / contorno a -6 dB
                    p_max = np.max(mapa)
                    ax.contour(X, Z, mapa, levels=[p_max * 0.707], colors=['cyan'], linewidths=[1.8])
                    ax.plot([], [], color='cyan', lw=1.8, label='Zona focal a -6 dB')

                ax.axhline(0.15, color='#0284c7', linestyle='--', label='Gel / Epidermis (1.5 mm)')
                ax.axhline(0.40, color='#16a34a', linestyle='--', label='Dermis Fibrótica')
                ax.set_xlabel("Dirección Lateral x (cm)", fontsize=8.5)
                ax.set_ylabel("Profundidad Axial z (cm)", fontsize=8.5)
                ax.legend(loc='lower left', fontsize=7.5)

            elif indice in [2, 5]: # 3. Presión Máxima vs Profundidad / 6. Atenuación
                Z = res.eje_z_cm
                P_z = res.perfil_axial_profundidad_mpa
                ax.plot(P_z, Z, color='#dc2626', lw=2.2, label='Presión Peak Axial p(z)')
                ax.axvline(0.5, color='#16a34a', linestyle='--', lw=1.5, label='Presión Mínima Diana (0.50 MPa)')
                ax.set_xlabel("Presión Acústica (MPa)", fontsize=8.5)
                ax.set_ylabel("Profundidad Axial z (cm)", fontsize=8.5)
                ax.set_ylim(max(Z), 0.0) # Invertido
                ax.grid(True, linestyle=':', alpha=0.6)
                ax.legend(loc='lower right', fontsize=7.5)

            elif indice == 3: # 4. Distribución Lateral en Región Focal
                X = res.eje_x_cm
                P_x = res.perfil_radial_focal_mpa
                ax.plot(X, P_x, color='#0284c7', lw=2.2, label='Perfil Radial en Foco')
                ax.set_xlabel("Distancia Radial x (cm)", fontsize=8.5)
                ax.set_ylabel("Presión Acústica (MPa)", fontsize=8.5)
                ax.grid(True, linestyle=':', alpha=0.6)
                ax.legend(loc='upper right', fontsize=7.5)

            elif indice == 4: # 5. Pulso Temporal p(t)
                t = res.eje_tiempo_ns
                p_t = res.senal_pulso_fuente_mpa
                ax.plot(t, p_t, color='#0284c7', lw=2.2, label='Pulso Acústico p(t)')
                ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
                ax.axhline(res.metricas.get("presion_p_positiva_mpa", 40.0), color='#dc2626', linestyle=':', label=f"P+ = {res.metricas.get('presion_p_positiva_mpa', 40.0):.1f} MPa")
                ax.axhline(res.metricas.get("presion_p_negativa_mpa", -10.0), color='#16a34a', linestyle=':', label=f"P- = {res.metricas.get('presion_p_negativa_mpa', -10.0):.1f} MPa")
                ax.set_xlabel("Tiempo (ns)", fontsize=8.5)
                ax.set_ylabel("Presión Acústica (MPa)", fontsize=8.5)
                ax.set_xlim(0, 350)
                ax.grid(True, linestyle=':', alpha=0.6)
                ax.legend(loc='upper right', fontsize=7.5)

            elif indice == 7: # 8. Bucle Iterativo y Boxplot de Confiabilidad
                from visualizacion.graficos import graficar_boxplot_confiabilidad
                graficar_boxplot_confiabilidad(
                    ax=ax,
                    muestras_p_peak=res.muestras_p_peak_iteraciones,
                    muestras_efd=res.muestras_efd_iteraciones,
                    estilo_oscuro=False
                )

            elif indice == 8: # 9. Barrido Paramétrico de Geometrías (Tarea 4.1)
                from fisica.barrido_geometrico import EvaluadorGeometriaESWT
                barrido = EvaluadorGeometriaESWT.ejecutar_barrido_completo()
                
                # Filtrar configuraciones válidas
                validas = [r for r in barrido if r.get("valida", False)]
                etiquetas = [f"Ø{int(r['apertura_mm'])}-R{int(r['radio_curvatura_mm'])}" for r in validas]
                p_maxs = [r["p_max_tejido_mpa"] for r in validas]
                focos = [r["z_pico_simulado_tejido_mm"] for r in validas]
                
                colores_barras = ['#10b981' if r["cumple_rango_terapeutico_5_20mm"] else '#f59e0b' for r in validas]
                
                x_idx = np.arange(len(etiquetas))
                ax.bar(x_idx, p_maxs, color=colores_barras, alpha=0.85, edgecolor='#334155', label='P_max en Tejido (MPa)')
                
                # Resaltar la geometría seleccionada (30-30)
                for i, r in enumerate(validas):
                    if r["apertura_mm"] == 30.0 and r["radio_curvatura_mm"] == 30.0:
                        ax.bar(x_idx[i], p_maxs[i], color='#0284c7', edgecolor='#0369a1', lw=2.5, label='Seleccionada (Ø30-R30)')
                        ax.annotate('SELECCIONADA\n(F=1.00, D15)', (x_idx[i], p_maxs[i]),
                                    xytext=(x_idx[i], p_maxs[i] + 0.3), ha='center',
                                    fontsize=7.5, fontweight='bold', color='#0284c7')

                ax.set_xticks(x_idx)
                ax.set_xticklabels(etiquetas, rotation=45, ha='right', fontsize=7.0)
                ax.set_ylabel("Presión Máxima Focal en Tejido (MPa)", fontsize=8.5)
                ax.set_title("Barrido Paramétrico: Presión Focal vs Geometría del Casquete Cóncavo", fontsize=9.5, fontweight='bold')
                ax.grid(True, linestyle=':', alpha=0.5)
                ax.legend(loc='upper right', fontsize=7.5)

            elif indice == 9: # 10. Plano Técnico Acotado del Aplicador (2D)
                import os
                import matplotlib.image as mpimg
                ruta_plano = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plano_acotado_aplicador_eswt.png")
                if not os.path.exists(ruta_plano):
                    from visualizacion.plano_acotado import generar_plano_acotado_aplicador
                    generar_plano_acotado_aplicador(ruta_plano)
                
                if os.path.exists(ruta_plano):
                    img = mpimg.imread(ruta_plano)
                    ax.imshow(img)
                    ax.axis('off')
                    ax.set_title("Plano Acotado 2D del Aplicador y Casquete Cóncavo (Tarea 4.1)", fontsize=9.5, fontweight='bold')
                else:
                    ax.text(0.5, 0.5, "Plano técnico no encontrado.", ha='center', va='center', transform=ax.transAxes)

            else:
                ax.text(0.5, 0.5, f"Vista Comparativa:\n{nombre_vista}", ha='center', va='center', transform=ax.transAxes, fontsize=10)

        # Si aún no se corrió la simulación
        else:
            ax.set_facecolor("#f8fafc")
            ax.set_title(nombre_vista, fontsize=10, fontweight='bold', color=Colores.AZUL_PRIMARIO, pad=12)

            if indice in [0, 1]:  # Mapas 2D
                ax.set_xlabel("Dirección Lateral x (cm)", fontsize=8.5)
                ax.set_ylabel("Profundidad z (cm)", fontsize=8.5)
                ax.set_xlim(-1.0, 1.0)
                ax.set_ylim(2.0, 0.0)
                ax.axhline(0.15, color='#0284c7', linestyle='--', label='Superficie Piel (z = 1.5 mm)')
                ax.axhline(1.00, color='#dc2626', linestyle=':', label='Profundidad Focal Diana (z = 1.0 cm)')
                ax.axhline(1.80, color='#16a34a', linestyle='--', label='Dermis Profunda (z = 1.8 cm)')
                ax.legend(loc='lower left', fontsize=7.5)

            elif indice in [2, 5]: # Presión vs profundidad / atenuación
                ax.set_xlabel("Presión Acústica (MPa)", fontsize=8.5)
                ax.set_ylabel("Profundidad z (cm)", fontsize=8.5)
                ax.set_xlim(0.0, 45.0)
                ax.set_ylim(2.0, 0.0)
                ax.axvline(0.5, color='#dc2626', linestyle='--', lw=1.5, label='Presión Mínima Diana (0.50 MPa)')
                ax.axhspan(0.4, 1.3, color='#fef3c7', alpha=0.5, label='Zona Cicatriz Hipertrófica')
                ax.legend(loc='lower right', fontsize=7.5)

            elif indice == 4: # Pulso temporal
                ax.set_xlabel("Tiempo (ns)", fontsize=8.5)
                ax.set_ylabel("Amplitud de Presión (MPa)", fontsize=8.5)
                ax.set_xlim(0, 350)
                ax.set_ylim(-15, 60)
                ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
                ax.text(20, 45, "Frente de subida (5 a 10 ns)\nDuración total ~300 ns", fontsize=7.5, color='#475569')

            elif indice == 8: # Barrido en modo reposo
                ax.text(0.5, 0.5, "Ejecute la simulación o seleccione la vista para ver el barrido paramétrico.", ha='center', va='center', transform=ax.transAxes)

            elif indice == 9: # Plano acotado en modo reposo
                import os
                import matplotlib.image as mpimg
                ruta_plano = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plano_acotado_aplicador_eswt.png")
                if not os.path.exists(ruta_plano):
                    from visualizacion.plano_acotado import generar_plano_acotado_aplicador
                    generar_plano_acotado_aplicador(ruta_plano)
                if os.path.exists(ruta_plano):
                    img = mpimg.imread(ruta_plano)
                    ax.imshow(img)
                    ax.axis('off')
                else:
                    ax.text(0.5, 0.5, "Plano técnico acotado.", ha='center', va='center', transform=ax.transAxes)

            else:
                ax.set_xlabel("Parámetro de Entrada", fontsize=8.5)
                ax.set_ylabel("Respuesta Acústica", fontsize=8.5)

            ax.grid(True, linestyle=':', alpha=0.6)

            cartel = (
                "Haga clic en 'Ejecutar Comprobación y Simulación'\nen el Módulo de Motor para calcular y visualizar los datos numéricos."
            )
            ax.text(
                0.5, 0.5, cartel,
                transform=ax.transAxes,
                ha='center', va='center',
                fontsize=8.5, color=Colores.TEXTO_SECUNDARIO,
                bbox=dict(boxstyle='round,pad=0.8', facecolor='#ffffff', edgecolor=Colores.BORDE_TARJETA, alpha=0.9)
            )

        self.figura.tight_layout()
        self.canvas.draw()

    def _exportar_png(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Gráfico",
            f"grafico_eswt_{self.combo_vistas.currentIndex() + 1}.png",
            "Imágenes PNG (*.png)"
        )
        if ruta:
            try:
                self.figura.savefig(ruta, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Exportación Exitosa", f"Gráfico guardado en:\n{ruta}")
            except Exception as e:
                QMessageBox.critical(self, "Error al Exportar", f"No se pudo guardar la imagen: {str(e)}")
