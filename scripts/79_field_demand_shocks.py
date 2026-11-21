"""Field demand shocks -- when the labour market for a field's graduates suddenly gets better or worse, do employers'
rankings of programmes move closer to or further from the academic ranking?

QUESTION (two-sided; no favoured direction). Within-field coupling = Spearman, across institutions offering bachelor
field f, of faculty-hiring prestige (F = Wapman field rank; G = university-wide rank) and graduates' median earnings
(PSEO V4.14.1, scripts/65 panel). When the labour market for a field's graduates suddenly gets much better or worse
(e.g., the dot-com bust for computing graduates of 2001-03, the 2008 finance crash, the 2010s tech boom), do
employers' rankings of programmes move closer to or further from the academic ranking, and is the department-specific
part (F beyond G) priced more in a hot market?

PRE-SPECIFICATION (written verbatim into this docstring and into
FIELD_DEMAND_SHOCKS_RESULT.md on 2026-11-14, before any outcome data (the coupling panel or the PSEO cells) were read by
this script; anything else is exploratory):

1. Field demand index D_{f,t}, built from data that do not use institutions. Primary: a shift-share index of national
occupational demand. Take fixed field→occupation shares, either from the CIP→O*NET-SOC crosswalk in data/raw/onet/
(check src/crosswalks/fields.py and the file) or from ACS 2023 PUMS FOD1P×OCCP for bachelor's holders aged 23-35
(data/raw/acs/). Combine them with national occupational real wage and employment growth by year from BLS OES
national files (bls.gov/oes; BLS often blocks scripts, so try a descriptive User-Agent; if blocked, fall back to the
Census ACS PUMS API at api.census.gov for field-of-degree (FOD1P) median earnings and employment of bachelor's
holders aged 23-27 by year, 2009+, and say which you used). Average over the calendar years in which each window's
y1 earnings are measured (scripts/65 gives earn_years). Standardise D within field (deviation from the field's own
mean over windows). Document the crosswalk and coverage. Save downloads under data/raw/<name>/ with a provenance
subsection (URL, date, md5) in data/raw/SOURCES.md. Keep each download under ~300 MB.
2. Primary test T1: on y1 cells, fixed-institution sample, regress z_F (Fisher-z coupling) on D_{f,t} with field FE
and window FE, weighting by inverse sampling variance. Inference: wild cluster bootstrap by field (Webb weights, 1999
reps) plus a field-label permutation of D. Report beta per SD of D, its 95% CI and the MDE. Verdict: "rises in hot
markets" if CI > 0, "falls" if CI < 0, "null" if the CI includes 0 and the MDE ≤ 0.05, otherwise "underpowered".
3. T2: same with z_par_F (department part beyond the university) as outcome. Same rule.
4. T3: same as T1 at y5, using D in the y5 earnings years. Same rule.
5. Descriptive case studies (no test; label them as such): computing fields (computer_science, computer_engineering)
by window at y1 and y5, against D; finance and economics around the 2007-09 window; any field with |D| ≥ 2 SD. One
figure: outputs/figures/field_demand_shocks.png.
6. State the data limits plainly in the RESULT file: PSEO windows start in 2001, so the dot-com boom itself is not
observed, only the bust; no institution × field earnings source observes a cohort entering after late 2022 yet (PSEO
y1 to 2020-22, Scorecard 1-year earnings to CY2020-21, UK LEO to tax year 2022/23), so AI-era entry cannot be studied.

END OF PRE-SPECIFICATION.

OPERATIONAL DEFINITIONS (fixed on 2026-11-14 after the demand index had been built and inspected -- it uses no
institution or earnings data -- and before any outcome data (the coupling panel's values or PSEO cells) were read;
they settle choices that items 1-6 leave open; everything not covered by items 1-6 or by this block is exploratory):
O1 Demand source. bls.gov answered HTTP 403 to every request (a descriptive user agent and a browser user agent; two
   URL paths). The identical BLS OES national files (oes01nat.zip, oes02nat.zip, oesm03nat.zip ... oesm23nat.zip;
   reference periods November 2001, November 2002, May 2003 ... May 2023) were taken from the Internet Archive's
   Wayback Machine copies of the bls.gov URLs (snapshots of 2025-12-20; URL and md5 per file in data/raw/SOURCES.md).
   The Census ACS PUMS API fallback was NOT used: it starts in 2009 and would lose the 2001-03 and 2004-06 windows at
   y1 (the dot-com bust). This departs from the literal fallback wording of item 1 and is stated in the write-up.
O2 Occupations. SOC minor groups (first four characters of the SOC code, e.g. 15-1 = computer occupations; the
   prefix is the same minor group in SOC 2000, 2010 and 2018), from the detailed occupations of each OES file. Growth
   t-1 -> t of group o: log change of total employment and of the employment-weighted mean annual wage (A_MEAN)
   deflated by the CPI-U annual average (CUUR0000SA0; BLS series via DBnomics), over the detailed codes published
   with positive employment in both years ("matched codes"). At the four SOC-revision transitions (2009->2010 and
   2011->2012: SOC 2000 -> 2010 through the OES 2010-11 hybrid; 2018->2019 and 2020->2021: SOC 2010 -> 2018 through
   the OES 2019-20 hybrid) a group whose matched codes cover < 50% of its employment in either year takes the growth
   of its crosswalk component instead (all minor groups joined by any cross-group link of that revision's official
   BLS SOC crosswalk), computed on component totals. A group without a defined growth in a year drops out of that
   year's index and the field's shares are renormalised over the rest.
O3 Occupational demand g_{o,t} = log growth of the real wage bill = employment growth + real mean-wage growth.
   Employment-only and wage-only indices are sensitivities.
O4 Shares. ACS 2023 1-year PUMS persons aged 23-35 with a bachelor's degree as highest degree (SCHL 21), civilian
   employed (ESR 1, 2), with an occupation (SOCP = the SOC code of the person's OCCP), weighted by PWGTP; field ->
   FOD1P map of scripts/69 field_map(); s_{f,o} = weighted share of field f's persons in minor group o, over groups
   present in OES 2023. The CIP -> O*NET-SOC crosswalk was not used (it lists links, not employment shares).
O5 Index. D_raw_{f,c,h} = mean of D_{f,t} = sum_o s_{f,o} g_{o,t} over the three earnings years of window c at
   horizon h (scripts/65 earn_years: c+h .. c+h+2). D_{f,c,h} = (D_raw - mean of D_raw over the field's windows in
   the test) / s_h, with s_h = pooled within-field SD, sqrt(sum of squared deviations / (N - k)) over the N cells of
   the k fields of the test. "Per SD of D" and "|D| >= 2 SD" use this unit. The SD of D left after field and window
   effects is printed, and beta is also shown per residual SD (rescaling by a constant; no separate verdict).
O6 Sample and outcomes. Fixed institutions = scripts/65 panel sample "fixed17" (institutions present in all 17 field x
   window x horizon cells; 7 y1 and 6 y5 windows). T1, T3: panel z_F (Fisher z of Spearman(F, p50)), weights
   1/var_z_F_bw (Bonett-Wright). T2: the panel column par_F is the partial Spearman of F and p50 GIVEN THE PSEO
   COVERAGE SHARE, computed only for sample "all" (scripts/65 cell_eval) -- not F given G. T2 therefore uses
   par_FG = partial Spearman(F, p50 | G), computed here on the same fixed17 cells (rebuilt with scripts/65
   load_long / build_samples; the rebuilt rho_F is asserted equal to the panel's), Fisher z, weights
   1 / [(1 + r^2/2) / (n - 4)].
O7 Model and inference. Weighted least squares z_{f,c} = a_f + g_c + beta D_{f,c} + e. CR1 variance clustered by
   field, factor G/(G-1) (N-1)/(N-K), K = 1 + (number of windows - 1) (field effects are nested in the clusters).
   p: wild cluster restricted (WCR) bootstrap-t, Webb six-point weights, 1999 replicates. 95% CI (basis of the
   verdict): inversion of the WCR test on the same draws (scripts/65 wcr_invert). MDE = (q + 0.842) x SE_CR1, q = 95%
   quantile of |t*| of the WCR bootstrap at beta = 0. The unrestricted wild bootstrap-t CI is shown alongside (no
   verdict). Field-label permutation: whole D trajectories (all windows of a field) permuted across fields, 1999
   permutations, two-sided on |beta|; the number of distinct trajectories is printed. Random numbers: numpy
   SeedSequence([79, crc32(tag)]).
O8 Sensitivities (reported, no verdict): unweighted; employment-only D; wage-only D; horizon-fixed sample
   (institutions present in every window of the horizon, >= 15 per field, built here from scripts/65 load_long) with
   the same outcomes and weights. Exploratory: z_G (Spearman(G, p50)) as outcome.
O9 Case studies (descriptive, no test): fixed17 cells where the field is in fixed17; computer_engineering is not, so
   its rows use the panel's "all"-sample rho_F (plain Spearman; the institutions change across windows). "Around the
   2007-09 window" = windows 2004-06, 2007-09, 2010-12 at y1 and y5. Cells with |D| >= 2 are listed from the T1 and
   T3 samples.
O10 Sanity check of D, done before outcomes (numbers printed in the write-up): relative to the mean over fields,
   computing's annual index is lowest in 2002 and above the mean in 2011-15; finance and economics are below it in
   2008-10; nursing is above it in 2008-10. The computing dip is confined to 2002 and offset in 2003-04, so the
   dot-com bust is only weakly present in the 2001-03 window's y1 index.

END OF OPERATIONAL DEFINITIONS.

Run:PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/79_field_demand_shocks.py
"""
from __future__ import annotations

import io
import sys
import json
import zlib
import hashlib
import zipfile
import argparse
import importlib.util
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr, norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s65 = _load("s65", "65_coupling_dynamics.py")      # PSEO cells, earn_years, Fisher z, Bonett-Wright, WCR inversion
s69 = _load("s69", "69_local_field_demand.py")      # field -> FOD1P map (66-field universe)

SEED = 79
RUN_DATE = "2026-11-14"
NWB = 1999                 # wild cluster bootstrap replicates (Webb six-point weights)
NPERM = 1999               # field-label permutations of D
BENCH = 0.05               # verdict benchmark for the MDE (Fisher-z coupling per SD of D)
Z975 = s65.Z975
Z80 = s65.Z80
WEBB = s65.WEBB
NMIN = s65.NMIN
HY = s65.HY
CO = s65.CO
FIXED = "fixed17"
COV_MIN = 0.5              # matched-code coverage below which a SOC-revision transition uses component growth
AGE_LO, AGE_HI = 23, 35
CHUNK = 200_000

RAW = ROOT / "data" / "raw"
OES_DIR = RAW / "oes_national"
XW_DIR = RAW / "soc_crosswalks"
CPI_FILE = RAW / "cpi_u" / "CUUR0000SA0_dbnomics.json"
ACS_DIR = RAW / "acs"
ACS_FILES = ["psam_pusa.csv", "psam_pusb.csv"]
PANEL = ROOT / "data" / "interim" / "coupling_dynamics_panel.csv"
OUT_ACS = ROOT / "data" / "interim" / "field_demand_acs_fod_minor.csv"
OUT_G = ROOT / "data" / "interim" / "field_demand_oes_minor_growth.csv"
OUT_D = ROOT / "data" / "interim" / "field_demand_index.csv"
OUT_CELLS = ROOT / "data" / "interim" / "field_demand_cells.csv"
OUT_RES = ROOT / "data" / "interim" / "field_demand_shocks_results.csv"
OUT_FIG = ROOT / "outputs" / "figures" / "field_demand_shocks.png"
OUT_MD = ROOT / "FIELD_DEMAND_SHOCKS_RESULT.md"
SOURCES = ROOT / "data" / "sources.csv"
SOURCES_SECTION = "Field demand shocks — BLS OES national files, SOC crosswalks and CPI-U (scripts/79)"

OES_FILES = {2001: "oes01nat.zip", 2002: "oes02nat.zip", **{y: f"oesm{y % 100:02d}nat.zip" for y in range(2003, 2024)}}
OES_YEARS = sorted(OES_FILES)
G_YEARS = OES_YEARS[1:]                       # growth years t (t-1 -> t): 2002..2023
# SOC revision transitions in OES (year t of the pair t-1 -> t): SOC 2000 -> OES 2010-11 hybrid -> SOC 2010 (2012);
# SOC 2010 -> OES 2019-20 hybrid -> SOC 2018 (2021). Each uses the official SOC crosswalk of its revision.
REVISION = {2010: "2000-2010", 2012: "2000-2010", 2019: "2010-2018", 2021: "2010-2018"}
XW_FILES = {"2000-2010": ("soc_2000_to_2010_crosswalk.xls", "2000 SOC code"),
            "2010-2018": ("soc_2010_to_2018_crosswalk.xlsx", "2010 SOC Code")}
# provenance (data/sources.csv, section SOURCES_SECTION); md5 asserted at run time
PROV = {
    "oes_national/oes01nat.zip": "e3931c5aebb3536d1cb6a0d9dc834881",
    "oes_national/oes02nat.zip": "54cb741f1762d23d2c23c826e964b111",
    "oes_national/oesm03nat.zip": "b6add49db9fd58347dfc008967e3f98c",
    "oes_national/oesm04nat.zip": "b4ade2247b62514c9ed9e8fe6e24c4af",
    "oes_national/oesm05nat.zip": "11076116f5587e6991b46b088779d3f5",
    "oes_national/oesm06nat.zip": "55af57905e83e9c2d5a56d1ff69dea18",
    "oes_national/oesm07nat.zip": "e13749f32bece52f3975b5595f3a8331",
    "oes_national/oesm08nat.zip": "89f021ab3b8650945934d982f296842b",
    "oes_national/oesm09nat.zip": "a1081371e397a7377f0f8cd465f08021",
    "oes_national/oesm10nat.zip": "f4609385d183e2ef7bb89b1b640a180c",
    "oes_national/oesm11nat.zip": "10d3292d7224d8803f2ca8aa9e42f9b9",
    "oes_national/oesm12nat.zip": "7f0f55fab3d59957aa36739cdbb25b6d",
    "oes_national/oesm13nat.zip": "1a195df1f55b8dc38d217d2ffdb9e4d1",
    "oes_national/oesm14nat.zip": "c8f74b58f4081479bdd2e143bd0cb276",
    "oes_national/oesm15nat.zip": "e3c0d61c44d23c08043334e9d286b8be",
    "oes_national/oesm16nat.zip": "e242e9a218eff111f9fb6334d8c8978b",
    "oes_national/oesm17nat.zip": "f49becee8a1048d658d735490784a6f0",
    "oes_national/oesm18nat.zip": "20999664e9fc8c2ce070f115998de254",
    "oes_national/oesm19nat.zip": "5b0303591a77efa36e649f9eb971922a",
    "oes_national/oesm20nat.zip": "1b3ec17409b13700c94bf25bd064bb39",
    "oes_national/oesm21nat.zip": "238efa62154cf60fae1acca250d6affe",
    "oes_national/oesm22nat.zip": "62ad7bec22510a1e85107fcb92dcc639",
    "oes_national/oesm23nat.zip": "79d510f702d9e2a6e0ae2065efca1823",
    "soc_crosswalks/soc_2000_to_2010_crosswalk.xls": "8b4967cab136d124fed0416147bdcd1d",
    "soc_crosswalks/soc_2010_to_2018_crosswalk.xlsx": "8a358b553965e3eb2bde6701d10e6d9e",
    "cpi_u/CUUR0000SA0_dbnomics.json": "1d04ba9d4a9748d427503398664a79d7",
}

RES: list[dict] = []


def rec(section, stat, est, lo=np.nan, hi=np.nan, se=np.nan, p=np.nan, k=np.nan, n=np.nan, sample="", note=""):
    RES.append(dict(section=section, stat=stat, sample=sample, estimate=est, ci_lo=lo, ci_hi=hi, se=se, p_value=p,
                    k=k, n=n, note=note))


def stage(msg):
    print(f"[79] {msg}", flush=True)


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rng_for(tag: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SEED, zlib.crc32(tag.encode())]))


def check_provenance() -> dict:
    src = SOURCES.read_text(encoding="utf-8")
    assert SOURCES_SECTION in src, "provenance section missing in data/sources.csv"
    out = {}
    for rel, h in PROV.items():
        got = md5(RAW / rel)
        assert got == h, f"{rel}: md5 {got} != {h}"
        assert h in src, f"{rel}: md5 not recorded in data/sources.csv"
        out[rel] = h
    return out


# =============================================================================================
# demand side: OES national occupational employment and wages (no institutions involved)
# =============================================================================================
def load_oes(y: int) -> pd.DataFrame:
    """Detailed occupations of one OES national file: code, employment, annual mean wage (nominal)."""
    zf = zipfile.ZipFile(OES_DIR / OES_FILES[y])
    nm = [n for n in zf.namelist() if "national" in n.lower()]
    assert len(nm) == 1, (y, zf.namelist())
    x = pd.read_excel(io.BytesIO(zf.read(nm[0])), dtype=str)
    x.columns = [c.strip().lower() for c in x.columns]
    gc = [c for c in x.columns if c in ("group", "occ_group", "o_group")]
    assert len(gc) == 1, (y, x.columns)
    x = x.rename(columns={gc[0]: "grp"})
    if "area" in x.columns:
        assert x.area.nunique() == 1
    x["grp"] = x.grp.fillna("detailed").str.strip().str.lower()
    x["occ_code"] = x.occ_code.str.strip()
    det = x[(x.grp == "detailed") & x.occ_code.str.fullmatch(r"\d\d-\d{4}") & ~x.occ_code.str.endswith("0000")].copy()
    assert not det.occ_code.duplicated().any(), y
    det["emp"] = pd.to_numeric(det.tot_emp.str.replace(",", ""), errors="coerce")
    det["wage"] = pd.to_numeric(det.a_mean.str.replace(",", ""), errors="coerce")
    det["year"] = y
    det["minor"] = det.occ_code.str[:4]
    det = det[det.minor.str[:2] != "55"]                   # military (not in OES; defensive)
    return det[["year", "occ_code", "minor", "emp", "wage"]].reset_index(drop=True)


def cpi_annual() -> dict:
    d = json.loads(CPI_FILE.read_text())
    s = d["series"]["docs"][0]
    assert s["series_code"] == "CUUR0000SA0"
    v = pd.DataFrame({"period": s["period"], "value": s["value"]})
    v = v[v.period.str.fullmatch(r"\d{4}-\d{2}")]
    v["year"] = v.period.str[:4].astype(int)
    g = v.groupby("year").value.agg(["mean", "size"])
    g = g[g["size"] == 12]
    return {int(y): float(m) for y, m in g["mean"].items()}


def xw_components(rev: str) -> dict:
    """Minor groups linked by any cross-minor-group link of the official SOC crosswalk -> component label."""
    fn, key = XW_FILES[rev]
    a = pd.read_excel(XW_DIR / fn, header=None, dtype=str)
    i = a.index[a[0].astype(str).str.strip().eq(key)][0]
    a = a.iloc[i + 1:, [0, 2]].dropna()
    a.columns = ["old", "new"]
    a = a[a.old.str.strip().str.fullmatch(r"\d\d-\d{4}") & a.new.str.strip().str.fullmatch(r"\d\d-\d{4}")]
    mo, mn = a.old.str.strip().str[:4], a.new.str.strip().str[:4]
    par: dict = {}

    def root(u):
        par.setdefault(u, u)
        while par[u] != u:
            par[u] = par[par[u]]
            u = par[u]
        return u

    for u, v in zip(mo, mn):
        ru, rv = root(u), root(v)
        if ru != rv:
            par[max(ru, rv)] = min(ru, rv)
    groups = sorted(set(mo) | set(mn))
    comp = {g: root(g) for g in groups}
    members: dict = {}
    for g, r in comp.items():
        members.setdefault(r, []).append(g)
    return dict(comp=comp, members={r: sorted(v) for r, v in members.items()}, n_links=len(a),
                n_cross=int((mo != mn).sum()))


def _tot(d: pd.DataFrame) -> tuple:
    e = d[d.emp > 0]
    ew = e[np.isfinite(e.wage)]
    emp = float(e.emp.sum())
    wbar = float((ew.emp * ew.wage).sum() / ew.emp.sum()) if len(ew) else np.nan
    return emp, wbar


def growth_table(det: pd.DataFrame, cpi: dict, xws: dict) -> pd.DataFrame:
    """Per minor group o and year t: log growth t-1 -> t of employment, real mean wage and real wage bill.
    Default: over detailed codes published in both years (matched codes). At a SOC revision transition, a group
    whose matched codes cover < COV_MIN of its employment in either year takes the growth of its crosswalk component
    (all minor groups linked by a cross-minor-group link of that revision's crosswalk, in total)."""
    rows = []
    for t in G_YEARS:
        a, b = det[det.year == t - 1], det[det.year == t]
        ok_a, ok_b = set(a.occ_code[a.emp > 0]), set(b.occ_code[b.emp > 0])
        m = ok_a & ok_b
        defl = np.log(cpi[t] / cpi[t - 1])
        for o in sorted(set(a.minor) | set(b.minor)):
            ao, bo = a[a.minor == o], b[b.minor == o]
            am, bm = ao[ao.occ_code.isin(m)], bo[bo.occ_code.isin(m)]
            ea, eb = float(ao.emp[ao.emp > 0].sum()), float(bo.emp[bo.emp > 0].sum())
            cov0 = float(am.emp.sum()) / ea if ea > 0 else 0.0
            cov1 = float(bm.emp.sum()) / eb if eb > 0 else 0.0
            r = dict(minor=o, year=t, emp_prev=ea, emp=eb, cov_prev=cov0, cov=cov1, method="", comp="")
            if t in REVISION and min(cov0, cov1) < COV_MIN and ea > 0 and eb > 0:
                X = xws[REVISION[t]]
                cg = X["comp"].get(o, o)
                mem = X["members"].get(cg, [o])
                (e0, w0), (e1, w1) = _tot(a[a.minor.isin(mem)]), _tot(b[b.minor.isin(mem)])
                r.update(method="component", comp="+".join(mem))
            elif len(am) and len(bm):
                (e0, w0), (e1, w1) = _tot(am), _tot(bm)
                r.update(method="matched")
            else:
                e0 = e1 = w0 = w1 = np.nan
                r.update(method="missing")
            ge = np.log(e1 / e0) if (e0 > 0 and e1 > 0) else np.nan
            gw = np.log(w1 / w0) - defl if (np.isfinite(w0) and np.isfinite(w1) and w0 > 0 and w1 > 0) else np.nan
            r.update(g_emp=ge, g_wage=gw, g_bill=ge + gw)
            rows.append(r)
    return pd.DataFrame(rows)


# =============================================================================================
# field -> occupation shares: ACS 2023 1-year PUMS (FOD1P x SOCP), bachelor's holders aged 23-35
# =============================================================================================
ACS_COLS = ["AGEP", "SCHL", "ESR", "FOD1P", "SOCP", "PWGTP"]


def _acs_file(fname: str):
    out, n_all = [], 0
    for ch in pd.read_csv(ACS_DIR / fname, usecols=ACS_COLS, chunksize=CHUNK,
                          dtype={"SOCP": str, "AGEP": float, "SCHL": float, "ESR": float, "FOD1P": float,
                                 "PWGTP": float}):
        n_all += len(ch)
        ch = ch[(ch.AGEP >= AGE_LO) & (ch.AGEP <= AGE_HI) & (ch.SCHL == 21) & ch.ESR.isin([1, 2])
                & ch.FOD1P.notna() & ch.SOCP.notna()]
        out.append(ch)
    x = pd.concat(out, ignore_index=True)
    x["minor"] = x.SOCP.str[:2] + "-" + x.SOCP.str[2]
    g = x.groupby([x.FOD1P.astype(int), "minor"]).PWGTP.agg(["sum", "size"]).reset_index()
    return g, n_all


def acs_fod_minor(workers: int) -> pd.DataFrame:
    if OUT_ACS.exists():
        return pd.read_csv(OUT_ACS, dtype={"FOD1P": int, "minor": str})
    with ProcessPoolExecutor(max_workers=min(2, workers)) as ex:
        res = list(ex.map(_acs_file, ACS_FILES))
    g = pd.concat([r[0] for r in res]).groupby(["FOD1P", "minor"], as_index=False)[["sum", "size"]].sum()
    g = g.rename(columns={"sum": "wt", "size": "n"}).sort_values(["FOD1P", "minor"]).reset_index(drop=True)
    g.to_csv(OUT_ACS, index=False)
    return g


def field_shares(acs: pd.DataFrame, oes_minors: set) -> tuple:
    fmap, kind = s69.field_map()
    rows, cov = [], {}
    for f in sorted(fmap):
        codes = [int(c) for c in fmap[f]]
        x = acs[acs.FOD1P.isin(codes)].groupby("minor")[["wt", "n"]].sum()
        tot_w, tot_n = float(x.wt.sum()), int(x.n.sum())
        x = x[x.index.isin(oes_minors)]
        cov[f] = dict(n_persons=tot_n, wt=tot_w, share_in_oes=float(x.wt.sum() / tot_w) if tot_w else np.nan,
                      kind=kind[f], fod1p="+".join(fmap[f]))
        for o, r in x.iterrows():
            rows.append(dict(field=f, minor=o, share=float(r.wt / x.wt.sum()), n=int(r.n)))
    return pd.DataFrame(rows), cov


def annual_index(S: pd.DataFrame, G: pd.DataFrame, comp: str = "g_bill") -> pd.DataFrame:
    """D_{f,t} = sum_o s_fo g_ot over groups with a defined g_ot, shares renormalised over those groups."""
    rows = []
    for t in G_YEARS:
        g = G[G.year == t].set_index("minor")[comp]
        for f, s in S.groupby("field"):
            gv = s.minor.map(g)
            ok = np.isfinite(gv.to_numpy(float))
            w = s.share.to_numpy(float)
            rows.append(dict(field=f, year=t, D=float(np.sum(w[ok] * gv.to_numpy(float)[ok]) / w[ok].sum()),
                             cov=float(w[ok].sum())))
    return pd.DataFrame(rows)


def window_index(A: pd.DataFrame) -> pd.DataFrame:
    """Raw window index: mean of D_{f,t} over the three earnings years of window c at horizon h (scripts/65)."""
    piv = A.pivot(index="field", columns="year", values="D")
    cvp = A.pivot(index="field", columns="year", values="cov")
    rows = []
    for h in ("y1", "y5"):
        for c in CO[h]:
            t0 = int(c) + HY[h]
            ys = [t0, t0 + 1, t0 + 2]
            assert s65.earn_years(c, h) == f"{t0}-{t0 + 2}"
            for f in piv.index:
                rows.append(dict(field=f, grad_window=int(c), horizon=h, earn_years=s65.earn_years(c, h),
                                 D_raw=float(piv.loc[f, ys].mean()), min_cov=float(cvp.loc[f, ys].min())))
    return pd.DataFrame(rows)


def build_demand(workers: int) -> dict:
    stage("OES national files 2001-2023")
    det = pd.concat([load_oes(y) for y in OES_YEARS], ignore_index=True)
    cpi = cpi_annual()
    xws = {k: xw_components(k) for k in XW_FILES}
    G = growth_table(det, cpi, xws)
    stage("ACS 2023 PUMS FOD1P x SOC minor group")
    acs = acs_fod_minor(workers)
    oes23 = set(det[det.year == 2023].minor)
    S, cov = field_shares(acs, oes23)
    out = dict(det=det, cpi=cpi, xws=xws, G=G, acs=acs, S=S, cov=cov)
    for comp in ("g_bill", "g_emp", "g_wage"):
        A = annual_index(S, G, comp)
        out[f"A_{comp}"] = A
        out[f"W_{comp}"] = window_index(A)
    return out




# =============================================================================================
# outcome side: coupling cells (scripts/65 panel; partial on G rebuilt from the scripts/65 cells)
# =============================================================================================
def rank_corrs(P, G, E) -> dict:
    rP, rG, rE = rankdata(P), rankdata(G), rankdata(E)
    c = np.corrcoef(np.vstack([rP, rG, rE]))
    rPG, rPE, rGE = c[0, 1], c[0, 2], c[1, 2]
    par = (rPE - rPG * rGE) / np.sqrt((1 - rPG ** 2) * (1 - rGE ** 2))
    return dict(rho_F=float(rPE), rho_G=float(rGE), rho_FG=float(rPG), par_FG=float(par))


def outcome_cells() -> tuple:
    """fixed17 cells (panel values + par_FG rebuilt here), horizon-fixed cells (built here), panel 'all' cells."""
    pan = pd.read_csv(PANEL)
    fx = pan[pan["sample"] == FIXED].copy()
    al = pan[pan["sample"] == "all"].copy()
    stage("rebuilding scripts/65 cells (load_long, build_samples)")
    L = s65.load_long()
    s65.build_samples(L)
    rows = []
    for c in s65.CELL:
        if c["sample"] != FIXED or c["horizon"] not in ("y1", "y5"):
            continue
        g = c["df"]
        r = rank_corrs(g.P.to_numpy(float), g.G.to_numpy(float), g.earnings.to_numpy(float))
        rows.append(dict(field=c["field"], grad_window=int(c["cohort"]), horizon=c["horizon"], n_chk=len(g),
                         rho_F_chk=r["rho_F"], rho_G_chk=r["rho_G"], rho_FG=r["rho_FG"], par_FG=r["par_FG"]))
    R = pd.DataFrame(rows)
    fx = fx[fx.horizon.isin(["y1", "y5"])].merge(R, on=["field", "grad_window", "horizon"], how="left",
                                                  validate="one_to_one")
    assert fx.par_FG.notna().all() and (fx.n_chk == fx.n_inst).all()
    chk = dict(n_cells=len(fx), max_dF=float(np.max(np.abs(fx.rho_F - fx.rho_F_chk))),
               max_dG=float(np.max(np.abs(fx.rho_G - fx.rho_G_chk))))
    assert chk["max_dF"] < 1e-10 and chk["max_dG"] < 1e-10, chk
    fx["z_par_FG"] = s65.fisher(fx.par_FG.to_numpy(float))
    fx["var_z_par_FG_bw"] = s65.bw_var(fx.par_FG.to_numpy(float), fx.n_inst.to_numpy(float), 1)
    # horizon-fixed sample (sensitivity): institutions present in every window of the horizon, >= NMIN per field
    hrows = []
    for h in ("y1", "y5"):
        X = L[L.horizon == h]
        nwin = X.groupby(["field", "inst_key"]).grad_cohort.transform("nunique")
        X = X[nwin == len(CO[h])]
        for (f, c), g in X.groupby(["field", "grad_cohort"], sort=True):
            if g.inst_key.nunique() < NMIN:
                continue
            assert g.inst_key.is_unique
            r = rank_corrs(g.P.to_numpy(float), g.G.to_numpy(float), g.earnings.to_numpy(float))
            n = len(g)
            hrows.append(dict(field=f, grad_window=int(c), horizon=h, n_inst=n, rho_F=r["rho_F"], rho_G=r["rho_G"],
                              par_FG=r["par_FG"], z_F=float(s65.fisher(r["rho_F"])),
                              z_G=float(s65.fisher(r["rho_G"])), z_par_FG=float(s65.fisher(r["par_FG"])),
                              var_z_F_bw=s65.bw_var(r["rho_F"], n), var_z_G_bw=s65.bw_var(r["rho_G"], n),
                              var_z_par_FG_bw=s65.bw_var(r["par_FG"], n, 1)))
    H = pd.DataFrame(hrows)
    H = H[H.groupby(["field", "horizon"]).grad_window.transform("size") == H.horizon.map({"y1": 7, "y5": 6})]
    return fx.reset_index(drop=True), H.reset_index(drop=True), al.reset_index(drop=True), chk


def standardise(df: pd.DataFrame, col: str = "D_raw") -> tuple:
    dev = df[col] - df.groupby("field")[col].transform("mean")
    N, k = len(df), df.field.nunique()
    s = float(np.sqrt(np.sum(dev ** 2) / (N - k)))
    return dev / s, s


# =============================================================================================
# weighted two-way FE regression, field-clustered wild bootstrap (WCR, Webb), permutation of D
# =============================================================================================
def fe_test(df: pd.DataFrame, y: str, v: str | None, d: str, tag: str) -> dict:
    df = df.sort_values(["field", "grad_window"]).reset_index(drop=True)
    fields = sorted(df.field.unique())
    wins = sorted(df.grad_window.unique())
    N, Gc, W = len(df), len(fields), len(wins)
    fidx = df.field.map({f: i for i, f in enumerate(fields)}).to_numpy()
    widx = df.grad_window.map({c: i for i, c in enumerate(wins)}).to_numpy()
    w = 1.0 / df[v].to_numpy(float) if v else np.ones(N)
    sw = np.sqrt(w)
    OH = np.zeros((N, Gc)); OH[np.arange(N), fidx] = 1.0
    OW = np.zeros((N, W)); OW[np.arange(N), widx] = 1.0
    Z = sw[:, None] * np.column_stack([OH, OW])
    U_, sv, _ = np.linalg.svd(Z, full_matrices=False)
    Q = U_[:, sv > 1e-10 * sv[0]]
    assert Q.shape[1] == Gc + W - 1

    def M(Y):
        return Y - (Y @ Q) @ Q.T

    x = df[d].to_numpy(float)
    yt, xt = M(sw * df[y].to_numpy(float)), M(sw * x)
    sxx = float(xt @ xt)
    beta = float(xt @ yt / sxx)
    e = yt - beta * xt
    q = xt / sxx
    K = 1 + (W - 1)
    scale = Gc / (Gc - 1) * (N - 1) / (N - K)
    se = float(np.sqrt(scale * np.sum(((q * e) @ OH) ** 2)))
    V = WEBB[rng_for(f"wcr:{tag}").integers(6, size=(NWB, Gc))][:, fidx]
    Vu = WEBB[rng_for(f"wcu:{tag}").integers(6, size=(NWB, Gc))][:, fidx]
    Y0 = M(V * yt[None, :])                                 # restricted at beta0 = 0: residuals = yt
    Y1 = xt[None, :] - M(V * xt[None, :])
    B0, B1 = Y0 @ q, Y1 @ q
    R0, R1 = Y0 - B0[:, None] * xt[None, :], Y1 - B1[:, None] * xt[None, :]
    g0, g1 = (R0 * q) @ OH, (R1 * q) @ OH
    inv = dict(B0=B0, B1=B1, a0=scale * (g0 ** 2).sum(1), a1=2 * scale * (g0 * g1).sum(1),
               a2=scale * (g1 ** 2).sum(1))
    t_r = B0 / np.sqrt(inv["a0"])
    p_wcr = float((1 + np.sum(np.abs(t_r) >= abs(beta / se) - 1e-12)) / (1 + NWB))
    q_r = float(np.quantile(np.abs(t_r), 0.95))
    ci = s65.wcr_invert(inv, beta, se)
    assert abs(ci["p0"] - p_wcr) <= 2.0 / (1 + NWB), (tag, ci["p0"], p_wcr)
    Yu = beta * xt[None, :] + M(Vu * e[None, :])          # unrestricted wild bootstrap-t (reported only)
    Bu = Yu @ q
    Ru = Yu - Bu[:, None] * xt[None, :]
    seu = np.sqrt(scale * (((Ru * q) @ OH) ** 2).sum(1))
    q_u = float(np.quantile(np.abs((Bu - beta) / seu), 0.95))
    # field-label permutation of the D trajectories
    Dm = np.full((Gc, W), np.nan); Dm[fidx, widx] = x
    assert np.isfinite(Dm).all(), "unbalanced panel: permutation of trajectories needs every window"
    n_distinct = len({tuple(np.round(r_, 12)) for r_ in Dm})
    rp = rng_for(f"perm:{tag}")
    P = np.empty((NPERM, N))
    for b in range(NPERM):
        P[b] = Dm[rp.permutation(Gc)][fidx, widx]
    Xp = M(sw[None, :] * P)
    bp = (Xp @ yt) / np.einsum("bn,bn->b", Xp, Xp)
    p_perm = float((1 + np.sum(np.abs(bp) >= abs(beta) - 1e-12)) / (1 + NPERM))
    # identifying variation: SD of D after field and window effects (unweighted, balanced panel)
    r_ = x - (OH @ np.linalg.lstsq(OH, x, rcond=None)[0])
    r_ = r_ - OW @ np.linalg.lstsq(OW, r_, rcond=None)[0]
    sd_res = float(np.sqrt(np.sum(r_ ** 2) / (N - Gc - W + 1)))
    mde = float((q_r + Z80) * se)
    return dict(beta=beta, se=se, p_wcr=p_wcr, lo=ci["lo"], hi=ci["hi"], connected=ci["connected"], q_r=q_r,
                lo_u=beta - q_u * se, hi_u=beta + q_u * se, q_u=q_u, mde=mde, p_perm=p_perm,
                power=s65.power(BENCH, se, q_r), N=N, G=Gc, W=W, n_distinct=n_distinct, sd_res=sd_res,
                beta_res=beta * sd_res, verdict=verdict(ci["lo"], ci["hi"], mde))


def verdict(lo, hi, mde) -> str:
    if lo > 0:
        return "rises in hot markets"
    if hi < 0:
        return "falls"
    return "null" if mde <= BENCH else "underpowered"


# =============================================================================================
# formatting
# =============================================================================================
def fm(v, d=3):
    return "—" if v is None or not np.isfinite(v) else f"{v:+.{d}f}"


def fu(v, d=3):
    return "—" if v is None or not np.isfinite(v) else f"{v:.{d}f}"


def fp(p):
    return "—" if not np.isfinite(p) else (f"{p:.3f}" if p >= 0.001 else "<0.001")


def ci_txt(r, d=3):
    return f"[{fm(r['lo'], d)}, {fm(r['hi'], d)}]"


def test_line(r, d=3):
    return (f"beta = {fm(r['beta'], d)} per SD of D, 95% CI (WCR inversion) {ci_txt(r, d)}, WCR p = {fp(r['p_wcr'])}, "
            f"field-label permutation p = {fp(r['p_perm'])}, MDE {fu(r['mde'], d)} (power vs 0.05: "
            f"{fu(r['power'], 2)}); unrestricted wild bootstrap-t CI [{fm(r['lo_u'], d)}, {fm(r['hi_u'], d)}]; "
            f"N = {r['N']} cells, {r['G']} fields, {r['W']} windows")


# =============================================================================================
# main
# =============================================================================================
def attach(df: pd.DataFrame, DM: dict) -> pd.DataFrame:
    out = df.copy()
    for comp, col in (("g_bill", "D_raw"), ("g_emp", "D_raw_emp"), ("g_wage", "D_raw_wage")):
        Wc = DM[f"W_{comp}"][["field", "grad_window", "horizon", "D_raw", "min_cov"]].rename(
            columns={"D_raw": col, "min_cov": f"min_cov_{comp}"})
        out = out.merge(Wc, on=["field", "grad_window", "horizon"], how="left", validate="many_to_one")
        assert out[col].notna().all(), comp
    return out


def std_all(df: pd.DataFrame) -> tuple:
    df = df.copy()
    sd = {}
    for raw, col in (("D_raw", "D"), ("D_raw_emp", "D_emp"), ("D_raw_wage", "D_wage")):
        df[col], sd[col] = standardise(df, raw)
    return df, sd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    s = Path(__file__).read_text()
    pre = s[s.index("1. Field demand index D_{f,t}"):s.index("END OF PRE-SPECIFICATION.")].rstrip() + "\n"
    op = s[s.index("OPERATIONAL DEFINITIONS (fixed"):s.index("END OF OPERATIONAL DEFINITIONS.")].rstrip() + "\n"
    md5s = dict(pre=hashlib.md5(pre.encode()).hexdigest(), op=hashlib.md5(op.encode()).hexdigest())
    prov = check_provenance()
    DM = build_demand(args.workers)
    G = DM["G"]
    G.to_csv(OUT_G, index=False, float_format="%.10g")
    A = DM["A_g_bill"].rename(columns={"D": "D_bill", "cov": "cov_bill"})
    for comp in ("g_emp", "g_wage"):
        A = A.merge(DM[f"A_{comp}"].rename(columns={"D": f"D_{comp[2:]}", "cov": f"cov_{comp[2:]}"}),
                    on=["field", "year"])
    WI = DM["W_g_bill"]
    for comp in ("g_emp", "g_wage"):
        WI = WI.merge(DM[f"W_{comp}"].rename(columns={"D_raw": f"D_raw_{comp[2:]}", "min_cov": f"min_cov_{comp[2:]}"}),
                      on=["field", "grad_window", "horizon", "earn_years"])
    pd.concat([A.assign(kind="annual"), WI.assign(kind="window")], ignore_index=True).to_csv(
        OUT_D, index=False, float_format="%.10g")

    # sanity check of D (O10): annual index relative to the mean over all mapped fields
    piv = A.pivot(index="year", columns="field", values="D_bill")
    rel = piv.sub(piv.mean(axis=1), axis=0)
    SAN = dict(n_fields=piv.shape[1], cs_2002=float(rel.loc[2002, "computer_science"]),
               cs_min_year=int(rel["computer_science"].idxmin()),
               cs_2003_04=float(rel.loc[[2003, 2004], "computer_science"].mean()),
               cs_2011_15=float(rel.loc[2011:2015, "computer_science"].mean()),
               fin_2008_10=float(rel.loc[2008:2010, "finance"].mean()),
               eco_2008_10=float(rel.loc[2008:2010, "economics"].mean()),
               nur_2008_10=float(rel.loc[2008:2010, "nursing"].mean()),
               cs_w2001_y1=float(rel.loc[2002:2004, "computer_science"].mean()))

    stage("outcome cells")
    fx, H, AL, chk = outcome_cells()
    fx, H = attach(fx, DM), attach(H, DM)
    c1, sd1 = std_all(fx[fx.horizon == "y1"])
    c5, sd5 = std_all(fx[fx.horizon == "y5"])
    h1, sdh1 = std_all(H[H.horizon == "y1"])
    h5, sdh5 = std_all(H[H.horizon == "y5"])

    stage("tests")
    T = {}
    T["T1"] = fe_test(c1, "z_F", "var_z_F_bw", "D", "T1")
    T["T2"] = fe_test(c1, "z_par_FG", "var_z_par_FG_bw", "D", "T2")
    T["T3"] = fe_test(c5, "z_F", "var_z_F_bw", "D", "T3")
    SPEC = {"T1": (c1, h1, "z_F", "var_z_F_bw"), "T2": (c1, h1, "z_par_FG", "var_z_par_FG_bw"),
            "T3": (c5, h5, "z_F", "var_z_F_bw")}
    SEN = {}
    for k, (cc, hh, y, v) in SPEC.items():
        SEN[(k, "unweighted")] = fe_test(cc, y, None, "D", f"{k}:unw")
        SEN[(k, "employment-only D")] = fe_test(cc, y, v, "D_emp", f"{k}:emp")
        SEN[(k, "real-wage-only D")] = fe_test(cc, y, v, "D_wage", f"{k}:wage")
        SEN[(k, "horizon-fixed sample")] = fe_test(hh, y, v, "D", f"{k}:hfix")
    EXP = {"z_G, y1": fe_test(c1, "z_G", "var_z_G_bw", "D", "X:G1"),
           "z_G, y5": fe_test(c5, "z_G", "var_z_G_bw", "D", "X:G5")}
    for k, r in T.items():
        rec("test", k, r["beta"], r["lo"], r["hi"], r["se"], r["p_wcr"], r["G"], r["N"], FIXED,
            f"verdict={r['verdict']}; MDE={r['mde']:.4f}; perm p={r['p_perm']:.4f}; "
            f"unrestricted CI=[{r['lo_u']:.4f},{r['hi_u']:.4f}]; beta per residual SD={r['beta_res']:.4f}")
    for (k, nm), r in SEN.items():
        rec("sensitivity", f"{k}: {nm}", r["beta"], r["lo"], r["hi"], r["se"], r["p_wcr"], r["G"], r["N"],
            "horizon-fixed" if "horizon" in nm else FIXED, f"MDE={r['mde']:.4f}; perm p={r['p_perm']:.4f}")
    for nm, r in EXP.items():
        rec("exploratory", nm, r["beta"], r["lo"], r["hi"], r["se"], r["p_wcr"], r["G"], r["N"], FIXED,
            f"MDE={r['mde']:.4f}; perm p={r['p_perm']:.4f}")

    # cells file
    keep = ["field", "grad_window", "horizon", "earn_years", "n_inst", "rho_F", "rho_G", "par_FG", "z_F", "z_G",
            "z_par_FG", "var_z_F_bw", "var_z_G_bw", "var_z_par_FG_bw", "D_raw", "D_raw_emp", "D_raw_wage", "D",
            "D_emp", "D_wage"]
    pd.concat([c1[keep].assign(sample=FIXED), c5[keep].assign(sample=FIXED),
               h1[[k for k in keep if k != "earn_years"]].assign(sample="horizon-fixed"),
               h5[[k for k in keep if k != "earn_years"]].assign(sample="horizon-fixed")],
              ignore_index=True).to_csv(OUT_CELLS, index=False, float_format="%.10g")

    # case studies (descriptive)
    CS = case_studies(c1, c5, AL, WI, sd1, sd5)
    stage("figure")
    make_figure(A, c1, c5, AL, WI, sd1, sd5, T)
    pd.DataFrame(RES).to_csv(OUT_RES, index=False, float_format="%.10g")
    write_md(md5s, prov, DM, SAN, chk, fx, H, c1, c5, h1, h5, sd1, sd5, sdh1, sdh5, T, SEN, EXP, CS, WI)
    stage("done")


def case_studies(c1, c5, AL, WI, sd1, sd5) -> dict:
    out = {}
    cc = {"y1": c1, "y5": c5}
    sdd = {"y1": sd1["D"], "y5": sd5["D"]}
    rows = []
    for f in ("computer_science", "computer_engineering"):
        for h in ("y1", "y5"):
            wi = WI[(WI.field == f) & (WI.horizon == h)].set_index("grad_window")
            dstd = (wi.D_raw - wi.D_raw.mean()) / sdd[h]
            fxh = cc[h].set_index(["field", "grad_window"])
            al = AL[(AL.field == f) & (AL.horizon == h)].set_index("grad_window")
            for c in CO[h]:
                c = int(c)
                r = dict(field=f, horizon=h, window=c, earn_years=s65.earn_years(c, h), D_raw=float(wi.D_raw[c]),
                         D=float(dstd[c]))
                if (f, c) in fxh.index:
                    r.update(rho_F_fixed=float(fxh.loc[(f, c), "rho_F"]), par_FG_fixed=float(fxh.loc[(f, c), "par_FG"]),
                             n_fixed=int(fxh.loc[(f, c), "n_inst"]))
                if c in al.index:
                    r.update(rho_F_all=float(al.loc[c, "rho_F"]), n_all=int(al.loc[c, "n_inst"]))
                rows.append(r)
    out["computing"] = pd.DataFrame(rows)
    rows = []
    for f in ("finance", "economics"):
        for h in ("y1", "y5"):
            x = cc[h]
            wm = x.groupby("grad_window").rho_F.mean()
            wp = x.groupby("grad_window").par_FG.mean()
            for c in (2004, 2007, 2010):
                r_ = x[(x.field == f) & (x.grad_window == c)].iloc[0]
                rows.append(dict(field=f, horizon=h, window=c, earn_years=s65.earn_years(c, h), D=float(r_.D),
                                 D_raw=float(r_.D_raw), rho_F=float(r_.rho_F), mean_rho_F_all_fields=float(wm[c]),
                                 par_FG=float(r_.par_FG), mean_par_FG_all_fields=float(wp[c]), n=int(r_.n_inst)))
    out["finance"] = pd.DataFrame(rows)
    rows = []
    for h, x in (("y1", c1), ("y5", c5)):
        # two-way demeaned z_F on the balanced fixed17 panel (equals the unweighted two-way FE residual)
        zt = x.z_F - x.groupby("field").z_F.transform("mean") - x.groupby("grad_window").z_F.transform("mean") \
            + x.z_F.mean()
        fmn = x.groupby("field").rho_F.transform("mean")
        big = x[np.abs(x.D) >= 2].index
        for i in big:
            rows.append(dict(field=x.loc[i, "field"], horizon=h, window=int(x.loc[i, "grad_window"]),
                             earn_years=x.loc[i, "earn_years"], D=float(x.loc[i, "D"]), rho_F=float(x.loc[i, "rho_F"]),
                             field_mean_rho_F=float(fmn[i]), z_F_twoway_resid=float(zt[i]),
                             par_FG=float(x.loc[i, "par_FG"])))
    out["big"] = pd.DataFrame(rows).sort_values(["horizon", "field", "window"]).reset_index(drop=True) if rows \
        else pd.DataFrame()
    out["n_cells"] = {"y1": len(c1), "y5": len(c5)}
    return out


def add_rel(x: pd.DataFrame, s_h: float, ref: pd.DataFrame) -> pd.Series:
    """Two-way-demeaned index in SD units: D_raw minus the fixed17 window mean, demeaned over the field's windows."""
    wm = ref.groupby("grad_window").D_raw.mean()
    r = x.D_raw - x.grad_window.map(wm)
    return (r - r.groupby(x.field).transform("mean")) / s_h


def make_figure(A, c1, c5, AL, WI, sd1, sd5, T):
    piv = A.pivot(index="year", columns="field", values="D_bill")
    rel = piv.sub(piv.mean(axis=1), axis=0)
    fig, ax = plt.subplots(2, 2, figsize=(12.5, 9.0))
    a = ax[0, 0]
    sty = {"computer_science": ("#1f4e9c", "-"), "finance": ("#c0392b", "-"), "economics": ("#e67e22", "--"),
           "nursing": ("#2e8b57", "-"), "mechanical_engineering": ("#7f7f7f", ":")}
    for f, (col, ls) in sty.items():
        a.plot(rel.index, 100 * rel[f], color=col, ls=ls, lw=1.8, label=s65.LAB.get(f, f))
    a.axhline(0, color="k", lw=0.6)
    a.set_title("(a) Field demand index relative to the mean of 65 fields\n(log growth of the real wage bill, x100)",
                fontsize=10)
    a.set_xlabel("calendar year (growth from the previous year)")
    a.legend(fontsize=8, frameon=False)
    # (b) computing at y1 and y5
    a = ax[0, 1]
    for h, x_, mk in (("y1", c1, "o"), ("y5", c5, "s")):
        cs = x_[x_.field == "computer_science"].sort_values("grad_window")
        a.plot(cs.grad_window, cs.rho_F, marker=mk, color="#1f4e9c", lw=1.8, label=f"CS, fixed institutions, {h}",
               ls="-" if h == "y1" else "--")
        ce = AL[(AL.field == "computer_engineering") & (AL.horizon == h)].sort_values("grad_window")
        a.plot(ce.grad_window, ce.rho_F, marker=mk, color="#8e44ad", lw=1.2, ls="-" if h == "y1" else "--",
               label=f"Comp. eng., all institutions, {h}", alpha=0.8)
    a.set_ylabel("Spearman(F, median earnings)")
    a.set_xlabel("graduation window (first year)")
    a2 = a.twinx()
    for h, x_, sd, off in (("y1", c1, sd1["D"], -0.45), ("y5", c5, sd5["D"], 0.45)):
        cs = x_[x_.field == "computer_science"].sort_values("grad_window")
        rr = add_rel(x_, sd, x_).loc[cs.index]
        a2.bar(cs.grad_window + off, rr, width=0.8, color="#1f4e9c", alpha=0.18 if h == "y1" else 0.35)
    a2.axhline(0, color="k", lw=0.4)
    a2.set_ylabel("CS demand, net of window means (SD)\nbars: light = y1, dark = y5", fontsize=8)
    a2.set_ylim(-3, 3)
    a.set_title("(b) Computing: coupling by window (lines), demand (bars)\ndescriptive", fontsize=10)
    a.set_xticks([int(c) for c in CO["y1"]])
    a.legend(fontsize=7, frameon=False, loc="lower right")
    # (c) finance and economics around 2007-09
    a = ax[1, 0]
    for f, col in (("finance", "#c0392b"), ("economics", "#e67e22")):
        for h, x_, ls in (("y1", c1, "-"), ("y5", c5, "--")):
            z = x_[x_.field == f].sort_values("grad_window")
            a.plot(z.grad_window, z.rho_F, color=col, ls=ls, marker="o", ms=3, lw=1.5, label=f"{s65.LAB.get(f, f)}, {h}")
    for h, x_, ls in (("y1", c1, "-"), ("y5", c5, "--")):
        m = x_.groupby("grad_window").rho_F.mean()
        a.plot(m.index, m.values, color="k", ls=ls, lw=1.0, alpha=0.6, label=f"mean of 24 fields, {h}")
    a.axvspan(2006.0, 2008.0, color="#c0392b", alpha=0.08)
    a.set_xlabel("graduation window (first year)")
    a.set_ylabel("Spearman(F, median earnings)")
    a.set_title("(c) Finance and economics, fixed institutions\nshaded: 2007-09 window; descriptive", fontsize=10)
    a.set_xticks([int(c) for c in CO["y1"]])
    a.legend(fontsize=7, frameon=False, ncol=2)
    # (d) pooled within-field, within-window relation
    a = ax[1, 1]
    for h, x_, r, col in (("y1", c1, T["T1"], "#1f4e9c"), ("y5", c5, T["T3"], "#c0392b")):
        zt = x_.z_F - x_.groupby("field").z_F.transform("mean") - x_.groupby("grad_window").z_F.transform("mean") \
            + x_.z_F.mean()
        dt = x_.D - x_.groupby("grad_window").D.transform("mean")
        a.scatter(dt, zt, s=12, color=col, alpha=0.55, label=f"{h} cells (T{'1' if h == 'y1' else '3'})")
        g = np.linspace(dt.min(), dt.max(), 10)
        a.plot(g, r["beta"] * g, color=col, lw=1.6)
    a.axhline(0, color="k", lw=0.5); a.axvline(0, color="k", lw=0.5)
    a.set_xlabel("D net of field and window means (SD units)")
    a.set_ylabel("Fisher z coupling net of field and window means")
    a.set_title(f"(d) T1 slope {T['T1']['beta']:+.3f}, T3 slope {T['T3']['beta']:+.3f} per SD (weighted FE fits)",
                fontsize=10)
    a.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=150, metadata={"Software": None})
    plt.close(fig)


def write_md(md5s, prov, DM, SAN, chk, fx, H, c1, c5, h1, h5, sd1, sd5, sdh1, sdh5, T, SEN, EXP, CS, WI):
    G, S, cov, det = DM["G"], DM["S"], DM["cov"], DM["det"]
    L = []
    A_ = L.append
    s = Path(__file__).read_text()
    pre = s[s.index("1. Field demand index D_{f,t}"):s.index("END OF PRE-SPECIFICATION.")].rstrip()
    op = s[s.index("OPERATIONAL DEFINITIONS (fixed"):s.index("END OF OPERATIONAL DEFINITIONS.")].rstrip()
    v = {k: T[k]["verdict"] for k in T}
    nf1, nf5 = c1.field.nunique(), c5.field.nunique()
    ninst = fx[fx.horizon == "y1"].groupby("field").n_inst.first()
    rel1, rel5 = add_rel(c1, sd1["D"], c1), add_rel(c5, sd5["D"], c5)
    meth = G.groupby("method").size().to_dict()
    comp_rows = G[G.method == "component"]
    ncomp = len(comp_rows)
    cov_min = float(DM["A_g_bill"][DM["A_g_bill"].field.isin(c1.field.unique())]["cov"].min())
    oes_n = det.groupby("year").occ_code.size()
    acs_min = min(cov[f]["n_persons"] for f in c1.field.unique())
    acs_inoes = min(cov[f]["share_in_oes"] for f in c1.field.unique())

    # ---- descriptive case-study quantities (used in the Answer and in item 7)
    cmp_ = CS["computing"]
    fin = CS["finance"]
    big = CS["big"]
    def net_rho(x_, f):
        wm = x_.groupby("grad_window").rho_F.transform("mean")
        z = x_[x_.field == f].sort_values("grad_window")
        return (z.rho_F - wm.loc[z.index]), z
    def sp(x_, rel, f, col="rho_F"):
        z = x_[x_.field == f].sort_values("grad_window")
        return float(spearmanr(z[col], rel.loc[z.index])[0])
    def rises(x_, f):
        z = x_[x_.field == f].sort_values("grad_window").rho_F.to_numpy()
        return int(np.sum(np.diff(z) > 0)), len(z) - 1
    up1, n1 = rises(c1, "computer_science"); up5, n5 = rises(c5, "computer_science")
    nr1, z1 = net_rho(c1, "computer_science"); nr5, z5 = net_rho(c5, "computer_science")
    sp_net1 = float(spearmanr(nr1, rel1.loc[z1.index])[0]); sp_net5 = float(spearmanr(nr5, rel5.loc[z5.index])[0])
    def fin_dev(f, h):
        x = fin[(fin.field == f) & (fin.horizon == h)].set_index("window")
        return float(x.rho_F[2007] - (x.rho_F[2004] + x.rho_F[2010]) / 2), \
            float(x.mean_rho_F_all_fields[2007] - (x.mean_rho_F_all_fields[2004] + x.mean_rho_F_all_fields[2010]) / 2)
    fd1, ad1 = fin_dev("finance", "y1"); ed1, _ = fin_dev("economics", "y1")
    fd5, ad5 = fin_dev("finance", "y5"); ed5, _ = fin_dev("economics", "y5")
    frel = float(rel1[(c1.field == "finance") & (c1.grad_window == 2007)].iloc[0])
    erel = float(rel1[(c1.field == "economics") & (c1.grad_window == 2007)].iloc[0])
    csy1 = cmp_[(cmp_.field == "computer_science") & (cmp_.horizon == "y1")].set_index("window")
    cey1 = cmp_[(cmp_.field == "computer_engineering") & (cmp_.horizon == "y1")].set_index("window")
    cs_low = bool(csy1.rho_F_fixed.idxmin() == 2001 and cey1.rho_F_all.idxmin() == 2001)
    ce_cs_diff = float(np.max(np.abs(WI[WI.field == "computer_science"].set_index(["horizon", "grad_window"]).D_raw
                                     - WI[WI.field == "computer_engineering"].set_index(["horizon", "grad_window"]).D_raw)))
    nbig = len(big)
    nneg = int((big.D < 0).sum()) if nbig else 0
    nres_hi = int((big.z_F_twoway_resid > 0.1).sum()) if nbig else 0
    CS_SUM = (f"Descriptively (no test): computer science's y1 coupling rises in {up1} of {n1} window steps, from "
              f"{fu(csy1.rho_F_fixed[2001])} (2001-03) to {fu(csy1.rho_F_fixed[2019])} (2019-21); net of the 24-field "
              f"window mean, its rank correlation with computing's relative demand is {fm(sp_net1, 2)} across the "
              f"{n1 + 1} y1 windows and {fm(sp_net5, 2)} across the {n5 + 1} y5 windows"
              + ("; the dot-com bust window (2001-03) has both its lowest relative demand and its lowest relative "
                 "y1 coupling, a single window" if (int(z1.grad_window.iloc[int(np.argmin(rel1.loc[z1.index].to_numpy()))])
                                                   == 2001 and int(z1.grad_window.iloc[int(np.argmin(nr1.to_numpy()))])
                                                   == 2001) else "")
              + f". Finance and economics, whose demand fell relative to "
              f"other fields in the 2007-09 window's y1 earnings years (D net of window means {fm(frel, 2)} and "
              f"{fm(erel, 2)}), deviate from their neighbouring windows by {fm(fd1)} and {fm(ed1)} in y1 coupling, "
              f"against {fm(ad1)} for the 24-field mean. {nbig} cells reach |D| >= 2 SD"
              + (f", {nneg} of them on the weak-demand side; in {nres_hi} of them coupling is more than 0.1 (Fisher z) "
                 "above its field and window means" if nbig else ""))

    mres = {k: T[k]["mde"] * T[k]["sd_res"] for k in T}
    piv_ = DM["A_g_bill"].pivot(index="year", columns="field", values="D")
    relA = piv_.sub(piv_.mean(axis=1), axis=0)["computer_science"]
    g21 = G[(G.minor == "15-1") & (G.year == 2021)].iloc[0]
    d20, d21 = det[(det.year == 2020) & (det.minor == "15-1")], det[(det.year == 2021) & (det.minor == "15-1")]
    gtot21 = float(np.log(d21.emp[d21.emp > 0].sum() / d20.emp[d20.emp > 0].sum()))
    SWING = (f"Computing's relative annual index swings from {100 * relA[2021]:+.2f} in 2021 to "
             f"{100 * relA[2022]:+.2f} in 2022 (log points x100). The 2020->2021 step of computer occupations (15-1) "
             f"uses {g21['method']} codes covering {g21['cov_prev']:.2f} / {g21['cov']:.2f} of the group's employment, with "
             f"employment growth {g21['g_emp']:+.3f} against {gtot21:+.3f} on group totals. This step enters the y1 "
             "2019-21 and y5 2016-18 windows of computer science and computer engineering, and was not re-tuned "
             "after outcomes.")
    RES_SD = ("*Post hoc, not part of the verdict:* measured per SD of the demand variation left after field and "
              f"window effects, the MDEs are {fu(mres['T1'])} (T1), {fu(mres['T2'])} (T2) and {fu(mres['T3'])} (T3)"
              + (", all below 0.05, so in that unit the same rule would read 'null' for all three; the unit fixed "
                 "before outcomes (O5, pooled within-field SD) gives 'underpowered'. "
                 if all(T[k]["verdict"] == "underpowered" for k in T) and max(mres.values()) <= BENCH
                 else "; the verdicts use the unit fixed in O5. "))
    A_("# Field demand shocks and within-field coupling (PSEO V4.14.1; national occupational demand from BLS OES "
       "2001-2023)")
    A_("")
    A_("Script: `scripts/79_field_demand_shocks.py` (seeded with numpy SeedSequence; outputs byte-identical on re-run). "
       "It imports scripts/65 (PSEO cells, earnings years, Fisher z, Bonett-Wright variances, WCR test inversion) and "
       "scripts/69 (field -> ACS field-of-degree map); neither is edited. Descriptive, not causal. Outputs: "
       "`data/interim/field_demand_index.csv` (annual and window demand index per field), "
       "`data/interim/field_demand_oes_minor_growth.csv` (occupation-group growth), "
       "`data/interim/field_demand_acs_fod_minor.csv` (ACS field-of-degree x occupation counts), "
       "`data/interim/field_demand_cells.csv` (test cells), `data/interim/field_demand_shocks_results.csv` (every "
       "estimate), `outputs/figures/field_demand_shocks.png`. The pre-specification (items 1-6, verbatim"
       f"; md5 `{md5s['pre']}`) was written into the script and into this file on {RUN_DATE} before "
       "any outcome data were read by the script; the operational definitions O1-O10 (md5 "
       f"`{md5s['op']}`) were added the same day after the demand index (which uses no institution or earnings data) "
       "had been built and inspected, and also before any outcome data were read. Both timing claims are "
       "self-reported: the script was not committed or hashed in git before the estimating run. What had been seen "
       "before each freeze: COUPLING_DYNAMICS_RESULT.md (all-field, window-level results of scripts/65) was read "
       "before items 1-6 were written; the panel's sample, field, window and n_inst columns "
       "(no coupling values) were read before O1-O10; no field x window coupling value was seen before either "
       "block. Everything not in "
       "items 1-6 or O1-O10 is labelled exploratory.")
    A_("")
    A_("**Demand source used: BLS OES national files, taken from Internet Archive (Wayback Machine) copies of the "
       "bls.gov files**, because bls.gov answered HTTP 403 to every scripted request. The Census ACS API fallback "
       "named in item 1 was not used. It starts in 2009 and would lose the 2001-03 and 2004-06 y1 windows, including "
       "the dot-com bust. This departs from the literal wording of item 1 (O1). Shares: ACS 2023 PUMS, field of degree x "
       "occupation (O4).")
    A_("")
    A_("## Answer")
    A_("")
    allu = all(x == "underpowered" for x in v.values())
    opening = ("The data cannot tell at the pre-set precision. All three pre-specified tests have 95% CIs that include 0 "
               "and MDEs above 0.05 per SD of the demand index. " if allu else "")
    mdes = [T[k]["mde"] for k in T]
    A_("**Key question: when the national labour market for a field's graduates gets better or worse, do employers' "
       "rankings of programmes move closer to or further from the academic ranking, and is the department-specific "
       "part (F beyond G) priced more in a hot market?** " + opening + "The verdicts "
       f"are T1 **{v['T1']}**, T2 **{v['T2']}** and T3 **{v['T3']}**. T1 (y1, coupling of the field rank F with "
       f"earnings): beta = {fm(T['T1']['beta'])} per SD of D {ci_txt(T['T1'])}, MDE {fu(T['T1']['mde'])}. T2 (y1, "
       f"partial coupling of F given G): {fm(T['T2']['beta'])} {ci_txt(T['T2'])}, MDE {fu(T['T2']['mde'])}. T3 (y5): "
       f"{fm(T['T3']['beta'])} {ci_txt(T['T3'])}, MDE {fu(T['T3']['mde'])}. "
       + (f"Effects as large as {min(mdes):.2f}-{max(mdes):.2f} in Fisher z per SD of field demand are therefore not "
          "ruled out, in either direction. " if allu else "") + "One reason is the demand variation "
       "itself. Most of a field's demand swings are national swings shared by all fields, which the window effects "
       f"absorb. After field and window effects, only {fu(T['T1']['sd_res'], 2)} SD (y1) and "
       f"{fu(T['T3']['sd_res'], 2)} SD (y5) of D remain to identify beta. " + RES_SD + CS_SUM + " (item 7).")
    A_("")
    # item 1
    r_ = SAN
    A_(f"1. **Demand index (O1-O5).** National occupational demand comes from {len(OES_YEARS)} BLS OES national files "
       f"({OES_YEARS[0]}-{OES_YEARS[-1]}; {oes_n.min()}-{oes_n.max()} detailed occupations per year). They are grouped "
       f"into {G.minor.nunique()} SOC minor groups. g = log growth of the real wage bill (employment growth plus "
       "real mean-wage growth, CPI-U). Growth over matched codes: "
       f"{meth.get('matched', 0)} group-years. Crosswalk-component growth at SOC-revision transitions: {ncomp} "
       f"group-years. Undefined (group absent in one year): {meth.get('missing', 0)}. Shares come from the ACS 2023 "
       "PUMS (bachelor's as highest degree, aged 23-35, civilian employed). The test fields have between "
       f"{acs_min:,} and {max(cov[f]['n_persons'] for f in c1.field.unique()):,} sample persons each; at least "
       f"{100 * acs_inoes:.1f}% of each field's weighted persons are in OES occupation groups, and at least "
       f"{100 * cov_min:.1f}% of each field's share has a defined growth in every year. Sanity check (O10; relative "
       f"to the mean of {r_['n_fields']} mapped fields, log points x100): computing is lowest in {r_['cs_min_year']} "
       f"({100 * r_['cs_2002']:+.2f}) and above the mean in 2003-04 ({100 * r_['cs_2003_04']:+.2f} per year) and "
       f"2011-15 ({100 * r_['cs_2011_15']:+.2f}). Finance is at {100 * r_['fin_2008_10']:+.2f} and economics at "
       f"{100 * r_['eco_2008_10']:+.2f} in 2008-10, and nursing at {100 * r_['nur_2008_10']:+.2f}. Over computing's "
       f"2001-03 y1 earnings years (2002-04) the relative index averages {100 * r_['cs_w2001_y1']:+.2f}: in the "
       "window index the dot-com bust shows up only as a shortfall against computing's otherwise above-average "
       f"growth ({r_['cs_min_year']} dip, 2003-04 recovery). Pooled within-field SD of "
       f"the window index (the unit of D): {100 * sd1['D']:.2f} log points per year at y1 and {100 * sd5['D']:.2f} at "
       "y5.")
    for i, (k, lab) in enumerate((("T1", "T1 -- y1, Spearman(F, p50) (pre-specified)"),
                                  ("T2", "T2 -- y1, partial Spearman(F, p50 | G), the department part beyond the "
                                         "university (pre-specified)"),
                                  ("T3", "T3 -- y5, Spearman(F, p50), D over the y5 earnings years (pre-specified)")),
                                 start=2):
        r = T[k]
        A_(f"{i}. **{lab}.** Fixed institutions (scripts/65 sample fixed17: {r['G']} fields, "
           f"{ninst.min()}-{ninst.max()} institutions per field). {test_line(r)}. Verdict: **{r['verdict']}**. "
           f"{r['n_distinct']} distinct D trajectories enter the permutation; after field and window effects the "
           f"SD of D is {fu(r['sd_res'], 2)}, so per residual SD beta is {fm(r['beta_res'])} and the MDE "
           f"{fu(r['mde'] * r['sd_res'])} (post hoc rescaling, no verdict). The 95% acceptance set "
           f"of the WCR test is {'one interval' if r['connected'] else 'not one interval (hull shown)'}.")
    A_("   T2 uses par_FG, rebuilt here, because the panel's par_F is the partial on PSEO coverage and exists only for "
       f"the all-institution sample (O6). The rebuilt Spearman(F, p50) and Spearman(G, p50) match the panel on all "
       f"{chk['n_cells']} fixed17 y1/y5 cells (max |diff| {chk['max_dF']:.1e} and {chk['max_dG']:.1e}).")
    # sensitivities
    sl = []
    for k in ("T1", "T2", "T3"):
        parts = [f"{nm} {fm(SEN[(k, nm)]['beta'])} {ci_txt(SEN[(k, nm)])} (MDE {fu(SEN[(k, nm)]['mde'])}"
                 + (f"; {SEN[(k, nm)]['G']} fields" if "horizon" in nm else "") + ")"
                 for nm in ("unweighted", "employment-only D", "real-wage-only D", "horizon-fixed sample")]
        sl.append(f"{k}: " + "; ".join(parts))
    nsen = sum(1 for r in SEN.values() if r["lo"] > 0 or r["hi"] < 0)
    A_(f"5. **Sensitivities (pre-specified in O8, no verdict).** " + ". ".join(sl) + f". {nsen} of {len(SEN)} "
       "sensitivity CIs exclude 0.")
    A_(f"6. **Exploratory: Spearman(G, p50) as outcome.** y1: {test_line(EXP['z_G, y1'])}. y5: "
       f"{test_line(EXP['z_G, y5'])}.")
    # case studies
    def cs_seq(f, h, col):
        x = cmp_[(cmp_.field == f) & (cmp_.horizon == h)]
        return ", ".join(f"{w}: {fu(val)}" for w, val in zip(x.window, x[col]))
    def rel_seq(x_, rel, f):
        z = x_[x_.field == f].sort_values("grad_window")
        return ", ".join(f"{w}: {fm(val, 2)}" for w, val in zip(z.grad_window, rel.loc[z.index]))
    A_("7. **Case studies (descriptive; no test).**")
    A_(f"   (a) *Computing.* Computer science, fixed institutions, Spearman(F, p50) at y1 by window: "
       f"{cs_seq('computer_science', 'y1', 'rho_F_fixed')}. It rises in {up1} of {n1} window steps. Its demand index "
       f"net of window means (SD units) is {rel_seq(c1, rel1, 'computer_science')}; Spearman across the {n1 + 1} "
       f"windows is {fm(sp(c1, rel1, 'computer_science'), 2)} with raw coupling (which carries the upward drift common to "
       f"all fields) and {fm(sp_net1, 2)} with coupling net of the 24-field window mean "
       f"({', '.join(f'{w}: {fm(val)}' for w, val in zip(z1.grad_window, nr1))}). At y5: {cs_seq('computer_science', 'y5', 'rho_F_fixed')} "
       f"({up5} of {n5} steps up); D net of window means {rel_seq(c5, rel5, 'computer_science')}; Spearman "
       f"{fm(sp(c5, rel5, 'computer_science'), 2)} (net of window means {fm(sp_net5, 2)}). Computer engineering is not in fixed17, so its rows use the "
       "all-institution cells, whose institutions change across windows (O9). y1: "
       f"{cs_seq('computer_engineering', 'y1', 'rho_F_all')}; y5: {cs_seq('computer_engineering', 'y5', 'rho_F_all')}. "
       f"Its window index differs from computer science's by at most {100 * ce_cs_diff:.2f} log points x100 per year "
       "(Appendix A). The 2001-03 window is the dot-com bust cohort. For computer science it is the window with "
       + ("the lowest" if int(z1.grad_window.iloc[int(np.argmin(rel1.loc[z1.index].to_numpy()))]) == 2001
          else "not the lowest")
       + f" demand net of window means ({fm(float(rel1.loc[z1.index].iloc[0]), 2)} SD) and "
       + ("the lowest" if int(z1.grad_window.iloc[int(np.argmin(nr1.to_numpy()))]) == 2001 else "not the lowest")
       + f" coupling net of the 24-field window mean ({fm(float(nr1.iloc[0]))})"
       + ("; for both computing fields it has the lowest raw y1 coupling" if cs_low else "")
       + f". Across all {n1 + 1} windows the two net series have a rank correlation of {fm(sp_net1, 2)}.")
    fr = fin.set_index(["field", "horizon", "window"])
    A_(f"   (b) *Finance and economics around 2007-09.* y1 window 2007-09 (earnings 2008-10): D = "
       f"{fm(fr.loc[('finance', 'y1', 2007), 'D'], 2)} (finance) and {fm(fr.loc[('economics', 'y1', 2007), 'D'], 2)} "
       f"(economics). Net of the window mean over the 24 fields, D = "
       f"{fm(rel1[(c1.field == 'finance') & (c1.grad_window == 2007)].iloc[0], 2)} and "
       f"{fm(rel1[(c1.field == 'economics') & (c1.grad_window == 2007)].iloc[0], 2)}. Spearman(F, p50) across 2004-06 / "
       f"2007-09 / 2010-12 is {fu(fr.loc[('finance', 'y1', 2004), 'rho_F'])} / "
       f"{fu(fr.loc[('finance', 'y1', 2007), 'rho_F'])} / {fu(fr.loc[('finance', 'y1', 2010), 'rho_F'])} for finance "
       f"and {fu(fr.loc[('economics', 'y1', 2004), 'rho_F'])} / {fu(fr.loc[('economics', 'y1', 2007), 'rho_F'])} / "
       f"{fu(fr.loc[('economics', 'y1', 2010), 'rho_F'])} for economics. The 2007-09 value minus the mean of its "
       f"two neighbours is {fm(fd1)} (finance) and {fm(ed1)} (economics), against {fm(ad1)} for the mean of the 24 "
       f"fields. At y5 the recession falls in the 2004-06 window's earnings years (2009-11: D = "
       f"{fm(fr.loc[('finance', 'y5', 2004), 'D'], 2)} finance, {fm(fr.loc[('economics', 'y5', 2004), 'D'], 2)} "
       f"economics), and the same 2007-09 deviation is {fm(fd5)} and {fm(ed5)} (24-field mean {fm(ad5)}). Partial "
       f"coupling given G at y1, 2004-06 / 2007-09 / 2010-12: finance {fu(fr.loc[('finance', 'y1', 2004), 'par_FG'])} / "
       f"{fu(fr.loc[('finance', 'y1', 2007), 'par_FG'])} / {fu(fr.loc[('finance', 'y1', 2010), 'par_FG'])}; economics "
       f"{fu(fr.loc[('economics', 'y1', 2004), 'par_FG'])} / {fu(fr.loc[('economics', 'y1', 2007), 'par_FG'])} / "
       f"{fu(fr.loc[('economics', 'y1', 2010), 'par_FG'])}.")
    if len(big):
        bl = "; ".join(f"{s65.LAB.get(r.field, r.field)} {r.horizon} {r.window} (earnings {r.earn_years}): D = "
                       f"{fm(r.D, 2)}, Spearman(F, p50) {fu(r.rho_F)} vs the field's mean over windows "
                       f"{fu(r.field_mean_rho_F)}, z_F net of field and window means {fm(r.z_F_twoway_resid)}"
                       for r in big.itertuples())
        npos = int((big.z_F_twoway_resid > 0).sum())
        ncov = int(((big.horizon == "y1") & (big.window == 2019)).sum())
        A_(f"   (c) *Cells with |D| >= 2 SD* ({len(big)} of {CS['n_cells']['y1']} y1 and {CS['n_cells']['y5']} y5 "
           f"cells): {bl}. {nneg} of {len(big)} have D < 0 (weak demand); {npos} of {len(big)} have z_F above their "
           f"field and window means ({nres_hi} by more than 0.1). {ncov} of them are y1 cells of the 2019-21 window, "
           "whose earnings years (2020-22) are the COVID period, when much else changed.")
    else:
        A_("   (c) *Cells with |D| >= 2 SD:* none.")
    A_("8. **Data limits (item 6).** PSEO windows start in 2001, so the dot-com boom itself (graduates of the late "
       "1990s) is not observed; only the bust is, through the 2001-03 window, and the OES-based index shows it as "
       "a one-year dip in 2002 (item 1). No institution x field earnings source yet observes a cohort entering "
       "after late 2022. PSEO y1 earnings end with the 2019-21 window (earnings 2020-22); College Scorecard 1-year "
       "earnings end with calendar years 2020-21; UK LEO ends with tax year 2022/23. AI-era entry therefore cannot "
       "be studied with these data.")
    A_("")
    A_("## Key numbers")
    A_("")
    A_("CI = inversion of the wild cluster restricted bootstrap test (Webb weights, 1999 replicates, clusters = "
       "fields); p = WCR bootstrap p; perm. p = field-label permutation of the D trajectories (1999). Units: Fisher z "
       "of the coupling per pooled within-field SD of D. MDE at 80% power, 5% two-sided.")
    A_("")
    A_("| quantity | sample | beta | 95% CI | p (WCR) | perm. p | MDE | verdict | fields | cells |")
    A_("|---|---|---|---|---|---|---|---|---|---|")
    for k, lab in (("T1", "T1: z_F on D, y1"), ("T2", "T2: z_par_FG on D, y1"), ("T3", "T3: z_F on D, y5")):
        r = T[k]
        A_(f"| {lab} | fixed17 | {fm(r['beta'])} | {ci_txt(r)} | {fp(r['p_wcr'])} | {fp(r['p_perm'])} | "
           f"{fu(r['mde'])} | {r['verdict']} | {r['G']} | {r['N']} |")
    for (k, nm), r in SEN.items():
        A_(f"| {k} sensitivity: {nm} | {'horizon-fixed' if 'horizon' in nm else 'fixed17'} | {fm(r['beta'])} | "
           f"{ci_txt(r)} | {fp(r['p_wcr'])} | {fp(r['p_perm'])} | {fu(r['mde'])} | — | {r['G']} | {r['N']} |")
    for nm, r in EXP.items():
        A_(f"| exploratory: {nm} on D | fixed17 | {fm(r['beta'])} | {ci_txt(r)} | {fp(r['p_wcr'])} | "
           f"{fp(r['p_perm'])} | {fu(r['mde'])} | — | {r['G']} | {r['N']} |")
    A_("")
    A_("## Method")
    A_("")
    A_("- **Outcome cells.** PSEO V4.14.1 bachelor's cells of scripts/65 (graduation windows 2001-03 ... 2019-21; "
       "earnings years c+h .. c+h+2). Fixed institutions: sample fixed17 of the scripts/65 panel (institutions of "
       f"the field present in all 17 window x horizon cells; {nf1} fields). z_F and its Bonett-Wright variance are "
       "read from the panel; par_FG = (r_FE - r_FG r_GE) / sqrt((1 - r_FG^2)(1 - r_GE^2)) on Spearman ranks is "
       "computed here on the same institutions, with variance (1 + r^2/2)/(n - 4).")
    A_("- **Demand index.** D_{f,t} = sum_o s_{f,o} g_{o,t}; g = log growth of the real wage bill of SOC minor group o "
       "from t-1 to t (O2-O3); s = ACS 2023 field-of-degree shares (O4); window value = mean over the three earnings "
       "years; D = deviation from the field's mean over the test's windows, divided by the pooled within-field SD "
       "(O5).")
    A_("- **Model.** Weighted least squares of Fisher z on D with field and window effects, weights = inverse "
       "Bonett-Wright variance; CR1 variance by field; WCR wild cluster bootstrap-t (Webb six-point weights, 1999 "
       "draws) for p and, by test inversion, the 95% CI that carries the verdict; MDE = (95% quantile of |t*| under "
       "the null + 0.842) x SE; field-label permutation of whole D trajectories (1999).")
    A_("- **Verdict rule (item 2).** rises in hot markets if the CI lies above 0, falls if below 0, null if it "
       "includes 0 and the MDE <= 0.05, otherwise underpowered.")
    A_("")
    A_("## Caveats")
    A_("")
    A_("- **Wayback copies.** The OES files are the Internet Archive's copies of the bls.gov files (snapshot time in "
       "each URL, md5 in data/sources.csv). They were not compared with a direct bls.gov download, which was "
       "refused.")
    A_("- **OES is not built for time series.** Each estimate pools survey panels collected over three years (the "
       "2001 file's field description: 'The 2001 estimates contain data collected in 1999, 2000, and 2001'; the May "
       "estimates from 2003 pool six semi-annual panels, with older wages aged forward by the ECI), so year-to-year "
       "changes are smoothed and lagged, and BLS advises caution in comparing OES estimates over time. "
       "*Correction to O1 (post hoc, wording only):* O1 calls the reference periods of the 2001 and 2002 files "
       "November; the files and the BLS table page label them by year only. May reference periods start in 2003, "
       "so the 2002->2003 change spans less than a year. The index is computed the same way either way. "
       "Code changes (2004 additions, the SOC 2010 and 2018 revisions through hybrid years, smaller 2014/2017 "
       "changes) are handled by matched codes and crosswalk components (O2). Component growth blends a group with "
       "the groups it exchanged codes with; for example, computer occupations are pooled with management, business "
       "operations and office groups at the 2018->2019 transition (Appendix C). " + SWING)
    A_("- **Shares from 2023.** Field-to-occupation shares are measured at the end of the period, on 23-35-year-olds "
       "in 2023, and held fixed. The index thus reflects demand for the occupations a field's graduates hold now, not "
       "in 2002. Occupation (SOCP) is the ACS coding of OCCP.")
    A_("- **National, not local.** D is the same for every institution offering field f; window effects absorb "
       "everything common to all fields in a window, including the national cycle. Fields with similar occupation "
       "mixes (the engineering fields; computer science and computer engineering) have similar D.")
    A_("- **What a null would and would not mean.** The tests ask whether coupling moves with field-specific demand "
       "growth in the earnings years. They do not measure the level of demand, local labour markets, changes in "
       "who enrols, or programme quality, and the index can be wrong about a field's market in any window. All "
       "statements are descriptive.")
    def resid_sd(x_):
        zt = x_.z_F - x_.groupby("field").z_F.transform("mean") - x_.groupby("grad_window").z_F.transform("mean") \
            + x_.z_F.mean()
        return float(np.sqrt(np.sum(zt ** 2) / (len(x_) - x_.field.nunique() - x_.grad_window.nunique() + 1)))
    A_(f"- **Power.** {nf1} fields with {c1.grad_window.nunique()} (y1) or {c5.grad_window.nunique()} (y5) windows. "
       f"The SD of z_F net of field and window means is {resid_sd(c1):.3f} (y1) and {resid_sd(c5):.3f} (y5), and the "
       f"median Bonett-Wright sampling SD of a cell is {np.sqrt(c1.var_z_F_bw.median()):.3f} (y1). Field demand "
       f"left after the window effects is {fu(T['T1']['sd_res'], 2)} SD (y1). Under these conditions the MDE of "
       "0.05 per SD was not reached." if allu else "- **Power.** See the MDE column.")
    A_("")
    A_("## Pre-specification (verbatim; md5 of the block " + f"`{md5s['pre']}`)")
    A_("")
    A_(pre)
    A_("")
    A_("## Operational definitions (verbatim; md5 of the block " + f"`{md5s['op']}`)")
    A_("")
    A_(op)
    A_("")
    A_("## Appendix A. Demand index by field and window (descriptive)")
    A_("")
    A_("D_raw = mean annual log growth of the real wage bill of the field's occupations over the window's earnings "
       "years (x100); D = deviation from the field's mean over windows in pooled SD units (the test variable). Fixed17 "
       "fields plus computer engineering.")
    A_("")
    flds = sorted(set(c1.field)) + ["computer_engineering"]
    for h, sdh in (("y1", sd1["D"]), ("y5", sd5["D"])):
        ws = [int(c) for c in CO[h]]
        A_(f"**{h}** (pooled within-field SD of D_raw x100: {100 * sdh:.3f})")
        A_("")
        A_("| field | " + " | ".join(f"{w} D_raw / D" for w in ws) + " |")
        A_("|---|" + "---|" * len(ws))
        for f in flds:
            x = WI[(WI.field == f) & (WI.horizon == h)].set_index("grad_window")
            dd = (x.D_raw - x.D_raw.mean()) / sdh
            A_(f"| {s65.LAB.get(f, f)} | " + " | ".join(f"{100 * x.D_raw[w]:+.2f} / {dd[w]:+.2f}" for w in ws) + " |")
        A_("")
    A_("## Appendix B. Case-study cells (descriptive)")
    A_("")
    A_("| field | horizon | window | earnings years | D | Spearman(F,p50) fixed17 | partial F given G, fixed17 | "
       "n fixed17 | Spearman(F,p50) all institutions | n all |")
    A_("|---|---|---|---|---|---|---|---|---|---|")
    for r in cmp_.itertuples():
        A_(f"| {s65.LAB.get(r.field, r.field)} | {r.horizon} | {r.window} | {r.earn_years} | {fm(r.D, 2)} | "
           f"{fu(getattr(r, 'rho_F_fixed', np.nan))} | {fu(getattr(r, 'par_FG_fixed', np.nan))} | "
           f"{'—' if not np.isfinite(getattr(r, 'n_fixed', np.nan)) else int(r.n_fixed)} | {fu(r.rho_F_all)} | "
           f"{int(r.n_all)} |")
    A_("")
    A_("| field | horizon | window | earnings years | D | Spearman(F,p50) | mean of 24 fields | partial F given G | "
       "mean of 24 fields | n |")
    A_("|---|---|---|---|---|---|---|---|---|---|")
    for r in fin.itertuples():
        A_(f"| {s65.LAB.get(r.field, r.field)} | {r.horizon} | {r.window} | {r.earn_years} | {fm(r.D, 2)} | "
           f"{fu(r.rho_F)} | {fu(r.mean_rho_F_all_fields)} | {fu(r.par_FG)} | {fu(r.mean_par_FG_all_fields)} | {r.n} |")
    A_("")
    A_("## Appendix C. OES occupation-group growth: construction by year")
    A_("")
    A_("| growth year | detailed occupations (t) | groups | matched codes | crosswalk component | undefined |")
    A_("|---|---|---|---|---|---|")
    cnt = G.groupby(["year", "method"]).size().unstack(fill_value=0)
    for t in G_YEARS:
        A_(f"| {t - 1}->{t} | {oes_n[t]} | {int(cnt.loc[t].sum())} | {int(cnt.loc[t].get('matched', 0))} | "
           f"{int(cnt.loc[t].get('component', 0))} | {int(cnt.loc[t].get('missing', 0))} |")
    A_("")
    A_("Component growth used (group, year, matched coverage before / after, component): " + "; ".join(
        f"{r.minor} {r.year} ({r.cov_prev:.2f} / {r.cov:.2f}; {r.comp})" for r in comp_rows.itertuples()) + ".")
    A_("")
    A_("## Appendix D. Field -> occupation shares (ACS 2023 PUMS; three largest SOC minor groups)")
    A_("")
    A_("| field | FOD1P | sample persons | share in OES groups | largest groups (share) |")
    A_("|---|---|---|---|---|")
    for f in flds:
        x = S[S.field == f].sort_values(["share", "minor"], ascending=[False, True]).head(3)
        A_(f"| {s65.LAB.get(f, f)} | {cov[f]['fod1p']} | {cov[f]['n_persons']:,} | {cov[f]['share_in_oes']:.3f} | "
           + ", ".join(f"{o} ({v_:.2f})" for o, v_ in zip(x.minor, x.share)) + " |")
    A_("")
    OUT_MD.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
