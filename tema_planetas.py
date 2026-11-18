"""Tema oscuro "espacio" para toda la app de planetas.

Uso en proyecto.py:
    from tema_planetas import TEMA, estilo_global, estilo_plotly

    app_ui = ui.page_navbar(
        ...,
        title="Análisis de planetas",
        theme=TEMA,
        header=estilo_global(),
    )

    y en los gráficos de plotly:   return estilo_plotly(fig)
"""

from shiny import ui

# Otras opciones de tema oscuro: "cyborg", "slate", "superhero", "vapor"
PRESET = "darkly"

FONDO = "#0b1020"

TEMA = ui.Theme(PRESET)

CSS = """
body {
  background: radial-gradient(ellipse at top, #16213e 0%, #0b1020 70%) fixed;
  min-height: 100vh;
}
.navbar {
  background: linear-gradient(90deg, #0b1020, #1b2a4a) !important;
  border-bottom: 1px solid #22304f;
}
.navbar {
  --bs-navbar-color: #c7d0e6;
  --bs-navbar-hover-color: #ffffff;
  --bs-navbar-active-color: #ffffff;
  --bs-navbar-brand-color: #ffffff;
  --bs-navbar-brand-hover-color: #ffffff;
}
.navbar a,
.navbar .navbar-brand,
.navbar .nav-link {
  color: #c7d0e6 !important;
}
.navbar .navbar-brand,
.navbar a:hover,
.navbar .nav-link:hover,
.navbar .nav-link.active {
  color: #ffffff !important;
}
.navbar-brand {
  font-weight: 600;
  letter-spacing: .5px;
}
.card {
  background-color: rgba(18, 27, 50, .92);
  border: 1px solid #22304f;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, .45);
}
h1, h2, h3, h4 {
  color: #f2f5ff;
}
.table {
  --bs-table-bg: transparent;
  --bs-table-striped-bg: rgba(255, 255, 255, .05);
}
.shiny-data-grid table thead th,
.table thead th {
  background-color: #1b2a4a !important;
  color: #f2f5ff !important;
}
.shiny-data-grid table tbody td {
  background-color: transparent !important;
  color: #e6e9f2;
}
"""


def estilo_global():
    """CSS que se agrega a toda la app (se pasa en header= del page_navbar)."""
    return ui.tags.style(CSS)


def estilo_plotly(fig):
    """Mismo aspecto oscuro para los gráficos de plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=FONDO,
        plot_bgcolor=FONDO,
        margin=dict(t=60, l=60, r=20, b=60),
    )
    return fig
