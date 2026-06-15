# Simulador TFG - GUI con aprendizaje adaptativo

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main_gui.py
```

## Funcionamiento del aprendizaje

Si se activa el aprendizaje adaptativo, al final de cada bloque de X sprints:

- se revisa la precisión histórica de cada jugador;
- si el jugador es optimista o pesimista;
- y su error histórico supera el umbral;
- su desviación se reduce hacia 0 usando el decaimiento.

Ejemplo:

- +30% con decaimiento 0.20 pasa a +24%.
- -30% con decaimiento 0.20 pasa a -24%.

La estimación visible sigue siendo discreta, ya que se redondea a la tarjeta Fibonacci más cercana.
