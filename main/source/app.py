import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_mantine_components as dmc
from utils.utils import *

df = pd.read_excel("../../data/CO2.xlsx", sheet_name="fossil_CO2_totals_by_country")
columns = df.columns.to_list()

df_top5 = get_top5_countries()

BACKGROUND_COLOR = "#101925"
BORDER_COLOR = "#141F2E"

min_year, max_year, years = get_years(df)

fig_pie = px.pie(
    df_top5,
    names="Country",         # etiquetas del pastel
    values="suma",   # valores que determinan tamaño de cada porción
    hole=0.4                   # hace un donut en vez de un pastel completo (opcional)
)

fig_pie.update_traces(
    marker=dict(line=dict(color='#233D38', width=2)),
    textposition="inside",    # pone los valores dentro de cada sector
    textinfo="percent+label", # muestra porcentaje + nombre
    textfont=dict(
        color='white',  # color de todos los textos
        size=14,        # tamaño
        family='Arial'  # fuente
    )
    # pull=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05]   # sacar porciones
)

fig_pie.update_layout(
    paper_bgcolor = BACKGROUND_COLOR,
    plot_bgcolor="white",
)

fig_pie.update_layout(showlegend=False)

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
        html.H2(
            "Top 5 Countries with the Most Historical Emissions",
            style={
                "textAlign": "center",
                "color": "white",
                "marginBottom": "0px"
            }
        ),
        dcc.Graph(
            id="pie-chart",
            figure=fig_pie,
            style={"height": "60vh", "width": "60vw", "margin": "0 auto"}
        )
    ], style = {
        "backgroundColor": BACKGROUND_COLOR
    }),

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
        projection=  "equirectangular"#"mercator"#"natural earth"#"equirectangular"
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
        framecolor = "#e6f2ff" #DESCOMENTAEmisiones de CO₂ por país y añoR Y PONER EL DE ARRIBA TRUE SI SE QUIERE EL MAPA CON UN BORDE DELIMITADOR
    )
    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)