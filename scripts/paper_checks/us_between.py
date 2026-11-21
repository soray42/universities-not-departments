"""Paper check (2026-11-15): US between-university (university-mean) correlation of F and pay, and
the size of one within-field SD of F in rank places. Reads the scripts/78 main-spec cells as rebuilt independently
by c_headline.py in this folder (paper_checks_main_sample_repaired.csv; 2026 Wapman release, repaired join).

Checks first that the cells reproduce scripts/78's G3 US rev. 2 numbers (3,961 programmes, 214 universities,
53 fields; across +0.448, within FE-only +0.047; data/interim/gap_checks_summary.csv).

Between-university statistic: the UK definition of scripts/78 (uk_stats, revision 1): Pearson correlation, over
universities, of the university means of the field-demeaned normal scores (Blom scores standardised within field).
Interval: percentile cluster bootstrap over universities (2,000 draws, seed 7801); in each draw the scores are
re-demeaned within field on the drawn rows and the university means are taken over the drawn copies, as scripts/78
does for the UK provider means.

Rank places: F = -OrdinalPrestigeRank (0 = top, contiguous over the field network's ranked departments). One SD of F
is the within-field SD (ddof = 1) over the programmes of the sample; reported over fields for the main-spec sample
and for the FE-only sample (scripts/58 fe_sample rules without the selectivity controls).
Run: python scripts/paper_checks/us_between.py (after c_headline.py)
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
d = pd.read_csv(ROOT / "data/interim/paper_checks_main_sample_repaired.csv", dtype={"UNITID": str})
print(f"main-spec cells: {len(d)} programmes, {d.inst_key.nunique()} universities, {d.field.nunique()} fields")
assert (len(d), d.inst_key.nunique(), d.field.nunique()) == (3961, 214, 53)

zF, zY = d.zF_blom.to_numpy(), d.zY_blom.to_numpy()
across = float(zF @ zY / np.sqrt((zF @ zF) * (zY @ zY)))
ic = pd.factorize(d.inst_key)[0]
fc = pd.factorize(d.field, sort=True)[0]
D = np.hstack([np.eye(ic.max() + 1)[ic], np.eye(fc.max() + 1)[fc][:, 1:]])
res = lambda v: v - D @ np.linalg.lstsq(D, v, rcond=None)[0]
rF, rY = res(zF), res(zY)
within = float(rF @ rY / np.sqrt((rF @ rF) * (rY @ rY)))
print(f"across {across:+.4f} (scripts/78 +0.4477); within FE-only {within:+.4f} (scripts/78 +0.0465)")
assert abs(across - 0.4477474234) < 5e-4 and abs(within - 0.0465032568) < 5e-4


def between(zf, zy, fcode, ucode):
    K, U = fcode.max() + 1, ucode.max() + 1
    nf = np.bincount(fcode, minlength=K)
    a = zf - (np.bincount(fcode, zf, K) / nf)[fcode]
    b = zy - (np.bincount(fcode, zy, K) / nf)[fcode]
    nu = np.bincount(ucode, minlength=U)
    ma, mb = np.bincount(ucode, a, U) / nu, np.bincount(ucode, b, U) / nu
    return float(np.corrcoef(ma, mb)[0, 1])


pt = between(zF, zY, fc, ic)
G = ic.max() + 1
groups = [np.flatnonzero(ic == g) for g in range(G)]
rng = np.random.default_rng(7801)
bs = []
for _ in range(2000):
    draw = rng.integers(G, size=G)
    rows = np.concatenate([groups[g] for g in draw])
    newu = np.concatenate([np.full(len(groups[g]), k) for k, g in enumerate(draw)])
    bs.append(between(zF[rows], zY[rows], fc[rows], newu))
lo, hi = np.percentile(bs, [2.5, 97.5])
print(f"US between-university (university-mean) correlation: {pt:+.4f} [{lo:+.4f}, {hi:+.4f}] "
      f"(2,000 university-cluster bootstrap draws, seed 7801; {G} universities)")

# one within-field SD of F in rank places
sd_main = d.groupby("field").F.std(ddof=1)
q = sd_main.quantile([0.25, 0.5, 0.75])
print(f"main-spec sample: within-field SD of F in rank places over {len(sd_main)} fields: median {q[0.5]:.1f}, "
      f"IQR [{q[0.25]:.1f}, {q[0.75]:.1f}], min {sd_main.min():.1f}, max {sd_main.max():.1f}")
c = pd.read_csv(ROOT / "data/interim/paper_checks_cells_repaired.csv", dtype={"UNITID": str})
f = c.dropna(subset=["earnings", "F"])
f = f[f.earnings > 0]
while True:
    n0 = len(f)
    f = f[f.groupby("inst_key").field.transform("size") >= 2]
    f = f[f.groupby("field").inst_key.transform("size") >= 15]
    if len(f) == n0:
        break
print(f"FE-only sample rebuilt: {len(f)} programmes, {f.inst_key.nunique()} universities, {f.field.nunique()} fields "
      f"(scripts/58: 4,645 / 251 / 55)")
sd_fe = f.groupby("field").F.std(ddof=1)
q = sd_fe.quantile([0.25, 0.5, 0.75])
print(f"FE-only sample: within-field SD of F in rank places over {len(sd_fe)} fields: median {q[0.5]:.1f}, "
      f"IQR [{q[0.25]:.1f}, {q[0.75]:.1f}], min {sd_fe.min():.1f}, max {sd_fe.max():.1f}")
for k in ("computer_science", "economics", "nursing", "psychology"):
    if k in sd_main.index:
        print(f"   {k}: SD {sd_main[k]:.1f} rank places (main), {sd_fe.get(k, np.nan):.1f} (FE-only); "
              f"ranked departments in the main sample {int((d.field == k).sum())}")
