from shiny import App, ui, render, reactive
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.express as px
from shinywidgets import output_widget, render_widget
from grafico_warren import panel_warren, servidor_warren
from analisis_extra import paneles_extra, servidor_extra
from tema_planetas import TEMA, estilo_global, estilo_plotly
planets = sns.load_dataset("planets")

metodos = sorted(planets["method"].dropna().unique())

# ---------- Datos y ayudas para la pestaña de descripción ----------
n_planetas = len(planets)
n_metodos = int(planets["method"].nunique())
anio_min = int(planets["year"].min())
anio_max = int(planets["year"].max())
n_variables = int(planets.shape[1])


def pct_con_datos(columna):
    """Porcentaje de planetas que tienen dato en esa columna, como texto."""
    return f"{planets[columna].notna().mean():.0%}"


# (variable, qué significa, tipo)
variables_descripcion = [
    ("method", "Método utilizado para descubrir el planeta", "Cualitativa nominal"),
    (
        "number",
        "Cantidad de planetas descubiertos alrededor de una estrella",
        "Cuantitativa discreta",
    ),
    (
        "orbital_period",
        "Tiempo que tarda el planeta en completar una órbita alrededor de su "
        "estrella (días)",
        "Cuantitativa continua",
    ),
    (
        "mass",
        "Masa del planeta, expresada en relación con la masa de Júpiter",
        "Cuantitativa continua",
    ),
    (
        "distance",
        "Distancia entre el sistema planetario y la Tierra (pársecs)",
        "Cuantitativa continua",
    ),
    ("year", "Año en que fue descubierto el planeta", "Cuantitativa discreta"),
]

pasos_app = [
    "Navega por las pestañas de la barra superior: cada una responde una de "
    "las preguntas de investigación.",
    "Usa los filtros de la barra lateral (métodos, escala, etc.) para cambiar "
    "lo que muestran los gráficos.",
    "Pasa el mouse sobre los puntos y las barras para ver los valores exactos.",
    "En «Período y distancia por método», la subpestaña «Período vs distancia, según el año» tiene "
    "un botón de play que recorre los descubrimientos año por año.",
    "Los gráficos se pueden ampliar, mover y descargar como imagen con los "
    "íconos de la esquina superior derecha.",
]

# Cada pregunta indica en qué pestaña se responde.
# Si cambian los nombres de las pestañas, se actualizan aquí.
preguntas = [
    {
        "texto": "¿Cuál es el método mediante el cual se han descubierto más planetas?",
        "pestana": "Análisis interactivo › Descubrimientos por método",
    },
    {
        "texto": (
            "¿Cómo ha evolucionado la cantidad de planetas descubiertos cada año "
            "y qué métodos han aportado más en cada etapa?"
        ),
        "pestana": "Evolución de los descubrimientos › Línea de tiempo",
    },
    {
        "texto": (
            "¿Son los planetas que detecta Radial Velocity más livianos "
            "y más lejanos con el paso de las décadas?"
        ),
        "pestana": "Evolución de los descubrimientos › Masa y distancia por década",
    },
    {
        "texto": (
            "¿Cada método de descubrimiento detecta planetas en una "
            "zona distinta de período orbital y distancia?"
        ),
        "pestana": "Período y distancia por método",
    },
]


def tarjeta_stat(valor, etiqueta):
    return ui.div(
        ui.div(valor, class_="desc-stat-valor"),
        ui.div(etiqueta, class_="desc-stat-etiqueta"),
        class_="desc-stat",
    )


def tarjeta_pregunta(numero, pregunta):
    return ui.div(
        ui.div(f"PREGUNTA {numero}", class_="pregunta-titulo"),
        pregunta["texto"],
        ui.div(
            "Se responde en: ",
            ui.tags.span(pregunta["pestana"], class_="desc-etiqueta"),
            class_="desc-donde",
        ),
        class_="pregunta",
    )


def tabla_variables():
    filas = [
        ui.tags.tr(
            ui.tags.td(ui.tags.code(variable)),
            ui.tags.td(significado),
            ui.tags.td(tipo),
            ui.tags.td(pct_con_datos(variable)),
        )
        for variable, significado, tipo in variables_descripcion
    ]
    return ui.div(
        ui.tags.table(
            ui.tags.thead(
                ui.tags.tr(
                    ui.tags.th("Variable"),
                    ui.tags.th("Qué significa"),
                    ui.tags.th("Tipo"),
                    ui.tags.th("Con datos"),
                )
            ),
            ui.tags.tbody(*filas),
            class_="table table-sm desc-tabla",
        ),
        style="overflow-x: auto;",
    )


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

            .desc-grid .pregunta {
                margin: 0;
                height: 100%;
            }

            .desc-donde {
                margin-top: 12px;
                font-size: 14px;
            }

            .desc-etiqueta {
                display: inline-block;
                padding: 2px 10px;
                border-radius: 999px;
                background-color: rgba(70, 130, 180, 0.25);
            }

            .desc-stat {
                text-align: center;
                padding: 16px 8px;
                border: 1px solid rgba(70, 130, 180, 0.25);
                border-radius: 12px;
                background-color: rgba(70, 130, 180, 0.10);
            }

            .desc-stat-valor {
                font-size: 32px;
                font-weight: bold;
                line-height: 1.1;
                color: #4682B4;
            }

            .desc-stat-etiqueta {
                margin-top: 4px;
                font-size: 13px;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                opacity: 0.8;
            }

            .desc-tabla thead th {
                background-color: rgba(70, 130, 180, 0.25);
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

            ui.layout_columns(
                tarjeta_stat(str(n_planetas), "planetas"),
                tarjeta_stat(str(n_metodos), "métodos de descubrimiento"),
                tarjeta_stat(f"{anio_min}–{anio_max}", "años de descubrimiento"),
                tarjeta_stat(str(n_variables), "variables"),
                col_widths=(3, 3, 3, 3),
            ),

            ui.h3("Conjunto de datos", class_="seccion"),

            ui.layout_columns(
                ui.card(
                    ui.card_header("Sobre los datos"),
                    ui.p(
                        "Se utiliza el conjunto de datos ",
                        ui.tags.em("planets"),
                        " de Seaborn, que contiene información sobre los "
                        "métodos de descubrimiento y diferentes "
                        "características de los planetas. Cada fila es un planeta."
                    ),
                    ui.p(
                        "No todos los planetas tienen todos los datos: tiene masa "
                        f"el {pct_con_datos('mass')}, distancia el "
                        f"{pct_con_datos('distance')} y período orbital el "
                        f"{pct_con_datos('orbital_period')}. Por eso algunos "
                        "gráficos usan menos planetas que el total."
                    ),
                ),
                ui.card(
                    ui.card_header("Cómo usar la app"),
                    ui.tags.ol(*[ui.tags.li(paso) for paso in pasos_app]),
                ),
                col_widths=(7, 5),
            ),

            ui.h4("Tabla de datos", class_="seccion"),

            ui.card(
                ui.output_data_frame("tabla_planetas")
            ),

            ui.h3("Descripción de las variables", class_="seccion"),

            ui.card(
                tabla_variables()
            ),

            ui.h3("Objetivo", class_="seccion"),

            ui.p(
               "Analizar cómo los distintos métodos de descubrimiento de exoplanetas han contribuido a lo largo del tiempo "
                "y qué tipo de planetas detecta cada uno, según su período orbital, distancia y masa.",
                class_="descripcion"
            ),

            ui.h3("Preguntas de investigación", class_="seccion"),

            ui.layout_columns(
                *[
                    tarjeta_pregunta(i, pregunta)
                    for i, pregunta in enumerate(preguntas, start=1)
                ],
                col_widths=(6, 6),
                class_="desc-grid",
            ),

            class_="contenido-descripcion"
        )
    ),



ui.nav_panel(
    "Análisis interactivo",

    ui.h4("¿Cuál es el método mediante el cual se han descubierto más planetas?"),

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