# Apppython

Proyecto

1. Este archivo contiene la informacion de
donde se estudian mediente graficos
2. Integrantes: Warren Murillo Morales, Brittany Sibaja Artavia, Jair Pérez Aburto.

# Análisis de exoplanetas con Shiny para Python

Proyecto del curso XS-0130 Programación para Estadística II · Universidad de Costa Rica

## Descripción

Aplicación web interactiva, desarrollada con Shiny para Python y plotly, que explora el conjunto de datos
`planets` de seaborn: 1035 planetas descubiertos fuera del Sistema Solar entre 1989 y 2014. La aplicación
permite estudiar con qué métodos se han descubierto los planetas, cómo evolucionaron los descubrimientos y
qué características (masa, período orbital y distancia) tienen los planetas que detecta cada método.

## Objetivo

Analizar cómo los distintos métodos de descubrimiento de exoplanetas han contribuido a lo largo del tiempo y qué tipo de planetas detecta cada uno, según su período orbital, distancia y masa.

## Preguntas de investigación

| # | Pregunta | Dónde se responde |
|---|---|---|
| 1 | ¿Cuál es el método mediante el cual se han descubierto más planetas? | Análisis interactivo |
| 2 | ¿Cómo ha evolucionado la cantidad de planetas descubiertos cada año y qué métodos han aportado más en cada etapa? | Evolución de los descubrimientos: línea de tiempo |
| 3 | ¿Son los planetas que detecta Radial Velocity más livianos y más lejanos con el paso de las décadas? | Evolución de los descubrimientos: masa y distancia por década |
| 4 | ¿Cada método de descubrimiento detecta planetas en una zona distinta de período orbital y distancia? | Período y distancia por método |

## Integrantes, partes y ramas

| Integrante | Parte | Rama de trabajo |
|---|---|---|
| Brittany Sibaja Artavia (GitHub: `brittanyfcxxdkks`) | Pestaña «Análisis interactivo»: descubrimientos por método | `rama_de_bri` |
| Warren Murillo Morales (GitHub: `warrenmurillo2005`) | Pestaña «Evolución de los descubrimientos»: línea de tiempo y masa y distancia por década | `rama_de_warren` e `integracion_graficos_warren` |
| Jair Pérez Aburto (GitHub: `perezjair760-coder`) | Pestaña «Período y distancia por método»: mapa de detección, mapa por año y resumen por método | `rama_de_jair` |

## Datos

- **Origen:** conjunto de datos `planets`, incluido en la librería seaborn.
- **Tamaño:** 1035 registros y 6 variables, con descubrimientos entre 1989 y 2014.

| Variable | Descripción | Tipo |
|---|---|---|
| `method` | Método utilizado para descubrir el planeta | Cualitativa nominal |
| `number` | Cantidad de planetas descubiertos alrededor de una estrella | Cuantitativa discreta |
| `orbital_period` | Tiempo que tarda el planeta en completar una órbita, en días | Cuantitativa continua |
| `mass` | Masa del planeta, en masas de Júpiter | Cuantitativa continua |
| `distance` | Distancia entre el sistema planetario y la Tierra, en parsecs | Cuantitativa continua |
| `year` | Año en que fue descubierto el planeta | Cuantitativa discreta |

**Valores faltantes:** 43 períodos orbitales, 522 masas y 227 distancias. Solo 776 planetas tienen período
orbital y distancia conocidos a la vez, y la masa solo se conoce casi completa para los planetas detectados
con el método Radial Velocity (92% de sus planetas; Transit, Imaging y Microlensing tienen 0%).

### Métodos de detección (`method`)

| Método | Traducción | Planetas | Descripción |
| :--- | :--- | :--- | :--- |
| `Radial Velocity` | Velocidad radial | 553 | Detecta el ligero bamboleo gravitacional de una estrella causado por un planeta, midiendo los cambios en su luz mediante el efecto Doppler. |
| `Transit` | Tránsito | 397 | Mide la pequeña y periódica disminución en el brillo de una estrella cuando un planeta pasa exactamente por delante de ella. |
| `Imaging` | Imagen directa | 38 | Captura fotografías directas de planetas jóvenes, masivos y muy alejados de su estrella bloqueando el resplandor estelar. |
| `Microlensing` | Microlente gravitacional | 23 | Aprovecha la gravedad de una estrella y su planeta en primer plano para curvar y amplificar temporalmente la luz de una estrella de fondo. |
| `Eclipse Timing Variations` | Variaciones en el tiempo de eclipse | 9 | Detecta anomalías en el momento exacto en que dos estrellas binarias se eclipsan entre sí, causadas por la gravedad de un planeta cercano. |
| `Pulsar Timing` | Temporización de púlsares | 5 | Mide alteraciones minúsculas en la regularidad de las ondas de radio emitidas por un púlsar debido al tirón gravitacional de un planeta. |
| `Transit Timing Variations` | Variaciones en el tiempo de tránsito | 4 | Identifica planetas ocultos al notar retrasos o adelantos en el tránsito de otro planeta ya conocido dentro del mismo sistema. |
| `Orbital Brightness Modulation` | Modulación del brillo orbital | 3 | Detecta variaciones en la luz combinada del sistema debido a las fases del planeta o al calor que refleja. |
| `Astrometry` | Astrometría | 2 | Mide con altísima precisión el desplazamiento físico de una estrella en el plano del cielo respecto a otras estrellas lejanas. |
| `Pulsation Timing Variations` | Variaciones en la pulsación estelar | 1 | Observa cambios en los ciclos naturales de expansión y contracción de estrellas variables causados por cuerpos en órbita. |


## La aplicación

### Descripción del proyecto

Presenta el conjunto de datos (con una tabla de ejemplo), la descripción y el tipo de cada variable, el
objetivo y las preguntas de investigación.

### Análisis interactivo

Gráfico de barras con la cantidad de planetas descubiertos por método, con filtros por método de
descubrimiento.

### Evolución de los descubrimientos

- **Línea de tiempo.** Áreas apiladas con los descubrimientos de cada año por método, con hitos de la historia
  de los exoplanetas (1992, 1995 y 2009) y los nombres escritos sobre las áreas. Filtros: tema y paleta de
  colores; vista por año, acumulada o en proporción; agrupar métodos pequeños en «Otros»; suavizado; hitos y
  nombres; tipo de sistema (solitario o múltiple); tipo de órbita; distancia máxima a la Tierra; y solo
  planetas con masa conocida. Debajo del gráfico se calculan cifras clave de los datos.
- **Masa y distancia por década.** Barras con la masa y la distancia medianas por década, con la cantidad de
  planetas (n) de cada barra. Se usa solo Radial Velocity, porque es el único método con masa y distancia
  conocidas en al menos 80% de sus planetas; la aplicación muestra la tabla de calidad de datos que respalda
  esta decisión. Filtro: mínimo de planetas por década.

### Período y distancia por método

- **Mapa de detección.** Dispersión del período orbital contra la distancia a la Tierra, con un color por
  método y opción de escala logarítmica. Filtro por método.
- **Mapa por año.** El mismo mapa mostrado año a año, con una barra de tiempo con botón de reproducción, opción
  de ver los planetas acumulados hasta ese año o solo los descubiertos ese año, y una tabla con los planetas por
  método en el año elegido.
- **Resumen por método.** Tabla con la cantidad de planetas, el período mediano y la distancia mediana de cada
  método, solo con planetas que tienen período y distancia conocidos.

## Principales resultados

Cifras obtenidas con la aplicación:

1. **Método con más planetas.** Radial Velocity (553 planetas), seguido de Transit (397). Entre los dos reúnen
   alrededor del 92% de los 1035 planetas.
2. **Evolución en el tiempo.** El año con más descubrimientos fue 2011 (185 planetas), con Radial Velocity como
   método líder ese año. Transit representó el 13% de los planetas descubiertos hasta 2008 (n=340) y el 51% de
   los descubiertos desde 2009 (n=695); Radial Velocity pasó del 78% al 42%. Esto es consistente con la
   entrada en operación de la misión Kepler en 2009, pero los datos no prueban una relación causal.
3. **Masa y distancia por década (solo Radial Velocity).** La masa mediana fue 1.94, 1.78 y 0.47 masas de
   Júpiter en los años 90, 2000 y 2010, es decir, unas 4.1 veces menor en la última década. La distancia
   mediana fue 20.6, 43 y 39.4 pc: unas 1.9 veces mayor que en los años 90, pero similar entre 2000 y 2010.
4. **Zonas de detección.** Cada método ocupa una zona distinta. Con los planetas que tienen período y distancia
   conocidos, Transit tiene un período mediano de 4 días y una distancia mediana de 341 pc, mientras que Radial
   Velocity tiene 355.4 días y 40.4 pc, e Imaging 14018.8 días y 25.8 pc.

## Instalación y uso

```bash
git clone https://github.com/brittanyfcxxdkks/Apppython.git
cd Apppython
pip install -r requirements.txt
python -m shiny run proyecto.py
```

Después se abre en el navegador la dirección que aparece en la terminal (normalmente `http://127.0.0.1:8000`).
Los datos se cargan con seaborn, por lo que la primera ejecución puede requerir conexión a internet. El archivo
`planets.csv` es una copia del conjunto de datos que usa la pestaña de Warren cuando está disponible.


## Flujo de trabajo con Git

Cada integrante desarrolló su parte en una rama propia y la integró a `main` mediante Pull Request:
`rama_de_bri` (Pull Request #1), `rama_de_warren` (Pull Request #2), `integracion_graficos_warren` (que conecta
el módulo de Warren con `proyecto.py`) y `rama_de_jair` (Pull Request #3).

## Limitaciones

- El conjunto de datos llega hasta 2014, y los últimos años podrían estar incompletos.
- La masa solo se conoce para menos de la mitad de los planetas, y casi toda corresponde a Radial Velocity. Por
  eso las conclusiones sobre la masa describen a los planetas que ese método puede detectar y no a todos los
  exoplanetas.
- Los mapas de período y distancia solo dibujan los 776 planetas que tienen ambos datos; algunos métodos, como
  Microlensing, no aparecen porque ninguno de sus planetas cumple esa condición.
- En Radial Velocity la masa publicada suele ser una masa mínima y no un valor exacto.
- Un cambio entre décadas puede reflejar el método usado en cada época y no solo cómo son los planetas.
- No se conoce el nombre de los planetas, así como el sistema planetario a el que pertenecen.
