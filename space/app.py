"""Rice straw boiler: heat-loss efficiency model built from the design workbook."""
import matplotlib
matplotlib.use("Agg")
import gradio as gr
import matplotlib.pyplot as plt
import numpy as np

from heat_loss_model import efficiency


def run(excess_air, stack_c, unburnt):
    r = efficiency(excess_air / 100, t_stack_k=stack_c + 273.15, unburnt=unburnt)
    grid = np.arange(20, 91, 2)
    eff = [efficiency(g / 100, t_stack_k=stack_c + 273.15, unburnt=unburnt)["efficiency"] for g in grid]
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    ax[0].bar(["Useful", "Flue gas", "Unburnt", "Radiation"], [r["efficiency"], r["stack_loss"], r["unburnt_loss"], r["radiation_loss"]],
              color=["#0b5d6b", "#8a8a82", "#b35c1e", "#6b4c9a"])
    ax[0].set_ylabel("% of fuel heat")
    ax[1].plot(grid, eff, color="#0b5d6b")
    ax[1].axvline(excess_air, color="#b35c1e", linestyle="--")
    ax[1].set_xlabel("Excess air (%)")
    ax[1].set_ylabel("Efficiency (%)")
    fig.tight_layout()
    text = (f"Efficiency {r['efficiency']:.1f} %. Flue gas loss {r['stack_loss']:.1f} %, unburnt {r['unburnt_loss']:.1f} %, radiation {r['radiation_loss']:.1f} %. "
            f"Flue gas {r['flue_gas_kg_per_kg_fuel']:.2f} kg per kg fuel. Design point (70 % excess air, 200 C, 5.5 % unburnt): 81.3 %. "
            "The unburnt loss is an input here: the model has no penalty for too little air.")
    return text, fig


demo = gr.Interface(run, [gr.Slider(20, 90, value=70, step=1, label="Excess air (%)"), gr.Slider(140, 300, value=200, step=5, label="Stack temperature (C)"),
                          gr.Slider(2, 9, value=5.5, step=0.5, label="Unburnt loss (%)")],
                    [gr.Textbox(label="Result"), gr.Plot()], title="Rice straw boiler: heat-loss model",
                    description="Built from the boiler design workbook, a design calculation, not plant data. Code: github.com/malliksmrity/Analysis-of-Rice-straw-Boiler")
if __name__ == "__main__":
    demo.launch()
