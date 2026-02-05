import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from utils.utils import *
from utils.figures import *
from pathlib import Path
import numpy as np
from datetime import datetime
import plotly.graph_objects as go


BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = f"{BASE_DIR}/../../data/CO2.xlsx"

df = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_per_capita_by_countr")
columns = df.columns.to_list()
columnas_años = [col for col in df.columns if str(col).isnumeric()]
p95 = np.percentile(df[columnas_años].values.flatten(), 95)

df_top5 = get_top5_countries(path=CSV_PATH)
df_top5_capita = get_top5_countries(CSV_PATH,"fossil_CO2_per_capita_by_countr")
df_sector = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_by_sector_and_countr")
lista_sectores = df_sector["Sector"].unique()

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
        
        html.Div([
            html.H2(
                "CO₂ Emissions per Capita by Country and Year",
                style={"textAlign": "center", "color": "white", "marginBottom": "10px", "fontSize": "18px"}
            ),
            dcc.Graph(
                id="choropleth-map",
                style={"height": "500px"}
            ),
            html.Div(
                dcc.Slider(
                    id="year-slider",
                    min=min_year, max=max_year, value=min_year,
                    marks={str(y): str(y) for y in years},
                    step=1, updatemode="drag"
                ),
                style={"width": "80%", "margin": "0 auto", "backgroundColor": BORDER_COLOR, "borderRadius": "10px", "padding": "10px"}
            ),
        ], style={"width": "70%", "backgroundColor": BORDER_COLOR, "borderRadius": "10px"}),

        html.Div([
            html.H4("Emissions by Sector for Selected Country", 
                    style={"color": "white", "textAlign": "center", "fontSize": "18px"}),
            dcc.Graph(
                id='grafico-sectores',
                style={"height": "400px"} 
            )
        ], style={
            "width": "28%", 
            "backgroundColor": BORDER_COLOR, 
            "justifyContent": "center",
            "borderRadius": "10px",
            "padding": "10px"
        })

    ], style={
        "display": "flex", 
        "flexDirection": "row", 
        "justifyContent": "space-between", 
        "alignItems": "center", 
    }),

    # SEPARADOR
    html.Div([
        html.Hr(style={
            'borderWidth': '1px',
            'borderColor': BORDER_COLOR,
            'margin': '50px 0',
            'width': '100%',
            'borderStyle': 'solid'
        })
    ]),

    html.Div([
        # Bloque del Treemap
        html.Div([
            html.H4("Internal Sectoral Distribution", 
                    style={"color": "white", "textAlign": "center", "fontSize": "18px"}),
            dcc.Graph(id='treemap-sectores', style={"height": "400px"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR, "padding": "20px", "borderRadius": "15px"}),

        # Bloque del Gauge con su selector
        html.Div([
            html.H4("Global Sectoral Significance", 
                    style={"color": "white", "textAlign": "center", "fontSize": "18px"}),
            dcc.Dropdown(
                id='sector-dropdown',
                options=[{'label': s, 'value': s} for s in lista_sectores],
                value=lista_sectores[0],
                clearable=False,
                style={"backgroundColor": "#1a2634", "color": "black", "marginBottom": "20px"}
            ),
            dcc.Graph(id='gauge-comparativo', style={"height": "320px"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR, "padding": "20px", "borderRadius": "15px"})

    ], style={
        "display": "flex", "flexDirection": "row", "gap": "20px", "marginTop": "20px", "width": "100%"
    }),

    # SEPARADOR
    html.Div([
        html.Hr(style={
            'borderWidth': '1px',
            'borderColor': BORDER_COLOR,
            'margin': '50px 0',
            'width': '100%',
            'borderStyle': 'solid'
        })
    ]),

    html.Div([
        html.Div([
            html.H4("National vs. Global Sectoral Footprint", 
                    style={"color": "white", "textAlign": "center", "fontSize": "18px"}),
            dcc.Graph(id='bar-comparativo', style={"height": "400px"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR, "padding": "20px", "borderRadius": "15px"}),
    ], style={
        "display": "flex", "marginTop": "20px", "width": "100%"
    }),

    # SEPARADOR
    html.Div([
        html.Hr(style={
            'borderWidth': '1px',
            'borderColor': BORDER_COLOR,
            'margin': '50px 0',
            'width': '100%',
            'borderStyle': 'solid'
        })
    ]),

    html.Div([
        html.Div([
            html.H4("Top 5 Countries with Highest Historical CO₂", style={"textAlign": "center", "color": "white", "fontSize": "18px"}),
            dcc.Graph(id="pie-chart", figure=fig_pie, style={"height": "45vh"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR}),

        html.Div([
            html.H4("Top 5 Countries with Highest CO₂ per Capita", style={"textAlign": "center", "color": "white", "fontSize": "18px"}),
            dcc.Graph(id="pie-chart-capita", figure=fig_pie_capita, style={"height": "45vh"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR}),
    ], style={
        "display": "flex",
        "flexDirection": "row",
        "justifyContent": "space-between",
        "gap": "20px",
        "width": "100%",
        "backgroundColor": BORDER_COLOR,
        "BorderRadius": "10px",
    })

], style={"backgroundColor": BACKGROUND_COLOR, "padding": "20px"})

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
        paper_bgcolor=BORDER_COLOR,
        dragmode=False,
        coloraxis_colorbar=dict(
            title="t CO₂/cap",
            thicknessmode="pixels", thickness=15,
            lenmode="fraction", len=0.6,
            yanchor="middle", y=0.5,
            xanchor="left", x=-0.13, # El valor negativo lo saca hacia la izquierda
            ticks="outside"
        )
    )
    return fig


@app.callback(
    Output('grafico-sectores', 'figure'),
    Input('choropleth-map', 'clickData')
)
def update_sector_chart(clickData):
    # Selección por defecto (España) si no hay interacción
    iso_code = "ESP"
    nombre_pais = "Spain"
    
    if clickData:
        iso_code = clickData['points'][0]['location']
        nombre_pais = clickData['points'][0]['hovertext']

    # Filtramos por país
    df_pais = df_sector[df_sector["ISOcode"] == iso_code]
    
    # Transformamos de formato ancho a largo (años en una sola columna)
    df_long = df_pais.melt(
        id_vars=["Sector", "Country", "ISOcode"], 
        var_name="Year", 
        value_name="Emissions"
    )
    
    # Convertimos 'Año' a numérico para que el eje X sea temporal
    df_long["Year"] = pd.to_numeric(df_long["Year"])

    fig = px.line(
        df_long, 
        x="Year", 
        y="Emissions", 
        color="Sector",
        title=f"Country: {nombre_pais}",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_layout(
        title=dict(
            text=f"Country: {nombre_pais}",
            font=dict(size=12, color="white"), # Ajusta el número para el tamaño
            x=0.5,                             # Centra el título opcionalmente
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h", 
            yanchor="bottom", y=-0.4, 
            xanchor="center", x=0.5,
            font=dict(size=10)
        ),
        margin=dict(l=60, r=20, t=50, b=80),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#2a3f5f", title="Emissions (Mt CO₂)")
    )
    
    return fig

# --- Callback para el Treemap Sectorial ---
@app.callback(
    Output('treemap-sectores', 'figure'),
    [Input('choropleth-map', 'clickData'),
     Input('year-slider', 'value')]
)
def update_treemap(clickData, selected_year):
    iso_code = "ESP" # España por defecto
    nombre_pais = "Spain"
    if clickData:
        iso_code = clickData['points'][0]['location']
        nombre_pais = clickData['points'][0]['hovertext']
    
    # Filtramos por país y año, quitando valores nulos o cero
    df_filtered = df_sector[df_sector["ISOcode"] == iso_code][["Sector", selected_year]]
    df_filtered = df_filtered[df_filtered[selected_year] > 0]
    
    # Creamos el objeto base (eliminamos el título de aquí para ponerlo en el layout)
    fig = px.treemap(
        df_filtered, 
        path=[px.Constant("National Total"), 'Sector'], 
        values=selected_year,
        template="plotly_dark",
        color=selected_year,
        color_continuous_scale='Greens',
        labels={str(selected_year): "Mt CO₂"}
    )
    
    # Ajustamos el título y los márgenes
    fig.update_layout(
        title={
            'text': f"Country: {nombre_pais} ({selected_year})",
            'x': 0.5,               # Lo sitúa en el 50% del ancho
            'xanchor': 'center',    # Asegura que el centro del texto coincida con el 0.5
            'font': {'size': 12, 'color': 'white'}
        },
        paper_bgcolor='rgba(0,0,0,0)', 
        # Aumentamos el margen superior (t=50) para que el título respire
        margin=dict(l=10, r=10, t=50, b=10) 
    )
    
    return fig

# --- Callback para el Gauge Comparativo ---
@app.callback(
    Output('gauge-comparativo', 'figure'),
    [Input('choropleth-map', 'clickData'),
     Input('year-slider', 'value'),
     Input('sector-dropdown', 'value')]
)
def update_gauge(clickData, selected_year, selected_sector):
    iso_code = "ESP"
    nombre_pais = "Spain"
    if clickData:
        iso_code = clickData['points'][0]['location']
        nombre_pais = clickData['points'][0]['hovertext']

    # Emisión del país en ese sector y año
    fila = df_sector[(df_sector["ISOcode"] == iso_code) & (df_sector["Sector"] == selected_sector)]
    val_pais = fila[selected_year].values[0] if not fila.empty else 0
    
    # Emisión mundial de ese mismo sector y año
    val_mundo = df_sector[df_sector["Sector"] == selected_sector][selected_year].sum()
    
    # Porcentaje de aporte
    porcentaje = (val_pais / val_mundo * 100) if val_mundo > 0 else 0

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = porcentaje,
        number = {'suffix': "%", 'font': {'size': 24}, 'valueformat': ".2f"},
        title = {'text': f"{nombre_pais}'s Contribution to Global {selected_sector} ({selected_year})",'font': {'size': 14}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00ffcc"},
            'bgcolor': "#101925",
            'steps': [{'range': [0, 100], 'color': "#141F2E"}],
            'threshold': {'line': {'color': "red", 'width': 3}, 'value': porcentaje}
        }
    ))
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, margin=dict(l=20, r=20, t=50, b=20))
    return fig

@app.callback(
    Output('bar-comparativo', 'figure'),
    [Input('choropleth-map', 'clickData'),
     Input('year-slider', 'value')]
)
def update_bar_comparison(clickData, selected_year):
    iso_code = "ESP"
    nombre_pais = "Spain"
    if clickData:
        iso_code = clickData['points'][0]['location']
        nombre_pais = clickData['points'][0]['hovertext']

    # 1. Identificar los 3 sectores con mayor emisión mundial en ese año
    sectores_top = df_sector.groupby("Sector")[selected_year].sum().nlargest(3).index.tolist()
    
    data_list = []
    for sector in sectores_top:
        emision_pais = df_sector[(df_sector["ISOcode"] == iso_code) & (df_sector["Sector"] == sector)][selected_year].sum()
        emision_total_mundo = df_sector[df_sector["Sector"] == sector][selected_year].sum()
        
        share_pct = (emision_pais / emision_total_mundo * 100) if emision_total_mundo > 0 else 0
        rest_pct = 100 - share_pct

        # Datos del País
        data_list.append({
            "Sector": sector, 
            "Value": emision_pais, 
            "Type": f"{nombre_pais}'s Share", 
            "Label": f"{share_pct:.1f}%"
        })
        # Datos del Resto del Mundo
        data_list.append({
            "Sector": sector, 
            "Value": emision_total_mundo - emision_pais, 
            "Type": "Rest of the World",
            "Label": f"{rest_pct:.1f}%"
        })

    df_plot = pd.DataFrame(data_list)

    # Creamos el gráfico HORIZONTAL (y=Sector, x=Value, orientation='h')
    fig = px.bar(
        df_plot, 
        y="Sector", 
        x="Value", 
        color="Type",
        text="Label", # Mostramos el porcentaje calculado
        orientation='h',
        template="plotly_dark",
        color_discrete_map={
            f"{nombre_pais}'s Share": "#00ffcc",
            "Rest of the World": "#1a2634"
        }
    )

    fig.update_traces(
        textposition='inside', 
        insidetextanchor='middle',
        textfont=dict(size=12, family="Arial Black")
    )

    fig.update_layout(
        title={
            'text': f"Country: {nombre_pais} ({selected_year})",
            'font': {'size': 14, 'color': "white"}, 
            'x': 0.5, 'xanchor': 'center', 'y': 0.95
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        barmode='stack',
        showlegend=True,
        legend=dict(
            title="", 
            orientation="h",        # Horizontal para que no ocupe mucho espacio vertical
            yanchor="bottom", 
            y=1.02,                 # Justo encima del eje del gráfico
            xanchor="right", 
            x=1                     # Alineado al borde derecho del gráfico
        ),        # Aumentamos el margen izquierdo (l) para que se lean bien los nombres de los sectores
        margin=dict(l=140, r=40, t=60, b=80),
        xaxis=dict(title="Emissions (Mt CO₂)", showgrid=True, gridcolor="#2a3f5f"),
        yaxis=dict(title="") # Eliminamos el título "Sector" para mayor limpieza
    )
    
    return fig

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)