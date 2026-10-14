"""
Generates a second dataset from the Steam Load section of your simulation
notebook, varying Load (%) AND Water Flow Rate (kg/s) — the two variables
that genuinely produce different outcomes in your formulas.

ASSUMPTION TO VERIFY: your notebook's steam-load section used fixed
constants (flue_gas_mass_flow, flue_gas_inlet_temp) derived at one
specific operating point (~2957 kg/hr fuel). To vary this with Load,
flue gas mass flow and available heat are scaled proportionally to
fuel quantity at each load level. This is a reasonable engineering
approximation but not something your original notebook validated —
flag this in any writeup, and correct the scaling if you have better
data on how flue gas flow actually changes with load.
"""

import numpy as np
import pandas as pd

NCV = 2609
kcal_to_watts = 4184 / 3600
cpg = 1131.62145
cpw = 4186
overall_UA = 6461.348722
LMTD = 203.760684
economy_efficiency = 0.7
latent_heat_steam = 2257000
water_inlet_temp = 50

baseline_fuel_qty = 2957
baseline_flue_gas_flow = 5.71551822

load_range = np.arange(60, 100.5, 2)
water_flow_range = np.arange(1.0, 5.05, 0.1)

rows = []
for load in load_range:
    fuel_qty = 2000 + (load - 60) * 30
    flue_gas_mass_flow = baseline_flue_gas_flow * (fuel_qty / baseline_fuel_qty)

    for water_flow in water_flow_range:
        Q_gas = flue_gas_mass_flow * cpg * (389.0484 - 200)
        Q_UA = overall_UA * LMTD
        Q_effective = min(Q_gas, Q_UA) * economy_efficiency

        delta_T_water = Q_effective / (water_flow * cpw)
        feedwater_outlet_temp = water_inlet_temp + delta_T_water

        steam_load = Q_effective / latent_heat_steam

        rows.append({
            "Load (%)": load,
            "Water Flow Rate (kg/s)": round(water_flow, 2),
            "Feedwater Outlet Temp (C)": feedwater_outlet_temp,
            "Steam Load (kg/s)": steam_load,
        })

df = pd.DataFrame(rows)
df.to_csv("data/steam_dataset.csv", index=False)

print(f"Generated {len(df)} rows.")
print(df.describe())
print("\nSaved to data/steam_dataset.csv")