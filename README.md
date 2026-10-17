# Rice straw boiler: efficiency from a heat-loss model

Calculates how much fuel heat a rice-straw-fired boiler turns into steam, from its design data, and shows which losses matter most and how uncertain the result is. Final-year B.Eng. project, carried out with Thermax.

Live demo: https://huggingface.co/spaces/malliksmrity/boiler-sim-env


## 1. Problem
Straw is wet, ash-rich, and variable, so the efficiency of a biomass boiler is not obvious. The questions are where the fuel heat goes at the design point, which input changes efficiency most, and how uncertain the figure is.

## 2. Data
A design workbook (Excel) with the fuel analysis per 1,000 kg (C 318.6, H 31.7, O 275.7, N 18.2, S 1.7, moisture 150, ash 204 kg), net calorific value 2,609 kcal/kg, heat-capacity polynomials, a stack temperature of about 200 °C, an unburnt loss of 5.5 % and a radiation loss of 1.6 %. The workbook itself is not in the repository; its values are in `src/heat_loss_model.py`. A second, synthetic dataset (2,091 rows) was generated for a machine-learning comparison.

## 3. Approach
1. Burn the fuel on paper to get flue-gas composition and mass.
2. Heat each flue-gas species from 30 °C to the stack temperature by integrating the workbook's heat-capacity polynomials.
3. Efficiency = 100 % − flue-gas loss − unburnt loss − radiation loss.
4. Check flue-gas mass and oxygen against the workbook.
5. Vary inputs one at a time, then run 5,000 random draws for an uncertainty range.

## 4. Results
- Match with the workbook: flue gas 6,958.4 kg per 1,000 kg fuel (workbook 6,958.4); oxygen 7.77 % by volume (workbook 7.77 %).
- Design point (70 % excess air, 200 °C stack): flue-gas loss 11.62 %, unburnt 5.50 %, radiation 1.60 %, **efficiency 81.3 %**.
- Monte Carlo (5,000 draws over assumed ranges): mean 81.2 %, 90 % range 78.7 to 83.6 %.
- Largest effects on efficiency, one input at a time: stack temperature 180 vs 240 °C (4.2 points), unburnt loss 3.5 vs 7.5 % (4.0), excess air 50 vs 90 % (2.3).
- Machine learning added nothing: tree models matched a straight line through the oxygen value, because the synthetic labels come from a straight-line formula, and they extrapolate worse outside the training range.

## 5. Technical notes
- Heat to flue gas: sum of n_i × ∫ Cp_i(T) dT from 303.15 K to the stack temperature, Cp = a + bT + cT² + dT³ with coefficients from the workbook.
- Monte Carlo ranges are assumptions: excess air 55 to 85 % (uniform), stack 200 ± 15 °C (normal), extra fuel water 0 to 40 kg/t, unburnt 4 to 7 %, radiation 1.2 to 2.0 %; seed 42.
- Reproduce: `pip install -r requirements.txt`, then `python src/heat_loss_model.py`.

## 6. Validation and limitations
- Not validated against measured plant data in this repository. The model reproduces the design workbook, which checks the arithmetic, not real-world accuracy.
- For context only: Thermax lists 74 % for its HuskPac Ultra rice-husk boiler (different boiler and fuel, heating-value basis not stated); a published bagasse-boiler heat-loss study reports 56 %.
- Unburnt and radiation losses are fixed inputs, so the model cannot show the penalty of too little air.
- The 3D plant in the demo is illustrative.

## 7. Deployment
| Item | Status |
|---|---|
| Static page (GitHub Pages, `/docs`) | live |
| Hugging Face static Space (3D simulator) | live |
| CI (GitHub Actions) | passing |

Smrity Mallik, B.Eng. Mechanical Engineering; MSc AI and Data Science (Gisma, Berlin).

