# Simulaciones Interactivas

Este repositorio contiene un conjunto de simulaciones interactivas implementadas en Python, incluyendo el Juego de la Vida (1D y 2D), una simulación de propagación de COVID-19 en una grilla, y un generador de distribuciones aleatorias. Las simulaciones se presentan con interfaces gráficas basadas en Tkinter y visualizaciones generadas con Matplotlib.

## Descripción

- **Juego de la Vida (1D y 2D)**: Implementación de los autómatas celulares de Conway y sus variantes 1D basadas en reglas de Wolfram (e.g., reglas 30, 110).
- **Simulación de COVID-19**: Modelo basado en grillas que simula la propagación de una enfermedad con estados (susceptible, infectado, recuperado, muerto).
- **Generador de Distribuciones**: Herramienta para generar y visualizar distribuciones aleatorias (uniforme, exponencial, gamma, etc.).
- **Menú Principal**: Interfaz que permite lanzar las diferentes simulaciones de manera independiente.

## Requisitos

- Python 3.7 o superior
- Bibliotecas:
  - `numpy`
  - `matplotlib`
  - `tkinter` (normalmente incluida con Python)

Instala las dependencias usando pip:

```bash
pip install numpy matplotlib
