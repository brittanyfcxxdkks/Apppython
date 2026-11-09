"""
grafico_warren.py  -  Parte de Warren del proyecto de análisis de exoplanetas.

Datos: conjunto «planets» de seaborn (1035 planetas descubiertos entre 1989 y 2014).

Dos visualizaciones interactivas (Shiny para Python + plotly):
  1. Línea de tiempo: ¿cuándo despegaron los descubrimientos y qué método los impulsó?
  2. Masa y distancia por década: ¿son los planetas que detecta Radial Velocity más
     livianos y más lejanos con el paso de las décadas?

Ejecutar solo:            shiny run grafico_warren.py
Integrar en la app del grupo (proyecto.py):
    from grafico_warren import panel_warren, servidor_warren
    # 1) agregar panel_warren a ui.page_navbar(...)
    # 2) dentro de server(input, output, session) llamar a:
    #        servidor_warren(input, output, session)
Todos los id de controles y salidas llevan el prefijo «w_» para no chocar con los de otras personas.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

# ----------------------------------------------------------------------
# Datos: se usa planets.csv si está junto a este archivo (no requiere
# internet); si no existe, se descarga de seaborn.
# ----------------------------------------------------------------------
RUTA_CSV = Path(__file__).parent / "planets.csv"
if RUTA_CSV.exists():
    planetas = pd.read_csv(RUTA_CSV)
else:
    planetas = sns.load_dataset("planets")

# década de descubrimiento (por ejemplo "2000s")
planetas["decada"] = (planetas["year"] // 10 * 10).astype(int).astype(str) + "s"

# ----------------------------------------------------------------------
# Opciones de los controles y constantes
# ----------------------------------------------------------------------
TEMAS = {"plotly_dark": "🌌 Espacio (oscuro)", "plotly_white": "☀️ Claro"}
PALETAS = {
    "Vivid": px.colors.qualitative.Vivid,
    "Bold": px.colors.qualitative.Bold,
    "Safe": px.colors.qualitative.Safe,  # pensada para daltonismo
    "Pastel": px.colors.qualitative.Pastel,
}
VISTAS_TIEMPO = {
    "anual": "Por año",
    "acum": "Acumulado",
    "pct": "Proporción por año (%)",
}
SISTEMAS = {
    "todos": "Todos",
    "solo": "Planeta solitario (1)",
    "multiple": "Sistema múltiple (2 o más)",
}
# Tipo de órbita según el período: (mínimo, máximo) en días
ORBITAS = {
    "todas": "Todas",
    "corta": "Menos de 10 días",
    "media": "10 días a 1 año",
    "larga": "1 a 10 años",
    "muy_larga": "Más de 10 años",
}
ORBITAS_LIMITES = {
    "corta": (0, 10), "media": (10, 365.25),
    "larga": (365.25, 3652.5), "muy_larga": (3652.5, np.inf),
}
LIMITES_DIST = {
    "0": "Sin límite",
    "2000": "Hasta 2000 pc",
    "500": "Hasta 500 pc",
    "100": "Hasta 100 pc",
}
# Hitos de la historia de los exoplanetas: (año, texto, altura sobre el área del gráfico)
HITOS = [
    (1992, "1992: primeros exoplanetas confirmados", 1.11),
    (1995, "1995: 51 Pegasi b", 1.04),
    (2009, "2009: lanza Kepler", 1.04),
]
# Un método tiene "datos completos" si al menos UMBRAL_COMPLETO % de sus planetas
# tienen masa Y distancia conocidas, y si tiene al menos MIN_PLANETAS_COMPLETO planetas
UMBRAL_COMPLETO = 80
MIN_PLANETAS_COMPLETO = 20


# ----------------------------------------------------------------------
# Funciones auxiliares (sin Shiny, fáciles de probar)
# ----------------------------------------------------------------------
def figura_vacia(mensaje, tema="plotly_dark"):
    """Figura con un mensaje, para cuando los filtros no dejan datos."""
    fig = go.Figure()
    fig.add_annotation(text=mensaje, showarrow=False, font=dict(size=16))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(template=tema)
    return fig


def colores_grupo(columna, paleta):
    """Un color fijo por grupo (el más frecuente recibe el primer color)."""
    orden = list(planetas[columna].value_counts().index)
    colores = PALETAS[paleta]
    return {g: colores[i % len(colores)] for i, g in enumerate(orden)}


def aplicar_filtros(d, sistema="todos", orbita="todas", dist_max=0):
    """Filtros comunes: tipo de sistema, tipo de órbita y distancia máxima.
    Los planetas sin dato de período o distancia quedan fuera si se usa ese filtro."""
    if sistema == "solo":
        d = d[d["number"] == 1]
    elif sistema == "multiple":
        d = d[d["number"] >= 2]
    if orbita != "todas":
        lo, hi = ORBITAS_LIMITES[orbita]
        d = d[(d["orbital_period"] >= lo) & (d["orbital_period"] < hi)]
    if dist_max:
        d = d[d["distance"] <= dist_max]
    return d


def serie_tiempo(agrupar_otros, sistema="todos", orbita="todas", dist_max=0, solo_masa=False):
    """Descubrimientos por año (filas) y método (columnas), sin huecos de años."""
    anios = range(int(planetas["year"].min()), int(planetas["year"].max()) + 1)
    d = aplicar_filtros(planetas, sistema, orbita, dist_max)
    if solo_masa:
        d = d.dropna(subset=["mass"])
    if d.empty:
        return pd.DataFrame(index=anios)  # sin columnas: nada que mostrar
    d = d.copy()
    if agrupar_otros:  # los 4 métodos más usados + "Otros métodos"
        top = d["method"].value_counts().nlargest(4).index
        d["grupo"] = d["method"].where(d["method"].isin(top), "Otros métodos")
    else:
        d["grupo"] = d["method"]
    anual = pd.crosstab(d["year"], d["grupo"]).reindex(anios, fill_value=0)
    return anual[list(d["grupo"].value_counts().index)]  # el método más frecuente va abajo


def anadir_hitos(fig, oscuro):
    """Líneas verticales con los hitos de la historia de los exoplanetas."""
    color = "rgba(255,255,255,0.55)" if oscuro else "rgba(0,0,0,0.45)"
    for anio, texto, y in HITOS:
        fig.add_vline(x=anio, line_dash="dot", line_width=1, line_color=color)
        fig.add_annotation(x=anio, y=y, yref="paper", text=texto, showarrow=False,
                           xanchor="left", yanchor="bottom", font=dict(size=11))




# ----------------------------------------------------------------------
# Calidad de los datos: qué métodos tienen masa y distancia completas
# ----------------------------------------------------------------------

def tabla_completitud():
    """Por método: cuántos planetas tiene y qué porcentaje tiene masa, distancia y ambas."""
    metodo = planetas["method"]
    completo = planetas["mass"].notna() & planetas["distance"].notna()
    t = pd.DataFrame({
        "planetas": planetas.groupby("method").size(),
        "% con masa": planetas["mass"].notna().groupby(metodo).mean() * 100,
        "% con distancia": planetas["distance"].notna().groupby(metodo).mean() * 100,
        "% con ambas": completo.groupby(metodo).mean() * 100,
    })
    return t.round(0).sort_values("planetas", ascending=False)


def metodos_completos(minimo_planetas=MIN_PLANETAS_COMPLETO, minimo_pct=UMBRAL_COMPLETO):
    """Métodos con suficientes planetas y con masa Y distancia conocidas en casi todos."""
    t = tabla_completitud()
    return list(t[(t["planetas"] >= minimo_planetas) & (t["% con ambas"] >= minimo_pct)].index)


METODOS_COMPLETOS = metodos_completos()




# ----------------------------------------------------------------------
# Masa y distancia por década
# ----------------------------------------------------------------------

def tabla_decadas(variable, metodo="completos", minimo=5):
    """Mediana y cantidad de planetas por década para una variable ("mass" o "distance").
    metodo: "completos" (solo los métodos con datos completos), "todos" o el nombre de un método.
    Solo se muestran las décadas con al menos "minimo" planetas con ese dato."""
    d = planetas.dropna(subset=[variable])
    if metodo == "completos":
        d = d[d["method"].isin(METODOS_COMPLETOS)]
    elif metodo != "todos":
        d = d[d["method"] == metodo]
    g = d.groupby("decada")[variable].agg(mediana="median", n="count")
    return g[g["n"] >= minimo]


def nombre_seleccion(metodo):
    """Texto corto que describe qué planetas se están analizando."""
    if metodo == "completos":
        return "métodos con datos completos: " + (", ".join(METODOS_COMPLETOS) or "ninguno")
    return "todos los métodos" if metodo == "todos" else f"solo {metodo}"


def resumen_decadas(metodo="completos", minimo=5):
    """Cuánto cambia la mediana entre la primera y la última década mostradas."""
    if metodo == "completos" and not METODOS_COMPLETOS:
        return "Ningún método tiene datos completos con los umbrales actuales."
    partes = []
    for var, nombre, unidad, baja, sube in (
        ("mass", "Masa", "M. Júpiter", "menos masivos", "más masivos"),
        ("distance", "Distancia", "pc", "más cerca", "más lejos"),
    ):
        t = tabla_decadas(var, metodo, minimo)
        if len(t) < 2:
            partes.append(f"{nombre}: menos de dos décadas con datos suficientes")
            continue
        a, b = t["mediana"].iloc[0], t["mediana"].iloc[-1]
        factor = max(a, b) / min(a, b)
        partes.append(
            f"{nombre} mediana: {t.index[0]} {a:.3g} → {t.index[-1]} {b:.3g} {unidad} "
            f"(unas {factor:.1f} veces {baja if b < a else sube})"
        )
    return f"[{nombre_seleccion(metodo)}] " + " · ".join(partes)


def parrafos_justificacion(minimo=5):
    """Párrafos (con cifras calculadas de los datos) que explican por qué el análisis de
    masa y distancia por década usa solo los métodos con datos completos."""
    t = tabla_completitud()
    incluidos = METODOS_COMPLETOS
    if not incluidos:
        return ["Ningún método cumple el criterio de datos completos con los umbrales actuales."]

    # 1) el criterio
    lista = ", ".join(incluidos)
    cumple = "es el único método que cumple" if len(incluidos) == 1 else "son los métodos que cumplen"
    p1 = (
        "Comparar la masa y la distancia de los planetas entre décadas exige conocer ambos datos. "
        f"Por eso solo se analizaron los métodos con al menos {MIN_PLANETAS_COMPLETO} planetas y con "
        f"masa y distancia conocidas en al menos {UMBRAL_COMPLETO}% de ellos. De los {len(t)} métodos "
        f"del conjunto de datos, {lista} {cumple}."
    )

    # 2) quiénes quedaron fuera y por qué
    grandes = t[t["planetas"] >= MIN_PLANETAS_COMPLETO]
    excluidos = [m for m in grandes.index if m not in incluidos]
    pequenos = int((t["planetas"] < MIN_PLANETAS_COMPLETO).sum())
    fuera = [
        f"{m} ({t.loc[m, '% con masa']:.0f}% con masa, {t.loc[m, '% con distancia']:.0f}% con distancia)"
        for m in excluidos
    ]
    if pequenos:
        fuera.append(f"otros {pequenos} métodos con menos de {MIN_PLANETAS_COMPLETO} planetas"
                     if pequenos > 1 else f"otro método con menos de {MIN_PLANETAS_COMPLETO} planetas")
    if len(fuera) > 1:
        texto_fuera = ", ".join(fuera[:-1]) + " y " + fuera[-1]
    else:
        texto_fuera = fuera[0] if fuera else ""
    p2 = (
        (f"Quedaron fuera {texto_fuera}. " if texto_fuera else "")
        + "Incluirlos mezclaría planetas descubiertos con técnicas distintas y con datos faltantes "
        "distintos, de modo que un cambio entre décadas podría reflejar el método y no los planetas."
    )

    # 3) lo que muestran los datos (cifras calculadas)
    def serie(var):
        td = tabla_decadas(var, "completos", minimo)
        return ", ".join(f"{dec} {fila['mediana']:.3g} (n={int(fila['n'])})" for dec, fila in td.iterrows())
    p3 = (
        f"Entre las décadas con al menos {minimo} planetas, la masa mediana (en masas de Júpiter) fue: "
        f"{serie('mass')}. La distancia mediana a la Tierra (en parsecs) fue: {serie('distance')}."
    )

    # 4) limitaciones
    ns = pd.concat([tabla_decadas(v, "completos", minimo)["n"] for v in ("mass", "distance")])
    limites = (
        "El conjunto de datos llega hasta 2014. Los resultados describen a los planetas que "
        f"{lista} puede detectar y no a todos los exoplanetas."
    )
    if len(ns):
        limites += f" La década con menos planetas tiene solo n={int(ns.min())}."
    if "Radial Velocity" in incluidos:
        limites += " En este método la masa publicada suele ser una masa mínima y no un valor exacto."
    return [p1, p2, p3, limites]


def texto_justificacion(minimo=5):
    """Los mismos párrafos, listos para copiar al informe."""
    return "\n\n".join(parrafos_justificacion(minimo))




# ----------------------------------------------------------------------
# Línea de tiempo
# ----------------------------------------------------------------------

def resumen_tiempo(anual):
    if anual.shape[1] == 0 or anual.values.sum() == 0:
        return "Ningún planeta cumple los filtros elegidos."
    total = anual.sum(axis=1)
    pico = int(total.idxmax())
    return (
        f"Año con más descubrimientos: {pico} ({int(total[pico])} planetas; "
        f"método líder ese año: {anual.loc[pico].idxmax()}) · "
        f"total en el gráfico: {int(total.sum())} planetas"
    )


def parrafos_hallazgos_tiempo(corte=2008):
    """Cifras clave de la línea de tiempo, calculadas de los datos (no escritas a mano)."""
    anual = serie_tiempo(False)
    total = anual.sum(axis=1)
    pico = int(total.idxmax())
    antes = planetas[planetas["year"] <= corte]
    despues = planetas[planetas["year"] > corte]

    def pct(df, metodo):
        return 100 * (df["method"] == metodo).mean() if len(df) else 0.0

    p1 = (
        f"El año con más descubrimientos fue {pico} ({int(total[pico])} planetas), con "
        f"{anual.loc[pico].idxmax()} como método líder ese año."
    )
    p2 = (
        f"Transit representó el {pct(antes, 'Transit'):.0f}% de los planetas descubiertos hasta {corte} "
        f"(n={len(antes)}) y el {pct(despues, 'Transit'):.0f}% de los descubiertos desde {corte + 1} "
        f"(n={len(despues)}); Radial Velocity pasó del {pct(antes, 'Radial Velocity'):.0f}% al "
        f"{pct(despues, 'Radial Velocity'):.0f}%. Esto es consistente con la entrada en operación de la "
        "misión Kepler en 2009, pero el gráfico no prueba una relación causal."
    )
    p3 = (
        f"El conjunto de datos termina en {int(planetas['year'].max())}: la caída posterior al "
        "máximo podría deberse en parte a que los últimos años estén incompletos."
    )
    return [p1, p2, p3]


def texto_hallazgos():
    """Los mismos párrafos, listos para copiar al informe."""
    return "\n\n".join(parrafos_hallazgos_tiempo())


def posiciones_etiquetas(datos, es_pct):
    """Dónde escribir el nombre de cada área apilada: lista de (grupo, año, y).
    Las áreas muy pequeñas no se etiquetan (la leyenda las identifica)."""
    if es_pct:
        base = datos.div(datos.sum(axis=1).replace(0, np.nan), axis=0).fillna(0) * 100
    else:
        base = datos
    acumulado = base.cumsum(axis=1)  # mismo orden de apilado que las trazas
    umbral = 0.07 * datos.sum(axis=1).max()
    primero, ultimo = int(datos.index.min()), int(datos.index.max())
    posiciones = []
    for grupo in datos.columns:
        if datos[grupo].max() < umbral:
            continue
        anio = int(np.clip(datos[grupo].idxmax(), primero + 2, ultimo - 2))
        y = acumulado.loc[anio, grupo] - base.loc[anio, grupo] / 2  # mitad del área
        posiciones.append((grupo, anio, y))
    return posiciones




# ----------------------------------------------------------------------
# Construcción de las figuras
# ----------------------------------------------------------------------

def construir_decadas(metodo, minimo, tema):
    """Dos gráficos de barras: masa mediana y distancia mediana por década.
    metodo: "completos" (métodos con datos completos), "todos" o el nombre de un método."""
    if metodo == "completos" and not METODOS_COMPLETOS:
        return figura_vacia("Ningún método tiene datos completos con los umbrales actuales", tema)
    paneles = [
        ("mass", "Masa mediana (masas de Júpiter)", "#f28e2b"),
        ("distance", "Distancia mediana a la Tierra (pc)", "#4e9be8"),
    ]
    tablas = [tabla_decadas(var, metodo, minimo) for var, _, _ in paneles]
    if all(t.empty for t in tablas):
        return figura_vacia("Ninguna década llega al mínimo de planetas elegido", tema)

    fig = make_subplots(rows=1, cols=2, subplot_titles=[p[1] for p in paneles],
                        horizontal_spacing=0.12)
    for col, ((var, titulo, color), t) in enumerate(zip(paneles, tablas), start=1):
        if t.empty:
            continue
        fig.add_trace(go.Bar(
            x=list(t.index), y=t["mediana"], marker_color=color, showlegend=False,
            text=[f"<b>{v:.3g}</b><br>n={int(n)}" for v, n in zip(t["mediana"], t["n"])],
            textposition="outside", cliponaxis=False,
            hovertemplate="Década %{x}<br>Mediana: %{y:.3g}<extra></extra>",
        ), row=1, col=col)
        fig.update_yaxes(range=[0, float(t["mediana"].max()) * 1.35], row=1, col=col)  # espacio para el texto
    fig.update_layout(
        title="¿Planetas más livianos y más lejanos con el paso de las décadas?<br>"
              f"<sup>Planetas analizados: {nombre_seleccion(metodo)}</sup>",
        template=tema, height=480, margin=dict(t=120),
    )
    return fig


def construir_tiempo(anual, vista, tema, paleta, suavizado=1, hitos=True, etiquetas=True):
    if anual.shape[1] == 0 or anual.values.sum() == 0:
        return figura_vacia("Ningún planeta cumple los filtros elegidos", tema)
    oscuro = tema == "plotly_dark"
    colores = colores_grupo("method", paleta)
    suave = vista == "anual" and suavizado > 1  # promedio móvil solo en la vista por año
    if vista == "acum":
        datos = anual.cumsum()
    elif suave:
        datos = anual.rolling(suavizado, center=True, min_periods=1).mean()
    else:
        datos = anual
    es_pct = vista == "pct"
    formato = "%{y:.1f} %" if es_pct else ("%{y:,.1f} planetas" if suave else "%{y:,.0f} planetas")
    fig = go.Figure()
    for grupo in datos.columns:
        color = colores.get(grupo, "#888888")  # "Otros métodos" va en gris
        fig.add_trace(go.Scatter(
            x=datos.index, y=datos[grupo], mode="lines", name=grupo,
            stackgroup="uno", groupnorm="percent" if es_pct else "",
            line=dict(width=0.8, color=color), opacity=0.9,
            hovertemplate=f"<b>{grupo}</b><br>Año %{{x}}<br>" + formato + "<extra></extra>",
        ))

    # Nombre escrito directamente sobre cada área
    if etiquetas:
        for grupo, anio, y in posiciones_etiquetas(datos, es_pct):
            fig.add_annotation(
                x=anio, y=y, text=f"<b>{grupo}</b>", showarrow=False,
                font=dict(size=12, color="white" if oscuro else "black"),
                bgcolor="rgba(0,0,0,0.35)" if oscuro else "rgba(255,255,255,0.55)",
            )
    if hitos:
        anadir_hitos(fig, oscuro)

    titulo_anual = "Descubrimientos por año y método"
    if suave:
        titulo_anual += f" (promedio móvil de {suavizado} años)"
    titulos = {
        "acum": ("Descubrimientos acumulados por método", "Planetas acumulados"),
        "anual": (titulo_anual, "Planetas descubiertos en el año"),
        "pct": ("Peso de cada método en los descubrimientos de cada año",
                "% de los descubrimientos del año"),
    }
    fig.update_layout(
        title=titulos[vista][0], xaxis_title="Año de descubrimiento",
        yaxis_title=titulos[vista][1], legend_title_text="Método",
        legend=dict(traceorder="reversed"),  # la leyenda sigue el orden del apilado
        hovermode="x unified", template=tema, height=600,
        margin=dict(t=130 if hitos else 80),
    )
    return fig


# ----------------------------------------------------------------------
# Textos que se calculan una sola vez a partir de los datos
# ----------------------------------------------------------------------
if len(METODOS_COMPLETOS) == 1:
    SUJETO_DECADAS = f"los planetas que detecta {METODOS_COMPLETOS[0]}"
else:
    SUJETO_DECADAS = "los planetas de los métodos con datos completos"
PREGUNTA_DECADAS = f"¿Son {SUJETO_DECADAS} más livianos y más lejanos con el paso de las décadas?"
TITULO_POR_QUE = (
    "¿Por qué solo " + " y ".join(METODOS_COMPLETOS) + "?"
    if METODOS_COMPLETOS else "¿Qué métodos tienen datos completos?"
)
TABLA_COMPLETITUD_HTML = (
    tabla_completitud().rename_axis("Método").astype(int)
    .to_html(classes="table table-sm table-striped", border=0, justify="left")
)
PARRAFOS_JUSTIFICACION = parrafos_justificacion()
PARRAFOS_HALLAZGOS = parrafos_hallazgos_tiempo()


# ----------------------------------------------------------------------
# Interfaz
# ----------------------------------------------------------------------
panel_warren = ui.nav_panel(
    "Evolución de los descubrimientos",
    ui.layout_sidebar(
        ui.sidebar(
            # Apariencia: vale para los dos gráficos
            ui.h4("Apariencia"),
            ui.input_select("w_tema", "Tema:", choices=TEMAS, selected="plotly_dark"),
            ui.input_select("w_paleta", "Paleta de colores:",
                            choices=list(PALETAS), selected="Vivid"),
            ui.hr(),
            # Filtros de la línea de tiempo (solo visibles en esa pestaña)
            ui.panel_conditional(
                "input.w_tab === 'tiempo'",
                ui.h4("Vista"),
                ui.input_radio_buttons("w_vista", "Mostrar:",
                                       choices=VISTAS_TIEMPO, selected="anual"),
                ui.input_switch("w_otros", "Agrupar métodos pequeños en «Otros»", value=True),
                ui.input_slider("w_suavizado", "Suavizar la vista «Por año» (años):",
                                min=1, max=5, value=1),
                ui.input_switch("w_hitos", "Mostrar hitos (1992, 1995, 2009)", value=True),
                ui.input_switch("w_etiquetas", "Nombres sobre las áreas", value=True),
                ui.hr(),
                ui.h4("Qué planetas mostrar"),
                ui.input_select("w_t_sistema", "Tipo de sistema:",
                                choices=SISTEMAS, selected="todos"),
                ui.input_select("w_t_orbita", "Tipo de órbita (período):",
                                choices=ORBITAS, selected="todas"),
                ui.input_select("w_t_dist", "Distancia máxima a la Tierra:",
                                choices=LIMITES_DIST, selected="0"),
                ui.input_switch("w_t_solo_masa", "Solo planetas con masa conocida", value=False),
            ),
            # Filtro del gráfico por década (solo visible en esa pestaña)
            ui.panel_conditional(
                "input.w_tab === 'decadas'",
                ui.h4("Filtros"),
                ui.input_slider("w_a_min", "Mínimo de planetas por década:",
                                min=1, max=50, value=5),
            ),
            width=330,
        ),
        ui.navset_tab(
            # ---- Gráfico 1: línea de tiempo ----
            ui.nav_panel(
                "Línea de tiempo",
                ui.p("¿Cuándo despegaron los descubrimientos de exoplanetas y qué método los impulsó?"),
                ui.p("Cada área es un método y su altura es la cantidad de planetas descubiertos "
                     "ese año. Las líneas punteadas marcan hitos de la historia de los exoplanetas.",
                     class_="text-muted small"),
                ui.card(output_widget("w_tiempo")),
                ui.div(ui.output_text("w_res_tiempo"), class_="text-muted small"),
                ui.card(
                    ui.h5("Qué se observa"),
                    *[ui.p(p) for p in PARRAFOS_HALLAZGOS],
                ),
                value="tiempo",
            ),
            # ---- Gráfico 2: masa y distancia por década ----
            ui.nav_panel(
                "Masa y distancia por década",
                ui.p(PREGUNTA_DECADAS),
                ui.card(output_widget("w_decadas")),
                ui.div(ui.output_text("w_res_decadas"), class_="text-muted small"),
                ui.card(
                    ui.h5(TITULO_POR_QUE),
                    ui.HTML(TABLA_COMPLETITUD_HTML),
                    *[ui.p(p) for p in PARRAFOS_JUSTIFICACION],
                ),
                value="decadas",
            ),
            id="w_tab",
        ),
    ),
)


# ----------------------------------------------------------------------
# Servidor
# ----------------------------------------------------------------------
def servidor_warren(input, output, session):

    @reactive.calc
    def anual():
        """Descubrimientos por año y método, con los filtros elegidos."""
        return serie_tiempo(
            input.w_otros(), input.w_t_sistema(), input.w_t_orbita(),
            int(input.w_t_dist()), input.w_t_solo_masa(),
        )

    # --- Línea de tiempo ---
    @render_widget
    def w_tiempo():
        return construir_tiempo(
            anual(), input.w_vista(), input.w_tema(), input.w_paleta(),
            input.w_suavizado(), input.w_hitos(), input.w_etiquetas(),
        )

    @render.text
    def w_res_tiempo():
        return resumen_tiempo(anual())

    # --- Masa y distancia por década ---
    @render_widget
    def w_decadas():
        return construir_decadas("completos", input.w_a_min(), input.w_tema())

    @render.text
    def w_res_decadas():
        return resumen_decadas("completos", input.w_a_min())


# Para ejecutar este archivo solo: shiny run grafico_warren.py
app_ui = ui.page_navbar(panel_warren, title="Exoplanetas: evolución de los descubrimientos")
app = App(app_ui, servidor_warren)
