import pandas as pd

def open_totals_country(path = "../../data/CO2.xlsx", name = "fossil_CO2_totals_by_country"):
    return pd.read_excel(path, sheet_name=name)
def open_capita(path = "../../data/CO2.xlsx", name ="fossil_CO2_per_capita_by_countr"):
    return pd.read_excel(path, sheet_name=name)
def open_sector(path = "../../data/CO2.xlsx", name = "fossil_CO2_by_sector_and_countr"):
    return pd.read_excel(path, sheet_name=name)

def sum_co2_countries():
    """
    Suma toda la contaminación por cada país de los datos existentes
    :return: DataFrame (n, 2): primer elemento nombre pais, segundo elemento suma
    """
    df = open_totals_country()
    names = df["Country"]
    min_year, max_year, _ = get_years(df)
    suma = df.loc[:, min_year:max_year].sum(axis=1)

    return pd.concat([names, suma.rename("suma")], axis=1)

def sum_co2_all_countries():
    """
    Suma toda la contaminación de todos los paises en todos los años
    :return la suma total
    """
    df = sum_co2_countries()
    return df["suma"].sum()

def get_top5_countries():
    """
    Selecciona los 5 paises con más contaminación histórica, también añade otra fila con los demás países
    :return: DataFrame de los 5 paises con su contaminacion y los otros
    """
    df = sum_co2_countries()
    total = sum_co2_all_countries()

    top5 = df.nlargest(5, "suma")

    top5_sum = top5["suma"].sum()

    others = total - top5_sum

    new_line = pd.DataFrame({"Country": ["Others"], "suma": [others]})

    return pd.concat([top5, new_line], ignore_index = True)

def get_years(df):
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
    return min_year, max_year, years
