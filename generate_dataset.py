"""
Generates a physics-grounded dataset for the Rice Straw Boiler project
by sweeping Load (%) and Excess Air (%) through the same formulas used
in your combustion simulation notebook.

Run this first, before benchmark_models.py or the Streamlit app changes.
Output: boiler_dataset.csv
"""

import numpy as np
import pandas as pd

# --- Constants from your simulation notebook ---
stoich_afr = 3.6479          # stoichiometric air-fuel ratio
NCV = 2609                   # kcal/kg
kcal_to_watts = 4184 / 3600  # conversion factor

# --- Sweep ranges ---
load_range = np.arange(60, 100.5, 1)        # 60% to 100%, step 1%
excess_air_range = np.arange(30, 80.5, 1)   # 30% to 80%, step 1%

rows = []
for load in load_range:
    fuel_qty = 2000 + (load - 60) * 30

    for excess_air in excess_air_range:
        actual_afr = stoich_afr * (1 + excess_air / 100)
        air_flow_rate = actual_afr * fuel_qty
        o2_pct = excess_air / (excess_air + 100) * 21

        combustion_eff = 100 - (o2_pct * 0.8 + 1)

        noise = np.random.normal(0, 0.15)
        combustion_eff = combustion_eff + noise

        rows.append({
            "Load (%)": load,
            "Excess Air (%)": excess_air,
            "Fuel Qty (kg/hr)": fuel_qty,
            "Air Flow Rate (kg/hr)": air_flow_rate,
            "O2 in Flue Gas (%)": o2_pct,
            "Combustion Efficiency (%)": combustion_eff,
        })

df = pd.DataFrame(rows)
df.to_csv("boiler_dataset.csv", index=False)

print(f"Generated {len(df)} rows.")
print(df.describe())
print("\nSaved to boiler_dataset.csv")
