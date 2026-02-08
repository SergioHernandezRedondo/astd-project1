
## Introduction

This project presents an interactive data visualization dashboard for the analysis of CO₂ emissions, developed as part of a data visualization and analytics assignment. The dashboard is built using Python and Dash and explores official emissions data provided in the file CO2.xlsx.

## Goal of the project

The main objective of the project is to enable an intuitive exploration of spatio-temporal CO₂ emission patterns, including comparisons by country, sector, and year. Through interactive maps, charts, and comparative visualizations, the dashboard allows users to identify trends, disparities, and key contributors to global CO₂ emissions.


## Dataset Description

The dataset used in this project is provided in the Excel file CO2.xlsx and contains historical data on CO₂ emissions by country, sector, and year.
Each row in the dataset represents a specific country and sector, identified by the following columns:

Sector: Economic sector responsible for the emissions (e.g. Power Industry,transports, buildings...).

ISOcode: Three-letter ISO country code.

Country: Full country name.

Year columns: Numerical values representing CO₂ emissions for each year (1970-2021).

This structure supports spatio-temporal analysis as well as sectoral comparisons, making the dataset suitable for advanced interactive visualizations.

## Project structure


├── .idea/

│   └── IDE configuration files

├── data/

│   └── CO2.xlsx              # Dataset provided by ALLSTAT

├── main/

│   └── source/

│       ├── utils/

│       │   └── utility functions for data processing and statistics

│       └── app.py            # Main Dash application

├── guide.md                  # Usage and navigation guide for the dashboard

└── README.md                 # Project documentation

The dashboard is developed using Dash, a Python framework designed for creating interactive data visualization web applications.

## Dashboard Features

## Minimum requirements

1. Exploration/visualization of the data.
  1. All the data must be visualized/explored somehow.
  2. At least three different types of graphics must be used.
  3. At least one non-basic graphic must be used (histograms, scatter-plots, pie-charts, box-plots etc. are basic).

2. Compilation of results.
  1. All results (tables, graphics, etc.) must be shown in a dashboard.

## Deadline

**February 08th 2026 at 23:55 via eGELA**
