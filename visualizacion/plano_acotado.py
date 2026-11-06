"""
================================================================================
GENERADOR DE PLANO TÉCNICO ACOTADO 2D DEL APLICADOR ESWT (TAREA 4.1)
SIMULADOR ESWT - TALLER DE BIOINGENIERÍA (UNER)
================================================================================
Genera el plano acotado 2D del aplicador manual con:
- Vista lateral general y sección longitudinal acotada.
- Cabezal cóncavo (apertura 30 mm, R=30 mm, chasis externo Ø=38 mm).
- Distanciador acústico intercambiable (15 mm nominal para foco a 15 mm en tejido; set D10-D25).
- Empuñadura cilíndrica ergonómica (longitud 120 mm, diámetro 33 mm).
- Botonera de disparo táctil, paso de cable axial y sellos de estanqueidad.
================================================================================
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
import numpy as np


def generar_plano_acotado_aplicador(ruta_salida: str = "plano_acotado_aplicador_eswt.png") -> Figure:
    """Genera y guarda el plano técnico acotado formal 2D."""
    fig = Figure(figsize=(13.0, 8.5), dpi=300, facecolor="#ffffff")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#ffffff")
    ax.set_aspect("equal")

    # Ocultar ejes estándar
    ax.axis("off")

    # Marco del plano normalizado (formato rótulo de ingeniería)
    ax.add_patch(patches.Rectangle((0, 0), 260, 170, fill=False, edgecolor="#0f172a", lw=2.0))
    ax.add_patch(patches.Rectangle((2, 2), 256, 166, fill=False, edgecolor="#0f172a", lw=0.8))

    # Rótulo inferior derecho
    ax.add_patch(patches.Rectangle((150, 2), 108, 38, fill=False, edgecolor="#0f172a", lw=1.2))
    ax.plot([150, 258], [24, 24], color="#0f172a", lw=0.8)
    ax.plot([150, 258], [14, 14], color="#0f172a", lw=0.8)
    ax.plot([204, 204], [2, 24], color="#0f172a", lw=0.8)

    ax.text(152, 32, "UNIVERSIDAD NACIONAL DE ENTRE RÍOS - FACULTAD DE INGENIERÍA", fontsize=6.5, fontweight="bold", color="#0f172a")
    ax.text(152, 26, "TALLER DE BIOINGENIERÍA | ANTEPROYECTO ESWT (TAREA 4.1)", fontsize=6.5, color="#334155")
    ax.text(152, 17, "PLANO: ENSAMBLE SECCIONADO Y COTAS DEL APLICADOR", fontsize=7, fontweight="bold", color="#0369a1")
    ax.text(152, 6, "ESCALA: 1:1 (mm) | AUTORAS: Gastaldi, Gerstner, Kessel", fontsize=6, color="#475569")
    ax.text(206, 6, "FECHA: Nov 2026 | HOJA 1/1", fontsize=6, color="#475569")

    # Coordenadas base del ensamble
    # Eje longitudinal horizontal Y=100
    y_eje = 100.0
    x_inicio = 35.0

    # Línea de centro / eje de simetría (trazo largo y punto)
    ax.plot([x_inicio - 15, x_inicio + 205], [y_eje, y_eje], color="#dc2626", linestyle="-.", lw=1.0, label="Eje de Simetría Acústico")

    # 1. Distanciador Acústico Intercambiable (Frontal / Izquierda)
    # Longitud = 15 mm, Diámetro = 36 mm
    ancho_dist = 15.0
    diam_dist = 36.0
    x_dist = x_inicio
    ax.add_patch(patches.Rectangle(
        (x_dist, y_eje - diam_dist/2.0), ancho_dist, diam_dist,
        facecolor="#e0f2fe", edgecolor="#0284c7", lw=1.4, hatch="//"
    ))
    ax.text(x_dist + ancho_dist/2.0, y_eje + diam_dist/2.0 + 3.0, "Distanciador 15 mm\n(Acople Acústico)", fontsize=6.5, ha="center", color="#0284c7", fontweight="bold")

    # Membrana frontal de contacto (espesor 1 mm)
    ax.plot([x_dist, x_dist], [y_eje - diam_dist/2.0, y_eje + diam_dist/2.0], color="#0f172a", lw=2.2)
    ax.text(x_dist - 2.0, y_eje - diam_dist/2.0 - 5.0, "Membrana / Piel (z=0)", fontsize=6, ha="right", color="#0f172a")

    # 2. Cabezal Acústico Rígido
    # Longitud = 45 mm, Diámetro = 38 mm (<= 40 mm)
    ancho_cabezal = 45.0
    diam_cabezal = 38.0
    x_cabezal = x_dist + ancho_dist
    ax.add_patch(patches.Rectangle(
        (x_cabezal, y_eje - diam_cabezal/2.0), ancho_cabezal, diam_cabezal,
        facecolor="#f1f5f9", edgecolor="#0f172a", lw=1.6
    ))

    # Casquete Cóncavo Interno (R=30 mm, Apertura=30 mm)
    # Dibujamos el arco cóncavo centrado
    ang_arco = np.linspace(-np.pi/4.5, np.pi/4.5, 50)
    r_concavo = 30.0
    # Centro de la esfera cóncava ubicado en el foco
    x_centro_esfera = x_cabezal + r_concavo - 6.0
    arco_x = x_centro_esfera - r_concavo * np.cos(ang_arco)
    arco_y = y_eje + r_concavo * np.sin(ang_arco)
    ax.plot(arco_x, arco_y, color="#0284c7", lw=3.0, label="Casquete Cóncavo Piezoeléctrico")

    # Marcador de foco acústico terapéutico (a 10 mm en el tejido, a la izquierda de la membrana)
    foco_tejido_x = x_dist - 10.0
    ax.plot(foco_tejido_x, y_eje, marker="o", markersize=7, color="#dc2626", zorder=6)
    ax.plot([foco_tejido_x, foco_tejido_x], [y_eje - 12, y_eje + 12], color="#dc2626", linestyle=":", lw=1.2)
    ax.text(foco_tejido_x, y_eje - 16, "Zona Focal Terapéutica\n(zf = 10 mm en tejido)", fontsize=6.5, ha="center", color="#dc2626", fontweight="bold")

    # 3. Transición cónica cabezal - empuñadura
    x_trans = x_cabezal + ancho_cabezal
    ancho_trans = 10.0
    diam_mango = 33.0
    puntos_trans_sup = [[x_trans, y_eje + diam_cabezal/2.0], [x_trans + ancho_trans, y_eje + diam_mango/2.0]]
    puntos_trans_inf = [[x_trans, y_eje - diam_cabezal/2.0], [x_trans + ancho_trans, y_eje - diam_mango/2.0]]
    ax.plot([x_trans, x_trans + ancho_trans], [y_eje + diam_cabezal/2.0, y_eje + diam_mango/2.0], color="#0f172a", lw=1.6)
    ax.plot([x_trans, x_trans + ancho_trans], [y_eje - diam_cabezal/2.0, y_eje - diam_mango/2.0], color="#0f172a", lw=1.6)

    # 4. Empuñadura Ergonómica (Longitud = 120 mm, Diámetro = 33 mm)
    x_mango = x_trans + ancho_trans
    largo_mango = 120.0
    ax.add_patch(patches.Rectangle(
        (x_mango, y_eje - diam_mango/2.0), largo_mango, diam_mango,
        facecolor="#e2e8f0", edgecolor="#0f172a", lw=1.6
    ))

    # Relieve de agarre texturado (grip estriado antideslizante)
    for xi in np.linspace(x_mango + 20, x_mango + 90, 15):
        ax.plot([xi, xi], [y_eje - diam_mango/2.0 + 1.5, y_eje + diam_mango/2.0 - 1.5], color="#94a3b8", lw=0.9)

    # Botonera de control integrada (Pulsador de disparo ergonómico a 35 mm del inicio del mango)
    x_btn = x_mango + 35.0
    ax.add_patch(patches.Rectangle((x_btn - 6.0, y_eje + diam_mango/2.0), 12.0, 3.5, facecolor="#0284c7", edgecolor="#0f172a", lw=1.2))
    ax.text(x_btn, y_eje + diam_mango/2.0 + 6.0, "Pulsador de Disparo\n(Doble acción)", fontsize=6, ha="center", color="#0369a1", fontweight="bold")

    # 5. Salida de Cable y Pasacables Flexible
    x_cola = x_mango + largo_mango
    ax.add_patch(patches.Polygon([[x_cola, y_eje + 8], [x_cola + 16, y_eje + 4], [x_cola + 16, y_eje - 4], [x_cola, y_eje - 8]],
                                 facecolor="#334155", edgecolor="#0f172a", lw=1.2))
    ax.plot([x_cola + 16, x_cola + 30], [y_eje, y_eje], color="#0f172a", lw=4.0)
    ax.text(x_cola + 23, y_eje + 6, "Cable de Alta Tensión\n(Blindado Coaxial)", fontsize=5.5, ha="center", color="#475569")

    # COTAS TÉCNICAS NORMALIZADAS (Líneas de cota con flechas y textos)
    color_cota = "#0f172a"

    def dibujar_cota_h(x1, x2, y, texto, offset_y=2.5):
        ax.annotate('', xy=(x1, y), xytext=(x2, y),
                    arrowprops=dict(arrowstyle='<->', color=color_cota, lw=0.9))
        ax.plot([x1, x1], [y - 3, y + 3], color=color_cota, lw=0.6)
        ax.plot([x2, x2], [y - 3, y + 3], color=color_cota, lw=0.6)
        ax.text((x1 + x2)/2.0, y + offset_y, texto, fontsize=6.5, ha='center', va='bottom', color=color_cota, fontweight='bold')

    def dibujar_cota_v(x, y1, y2, texto, offset_x=2.5):
        ax.annotate('', xy=(x, y1), xytext=(x, y2),
                    arrowprops=dict(arrowstyle='<->', color=color_cota, lw=0.9))
        ax.plot([x - 3, x + 3], [y1, y1], color=color_cota, lw=0.6)
        ax.plot([x - 3, x + 3], [y2, y2], color=color_cota, lw=0.6)
        ax.text(x + offset_x, (y1 + y2)/2.0, texto, fontsize=6.5, ha='left', va='center', rotation=90, color=color_cota, fontweight='bold')

    # Cotas longitudinales inferiores
    y_cota_inf1 = y_eje - diam_cabezal/2.0 - 15.0
    dibujar_cota_h(x_dist, x_cabezal, y_cota_inf1, "15 (Distanciador)")
    dibujar_cota_h(x_cabezal, x_trans, y_cota_inf1, "45 (Cabezal)")
    dibujar_cota_h(x_mango, x_cola, y_cota_inf1, "120 (Empuñadura Sancho-Bru)")

    y_cota_inf2 = y_cota_inf1 - 12.0
    dibujar_cota_h(x_dist, x_cola, y_cota_inf2, "190 mm (Longitud Total del Aplicador)")

    # Cotas diametrales verticales
    dibujar_cota_v(x_cabezal + 22.0, y_eje - diam_cabezal/2.0, y_eje + diam_cabezal/2.0, "Ø 38 (Carcasa Cabezal ≤ 40 mm)", offset_x=-14)
    dibujar_cota_v(x_mango + 60.0, y_eje - diam_mango/2.0, y_eje + diam_mango/2.0, "Ø 33 mm (Empuñadura)", offset_x=-12)

    # Detalle de especificaciones técnicas en cuadro lateral
    cuadro_txt = (
        "ESPECIFICACIONES TÉCNICAS SELECCIONADAS (TAREA 4.1):\n"
        "• Transductor: Cerámica Piezoeléctrica Cóncava PZT-4 / PZT-8\n"
        "• Apertura Activa (2a): 30.0 mm | Radio Curvatura (R): 30.0 mm\n"
        "• Número F: F = R / 2a = 1.00 (Focalización Alta Eficiencia)\n"
        "• Distanciador Acústico: 15.0 mm (Sitúa foco a zf = 15.0 mm en tejido; intercambiable D10–D25)\n"
        "• Empuñadura Manual: Longitud 120 mm, Diámetro 33 mm (Ergonomía óptima)\n"
        "• Modo de Emisión: Normal Fija (0.0° - Sin articulación móvil)\n"
        "• Adaptabilidad: Contacto en manos y articulaciones mediante gel conformable"
    )
    ax.text(12, 28, cuadro_txt, fontsize=6.8, color="#0f172a",
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#f8fafc", edgecolor="#cbd5e1", lw=1.0))

    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=300, bbox_inches="tight")
    return fig

