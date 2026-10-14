# Rice straw boiler: combustion efficiency model

**In one sentence:** this project models how much of the fuel energy a rice-straw boiler turns into heat, depending on boiler load and the amount of extra air, and tests whether machine learning adds anything to the formula behind it.

Project page (charts and a small calculator): `docs/index.html`, served with GitHub Pages once Pages is enabled for the `/docs` folder.

## The question

Which air setting gives the best combustion efficiency, and can a machine-learning model replace or improve the physical formula?

## Who could benefit, and how

Operators of small biomass boilers, and students learning combustion, could use the formula and the checks as a starting point for thinking about air settings. This is a model on generated data, not a plant study, so it is not ready for operating decisions.

## Data and licence

- No measured data. `src/generate_dataset.py` creates 2,091 rows (seed 42) by sweeping load from 60 to 100 percent and excess air from 30 to 80 percent through the combustion formulas of the boiler design study (stoichiometric air-fuel ratio 3.6479, net calorific value 2609 kcal/kg).
- `src/generate_steam_dataset.py` makes a second table (load and feedwater flow). It rests on an assumption stated in its header, namely that flue-gas flow scales with fuel, and it is not used in the results below.
- Background work: boiler design and simulation study presented at RDME 2025 and in IJARSCT 2025 (author's own; full references to be added by the author).

## How it works

1. Generate rows from the formulas: air flow, oxygen in flue gas, and efficiency `100 - (0.8 * O2 + 1)` plus a little noise (standard deviation 0.15).
2. Train Random Forest, XGBoost and Gradient Boosting to predict efficiency from the four inputs.
3. Compare with the formula and with a straight-line model on a held-out 20 percent.
4. Extra checks: predict outside the training range, find the best excess air, repeat the split with other seeds.

## Results

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

## Limitations

- The labels come from the formula, so a good score only shows the models can copy it.
- The formula has no loss for unburnt fuel or carbon monoxide. Real boilers have an optimum above the lowest air setting. This model cannot find it.
- Tree-based models do not extrapolate. Use them only inside the range of the data.
- No measured plant data, no uncertainty from the input constants.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/generate_dataset.py
python src/benchmark_models.py
python src/boiler_evaluation.py   # writes reports/evaluation.json and docs/data.js
```

## What is coursework and what I extended

Personal project based on the author's published design study. Kept as written: the notebooks, the physics, the dataset and benchmark scripts. Extended in this cleanup: the seed and the data path in `generate_dataset.py`, the checks in `boiler_evaluation.py`, the corrected README and the static page.

## For technical readers

- `generate_dataset.py` now sets `np.random.seed(42)` and writes to `data/` (it used to write to the current folder, so `benchmark_models.py` could not find it).
- Because of the seed, the data and scores differ slightly from the first, unseeded run (`reports/model_comparison_original.csv`: forest R² 0.972).
- Models use default scikit-learn and XGBoost settings with `random_state=42`. Split: `train_test_split(test_size=0.2, random_state=42)`.
- The old `requirements.txt` was saved as UTF-16 and could not be read by pip. The new one is plain text with pinned versions.

## Repository layout

```
data/        boiler_dataset.csv, steam_dataset.csv
notebooks/   boiler_analysis.ipynb, Rice_straw_Boiler_project.ipynb
src/         generate_dataset.py, benchmark_models.py, boiler_evaluation.py,
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
