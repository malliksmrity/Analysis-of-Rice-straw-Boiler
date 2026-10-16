"""BoilerSimEnv: live simulation. Pick a control policy, run a 12-hour shift, compare with the provable optimum."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import gradio as gr
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))
import boiler_env as b

RES = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
POLICIES = {"Fixed air": None, "O2 trim (hold oxygen at a set point)": None, "Moisture-aware (uses the noisy fuel hint)": b.moisture_aware()}


def run(policy, value, seed):
    pol = {"Fixed air": b.fixed_design(value), "O2 trim (hold oxygen at a set point)": b.o2_trim(value / 10.0), "Moisture-aware (uses the noisy fuel hint)": b.moisture_aware()}[policy]
    env = b.run_episode(pol, int(seed))
    sc = env.score()
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    x = range(1, b.STEPS + 1)
    ax[0].plot(x, env.water, color="#6b4c9a"); ax[0].set_title("Extra fuel water (kg per tonne)", fontsize=9)
    ax[1].plot(x, env.ea_hist, color="#0b5d6b", label="your policy"); ax[1].plot(x, [100 * b.ea_min(w) for w in env.water], "--", color="black", label="minimum air (assumed rule)")
    ax[1].set_title("Excess air (%)", fontsize=9); ax[1].legend(fontsize=7)
    ax[2].plot(x, env.eff_hist, color="#0b5d6b", label="your policy"); ax[2].plot(x, env.opt_hist, "--", color="black", label="provable optimum")
    ax[2].set_title("Efficiency (%)", fontsize=9); ax[2].legend(fontsize=7)
    for a in ax: a.set_xlabel("Step (30 min)")
    fig.tight_layout()
    text = (f"Mean efficiency {sc['mean_efficiency']} % against {sc['optimal_mean_efficiency']} % for the optimum (gap {sc['gap_points']} points), score {sc['score']}. "
            "The low-air penalty is a stylised assumption, not a measurement.")
    return text, fig


def table():
    return [[k, v["mean_efficiency"], v["mean_gap_points"], v["mean_score"]] for k, v in RES["policies"].items()]


with gr.Blocks(title="BoilerSimEnv") as demo:
    gr.Markdown("# BoilerSimEnv: air control for a rice-straw boiler\nThe physics is the heat-loss model built from the boiler design workbook (final-year project with Thermax). "
                "The fuel gets wetter and drier through a 12-hour shift; the agent sets the excess air every 30 minutes. A **stylised, unmeasured** rule adds losses when the air is too low, "
                "which makes the best setting provable. Code: github.com/malliksmrity/Analysis-of-Rice-straw-Boiler")
    with gr.Tab("Run a shift"):
        pol = gr.Dropdown(list(POLICIES), value="Fixed air", label="Policy")
        val = gr.Slider(20, 90, value=70, step=1, label="Fixed air in % (O2 trim: set point = value / 10 %)")
        sd = gr.Slider(0, 199, value=0, step=1, label="Scenario (random seed)")
        btn = gr.Button("Run")
        o, f = gr.Textbox(label="Result"), gr.Plot()
        btn.click(run, [pol, val, sd], [o, f])
    with gr.Tab("200 scenarios"):
        gr.Dataframe(headers=["Policy", "Mean efficiency (%)", "Gap to optimum (points)", "Mean score"], value=table())
if __name__ == "__main__":
    demo.launch()
