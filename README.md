
## Introduction

This project presents an interactive data visualization dashboard for the analysis of CO₂ emissions, developed as part of a data visualization and analytics assignment. The dashboard is built using Python and Dash and explores official emissions data provided in the file CO2.xlsx.

## Goal of the project

The main objective of the project is to enable an intuitive exploration of spatio-temporal CO₂ emission patterns, including comparisons by country, sector, and year. Through interactive maps, charts, and comparative visualizations, the dashboard allows users to identify trends, disparities, and key contributors to global CO₂ emissions.

The dashboard offers a fully synchronized experience: by selecting a specific country on the map and adjusting the year slider, all charts update instantly to reflect that selection. This allows you to perform a deep-dive analysis of a nation's carbon footprint, comparing its sectoral distribution and historical trends against global benchmarks in real-time.


## Dataset Description

The dataset used in this project is provided in the Excel file CO2.xlsx and contains historical data on CO₂ emissions by country, sector, and year.
Each row in the dataset represents a specific country and sector, identified by the following columns:

Sector: Economic sector responsible for the emissions (e.g. Power Industry,transports, buildings...).

ISOcode: Three-letter ISO country code.

Country: Full country name.

Year columns: Numerical values representing CO₂ emissions for each year (1970-2021).


## Project structure

```
.
├── app.py              # Main Dash application entry point
├── assets/             # CSS styles and static images
├── data/               # Source dataset (CO2.xlsx)
├── utils/              # Helper functions for data processing and themes
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

## How to run the environment


This project is developed in Python and uses Dash to create an interactive web dashboard. To run the application locally, follow the steps below.

1. Create a virtual environment

From the root directory of the project, create a Python virtual environment to isolate dependencies:

```bash
python -m venv .venv
```
2. Activate the virtual environment

Activate the environment depending on your operating system:

Windows (CMD / PowerShell):
```bash
.venv\Scripts\activate
```

Linux / macOS:
```bash
source .venv/bin/activate
```

Once activated, the terminal prompt will show the name of the environment, indicating that it is active.

3. Install project dependencies

With the virtual environment activated, install the required Python packages:
```bash
pip install -r requirements.txt
```

If a requirements.txt file is not provided, the main dependencies are:

```
pandas
numpy
dash
plotly
```

These can be installed manually using:
```bash
pip install pandas numpy dash plotly
```
4. Run the Dash application

Navigate to the source directory and start the application:
```bash
python app.py
```
5. Access the dashboard



Once the application is running, open a web browser and go to:

http://127.0.0.1:8050


The interactive dashboard will be displayed, allowing exploration of CO₂ emissions by country, sector, and year.



## Dashboard features video

https://drive.google.com/file/d/17hFhgrMKqZXX_WGwGmQUiBSmc2PZJf0I/view?usp=sharing
