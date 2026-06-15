"""
Archivo: modelo.py
Descripción: Contiene la parte principal del simulador donde se implementa toda la lógica matemática y experimental del sistema.
"""

import random
import statistics

ESCALA_FIBONACCI = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]


def obtener_valor_fibonacci_mas_cercano(valor):
    """Devuelve el valor Fibonacci más cercano."""
    return min(ESCALA_FIBONACCI, key=lambda x: abs(x - valor))


def generar_esfuerzo_real(minimo=3, maximo=34):
    """Genera un esfuerzo real dentro de la escala Fibonacci."""
    posibles = [v for v in ESCALA_FIBONACCI if minimo <= v <= maximo]
    return random.choice(posibles)


def calcular_estimacion_jugador(esfuerzo_real, desviacion):
    """
    Calcula una estimación individual.
    Primero se calcula una estimación continua:
        esfuerzo_real * (1 + desviacion)
    Después se transforma en un valor de Fibonacci.
    """
    estimacion_continua = esfuerzo_real * (1 + desviacion)

    # Ruido pequeño para simular incertidumbre.
    ruido = random.uniform(-0.10, 0.10) * esfuerzo_real
    estimacion_continua += ruido

    estimacion_fibonacci = obtener_valor_fibonacci_mas_cercano(estimacion_continua)
    return estimacion_fibonacci, estimacion_continua


def calcular_error_individual(estimacion, esfuerzo_real):
    """Calcula C_i = |E_i - R|."""
    return abs(estimacion - esfuerzo_real)


def calcular_estimacion_tradicional(estimaciones):
    """Calcula la media simple."""
    if not estimaciones:
        return 0
    return sum(estimaciones) / len(estimaciones)


def calcular_peso(precision_historica):
    """Calcula w_i = 1 / (1 + P_i)."""
    return 1 / (1 + precision_historica)


def calcular_estimacion_ajustada(estimaciones, pesos):
    """Calcula la media ponderada por precisión histórica."""
    suma_pesos = sum(pesos)
    if suma_pesos == 0:
        return calcular_estimacion_tradicional(estimaciones)
    return sum(e * w for e, w in zip(estimaciones, pesos)) / suma_pesos


def calcular_error_global(estimacion_final, esfuerzo_real):
    """Calcula C_global = |E - R|."""
    return abs(estimacion_final - esfuerzo_real)


def calcular_sesgo(estimacion_final, esfuerzo_real):
    """Calcula el sesgo: positivo sobreestima, negativo infraestima."""
    return estimacion_final - esfuerzo_real


def actualizar_precision_historica(errores_historicos):
    """Calcula P_i como media de errores históricos."""
    if not errores_historicos:
        return 0.0
    return sum(errores_historicos) / len(errores_historicos)


def crear_jugadores(jugadores_configurados):
    """Crea jugadores a partir de la configuración de la aplicación."""
    jugadores = []
    for indice, jugador in enumerate(jugadores_configurados, start=1):
        jugadores.append({
            "id_jugador": indice,
            "nombre": jugador["nombre"],
            "perfil": jugador["perfil"],
            "desviacion_inicial": jugador["desviacion"],
            "desviacion_actual": jugador["desviacion"],
            "errores_historicos": []
        })
    return jugadores


def debe_aplicar_aprendizaje(configuracion, sprint):
    """Comprueba si hay que revisar el aprendizaje al final del sprint."""
    if not configuracion.get("aprendizaje_activo", False):
        return False
    frecuencia = configuracion.get("frecuencia_aprendizaje", 1)
    if frecuencia <= 0:
        return False
    return sprint % frecuencia == 0


def adaptar_desviacion_jugador(jugador, configuracion):
    """
    Aplica aprendizaje adaptativo.
    Si P_i supera el umbral, la desviación se reduce hacia 0:
        desviacion_nueva = desviacion_actual * (1 - decaimiento)
    """
    precision = actualizar_precision_historica(jugador["errores_historicos"])
    desviacion_anterior = jugador["desviacion_actual"]

    if jugador["perfil"] not in ["optimista", "pesimista"]:
        return {
            "aplicado": False,
            "motivo": "perfil_realista",
            "precision_historica": precision,
            "desviacion_anterior": desviacion_anterior,
            "desviacion_nueva": desviacion_anterior
        }

    umbral = configuracion.get("umbral_error_aprendizaje", 2.0)
    decaimiento = configuracion.get("decaimiento_sesgo", 0.20)

    if precision > umbral:
        jugador["desviacion_actual"] = jugador["desviacion_actual"] * (1 - decaimiento)
        aplicado = True
        motivo = "precision_supera_umbral"
    else:
        aplicado = False
        motivo = "precision_no_supera_umbral"

    return {
        "aplicado": aplicado,
        "motivo": motivo,
        "precision_historica": precision,
        "desviacion_anterior": desviacion_anterior,
        "desviacion_nueva": jugador["desviacion_actual"]
    }


def ejecutar_simulacion(configuracion):
    """Ejecuta la simulación completa."""
    jugadores = crear_jugadores(configuracion["jugadores"])

    detalle_estimaciones = []
    metricas_sprint = []
    evolucion_jugadores = []
    eventos_aprendizaje = []

    errores_tradicionales_globales = []
    errores_ajustados_globales = []
    sesgos_tradicionales = []
    sesgos_ajustados = []

    for sprint in range(1, configuracion["numero_sprints"] + 1):
        errores_tradicionales_sprint = []
        errores_ajustados_sprint = []
        sesgos_tradicionales_sprint = []
        sesgos_ajustados_sprint = []

        for tarea in range(1, configuracion["tareas_por_sprint"] + 1):
            esfuerzo_real = generar_esfuerzo_real(
                configuracion["esfuerzo_minimo"],
                configuracion["esfuerzo_maximo"]
            )

            estimaciones = []
            estimaciones_continuas = []
            pesos = []
            errores_individuales = []
            precisiones_antes = []
            desviaciones_usadas = []

            for jugador in jugadores:
                precision_antes = actualizar_precision_historica(jugador["errores_historicos"])
                peso = calcular_peso(precision_antes)

                estimacion, estimacion_continua = calcular_estimacion_jugador(
                    esfuerzo_real,
                    jugador["desviacion_actual"]
                )

                error_individual = calcular_error_individual(estimacion, esfuerzo_real)

                estimaciones.append(estimacion)
                estimaciones_continuas.append(estimacion_continua)
                pesos.append(peso)
                errores_individuales.append(error_individual)
                precisiones_antes.append(precision_antes)
                desviaciones_usadas.append(jugador["desviacion_actual"])

            estimacion_tradicional = calcular_estimacion_tradicional(estimaciones)
            error_tradicional = calcular_error_global(estimacion_tradicional, esfuerzo_real)
            sesgo_tradicional = calcular_sesgo(estimacion_tradicional, esfuerzo_real)

            estimacion_ajustada = calcular_estimacion_ajustada(estimaciones, pesos)
            error_ajustado = calcular_error_global(estimacion_ajustada, esfuerzo_real)
            sesgo_ajustado = calcular_sesgo(estimacion_ajustada, esfuerzo_real)

            errores_tradicionales_sprint.append(error_tradicional)
            errores_ajustados_sprint.append(error_ajustado)
            sesgos_tradicionales_sprint.append(sesgo_tradicional)
            sesgos_ajustados_sprint.append(sesgo_ajustado)

            errores_tradicionales_globales.append(error_tradicional)
            errores_ajustados_globales.append(error_ajustado)
            sesgos_tradicionales.append(sesgo_tradicional)
            sesgos_ajustados.append(sesgo_ajustado)

            for indice, jugador in enumerate(jugadores):
                jugador["errores_historicos"].append(errores_individuales[indice])
                precision_despues = actualizar_precision_historica(jugador["errores_historicos"])

                detalle_estimaciones.append({
                    "sprint": sprint,
                    "tarea": tarea,
                    "id_jugador": jugador["id_jugador"],
                    "nombre": jugador["nombre"],
                    "perfil": jugador["perfil"],
                    "desviacion_usada": round(desviaciones_usadas[indice], 4),
                    "estimacion_continua": round(estimaciones_continuas[indice], 4),
                    "esfuerzo_real": esfuerzo_real,
                    "estimacion_individual_fibonacci": estimaciones[indice],
                    "error_individual": errores_individuales[indice],
                    "precision_historica_antes": round(precisiones_antes[indice], 4),
                    "peso_usado": round(pesos[indice], 4),
                    "precision_historica_despues": round(precision_despues, 4),
                    "estimacion_tradicional": round(estimacion_tradicional, 4),
                    "error_tradicional": round(error_tradicional, 4),
                    "sesgo_tradicional": round(sesgo_tradicional, 4),
                    "estimacion_ajustada": round(estimacion_ajustada, 4),
                    "error_ajustado": round(error_ajustado, 4),
                    "sesgo_ajustado": round(sesgo_ajustado, 4)
                })

                evolucion_jugadores.append({
                    "sprint": sprint,
                    "tarea": tarea,
                    "id_jugador": jugador["id_jugador"],
                    "nombre": jugador["nombre"],
                    "perfil": jugador["perfil"],
                    "desviacion_actual": round(jugador["desviacion_actual"], 4),
                    "precision_historica": round(precision_despues, 4),
                    "peso_siguiente": round(calcular_peso(precision_despues), 4)
                })

        metricas_sprint.append({
            "sprint": sprint,
            "mae_tradicional": round(sum(errores_tradicionales_sprint) / len(errores_tradicionales_sprint), 4),
            "mae_ajustado": round(sum(errores_ajustados_sprint) / len(errores_ajustados_sprint), 4),
            "sesgo_medio_tradicional": round(sum(sesgos_tradicionales_sprint) / len(sesgos_tradicionales_sprint), 4),
            "sesgo_medio_ajustado": round(sum(sesgos_ajustados_sprint) / len(sesgos_ajustados_sprint), 4),
            "varianza_error_tradicional": round(statistics.pvariance(errores_tradicionales_sprint), 4),
            "varianza_error_ajustado": round(statistics.pvariance(errores_ajustados_sprint), 4)
        })

        if debe_aplicar_aprendizaje(configuracion, sprint):
            for jugador in jugadores:
                evento = adaptar_desviacion_jugador(jugador, configuracion)
                eventos_aprendizaje.append({
                    "sprint": sprint,
                    "id_jugador": jugador["id_jugador"],
                    "nombre": jugador["nombre"],
                    "perfil": jugador["perfil"],
                    "aplicado": evento["aplicado"],
                    "motivo": evento["motivo"],
                    "precision_historica": round(evento["precision_historica"], 4),
                    "desviacion_anterior": round(evento["desviacion_anterior"], 4),
                    "desviacion_nueva": round(evento["desviacion_nueva"], 4)
                })

    metricas_globales = {
        "mae_tradicional_global": round(sum(errores_tradicionales_globales) / len(errores_tradicionales_globales), 4),
        "mae_ajustado_global": round(sum(errores_ajustados_globales) / len(errores_ajustados_globales), 4),
        "sesgo_medio_tradicional_global": round(sum(sesgos_tradicionales) / len(sesgos_tradicionales), 4),
        "sesgo_medio_ajustado_global": round(sum(sesgos_ajustados) / len(sesgos_ajustados), 4),
        "varianza_error_tradicional_global": round(statistics.pvariance(errores_tradicionales_globales), 4),
        "varianza_error_ajustado_global": round(statistics.pvariance(errores_ajustados_globales), 4)
    }

    return {
        "configuracion": configuracion,
        "detalle_estimaciones": detalle_estimaciones,
        "metricas_sprint": metricas_sprint,
        "metricas_globales": metricas_globales,
        "evolucion_jugadores": evolucion_jugadores,
        "eventos_aprendizaje": eventos_aprendizaje
    }
