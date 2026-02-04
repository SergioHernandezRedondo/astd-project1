import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from utils.utils import *
from utils.figures import *
from pathlib import Path
import numpy as np
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = f"{BASE_DIR}/../../data/CO2.xlsx"

df = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_per_capita_by_countr")
columns = df.columns.to_list()
columnas_años = [col for col in df.columns if str(col).isnumeric()]
p95 = np.percentile(df[columnas_años].values.flatten(), 95)

df_top5 = get_top5_countries(path=CSV_PATH)
df_top5_capita = get_top5_countries(CSV_PATH,"fossil_CO2_per_capita_by_countr")

BACKGROUND_COLOR = "#101925"
BORDER_COLOR = "#141F2E"

MIN_EMISSION, MAX_EMISSION = get_max_min_emission(CSV_PATH,"fossil_CO2_per_capita_by_countr")

min_year, max_year, years = get_years(df)

# Crear los donuts
fig_pie = get_pie_chart(df_top5)
fig_pie_capita = get_pie_chart(df_top5_capita)

app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([

        # Título de la sección
        html.H2(
            "CO2 Emissions by Country and Year",
            style={
                "textAlign": "center",
                "color": "white",
                "marginBottom": "0px"
            }
        ),

        # Gráfico principal
        dcc.Graph(
            id="choropleth-map",
            style={"height": "80vh"}
        ),

        # Slider debajo del gráfico
        html.Div(
            dcc.Slider(
                id="year-slider",
                min=min_year,
                max=max_year,
                value=min_year,
                marks={str(y): str(y) for y in years},
                step=1,
                updatemode="drag"
            ),
            style={
                "width": "95%",
                "margin": "0 auto 0 auto",  # centrado y con espacio arriba
                #"padding": "10px 0"
            }
        )

    ], style={
        "backgroundColor": BACKGROUND_COLOR,
        "padding": "0px",
        "marginBottom": "40px",
        "borderRadius": "12px",
        "position": "relative"
    }),
        # Dentro de app.layout, añade este bloque debajo del mapa de emisiones
    html.Div([
        html.H3("Análisis Atmosférico por Posición", 
                style={"color": "white", "marginTop": "30px", "textAlign": "center"}),
        html.P("Pulsa sobre cualquier país en el mapa superior para calcular su masa de aire actual.",
            style={"color": "#a1a1a1", "textAlign": "center", "marginBottom": "20px"}),
        
        # Solo el gráfico, sin botones ni entradas de texto
        dcc.Graph(id='grafico-aire')
    ], style={
        "backgroundColor": BORDER_COLOR, 
        "padding": "25px", 
        "borderRadius": "15px",
        "marginTop": "20px"
    }),
    html.Div([
        html.Hr(style={
            'borderWidth': '1px',      # grosor de la línea
            'borderColor': BORDER_COLOR,    # color de la línea
            'margin': '20px 0',        # espacio arriba y abajo
            'width': '100%',            # ancho de la línea
            'borderStyle': 'solid'     # estilo: solid, dashed, dotted
        })
    ], style = {
        "marginTop": "100px",
        "marginBottom": "100px"
    }),
    html.Div([
        html.Div([
            html.H4(
                "Top 5 Countries with the Highest Historical CO₂ Emissions",
                style={
                    "textAlign": "center",
                    "color": "white",
                    "marginBottom": "0px",
                    "flex": "1"
                }
            ),
            dcc.Graph(
                id="pie-chart",
                figure=fig_pie,
                style={"height": "45vh", "flex": "1"}
            )
        ], style = {
            "flex": "1 1 0",
            "backgroundColor": BACKGROUND_COLOR,

        }),
        html.Div([
            html.H4(
                "Top 5 Countries with the Highest Historical CO₂ Emissions By Population",
                style={
                    "textAlign": "center",
                    "color": "white",
                    "marginBottom": "0px",
                    "flex": "2"
                }
            ),
            dcc.Graph(
                id="pie-chart-capita",
                figure=fig_pie_capita,
                style={"height": "45vh", "flex": "2"}
            )
        ], style = {
            "flex": "1 1 0",
            "backgroundColor": BACKGROUND_COLOR

        }),
    ],
        style={
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "space-between",
            "alignItems": "center",
            "gap": "20px",
            "width": "100%"
        }
    )


],
style={
    "backgroundColor": BACKGROUND_COLOR,
    "padding": "20px"
})

@app.callback(
    Output("choropleth-map", "figure"),
    Input("year-slider", "value")
)
def update_map(selected_year):
    filtered = df[["ISOcode", "Country", selected_year]]
    fig = px.choropleth(
        filtered,
        locations="ISOcode",
        color=selected_year,
        hover_name="Country",
        color_continuous_scale="RdYlGn_r",
        projection=  "equirectangular",
        range_color = [MIN_EMISSION, p95],
    )
    fig.update_geos(
        lataxis_range=[-57, 90], # Quita la antártida del mapa
        bgcolor=BACKGROUND_COLOR,
        showocean=True,
        oceancolor=BACKGROUND_COLOR,
        showland=True,
        landcolor="#f2f2f2",
        showcountries=True,
        countrycolor="gray",
        showlakes=True,
        lakecolor=BACKGROUND_COLOR,
        showframe=True,
        framecolor = "#e6f2ff" #DESCOMENTAR Y PONER EL DE ARRIBA TRUE SI SE QUIERE EL MAPA CON UN BORDE DELIMITADOR
    )
    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        dragmode = False
    )
    return fig


# Mapa rápido de latitudes medias (puedes ampliarlo o usar el centroide del país)
LATITUDES_PAISES = {
    "ESP": 40.4, "USA": 37.0, "CHN": 35.8, "BRA": -14.2, "RUS": 61.5, "AUS": -25.2,
    "FRA": 46.2, "GER": 51.1, "IND": 20.5, "MEX": 23.6, "ARG": -38.4, "ZAF": -30.5
}

@app.callback(
    Output('grafico-aire', 'figure'),
    Input('choropleth-map', 'clickData') # Escuchamos al mapa principal
)
def actualizar_por_puntero(clickData):
    # Si no han hecho clic, usamos una posición por defecto (p. ej. España)
    lat_seleccionada = 40.4
    nombre_pais = "España (Default)"
    
    if clickData:
        # Extraemos el código del país donde se hizo clic
        iso_code = clickData['points'][0]['location']
        nombre_pais = clickData['points'][0]['hovertext']
        # Buscamos la latitud (o usamos 0 si no está en el mini-diccionario)
        lat_seleccionada = LATITUDES_PAISES.get(iso_code, 0.0)

    # Calculamos el ángulo cenital aproximado para HOY (simplificado)
    # En un proyecto real usaríamos pvlib, pero aquí estimamos según la latitud
    dia_del_año = datetime.now().timetuple().tm_yday
    declina_solar = 23.45 * np.sin(np.radians((360/365) * (284 + dia_del_año)))
    angulo_zenit = abs(lat_seleccionada - declina_solar)
    
    # Limitamos para evitar errores matemáticos en el horizonte
    angulo_zenit = min(89, max(0, angulo_zenit))
    
    # Generamos el gráfico de la curva
    angulos = np.linspace(0, 89, 100)
    masas = [calcular_masa_aire(a) for a in angulos]
    masa_actual = calcular_masa_aire(angulo_zenit)
    
    fig = px.line(x=angulos, y=masas, template="plotly_dark",
                 labels={'x': 'Inclinación Cenital (°)', 'y': 'Masa de Aire (AM)'})
    
    fig.add_scatter(x=[angulo_zenit], y=[masa_actual], mode='markers+text',
                    text=[f"{nombre_pais}: {masa_actual:.2f} AM"],
                    textposition="top center",
                    marker=dict(size=15, color='#00ffcc')) # Un color cian eléctrico
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)