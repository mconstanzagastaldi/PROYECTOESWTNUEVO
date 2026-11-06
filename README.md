# SIMULADOR ESWT
**Diseño y análisis computacional de un aplicador piezoeléctrico de ondas de choque extracorpóreas**

Proyecto Académico de Bioingeniería - Universidad Nacional de Entre Ríos (UNER)  
Facultad de Ingeniería | Cátedra: Taller de Bioingeniería  
**Autoras:** Gastaldi, María Constanza; Gerstner Soltermann, Marthina; Kessel, Florencia.  
**Asesor:** Zapata, Daniel.

---

## 1. Contexto y Objetivos del Proyecto

El proyecto aborda el diseño teórico y prototipado virtual de un aplicador de ondas de choque extracorpóreas de baja intensidad (**ESWT**, *Extracorporeal Shock Wave Therapy*) enfocado en la estimulación de la angiogénesis y remodelación tisular en **cicatrices hipertróficas postquemadura**.

### Delimitación de Responsabilidades en el Equipo
* **Desarrollo de Software y Simulación Computacional (Esta aplicación):**
  * Arquitectura modular del software en Python.
  * Interfaz gráfica de escritorio con estándares biomédicos mediante **PySide6 (Qt)**.
  * Modelado de datos del aplicador, tejidos, geometría y parámetros operativos.
  * Servicios de validación, almacenamiento en formato JSON y exportación tabular en CSV.
  * Módulos de visualización bidimensional y perfiles acústicos en **Matplotlib**.
  * Preparación de interfaces desacopladas para la futura conexión con el motor físico numérico.
* **Formulación Física y Diseño Mecánico-Acústico:**
  * Trabajo en paralelo de diseño del casquete cóncavo, transductor piezoeléctrico, componentes eléctricos y acústicos que se conectarán a esta plataforma.

---

## 2. Requerimientos Operativos de Referencia (Anteproyecto)

* **Densidad de Flujo de Energía (EFD):** Rango de operación nominal entre $0.03\text{ mJ/mm}^2$ y $0.25\text{ mJ/mm}^2$ (valor de diseño preferente: $0.10\text{ mJ/mm}^2$).
* **Frecuencia de Repetición de Pulsos (PRF):** $4.0\text{ Hz}$ a $5.0\text{ Hz}$.
* **Profundidad Focal Terapéutica Objetivo:** $0.5\text{ cm}$ a $2.0\text{ cm}$ (alcanzando dermis profunda y tejido celular subcutáneo).
* **Dosificación de Disparos:** Ráfagas configurables entre $10$ y $500\text{ pulsos/cm}^2$.
* **Tecnología del Aplicador:** Generador piezoeléctrico focalizado sobre geometría cóncava con orientación angular ajustable.

---

## 3. Estructura Modular del Software

```text
PROYECTO NUEVO TALLER/
│
├── main.py                       # Punto de entrada de la aplicación
├── requirements.txt              # Dependencias de Python verificadas
├── README.md                     # Documentación técnica
│
├── interfaz/                     # Interfaz Gráfica (PySide6)
│   ├── ventana_principal.py      # Shell principal, navegación y barra de estado
│   ├── panel_inicio.py           # Pantalla de bienvenida y resumen de estado
│   ├── modulo_aplicador.py       # Configuración del cabezal y tecnología piezoeléctrica
│   ├── modulo_geometria.py       # Superficie anatómica (plana / curva) y orientación
│   ├── modulo_parametros.py      # Parámetros operativos y rangos de partida
│   ├── modulo_tejidos.py         # Gestión de estratos tisulares y propiedades
│   ├── modulo_simulacion.py      # Configuración de malla espacial y temporal
│   ├── modulo_resultados.py      # Visualización gráfica de resultados acústicos
│   ├── modulo_comparacion.py     # Comparativa de escenarios y orientaciones
│   └── componentes.py            # Widgets reutilizables, tarjetas y estilos Qt
│
├── modelos/                      # Modelos de datos puros (Dataclasses)
│   ├── aplicador.py              # Entidad del aplicador piezoeléctrico
│   ├── cabezal.py                # Geometría cóncava y orientación angular
│   ├── geometria.py              # Superficie cutánea y posición relativa
│   ├── tejido.py                 # Capas tisulares (rho, c, Z, alpha)
│   ├── parametros.py             # Parámetros operativos y dosimétricos
│   ├── configuracion.py          # Objeto contenedor de la sesión completa
│   └── resultados.py             # Estructura desacoplada para matrices acústicas
│
├── servicios/                    # Servicios de infraestructura y soporte
│   ├── gestor_configuracion.py   # Persistencia en archivos JSON
│   ├── validador.py              # Reglas de validación biofísica y rangos
│   └── exportacion.py            # Exportador a CSV y reporte de sesión
│
├── fisica/                       # Interfaces para formulación física futura
│   ├── onda_acustica.py          # Contrato para la ecuación de onda
│   ├── focalizacion.py           # Contrato para el casquete cóncavo
│   └── atenuacion.py             # Contrato para absorción tisular
│
├── simulacion/                   # Motor numérico
│   ├── malla.py                  # Discretización espacial (x, z)
│   ├── propagacion.py            # Contrato para el solver acústico
│   └── motor_simulacion.py       # Fachada del motor (informa estado desacoplado)
│
├── visualizacion/                # Gráficos con Matplotlib
│   ├── graficos.py               # Lienzos para p(x,z), perfiles axiales y tiempo
│   └── representacion_geometrica.py # Esquema 2D del aplicador sobre el tejido
│
├── datos/
│   └── configuraciones/          # Almacén de archivos de configuración (.json)
│
└── tests/                        # Suite de pruebas unitarias automatizadas (PyTest)
```

---

## 4. Instalación y Ejecución

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

