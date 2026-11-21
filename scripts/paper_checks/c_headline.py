"""Transparent end-to-end recompute of the US headline pair (H1 across, H2 within FE-only) and the main-spec slope (D3)
from the raw files: 2026 Wapman institution-stats (OrdinalPrestigeRank), Scorecard FoS 4-yr medians, Scorecard institution
file. Join: project normaliser (repaired or v1, via GAP_NAMEJOIN). Usage: python c_headline.py [repaired|v1]"""
import os, sys, importlib.util
mode = sys.argv[1] if len(sys.argv) > 1 else "repaired"
os.environ["GAP_NAMEJOIN"] = mode
import numpy as np, pandas as pd
from scipy.stats import rankdata, norm
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from src.crosswalks import fields as Fx
from src.crosswalks.institutions import normalize_institution_name as norm_name

ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[2]) + "/"; R = ROOT + "data/raw/"
spec = importlib.util.spec_from_file_location("cw24", ROOT + "scripts/24_crosswalk_audit.py")
cw24 = importlib.util.module_from_spec(spec); spec.loader.exec_module(cw24)
FIELDS66 = Fx.ALL_FIELDS + cw24.RECOVER
wf2key = {f["wapman_field"]: f["key"] for f in FIELDS66}
cip2key = {}
for f in FIELDS66:
    for c in f["cip4"]:
        cip2key[c] = f["key"]
print(f"[{mode}] fields in crosswalk: {len(FIELDS66)}")

# ---- Wapman (2026, published ordinal rank) ----
ist = pd.read_csv(R + "wapman2026/institution-stats.csv")
v1r = pd.read_csv(R + "wapman2022_v1/ranks.csv"); v1e = pd.read_csv(R + "wapman2022_v1/edge_lists.csv")
v1n = pd.concat([v1r[["InstitutionId", "InstitutionName"]], v1e[["InstitutionId", "InstitutionName"]],
                 v1e[["DegreeInstitutionId", "DegreeInstitutionName"]].set_axis(["InstitutionId", "InstitutionName"], axis=1)]).dropna()
v1n = v1n.assign(InstitutionId=v1n.InstitutionId.astype(int)).drop_duplicates("InstitutionId").set_index("InstitutionId").InstitutionName
ist["name"] = [v1n.get(i, n) for i, n in zip(ist.InstitutionId, ist.InstitutionName)]
ist["inst_key"] = ist.name.map(norm_name)
fr = ist[(ist.TaxonomyLevel == "Field") & ist.TaxonomyValue.isin(wf2key)].copy()
fr["field"] = fr.TaxonomyValue.map(wf2key)
fr["F"] = -fr.OrdinalPrestigeRank.astype(float)
print("crosswalk fields with a 2026 rank:", fr.field.nunique(), " missing:", sorted(set(wf2key.values()) - set(fr.field)))
assert not fr.duplicated(["inst_key", "field"]).any()
ac = ist[ist.TaxonomyLevel == "Academia"][["inst_key", "OrdinalPrestigeRank", "InstitutionId"]]
ac = ac.assign(G=-ac.OrdinalPrestigeRank.astype(float))

# ---- Scorecard FoS (bachelor's, 4-yr median) ----
fos = pd.read_csv(R + "scorecard_fos/Most-Recent-Cohorts-Field-of-Study.csv",
                  usecols=["UNITID", "INSTNM", "CIPCODE", "CREDLEV", "EARN_MDN_4YR", "EARN_COUNT_WNE_4YR"], dtype=str)
fos = fos[fos.CREDLEV == "3"].copy()
fos["field"] = fos.CIPCODE.str.zfill(4).map(cip2key)
fos = fos[fos.field.notna()].copy()
fos["earn"] = pd.to_numeric(fos.EARN_MDN_4YR, errors="coerce")
fos = fos.dropna(subset=["earn"])
fos["w"] = pd.to_numeric(fos.EARN_COUNT_WNE_4YR, errors="coerce").fillna(1.0).clip(lower=1.0)
fos["inst_key"] = fos.INSTNM.map(norm_name)
fos["we"] = fos.earn * fos.w
er = fos.groupby(["field", "inst_key"], sort=False).agg(UNITID=("UNITID", "first"), we=("we", "sum"), ws=("w", "sum"),
                                                        n_unitid=("UNITID", "nunique")).reset_index()
er["earnings"] = er.we / er.ws
print("FoS (field, inst_key) groups pooling >1 UNITID:", int((er.n_unitid > 1).sum()))

inst = pd.read_csv(R + "scorecard_inst/Most-Recent-Cohorts-Institution.csv",
                   usecols=["UNITID", "SAT_AVG", "ADM_RATE", "PCTPELL"], dtype=str)
for c in ["SAT_AVG", "ADM_RATE", "PCTPELL"]:
    inst[c] = pd.to_numeric(inst[c], errors="coerce")

cells = fr[["inst_key", "field", "F", "InstitutionId"]].merge(er[["inst_key", "field", "UNITID", "earnings"]],
                                                             on=["inst_key", "field"], how="inner")
cells = cells.merge(inst, on="UNITID", how="left").merge(ac[["inst_key", "G"]], on="inst_key", how="left")
print(f"matched programmes {len(cells)}, institutions {cells.inst_key.nunique()}, fields {cells.field.nunique()}")

# ---- main-spec sample (scripts/58 fe_sample with field x {SAT, ADM, PCTPELL, G}) ----
d = cells.dropna(subset=["earnings", "F", "SAT_AVG", "ADM_RATE", "PCTPELL", "G"])
d = d[d.earnings > 0]
while True:
    n0 = len(d)
    d = d[d.groupby("inst_key").field.transform("size") >= 2]
    d = d[d.groupby("field").inst_key.transform("size") >= 15]
    if len(d) == n0:
        break
d = d.sort_values(["field", "inst_key"]).reset_index(drop=True)
print(f"MAIN-SPEC SAMPLE: {len(d)} programmes, {d.inst_key.nunique()} institutions, {d.field.nunique()} fields")
rut = d[d.InstitutionId.isin([177, 369, 537408])]
print("Rutgers campuses in main-spec sample:", rut.groupby("InstitutionId").size().to_dict(),
      "| fields where >=2 Rutgers campuses:", int((rut.groupby("field").size() >= 2).sum()))

y = np.log(d.earnings.to_numpy())

def blom(v):
    r = rankdata(v)
    return norm.ppf((r - 0.375) / (len(v) + 0.25))

zF = np.empty(len(d)); zY = np.empty(len(d))
for f, ix in d.groupby("field").indices.items():
    a = blom(d.F.to_numpy()[ix]); b = blom(y[ix])
    zF[ix] = (a - a.mean()) / a.std(ddof=1); zY[ix] = (b - b.mean()) / b.std(ddof=1)
H1 = float(zF @ zY / np.sqrt((zF @ zF) * (zY @ zY)))
print(f"H1 across (pooled Pearson of within-field Blom scores): {H1:+.4f}")
# per-field Spearman mean as a cross-check
print(f"   mean within-field Spearman(F, pay) on this sample: "
      f"{np.mean([pd.Series(g.F).corr(pd.Series(np.log(g.earnings)), method='spearman') for _, g in d.groupby('field')]):+.4f}")

# two-way FE residuals by explicit dummies (institution + field)
ic = pd.factorize(d.inst_key)[0]; fc = pd.factorize(d.field, sort=True)[0]
D = np.hstack([np.eye(ic.max() + 1)[ic], np.eye(fc.max() + 1)[fc][:, 1:]])
def resid(v, X):
    return v - X @ np.linalg.lstsq(X, v, rcond=None)[0]
rF, rY = resid(zF, D), resid(zY, D)
H2 = float(rF @ rY / np.sqrt((rF @ rF) * (rY @ rY)))
print(f"H2 within (institution + field FE on the Blom scores): {H2:+.4f}")
# variant: FE residuals of raw log pay and raw F z-scores (robustness of the statistic choice)
g = d.groupby("field")
zFl = g.F.transform(lambda s: (s - s.mean()) / s.std()).to_numpy()
rY2 = resid(y, D); rF2 = resid(zFl, D)
print(f"   variant: FE residuals of linear z(F) and log pay: {rF2 @ rY2 / np.sqrt((rF2 @ rF2) * (rY2 @ rY2)):+.4f}")

# ---- D3 main-spec slope: log pay on inst FE + field FE + beta z(F) + field x z{SAT, ADM, PCTPELL, G} ----
fields = sorted(d.field.unique()); Df = np.eye(len(fields))[fc]
cols = [np.eye(ic.max() + 1)[ic], Df[:, 1:], zFl[:, None]]
for c in ["SAT_AVG", "ADM_RATE", "PCTPELL", "G"]:
    zc = g[c].transform(lambda s: (s - s.mean()) / s.std()).fillna(0).to_numpy()
    cols.append(Df * zc[:, None])
X = np.hstack(cols); j = ic.max() + 1 + len(fields) - 1
# drop all-zero columns (fields where a control is constant)
keep = np.abs(X).sum(0) > 0
X = X[:, keep]; j = int(np.flatnonzero(keep).tolist().index(j))
XtX_inv = np.linalg.pinv(X.T @ X)
b = XtX_inv @ X.T @ y
u = y - X @ b
N, K = X.shape; rankX = np.linalg.matrix_rank(X); Gc = ic.max() + 1
meat = np.zeros((K, K))
for k in range(Gc):
    s = X[ic == k].T @ u[ic == k]; meat += np.outer(s, s)
# statsmodels' CR1 with within-demeaned X uses K = number of non-FE regressors; with explicit dummies the df
# correction differs: report both
V_dum = XtX_inv @ meat @ XtX_inv
c_sm = Gc / (Gc - 1) * (N - 1) / (N - (rankX - Gc))
c_dum = Gc / (Gc - 1) * (N - 1) / (N - rankX)
se_raw = np.sqrt(V_dum[j, j])
print(f"D3 main-spec beta = {b[j]:+.5f}   CR1 SE (absorbed-FE df) {se_raw*np.sqrt(c_sm):.5f}  (dummy df) {se_raw*np.sqrt(c_dum):.5f}"
      f"   K={K} rank={rankX}")
# pairs cluster bootstrap (institutions), 999 draws, on the within-institution-demeaned design
Xd = X[:, Gc:].copy(); yd = y.copy()
cnt = np.bincount(ic).astype(float)
def dm(M):
    s = np.zeros((Gc,) + M.shape[1:]); np.add.at(s, ic, M)
    return M - (s / (cnt[:, None] if M.ndim == 2 else cnt))[ic]
Xd = dm(Xd); yd = dm(yd); jd = j - Gc
bd = np.linalg.lstsq(Xd, yd, rcond=None)[0]
print(f"   FWL check (demeaned design) beta = {bd[jd]:+.5f}")
A = np.stack([Xd[ic == k].T @ Xd[ic == k] for k in range(Gc)]); bb = np.stack([Xd[ic == k].T @ yd[ic == k] for k in range(Gc)])
rng = np.random.default_rng(12345); bs = []
for _ in range(999):
    c = np.bincount(rng.integers(0, Gc, Gc), minlength=Gc).astype(float)
    XtX = np.tensordot(c, A, axes=1); Xty = c @ bb
    kk = np.diag(XtX) > 1e-10
    beta = np.linalg.lstsq(XtX[np.ix_(kk, kk)], Xty[kk], rcond=None)[0]
    bs.append(beta[int(np.flatnonzero(kk).tolist().index(jd))])
bs = np.array(bs)
print(f"   cluster bootstrap 95% percentile CI [{np.percentile(bs, 2.5):+.4f}, {np.percentile(bs, 97.5):+.4f}]  (999 draws, own seed)")
d.assign(zF_blom=zF, zY_blom=zY).to_csv(f"{ROOT}data/interim/paper_checks_main_sample_{mode}.csv", index=False)
cells.to_csv(f"{ROOT}data/interim/paper_checks_cells_{mode}.csv", index=False)
