# Rice straw boiler: efficiency from a heat-loss model

**In one sentence:** this project works out how much of the fuel heat a rice-straw-fired boiler turns into steam, from its own design data, and shows which losses matter most.

Final-year B.Eng. project, done together with Thermax. Project page with charts and a calculator: `docs/index.html` (served with GitHub Pages once enabled for `/docs`). A small live app for Hugging Face Spaces is in `space/`.

## The question

At the design point, where does the fuel heat go, how sure can we be of the efficiency, and which input would change it most?

## Who could benefit, and how

Engineers and students working on biomass boilers could use the loss breakdown and the sensitivity ranking to decide where to look first (stack temperature, unburnt fuel). It is a design calculation, not a plant test, so it is not a basis for operating decisions.

## Data and licence

- **Design workbook** (author's own, Excel, sheets MAIN, composition, prop, furnace, settling chamber, convection bank, economizer): fuel analysis per 1000 kg (C 318.6, H 31.7, O 275.7, N 18.2, S 1.7, moisture 150, ash 204 kg), stoichiometric air 3647.9 kg, net calorific value 2609 kcal/kg, heat-capacity polynomials, a stack temperature of about 200 °C after the economizer, unburnt loss 5.5 % and radiation loss 1.6 %. The workbook is not in this repository. The numbers used are written into `src/heat_loss_model.py`.
- Earlier part: 2,091 generated rows (`src/generate_dataset.py`, seed 42) used to test machine learning. Details below.
- Background: boiler design and simulation study presented at RDME 2025 and in IJARSCT 2025 (full references to be added by the author).

## How it works

1. Burn the fuel on paper: carbon, hydrogen, sulphur and fuel moisture give CO2, water vapour and SO2; nitrogen and surplus oxygen come with the air.
2. Heat every flue gas species from 30 °C to the stack temperature, integrating the workbook's Cp polynomials (J/mol K, T in kelvin).
3. Efficiency = 100 − flue gas loss − unburnt loss − radiation loss, all as percent of the fuel heat.
4. Sweep the inputs, rank them one at a time, and run 5,000 random draws for an uncertainty range.

## Results (heat-loss model)

From `python src/heat_loss_model.py`, saved in `reports/heat_loss.json`.

- **Check against the workbook:** flue gas mass 6,958.4 kg per 1000 kg fuel (workbook: 6,958.4); oxygen in flue gas 7.77 % by volume (workbook: 7.77 %).
- **Design point** (70 % excess air, 200 °C stack): flue gas loss 11.62 %, unburnt 5.50 %, radiation 1.60 %, **efficiency 81.28 %**.
- **Sensitivity** (one input at a time): stack temperature 180 vs 240 °C moves efficiency by 4.2 points; unburnt loss 3.5 vs 7.5 % by 4.0; excess air 50 vs 90 % by 2.3; ambient 10 vs 40 °C by 2.0; radiation loss 1.0 vs 2.5 % by 1.5; 100 kg extra water per tonne of fuel by 0.6.
- **Uncertainty** (5,000 draws, ranges are my assumptions: excess air 55 to 85 % uniform, stack 200 ± 15 °C, extra fuel water 0 to 40 kg/t, unburnt 4 to 7 %, radiation 1.2 to 2.0 %): mean 81.15 %, 90 % range 78.71 to 83.56 %.
- **Excess air:** cutting it from 70 % to 50 % raises efficiency by 1.16 points on paper (82.44 %). The workbook keeps the unburnt loss fixed, so the model cannot show the penalty of too little air. `reports/heat_loss.json` also shows what an assumed low-air carbon-monoxide penalty would do. In that case the best air setting simply equals the assumed threshold, so it is an illustration and not a finding.

## What would make it stronger

- Compare with a commissioning or performance test of the real boiler.
- Replace the fixed unburnt loss by a measured or literature curve against excess air.
- Check the furnace sheet: heat generation there is 8.32 MW while 2,957 kg/h × 2,609 kcal/kg gives 8.97 MW.

## Limitations

- Design calculation with fixed unburnt and radiation losses, no measured plant data.
- Uncertainty ranges are assumptions.
- Efficiency here is the indirect (loss) method on the fuel net calorific value; the furnace, bank and economizer iteration of the workbook is used only for the stack temperature.

## Earlier part: does machine learning add anything?

`src/generate_dataset.py` made rows from a simplified formula (`efficiency = 100 - (0.8 * O2 + 1)` plus noise of 0.15), and the models learned it. This was a test of machine learning, and the answer is no: the labels come from a straight line, so nothing can beat that line, and trees fail outside the training range. Machine learning could still serve later as a fast stand-in for the slow furnace and economizer iteration.
### Machine-learning results

From `python src/benchmark_models.py` and `python src/boiler_evaluation.py` (see `reports/`). 419 test rows.

| Model | MAE (points) | R² |
|---|---|---|
| Always the average | 0.899 | -0.001 |
| Physics formula (it made the labels) | 0.125 | 0.977 |
| Linear regression, oxygen only | 0.124 | 0.977 |
| Random forest | 0.139 | 0.971 |
| XGBoost | 0.138 | 0.972 |
| Gradient boosting | 0.126 | 0.976 |

- Efficiency in the data runs from 91.24 to 95.43 percent.
- Random forest R² over 5 different splits: 0.975 on average, standard deviation 0.001.
- **Beyond the training range** (train on excess air up to 55 percent, test above): the three tree models have MAE of about 0.84. The linear model has 0.12 and the formula 0.118.
- **Best excess air:** both the formula and the random forest put it at 30 percent, the lowest value tested. Efficiency in this model never rises with more air.
- **Load:** the average efficiency differs by only 0.097 points between loads, which is noise. In this formula load has no effect on efficiency.

## Corrections to the earlier README

- It said the Random Forest reaches R² of about 0.98. The 0.98 is the formula itself. The forest gets 0.971.
- It said the best excess air is 40 to 50 percent. In this model it is the lowest tested value, 30 percent.
- It described the dashboard as trained on 2,000+ points. The Streamlit app used five hand-entered rows. It is now in `_archive/`.

### Limitations of the machine-learning part

- The labels come from the formula, so a good score only shows the models can copy it.
- The formula has no loss for unburnt fuel or carbon monoxide. Real boilers have an optimum above the lowest air setting. This model cannot find it.
- Tree-based models do not extrapolate. Use them only inside the range of the data.
- No measured plant data, no uncertainty from the input constants.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/heat_loss_model.py       # the main model: writes reports/heat_loss.json and docs/heat_loss.js
python src/generate_dataset.py
python src/benchmark_models.py
python src/boiler_evaluation.py   # writes reports/evaluation.json and docs/data.js
```

## What is coursework and what I extended

Final-year engineering project (with Thermax) and its design study. The design workbook and the thermal calculation are the author's own work. Kept as written: the notebooks, the physics, the dataset and benchmark scripts. Extended in this cleanup: the seed and the data path in `generate_dataset.py`, the checks in `boiler_evaluation.py`, the corrected README and the static page.

## For technical readers

- `generate_dataset.py` now sets `np.random.seed(42)` and writes to `data/` (it used to write to the current folder, so `benchmark_models.py` could not find it).
- Because of the seed, the data and scores differ slightly from the first, unseeded run (`reports/model_comparison_original.csv`: forest R² 0.972).
- Models use default scikit-learn and XGBoost settings with `random_state=42`. Split: `train_test_split(test_size=0.2, random_state=42)`.
- The old `requirements.txt` was saved as UTF-16 and could not be read by pip. The new one is plain text with pinned versions.

## Repository layout

```
data/        boiler_dataset.csv, steam_dataset.csv
notebooks/   boiler_analysis.ipynb, Rice_straw_Boiler_project.ipynb
src/         heat_loss_model.py, generate_dataset.py, benchmark_models.py, boiler_evaluation.py,
             generate_steam_dataset.py, rdme_fuel_composition.py
reports/     model_comparison.csv, evaluation.json, model_comparison_original.csv
docs/        static project page
_archive/    moved files: Streamlit app, notebook checkpoint, original README
```

Smrity Mallik, MSc AI and Data Science (Gisma, Berlin), B.Eng. Mechanical Engineering.
GitHub: github.com/malliksmrity. LinkedIn: linkedin.com/in/smritymallik.

## Process and automation

- `PROCESS.md`: backlog, definition of done and sprint rhythm for the next work (a plan, not past experience).
- `.github/workflows/ci.yml`: GitHub Actions check (written here, not yet run on GitHub).
- `Dockerfile`: container for the main script (not built or tested yet).

## Live model UI (Hugging Face Space)

`space/` is a ready-to-deploy Gradio app for a Hugging Face Space. Instructions in `space/README.md`. Not deployed yet: it needs your Hugging Face account.
