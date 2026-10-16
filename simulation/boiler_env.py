"""BoilerSimEnv: control the excess air of the rice-straw boiler through a shift.

The physics is the heat-loss model in src/heat_loss_model.py (built from the design workbook). One extra rule is a
STYLISED ASSUMPTION, not taken from the workbook and not measured: if the excess air is below a minimum that depends
on how wet the fuel is, unburnt/CO losses grow.

    ea_min      = 0.35 + 0.0015 * extra_water_kg_per_tonne        (35 % for the design fuel, wetter fuel needs more air)
    extra loss  = 0.25 percentage points of efficiency for every percentage point of excess air below ea_min

Under these two lines the best air setting at every step is exactly ea_min (stack loss falls with less air, the penalty
rises faster), so the optimum is provable and the agent is graded against it. Replace the rule with a measured curve
before drawing plant conclusions.

Episode: 24 steps of 30 minutes. The fuel moisture drifts (random walk, seeded). The agent sees the oxygen in the
flue gas (dry, %), the stack temperature (C), the previous efficiency and a noisy fuel-moisture hint. Action: the
excess air for the next step, 20 to 90 percent.

API: reset(seed) / step(excess_air_pct), tools: get_situation(), and score().
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))  # self-contained copy of heat_loss_model.py for the Space
from heat_loss_model import efficiency  # noqa: E402

EA_MIN_BASE, EA_MIN_PER_KG, PENALTY = 0.35, 0.0015, 0.25
STEPS = 24


def ea_min(extra_water):
    return EA_MIN_BASE + EA_MIN_PER_KG * extra_water


def step_efficiency(ea, extra_water, t_stack_c=200.0):
    """Efficiency in percent for one step, including the stylised low-air penalty."""
    pen = PENALTY * max(0.0, (ea_min(extra_water) - ea) * 100)
    return efficiency(ea, t_stack_k=t_stack_c + 273.15, moisture_extra_kg=extra_water, co_loss=pen)


class BoilerSimEnv:
    def reset(self, seed=0):
        self.rng = np.random.default_rng(seed)
        self.k, self.eff_hist, self.opt_hist, self.ea_hist = 0, [], [], []
        w = [float(np.clip(self.rng.normal(40, 25), 0, 120))]
        for _ in range(STEPS - 1):
            w.append(float(np.clip(w[-1] + self.rng.normal(0, 12), 0, 120)))
        self.water = w
        self.prev_eff = efficiency()["efficiency"]
        return self._obs(0.70)

    def _obs(self, ea):
        w = self.water[min(self.k, STEPS - 1)]
        e = efficiency(ea, t_stack_k=473.15, moisture_extra_kg=w)
        return {"step": self.k, "o2_dry_pct": round(e["o2_dry_pct"], 2), "stack_c": round(200 + float(self.rng.normal(0, 3)), 1),
                "prev_efficiency": round(self.prev_eff, 2), "moisture_hint_kg_per_t": round(w + float(self.rng.normal(0, 20)), 0)}

    def step(self, excess_air_pct):
        ea = float(np.clip(excess_air_pct, 20, 90)) / 100
        w = self.water[self.k]
        eff = step_efficiency(ea, w)["efficiency"]
        opt = step_efficiency(ea_min(w), w)["efficiency"]
        self.eff_hist.append(eff); self.opt_hist.append(opt); self.ea_hist.append(ea * 100)
        self.prev_eff = eff
        self.k += 1
        done = self.k >= STEPS
        return self._obs(ea), eff, done, {"optimal_efficiency": opt}

    def score(self):
        """1 = as good as the provable optimum; the gap is in efficiency points averaged over the shift."""
        gap = float(np.mean(np.array(self.opt_hist) - np.array(self.eff_hist)))
        return {"mean_efficiency": round(float(np.mean(self.eff_hist)), 2), "optimal_mean_efficiency": round(float(np.mean(self.opt_hist)), 2),
                "gap_points": round(gap, 2), "score": round(max(0.0, 1 - gap / 3.0), 3)}  # 3 points of gap = score 0

    def get_situation(self):
        return {"steps": STEPS, "minutes_per_step": 30, "action": "excess air in percent, 20 to 90", "sees": "oxygen in dry flue gas, stack temperature, previous efficiency, noisy moisture hint",
                "assumption": "low-air penalty rule, see module docstring"}


# --- policies --------------------------------------------------------------------------------
def fixed_design(ea=70.0):
    return lambda o, last: ea


def o2_trim(setpoint=6.0, gain=2.0):
    """Common practice: keep oxygen near a set point by moving the air a little each step."""
    return lambda o, last: float(np.clip(last + gain * (o["o2_dry_pct"] - setpoint) * -1, 20, 90))


def moisture_aware():
    """Uses the noisy moisture hint to aim just above the minimum air."""
    return lambda o, last: 100 * (ea_min(max(0.0, o["moisture_hint_kg_per_t"])) + 0.03)


def run_episode(policy, seed):
    env = BoilerSimEnv()
    o, last, done = env.reset(seed), 70.0, False
    while not done:
        last = policy(o, last)
        o, r, done, info = env.step(last)
    return env


def evaluate(policy, seeds=range(200)):
    s = [run_episode(policy, sd).score() for sd in seeds]
    return {"mean_efficiency": round(float(np.mean([x["mean_efficiency"] for x in s])), 2), "mean_gap_points": round(float(np.mean([x["gap_points"] for x in s])), 2),
            "mean_score": round(float(np.mean([x["score"] for x in s])), 3)}
