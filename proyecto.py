from shiny import App, ui, render, reactive
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.express as px
from shinywidgets import output_widget, render_widget
from grafico_warren import panel_warren, servidor_warren
planets= sns.load_dataset("planets")
planets = sns.load_dataset("planets")

metodos = sorted(planets["method"].dropna().unique())

anio_min = int(planets["year"].min())
anio_max = int(planets["year"].max())

app_ui = ui.page_navbar(


    ui.nav_panel(
        "Descripción del proyecto",

        ui.h2("Exploración de datos sobre planetas"),

        ui.p(
            "En este proyecto se analiza información "
            "sobre planetas descubiertos fuera de "
            "nuestro sistema solar."
        ),

        ui.h3("Conjunto de datos"),

        ui.p(
            "Se utiliza el conjunto de datos planets "
            "de Seaborn, que contiene información sobre "
            "los métodos de descubrimiento y diferentes "
            "características de los planetas."
        ),

        ui.h3("Objetivo"),

        ui.p(
            "Analizar los métodos de descubrimiento "
            "de planetas y la distribución de sus "
            "períodos orbitales."
        ),

        ui.h3("Preguntas de investigación"),

               ui.tags.ol(
            ui.tags.li(
                "¿Cuál es el método mediante el cual "
                "se han descubierto más planetas?"
            ),
            ui.tags.li(
                "¿Cómo se distribuyen los períodos "
                "orbitales de los planetas?"
            ),
            ui.tags.li(
                "¿Cómo ha evolucionado la cantidad de planetas "
                "descubiertos cada año y qué métodos han aportado "
                "más en cada etapa?"
            ),
            ui.tags.li(
                "¿Son los planetas que detecta Radial Velocity "
                "más livianos y más lejanos con el paso de las décadas?"
            )
        )
    ),



    ui.nav_panel(
        "Análisis interactivo",

        ui.layout_sidebar(

            ui.sidebar(

                ui.h4("Filtros"),

                ui.input_selectize(
                    "metodo",
                    "Método de descubrimiento:",
                    choices=metodos,
                    selected=metodos,
                    multiple=True
                ),

                ui.input_slider(
                    "anios",
                    "Rango de años:",
                    min=anio_min,
                    max=anio_max,
                    value=(anio_min, anio_max)
                )
            ),

            ui.h3("Visualización de datos"),

            ui.navset_tab(

                ui.nav_panel(
                    "Descubrimientos por método",

                    ui.card(
                        output_widget("grafico_metodos")
                    )
                ),

                ui.nav_panel(
                    "Distribución del período orbital",

                    ui.card(
                        output_widget("grafico_histograma")
                    )
                )
            )
        )
    ),
    
    panel_warren,

    title="Análisis de planetas"
)
def server(input, output, session):

    servidor_warren(input, output, session)

    @reactive.calc
    def datos_filtrados():

        datos = planets.copy()

        # Filtrar por método

        metodos_seleccionados = input.metodo()

        if metodos_seleccionados:
            datos = datos[
                datos["method"].isin(metodos_seleccionados)
            ]
        else:
            datos = datos.iloc[0:0]

        # Filtrar por año

        desde, hasta = input.anios()

        datos = datos[
            (datos["year"] >= desde) &
            (datos["year"] <= hasta)
        ]

        return datos

    @render_widget
    def grafico_metodos():

        datos = datos_filtrados().dropna(
            subset=["method"]
        )

        resumen = (
            datos.groupby("method")
            .size()
            .reset_index(name="cantidad")
        )

        fig = px.bar(
            resumen,
            x="method",
            y="cantidad",
            title="Descubrimientos de planetas por método",
            labels={
                "method": "Método de descubrimiento",
                "cantidad": "Cantidad de planetas"
            },
            hover_data=["cantidad"]
        )

        fig.update_layout(
            xaxis_tickangle=-35
        )

        return fig

    @render_widget
    def grafico_histograma():

        datos = datos_filtrados().dropna(
            subset=["orbital_period"]
        )

        fig = px.histogram(
            datos,
            x="orbital_period",
            nbins=30,
            title="Distribución del período orbital",
            labels={
                "orbital_period": "Período orbital (días)",
                "count": "Cantidad de planetas"
            }
        )

        return fig


app = App(app_ui, server)