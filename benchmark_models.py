"""
Benchmarks Random Forest, XGBoost, and Gradient Boosting on the
physics-grounded boiler dataset (data/boiler_dataset.csv), using a
proper train/test split so the comparison is actually meaningful.

Run generate_dataset.py first to create data/boiler_dataset.csv.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor

df = pd.read_csv("data/boiler_dataset.csv")

feature_cols = ["Load (%)", "Excess Air (%)", "Air Flow Rate (kg/hr)", "O2 in Flue Gas (%)"]
target_col = "Combustion Efficiency (%)"

X = df[feature_cols]
y = df[target_col]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Train rows: {len(X_train)} | Test rows: {len(X_test)}")

baseline_pred = 100 - (X_test["O2 in Flue Gas (%)"] * 0.8 + 1)
baseline_mae = mean_absolute_error(y_test, baseline_pred)
baseline_r2 = r2_score(y_test, baseline_pred)

results = [{
    "Model": "Physics formula (baseline)",
    "MAE": baseline_mae,
    "R2": baseline_r2
}]

models = {
    "Random Forest": RandomForestRegressor(random_state=42),
    "XGBoost": XGBRegressor(random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(random_state=42),
}

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    results.append({
        "Model": name,
        "MAE": mean_absolute_error(y_test, preds),
        "R2": r2_score(y_test, preds)
    })

comparison_df = pd.DataFrame(results)
print("\nModel comparison on held-out test data:")
print(comparison_df.to_string(index=False))
comparison_df.to_csv("model_comparison.csv", index=False)
print("\nSaved to model_comparison.csv")