import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from utils.utils import get_max_min_emission, get_years, get_theme_colors
from plotly.subplots import make_subplots

CSV_PATH = os.path.join("data", "CO2.xlsx")

df = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_per_capita_by_countr")
df_totals = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_totals_by_country")
df_sector = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_by_sector_and_countr")

columns = df.columns.to_list()
columns_years = [col for col in df.columns if str(col).isnumeric()]
p95 = np.percentile(df[columns_years].values.flatten(), 95)

MIN_EMISSION, MAX_EMISSION = get_max_min_emission(
    CSV_PATH, "fossil_CO2_per_capita_by_countr"
)

min_year, max_year, years = get_years(df)

# Country options for dropdown
country_options = [{"label": c, "value": c} for c in sorted(df["Country"].unique())]

app = dash.Dash(__name__, assets_folder="assets")

app.layout = html.Main(
    id="main-container",
    children=[
        dcc.Store(
            id="session-storage",
            data={
                "year": 2000,
                "country": "Taiwan",
                "iso_code": "TWN",
                "theme": "light",
            },
        ),
        html.Header(
            [
                html.Div(
                    [
                        html.H1(id="dynamic-title"),
                        dcc.Checklist(
                            id="theme-switch",
                            options=[{"label": "🌙 Dark Mode", "value": "dark"}],
                            value=[],
                            inline=True,
                            className="theme-switch-container",
                        ),
                    ],
                    className="header-top-row",
                ),
                # Slider container (height: auto)
                html.Div(
                    dcc.Slider(
                        id="year-slider",
                        min=min_year,
                        max=max_year,
                        value=2000,
                        marks={
                            str(y): {
                                "label": str(y),
                                "style": {"color": "var(--text-main)"},
                            }
                            for y in years
                            if y % 5 == 0
                        },
                        step=1,
                        updatemode="drag",
                    ),
                    className="header-slider-row",
                ),
            ]
        ),
        html.P("Select the country you wish to analyze"),
        # Map Section
        html.Section(
            [
                dcc.Graph(id="choropleth-map", responsive=True, className="card-map"),
            ]
        ),
        # Sectoral Distribution Row
        html.Section(
            [
                html.Div(
                    [
                        html.H2("Internal Sectoral Distribution"),
                        dcc.Graph(id="treemap-sectores", responsive=True),
                    ],
                    className="card",
                ),
                html.Div(
                    [
                        html.H2("Historical Emissions by Sector"),
                        dcc.Graph(id="grafico-sectores", responsive=True),
                    ],
                    className="card",
                ),
            ],
            className="grid-row",
        ),
        # Global Comparison (Tall Card)
        html.Section(
            [
                html.Div(
                    [
                        html.H2("Global Sectoral Comparison"),
                        html.Label("Select Countries to Compare with:"),
                        dcc.Dropdown(
                            id="sector-countries-dropdown",
                            options=country_options,
                            value=[],
                            multi=True,
                        ),
                        dcc.Graph(id="sector-comparison-graph", responsive=True),
                    ],
                    className="card tall-card",
                ),
            ]
        ),
        # Rankings Row
        html.Section(
            [
                html.Div([dcc.Graph(id="pie-chart-dynamic")], className="card"),
                html.Div([dcc.Graph(id="pie-chart-capita-dynamic")], className="card"),
            ],
            className="grid-row",
        ),
        # Trends Section
        html.Section(
            [
                html.Div(
                    [
                        html.H2("Compare Country Trends"),
                        html.Label("Select Countries to Compare with:"),
                        dcc.Dropdown(
                            id="multi-country-dropdown",
                            options=[
                                {"label": c, "value": c} for c in df["Country"].unique()
                            ],
                            value=[],
                            multi=True,
                        ),
                        dcc.Graph(id="trend-comparison-graph"),
                    ],
                    className="card",
                ),
            ]
        ),
    ],
)


@app.callback(
    Output("main-container", "data-theme"),
    Input("theme-switch", "value"),
)
def update_theme(switch_value):
    """Updates the data-theme attribute of the main container."""
    return "dark" if "dark" in switch_value else "light"


@app.callback(
    [Output("session-storage", "data"), Output("dynamic-title", "children")],
    [Input("year-slider", "value"), Input("choropleth-map", "clickData")],
    State("session-storage", "data"),
)
def sync_and_title(selected_year, map_click, current_data):
    """
    Updates the global session storage with the selected year and country,
    and generates a dynamic title for the dashboard header.
    """

    # 1. Update Country if a map location is clicked
    if map_click:
        # Store the country name from hovertext for display purposes
        current_data["country"] = map_click["points"][0]["hovertext"]
        # If you need the ISO code for filtering, store it as well:
        current_data["iso_code"] = map_click["points"][0]["location"]

    # 2. Update Year from the slider value
    current_data["year"] = selected_year

    # 3. Format the dynamic title string
    new_title = (
        f"CO2 Emissions in {current_data['country']} in the year {selected_year}"
    )

    return current_data, new_title


@app.callback(
    Output("choropleth-map", "figure"),
    [Input("year-slider", "value"), Input("session-storage", "data")],
)
def update_map(selected_year, global_data):
    """
    Updates the global choropleth map based on the selected year and
    highlights the borders of the currently selected country.
    """
    # 1. Retrieve the selected ISO code from the global store
    selected_iso = global_data.get("iso_code") if global_data else None

    # Filter data for the specific year
    filtered = df[["ISOcode", "Country", selected_year]]

    # --- BASE LAYER: Main Choropleth Map ---
    fig = px.choropleth(
        filtered,
        locations="ISOcode",
        color=selected_year,
        hover_name="Country",
        color_continuous_scale="Teal",
        projection="natural earth",
        range_color=[MIN_EMISSION, p95],
        labels={str(selected_year): "Pollution"},
    )

    # --- HIGHLIGHT LAYER: Selected Country Border ---
    if selected_iso:
        fig.add_trace(
            go.Choropleth(
                locations=[selected_iso],
                z=[1],  # Dummy value
                # Transparent fill to show only the border
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                showscale=False,
                marker=dict(
                    line=dict(
                        color="red",  # High contrast border
                        width=3,  # Thickness of the highlight
                    )
                ),
                hoverinfo="skip",  # Do not interfere with base hover
            )
        )

    # Geographic configuration to fix whitespace and set zoom
    fig.update_geos(
        showcoastlines=False,
        showland=False,
        showocean=False,
        showlakes=False,
        showcountries=True,
        countrycolor="#cccccc",
        # Crop poles and apply zoom
        lataxis_range=[-50, 85],
        projection_scale=1.15,
        framecolor="rgba(0,0,0,0)",
        bgcolor="rgba(0,0,0,0)",
    )

    # Layout and Colorbar styling
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title="t CO₂/cap",
            thicknessmode="pixels",
            thickness=15,
            lenmode="fraction",
            len=0.6,
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(0,0,0,0)",
            outlinecolor="rgba(0,0,0,0)",
            tickfont=dict(color="#7f8c8d"),
        ),
        dragmode=False,
        transition_duration=500,
        transition_easing="cubic-in-out",
    )

    # Custom Tooltip
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Fossils: %{z:.2f}<extra></extra>",
        selector=dict(type="choropleth"),  # Apply only to the base map
    )

    return fig


@app.callback(Output("treemap-sectores", "figure"), Input("session-storage", "data"))
def update_treemap(global_data):
    """
    Generates a sectoral treemap for the selected country and year
    stored in the session storage.
    """
    # 1. Retrieve data from global store
    iso_code = global_data.get("iso_code", "ESP")
    selected_year = str(global_data.get("year", 1990))

    try:
        selected_year = int(global_data.get("year", 1990))
    except (TypeError, ValueError):
        selected_year = 1990

    # 2. Filter data by country and year, removing nulls
    df_filtered = df_sector[df_sector["ISOcode"] == iso_code][["Sector", selected_year]]
    df_filtered = df_filtered[df_filtered[selected_year] > 0]

    # 3. Create Treemap with color mapping based on emissions
    fig = px.treemap(
        df_filtered,
        path=["Sector"],
        values=selected_year,
        color=selected_year,
        color_continuous_scale="Teal",
        labels={selected_year: "Mt CO₂"},
    )

    # 4. Trace configuration for static, high-visibility look
    fig.update_traces(
        textinfo="label+percent parent",
        hoverinfo="none",
        marker=dict(line=dict(width=1, color="white")),
        maxdepth=1,  # Disables drill-down zoom
    )

    # 5. Layout adjustment for full integration
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),  # Stretch to fill Div
        hovermode=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7f8c8d"),
        coloraxis_showscale=False,
        clickmode="event",  # Prevents unwanted zoom behavior
    )

    return fig


@app.callback(Output("grafico-sectores", "figure"), Input("session-storage", "data"))
def update_sector_chart(global_data):
    """
    Generates a historical line chart for emissions by sector based on
    the country stored in session storage.
    """
    # 1. Retrieve current country data
    iso_code = global_data.get("iso_code", "ESP")
    country_name = global_data.get("country", "Spain")

    try:
        selected_year = int(global_data.get("year", 1990))
    except (TypeError, ValueError):
        selected_year = 1990

    # 2. Filter and reshape data from wide to long format
    df_country = df_sector[df_sector["ISOcode"] == iso_code]
    df_long = df_country.melt(
        id_vars=["Sector", "Country", "ISOcode"],
        var_name="Year",
        value_name="Emissions",
    )
    df_long["Year"] = pd.to_numeric(df_long["Year"])

    # 3. Create line chart with a harmonious color sequence
    fig = px.line(
        df_long,
        x="Year",
        y="Emissions",
        color="Sector",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    # 4. Remove all hardcoded styles and apply transparent theme
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7f8c8d"),
        # Modern horizontal legend at the bottom
        legend=dict(
            orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, title=None
        ),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(127, 140, 141, 0.2)",  # Subtle gray grid
            title="Mt CO₂",
            zeroline=False,
        ),
        hovermode=False,  # Professional vertical hover line
    )

    # 5. Clean line appearance
    fig.update_traces(line=dict(width=2))

    return fig


@app.callback(
    Output("sector-comparison-graph", "figure"),
    [
        Input("sector-countries-dropdown", "value"),
        Input("year-slider", "value"),
        Input("session-storage", "data"),
    ],
)
def update_sector_graph(dropdown_countries, year, global_data):
    theme = global_data.get("theme", "light")
    colors = get_theme_colors(theme)
    map_country = global_data.get("country")

    countries = list(dropdown_countries) if dropdown_countries else []
    if map_country and map_country not in countries:
        countries.insert(0, map_country)

    if not countries:
        # Return empty figure if no selection to avoid "Afghanistan" default
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"visible": False},
            yaxis={"visible": False},
            margin=dict(t=50, b=80, l=40, r=10),
            height=450,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                title=None,
                font=dict(color="#7f8c8d"),
            ),
        )
        return fig

    data = df_sector[df_sector["Country"].isin(countries)][["Country", "Sector", year]]

    fig = px.bar(
        data,
        x="Sector",
        y=year,
        color="Country",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Sector Breakdown</b><br><sup>Year: {year}</sup>",
            x=0.05,
            y=0.95,
            font=dict(size=16, color="#7f8c8d"),  # Grey title
        ),
        template=colors["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7f8c8d", size=11),  # Grey general text
        margin=dict(t=80, b=20, l=40, r=10),
        yaxis=dict(gridcolor=colors["grid"], title="Mt CO₂", zeroline=False),
        xaxis=dict(title=None),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title=None,
            font=dict(color="#7f8c8d"),
        ),
        transition_duration=500,
    )
    return fig


@app.callback(
    [
        Output("pie-chart-dynamic", "figure"),
        Output("pie-chart-capita-dynamic", "figure"),
    ],
    [Input("year-slider", "value"), Input("session-storage", "data")],
)
def update_dynamic_rankings(selected_year, session_data):
    theme = session_data.get("theme", "light")
    colors = get_theme_colors(theme)

    def create_ranked_pie(dataframe, val_col, title_main):
        full_rank = dataframe.sort_values(by=val_col, ascending=False)
        top5 = full_rank.head(5)
        others_val = full_rank.iloc[5:][val_col].sum()
        df_pie = pd.concat(
            [top5, pd.DataFrame({"Country": ["Others"], val_col: [others_val]})]
        )

        fig = make_subplots(
            rows=1,
            cols=2,
            column_widths=[0.35, 0.65],
            specs=[[{"type": "table"}, {"type": "pie"}]],
            horizontal_spacing=0.05,
        )

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["<b>Rank</b>", "<b>Country</b>"],
                    fill_color=colors["grid"],
                    align="left",
                    font=dict(color="#7f8c8d", size=12),  # Grey header
                    line_color=colors["grid"],
                ),
                cells=dict(
                    values=[[1, 2, 3, 4, 5], top5["Country"]],
                    fill_color="rgba(0,0,0,0)",
                    align="left",
                    font=dict(color="#7f8c8d", size=11),  # Grey cells
                    line_color=colors["grid"],
                    height=25,
                ),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Pie(
                labels=df_pie["Country"],
                values=df_pie[val_col],
                hole=0.5,
                textinfo="percent",
                marker=dict(line=dict(color=colors["bg"], width=2)),
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title=dict(
                text=f"<b>{title_main}</b><br><sup>Year: {selected_year}</sup>",
                x=0.05,
                y=0.95,
                font=dict(size=16, color="#7f8c8d"),  # Grey title
            ),
            template=colors["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#7f8c8d"),  # Grey general font
            margin=dict(l=10, r=10, t=80, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        return fig

    df_total = df_sector.groupby("Country")[selected_year].sum().reset_index()
    fig1 = create_ranked_pie(df_total, selected_year, "Top 5 Global Emitters")
    fig2 = create_ranked_pie(df, selected_year, "Top 5 Per Capita Emitters")

    return fig1, fig2

import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from utils.utils import get_max_min_emission, get_years, get_theme_colors
from plotly.subplots import make_subplots

CSV_PATH = os.path.join("data", "CO2.xlsx")

df = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_per_capita_by_countr")
df_sector = pd.read_excel(CSV_PATH, sheet_name="fossil_CO2_by_sector_and_countr")

columns = df.columns.to_list()
columns_years = [col for col in df.columns if str(col).isnumeric()]
p95 = np.percentile(df[columns_years].values.flatten(), 95)

MIN_EMISSION, MAX_EMISSION = get_max_min_emission(
    CSV_PATH, "fossil_CO2_per_capita_by_countr"
)

min_year, max_year, years = get_years(df)

# Country options for dropdown
country_options = [{"label": c, "value": c} for c in sorted(df["Country"].unique())]

app = dash.Dash(__name__, assets_folder="assets")

app.layout = html.Main(
    id="main-container",
    children=[
        dcc.Store(
            id="session-storage",
            data={
                "year": 2000,
                "country": "Taiwan",
                "iso_code": "TWN",
                "theme": "light",
            },
        ),
        html.Header(
            [
                html.Div(
                    [
                        html.H1(id="dynamic-title"),
                        dcc.Checklist(
                            id="theme-switch",
                            options=[{"label": "🌙 Dark Mode", "value": "dark"}],
                            value=[],
                            inline=True,
                            className="theme-switch-container",
                        ),
                    ],
                    className="header-top-row",
                ),
                # Slider container (height: auto)
                html.Div(
                    dcc.Slider(
                        id="year-slider",
                        min=min_year,
                        max=max_year,
                        value=2000,
                        marks={
                            str(y): {
                                "label": str(y),
                                "style": {"color": "var(--text-main)"},
                            }
                            for y in years
                            if y % 5 == 0
                        },
                        step=1,
                        updatemode="drag",
                    ),
                    className="header-slider-row",
                ),
            ]
        ),
        html.P("Select the country you wish to analyze."),
        # Map Section
        html.Section(
            [
                dcc.Graph(id="choropleth-map", responsive=True, className="card-map"),
            ]
        ),
        # Sectoral Distribution Row
        html.Section(
            [
                html.Div(
                    [
                        html.H2("Internal Sectoral Distribution"),
                        dcc.Graph(id="treemap-sectores", responsive=True),
                    ],
                    className="card",
                ),
                html.Div(
                    [
                        html.H2("Historical Emissions by Sector"),
                        dcc.Graph(id="grafico-sectores", responsive=True),
                    ],
                    className="card",
                ),
            ],
            className="grid-row",
        ),

        html.Section(
            [
                html.Div(
                    [
                        html.H2("Global Sectoral Comparison"),
                        dcc.Dropdown(
                            id="sector-countries-dropdown",
                            options=country_options,
                            value=[],
                            multi=True,
                            placeholder="Select Countries to Compare with..."
                        ),
                        dcc.Graph(id="sector-comparison-graph", responsive=True),
                    ],
                    className="card tall-card",
                ),
            ]
        ),
        # Rankings Row
        html.Section(
            [
                html.Div([dcc.Graph(id="pie-chart-dynamic")], className="card"),
                html.Div([dcc.Graph(id="pie-chart-capita-dynamic")], className="card"),
            ],
            className="grid-row",
        ),
        # Trends Section
        html.Section(
            [
                html.Div(
                    [
                        html.H2("Compare Country Trends"),
                        dcc.Dropdown(
                            id="multi-country-dropdown",
                            options=[
                                {"label": c, "value": c} for c in df["Country"].unique()
                            ],
                            value=[],
                            multi=True,
                            placeholder="Select Countries to Compare with..."
                        ),
                        dcc.Graph(id="trend-comparison-graph"),
                    ],
                    className="card",
                ),
            ]
        ),
    ],
)


@app.callback(
    Output("main-container", "data-theme"),
    Input("theme-switch", "value"),
)
def update_theme(switch_value):
    """Updates the data-theme attribute of the main container."""
    return "dark" if "dark" in switch_value else "light"


@app.callback(
    [Output("session-storage", "data"), Output("dynamic-title", "children")],
    [Input("year-slider", "value"), Input("choropleth-map", "clickData")],
    State("session-storage", "data"),
)
def sync_and_title(selected_year, map_click, current_data):
    """
    Updates the global session storage with the selected year and country,
    and generates a dynamic title for the dashboard header.
    """

    # 1. Update Country if a map location is clicked
    if map_click:
        # Store the country name from hovertext for display purposes
        current_data["country"] = map_click["points"][0]["hovertext"]
        # If you need the ISO code for filtering, store it as well:
        current_data["iso_code"] = map_click["points"][0]["location"]

    # 2. Update Year from the slider value
    current_data["year"] = selected_year

    # 3. Format the dynamic title string
    new_title = (
        f"CO2 Emissions in {current_data['country']} in the year {selected_year}"
    )

    return current_data, new_title


@app.callback(
    Output("choropleth-map", "figure"),
    [Input("year-slider", "value"), Input("session-storage", "data")],
)
def update_map(selected_year, global_data):
    """
    Updates the global choropleth map based on the selected year and
    highlights the borders of the currently selected country.
    """
    # 1. Retrieve the selected ISO code from the global store
    selected_iso = global_data.get("iso_code") if global_data else None

    # Filter data for the specific year
    filtered = df[["ISOcode", "Country", selected_year]]

    # --- BASE LAYER: Main Choropleth Map ---
    fig = px.choropleth(
        filtered,
        locations="ISOcode",
        color=selected_year,
        hover_name="Country",
        color_continuous_scale="Teal",
        projection="natural earth",
        range_color=[MIN_EMISSION, p95],
        labels={str(selected_year): "Pollution"},
    )

    # --- HIGHLIGHT LAYER: Selected Country Border ---
    if selected_iso:
        fig.add_trace(
            go.Choropleth(
                locations=[selected_iso],
                z=[1],  # Dummy value
                # Transparent fill to show only the border
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                showscale=False,
                marker=dict(
                    line=dict(
                        color="red",  # High contrast border
                        width=3,  # Thickness of the highlight
                    )
                ),
                hoverinfo="skip",  # Do not interfere with base hover
            )
        )

    # Geographic configuration to fix whitespace and set zoom
    fig.update_geos(
        showcoastlines=False,
        showland=False,
        showocean=False,
        showlakes=False,
        showcountries=True,
        countrycolor="#cccccc",
        # Crop poles and apply zoom
        lataxis_range=[-50, 85],
        projection_scale=1.15,
        framecolor="rgba(0,0,0,0)",
        bgcolor="rgba(0,0,0,0)",
    )

    # Layout and Colorbar styling
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title="t CO₂/cap",
            thicknessmode="pixels",
            thickness=15,
            lenmode="fraction",
            len=0.6,
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(0,0,0,0)",
            outlinecolor="rgba(0,0,0,0)",
            tickfont=dict(color="#7f8c8d"),
        ),
        dragmode=False,
        transition_duration=500,
        transition_easing="cubic-in-out",
    )

    # Custom Tooltip
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Fossils: %{z:.2f}<extra></extra>",
        selector=dict(type="choropleth"),  # Apply only to the base map
    )

    return fig


@app.callback(Output("treemap-sectores", "figure"), Input("session-storage", "data"))
def update_treemap(global_data):
    """
    Generates a sectoral treemap for the selected country and year
    stored in the session storage.
    """
    # 1. Retrieve data from global store
    iso_code = global_data.get("iso_code", "ESP")
    selected_year = str(global_data.get("year", 1990))

    try:
        selected_year = int(global_data.get("year", 1990))
    except (TypeError, ValueError):
        selected_year = 1990

    # 2. Filter data by country and year, removing nulls
    df_filtered = df_sector[df_sector["ISOcode"] == iso_code][["Sector", selected_year]]
    df_filtered = df_filtered[df_filtered[selected_year] > 0]

    # 3. Create Treemap with color mapping based on emissions
    fig = px.treemap(
        df_filtered,
        path=["Sector"],
        values=selected_year,
        color=selected_year,
        color_continuous_scale="Teal",
        labels={selected_year: "Mt CO₂"},
    )

    # 4. Trace configuration for static, high-visibility look
    fig.update_traces(
        textinfo="label+percent parent",
        hoverinfo="none",
        marker=dict(line=dict(width=1, color="white")),
        maxdepth=1,  # Disables drill-down zoom
    )

    # 5. Layout adjustment for full integration
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),  # Stretch to fill Div
        hovermode=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7f8c8d"),
        coloraxis_showscale=False,
        clickmode="event",  # Prevents unwanted zoom behavior
    )

    return fig


@app.callback(Output("grafico-sectores", "figure"), Input("session-storage", "data"))
def update_sector_chart(global_data):
    """
    Generates a historical line chart for emissions by sector based on
    the country stored in session storage.
    """
    # 1. Retrieve current country data
    iso_code = global_data.get("iso_code", "ESP")
    country_name = global_data.get("country", "Spain")

    try:
        selected_year = int(global_data.get("year", 1990))
    except (TypeError, ValueError):
        selected_year = 1990

    # 2. Filter and reshape data from wide to long format
    df_country = df_sector[df_sector["ISOcode"] == iso_code]
    df_long = df_country.melt(
        id_vars=["Sector", "Country", "ISOcode"],
        var_name="Year",
        value_name="Emissions",
    )
    df_long["Year"] = pd.to_numeric(df_long["Year"])

    # 3. Create line chart with a harmonious color sequence
    fig = px.line(
        df_long,
        x="Year",
        y="Emissions",
        color="Sector",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    # 4. Remove all hardcoded styles and apply transparent theme
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7f8c8d"),
        # Modern horizontal legend at the bottom
        legend=dict(
            orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, title=None
        ),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(127, 140, 141, 0.2)",  # Subtle gray grid
            title="Mt CO₂",
            zeroline=False,
        ),
        hovermode=False,  # Professional vertical hover line
    )

    # 5. Clean line appearance
    fig.update_traces(line=dict(width=2))

    return fig


@app.callback(
    Output("sector-comparison-graph", "figure"),
    [
        Input("sector-countries-dropdown", "value"),
        Input("year-slider", "value"),
        Input("session-storage", "data"),
    ],
)
def update_sector_graph(dropdown_countries, year, global_data):
    theme = global_data.get("theme", "light")
    colors = get_theme_colors(theme)
    map_country = global_data.get("country")

    countries = list(dropdown_countries) if dropdown_countries else []
    if map_country and map_country not in countries:
        countries.insert(0, map_country)

    if not countries:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"visible": False},
            yaxis={"visible": False},
            margin=dict(t=50, b=80, l=40, r=10),
            height=450,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                title=None,
                font=dict(color="#7f8c8d"),
            ),
        )
        return fig

    data = df_sector[df_sector["Country"].isin(countries)][["Country", "Sector", year]]

    fig = px.bar(
        data,
        x="Sector",
        y=year,
        color="Country",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Sector Breakdown</b><br><sup>Year: {year}</sup>",
            x=0.05,
            y=0.95,
            font=dict(size=16, color="#7f8c8d"),  # Grey title
        ),
        template=colors["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7f8c8d", size=11),  # Grey general text
        margin=dict(t=80, b=20, l=40, r=10),
        yaxis=dict(gridcolor=colors["grid"], title="Mt CO₂", zeroline=False),
        xaxis=dict(title=None),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title=None,
            font=dict(color="#7f8c8d"),
        ),
        transition_duration=500,
    )
    return fig


@app.callback(
    [
        Output("pie-chart-dynamic", "figure"),
        Output("pie-chart-capita-dynamic", "figure"),
    ],
    [Input("year-slider", "value"), Input("session-storage", "data")],
)
def update_dynamic_rankings(selected_year, session_data):
    theme = session_data.get("theme", "light")
    colors = get_theme_colors(theme)

    def create_ranked_pie(dataframe, val_col, title_main):
        full_rank = dataframe.sort_values(by=val_col, ascending=False)
        top5 = full_rank.head(5)
        others_val = full_rank.iloc[5:][val_col].sum()
        df_pie = pd.concat(
            [top5, pd.DataFrame({"Country": ["Others"], val_col: [others_val]})]
        )

        fig = make_subplots(
            rows=1,
            cols=2,
            column_widths=[0.35, 0.65],
            specs=[[{"type": "table"}, {"type": "pie"}]],
            horizontal_spacing=0.05,
        )

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["<b>Rank</b>", "<b>Country</b>"],
                    fill_color=colors["grid"],
                    align="left",
                    font=dict(color="#7f8c8d", size=12),  # Grey header
                    line_color=colors["grid"],
                ),
                cells=dict(
                    values=[[1, 2, 3, 4, 5], top5["Country"]],
                    fill_color="rgba(0,0,0,0)",
                    align="left",
                    font=dict(color="#7f8c8d", size=11),  # Grey cells
                    line_color=colors["grid"],
                    height=25,
                ),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Pie(
                labels=df_pie["Country"],
                values=df_pie[val_col],
                hole=0.5,
                textinfo="percent",
                marker=dict(line=dict(color=colors["bg"], width=2)),
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title=dict(
                text=f"<b>{title_main}</b><br><sup>Year: {selected_year}</sup>",
                x=0.05,
                y=0.95,
                font=dict(size=16, color="#7f8c8d"),  # Grey title
            ),
            template=colors["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#7f8c8d"),  # Grey general font
            margin=dict(l=10, r=10, t=80, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        return fig

    df_total = df_sector.groupby("Country")[selected_year].sum().reset_index()
    fig1 = create_ranked_pie(df_total, selected_year, "Top 5 Global Emitters")
    fig2 = create_ranked_pie(df, selected_year, "Top 5 Per Capita Emitters")

    return fig1, fig2

@app.callback(
    Output("trend-comparison-graph", "figure"),
    [Input("multi-country-dropdown", "value"), Input("session-storage", "data")],
)
def update_trend_comparison(dropdown_countries, global_data):
    theme = global_data.get("theme", "light")
    colors = get_theme_colors(theme)
    map_country = global_data.get("country")

    countries = list(dropdown_countries) if dropdown_countries else []
    if map_country and map_country not in countries:
        countries.insert(0, map_country)

    if not countries:
        return go.Figure().update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )

    # --- CAMBIO IMPORTANTE: Usamos df_totals en vez de df ---
    df_multi = df_totals[df_totals["Country"].isin(countries)]
    
    # Derretimos (melt) el dataframe de totales
    df_long = df_multi.melt(
        id_vars=["Country"],
        value_vars=columns_years, # Usamos las mismas columnas de años
        var_name="Year",
        value_name="Emissions",
    )

    fig = px.line(
        df_long,
        x="Year",
        y="Emissions",
        color="Country",
        title="Historical Trend Comparison (Total Emissions)", # Título actualizado
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    fig.update_layout(
        title=dict(font=dict(color="#7f8c8d", size=16)),
        template=colors["template"],
        paper_bgcolor=colors["bg"],
        plot_bgcolor=colors["bg"],
        font_color="#7f8c8d",
        xaxis=dict(
            gridcolor=colors["grid"],
            showline=True,
            linecolor=colors["grid"],
            tickangle=45,
        ),
        yaxis=dict(
            gridcolor=colors["grid"],
            title="Mt CO₂",  # Unidad cambiada a Megatoneladas (Totales)
            showline=True,
            linecolor=colors["grid"],
        ),
        # Leyenda arreglada para que no tape el eje X
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            title=None,
        ),
        margin=dict(l=40, r=20, t=60, b=120),
        hovermode="x unified",
        transition_duration=500,
    )
    return fig


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
