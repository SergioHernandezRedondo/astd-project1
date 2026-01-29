import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_mantine_components as dmc

df = pd.read_excel("../../data/CO2.xlsx", sheet_name="fossil_CO2_totals_by_country")
columns = df.columns.to_list()
years = []

BACKGROUND_COLOR = "#101925"

for col in columns:
    try:
        years.append(int(col))
    except ValueError:
        pass

if years:
    min_year = min(years)
    max_year = max(years)
else:
    print("ERROR: no hay años en la lista de columnas")
    exit(1)

app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([

        # Título de la sección
        html.H2(
            "Emisiones de CO₂ por país y año",
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
        framecolor = "#e6f2ff" #DESCOMENTAR Y PONER EL DE ARRIBA TRUE SI SE QUIERE EL MAPA CON UN BORDE DELIMITADOR
    )
    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)