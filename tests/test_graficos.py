"""
Pruebas unitarias para el módulo de visualización científica (visualizacion/graficos.py y representacion_geometrica.py).
Verifica el cumplimiento de los 4 gráficos bioacústicos del anteproyecto ESWT.
"""

import pytest
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
import numpy as np

from visualizacion.graficos import (
    graficar_pulso_temporal,
    graficar_mapa_2d,
    graficar_perfil_axial,
    graficar_esquema_tisular
)
from visualizacion.representacion_geometrica import generar_figura_esquema_tisular


def test_graficar_pulso_temporal():
    fig = Figure()
    ax = fig.add_subplot(111)
    graficar_pulso_temporal(ax, efd_nominal=0.10, t_rise_ns=8.0, duracion_ns=300.0)
    
    # Debe tener curvas graficadas
    assert len(ax.lines) >= 1
    # Debe tener límites temporales hasta ~350 ns
    assert ax.get_xlim()[1] >= 300


def test_graficar_mapa_2d():
    fig = Figure()
    ax = fig.add_subplot(111)
    graficar_mapa_2d(ax, fig, efd_nominal=0.10, profundidad_focal_mm=10.0, tipo_quemadura="3er Grado")
    
    # Debe contener la imagen del mapa de calor (imshow)
    assert len(ax.images) >= 1
    # Límites axiales z en mm (0 a 25)
    ylim = ax.get_ylim()
    assert max(ylim) >= 20.0


def test_graficar_perfil_axial():
    fig = Figure()
    ax = fig.add_subplot(111)
    graficar_perfil_axial(ax, efd_nominal=0.10, profundidad_focal_mm=10.0, tipo_quemadura="3er Grado", edad_paciente=40)
    
    # Debe tener curvas y sombreado de ventana terapéutica
    assert len(ax.lines) >= 1
    assert len(ax.patches) >= 1  # axhspan ventana terapéutica


def test_graficar_esquema_tisular():
    fig = Figure()
    ax = fig.add_subplot(111)
    graficar_esquema_tisular(ax, tipo_superficie="Curva", profundidad_focal_mm=15.0)
    
    assert len(ax.lines) >= 1
    # Colecciones de fill_between
    assert len(ax.collections) >= 1


def test_generar_figura_esquema():
    fig = generar_figura_esquema_tisular(tipo_superficie="Plana")
    assert isinstance(fig, Figure)

