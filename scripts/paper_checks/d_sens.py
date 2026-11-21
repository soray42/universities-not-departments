"""Sensitivity of H1/H2/D3 to OPEID6-pooled pay (Rutgers triplet; branch-pooled flagships) and to the added institutions.
Reads the cells written by c_headline.py (run it with 'repaired' and with 'v1' first)."""
import numpy as np, pandas as pd
from scipy.stats import rankdata, norm
S = str(__import__("pathlib").Path(__file__).resolve().parents[2]) + "/data/interim/paper_checks_"
R = str(__import__("pathlib").Path(__file__).resolve().parents[2]) + "/data/raw/"
cells = pd.read_csv(S + "cells_repaired.csv", dtype={"UNITID": str})
v1s = pd.read_csv(S + "main_sample_v1.csv", dtype={"UNITID": str})
fos = pd.read_csv(R + "scorecard_fos/Most-Recent-Cohorts-Field-of-Study.csv", usecols=["UNITID", "OPEID6"], dtype=str).drop_duplicates("UNITID")
nper = fos.groupby("OPEID6").UNITID.nunique()
pooled = set(fos[fos.OPEID6.map(nper) > 1].UNITID)

def sample(c):
    d = c.dropna(subset=["earnings", "F", "SAT_AVG", "ADM_RATE", "PCTPELL", "G"]); d = d[d.earnings > 0]
    while True:
        n0 = len(d)
        d = d[d.groupby("inst_key").field.transform("size") >= 2]
        d = d[d.groupby("field").inst_key.transform("size") >= 15]
        if len(d) == n0: break
    return d.sort_values(["field", "inst_key"]).reset_index(drop=True)

def blom(v):
    r = rankdata(v); return norm.ppf((r - 0.375) / (len(v) + 0.25))

def stats(d):
    y = np.log(d.earnings.to_numpy()); zF = np.empty(len(d)); zY = np.empty(len(d))
    for f, ix in d.groupby("field").indices.items():
        a = blom(d.F.to_numpy()[ix]); b = blom(y[ix])
        zF[ix] = (a - a.mean()) / a.std(ddof=1); zY[ix] = (b - b.mean()) / b.std(ddof=1)
    H1 = zF @ zY / np.sqrt((zF @ zF) * (zY @ zY))
    ic = pd.factorize(d.inst_key)[0]; fc = pd.factorize(d.field, sort=True)[0]
    Dm = np.hstack([np.eye(ic.max() + 1)[ic], np.eye(fc.max() + 1)[fc][:, 1:]])
    res = lambda v, X: v - X @ np.linalg.lstsq(X, v, rcond=None)[0]
    rF, rY = res(zF, Dm), res(zY, Dm); H2 = rF @ rY / np.sqrt((rF @ rF) * (rY @ rY))
    g = d.groupby("field"); Df = np.eye(fc.max() + 1)[fc]
    zFl = g.F.transform(lambda s: (s - s.mean()) / s.std()).to_numpy()
    cols = [Dm, zFl[:, None]]
    for c in ["SAT_AVG", "ADM_RATE", "PCTPELL", "G"]:
        cols.append(Df * g[c].transform(lambda s: (s - s.mean()) / s.std()).fillna(0).to_numpy()[:, None])
    X = np.hstack(cols); b = np.linalg.lstsq(X, y, rcond=None)[0]
    return len(d), d.inst_key.nunique(), d.field.nunique(), H1, H2, b[Dm.shape[1]]

rows = {"all (repaired)": cells,
        "drop Rutgers-Camden (pay = pooled Rutgers system)": cells[cells.InstitutionId != 537408],
        "drop all Rutgers campuses": cells[~cells.InstitutionId.isin([177, 369, 537408])],
        "drop every UNITID whose OPEID6 has >1 FoS UNITID (branch/system-pooled pay)": cells[~cells.UNITID.isin(pooled)],
        "only institutions in the old-join main sample": cells[cells.inst_key.isin(set(v1s.inst_key))]}
for k, c in rows.items():
    n, G, K, h1, h2, b = stats(sample(c))
    print(f"{k:80s} n={n:5d} G={G:3d} K={K:2d}  H1 {h1:+.4f}  H2 {h2:+.4f}  beta {b:+.5f}")
d = sample(cells)
print("main-sample institutions with OPEID6-pooled pay:", sorted(d[d.UNITID.isin(pooled)].inst_key.unique()))
