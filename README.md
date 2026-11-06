# SIMULADOR ESWT

**Diseño y análisis computacional de un aplicador piezoeléctrico de ondas de choque extracorpóreas**

Proyecto Académico de Bioingeniería – Universidad Nacional de Entre Ríos (UNER)  
Facultad de Ingeniería | Cátedra: Taller de Bioingeniería

**Autoras:** María Constanza Gastaldi, Marthina Gerstner Soltermann y Florencia Kessel.  
**Asesor:** Daniel Zapata.

---

## 1. Contexto y objetivos del proyecto

El proyecto aborda el diseño teórico y el prototipado virtual de un aplicador de ondas de choque extracorpóreas de baja intensidad (**ESWT**, *Extracorporeal Shock Wave Therapy*), orientado al estudio de su potencial aplicación en la estimulación de la angiogénesis y la remodelación tisular en cicatrices hipertróficas postquemadura.

El software constituye una plataforma de configuración, modelado y análisis computacional destinada a estudiar los parámetros operativos del aplicador y la propagación acústica en diferentes medios tisulares.

### Delimitación de responsabilidades del equipo

**Desarrollo de software y simulación computacional (esta aplicación)**

- Arquitectura modular del software en Python.
- Interfaz gráfica de escritorio mediante PySide6 (Qt).
- Modelado de datos del aplicador, tejidos, geometría y parámetros operativos.
- Servicios de validación, almacenamiento en formato JSON y exportación tabular en CSV.
- Módulos de visualización bidimensional y perfiles acústicos mediante Matplotlib.
- Preparación de interfaces desacopladas para la integración del motor físico numérico.

**Formulación física y diseño mecánico-acústico**

- Diseño conceptual del casquete cóncavo y del transductor piezoeléctrico.
- Análisis de los componentes eléctricos y acústicos.
- Definición de las características geométricas y operativas del aplicador.
- Estudio de la interacción entre el campo acústico y los distintos medios tisulares.

## 2. Requerimientos operativos de referencia

Los siguientes valores corresponden a los rangos de partida establecidos en el anteproyecto:

| Parámetro | Valor de referencia |
|---|---|
| Densidad de flujo de energía (EFD) | 0,03–0,25 mJ/mm² |
| EFD preferente de diseño | 0,10 mJ/mm² |
| Frecuencia de repetición de pulsos (PRF) | 4–5 Hz |
| Profundidad focal objetivo | 0,5–2 cm |
| Dosificación | 10–500 pulsos/cm² |
| Tecnología | Generador piezoeléctrico focalizado sobre geometría cóncava |

Estos parámetros constituyen referencias de diseño y no deben interpretarse como un protocolo terapéutico clínicamente validado.

## 3. Estructura modular del software

```text
PROYECTO NUEVO TALLER/
│
├── main.py
├── requirements.txt
├── README.md
│
├── interfaz/
│   ├── ventana_principal.py
│   ├── panel_inicio.py
│   ├── modulo_aplicador.py
│   ├── modulo_geometria.py
│   ├── modulo_parametros.py
│   ├── modulo_tejidos.py
│   ├── modulo_simulacion.py
│   ├── modulo_resultados.py
│   ├── modulo_comparacion.py
│   └── componentes.py
│
├── modelos/
│   ├── aplicador.py
│   ├── cabezal.py
│   ├── geometria.py
│   ├── tejido.py
│   ├── parametros.py
│   ├── configuracion.py
│   └── resultados.py
│
├── servicios/
│   ├── gestor_configuracion.py
│   ├── validador.py
│   └── exportacion.py
│
├── fisica/
│   ├── onda_acustica.py
│   ├── focalizacion.py
│   └── atenuacion.py
│
├── simulacion/
│   ├── malla.py
│   ├── propagacion.py
│   └── motor_simulacion.py
│
├── visualizacion/
│   ├── graficos.py
│   └── representacion_geometrica.py
│
├── datos/
│   └── configuraciones/
│
└── tests/
```

*Nota: la estructura representa la organización modular prevista para el software. La implementación efectiva de cada módulo y sus funcionalidades debe verificarse en el código fuente.*

## 4. Tecnologías utilizadas

- **Python:** lenguaje principal de desarrollo.
- **PySide6 (Qt):** construcción de la interfaz gráfica.
- **Matplotlib:** visualización de resultados y perfiles acústicos.
- **JSON:** almacenamiento de configuraciones.
- **CSV:** exportación de datos y resultados.
- **PyTest:** pruebas automatizadas del software.

## 5. Instalación y ejecución

### Requisitos previos

- Python instalado.
- Git instalado (opcional, para control de versiones).

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Ejecución de la aplicación

```bash
python main.py
```

## 6. Alcance y limitaciones

El desarrollo corresponde a un proyecto académico de diseño conceptual, modelado y simulación computacional.

La plataforma está orientada al análisis de parámetros operativos y al estudio de la propagación acústica. Los resultados obtenidos dependen de las ecuaciones, propiedades de los medios y modelos físicos efectivamente implementados.

El simulador no constituye un dispositivo médico funcional ni reemplaza ensayos experimentales o validaciones clínicas. Tampoco permite afirmar efectos biológicos medidos, como angiogénesis o remodelación tisular, si estos no forman parte de un modelo biológico específico.

---

**Universidad Nacional de Entre Ríos – Facultad de Ingeniería**  
**Taller de Bioingeniería**