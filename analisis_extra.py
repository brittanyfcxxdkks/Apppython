"""Pregunta de investigación adicional para la app de planetas:
¿cada método de descubrimiento detecta planetas en una zona distinta de
período orbital y distancia a la Tierra?

Uso en proyecto.py:
    from analisis_extra import paneles_extra, servidor_extra
    ...  *paneles_extra(planets),          (dentro de ui.page_navbar)
    ...  servidor_extra(input, output, session, planets)   (dentro de server)
"""

import numpy as np
import pandas as pd
import plotly.express as px
from shiny import ui, render, reactive
from shinywidgets import output_widget, render_widget

FONDO = "#0b1020"


# ----------------------------------------------------------------------
# Estilo y figuras (funciones que reciben datos y devuelven la figura)
# ----------------------------------------------------------------------
def _estilo(fig):
    """Mismo aspecto oscuro para todos los gráficos de este módulo."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=FONDO,
        plot_bgcolor=FONDO,
        margin=dict(t=60, l=60, r=20, b=60),
    )
    return fig


def _fig_vacia(texto="No hay datos con los filtros elegidos"):
    fig = px.scatter()
    fig.add_annotation(
        text=texto,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _estilo(fig)


def _mapa_colores(planets):
    """Un color fijo por método, igual en el mapa normal y en el animado."""
    paleta = px.colors.qualitative.Plotly
    metodos = sorted(planets["method"].dropna().unique())
    return {m: paleta[i % len(paleta)] for i, m in enumerate(metodos)}


def _plural(n):
    return f"{n} planeta" if n == 1 else f"{n} planetas"


def _filtrar_anio(d, anio, modo):
    """modo 'solo': descubiertos ese año. Otro valor: acumulado hasta ese año."""
    if modo == "solo":
        return d[d["year"] == anio]
    return d[d["year"] <= anio]


def _fig_anio(d, anio, modo, log, colores):
    """Mapa período vs distancia para un año (o hasta un año), con ejes fijos."""
    d = d.dropna(subset=["year"])
    if d.empty:
        return _fig_vacia()

    cuando = f"en {anio}" if modo == "solo" else f"hasta {anio}"
    elegidos = _filtrar_anio(d, anio, modo)
    if elegidos.empty:
        return _fig_vacia(f"Sin planetas con período y distancia conocidos {cuando}")

    fig = px.scatter(
        elegidos,
        x="orbital_period",
        y="distance",
        color="method",
        color_discrete_map=colores,
        log_x=log,
        log_y=log,
        opacity=0.75,
        hover_data=["year"],
        title=f"Planetas descubiertos {cuando}: {_plural(len(elegidos))}",
        labels={
            "orbital_period": "Período orbital (días)",
            "distance": "Distancia a la Tierra (pc)",
            "method": "Método",
            "year": "Año de descubrimiento",
        },
    )

    # Ejes fijos (calculados con todos los años) para que el mapa no "salte"
    for eje, col in (("x", "orbital_period"), ("y", "distance")):
        if log:
            positivos = d.loc[d[col] > 0, col]
            rango = [np.log10(positivos.min()) - 0.2, np.log10(positivos.max()) + 0.2]
        else:
            rango = [0, d[col].max() * 1.05]
        if eje == "x":
            fig.update_xaxes(range=rango)
        else:
            fig.update_yaxes(range=rango)

    return _estilo(fig)


def _tabla_anio(d, anio, modo):
    """Cuántos planetas hay por método en el año elegido."""
    columnas = ["Método", "Descubiertos", "Con período y distancia (en el mapa)"]
    d = d.dropna(subset=["method", "year"])
    d = _filtrar_anio(d, anio, modo)
    if d.empty:
        return pd.DataFrame(columns=columnas)

    d = d.assign(en_mapa=d["orbital_period"].notna() & d["distance"].notna())
    tabla = (
        d.groupby("method")
        .agg(total=("en_mapa", "size"), mapa=("en_mapa", "sum"))
        .reset_index()
        .sort_values("total", ascending=False)
    )
    total = pd.DataFrame(
        {
            "method": ["Total"],
            "total": [tabla["total"].sum()],
            "mapa": [tabla["mapa"].sum()],
        }
    )
    tabla = pd.concat([tabla, total], ignore_index=True)
    tabla.columns = columnas
    return tabla


# ----------------------------------------------------------------------
# Interfaz
# ----------------------------------------------------------------------
def paneles_extra(planets):
    metodos = sorted(planets["method"].dropna().unique())
    anio_min = int(planets["year"].min())
    anio_max = int(planets["year"].max())

    panel = ui.nav_panel(
        "Período y distancia por método",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h4("Filtros"),
                ui.input_selectize(
                    "ex_metodos_p5",
                    "Método de descubrimiento:",
                    choices=metodos,
                    selected=metodos,
                    multiple=True,
                ),
                ui.input_switch(
                    "ex_log_p5",
                    "Escala logarítmica",
                    value=True,
                ),
            ),
            ui.p(
                "¿Cada método de descubrimiento detecta planetas en una "
                "zona distinta de período orbital y distancia a la Tierra?"
            ),
            ui.navset_tab(
                ui.nav_panel(
                    "Mapa de detección",
                    ui.card(output_widget("ex_grafico_mapa")),
                ),
                ui.nav_panel(
                    "Mapa por año",
                    ui.p(
                        "Elige qué ver con la barra de años, o escribe un año "
                        "específico. El botón de play, debajo de la barra, "
                        "avanza año por año. El mapa solo dibuja los planetas "
                        "con período y distancia conocidos, así que algunos "
                        "métodos aparecen más tarde que en el conteo total "
                        "(mira la tabla).",
                        class_="text-muted",
                    ),
                    ui.layout_columns(
                        ui.input_radio_buttons(
                            "ex_modo_anim",
                            "Mostrar:",
                            choices={
                                "acumulado": "Acumulado hasta ese año",
                                "solo": "Solo los descubiertos ese año",
                            },
                            selected="acumulado",
                        ),
                        ui.input_numeric(
                            "ex_anio_num",
                            f"Ir a un año específico ({anio_min}-{anio_max}):",
                            value=anio_max,
                            min=anio_min,
                            max=anio_max,
                            step=1,
                        ),
                        col_widths=(6, 6),
                    ),
                    ui.input_slider(
                        "ex_anio_anim",
                        "Año:",
                        min=anio_min,
                        max=anio_max,
                        value=anio_max,
                        step=1,
                        sep="",
                        width="100%",
                        animate=ui.AnimationOptions(interval=600, loop=True),
                    ),
                    ui.card(output_widget("ex_grafico_animado")),
                    ui.card(
                        ui.card_header("Planetas por método en el año elegido"),
                        ui.output_data_frame("ex_tabla_anio"),
                    ),
                ),
                ui.nav_panel(
                    "Resumen por método",
                    ui.p(
                        "Solo se incluyen los planetas con período orbital "
                        "y distancia conocidos."
                    ),
                    ui.card(ui.output_data_frame("ex_tabla_resumen")),
                ),
            ),
        ),
    )

    return [panel]


# ----------------------------------------------------------------------
# Servidor
# ----------------------------------------------------------------------
def servidor_extra(input, output, session, planets):

    colores = _mapa_colores(planets)
    anio_min = int(planets["year"].min())
    anio_max = int(planets["year"].max())

    @reactive.calc
    def datos_p5():
        d = planets.dropna(subset=["method", "orbital_period", "distance"])
        seleccion = input.ex_metodos_p5()
        if seleccion:
            return d[d["method"].isin(seleccion)]
        return d.iloc[0:0]

    @reactive.calc
    def seleccion_p5():
        """Planetas de los métodos elegidos, aunque les falte período o distancia."""
        d = planets.dropna(subset=["method", "year"])
        seleccion = input.ex_metodos_p5()
        if seleccion:
            return d[d["method"].isin(seleccion)]
        return d.iloc[0:0]

    @reactive.effect
    @reactive.event(input.ex_anio_num, ignore_init=True)
    def _saltar_a_anio():
        valor = input.ex_anio_num()
        if valor is None:
            return
        valor = int(min(max(valor, anio_min), anio_max))
        ui.update_slider("ex_anio_anim", value=valor, session=session)

    @render_widget
    def ex_grafico_mapa():
        d = datos_p5()
        if d.empty:
            return _fig_vacia()
        log = input.ex_log_p5()
        fig = px.scatter(
            d,
            x="orbital_period",
            y="distance",
            color="method",
            color_discrete_map=colores,
            log_x=log,
            log_y=log,
            opacity=0.75,
            hover_data=["year"],
            title="Período orbital vs distancia a la Tierra",
            labels={
                "orbital_period": "Período orbital (días)",
                "distance": "Distancia a la Tierra (pc)",
                "method": "Método",
                "year": "Año",
            },
        )
        return _estilo(fig)

    @render_widget
    def ex_grafico_animado():
        return _fig_anio(
            datos_p5(),
            input.ex_anio_anim(),
            input.ex_modo_anim(),
            input.ex_log_p5(),
            colores,
        )

    @render.data_frame
    def ex_tabla_anio():
        return render.DataGrid(
            _tabla_anio(seleccion_p5(), input.ex_anio_anim(), input.ex_modo_anim())
        )

    @render.data_frame
    def ex_tabla_resumen():
        d = datos_p5()
        resumen = (
            d.groupby("method")
            .agg(
                planetas=("method", "size"),
                periodo=("orbital_period", "median"),
                distancia=("distance", "median"),
            )
            .round(1)
            .reset_index()
            .sort_values("planetas", ascending=False)
        )
        resumen.columns = [
            "Método",
            "Planetas",
            "Período mediano (días)",
            "Distancia mediana (pc)",
        ]
        return render.DataGrid(resumen)
