import pandas as pd

def open_totals_country(path = "../../../data/CO2.xlsx", name = "fossil_CO2_totals_by_country"):
    return pd.read_excel(path, sheet_name=name)
def open_capita(path = "../../../data/CO2.xlsx", name ="fossil_CO2_per_capita_by_countr"):
    return pd.read_excel(path, sheet_name=name)
def open_sector(path = "../../../data/CO2.xlsx", name = "fossil_CO2_by_sector_and_countr"):
    return pd.read_excel(path, sheet_name=name)

def sum_co2_countries():
    """
    Suma toda la contaminación por cada país de los datos existentes
    :return: matriz (n, 2): primer elemento nombre pais, segundo elemento suma
    """
    df = open_totals_country()
    names = df["Country"]

    suma = df.loc[:, 'B':'F'].sum(axis=1)

    return pd.concat([names, suma.rename("suma")], axis=1)

def sum_co2_all_countries():
    """
    Suma toda la contaminación de todos los paises en todos los años
    :return la suma total
    """
    df = sum_co2_countries()
    return df["suma"].sum()

def get_top5_countries():

    df = sum_co2_countries()
    total = sum_co2_all_countries()

    top5 = df.nlargest(5, "suma")

    top5_sum = top5["suma"].sum()

    others = total - top5_sum

    new_line = pd.DataFrame({"Country": ["Others"], "Suma": [others]})

    return pd.concat([top5, new_line], ignore_index = True)
