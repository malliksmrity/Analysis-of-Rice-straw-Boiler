"""Rice straw boiler: efficiency from load and excess air (formula and a random forest)."""
import matplotlib
matplotlib.use("Agg")
import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

STOICH_AFR = 3.6479
FEATS = ["Load (%)", "Excess Air (%)", "Air Flow Rate (kg/hr)", "O2 in Flue Gas (%)"]
df = pd.read_csv("boiler_dataset.csv")
rf = RandomForestRegressor(random_state=42, n_jobs=1).fit(df[FEATS], df["Combustion Efficiency (%)"])


def row(load, ea):
    fuel = 2000 + (load - 60) * 30
    return [load, ea, STOICH_AFR * (1 + ea / 100) * fuel, ea / (ea + 100) * 21]


def formula(o2):
    return 100 - (0.8 * o2 + 1)


def run(load, ea):
    r = row(load, ea)
    f, m = formula(r[3]), float(rf.predict(pd.DataFrame([r], columns=FEATS))[0])
    grid = np.arange(30, 80.5, 0.5)
    rows = pd.DataFrame([row(load, g) for g in grid], columns=FEATS)
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.scatter(df["Excess Air (%)"].sample(300, random_state=1), df["Combustion Efficiency (%)"].sample(300, random_state=1), s=5, color="#8a8a82", label="generated samples")
    ax.plot(grid, formula(rows[FEATS[3]]), color="#0b5d6b", label="formula")
    ax.plot(grid, rf.predict(rows), "--", color="black", linewidth=1, label="random forest")
    ax.axvline(ea, color="#b35c1e", linewidth=1)
    ax.set_xlabel("Excess air (%)"); ax.set_ylabel("Efficiency (%)"); ax.legend(fontsize=8); fig.tight_layout()
    text = (f"Formula: {f:.2f} %. Random forest: {m:.2f} %. Air flow {r[2]:.0f} kg/h, oxygen {r[3]:.2f} %.\n"
            "In this model efficiency only falls as excess air rises, so the best value is the lowest tested (30 %). "
            "The formula has no loss for unburnt fuel, so this is not a real optimum.")
    return text, fig


demo = gr.Interface(run, [gr.Slider(60, 100, value=80, step=1, label="Boiler load (%)"), gr.Slider(30, 80, value=50, step=1, label="Excess air (%)")],
                    [gr.Textbox(label="Result"), gr.Plot(label="Efficiency against excess air")],
                    title="Rice straw boiler: combustion efficiency",
                    description="Generated data from a simplified combustion formula, not plant measurements. Code: github.com/malliksmrity/Analysis-of-Rice-straw-Boiler")
if __name__ == "__main__":
    demo.launch()
