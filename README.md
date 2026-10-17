# Rice straw boiler: efficiency from a heat-loss model

**In one sentence:** this project works out how much of the fuel heat a rice-straw-fired boiler turns into steam, from its own design data, and shows which losses matter most and how sure the answer is.

Final-year B.Eng. project, done together with Thermax. Live page with charts and a calculator: `docs/index.html` (GitHub Pages, folder `/docs`). Live app for Hugging Face Spaces: `space/`.

## 1. Problem

A biomass boiler burns agricultural waste (rice straw) to make steam. Straw is wet, ash-rich and variable, so efficiency is not obvious. Operators and designers need to know: **where does the fuel heat go at the design point, which input would change the efficiency most, and how uncertain is the number?** A second question from the first version of this project: does machine learning add anything to the physics?

Who could use it: engineers and students working on biomass boilers (plausible uses, not tested). It is a design calculation, not a plant test.

## 2. Dataset

- **Design workbook** (the author's own Excel file, sheets MAIN, composition, prop, furnace, settling chamber, convection bank, economizer): fuel analysis per 1000 kg (C 318.6, H 31.7, O 275.7, N 18.2, S 1.7, moisture 150, ash 204 kg), stoichiometric air 3647.9 kg, net calorific value 2609 kcal/kg, heat-capacity polynomials, stack temperature about 200 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°C after the economizer, unburnt loss 5.5 %, radiation loss 1.6 %. The workbook is not in the repository; the numbers are written into `src/heat_loss_model.py`.
- **Generated data for the machine-learning test:** 2,091 rows (`src/generate_dataset.py`, seed 42), load 60 to 100 percent, excess air 30 to 80 percent, from a simplified efficiency formula plus noise.
- Background: boiler design and simulation study presented at RDME 2025 and in IJARSCT 2025 (full references to be added by the author).

## 3. How I solved it

1. Burn the fuel on paper: carbon, hydrogen, sulphur and moisture give CO2, water vapour and SO2; nitrogen and surplus oxygen come with the air.
2. Heat every flue gas species from 30 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°C to the stack temperature by integrating the workbook's heat-capacity polynomials.
3. Efficiency = 100 ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã¢â‚¬Â¹ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ flue gas loss ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã¢â‚¬Â¹ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ unburnt loss ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã¢â‚¬Â¹ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ radiation loss (percent of the fuel heat).
4. Check the result against the workbook (flue gas mass and oxygen share).
5. Sweep inputs, rank them one at a time, and run 5,000 random draws for an uncertainty range.
6. Separately, test whether machine learning can add anything.

## 4. Findings

- **Check against the workbook:** flue gas mass 6,958.4 kg per 1000 kg fuel (workbook 6,958.4); oxygen 7.77 % by volume (workbook 7.77 %).
- **Design point** (70 % excess air, 200 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°C stack): flue gas loss 11.62 %, unburnt 5.50 %, radiation 1.60 %, **efficiency 81.28 %**.
- **What matters most** (change in efficiency over a plausible range, one input at a time): stack temperature 180 vs 240 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°C: 4.2 points; unburnt loss 3.5 vs 7.5 %: 4.0; excess air 50 vs 90 %: 2.3; ambient 10 vs 40 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°C: 2.0; radiation 1.0 vs 2.5 %: 1.5; 100 kg extra fuel water per tonne: 0.6.
- **Uncertainty:** 5,000 draws over assumed input ranges give a mean of 81.15 % and a 90 % range of 78.71 to 83.56 %.
- **Excess air:** cutting it from 70 to 50 percent raises efficiency by 1.16 points on paper. The workbook keeps the unburnt loss fixed, so the model cannot show the penalty of too little air. `reports/heat_loss.json` shows what an assumed carbon-monoxide penalty would do; then the best air setting simply equals the assumed threshold, so that is an illustration and not a finding.
- **Machine learning added nothing here:** random forest MAE 0.139, XGBoost 0.138, gradient boosting 0.126 against a straight line through the oxygen value, 0.124, because the labels come from a straight line. Outside the training range (train up to 55 % excess air, test above) the tree models' error is 0.84 against 0.12.
- **Check the furnace sheet:** heat generation there is 8.32 MW while 2,957 kg/h ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â 2,609 kcal/kg gives 8.97 MW.

## 5. Models used

| Part | Model | Role |
|---|---|---|
| Main | indirect heat-loss (energy balance) model with polynomial heat capacities | the engineering result |
| Uncertainty | Monte Carlo (5,000 draws, uniform and normal inputs) | range of the efficiency |
| Test | Random forest, XGBoost, gradient boosting, linear regression | does ML add to the physics? (no) |

Earlier machine-learning scores (419 held-out rows): average guess MAE 0.899, formula 0.125, linear (oxygen only) 0.124, random forest 0.139, XGBoost 0.138, gradient boosting 0.126. Random forest RÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â² over five splits 0.975 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â± 0.001.

## 6. Technical documentation

- Heat to the flue gas: `ÃƒÆ’Ã†â€™Ãƒâ€¦Ã‚Â½ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â£ n_i ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã¢â‚¬Â¹ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â« Cp_i(T) dT` from 303.15 K to the stack temperature, `Cp = a + bT + cTÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â² + dTÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â³` in J/(mol K), T in kelvin, coefficients from sheet `prop`.
- Moles per 1000 kg fuel: CO2 26.55, H2O 24.183, SO2 0.0531, N2 99.9256 ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â (1 + EA), O2 26.5625 ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â EA.
- Fuel heat = 1000 kg ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â 2609 kcal/kg ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â 4.184. Extra fuel water lowers the heat by 2.442 MJ per kg of water.
- Monte Carlo ranges are my assumptions: excess air 55 to 85 % uniform, stack 200 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â± 15 ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°C normal, extra fuel water 0 to 40 kg/t half-normal, unburnt 4 to 7 %, radiation 1.2 to 2.0 %. Seed 42.
- Limits: fixed unburnt and radiation losses; no measured plant data; the furnace, bank and economizer iteration of the workbook is used only for the stack temperature.
- To make it stronger: compare with a commissioning test; replace the fixed unburnt loss by a measured curve against excess air.
- Reproduce: `pip install -r requirements.txt`; `python src/heat_loss_model.py` (main); `python src/generate_dataset.py`, `python src/benchmark_models.py`, `python src/boiler_evaluation.py` (machine-learning test).
- The first version's README claimed forest RÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â² of about 0.98 (that was the formula itself; the forest gets 0.971), a best excess air of 40 to 50 percent (the earlier model and the formula put it at the lowest tested value, 30 percent), and a dashboard trained on 2,000+ points (it used five typed rows).
- `generate_dataset.py` is seeded and writes to `data/`. The old UTF-16 `requirements.txt` was replaced.

## 7. Output

- Static page with the loss breakdown, excess-air curve, sensitivity ranking, Monte Carlo histogram and an in-browser calculator: `docs/index.html`.
- Live app: `space/app.py` (Gradio), same model.
- Results: `reports/heat_loss.json`, `reports/evaluation.json`, `reports/model_comparison.csv`.

## 7a. How far can the efficiency be trusted?

**Plant check by the project guide (Thermax), October 2026.** When asked, the project guide confirmed that the real boiler's stack temperature, flue-gas oxygen, fuel rate and steam flow are the same as the values calculated in the design workbook, and rated the model's match to the real boiler at about 90 %. This is the guide's confirmation: the plant readings belong to Thermax and are not in this repository, so I cannot show or repeat the comparison from here. What I could check independently: What I could check independently:

- **Against the design workbook:** flue gas (6,958.4 kg per 1,000 kg fuel) and oxygen (7.77 % wet) match the workbook exactly. This proves the arithmetic, not the real-world accuracy.
- **Against published figures:** Thermax lists 74 % efficiency for its HuskPac Ultra rice-husk boiler ([Thermax product page](https://websitenp.thermaxglobal.com/industrial-products/process-heat-solutions/steam-boilers/huskpac-ultra)); the page does not say what fuel heating-value basis that figure uses, and it is a different boiler and fuel. A published heat-loss study of a bagasse boiler found 56 % ([AGRIS record](https://agris.fao.org/search/ar/records/6473a35a96fdec8b71b460ba)). Our model gives 81.3 % at the design point (78.7 to 83.6 % in the Monte Carlo range), above both, but it uses a design fuel analysis with 5.5 % unburnt and 1.6 % radiation loss taken as assumptions.
- **What this means:** a figure in the 75 to 85 % range is plausible for a well-run biomass boiler at design load, and part-load or wetter fuel would lower it. Treat 81.3 % as a design-point estimate. The guide's agreement of 80 to 90 % with the plant supports it, but a public, reproducible validation would need the measured stack O2, stack temperature, fuel rate and steam output, which cannot be published here.
## 8. Deployment

**Live (Hugging Face static Spaces):** https://huggingface.co/spaces/malliksmrity/boiler-sim-env (simulation) and https://huggingface.co/spaces/malliksmrity/rice-straw-boiler (model page)

**Simulation environment (simulation/):** BoilerSimEnv runs the heat-loss model through a 12-hour shift with drifting fuel moisture; the agent sets the excess air each 30 minutes and is graded against a provable optimum. A stylised, unmeasured low-air penalty rule makes the optimum definite. Over 200 shifts: fixed 70 % design setting is 1.65 efficiency points from the optimum, an O2 trim at 6 % 0.66, a moisture-aware policy 0.23. Live Gradio app, Space-ready, not yet deployed.

| What | How | Status |
|---|---|---|
| Static page | GitHub Pages, folder `/docs` | needs enabling |
| Live app | Hugging Face Space (Gradio), folder `space/`, steps in `space/README.md` | not deployed (needs your account) |
| Container | `Dockerfile` runs `src/boiler_evaluation.py` | written, not built |
| CI | `.github/workflows/ci.yml` | written, not yet run on GitHub |
| Process | `PROCESS.md` | plan, not past experience |

## Coursework and extensions

Final-year engineering project (with Thermax) and its design study. The design workbook and the thermal calculation are the author's own. Extended in the cleanup: the heat-loss model and its checks, the seeded dataset scripts, the corrected README, the static page and Space app. Your college has approved publishing coursework (results pending).

```
data/        boiler_dataset.csv, steam_dataset.csv
notebooks/   boiler_analysis.ipynb, Rice_straw_Boiler_project.ipynb
src/         heat_loss_model.py, generate_dataset.py, benchmark_models.py, boiler_evaluation.py, generate_steam_dataset.py, rdme_fuel_composition.py
reports/     heat_loss.json, evaluation.json, model_comparison.csv, model_comparison_original.csv
docs/        static project page
space/       Hugging Face Space app
_archive/    moved files: Streamlit app, notebook checkpoint, original README
```

Smrity Mallik, MSc AI and Data Science (Gisma, Berlin), B.Eng. Mechanical Engineering. GitHub: github.com/malliksmrity. LinkedIn: linkedin.com/in/smritymallik.
