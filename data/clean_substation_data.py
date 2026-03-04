import pandas as pd

buses = pd.read_csv("data/raw/gb_buses.csv")

buses_clean = buses[buses['symbol'] == 'Substation']
buses_clean = buses_clean[buses_clean['under_construction'] == False]

buses_clean.to_csv("data/clean_data/gb_buses_clean.csv", index=False)