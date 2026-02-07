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
        ], style={"width": "100%", "backgroundColor": BORDER_COLOR, "borderRadius": "10px"}),

    ], style={
        "display": "flex", 
        "flexDirection": "row", 
        "justifyContent": "space-between", 
        "alignItems": "center", 
    }),

    html.Div([
        html.Div([
            html.H4("Historical Emissions by Sector for Selected Country", 
                    style={"color": "white", "textAlign": "center", "fontSize": "18px"}),
            dcc.Graph(
                id='grafico-sectores',
                style={"height": "400px"} 
            )
        ], style={
            "backgroundColor": BORDER_COLOR, 
            "justifyContent": "center",
            "borderRadius": "10px",
            "padding": "10px",
            "width": "50%"
        }),

        html.Div([
            html.H4("Internal Sectoral Distribution", 
                    style={"color": "white", "textAlign": "center", "fontSize": "18px"}),
            dcc.Graph(id='treemap-sectores', style={"height": "400px"})
        ], style={"backgroundColor": BORDER_COLOR, "padding": "20px", "borderRadius": "15px", "width": "50%"})

    ], style={
        "display": "flex", "flexDirection": "row", "gap": "20px", "marginTop": "20px", "width": "100%"
    }),

    html.Div([
        html.Div([
            html.H4("National vs. Global Sectoral Footprint", 
                    style={"color": "white", "textAlign": "center", "fontSize": "18px"}),
            dcc.Graph(id='bar-comparativo', style={"height": "400px"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR, "padding": "20px", "borderRadius": "15px"}),
    ], style={
        "display": "flex", "marginTop": "20px", "width": "100%"
    }),

    # NUEVA FILA: COMPARATIVA DE TENDENCIAS (Ranking y Evolución)
    html.Div([
        html.Div([
            html.H4("Compare Country Trends", style={"color": "white", "textAlign": "center"}),
            dcc.Dropdown(
                id='multi-country-dropdown',
                options=[{'label': c, 'value': c} for c in df['Country'].unique()],
                value=['Spain and Andorra', 'China', 'United States'], # Valores iniciales para la comparativa
                multi=True,
                style={"backgroundColor": "#1a2634", "color": "black"}
            ),
            dcc.Graph(id='trend-comparison-graph', style={"height": "400px"})
        ], style={"flex": "2", "backgroundColor": BORDER_COLOR, "padding": "20px", "borderRadius": "15px"}),

        html.Div([
            html.H4("Yearly Statistical Summary", style={"color": "white", "textAlign": "center"}),
            html.Div(id='summary-table-container') # Aquí inyectaremos una tabla dinámica
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR, "padding": "20px", "borderRadius": "15px"})
    ], style={"display": "flex", "flexDirection": "row", "gap": "20px", "marginTop": "20px"}),

    # FILA DE PIE CHARTS (Ahora serán dinámicos por año)
    html.Div([
        html.Div([
            html.H4("Top 5 Emitters by Year", style={"textAlign": "center", "color": "white"}),
            dcc.Graph(id="pie-chart-dynamic", style={"height": "45vh"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR, "borderRadius": "10px", "padding": "10px"}),

        html.Div([
            html.H4("Top 5 Per Capita by Year", style={"textAlign": "center", "color": "white"}),
            dcc.Graph(id="pie-chart-capita-dynamic", style={"height": "45vh"})
        ], style={"flex": "1", "backgroundColor": BORDER_COLOR, "borderRadius": "10px", "padding": "10px"}),
    ], style={"display": "flex", "gap": "20px", "width": "100%"})

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

    sectores_ordenados = df_sector.groupby("Sector")[selected_year].sum().sort_values(ascending=True).index.tolist()  

    data_list = []
    for sector in sectores_ordenados:
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

@app.callback(
    Output('trend-comparison-graph', 'figure'),
    Input('multi-country-dropdown', 'value')
)
def update_trend_comparison(selected_countries):
    # Filtramos el dataframe original por los países seleccionados
    df_multi = df[df['Country'].isin(selected_countries)]
    df_long = df_multi.melt(id_vars=["Country"], value_vars=columnas_años, var_name="Year", value_name="Emissions")
    
    fig = px.line(df_long, x="Year", y="Emissions", color="Country", template="plotly_dark",
                 title="Historical Trend Comparison (Per Capita)")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="t CO₂/cap")
    return fig

@app.callback(
    Output('summary-table-container', 'children'),
    Input('year-slider', 'value')
)
def update_summary_table(selected_year):
    # Calculamos métricas sobre el DataFrame per cápita (df)
    avg_val = df[selected_year].mean()
    max_val = df[selected_year].max()
    max_country = df.loc[df[selected_year].idxmax(), 'Country']
    
    # Construcción de la tabla con estilo CSS para que encaje en el diseño oscuro
    return html.Table([
        html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")], style={"borderBottom": "2px solid #555"})),
        html.Tbody([
            html.Tr([html.Td("Global Average"), html.Td(f"{avg_val:.2f} t/cap")]),
            html.Tr([html.Td("Top Emitter"), html.Td(f"{max_country}")]),
            html.Tr([html.Td("Peak Emission"), html.Td(f"{max_val:.2f} t/cap")]),
        ])
    ], style={"color": "white", "width": "100%", "marginTop": "20px", "textAlign": "left", "fontSize": "14px"})

from plotly.subplots import make_subplots

@app.callback(
    [Output("pie-chart-dynamic", "figure"),
     Output("pie-chart-capita-dynamic", "figure")],
    Input("year-slider", "value")
)
def update_dynamic_rankings(selected_year):
    def create_ranked_pie(dataframe, val_col):
        # 1. Preparar datos: Top 5 + Others
        full_rank = dataframe.sort_values(by=val_col, ascending=False)
        top5 = full_rank.head(5)
        others_val = full_rank.iloc[5:][val_col].sum()
        
        # Combinamos para el gráfico
        df_pie = pd.concat([
            top5, 
            pd.DataFrame({"Country": ["Others"], val_col: [others_val]})
        ])

        # 2. Crear Subplots: Tabla (Ranking) + Pie
        fig = make_subplots(
            rows=1, cols=2, 
            column_widths=[0.4, 0.6],
            specs=[[{"type": "table"}, {"type": "pie"}]]
        )

        # Añadir Tabla de Ranking
        fig.add_trace(
            go.Table(
                header=dict(values=["Ranking", "Country", "Value"], fill_color='#1a2634', align='left', font=dict(color='white', size=11)),
                cells=dict(values=[[1,2,3,4,5], top5["Country"], top5[val_col].round(2)], fill_color='#101925', align='left', font=dict(color='white', size=10))
            ),
            row=1, col=1
        )

        # Añadir Pie Chart
        fig.add_trace(
            go.Pie(
                labels=df_pie["Country"], 
                values=df_pie[val_col],
                hole=0.5,
                textinfo='label+percent', # Nombre del país + porcentaje
                insidetextorientation='radial',
                marker=dict(colors=px.colors.qualitative.Pastel)
            ),
            row=1, col=2
        )

        fig.update_layout(
            title=dict(
                text=f"({selected_year})",
                x=0.5, font=dict(size=14, color="white")
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        return fig

    # Gráfico 1: Emisiones Totales (desde df_sector)
    df_total = df_sector.groupby("Country")[selected_year].sum().reset_index()
    fig1 = create_ranked_pie(df_total, selected_year)

    # Gráfico 2: Emisiones Per Capita (desde df)
    fig2 = create_ranked_pie(df, selected_year)
    
    return fig1, fig2

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)