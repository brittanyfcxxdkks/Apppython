# Mi parte del proyecto: evolución de los descubrimientos de exoplanetas

**Autor:** Warren Murillo Morales · Curso XS-0130 Programación para Estadística II (UCR)

Esta parte del proyecto agrega a la aplicación Shiny dos visualizaciones interactivas sobre el
conjunto de datos de planetas fuera del Sistema Solar (exoplanetas).

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `grafico_warren.py` | Módulo con las dos visualizaciones, sus filtros y los textos explicativos |
| `planets.csv` | Copia del conjunto de datos `planets` de seaborn, para ejecutar sin internet |
| `requirements.txt` | Paquetes de Python necesarios |

## Datos

- **Origen:** conjunto de datos `planets`, incluido en la librería seaborn.
- **Tamaño:** 1035 planetas y 6 variables, con descubrimientos entre 1989 y 2014.
- **Variables:** `method` (método de descubrimiento, categórica), `number` (planetas en el sistema),
  `orbital_period` (período orbital, en días), `mass` (masa, en masas de Júpiter),
  `distance` (distancia a la Tierra, en parsecs) y `year` (año de descubrimiento).
- **Valores faltantes:** 43 períodos orbitales, 522 masas y 227 distancias.

## Preguntas y visualizaciones

1. **Línea de tiempo.** ¿Cuándo despegaron los descubrimientos de exoplanetas y qué método los impulsó?
   Áreas apiladas por método, con hitos de la historia de los exoplanetas (1992, 1995 y 2009).
2. **Masa y distancia por década.** ¿Son los planetas que detecta Radial Velocity más livianos y más
   lejanos con el paso de las décadas? Barras con la mediana por década y la cantidad de planetas (n).
   Solo se usa Radial Velocity porque es el único método con masa y distancia conocidas en la mayoría de
   sus planetas; la aplicación muestra la tabla de calidad de datos que respalda esta decisión.

## Filtros disponibles

- **Apariencia:** tema (oscuro o claro) y paleta de colores.
- **Línea de tiempo:** vista (por año, acumulado o proporción), agrupar métodos pequeños, suavizado de la
  vista por año, hitos, nombres sobre las áreas, tipo de sistema (solitario o múltiple), tipo de órbita,
  distancia máxima a la Tierra y solo planetas con masa conocida.
- **Masa y distancia por década:** mínimo de planetas por década.

## Instalación y ejecución

```bash
pip install -r requirements.txt
shiny run grafico_warren.py
```

Luego se abre en el navegador la dirección que aparece en la terminal (normalmente `http://127.0.0.1:8000`).

## Cómo integrarlo en la aplicación del grupo

En `proyecto.py`:

```python
from grafico_warren import panel_warren, servidor_warren

# 1) agregar panel_warren dentro de ui.page_navbar(...)
# 2) dentro de la función server(input, output, session), llamar a:
servidor_warren(input, output, session)
```

Todos los identificadores de controles y salidas de este módulo empiezan con `w_`, para no chocar con
los de otras personas del grupo.

## Limitaciones

- El conjunto de datos llega hasta 2014, y los últimos años podrían estar incompletos.
- Más de la mitad de los planetas no tienen masa conocida, y casi toda la masa disponible corresponde a
  planetas detectados con Radial Velocity. Por eso los resultados sobre masa y distancia describen a los
  planetas que ese método puede detectar y no a todos los exoplanetas.
- En Radial Velocity la masa publicada suele ser una masa mínima y no un valor exacto.
- Un cambio entre décadas puede reflejar el método usado en cada época y no solo cómo son los planetas.
