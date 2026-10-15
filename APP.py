from shiny import App, ui, render

app_ui = ui.page_fluid(
    ui.h2("Mi primera aplicación Shiny"),
    ui.input_text("nombre", "Escribe tu nombre:"),
    ui.output_text("saludo")
)

def server(input, output, session):

    @output
    @render.text
    def saludo():
        return f"¡Hola, {input.nombre()}!"

app = App(app_ui, server)
