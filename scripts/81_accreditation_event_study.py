"""81 -- Design B event study: first accreditation (ABET, AACSB), then graduates' pay (PSEO V4.14.1).

PRE-SPECIFICATION (project owner, 2026-11-14; written here verbatim before any outcome was read)
<<<SPEC
Use only the events and cells you counted in scripts/80.

- **Units:** PSEO V4.14.1 institution × CIP-4 cells. ABET applies to the engineering and computing CIPs you mapped (IT/IS kept and dropped, as two versions). AACSB applies to the business CIPs.
- **Outcome:** the primary is log p50 earnings at y1 by graduation window. Secondaries are (a) y5 and (b) the cell's within-field percentile rank of p50 among the same window's institutions, because our object is rank agreement.
- **Treatment timing:** a window is post if its first graduation year is ≥ the first-accreditation year. For ABET, use the retroactive effective date. As a sensitivity, set it 2 years earlier.
- **Estimator:** a heterogeneity-robust staggered DiD (Callaway–Sant'Anna or Sun–Abraham, implemented yourself or with a vetted package).
  - Controls are not-yet-treated plus never-treated cells in the same field. Report already-accredited cells as an alternative control set.
  - Fixed effects: cell, and field × window.
  - Cluster by institution, using a wild cluster bootstrap if there are fewer than 50 clusters.
- **Estimates to report:** the average post effect (ATT), event-time estimates with 2 pre-windows, the MDE and a pre-trend joint test. Report ABET, AACSB and pooled.
- **Verdict per estimate:**
  - "invalid (pre-trend)" if the joint pre-trend p < 0.10;
  - otherwise "positive" if the CI is above 0 and "negative" if below;
  - "null" if the CI includes 0 and MDE ≤ 0.05;
  - "underpowered" otherwise.
- Say plainly that accreditation timing is chosen by institutions and also changes curricula. A positive effect therefore fits "employers price a visible department signal", but does not isolate information from content.
SPEC>>>

OPERATIONAL DEFINITIONS (written 2026-11-14, after the specification and before any outcome was read)
<<<OPS
O1 Data. PSEO V4.14.1 (data/raw/pseo_2026q2), bachelor's (degree_level 05), institution level, CIP-4 rows, 3-year
   graduation windows c = 2001, 2004, ..., 2019 (graduates c..c+2). A cell-window observation exists iff
   status_y{h}_earnings == 1 and p50 > 0. Primary: y1 log p50. (a): y5 log p50 (windows 2001-2016).
   (b): y1 within-field percentile rank, r = (average rank of p50 - 0.5) / n among all released institution cells
   of the same CIP-4 x window (scale 0-1, so 0.05 = 5 percentile points).
O2 Field = CIP-4. ABET fields = the CIP-4 codes of scripts/80 ABET_CIP; AACSB fields = all CIP-4 codes 52.xx.
O3 Treated cells (only those counted in scripts/80). ABET, IT/IS kept: the 41 institution x CIP-4 cells usable in
   scripts/80 (B1). ABET, IT/IS dropped: the same minus CIP 11.01 and 11.04 (25 cells). AACSB: the CIP-4 52.xx cells
   that scripts/80 counted as usable at CIP-4 at its 60 AACSB events (a released y1 window ending <= e_lo - 1 and one
   starting >= e_hi; 120 cells), all with their institution's accreditation year.
   Accreditation year A: ABET = year of the earliest ABET accreditation date (the effective date, which ABET may set
   retroactively) over all ABET records matched to the institution x CIP-4 (scripts/80 matching); sensitivity A - 2.
   AACSB = e_lo of scripts/80 (the board-ratification year for exact-dated events; the earliest year consistent with
   the page for interval-dated ones). Window c is post iff c >= A. Cohort g = first window with c >= A.
O4 Control status (same field). ABET: every PSEO cell in an ABET field gets A from the same ABET matching;
   never-treated = no ABET record in that CIP-4; already-accredited = A <= 2001 (post in every window). AACSB
   (institution level, applied to all its 52.xx cells): already-accredited = in AACSB's June-2002 list of schools
   accredited in business (InstLists lid=3, Wayback 2002-06-21) and not listed as an initial accreditation on any
   2002+ page; A = e_lo if listed as an initial business accreditation on the 2002-2017 pages; status unknown (excluded
   from every control set) = in AACSB's April-2015 US listing or its current (2026) Americas listing but in neither
   of the above; never-treated = in none of these lists. Names are matched as in scripts/80 (exact normalised name +
   state against the IPEDS name history). Cells first accredited in or after the sample but not counted in scripts/80
   serve only as not-yet-treated controls, before their A.
O5 Estimator: Callaway-Sant'Anna, implemented here. Universal base window b = g - 1 (the last pre window).
   ATT_f(g,t) = mean over treated cells of field f, cohort g of (Y_t - Y_b) minus the same mean over control cells of
   field f; only cells released in both b and t enter. Main controls: never-treated cells and cells with
   g_j > max(t, b) (not yet treated in either period), cohort g itself excluded. Alternative controls:
   already-accredited cells only. Within-field differencing gives the field x window effects; the base-period
   difference gives the cell effects. Overall ATT = average of ATT_f(g,t) over all t >= g, weighted by the number of
   treated cells entering each comparison. Event time e = t - g in windows; theta_e = the same weighted average over
   comparisons with t = g + e. Reported: e = -3, -2 (two pre windows; e = -1 is the reference) and e = 0, 1, 2.
O6 Inference: clusters = institutions (treated and control). Multiplier (wild cluster) bootstrap of the influence
   functions, Webb six-point weights, B = 9,999, seeds from numpy SeedSequence(20261114) spawned per estimate. Every
   estimate has fewer than 50 treated institutions, so the wild bootstrap is used throughout. 95% CI = theta +/- the
   95th percentile of |theta* - theta|; SE = SD of theta*; MDE = 2.80 x SE (80% power, 5% two-sided); p = share of
   |theta* - theta| >= |theta|. Pre-trend joint test: H0 theta_-3 = theta_-2 = 0, Wald statistic with the bootstrap
   covariance, p = share of bootstrap Wald statistics (centred) >= the observed one; if only one pre estimate exists
   the test uses it alone; if none exists the pre-trend is "not testable" and the verdict starts at step 2.
O7 Estimates with verdicts: {ABET IT/IS kept, ABET IT/IS dropped, AACSB, pooled (ABET kept + AACSB), pooled (ABET
   dropped + AACSB)} x {primary, (a) y5, (b) rank} with main controls; sensitivities on the primary: ABET timing A - 2
   (both ABET versions and both pooled versions) and the already-accredited control set (all five). Pooled = both
   designs' comparisons averaged together with the same weights. The MDE <= 0.05 threshold of the verdict rule is
   applied in each outcome's own units (log points; rank share). Everything else is exploratory.
OPS>>>

What had been seen before this freeze: scripts/80 output (event counts, release flags and graduate counts of the event
cells, pooled noise variances over all cells, design-level MDEs). No earnings or rank value of any event cell, and no
outcome change around any event, had been read.

REVISION 1 (2026-11-14), added after the results had been seen: a (g,t)-centred influence
function, an audited AACSB roster alias table, A+1/A+2 timing checks and disclosures are added after the frozen
estimates, which are printed unchanged. See ACCREDITATION_RESULT.md, "Revision 1".

Run:  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I -B scripts/81_accreditation_event_study.py
Reuses scripts/80 functions through importlib (scripts/80 is not edited). Single process; peak memory < 1 GB.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import re
import sys
import contextlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("s80", ROOT / "scripts" / "80_causal_feasibility.py")
s80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s80)


def block(tag: str) -> str:
    return __doc__.split(f"<<<{tag}\n", 1)[1].split(f"{tag}>>>", 1)[0]


if __name__ == "__main__" and "--md5" in sys.argv:
    print("SPEC md5", hashlib.md5(block("SPEC").encode()).hexdigest())
    print("OPS  md5", hashlib.md5(block("OPS").encode()).hexdigest())
    sys.exit(0)

# ----------------------------------------------------------------------------------------------------
# constants
# ----------------------------------------------------------------------------------------------------
RAW = ROOT / "data" / "raw"
WINDOWS = s80.COHORTS                                   # 2001, 2004, ..., 2019
WIX = {c: k for k, c in enumerate(WINDOWS)}
NEVER = 10 ** 6
B = 9_999
SEED = 20261114
EVENT_TIMES = [-3, -2, 0, 1, 2]
# revision 1: AACSB roster names (June-2002 lid=3 list, 2026 Americas list) -> IPEDS names, same state; each checked
# against the two lists. scripts/80 (and its AACSB_ALIAS) is not edited; this table is used only for status.
ROSTER_ALIAS = {
    ("Baruch College-The City University of New York", "NY"): ["CUNY Bernard M Baruch College"],
    ("Binghamton University, State University of New York", "NY"): ["Binghamton University"],
    ("Fairleigh Dickinson University", "NJ"): ["Fairleigh Dickinson University-Metropolitan Campus",
                                               "Fairleigh Dickinson University-Florham Campus"],
    ("Indiana University", "IN"): ["Indiana University-Bloomington", "Indiana University-Purdue University-Indianapolis"],
    ("Louisiana State University", "LA"): ["Louisiana State University and Agricultural & Mechanical College"],
    ("Miami University", "OH"): ["Miami University-Oxford"],
    ("North Carolina State University", "NC"): ["North Carolina State University at Raleigh"],
    ("Plattsburgh State University of New York", "NY"): ["SUNY College at Plattsburgh"],
    ("Rutgers-The State University of New Jersey-Camden", "NJ"): ["Rutgers University-Camden"],
    ("Rutgers-The State University of New Jersey-Newark", "NJ"): ["Rutgers University-Newark"],
    ("The Pennsylvania State University at Harrisburg", "PA"): ["Pennsylvania State University-Penn State Harrisburg"],
    ("The University of Michigan", "MI"): ["University of Michigan-Ann Arbor"],
    ("University at Albany, State University of New York", "NY"): ["SUNY at Albany"],
    ("University at Buffalo, State University of New York", "NY"): ["University at Buffalo"],
    ("University of Maryland", "MD"): ["University of Maryland-College Park"],
    ("University of Minnesota", "MN"): ["University of Minnesota-Twin Cities"],
    ("University of Oklahoma", "OK"): ["University of Oklahoma-Norman Campus"],
    ("University of South Carolina", "SC"): ["University of South Carolina-Columbia"],
    ("University of Virginia-McIntire", "VA"): ["University of Virginia-Main Campus"],
    ("The Citadel", "SC"): ["Citadel Military College of South Carolina"],
    # only on the 2026 list -> date unknown
    ("Brooklyn College of the City University of New York", "NY"): ["CUNY Brooklyn College"],
    ("State University of New York at Farmingdale", "NY"): ["Farmingdale State College"],
    ("State University of New York at Old Westbury", "NY"): ["SUNY College at Old Westbury"],
    ("Rutgers-The State University of New Jersey-Newark/New Brunswick", "NJ"): ["Rutgers University-New Brunswick"],
    ("University of St. Thomas-Minnesota", "MN"): ["University of St Thomas"],
}


def say(*a):
    print(*a, flush=True)


def quiet(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def cohort(A: float) -> int:
    """window index of the first window whose first graduation year is >= A (NEVER if none)"""
    for c in WINDOWS:
        if c >= A:
            return WIX[c]
    return NEVER


# ----------------------------------------------------------------------------------------------------
# treatment status (no outcome data)
# ----------------------------------------------------------------------------------------------------
def abet_status(ni, av):
    """all PSEO institution x CIP-4 cells with an ABET record: A = earliest accreditation year (scripts/80 logic)"""
    abet = s80.load_abet()
    b = abet[(abet.degreeLevelCode == "B") & abet.commissionName.isin(["EAC", "CAC"])].copy()
    b["cip"] = b.disciplineName.map(s80.ABET_CIP)
    b = b[b.cip.notna() & b.first_year.notna()]
    cell = b.groupby(["organizationId", "cip"]).agg(
        name=("organizationName", "first"), state=("organizationStateCode", "first"),
        alt=("organizationAlternateName", "first"), first_year=("first_year", "min")).reset_index()
    cell["opeid"] = [ni.resolve([s80.ALIAS[(n, st)][0]], s80.ALIAS[(n, st)][1]) if isinstance(s80.ALIAS.get((n, st)), tuple)
                     else ni.resolve([n] + ([a] if isinstance(a, str) and a else []), st, s80.ALIAS.get((n, st)))
                     for n, st, a in zip(cell.name, cell.state, cell.alt)]
    pc = cell[cell.opeid.notna() & ~cell.opeid.str.contains(":", na=False)]
    return pc.groupby(["opeid", "cip"]).first_year.min().rename("A").reset_index()


def roster(path: Path, kind: str) -> list[tuple[str, str]]:
    L = s80.page_lines(path)
    out = []
    for k, ln in enumerate(L):
        if kind == "2002":
            m = re.match(r"^(.*?)\s*\(USA\s*-\s*([^)]+)\)\s*$", ln)
            if m and m.group(2).strip() in s80.STATE:
                out.append((m.group(1).strip(), s80.STATE[m.group(2).strip()]))
        elif kind == "2015":
            m = re.match(r"^(.*?)\s*\(United States\s*-\s*([A-Z]{2})\)\s*$", ln)
            if m:
                out.append((m.group(1).strip(), m.group(2)))
        else:
            m = re.match(r"^(.+),\s*([A-Za-z .]+),\s*United States$", ln)
            if m and m.group(2).strip() in s80.STATE and k >= 2:
                out.append((L[k - 2], s80.STATE[m.group(2).strip()]))
                out.append((L[k - 1], s80.STATE[m.group(2).strip()]))     # in case the card has no school line
    return out


def aacsb_status(ni, av):
    """institution-level AACSB status and the counted treated cells (scripts/80 logic, re-run quietly)"""
    t, first, _ = quiet(s80.design_b_aacsb, ni, av, s80.pseo_noise(PSEO[PSEO.cip == "52"], "y1", cip_level="2"))
    m = first[first.status == "matched"].copy()
    m["e_lo"] = m[["lo_year", "cap_year"]].min(axis=1)
    initial = m.groupby("opeid").e_lo.min()                       # every listed initial accreditation (2002-2017)

    def resolve_all(entries):
        hits, tot, unm = set(), 0, 0
        for nm, st in entries:
            al = s80.AACSB_ALIAS.get((nm, st)) or s80.AACSB_ALIAS.get((nm, ""))
            op = ni.resolve([al[0]], al[1]) if al else ni.resolve([nm], st)
            if op and ":" not in op:
                hits.add(op)
        return hits

    r02 = roster(RAW / "aacsb" / "rosters" / "aacsb_instlists_lid3_20020621044818.html", "2002")
    r15 = roster(RAW / "aacsb" / "rosters" / "aacsb_globallisting_US_20150404213651.html", "2015")
    r26 = [e for f in sorted((RAW / "aacsb" / "current").glob("*.html")) for e in roster(f, "2026")]
    h02, h15, h26 = resolve_all(r02), resolve_all(r15), resolve_all(r26)
    already = h02 - set(initial.index)
    unknown = (h15 | h26) - already - set(initial.index)
    say(f"AACSB rosters: June-2002 list {len(r02)} US entries -> {len(h02)} PSEO institutions; April-2015 US list "
        f"{len(r15)} -> {len(h15)}; 2026 Americas list {len(set(r26)) // 2 if r26 else 0} US cards -> {len(h26)}")
    say(f"  status of PSEO institutions: already accredited (2002 list, never 'initial') {len(already)}; initial "
        f"accreditation listed 2002-2017 {len(initial)}; unknown date (2015/2026 lists only; excluded from controls) "
        f"{len(unknown)}; listed initial yet on the June-2002 list {len(h02 & set(initial.index))}")
    # counted treated cells: CIP-4 52.xx cells usable in scripts/80 (pre window ending <= e_lo-1, post starting >= e_hi)
    cells = []
    for r in t.itertuples():
        x4 = av[(av.institution == r.opeid) & (av.cip_level == "4") & av.cip.str.startswith("52") & av.rel_y1]
        ok = x4.groupby("cip").c.agg(lambda c: ((c + 2 <= r.e_lo - 1).any()) and ((c >= r.e_hi).any()))
        for cip in ok[ok].index:
            cells.append(dict(opeid=r.opeid, cip=cip, A=int(r.e_lo), e_hi=int(r.e_hi), name=r.name))
    tc = pd.DataFrame(cells)
    return tc, initial, already, unknown


# ----------------------------------------------------------------------------------------------------
# panel and Callaway-Sant'Anna (universal base window), influence functions for the multiplier bootstrap
# ----------------------------------------------------------------------------------------------------
def outcome_frame(p: pd.DataFrame) -> pd.DataFrame:
    x = p[p.cip_level == "4"][["institution", "cip", "c", "rel_y1", "rel_y5", "p50_y1", "p50_y5"]].copy()
    x["y1"] = np.where(x.rel_y1 & (x.p50_y1 > 0), np.log(x.p50_y1.where(x.p50_y1 > 0)), np.nan)
    x["y5"] = np.where(x.rel_y5 & (x.p50_y5 > 0), np.log(x.p50_y5.where(x.p50_y5 > 0)), np.nan)
    v = x[x.y1.notna()]
    rk = v.groupby(["cip", "c"]).p50_y1.rank(method="average")
    n = v.groupby(["cip", "c"]).p50_y1.transform("count")
    x["rank"] = np.nan
    x.loc[v.index, "rank"] = (rk - 0.5) / n
    x["w"] = x.c.map(WIX)
    return x[["institution", "cip", "w", "y1", "y5", "rank"]]


def cs_components(Y: pd.DataFrame, G: pd.Series, treated: pd.DataFrame, control: str) -> list[dict]:
    """Y: wide panel (index (institution, cip), columns window index) for one outcome; G: cohort index per cell
    (NEVER = never treated, -1 = unknown status, 0 = already treated); treated: rows (institution, cip, g) counted.
    Returns one record per estimable 2x2: field, g, t, e, n_treated, theta, and IF contributions per cell."""
    recs = []
    cells_by_field = defaultdict(list)
    for idx in Y.index:
        cells_by_field[idx[1]].append(idx)
    tg = treated.groupby(["cip", "g"])
    for (f, g), grp in tg:
        b = g - 1
        if b < 0:
            continue
        T = [(i, f) for i in grp.institution]
        Tset = set(T)
        pool = [u for u in cells_by_field[f] if u not in Tset]
        for t in range(len(WINDOWS)):
            if t == b:
                continue
            if control == "main":
                C = [u for u in pool if G.get(u, NEVER) == NEVER or G.get(u, NEVER) > max(t, b)]
                C = [u for u in C if G.get(u, NEVER) not in (-1, g)]        # unknown status / own cohort out
            else:
                C = [u for u in pool if G.get(u, NEVER) == 0]
            yt, yb = Y[t] if t in Y.columns else None, Y[b] if b in Y.columns else None
            if yt is None or yb is None:
                continue
            dT = (yt.reindex(T) - yb.reindex(T)).dropna()
            dC = (yt.reindex(C) - yb.reindex(C)).dropna()
            if len(dT) == 0 or len(dC) < 2:
                continue
            th = float(dT.mean() - dC.mean())
            psi = pd.concat([(dT - dT.mean()) / len(dT), -(dC - dC.mean()) / len(dC)])
            recs.append(dict(field=f, g=g, t=t, e=t - g, n=len(dT), theta=th, psi=psi, nC=len(dC), dT=dT, dC=dC))
    return recs


def aggregate(recs: list[dict], clusters: pd.Index, mode: str = "frozen") -> dict:
    """overall ATT (t >= g) and event-time thetas, weights = treated cells entering each 2x2; IF summed by cluster.
    mode 'frozen': treated side of the influence function demeaned within field x cohort x window (as frozen).
    mode 'gt' (revision 1): treated side demeaned within cohort x window (x design), pooling fields, i.e. CS with
    field as a covariate; a field x cohort x window comparison with a single treated cell no longer has zero
    treated-side variance. Point estimates are identical in both modes."""
    if mode == "gt":
        return _aggregate_gt(recs, clusters)
    out = {}
    groups = {"ATT": [r for r in recs if r["e"] >= 0]}
    for e in EVENT_TIMES:
        groups[f"e{e}"] = [r for r in recs if r["e"] == e]
    for k, rs in groups.items():
        if not rs:
            out[k] = None
            continue
        w = np.array([r["n"] for r in rs], float)
        w = w / w.sum()
        th = float(np.sum(w * np.array([r["theta"] for r in rs])))
        ps = pd.concat([r["psi"] * wi for r, wi in zip(rs, w)])
        inst = ps.index.get_level_values(0)
        psi_c = ps.groupby(inst).sum().reindex(clusters, fill_value=0.0).to_numpy()
        tre = {u for r in rs for u in r["psi"].index[: r["n"]]}
        out[k] = dict(theta=th, psi=psi_c, n_cells=len(tre), n_inst=len({u[0] for u in tre}),
                      n_comp=len(rs), n_ctrl=int(np.mean([r["nC"] for r in rs])))
    return out


def _aggregate_gt(recs: list[dict], clusters: pd.Index) -> dict:
    out = {}
    groups = {"ATT": [r for r in recs if r["e"] >= 0]}
    for e in EVENT_TIMES:
        groups[f"e{e}"] = [r for r in recs if r["e"] == e]
    for k, rs in groups.items():
        if not rs:
            out[k] = None
            continue
        N = float(sum(r["n"] for r in rs))
        th = float(sum(r["n"] * r["theta"] for r in rs) / N)
        gt = defaultdict(list)
        for r in rs:
            gt[(r["g"], r["t"], r.get("des", ""))].append((r["dT"] - r["dC"].mean()).to_numpy())
        gtm = {kk: float(np.concatenate(v).mean()) for kk, v in gt.items()}
        parts = []
        for r in rs:
            res = r["dT"] - r["dC"].mean()
            parts.append((res - gtm[(r["g"], r["t"], r.get("des", ""))]) / N)
            parts.append(-(r["n"] / N) * (r["dC"] - r["dC"].mean()) / len(r["dC"]))
        ps = pd.concat(parts)
        psi_c = ps.groupby(ps.index.get_level_values(0)).sum().reindex(clusters, fill_value=0.0).to_numpy()
        tre = {u for r in rs for u in r["dT"].index}
        out[k] = dict(theta=th, psi=psi_c, n_cells=len(tre), n_inst=len({u[0] for u in tre}),
                      n_comp=len(rs), n_ctrl=int(np.mean([r["nC"] for r in rs])))
    return out


def webb(rng, size):
    v = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
    return v[rng.integers(0, 6, size=size)]


def bootstrap(agg: dict, seed: np.random.SeedSequence) -> dict:
    keys = [k for k, v in agg.items() if v is not None]
    P = np.vstack([agg[k]["psi"] for k in keys])                 # K x C
    rng = np.random.default_rng(seed)
    D = np.empty((B, len(keys)))
    for s in range(0, B, 2000):
        m = min(2000, B - s)
        D[s:s + m] = webb(rng, (m, P.shape[1])) @ P.T
    res = {}
    for j, k in enumerate(keys):
        th, d = agg[k]["theta"], D[:, j]
        q = float(np.quantile(np.abs(d), 0.95))
        se = float(d.std(ddof=1))
        res[k] = dict(agg[k], se=se, lo=th - q, hi=th + q, p=float(np.mean(np.abs(d) >= abs(th))), mde=2.80 * se)
        res[k].pop("psi")
    pre = [k for k in ("e-3", "e-2") if k in keys]
    if pre:
        jj = [keys.index(k) for k in pre]
        th = np.array([agg[k]["theta"] for k in pre])
        Dp = D[:, jj]
        V = np.cov(Dp, rowvar=False).reshape(len(pre), len(pre))
        Vi = np.linalg.pinv(V)
        W = float(th @ Vi @ th)
        Wb = np.einsum("bi,ij,bj->b", Dp, Vi, Dp)
        res["pretrend"] = dict(W=W, p=float(np.mean(Wb >= W)), k=len(pre))
    else:
        res["pretrend"] = None
    return res


def verdict(r: dict, pre) -> str:
    if pre is not None and pre["p"] < 0.10:
        return "invalid (pre-trend)"
    if r["lo"] > 0:
        return "positive"
    if r["hi"] < 0:
        return "negative"
    if r["mde"] <= 0.05:
        return "null"
    return "underpowered"


# ----------------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------------
def main():
    global PSEO
    say("SPEC md5", hashlib.md5(block("SPEC").encode()).hexdigest(), "| OPS md5", hashlib.md5(block("OPS").encode()).hexdigest())
    PSEO = s80.load_pseo()
    av = s80.availability(PSEO)
    hd = s80.load_hd()
    ni = s80.NameIndex(hd, set(av.institution))

    # ---- ABET status and counted treated cells (re-run scripts/80 B1 quietly, then check the replication) ----
    ins = pd.read_csv(s80.PSEO_I, dtype=str, encoding="utf-8-sig")
    p_tech = PSEO[PSEO.cip.str[:2].isin(["11", "14", "15"])]
    t80, _, _ = quiet(s80.design_b_abet, s80.load_abet(), ni, av, set(ins.institution_state), s80.pseo_noise(p_tech, "y1"))
    abet_tc = t80[t80.usable_y1][["opeid", "cip", "first_year", "name"]].rename(columns={"first_year": "A"})
    st_abet = abet_status(ni, av)
    chk = abet_tc.merge(st_abet, on=["opeid", "cip"], suffixes=("", "_st"))
    assert len(chk) == len(abet_tc) and (chk.A == chk.A_st).all(), "ABET status replication failed"
    say(f"ABET: counted treated cells {len(abet_tc)} ({abet_tc.opeid.nunique()} institutions); without IT/IS "
        f"{int((~abet_tc.cip.isin(['1101', '1104'])).sum())}; PSEO cells with an ABET record {len(st_abet)} "
        f"(already accredited, A <= 2001: {int((st_abet.A <= 2001).sum())})")

    aacsb_tc, aacsb_init, aacsb_already, aacsb_unknown = aacsb_status(ni, av)
    say(f"AACSB: counted treated CIP-4 cells {len(aacsb_tc)} at {aacsb_tc.opeid.nunique()} institutions")

    X = outcome_frame(PSEO)
    abet_fields = sorted({v for v in s80.ABET_CIP.values() if v})
    bus_fields = sorted({c for c in X.cip.unique() if c.startswith("52")})

    def G_series(design: str, shift: int = 0, override: dict | None = None) -> pd.Series:
        cells = X[X.cip.isin(abet_fields if design == "abet" else bus_fields)][["institution", "cip"]].drop_duplicates()
        idx = pd.MultiIndex.from_frame(cells)
        G = pd.Series(NEVER, index=idx, dtype=int)
        if design == "abet":
            for r in st_abet.itertuples():                       # the A-2 sensitivity shifts every ABET date
                if (r.opeid, r.cip) in G.index:
                    G[(r.opeid, r.cip)] = 0 if r.A - shift <= 2001 else cohort(r.A - shift)
            for r in abet_tc.itertuples():
                G[(r.opeid, r.cip)] = cohort(r.A - shift)
        else:
            inst = cells.institution
            for u in idx:
                op = u[0]
                if op in aacsb_already:
                    G[u] = 0
                elif op in aacsb_init.index:
                    G[u] = cohort(aacsb_init[op])
                elif op in aacsb_unknown:
                    G[u] = -1
            if override:                                          # revision 1: audited roster corrections
                for u in idx:
                    if u[0] in override:
                        G[u] = override[u[0]]
            for r in aacsb_tc.itertuples():
                G[(r.opeid, r.cip)] = cohort(r.A)
        return G

    def treated_frame(design: str, drop_itis=False, shift=0) -> pd.DataFrame:
        tc = abet_tc if design == "abet" else aacsb_tc
        if drop_itis:
            tc = tc[~tc.cip.isin(["1101", "1104"])]
        return pd.DataFrame({"institution": tc.opeid.values, "cip": tc.cip.values,
                             "g": [cohort(a - shift) for a in tc.A]})

    clusters = pd.Index(sorted(X.institution.unique()))
    wide = {o: X.pivot_table(index=["institution", "cip"], columns="w", values=o) for o in ("y1", "y5", "rank")}

    specs = []   # (label, outcome, list of (design, drop_itis, shift), control, primary?)
    versions = [("ABET, IT/IS kept", [("abet", False)]), ("ABET, IT/IS dropped", [("abet", True)]),
                ("AACSB", [("aacsb", False)]), ("pooled (ABET kept + AACSB)", [("abet", False), ("aacsb", False)]),
                ("pooled (ABET dropped + AACSB)", [("abet", True), ("aacsb", False)])]
    for out_, olab in (("y1", "primary: y1 log p50"), ("y5", "(a) y5 log p50"), ("rank", "(b) y1 within-field rank")):
        for vlab, parts in versions:
            specs.append((vlab, olab, out_, [(d, dr, 0) for d, dr in parts], "main"))
    for vlab, parts in versions:
        if any(d == "abet" for d, _ in parts):
            specs.append((vlab, "sensitivity: ABET timing A-2", "y1", [(d, dr, 2 if d == "abet" else 0) for d, dr in parts], "main"))
    for vlab, parts in versions:
        specs.append((vlab, "sensitivity: already-accredited controls", "y1", [(d, dr, 0) for d, dr in parts], "already"))

    seeds = np.random.SeedSequence(SEED).spawn(len(specs))
    rows, store = [], {}
    for (vlab, olab, out_, parts, ctrl), sd in zip(specs, seeds):
        recs = []
        for d, dr, sh in parts:
            G = G_series(d, sh)
            tf = treated_frame(d, dr, sh)
            Y = wide[out_].reindex(G.index)
            rr = cs_components(Y, G.to_dict(), tf, ctrl)
            for r in rr:
                r["des"] = d
            recs += rr
        store[(vlab, olab, ctrl)] = recs
        agg = aggregate(recs, clusters)
        if agg.get("ATT") is None:
            rows.append(dict(version=vlab, outcome=olab, verdict="not estimable"))
            continue
        res = bootstrap(agg, sd)
        a, pre = res["ATT"], res["pretrend"]
        row = dict(version=vlab, outcome=olab, control=ctrl, att=a["theta"], lo=a["lo"], hi=a["hi"], p=a["p"],
                   se=a["se"], mde=a["mde"], n_cells=a["n_cells"], n_inst=a["n_inst"], n_comp=a["n_comp"],
                   n_ctrl=a["n_ctrl"], pre_p=pre["p"] if pre else np.nan, pre_k=pre["k"] if pre else 0,
                   verdict=verdict(a, pre))
        for e in EVENT_TIMES:
            r = res.get(f"e{e}")
            row[f"e{e}"] = r["theta"] if r else np.nan
            row[f"e{e}_lo"] = r["lo"] if r else np.nan
            row[f"e{e}_hi"] = r["hi"] if r else np.nan
            row[f"e{e}_n"] = r["n_cells"] if r else 0
        rows.append(row)
        say(f"[{olab} | {vlab} | controls={ctrl}] ATT {a['theta']:+.4f} [{a['lo']:+.4f}, {a['hi']:+.4f}] p={a['p']:.3f} "
            f"MDE {a['mde']:.4f}; pre-trend p={'%.3f' % pre['p'] if pre else 'n/a'} (k={pre['k'] if pre else 0}); "
            f"treated cells {a['n_cells']} at {a['n_inst']} inst.; {a['n_comp']} comparisons; ~{a['n_ctrl']} controls "
            f"-> {row['verdict']}")
        say("    event time: " + "; ".join(
            f"e={e}: {row[f'e{e}']:+.4f} [{row[f'e{e}_lo']:+.4f}, {row[f'e{e}_hi']:+.4f}] (n={row[f'e{e}_n']})"
            if row[f"e{e}_n"] else f"e={e}: n/a" for e in EVENT_TIMES))
    R = pd.DataFrame(rows)
    say("\nKEY TABLE (markdown)")
    say("| outcome | version | controls | ATT | 95% CI | MDE | pre-trend p | treated cells (inst.) | verdict |")
    say("|---|---|---|---|---|---|---|---|---|")
    for r in R.itertuples():
        if r.verdict == "not estimable":
            say(f"| {r.outcome} | {r.version} | | | | | | | not estimable |")
            continue
        say(f"| {r.outcome} | {r.version} | {'not-yet + never' if r.control == 'main' else 'already-accredited'} | "
            f"{r.att:+.3f} | [{r.lo:+.3f}, {r.hi:+.3f}] | {r.mde:.3f} | "
            f"{'n/a' if np.isnan(r.pre_p) else f'{r.pre_p:.3f}'} | {r.n_cells} ({r.n_inst}) | {r.verdict} |")
    say("\nEVENT-TIME TABLE (markdown; theta [95% CI] (treated cells))")
    say("| outcome | version | controls | e=-3 | e=-2 | e=0 | e=+1 | e=+2 |")
    say("|---|---|---|---|---|---|---|---|")
    for r in R.itertuples():
        if r.verdict == "not estimable":
            continue
        cells = []
        for e in EVENT_TIMES:
            v, lo, hi, n = getattr(r, f"_{EVENT_TIMES.index(e) + 0}", None), None, None, None
            d = R.loc[r.Index]
            cells.append("—" if not d[f"e{e}_n"] else f"{d[f'e{e}']:+.3f} [{d[f'e{e}_lo']:+.3f}, {d[f'e{e}_hi']:+.3f}] ({d[f'e{e}_n']})")
        say(f"| {r.outcome} | {r.version} | {'not-yet + never' if r.control == 'main' else 'already'} | " + " | ".join(cells) + " |")

    # ================================================================================================
    # EXPLORATORY (added after the first estimating run; not part of the frozen estimates or verdicts)
    # ================================================================================================
    say("\nEXPLORATORY 1 -- CIP-4 mix of the ABET treated cells entering the primary estimates (main controls)")
    for vlab in ("ABET, IT/IS kept", "ABET, IT/IS dropped"):
        recs = store[(vlab, "primary: y1 log p50", "main")]
        ent = {u for r in recs if r["e"] >= 0 for u in r["psi"].index[: r["n"]]}
        say(f"  {vlab}: {len(ent)} cells; by CIP-4 "
            f"{dict(sorted(Counter(u[1] for u in ent).items(), key=lambda kv: (-kv[1], kv[0])))}")

    say("\nEXPLORATORY 2 -- AACSB control pool: never-treated institutions supplying control cells (primary, main controls)")
    recs = store[("AACSB", "primary: y1 log p50", "main")]
    Gb = G_series("aacsb")
    ctrl_use = Counter()
    for r in recs:
        for u in r["psi"].index[r["n"]:]:
            ctrl_use[u[0]] += 1
    tot = sum(ctrl_use.values())
    never_inst = {u[0] for u, g in Gb.items() if g == NEVER}
    grads = av[(av.cip_level == "4") & av.cip.str.startswith("52") & av.rel_y1].groupby(["institution", "cip"]).n_y1.median() \
        .groupby(level=0).sum()
    nv = pd.DataFrame({"uses": pd.Series({i: ctrl_use[i] for i in sorted(never_inst) if ctrl_use[i] > 0})})
    nv["grads"] = grads.reindex(nv.index)
    names = hd.sort_values("year").groupby("opeid8").agg(name=("instnm", "last"), state=("stabbr", "last"))
    nv = nv.join(names).sort_index().sort_values("grads", ascending=False, kind="mergesort")
    say(f"  never-treated institutions used as controls: {len(nv)}, supplying {int(nv.uses.sum())} of {tot} control-cell "
        f"uses ({nv.uses.sum() / tot:.0%}); the 25 largest by business graduates with earnings (median per cell, summed):")
    say(nv.head(25).to_string())

    # ================================================================================================
    # REVISION 1, added after the results had been seen (2026-11-14). The frozen rows above are kept.
    # ================================================================================================
    say("\n" + "=" * 100 + "\nREVISION 1, added after the results had been seen\n" + "=" * 100)
    R1 = np.random.SeedSequence(SEED + 1001)

    def run(parts_spec, out_, ctrl, mode, seed, override=None):
        recs = []
        for d, dr, sh in parts_spec:
            G = G_series(d, sh, override if d == "aacsb" else None)
            rr = cs_components(wide[out_].reindex(G.index), G.to_dict(), treated_frame(d, dr, sh), ctrl)
            for r in rr:
                r["des"] = d
            recs += rr
        agg = aggregate(recs, clusters, mode)
        res = bootstrap(agg, seed)
        a, pre = res["ATT"], res["pretrend"]
        return dict(att=a["theta"], lo=a["lo"], hi=a["hi"], mde=a["mde"], pre_p=pre["p"] if pre else np.nan,
                    n_cells=a["n_cells"], n_inst=a["n_inst"], n_ctrl=a["n_ctrl"], verdict=verdict(a, pre))

    # (R1-1) all 25 frozen specifications under the (g,t)-centred influence function
    say("\n(R1-1) The 25 frozen estimates with the treated side of the influence function demeaned within cohort x window "
        "(pooling fields; CS with field as a covariate). Same point estimates; multiplier bootstrap unchanged otherwise "
        "(unrestricted, not studentised).")
    sds = R1.spawn(len(specs) + 40)
    say("| outcome | version | controls | ATT | frozen 95% CI | frozen MDE | frozen pre p | frozen verdict | "
        "revised 95% CI | revised MDE | revised pre p | revised verdict | treated cells (inst.) |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    changed = 0
    for k, ((vlab, olab, out_, parts, ctrl), fr) in enumerate(zip(specs, rows)):
        r = run(parts, out_, ctrl, "gt", sds[k])
        assert abs(r["att"] - fr["att"]) < 1e-12
        changed += r["verdict"] != fr["verdict"]
        say(f"| {olab} | {vlab} | {'not-yet + never' if ctrl == 'main' else 'already-accredited'} | {fr['att']:+.3f} | "
            f"[{fr['lo']:+.3f}, {fr['hi']:+.3f}] | {fr['mde']:.3f} | {fr['pre_p']:.3f} | {fr['verdict']} | "
            f"[{r['lo']:+.3f}, {r['hi']:+.3f}] | {r['mde']:.3f} | {r['pre_p']:.3f} | {r['verdict']} | "
            f"{r['n_cells']} ({r['n_inst']}) |")
    say(f"  verdicts that change under the revised influence function: {changed} of {len(specs)}")

    # (R1-2) audited AACSB never-treated pool
    say("\n(R1-2) AACSB status audit: frozen never-treated schools found on the AACSB lists under a different name")
    r02 = roster(RAW / "aacsb" / "rosters" / "aacsb_instlists_lid3_20020621044818.html", "2002")
    r26 = sorted(set(e for f in sorted((RAW / "aacsb" / "current").glob("*.html")) for e in roster(f, "2026")))
    ov_already, ov_unknown = {}, {}
    for (rn, st), targets in ROSTER_ALIAS.items():
        in02, in26 = (rn, st) in set(r02), (rn, st) in set(r26)
        assert in02 or in26, (rn, st)
        for tn in targets:
            op = ni.resolve([tn], st)
            assert op and ":" not in op, (tn, op)
            assert Gb.loc[[u for u in Gb.index if u[0] == op]].eq(NEVER).all(), (op, "not frozen never-treated")
            if in02:
                ov_already[op] = (rn, tn)
            elif op not in ov_already:
                ov_unknown[op] = (rn, tn)
    for op in ov_already:
        ov_unknown.pop(op, None)
    say(f"  recoded as already accredited (on the June-2002 list): {len(ov_already)}")
    for op, (rn, tn) in sorted(ov_already.items()):
        say(f"    {op} {tn}  <- '{rn}'  (control-cell uses in the frozen AACSB estimate: {ctrl_use.get(op, 0)})")
    say(f"  excluded as unknown date (only on the 2026 list): {len(ov_unknown)}")
    for op, (rn, tn) in sorted(ov_unknown.items()):
        say(f"    {op} {tn}  <- '{rn}'  (control-cell uses: {ctrl_use.get(op, 0)})")
    v1 = {**{op: 0 for op in ov_already}, **{op: -1 for op in ov_unknown}}
    v2 = {op: 0 for op in ov_already}
    say("| AACSB pool | version | ATT | 95% CI (frozen IF) | MDE | pre p | verdict | 95% CI (revised IF) | MDE | pre p | "
        "verdict | controls per comparison |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|")
    kk = len(specs)
    for plab, ov in (("22 already + 5 unknown", v1), ("22 already, 5 kept as never-treated", v2)):
        for vlab, parts in (("AACSB", [("aacsb", False, 0)]), ("pooled (ABET kept + AACSB)", [("abet", False, 0), ("aacsb", False, 0)]),
                            ("pooled (ABET dropped + AACSB)", [("abet", True, 0), ("aacsb", False, 0)])):
            a = run(parts, "y1", "main", "frozen", sds[kk], ov)
            b = run(parts, "y1", "main", "gt", sds[kk + 1], ov)
            kk += 2
            say(f"| {plab} | {vlab} | {a['att']:+.3f} | [{a['lo']:+.3f}, {a['hi']:+.3f}] | {a['mde']:.3f} | "
                f"{a['pre_p']:.3f} | {a['verdict']} | [{b['lo']:+.3f}, {b['hi']:+.3f}] | {b['mde']:.3f} | "
                f"{b['pre_p']:.3f} | {b['verdict']} | ~{a['n_ctrl']} |")

    # (R1-3) ABET timing: employers learn of a retroactive accreditation after its effective date
    say("\n(R1-3) ABET timing (exploratory): A (frozen), A+1, A+2 (employer-visibility direction), A-2 (frozen "
        "sensitivity, an anticipation test); every ABET date shifted, controls' included")
    say("| timing | version | ATT | 95% CI (frozen IF) | MDE | pre p | verdict | 95% CI (revised IF) | MDE | pre p | "
        "verdict | treated cells |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for sh, tlab in ((0, "A"), (-1, "A+1"), (-2, "A+2"), (2, "A-2")):
        for vlab, dr in (("ABET, IT/IS kept", False), ("ABET, IT/IS dropped", True)):
            a = run([("abet", dr, sh)], "y1", "main", "frozen", sds[kk], None)
            b = run([("abet", dr, sh)], "y1", "main", "gt", sds[kk + 1], None)
            kk += 2
            say(f"| {tlab} | {vlab} | {a['att']:+.3f} | [{a['lo']:+.3f}, {a['hi']:+.3f}] | {a['mde']:.3f} | "
                f"{a['pre_p']:.3f} | {a['verdict']} | [{b['lo']:+.3f}, {b['hi']:+.3f}] | {b['mde']:.3f} | "
                f"{b['pre_p']:.3f} | {b['verdict']} | {a['n_cells']} |")

    # (R1-4) disclosures
    moved = sum(cohort(a) != cohort(a + 1) for a in abet_tc.A)
    say(f"\n(R1-4) scripts/80 counted ABET cells with the first covered class A+1; the estimates use A. Counted cells "
        f"whose first post window differs between A and A+1: {moved} of {len(abet_tc)}")
    say("  treated clusters (institutions) in the primary estimates: " + "; ".join(
        f"{r['version']} {r['n_inst']}" for r in rows if r.get("outcome") == "primary: y1 log p50" and "pooled" not in r["version"]))


def status_only():
    """treatment-status checks only (no outcome data)"""
    global PSEO
    PSEO = s80.load_pseo()
    av = s80.availability(PSEO)
    ni = s80.NameIndex(s80.load_hd(), set(av.institution))
    st = abet_status(ni, av)
    say(f"ABET PSEO cells with records: {len(st)}; A<=2001: {int((st.A <= 2001).sum())}; 2002-2016: "
        f"{int(st.A.between(2002, 2016).sum())}; 2017+: {int((st.A >= 2017).sum())}")
    tc, init, already, unknown = aacsb_status(ni, av)
    say(f"AACSB treated cells {len(tc)} at {tc.opeid.nunique()} inst.; cohorts {dict(sorted(Counter(tc.A).items()))}")


if __name__ == "__main__" and "--status" in sys.argv:
    status_only()
elif __name__ == "__main__":
    main()
