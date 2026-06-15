"""
Archivo: vista_gui.py
Descripción: Capa de presentación, contiene toda la lógica relacionada con la interfaz gráfica. Construye la ventana principal, muestra los campos de configuración, recoge los valores introducidos por el usuario y presenta un resumen de los resultados obtenidos.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from controlador_gui import ejecutar_desde_interfaz

PERFILES = ["optimista", "realista", "pesimista"]


def crear_ventana_principal():
    ventana = tk.Tk()
    ventana.title("Simulador TFG - Estimación con teoría de juegos")
    ventana.geometry("1050x780")

    variable_numero_jugadores = tk.IntVar(value=3)
    variable_numero_sprints = tk.IntVar(value=10)
    variable_tareas_por_sprint = tk.IntVar(value=5)
    variable_esfuerzo_minimo = tk.IntVar(value=3)
    variable_esfuerzo_maximo = tk.IntVar(value=34)
    variable_ruta_excel = tk.StringVar(value="resultados_simulacion_gui_aprendizaje.xlsx")

    variable_aprendizaje_activo = tk.BooleanVar(value=False)
    variable_frecuencia_aprendizaje = tk.IntVar(value=3)
    variable_umbral_error = tk.DoubleVar(value=2.0)
    variable_decaimiento_sesgo = tk.DoubleVar(value=0.20)

    variables_jugadores = []

    marco_principal = ttk.Frame(ventana, padding=15)
    marco_principal.pack(fill="both", expand=True)

    ttk.Label(
        marco_principal,
        text="Simulador de estimación basado en precisión histórica",
        font=("Arial", 16, "bold")
    ).pack(anchor="w", pady=(0, 15))

    marco_configuracion = ttk.LabelFrame(marco_principal, text="Configuración general", padding=10)
    marco_configuracion.pack(fill="x", pady=(0, 10))

    ttk.Label(marco_configuracion, text="Número de jugadores").grid(row=0, column=0, sticky="w")
    ttk.Spinbox(marco_configuracion, from_=1, to=12, textvariable=variable_numero_jugadores, width=8).grid(row=0, column=1, padx=10)

    ttk.Label(marco_configuracion, text="Número de sprints").grid(row=0, column=2, sticky="w")
    ttk.Spinbox(marco_configuracion, from_=1, to=100, textvariable=variable_numero_sprints, width=8).grid(row=0, column=3, padx=10)

    ttk.Label(marco_configuracion, text="Tareas por sprint").grid(row=0, column=4, sticky="w")
    ttk.Spinbox(marco_configuracion, from_=1, to=100, textvariable=variable_tareas_por_sprint, width=8).grid(row=0, column=5, padx=10)

    ttk.Label(marco_configuracion, text="Esfuerzo mínimo").grid(row=1, column=0, sticky="w", pady=8)
    ttk.Spinbox(marco_configuracion, from_=1, to=89, textvariable=variable_esfuerzo_minimo, width=8).grid(row=1, column=1, padx=10)

    ttk.Label(marco_configuracion, text="Esfuerzo máximo").grid(row=1, column=2, sticky="w", pady=8)
    ttk.Spinbox(marco_configuracion, from_=1, to=89, textvariable=variable_esfuerzo_maximo, width=8).grid(row=1, column=3, padx=10)

    ttk.Label(marco_configuracion, text="Excel salida").grid(row=2, column=0, sticky="w", pady=8)
    ttk.Entry(marco_configuracion, textvariable=variable_ruta_excel, width=60).grid(row=2, column=1, columnspan=4, sticky="we", padx=10)

    def seleccionar_excel():
        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if ruta:
            variable_ruta_excel.set(ruta)

    ttk.Button(marco_configuracion, text="Seleccionar...", command=seleccionar_excel).grid(row=2, column=5)

    marco_aprendizaje = ttk.LabelFrame(marco_principal, text="Aprendizaje adaptativo", padding=10)
    marco_aprendizaje.pack(fill="x", pady=(0, 10))

    ttk.Checkbutton(marco_aprendizaje, text="Activar aprendizaje adaptativo", variable=variable_aprendizaje_activo).grid(row=0, column=0, sticky="w", padx=5)

    ttk.Label(marco_aprendizaje, text="Revisar cada X sprints").grid(row=0, column=1, sticky="w", padx=10)
    ttk.Spinbox(marco_aprendizaje, from_=1, to=50, textvariable=variable_frecuencia_aprendizaje, width=8).grid(row=0, column=2, padx=5)

    ttk.Label(marco_aprendizaje, text="Umbral error histórico").grid(row=0, column=3, sticky="w", padx=10)
    ttk.Entry(marco_aprendizaje, textvariable=variable_umbral_error, width=8).grid(row=0, column=4, padx=5)

    ttk.Label(marco_aprendizaje, text="Decaimiento sesgo").grid(row=0, column=5, sticky="w", padx=10)
    ttk.Entry(marco_aprendizaje, textvariable=variable_decaimiento_sesgo, width=8).grid(row=0, column=6, padx=5)

    ttk.Label(
        marco_aprendizaje,
        text="Ejemplo: 0.20 transforma +30% en +24%, o -30% en -24% cuando se supera el umbral.",
        foreground="gray"
    ).grid(row=1, column=0, columnspan=7, sticky="w", pady=(8, 0))

    marco_jugadores = ttk.LabelFrame(marco_principal, text="Jugadores", padding=10)
    marco_jugadores.pack(fill="both", expand=True, pady=(0, 10))

    canvas = tk.Canvas(marco_jugadores)
    barra_scroll = ttk.Scrollbar(marco_jugadores, orient="vertical", command=canvas.yview)
    marco_jugadores_scroll = ttk.Frame(canvas)

    marco_jugadores_scroll.bind("<Configure>", lambda evento: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=marco_jugadores_scroll, anchor="nw")
    canvas.configure(yscrollcommand=barra_scroll.set)

    canvas.pack(side="left", fill="both", expand=True)
    barra_scroll.pack(side="right", fill="y")

    marco_resultados = ttk.LabelFrame(marco_principal, text="Resumen de resultados", padding=10)
    marco_resultados.pack(fill="x")

    texto_resultados = tk.Text(marco_resultados, height=8)
    texto_resultados.pack(fill="x")

    def actualizar_desviacion_por_perfil(variable_perfil, variable_desviacion):
        perfil = variable_perfil.get()
        if perfil == "optimista":
            variable_desviacion.set(-25)
        elif perfil == "realista":
            variable_desviacion.set(0)
        elif perfil == "pesimista":
            variable_desviacion.set(25)

    def reconstruir_jugadores():
        for widget in marco_jugadores_scroll.winfo_children():
            widget.destroy()

        variables_jugadores.clear()

        encabezados = ["Jugador", "Perfil", "Desviación inicial (%)", "Valor"]
        for columna, texto in enumerate(encabezados):
            ttk.Label(marco_jugadores_scroll, text=texto, font=("Arial", 10, "bold")).grid(row=0, column=columna, padx=8, pady=5, sticky="w")

        for i in range(1, variable_numero_jugadores.get() + 1):
            variable_nombre = tk.StringVar(value=f"J{i}")
            variable_perfil = tk.StringVar(value="realista")
            variable_desviacion = tk.IntVar(value=0)
            variable_texto_desviacion = tk.StringVar(value="0%")

            ttk.Entry(marco_jugadores_scroll, textvariable=variable_nombre, width=12).grid(row=i, column=0, padx=8, pady=5)

            combo = ttk.Combobox(marco_jugadores_scroll, textvariable=variable_perfil, values=PERFILES, state="readonly", width=14)
            combo.grid(row=i, column=1, padx=8, pady=5)

            escala = ttk.Scale(marco_jugadores_scroll, from_=-75, to=75, orient="horizontal", variable=variable_desviacion, length=360)
            escala.grid(row=i, column=2, padx=8, pady=5)

            ttk.Label(marco_jugadores_scroll, textvariable=variable_texto_desviacion, width=8).grid(row=i, column=3, padx=8, pady=5)

            def actualizar_texto(var_desv=variable_desviacion, var_texto=variable_texto_desviacion):
                var_texto.set(f"{int(float(var_desv.get()))}%")

            def al_mover_escala(valor, funcion=actualizar_texto):
                funcion()

            escala.configure(command=al_mover_escala)

            def al_cambiar_perfil(evento, var_perfil=variable_perfil, var_desv=variable_desviacion, funcion=actualizar_texto):
                actualizar_desviacion_por_perfil(var_perfil, var_desv)
                funcion()

            combo.bind("<<ComboboxSelected>>", al_cambiar_perfil)

            variables_jugadores.append({
                "nombre": variable_nombre,
                "perfil": variable_perfil,
                "desviacion": variable_desviacion
            })

    def construir_configuracion():
        jugadores = []
        for jugador in variables_jugadores:
            jugadores.append({
                "nombre": jugador["nombre"].get(),
                "perfil": jugador["perfil"].get(),
                "desviacion": jugador["desviacion"].get() / 100
            })

        return {
            "jugadores": jugadores,
            "numero_sprints": int(variable_numero_sprints.get()),
            "tareas_por_sprint": int(variable_tareas_por_sprint.get()),
            "esfuerzo_minimo": int(variable_esfuerzo_minimo.get()),
            "esfuerzo_maximo": int(variable_esfuerzo_maximo.get()),
            "ruta_excel": variable_ruta_excel.get(),
            "aprendizaje_activo": bool(variable_aprendizaje_activo.get()),
            "frecuencia_aprendizaje": int(variable_frecuencia_aprendizaje.get()),
            "umbral_error_aprendizaje": float(variable_umbral_error.get()),
            "decaimiento_sesgo": float(variable_decaimiento_sesgo.get())
        }

    def ejecutar_simulacion_gui():
        try:
            configuracion = construir_configuracion()
            resultados = ejecutar_desde_interfaz(configuracion)
            metricas = resultados["metricas_globales"]

            texto_resultados.delete("1.0", tk.END)
            texto_resultados.insert(tk.END, "Simulación completada correctamente.\n\n")
            texto_resultados.insert(tk.END, f"MAE tradicional: {metricas['mae_tradicional_global']}\n")
            texto_resultados.insert(tk.END, f"MAE ajustado:    {metricas['mae_ajustado_global']}\n")
            texto_resultados.insert(tk.END, f"Sesgo tradicional: {metricas['sesgo_medio_tradicional_global']}\n")
            texto_resultados.insert(tk.END, f"Sesgo ajustado:    {metricas['sesgo_medio_ajustado_global']}\n")
            texto_resultados.insert(tk.END, f"Varianza tradicional: {metricas['varianza_error_tradicional_global']}\n")
            texto_resultados.insert(tk.END, f"Varianza ajustada:    {metricas['varianza_error_ajustado_global']}\n")
            texto_resultados.insert(tk.END, f"\nEventos de aprendizaje: {len(resultados['eventos_aprendizaje'])}\n")
            texto_resultados.insert(tk.END, f"Excel generado en: {configuracion['ruta_excel']}\n")

            messagebox.showinfo("Simulación completada", "La simulación se ha ejecutado correctamente.")

        except Exception as error:
            messagebox.showerror("Error", str(error))

    ttk.Button(marco_configuracion, text="Actualizar jugadores", command=reconstruir_jugadores).grid(row=0, column=6, padx=10)
    ttk.Button(marco_configuracion, text="Ejecutar simulación", command=ejecutar_simulacion_gui).grid(row=1, column=6, padx=10)

    reconstruir_jugadores()
    return ventana


def iniciar_interfaz():
    ventana = crear_ventana_principal()
    ventana.mainloop()
