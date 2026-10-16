"""Score control policies in BoilerSimEnv over 200 seeded shifts.  Run from the repo root: python simulation/evaluate.py"""
import json
from pathlib import Path

import boiler_env as b

P = {"Fixed 70 % (design point)": b.fixed_design(70), "Fixed 50 %": b.fixed_design(50), "Fixed 90 %": b.fixed_design(90),
     "O2 trim, set point 6 %": b.o2_trim(6.0), "O2 trim, set point 4 %": b.o2_trim(4.0), "Moisture-aware (noisy hint)": b.moisture_aware()}
out = {"scenarios": 200, "policies": {k: b.evaluate(v) for k, v in P.items()},
       "assumption": "low-air penalty rule in boiler_env.py is stylised, not measured; optimum = minimum air under that rule"}
(Path(__file__).resolve().parent / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
for k, v in out["policies"].items():
    print(f"{k:30s} {v}")
