# Rice Straw Boiler Combustion Optimization Tool 

An ML-driven decision-support system for a rice-straw-fired boiler, predicting 
and optimizing combustion efficiency. Built on design and simulation research 
published at RDME-2025 and IJARSCT 2025.

##  Live Demo
 [Open the Dashboard](https://analysis-of-rice-straw-boiler-6hp89keqegbvvzddwryd37.streamlit.app/)

##  Project Overview
- Modeled boiler performance across 60–100% load conditions using first-principles 
  combustion physics (stoichiometric air-fuel ratio, excess air, heat balance)
- Generated a physics-grounded training dataset (2,000+ data points) instead of 
  relying on limited historical samples
- Built and validated a Random Forest model against the underlying physics formula 
  as a baseline (R² ≈ 0.98 on held-out test data), confirming the model correctly 
  learns the combustion relationship rather than overfitting
- Extended modeling to a second controllable variable — water flow rate — capturing 
  feedwater/steam behavior for future multi-variable optimization
- Deployed an interactive dashboard with real-time parameter sliders and an 
  optimization recommendation feature

## Tech Stack
Python · Pandas · Scikit-learn · Streamlit · Matplotlib · Jupyter

##  Key Findings
- Combustion efficiency ranges ~91–95.5% across the modeled load/excess-air space
- Optimal excess air: ~40–50% for maximum efficiency
- O₂ in flue gas is the primary driver of combustion efficiency in the model
- Model performance validated against physics ground truth, not just fit to data

## 🧪 Methodology & Validation
Rather than training on a handful of historical readings, this project generates 
training data directly from the combustion physics formulas used in the underlying 
simulation research. This produces a much larger, physically consistent dataset 
and allows the model to be validated against a known-correct baseline (the physics 
formula itself) — a proper train/test split shows the model matches the physics 
baseline closely, confirming it has learned the real relationship rather than 
memorizing a small sample.

## 👩‍💻 Author
**Smrity Mallik** | MSc AI & Data Science | Published Researcher — RDME-2025, IJARSCT 2025
