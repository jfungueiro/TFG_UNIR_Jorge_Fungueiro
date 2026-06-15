"""
Archivo: persistencia.py
Descripción: Exportación de resultados a Excel.
"""

import pandas as pd


def exportar_a_excel(resultados, ruta_salida):
    """Exporta todos los resultados a Excel."""
    filas_configuracion = []
    for clave, valor in resultados["configuracion"].items():
        filas_configuracion.append({"parametro": clave, "valor": str(valor)})

    df_configuracion = pd.DataFrame(filas_configuracion)
    df_detalle = pd.DataFrame(resultados["detalle_estimaciones"])
    df_metricas_sprint = pd.DataFrame(resultados["metricas_sprint"])
    df_metricas_globales = pd.DataFrame([resultados["metricas_globales"]])
    df_evolucion = pd.DataFrame(resultados["evolucion_jugadores"])
    df_aprendizaje = pd.DataFrame(resultados["eventos_aprendizaje"])

    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
        df_configuracion.to_excel(writer, sheet_name="configuracion", index=False)
        df_detalle.to_excel(writer, sheet_name="detalle_estimaciones", index=False)
        df_metricas_sprint.to_excel(writer, sheet_name="metricas_sprint", index=False)
        df_metricas_globales.to_excel(writer, sheet_name="metricas_globales", index=False)
        df_evolucion.to_excel(writer, sheet_name="evolucion_jugadores", index=False)
        df_aprendizaje.to_excel(writer, sheet_name="eventos_aprendizaje", index=False)

    return ruta_salida
