from shiny import App, ui, render, reactive
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.express as px
from shinywidgets import output_widget, render_widget
from grafico_warren import panel_warren, servidor_warren
from analisis_extra import paneles_extra, servidor_extra
from tema_planetas import TEMA, estilo_global, estilo_plotly
planets= sns.load_dataset("planets")
planets = sns.load_dataset("planets")

metodos = sorted(planets["method"].dropna().unique())


app_ui = ui.page_navbar(



    

ui.nav_panel(
    "Descripción del proyecto",

    ui.tags.style("""
        .descripcion {
            font-size: 18px;
            line-height: 1.8;
            text-align: justify;
        }

        .seccion {
            margin-top: 30px;
            margin-bottom: 14px;
        }

        .pregunta {
            background-color: rgba(70, 130, 180, 0.10);
            border: 1px solid rgba(70, 130, 180, 0.25);
            border-left: 5px solid #4682B4;
            padding: 20px 22px;
            margin: 14px 0;
            border-radius: 10px;
            font-size: 17px;
            line-height: 1.7;
        }

        .pregunta-titulo {
            font-size: 16px;
            font-weight: bold;
            color: #4682B4;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }

        .contenido-descripcion {
            max-width: 1100px;
            margin: auto;
            padding: 15px 20px;
        }
    """),

    ui.div(
        ui.h2("Exploración de datos sobre planetas"),

        ui.p(
            "En este proyecto se analiza información "
            "sobre planetas descubiertos fuera de "
            "nuestro sistema solar.",
            class_="descripcion"
        ),

        ui.h3("Conjunto de datos", class_="seccion"),

        ui.p(
            "Se utiliza el conjunto de datos planets "
            "de Seaborn, que contiene información sobre "
            "los métodos de descubrimiento y diferentes "
            "características de los planetas.",
            class_="descripcion"
        ),

        ui.h4("Tabla de datos", class_="seccion"),

        ui.card(
            ui.output_data_frame("tabla_planetas")
        ),

        ui.h3("Descripción de las variables", class_="seccion"),

        ui.p(
            "El conjunto de datos planets contiene las variables vistas anteriormente. "
            "Podemos observar que method es el método utilizado para descubrir el planeta. "
            "Esta es una variable cualitativa nominal. "
            "Number es la cantidad de planetas descubiertos alrededor de una estrella. "
            "Esta es una variable cuantitativa discreta. "
            "Orbital_period es el tiempo que tarda un planeta en completar una órbita "
            "alrededor de su estrella, medido en días. Esta es una variable cuantitativa continua. "
            "La variable mass representa la masa del planeta, expresada en relación con "
            "la masa de Júpiter. Esta es una variable cuantitativa continua. "
            "La variable distance representa la distancia entre el sistema planetario y "
            "la Tierra, expresada en pársecs. Esta es una variable cuantitativa continua. "
            "Por último, la variable year corresponde al año en que fue descubierto el planeta. "
            "Esta es una variable cuantitativa discreta.",
            class_="descripcion"
        ),

        ui.h3("Objetivo", class_="seccion"),

        ui.p(
            "Analizar los métodos de descubrimiento "
            "de planetas y la distribución de sus "
            "períodos orbitales.",
            class_="descripcion"
        ),

        ui.h3("Preguntas de investigación", class_="seccion"),

        ui.div(
            ui.div("PREGUNTA 1", class_="pregunta-titulo"),
            "¿Cuál es el método mediante el cual se han descubierto más planetas?",
            class_="pregunta"
        ),

        ui.div(
            ui.div("PREGUNTA 2", class_="pregunta-titulo"),
            "¿Cómo ha evolucionado la cantidad de planetas descubiertos cada año "
            "y qué métodos han aportado más en cada etapa?",
            class_="pregunta"
        ),

        ui.div(
            ui.div("PREGUNTA 3", class_="pregunta-titulo"),
            "¿Son los planetas que detecta Radial Velocity más livianos "
            "y más lejanos con el paso de las décadas?",
            class_="pregunta"
        ),

        ui.div(
            ui.div("PREGUNTA 4", class_="pregunta-titulo"),
            "¿Cada método de descubrimiento detecta planetas en una "
            "zona distinta de período orbital y distancia?",
            class_="pregunta"
        ),

        class_="contenido-descripcion"
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
    *paneles_extra(planets),

    title="Análisis de planetas",
    theme=TEMA,
    header=estilo_global(),
)
def server(input, output, session):

    servidor_warren(input, output, session)
    servidor_extra(input, output, session, planets)

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
            color_discrete_sequence=["#FFD700", "#4682B4", "#66A182", "#DB7093", "#E69F52","#8B4513", "#DC143C","#6A0DAD", "#FFA500","#9370DB"],
            template="plotly_dark",
        )

        fig.update_layout(
            xaxis_tickangle=-35
        )

        return estilo_plotly(fig)


app = App(app_ui, server)