import sys
import os

# Asegura que la raíz del proyecto esté en el path de búsqueda de módulos
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRECTORIO_RAIZ)

