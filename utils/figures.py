import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

BACKGROUND_COLOR = "#101925"
BORDER_COLOR = "#141F2E"

def get_pie_chart(data):
    fig_pie = px.pie(
        data,
        names="Country",  # etiquetas del pastel
        values="suma",  # valores que determinan tamaño de cada porción
        hole=0.4  # hace un donut en vez de un pastel completo (opcional)
    )

    fig_pie.update_traces(
        marker=dict(line=dict(color='#233D38', width=2)),
        textposition="inside",  # pone los valores dentro de cada sector
        textinfo="percent+label",  # muestra porcentaje y nombre
        textfont=dict(
            color='white',  # color de todos los textos
            size=14,  # tamaño
            family='Arial'  # fuente
        )
        # pull=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05]   # sacar porciones
    )

    fig_pie.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor="white",
    )

    fig_pie.update_layout(showlegend=False)

    return fig_pie