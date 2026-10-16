"""Indirect-method (heat-loss) efficiency of the rice-straw boiler, built from the design workbook.

Inputs come from the Thermax-related design workbook (sheets 'composition', 'prop', 'economizer'):
  fuel per 1000 kg: C 318.6, H 31.7, O 275.7, N 18.2, S 1.7, moisture 150, ash 204 kg
  stoichiometric air 3647.92 kg per 1000 kg fuel (O2 26.5625 kmol, N2 99.9256 kmol)
  NCV 2609 kcal/kg, unburnt loss 5.5 %, radiation loss 1.6 %
  stack (economizer outlet) about 200 C, ambient 30 C, design excess air 70 %
  specific heat Cp = a + b T + c T^2 + d T^3 (J/mol K, T in kelvin), coefficients from sheet 'prop'

Efficiency = 100 - stack loss - unburnt loss - radiation loss (all in percent of the fuel heat).
The stack loss is the heat carried by all flue gas species from ambient to stack temperature,
integrating the Cp polynomials (so it includes the water vapour from fuel hydrogen and moisture).

What this model does NOT contain: a loss that grows when air is too low (carbon monoxide, more
unburnt carbon). The workbook keeps unburnt loss fixed at 5.5 percent. So the model can say how
much efficiency is gained by trimming excess air, but it cannot find the true optimum. Section
"optional CO loss" shows how an assumed low-air penalty would create one.

Run from the repo root:  python src/heat_loss_model.py     (needs numpy, pandas)
Writes reports/heat_loss.json and docs/heat_loss.js.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# kmol per 1000 kg fuel (sheet 'composition'), molar masses kg/kmol
CO2_K, H2O_K, SO2_K = 26.55, 24.183333, 0.053125
O2_STOICH, N2_STOICH = 26.5625, 99.925595
NCV_KCAL, KCAL_TO_KJ = 2609.0, 4.184
FUEL_KG = 1000.0
UNBURNT, RADIATION = 5.5, 1.6
T_AMB_K, T_STACK_K, EA_DESIGN = 303.15, 473.15, 0.70
# a, b, c, d for Cp in J/(mol K), T in K (sheet 'prop')
CP = {"CO2": (22.26, 0.05981, -3.501e-05, 7.469e-09), "H2O": (32.24, 0.001923, 1.055e-05, -3.595e-09),
      "N2": (28.90, -0.001571, 8.081e-06, -2.873e-09), "O2": (25.48, 0.0152, -7.155e-06, 1.312e-09),
      "SO2": (25.78, 0.05795, -3.812e-05, 8.612e-09)}


def heat_per_kmol(sp, t_from, t_to):
    """kJ per kmol of species sp heated from t_from to t_to (kelvin): integral of the Cp polynomial."""
    a, b, c, d = CP[sp]
    F = lambda T: a * T + b * T ** 2 / 2 + c * T ** 3 / 3 + d * T ** 4 / 4
    return F(t_to) - F(t_from)  # J/mol = kJ/kmol


def efficiency(ea=EA_DESIGN, t_stack_k=T_STACK_K, t_amb_k=T_AMB_K, moisture_extra_kg=0.0, ncv_kcal=NCV_KCAL,
               unburnt=UNBURNT, radiation=RADIATION, co_loss=0.0):
    """Return dict with the loss breakdown (percent of fuel heat) and efficiency. moisture_extra_kg is added
    water per 1000 kg fuel (fuel wetter than design). co_loss is an optional extra loss in percent."""
    h2o = H2O_K + moisture_extra_kg / 18.0
    n = {"CO2": CO2_K, "H2O": h2o, "SO2": SO2_K, "N2": N2_STOICH * (1 + ea), "O2": O2_STOICH * ea}
    q_stack = sum(k * heat_per_kmol(sp, t_amb_k, t_stack_k) for sp, k in n.items())  # kJ per 1000 kg fuel
    fuel_heat = FUEL_KG * ncv_kcal * KCAL_TO_KJ
    stack = 100 * q_stack / fuel_heat
    # NCV is defined per kg of fuel as fired; extra water lowers it by about 2.44 MJ/kg of water (latent heat)
    if moisture_extra_kg:
        stack = 100 * q_stack / (fuel_heat - moisture_extra_kg * 2442.0)
    total = stack + unburnt + radiation + co_loss
    flue_kg = sum(k * m for k, m in zip(n.values(), (44, 18, 64, 28, 32)))
    o2_dry = n["O2"] / (n["CO2"] + n["SO2"] + n["N2"] + n["O2"]) * 100
    return {"excess_air_pct": ea * 100, "stack_loss": stack, "unburnt_loss": unburnt, "radiation_loss": radiation,
            "co_loss": co_loss, "efficiency": 100 - total, "flue_gas_kg_per_kg_fuel": flue_kg / FUEL_KG, "o2_dry_pct": o2_dry, "o2_wet_pct": n["O2"] / sum(n.values()) * 100}


def main():
    design = efficiency()
    # 1. excess air sweep
    eas = np.arange(0.10, 0.901, 0.05)
    sweep = [efficiency(ea) for ea in eas]
    # 2. stack temperature, moisture, ambient sweeps
    stacks = [{"stack_c": t, "efficiency": efficiency(t_stack_k=t + 273.15)["efficiency"]} for t in range(140, 301, 20)]
    moist = [{"extra_water_kg_per_1000kg": m, "efficiency": efficiency(moisture_extra_kg=m)["efficiency"]} for m in range(0, 201, 25)]
    # 3. one-at-a-time sensitivity (tornado): efficiency change for a plausible swing
    base = design["efficiency"]
    tor = {
        "Excess air 50 % vs 90 %": (efficiency(0.5)["efficiency"], efficiency(0.9)["efficiency"]),
        "Stack temperature 180 vs 240 C": (efficiency(t_stack_k=453.15)["efficiency"], efficiency(t_stack_k=513.15)["efficiency"]),
        "Fuel wetter by 0 vs 100 kg water per t": (efficiency()["efficiency"], efficiency(moisture_extra_kg=100)["efficiency"]),
        "Unburnt loss 3.5 vs 7.5 %": (efficiency(unburnt=3.5)["efficiency"], efficiency(unburnt=7.5)["efficiency"]),
        "Radiation loss 1.0 vs 2.5 %": (efficiency(radiation=1.0)["efficiency"], efficiency(radiation=2.5)["efficiency"]),
        "Ambient 10 vs 40 C": (efficiency(t_amb_k=283.15)["efficiency"], efficiency(t_amb_k=313.15)["efficiency"]),
    }
    tornado = sorted([{"input": k, "high": round(v[0], 2), "low": round(v[1], 2), "swing": round(abs(v[0] - v[1]), 2)} for k, v in tor.items()],
                     key=lambda r: -r["swing"])
    # 4. Monte Carlo over uncertain inputs (assumed ranges, see README)
    rng = np.random.default_rng(42)
    N = 5000
    mc = [efficiency(ea=rng.uniform(0.55, 0.85), t_stack_k=273.15 + rng.normal(200, 15), moisture_extra_kg=max(0, rng.normal(0, 40)),
                     unburnt=rng.uniform(4.0, 7.0), radiation=rng.uniform(1.2, 2.0))["efficiency"] for _ in range(N)]
    mc_stats = {"n": N, "mean": round(float(np.mean(mc)), 2), "p5": round(float(np.percentile(mc, 5)), 2), "p95": round(float(np.percentile(mc, 95)), 2),
                "assumed_ranges": "excess air 55-85 % (uniform), stack 200 C +/- 15 (normal), extra fuel water 0-40 kg per t (half-normal), unburnt 4-7 %, radiation 1.2-2.0 %"}
    # 5. optional CO penalty: assumed extra loss that rises when excess air is below a threshold (ASSUMPTION, not from data)
    def co_pen(ea, thr, k=0.25):
        return max(0.0, (thr - ea) * 100) * k
    optional = {}
    for thr in (0.30, 0.40, 0.50):
        curve = [(round(ea * 100), round(efficiency(ea, co_loss=co_pen(ea, thr))["efficiency"], 2)) for ea in eas]
        best = max(curve, key=lambda x: x[1])
        optional[f"threshold_{int(thr*100)}"] = {"best_excess_air_pct": best[0], "best_efficiency": best[1]}

    out = {"design_point": {k: round(v, 2) for k, v in design.items()},
           "checks_against_workbook": {"flue_gas_kg_per_1000kg_fuel_model": round(design["flue_gas_kg_per_kg_fuel"] * 1000, 1), "workbook_6958_4": 6958.4,
                                       "o2_wet_pct_model": round(design["o2_wet_pct"], 2), "workbook_o2_vol_pct": 7.77, "o2_dry_pct_model": round(design["o2_dry_pct"], 2)},
           "monte_carlo": mc_stats, "tornado": tornado, "optional_co_penalty_assumption": optional,
           "sweep_excess_air": [{"ea": round(r["excess_air_pct"]), "stack": round(r["stack_loss"], 2), "efficiency": round(r["efficiency"], 2)} for r in sweep],
           "sweep_stack": [{k: round(v, 2) for k, v in r.items()} for r in stacks], "sweep_moisture": [{k: round(v, 2) for k, v in r.items()} for r in moist],
           "monte_carlo_hist": np.histogram(mc, bins=20)[0].tolist(), "monte_carlo_edges": [round(float(e), 2) for e in np.histogram(mc, bins=20)[1]]}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "heat_loss.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "heat_loss.js").write_text("window.HEAT = " + json.dumps(out) + ";\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("design_point", "checks_against_workbook", "monte_carlo", "tornado", "optional_co_penalty_assumption")}, indent=2))


if __name__ == "__main__":
    main()
