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
        ui.h4("Tabla de datos"),
        ui.card(
            ui.output_data_frame("tabla_planetas")
        ),

        ui.h3("Descripción de las variables"),
        ui.p(
            "El conjunto de datos planets contiene las variables vistas anteriormente."
            
            " Podemos observar que method es el método utilizado para descubrir el planeta."
            " Esta es una varoble cualitativa nominal."
            
            " Number es la cantidad de planetas descubiertos alrededor de una estrella."
            " Esta es una variable cuantitativa	discreta."
            
            " Orbital_period es el tiempo que tarda un planeta en completar una órbita alrededor de su estrella, medido en días."
            "Esta es una variable cuantitativa	continua"

            " La variable mass Masa del planeta, expresada en relación con la masa de Júpiter."
            " Esta es una variable cuantitativa	continua"

            " La variable distance Distancia entre el sistema planetario y la Tierra, expresada en pársecs."	
            " Esta es cuantitativa	continua"

            "Por ultimo la variable year que es el año en que fue descubierto el planeta."
            " Esta es cuantitativa	discreta."
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
                "¿ACA EL DE JAIR "
                "ACA IRIA EL DE JAIR?"
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
                )
            ),

            ui.h3("Visualización de datos"),

            ui.navset_tab(

                ui.nav_panel(
                    "Descubrimientos por método",

                    ui.card(
                        output_widget("grafico_metodos")
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

    @render.data_frame
    def tabla_planetas():
        return render.DataGrid(planets.head(10))
    
        
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
            hover_data=["cantidad"],
            color="method",
            color_discrete_sequence=["#FFD700", "#4682B4", "#66A182", "#DB7093", "#E69F52","#8B4513", "#DC143C","#6A0DAD", "#FFA500","#9370DB"]
        )

        fig.update_layout(
            xaxis_tickangle=-35
        )

        return fig


app = App(app_ui, server)