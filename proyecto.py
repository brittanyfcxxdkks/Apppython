from shiny import App, ui, render
import matplotlib.pyplot as plt
import numpy as np

app_ui = ui.page_fluid(
    ui.h2("Análisis de datos"),
    ui.h3("Prueba"),
    ui.output_plot("grafico1")
)

def server(input, output, session):
    @output
    @render.plot
    def grafico1():
        x = np.linspace(0, 2 * np.pi, 200)
        y = np.sin(x)
        y1 = np.cos(x)
        
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.plot(x, y1)
        
        return fig

app = App(app_ui, server)