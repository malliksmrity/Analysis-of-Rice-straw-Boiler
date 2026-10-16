---
title: BoilerSimEnv
sdk: gradio
sdk_version: 6.30.0
app_file: app.py
pinned: false
---

# BoilerSimEnv: air control for a rice-straw boiler

A simulation environment on top of the heat-loss model built from the boiler design workbook (final-year project, with Thermax).

- **Episode:** 24 steps of 30 minutes. The fuel water content drifts (seeded random walk).
- **Observation:** oxygen in the dry flue gas, stack temperature, previous efficiency, a noisy fuel-moisture hint.
- **Action:** excess air for the next step, 20 to 90 percent.
- **Reward:** efficiency of the step (percent).
- **Grade:** gap to the provable optimum, averaged over the shift.
- **Assumption:** the workbook has no penalty for too little air, so a stylised rule adds one (see `boiler_env.py`). Under that rule the best setting is exactly the minimum air. This is **not measured**; replace it with a plant curve before drawing conclusions.

Files: `boiler_env.py`, `heat_loss_model.py` (copy of `src/`), `evaluate.py` (writes `results.json`), `app.py` (live app).

## Deploy (you do this, with your own Hugging Face account)

1. Create a new Space: SDK Gradio, free CPU.
2. Clone it and copy everything from this `simulation/` folder into it.
3. `git add . && git commit -m "first version" && git push`.

Run locally: `pip install -r requirements.txt` then `python app.py`.