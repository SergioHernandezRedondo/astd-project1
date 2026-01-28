import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

df = pd.read_excel("../../data/CO2.xlsx", sheet_name="fossil_CO2_totals_by_country")
columns = df.columns.to_list()
years = []

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
    dcc.Slider(
        id="year-slider",
        min=min_year,
        max=max_year,
        value=min_year,
        marks={str(y): str(y) for y in years},
    ),
    dcc.Graph(id="choropleth-map")
])

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
        projection="equirectangular"
    )
    fig.update_layout(title=f"Valores en {selected_year}")
    return fig

if __name__ == "__main__":
    app.run(debug=True)