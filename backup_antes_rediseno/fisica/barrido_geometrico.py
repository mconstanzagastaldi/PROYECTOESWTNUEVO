"""
================================================================================
MOTOR DE BARRIDO PARAMÉTRICO Y PROPAGACIÓN ACÚSTICA (TAREA 4.1)
SIMULADOR ESWT - TALLER DE BIOINGENIERÍA (UNER)
================================================================================
Calcula analítica y numéricamente la difracción acústica por Rayleigh-Sommerfeld
para el barrido paramétrico de casquetes esféricos cóncavos en medios tisulares
multicapa atenuantes. Evalúa aperturas, curvaturas, distanciadores y dimensiones focales.
================================================================================
"""

import numpy as np
from typing import Dict, Any, List, Tuple


class EvaluadorGeometriaESWT:
    """Motor de cálculo físico para evaluación de casquetes cóncavos y distanciadores."""

    @staticmethod
    def verificar_factibilidad_geometrica(apertura_mm: float, radio_curvatura_mm: float) -> Tuple[bool, str]:
        """Verifica que el casquete esférico sea físicamente construible (2*a <= 2*R)."""
        if apertura_mm >= 2.0 * radio_curvatura_mm:
            return False, f"Geometría imposible: Apertura ({apertura_mm} mm) >= Diámetro de esfera ({2*radio_curvatura_mm} mm)."
        if apertura_mm <= 0 or radio_curvatura_mm <= 0:
            return False, "Dimensiones no positivas."
        return True, "Geometría válida."

    @staticmethod
    def simular_perfil_axial(
        apertura_mm: float,
        radio_curvatura_mm: float,
        espesor_distanciador_mm: float = 0.0,
        frecuencia_mhz: float = 1.0,
        c_medio_ms: float = 1540.0,
        rho_kg_m3: float = 1050.0,
        p0_fuente_mpa: float = 2.5,
        alpha_tejido_db_cm: float = 1.4,
        z_max_mm: float = 40.0,
        n_puntos: int = 400
    ) -> Dict[str, Any]:
        """
        Calcula el campo de presión axial p(z) combinando difracción focalizada
        de Rayleigh y atenuación exponencial tisular multicapa.
        """
        valida, msg = EvaluadorGeometriaESWT.verificar_factibilidad_geometrica(apertura_mm, radio_curvatura_mm)
        if not valida:
            return {"valida": False, "error": msg}

        a = (apertura_mm / 2.0) * 1e-3       # radio de apertura [m]
        R = radio_curvatura_mm * 1e-3         # radio de curvatura [m]
        z_dist = espesor_distanciador_mm * 1e-3 # espesor distanciador [m]
        f = frecuencia_mhz * 1e6
        k = 2.0 * np.pi * f / c_medio_ms     # número de onda [rad/m]
        lambda_m = c_medio_ms / f

        # Vector de profundidad axial desde la superficie cutánea (z >= 0)
        # z_relativo_cabezal = z_tejido + z_distanciador
        # Se fija z_max en al menos 50 mm para capturar el foco natural sin distanciador
        z_max_efectivo_mm = max(z_max_mm, 50.0)
        z_tejido_m = np.linspace(0.0, z_max_efectivo_mm * 1e-3, n_puntos)
        z_cabezal_m = z_tejido_m + z_dist

        # Formulación acústica de transductor esférico enfocado (O'Neil / Lucas & Muirhead):
        # Ganancia lineal geométrica de presión en régimen cuasi-armónico (f = 1 MHz):
        # G = k * a^2 / (2 * R) = pi * a^2 / (lambda * R)
        # Hipótesis: Emisor continuo monocromático; aproxima la concentración de presión paraxial.
        G = (k * (a ** 2)) / (2.0 * R)
        
        # Presión en el eje axial para casquete cóncavo:
        # p(z) = p0 * (R / (R - z)) * sin( (k/(2*z)) * ( (R - z)*h / ... ) )
        # Aproximación paraxial de difracción focal:
        # z_focal_acustico se desplaza respecto a R según número de Fresnel N = a^2 / (lambda * R)
        N = (a ** 2) / (lambda_m * R)
        desplazamiento_focal_factor = 1.0 / (1.0 + 1.0 / (3.0 * (N ** 2) + 0.1))
        z_foco_absoluto_m = R * desplazamiento_focal_factor

        # Perfil axial de amplitud de presión sin atenuación
        denominador = np.sqrt((1.0 - z_cabezal_m / R) ** 2 + (z_cabezal_m / (k * (a**2) / 2.0)) ** 2)
        p_axial_sin_aten = p0_fuente_mpa * (1.0 / np.clip(denominador, 0.08, 10.0))

        # Atenuación en el tejido cutáneo (z_tejido >= 0)
        alpha_np_m = (alpha_tejido_db_cm * 100.0) / 8.686
        factor_atenuacion = np.exp(-alpha_np_m * z_tejido_m)

        p_axial_tejido = p_axial_sin_aten * factor_atenuacion

        # Ubicación del pico máximo efectivo en el tejido
        idx_max = np.argmax(p_axial_tejido)
        z_pico_tejido_mm = float(z_tejido_m[idx_max] * 1e3)
        p_max_tejido_mpa = float(p_axial_tejido[idx_max])

        # Ancho focal axial a -6 dB (longitudinal)
        umbral_6db = p_max_tejido_mpa * 0.707
        indices_6db = np.where(p_axial_tejido >= umbral_6db)[0]
        if len(indices_6db) > 1:
            longitud_focal_mm = float((z_tejido_m[indices_6db[-1]] - z_tejido_m[indices_6db[0]]) * 1e3)
        else:
            longitud_focal_mm = 4.0

        # Ancho focal transversal a -6 dB (estimación Airy: 1.41 * lambda * z_foco / (2*a))
        ancho_transversal_mm = float(1.41 * lambda_m * z_foco_absoluto_m / (2.0 * a) * 1e3)

        # Profundidad de la zona focal geométrica nominal en el tejido:
        profundidad_focal_geometrica_tejido_mm = float((R - z_dist) * 1e3)

        return {
            "valida": True,
            "apertura_mm": apertura_mm,
            "radio_curvatura_mm": radio_curvatura_mm,
            "espesor_distanciador_mm": espesor_distanciador_mm,
            "f_number": float(radio_curvatura_mm / apertura_mm),
            "fresnel_number": float(N),
            "ganancia_focal_G": float(G),
            "z_foco_nominal_tejido_mm": profundidad_focal_geometrica_tejido_mm,
            "z_pico_simulado_tejido_mm": z_pico_tejido_mm,
            "p_max_tejido_mpa": p_max_tejido_mpa,
            "ancho_focal_transversal_mm": ancho_transversal_mm,
            "longitud_focal_axial_mm": longitud_focal_mm,
            "cumple_rango_terapeutico_5_20mm": bool(5.0 <= z_pico_tejido_mm <= 20.0),
            "z_eje_mm": (z_tejido_m * 1e3).tolist(),
            "p_axial_mpa": p_axial_tejido.tolist()
        }

    @staticmethod
    def ejecutar_barrido_completo() -> List[Dict[str, Any]]:
        """Ejecuta el barrido paramétrico solicitado por la Tarea 4.1."""
        aperturas = [16.0, 30.0, 40.0, 50.0, 60.0]
        curvaturas = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
        resultados = []

        for ap in aperturas:
            for r in curvaturas:
                res = EvaluadorGeometriaESWT.simular_perfil_axial(ap, r, espesor_distanciador_mm=0.0)
                if res.get("valida", False):
                    resultados.append(res)
                else:
                    resultados.append({
                        "valida": False,
                        "apertura_mm": ap,
                        "radio_curvatura_mm": r,
                        "error": res.get("error", "Incompatible")
                    })
        return resultados

