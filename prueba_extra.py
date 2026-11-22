"""Mini-app para probar SOLO las dos preguntas nuevas con el tema oscuro,
sin tocar proyecto.py.

Ejecutar desde la carpeta del repositorio:
    shiny run --reload --port 8001 prueba_extra.py
"""

import seaborn as sns
from shiny import App, ui

from analisis_extra import paneles_extra, servidor_extra
from tema_planetas import TEMA, estilo_global

planets = sns.load_dataset("planets")

app_ui = ui.page_navbar(
    *paneles_extra(planets),
    title="Prueba de mis preguntas",
    theme=TEMA,
    header=estilo_global(),
)


def server(input, output, session):
    servidor_extra(input, output, session, planets)


app = App(app_ui, server)
