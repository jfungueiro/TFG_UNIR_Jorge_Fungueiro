"""
Archivo: controlador_gui.py
Descripción: Coordina vista, modelo y persistencia. Coordina el flujo de ejecución de la aplicación y evita la dependencia de los detalles internos del modelo y del sistema usado para la persistencia.
"""

from modelo import ejecutar_simulacion
from persistencia import exportar_a_excel


def ejecutar_desde_interfaz(configuracion):
    """Ejecuta simulación y exporta a Excel."""
    resultados = ejecutar_simulacion(configuracion)
    exportar_a_excel(resultados, configuracion["ruta_excel"])
    return resultados
