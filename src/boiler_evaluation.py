"""Extra checks for the rice-straw boiler efficiency models.

The dataset is generated from a formula (see generate_dataset.py):
    O2 = EA / (EA + 100) * 21
    efficiency = 100 - (0.8 * O2 + 1) + noise(0, 0.15)
so the "physics formula" is the rule that created the labels. These checks ask:
  1. Is a machine-learning model needed at all? (linear baseline)
  2. What happens when the model must predict outside the range it was trained on?
  3. Where is the "optimal" excess air, and is that a real optimum?
  4. Is the random-split score stable across seeds?

Run from the repo root (after src/generate_dataset.py):  python src/boiler_evaluation.py
Writes reports/evaluation.json and docs/data.js.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
FEATS = ["Load (%)", "Excess Air (%)", "Air Flow Rate (kg/hr)", "O2 in Flue Gas (%)"]
TARGET = "Combustion Efficiency (%)"
STOICH_AFR = 3.6479


def formula(o2):
    return 100 - (0.8 * o2 + 1)


def models(seed=42):
    return {"Linear regression (all 4 inputs)": LinearRegression(),
            "Random forest": RandomForestRegressor(random_state=seed, n_jobs=1),
            "XGBoost": XGBRegressor(random_state=seed, n_jobs=1),
            "Gradient boosting": GradientBoostingRegressor(random_state=seed)}


def score(y, p):
    return {"mae": round(float(mean_absolute_error(y, p)), 3), "r2": round(float(r2_score(y, p)), 3),
            "rmse": round(float(np.sqrt(np.mean((np.asarray(y) - p) ** 2))), 3)}


def main():
    df = pd.read_csv(ROOT / "data" / "boiler_dataset.csv")
    y = df[TARGET]
    noise_sd = float((y - formula(df["O2 in Flue Gas (%)"])).std())

    # 1. random split, with baselines
    Xtr, Xte, ytr, yte = train_test_split(df[FEATS], y, test_size=0.2, random_state=42)
    rows = [dict(model="Always the average", **score(yte, DummyRegressor().fit(Xtr, ytr).predict(Xte))),
            dict(model="Physics formula (made the labels)", **score(yte, formula(Xte["O2 in Flue Gas (%)"])))]
    lin1 = LinearRegression().fit(Xtr[["O2 in Flue Gas (%)"]], ytr)
    rows.append(dict(model="Linear regression (O2 only)", **score(yte, lin1.predict(Xte[["O2 in Flue Gas (%)"]]))))
    for name, m in models().items():
        rows.append(dict(model=name, **score(yte, m.fit(Xtr, ytr).predict(Xte))))

    # 2. extrapolation: train on low excess air, test on higher excess air
    ex_tr, ex_te = df[df["Excess Air (%)"] <= 55], df[df["Excess Air (%)"] > 55]
    extrap = []
    for name, m in models().items():
        m.fit(ex_tr[FEATS], ex_tr[TARGET])
        extrap.append(dict(model=name, **score(ex_te[TARGET], m.predict(ex_te[FEATS]))))
    extrap.append(dict(model="Physics formula (made the labels)", **score(ex_te[TARGET], formula(ex_te["O2 in Flue Gas (%)"]))))

    # 3. where is the best excess air?  (formula and random forest trained on all data, load 80 %)
    grid = np.arange(30, 80.5, 0.5)
    fuel = 2000 + (80 - 60) * 30
    g = pd.DataFrame({"Load (%)": 80.0, "Excess Air (%)": grid,
                      "Air Flow Rate (kg/hr)": STOICH_AFR * (1 + grid / 100) * fuel,
                      "O2 in Flue Gas (%)": grid / (grid + 100) * 21})
    rf_all = RandomForestRegressor(random_state=42, n_jobs=1).fit(df[FEATS], y)
    curve_f, curve_rf = formula(g["O2 in Flue Gas (%)"]), rf_all.predict(g[FEATS])
    optimum = {"formula_best_excess_air": float(grid[int(np.argmax(curve_f))]),
               "random_forest_best_excess_air": float(grid[int(np.argmax(curve_rf))]),
               "searched_range": [30, 80]}

    # 4. does load matter in this data set?
    load_effect = float(df.groupby("Load (%)")[TARGET].mean().max() - df.groupby("Load (%)")[TARGET].mean().min())

    # 5. stability over 5 random splits
    r2s = []
    for sd in range(1, 6):
        a, b, c, d = train_test_split(df[FEATS], y, test_size=0.2, random_state=sd)
        r2s.append(r2_score(d, RandomForestRegressor(random_state=sd, n_jobs=1).fit(a, c).predict(b)))

    out = {"rows": int(len(df)), "efficiency_min": round(float(y.min()), 2), "efficiency_max": round(float(y.max()), 2),
           "label_noise_sd": round(noise_sd, 3), "random_split": rows, "extrapolation_excess_air_above_55": extrap,
           "optimum": optimum, "mean_efficiency_spread_across_loads": round(load_effect, 3),
           "rf_r2_over_5_splits": {"mean": round(float(np.mean(r2s)), 3), "std": round(float(np.std(r2s)), 3)}}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "evaluation.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    sample = df.sample(150, random_state=42)
    page = dict(out, curve={"excess_air": grid.tolist(), "formula": curve_f.round(3).tolist(), "random_forest": np.round(curve_rf, 3).tolist()},
                points={"excess_air": sample["Excess Air (%)"].tolist(), "efficiency": sample[TARGET].round(3).tolist()},
                constants={"stoich_afr": STOICH_AFR, "fuel_base": 2000, "fuel_per_load": 30})
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "data.js").write_text("window.PAGE_DATA = " + json.dumps(page) + ";\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
