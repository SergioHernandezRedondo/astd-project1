import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from utils.utils import *
from utils.figures import *

df = pd.read_excel("../../data/CO2.xlsx", sheet_name="fossil_CO2_totals_by_country")
columns = df.columns.to_list()

df_top5 = get_top5_countries()
df_top5_capita = get_top5_countries("fossil_CO2_per_capita_by_countr")

BACKGROUND_COLOR = "#101925"
BORDER_COLOR = "#141F2E"

MIN_EMISSION, MAX_EMISSION = get_max_min_emission("fossil_CO2_totals_by_country")

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
        range_color = [MIN_EMISSION, MAX_EMISSION]
    )
    fig.update_geos(
        lataxis_range=[-60, 90], # Quita la antártida del mapa
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

if __name__ == "__main__":
    app.run(debug=True)