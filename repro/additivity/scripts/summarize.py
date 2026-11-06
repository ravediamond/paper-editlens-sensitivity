"""Summary statistics of PROTOCOL.md from expected/additivity.json (standard library and numpy)."""
import json
from pathlib import Path
import numpy as np

E = Path(__file__).resolve().parent.parent / "expected"


def summary(P):
    multi = [p for p in P if len(p["hunks"]) >= 2]
    D = np.array([p["D"] for p in multi]); Sm = np.array([p["S"] for p in multi])
    from scipy.stats import spearmanr
    out = {"paragraphs": len(P), "hunks": sum(len(p["hunks"]) for p in P), "multi": len(multi), "single": len(P) - len(multi),
           "mean_D": float(D.mean()), "mean_S": float(Sm.mean()), "pearson": float(np.corrcoef(D, Sm)[0, 1]),
           "spearman": float(spearmanr(D, Sm)[0]), "mean_abs_resid": float(np.abs(D - Sm).mean())}
    big = [max(p["hunks"], key=lambda h: abs(h["d"]))["d"] for p in multi]
    out["big_sign_share"] = float(np.mean([np.sign(b) == np.sign(p["D"]) for b, p in zip(big, multi)]))
    rng = np.random.default_rng(0); ty = {}
    for t in ("delete", "insert", "replace"):
        per = [[h["d"] for h in p["hunks"] if h["type"] == t] for p in P]
        flat = [x for v in per for x in v]
        if not flat:
            continue
        means = []
        for _ in range(2000):
            idx = rng.integers(len(P), size=len(P)); v = [x for i in idx for x in per[i]]
            if v:
                means.append(np.mean(v))
        ty[t] = {"n": len(flat), "mean": float(np.mean(flat)), "ci": [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]}
    out["by_type"] = ty
    return out


if __name__ == "__main__":
    s = summary(json.loads((E / "additivity.json").read_text()))
    (E / "additivity_summary.json").write_text(json.dumps(s, indent=1)); print(json.dumps(s, indent=1))
