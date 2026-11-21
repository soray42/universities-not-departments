"""80 -- Feasibility of three quasi-experimental designs on public data (counts and power only).

Counts events and computes minimum detectable effects (MDE). It estimates NO treatment effect and never
looks at outcome changes around events: for event cells it reads only existence, release-status flags and
graduate counts; noise is computed in separate pooled functions over all cells (event cells are not singled out).

  (A) name shocks: IPEDS directory names 1999-2019 by UNITID; upgrade-type renamings 2000-2018 at PSEO
      institutions; outcome would be PSEO bachelor's log p50 earnings (3-year graduation windows).
  (B) department credential shocks: first-time ABET (EAC/CAC, bachelor's) accreditation 2002-2016 from the
      ABET public API; first-time AACSB business accreditation 2002-2016 from AACSB's own "newly accredited"
      pages (Internet Archive captures). Outcome as in (A), field-matched.
  (C) department reputation shocks: Nobel prizes (physics, chemistry, medicine, economics) 1995-2018 by
      affiliation at award time (nobelprize.org API); outcome would be IPEDS bachelor's completions
      (annual C files 1990-2023) in the matching field.

Run:  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I -B scripts/80_causal_feasibility.py
Inputs: data/raw/{ipeds_hd, ipeds_c_annual, ipeds, abet, aacsb, nobel, pseo_2026q2} (see data/sources.csv).
Memory: reads files one at a time with usecols; peak well under 1 GB. Single process.
"""
from __future__ import annotations

import glob
import html
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PSEO_E = RAW / "pseo_2026q2" / "pseoe_all.csv.gz"
PSEO_I = RAW / "pseo_2026q2" / "pseo_all_institutions.csv"
HD_DIR = RAW / "ipeds_hd"
C_DIR = RAW / "ipeds_c_annual"
ABET_DIR = RAW / "abet" / "pages"
AACSB_DIR = RAW / "aacsb" / "wayback"
NOBEL = RAW / "nobel" / "laureates_v2.1_all.json"

COHORTS = [2001, 2004, 2007, 2010, 2013, 2016, 2019]      # PSEO bachelor's 3-year windows c..c+2
Z = 1.959964 + 0.841621                                    # two-sided 5%, power 80%  (= 2.80)
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_colwidth", 70)


def say(*a):
    print(*a, flush=True)


def head(t):
    say("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# ----------------------------------------------------------------------------------------------------
# name normalisation (shared by IPEDS name history, ABET and AACSB matching)
# ----------------------------------------------------------------------------------------------------
ABBR = {"univ": "university", "coll": "college", "inst": "institute", "saint": "st", "ctr": "center",
        "cmty": "community", "comm": "community", "sch": "school", "intl": "international", "mt": "mount",
        "ft": "fort", "technological": "technology", "tech": "technology", "u": "university",
        "suny": "state university new york", "cuny": "city university new york"}
STOP = {"the", "of", "at", "and", "in", "a", "an", "inc", "main", "campus", "for", "on"}


def norm(s: str) -> str:
    s = str(s).lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(ABBR.get(t, t) for t in s.split())


def key(s: str) -> str:
    """order-preserving, stop words dropped: the matching key"""
    return " ".join(t for t in norm(s).split() if t not in STOP)


def core(s: str) -> tuple:
    return tuple(sorted(key(s).split()))


# ----------------------------------------------------------------------------------------------------
# PSEO: availability (flags/counts only) and pooled noise (all cells)
# ----------------------------------------------------------------------------------------------------
def load_pseo() -> pd.DataFrame:
    use = ["inst_level", "institution", "degree_level", "cip_level", "cipcode", "grad_cohort",
           "grad_cohort_years", "status_y1_earnings", "y1_p50_earnings", "y1_grads_earn",
           "status_y5_earnings", "y5_p50_earnings", "y5_grads_earn"]
    parts = []
    for ch in pd.read_csv(PSEO_E, dtype=str, usecols=use, chunksize=200_000):
        ch = ch[(ch.inst_level == "I") & (ch.degree_level == "05") & ch.cip_level.isin(["2", "4"]) &
                (ch.grad_cohort_years == "3") & (ch.grad_cohort != "0000")]
        parts.append(ch.drop(columns=["inst_level", "degree_level", "grad_cohort_years"]))
    d = pd.concat(parts, ignore_index=True)
    d["c"] = d.grad_cohort.astype(int)
    d = d[d.c.isin(COHORTS)]
    for h in ("y1", "y5"):
        d[f"rel_{h}"] = (d[f"status_{h}_earnings"] == "1")
        d[f"p50_{h}"] = pd.to_numeric(d[f"{h}_p50_earnings"], errors="coerce")
        d[f"n_{h}"] = pd.to_numeric(d[f"{h}_grads_earn"], errors="coerce")
        d.loc[~d[f"rel_{h}"], f"p50_{h}"] = np.nan
    d["cip"] = d.cipcode.str.replace(".", "", regex=False)
    keep = ["institution", "cip_level", "cip", "c", "rel_y1", "rel_y5", "p50_y1", "p50_y5", "n_y1", "n_y5"]
    return d[keep].reset_index(drop=True)


def availability(p: pd.DataFrame) -> pd.DataFrame:
    """FIREWALL: what event-side code may see -- release flags and counts, no earnings values."""
    return p[["institution", "cip_level", "cip", "c", "rel_y1", "rel_y5", "n_y1", "n_y5"]].copy()


def window_side(c: int, e: int, strict: bool = False) -> str:
    """pre if the window (c..c+2) ends before event year e; post if it starts at or after e; else straddle.
    strict: pre must end by e-2 and post start at e+1 (one-year guard band on each side)."""
    if c + 2 <= e - (2 if strict else 1):
        return "pre"
    if c >= e + (1 if strict else 0):
        return "post"
    return "straddle"


def usable_cells(av: pd.DataFrame, inst: str, e: int, cip_level: str, cips=None, h="y1",
                 strict: bool = False) -> pd.DataFrame:
    """cells of one institution with a released window before and one after year e (flags only)."""
    x = av[(av.institution == inst) & (av.cip_level == cip_level) & av[f"rel_{h}"]]
    if cips is not None:
        x = x[x.cip.isin(cips)]
    if x.empty:
        return x.assign(side=[])
    x = x.assign(side=[window_side(c, e, strict) for c in x.c])
    g = x.groupby("cip").side.agg(lambda s: ("pre" in set(s)) and ("post" in set(s)))
    ok = g[g].index
    return x[x.cip.isin(ok) & (x.side != "straddle")]


def pseo_noise(p: pd.DataFrame, h="y1", cip_level="4") -> dict:
    """Pooled noise over ALL institution x field cells (no event information used)."""
    x = p[(p.cip_level == cip_level) & p[f"rel_{h}"] & (p[f"p50_{h}"] > 0)][
        ["institution", "cip", "c", f"p50_{h}", f"n_{h}"]].copy()
    x["y"] = np.log(x[f"p50_{h}"])
    x["r"] = x.y - x.groupby(["cip", "c"]).y.transform("mean")       # net of field x window effects
    out = {"cells": x.groupby(["institution", "cip"]).ngroups, "obs": len(x)}
    for col, lab in (("y", "raw"), ("r", "net")):
        g = x.groupby(["institution", "cip"])[col]
        k = g.transform("count")
        dev = x[col] - g.transform("mean")
        df = (g.count() - 1).clip(lower=0).sum()
        out[f"s2_within_{lab}"] = float((dev[k >= 2] ** 2).sum() / df)
    out["frame"] = x
    return out


def contrasts(x: pd.DataFrame, split: int, level="cell") -> pd.DataFrame:
    """Placebo pre/post contrasts at a split year for every unit with a window on each side -- noise only.
    level='cell': institution x field; level='inst': institution mean over its cells."""
    s = x.assign(side=[window_side(c, split) for c in x.c])
    s = s[s.side != "straddle"]
    if level == "inst":
        s = s.groupby(["institution", "c", "side"], as_index=False).r.mean()
        grp = ["institution"]
    else:
        grp = ["institution", "cip"]
    m = s.groupby(grp + ["side"]).r.mean().unstack("side").dropna(subset=["pre", "post"])
    return (m["post"] - m["pre"]).rename("con").reset_index()


def unit_sizes(x: pd.DataFrame, ncol: str) -> tuple[pd.Series, pd.Series]:
    """cell size = median graduates with earnings over released windows; institution size = sum over its cells"""
    cs = x.groupby(["institution", "cip"])[ncol].median()
    return cs, cs.groupby(level=0).sum()


def mde(var_unit: float, n_t: int, n_c: int | None = None) -> float:
    if n_t <= 0:
        return float("nan")
    f = 1.0 + (n_t / n_c if n_c else 0.0)
    return Z * np.sqrt(var_unit / n_t * f)


def power_block(tag: str, noise: dict, splits: list[int], sizes: list[float], n_inst: int, n_clusters: int,
                npre: float, npost: float, level_note="y1 log p50", unit="inst", n_cells: int | None = None) -> dict:
    """MDEs from noise only. One entry of splits/sizes per treated unit (institution if unit='inst', cell otherwise).
    Headline: placebo contrast variance among units in the event unit's size quintile, averaged over events."""
    x = noise["frame"]
    ncol = [c for c in x.columns if c.startswith("n_")][0]
    cs, is_ = unit_sizes(x, ncol)
    sz = (is_ if unit == "inst" else cs).rename("size")
    edges = np.quantile(sz.dropna(), [0.2, 0.4, 0.6, 0.8])
    sbin = pd.Series(np.searchsorted(edges, sz.values), index=sz.index, name="bin")
    lev = "inst" if unit == "inst" else "cell"
    keys = ["institution"] if lev == "inst" else ["institution", "cip"]
    v_all, v_bin, n_ctrl = [], [], []
    cache = {}
    for e, z in zip(splits, sizes):
        if e not in cache:
            c = contrasts(x, int(e), lev)
            c = c.join(sbin, on=keys)
            cache[e] = c
        c = cache[e]
        b = int(np.searchsorted(edges, z)) if pd.notna(z) else None
        v_all.append(float(c.con.var(ddof=1)))
        v_bin.append(float(c[c.bin == b].con.var(ddof=1)) if b is not None else float(c.con.var(ddof=1)))
        n_ctrl.append(len(c))
    V_all, V_bin = float(np.mean(v_all)), float(np.mean(v_bin))
    n_t = len(splits)
    n_cells = n_cells if n_cells is not None else n_t
    ebins = Counter(int(np.searchsorted(edges, z)) + 1 for z in sizes if pd.notna(z))
    r = dict(n_units=n_t, n_inst=n_inst, n_cells=n_cells, n_clusters=n_clusters, V_all=V_all, V_size=V_bin,
             mde_all=mde(V_all, n_t, int(np.mean(n_ctrl))), mde_size=mde(V_bin, n_t, int(np.mean(n_ctrl))),
             mde_cluster=mde(V_bin, n_clusters, int(np.mean(n_ctrl))),
             mde_iid_raw=Z * np.sqrt(noise["s2_within_raw"] * (1 / npre + 1 / npost) / max(n_cells, 1)),
             mde_iid_net=Z * np.sqrt(noise["s2_within_net"] * (1 / npre + 1 / npost) / max(n_cells, 1)))
    say(f"\nPOWER ({tag}), {level_note}; noise from all PSEO cells of this frame (event cells not singled out):")
    say(f"  literal: within-cell cross-window variance of log p50 = {noise['s2_within_raw']:.5f} raw "
        f"(SD {np.sqrt(noise['s2_within_raw']):.4f}), {noise['s2_within_net']:.5f} net of field x window "
        f"(SD {np.sqrt(noise['s2_within_net']):.4f}); {noise['cells']} cells")
    say(f"  iid MDE = 2.8*sqrt(s2*(1/npre+1/npost)/N_cells), npre={npre:.2f}, npost={npost:.2f}, N_cells={n_cells}: "
        f"raw {r['mde_iid_raw']:.4f}, net {r['mde_iid_net']:.4f}")
    say(f"  placebo {lev}-level post-minus-pre contrast at the events' splits: all units var {V_all:.5f} "
        f"(SD {np.sqrt(V_all):.4f}); same size quintile var {V_bin:.5f} (SD {np.sqrt(V_bin):.4f}); "
        f"~{int(np.mean(n_ctrl))} control units per split")
    say(f"  event units by size quintile of all {lev}s (1 = smallest): {dict(sorted(ebins.items()))}")
    say(f"  MDE, N={n_t} treated {lev}s, size-matched noise: {r['mde_size']:.4f}   <- headline "
        f"(all-unit noise: {r['mde_all']:.4f})")
    say(f"  MDE with N={n_clusters} clusters as units (conservative): {r['mde_cluster']:.4f}")
    r["headline"] = r["mde_size"]
    return r


def pseo_scales(noise: dict) -> dict:
    """in-data scales for judging MDEs (all cells): SD of institution effects and of department deviations"""
    x = noise["frame"]
    cell = x.groupby(["institution", "cip"]).r.mean().rename("cell").reset_index()
    inst = cell.groupby("institution").cell.mean().rename("inst")
    cell = cell.join(inst, on="institution")
    ninst = cell.groupby("institution").size()
    dev = (cell.cell - cell.inst)[cell.institution.map(ninst) >= 3]
    return {"sd_inst": float(inst[ninst[inst.index] >= 3].std()), "sd_dept_within": float(dev.std()),
            "n_inst": int((ninst >= 3).sum())}


# ----------------------------------------------------------------------------------------------------
# IPEDS directory (HD) panel 1999-2019
# ----------------------------------------------------------------------------------------------------
HD_FILES = {1999: "IC99_HD", 2000: "FA2000HD", 2001: "FA2001HD", **{y: f"HD{y}" for y in range(2002, 2020)}}
HD_COLS = ["unitid", "instnm", "city", "stabbr", "opeid", "act", "newid", "sector", "iclevel"]


def _cl(c: str) -> str:
    return c.replace("\ufeff", "").replace("ï»¿", "").strip().lower()


def _read_zip_csv(path: Path, cols_lower: list[str] | None, prefer_rv=True) -> pd.DataFrame:
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if n.lower().endswith(".csv")]
    rv = [n for n in names if n.lower().endswith("_rv.csv")]
    nm = (rv if (prefer_rv and rv) else [n for n in names if n not in rv] or names)[0]
    with z.open(nm) as fh:
        d = pd.read_csv(fh, dtype=str, encoding="latin-1",
                        usecols=(lambda c: _cl(c) in cols_lower) if cols_lower else None)
    d.columns = [_cl(c) for c in d.columns]
    return d


def load_hd() -> pd.DataFrame:
    out = []
    for y, f in HD_FILES.items():
        d = _read_zip_csv(HD_DIR / f"{f}.zip", HD_COLS)
        d["year"] = y
        out.append(d)
    hd = pd.concat(out, ignore_index=True)
    for c in hd.columns:
        if c != "year":
            hd[c] = hd[c].astype(str).str.strip().replace({"nan": None})
    hd["opeid8"] = hd.opeid.fillna("").str.replace(r"\D", "", regex=True).str.zfill(8)
    return hd


# ----------------------------------------------------------------------------------------------------
# (A) name shocks
# ----------------------------------------------------------------------------------------------------
UNI = {"university", "universidad"}
TYPEW = {"college", "school", "institute", "center", "seminary", "academy"} | UNI


def cls_tokens(s: str, expand_system: bool = False) -> set:
    """raw lower-case words for classification (univ/coll/inst expanded; SUNY/CUNY expanded only on request)"""
    s = re.sub(r"[^a-z0-9 ]", " ", str(s).lower().replace("&", " and "))
    out = set()
    for t in s.split():
        t = {"univ": "university", "unversity": "university", "coll": "college", "inst": "institute",
             "cmty": "community", "comm": "community"}.get(t, t)
        if expand_system and t in ("suny", "cuny"):
            out |= {"state" if t == "suny" else "city", "university"}
        else:
            out.add(t)
    return out


def classify_change(old: str, new: str, merged: bool) -> str:
    no, nn = norm(old), norm(new)
    if core(old) == core(new):
        return "cosmetic"
    if (len(old) >= 45 or len(new) >= 45) and (nn.startswith(no) or no.startswith(nn)):
        return "cosmetic"                                            # IPEDS 50-character truncation
    if SequenceMatcher(None, no, nn).ratio() >= 0.95:
        return "cosmetic"                                            # spelling fix
    to, tn = cls_tokens(old, True), cls_tokens(new, True)            # SUNY/CUNY count as 'University'
    tn_raw = cls_tokens(new)
    if not (to & TYPEW) and nn.startswith(no):
        return "cosmetic"                                            # name completed ("Furman" -> "Furman University")
    if merged:
        return "merger"
    if not (to & UNI) and (tn & UNI):
        if not (tn_raw & UNI) or (tn_raw & (TYPEW - UNI)):
            return "other_system_affiliation"                        # 'University' enters only as a system name
        return "upgrade_college_to_university"
    if (to & {"community", "junior"}) and not (tn & {"community", "junior"}) and (tn & ({"college"} | UNI)):
        return "upgrade_drop_two_year_marker"
    if (to & UNI) and not (tn & UNI):
        return "other_downgrade"
    return "other_lateral"


def name_changes(hd: pd.DataFrame) -> pd.DataFrame:
    h = hd.sort_values(["unitid", "year"]).copy()
    h["n"] = h.instnm.map(norm)
    g = h.groupby("unitid")
    h["prev_name"], h["prev_n"], h["prev_year"] = g.instnm.shift(), g.n.shift(), g.year.shift()
    h["next_n"], h["next_year"] = g.n.shift(-1), g.year.shift(-1)
    h["next2_n"] = g.n.shift(-2)
    ch = h[h.prev_n.notna() & (h.n != h.prev_n) & (h.prev_year == h.year - 1) & h.year.between(2000, 2018)].copy()
    # absorbed institutions: ACT == 'C' (combined) with NEWID = absorber, any year
    comb = hd[(hd.act == "C") & hd.newid.notna() & ~hd.newid.isin(["-2", "-1", "0", ""])]
    absorb = defaultdict(set)
    for u, y in zip(comb.newid, comb.year):
        absorb[u].add(y)
    absorbed = defaultdict(set)                                       # this UNITID itself combined into another
    for u, y in zip(comb.unitid, comb.year):
        absorbed[u].add(y)
    ch["merged"] = [any((y + k) in absorb.get(u, ()) or (y + k) in absorbed.get(u, ()) for k in (-1, 0, 1, 2))
                    for u, y in zip(ch.unitid, ch.year)]
    ch["merger_later"] = [any((y + k) in absorb.get(u, ()) or (y + k) in absorbed.get(u, ()) for k in range(3, 10))
                          for u, y in zip(ch.unitid, ch.year)]
    ch["merger_before"] = [any((y + k) in absorb.get(u, ()) or (y + k) in absorbed.get(u, ()) for k in range(-8, -1))
                           for u, y in zip(ch.unitid, ch.year)]
    ch["persists"] = [(pd.isna(nx) or nx == n or core(nx) == core(n)) and not (pd.notna(n2) and n2 == p)
                      for n, nx, n2, p in zip(ch.n, ch.next_n, ch.next2_n, ch.prev_n)]
    ch["cls"] = [classify_change(o, nw, m) for o, nw, m in zip(ch.prev_name, ch.instnm, ch.merged)]
    return ch


def design_a(hd, av, noise_y1, noise_y5):
    head("(A) NAME SHOCKS -- IPEDS directory names by UNITID, 1999-2019")
    ins = pd.read_csv(PSEO_I, dtype=str, encoding="utf-8-sig")
    bach_inst = set(av.institution)
    say(f"PSEO V4.14.1 institutions: {ins.institution.nunique()}; with bachelor's rows (3-yr windows): {len(bach_inst)}")
    op_any = set(hd.opeid8)
    say(f"PSEO institutions matched to an IPEDS OPEID (any HD year 1999-2019): "
        f"{sum(i in op_any for i in ins.institution)} / {ins.institution.nunique()}; "
        f"bachelor's institutions matched: {sum(i in op_any for i in bach_inst)} / {len(bach_inst)}")
    op2u = hd[hd.opeid8.isin(bach_inst)].groupby("opeid8").unitid.agg(lambda s: sorted(set(s)))
    multi = op2u[op2u.map(len) > 1]
    say(f"bachelor's PSEO OPEIDs mapping to >1 UNITID over 1999-2019: {len(multi)} (handled: an event at any "
        f"UNITID of the OPEID is attributed to the PSEO institution and flagged)")
    u2op = {u: op for op, us in op2u.items() for u in us}

    ch = name_changes(hd)
    ch = ch[ch.persists]
    say(f"\nall UNITIDs: name changes 2000-2018 (normalised name differs, new name persists): {len(ch)}")
    say(ch.cls.value_counts().to_string())
    four = ch[ch.iclevel == "1"]
    say(f"\nfour-year institutions (ICLEVEL=1): {len(four)}")
    say(four.cls.value_counts().to_string())

    ch = ch.assign(pseo=ch.unitid.map(u2op))
    cp = ch[ch.pseo.notna()].copy()
    say(f"\nat PSEO bachelor's institutions (via OPEID): {len(cp)} changes at {cp.pseo.nunique()} institutions")
    say(cp.cls.value_counts().to_string())

    up = cp[cp.cls.str.startswith("upgrade")].copy()
    rows = []
    for r in up.itertuples():
        row = dict(unitid=r.unitid, opeid=r.pseo, state=r.stabbr, year=int(r.year), old=r.prev_name,
                   new=r.instnm, cls=r.cls, multi_unitid=r.pseo in multi.index, merger_later=bool(r.merger_later),
                   merger_before=bool(r.merger_before))
        for h in ("y1", "y5"):
            u4 = usable_cells(av, r.pseo, int(r.year), "4", h=h)
            u2 = usable_cells(av, r.pseo, int(r.year), "2", h=h)
            row[f"cells4_{h}"] = u4.cip.nunique()
            row[f"cells2_{h}"] = u2.cip.nunique()
            if h == "y1":
                row["npre_y1"] = float(u4[u4.side == "pre"].groupby("cip").c.nunique().mean()) if len(u4) else np.nan
                row["npost_y1"] = float(u4[u4.side == "post"].groupby("cip").c.nunique().mean()) if len(u4) else np.nan
                row["grads_y1_median"] = float(u4.n_y1.median()) if len(u4) else np.nan
                row["max_npre_y1"] = int(u4[u4.side == "pre"].groupby("cip").c.nunique().max()) if len(u4) else 0
        row["cells4_y1_strict"] = usable_cells(av, r.pseo, int(r.year), "4", h="y1", strict=True).cip.nunique()
        rows.append(row)
    ev = pd.DataFrame(rows)
    say(f"\nupgrade-type renamings at PSEO bachelor's institutions: {len(ev)} "
        f"({ev.cls.value_counts().to_dict() if len(ev) else {}})")
    if len(ev):
        say(f"  event years: {dict(sorted(Counter(ev.year).items()))}")
        say(f"  structural loss: events before 2004 cannot have a pre window (first window 2001-03): "
            f"{int((ev.year < 2004).sum())}")
    usable = ev[ev.cells4_y1 > 0] if len(ev) else ev
    say(f"\nUSABLE (>=1 CIP-4 cell with released y1 earnings in a window before and one after): "
        f"{len(usable)} institutions, {int(usable.cells4_y1.sum()) if len(usable) else 0} institution x CIP-4 cells")
    if len(ev):
        say(f"  y5 horizon: {int((ev.cells4_y5 > 0).sum())} institutions, {int(ev.cells4_y5.sum())} cells")
        say(f"  CIP-2 fallback (y1): {int((ev.cells2_y1 > 0).sum())} institutions, {int(ev.cells2_y1.sum())} cells")
        say(f"  strict timing (pre ends <= e-2, post starts >= e+1): {int((ev.cells4_y1_strict > 0).sum())} "
            f"institutions, {int(ev.cells4_y1_strict.sum())} cells")
    if len(usable):
        cl = usable.groupby(["state", "year"]).size()
        say(f"  state x year clusters among usable events: {len(cl)}; largest clusters: "
            f"{cl.sort_values(ascending=False).head(6).to_dict()}")
        say(f"  usable events at multi-UNITID OPEIDs: {int(usable.multi_unitid.sum())}; with an IPEDS merger 3-9 years "
            f"after the rename (contaminates post windows): {int(usable.merger_later.sum())} "
            f"{list(usable[usable.merger_later].new)}; 2-8 years before (contaminates pre windows): "
            f"{int(usable.merger_before.sum())} {list(usable[usable.merger_before].new)}")
        clean = usable[~usable.merger_later & ~usable.merger_before]
        say(f"  USABLE AND MERGER-FREE: {len(clean)} institutions, {int(clean.cells4_y1.sum())} cells; with >=2 released "
            f"pre windows in some cell (a pre-trend check is possible): {int((clean.max_npre_y1 >= 2).sum())}")
    say("\nall upgrade-type events at PSEO institutions:")
    if len(ev):
        say(ev[["year", "state", "unitid", "opeid", "old", "new", "cls", "cells4_y1", "cells4_y5",
                "cells2_y1", "cells4_y1_strict", "npre_y1", "npost_y1", "merger_later", "merger_before"]].sort_values(["year", "state"]).to_string(index=False))
    oth = cp[~cp.cls.str.startswith("upgrade") & (cp.cls != "cosmetic")]
    say("\nnon-upgrade substantive changes at PSEO institutions (merger / other) -- listed for audit:")
    say(oth[["year", "stabbr", "unitid", "prev_name", "instnm", "cls"]].sort_values("year").to_string(index=False))

    # ---- power: placebo pre/post contrasts over ALL cells at the events' split years (noise only) ----
    res = {}
    if len(usable):
        pw = usable[~usable.merger_later & ~usable.merger_before]          # power on the merger-free usable set
        sizes = [float(av[(av.institution == op) & (av.cip_level == "4") & av.rel_y1].groupby("cip").n_y1.median().sum())
                 for op in pw.opeid]
        res = power_block("A, merger-free usable events", noise_y1, pw.year.astype(int).tolist(), sizes,
                          n_inst=len(pw), n_clusters=pw.groupby(["state", "year"]).ngroups, npre=pw.npre_y1.mean(),
                          npost=pw.npost_y1.mean(), unit="inst", n_cells=int(pw.cells4_y1.sum()),
                          level_note="y1 log p50, all CIP-4 cells, institution means")
        sc = pseo_scales(noise_y1)
        res.update(sc)
        say(f"  scale: SD of institution effects (field x window-adjusted log y1 p50, institutions with >=3 cells, "
            f"N={sc['n_inst']}) = {sc['sd_inst']:.4f}; within-institution SD of department deviations = "
            f"{sc['sd_dept_within']:.4f}; headline MDE / SD(institution) = {res['headline'] / sc['sd_inst']:.2f}")
    return ev, res


# ----------------------------------------------------------------------------------------------------
# institution name index for ABET / AACSB matching
# ----------------------------------------------------------------------------------------------------
class NameIndex:
    """(normalised IPEDS name, state) -> UNITIDs over 1999-2019; UNITID -> all OPEIDs it carried."""

    def __init__(self, hd: pd.DataFrame, pseo_ops: set):
        self.idx = defaultdict(set)
        for nm, st, u in zip(hd.instnm, hd.stabbr, hd.unitid):
            self.idx[(key(nm), st)].add(u)
        self.u2op = hd.groupby("unitid").opeid8.agg(lambda s: set(s)).to_dict()
        self.last_op = hd.sort_values("year").groupby("unitid").opeid8.last().to_dict()
        self.pseo = pseo_ops

    def resolve(self, names: list[str], st: str, alias_name: str | None = None) -> str | None:
        us = set()
        for n in names:
            us |= self.idx.get((key(n), st), set())
        if not us and alias_name:
            us = self.idx.get((key(alias_name), st), set())
        if not us:
            return None
        ops = {op for u in us for op in self.u2op.get(u, ()) if op in self.pseo}
        if len(ops) == 1:
            return ops.pop()
        if len(ops) > 1:
            return "AMBIG:" + "|".join(sorted(ops))
        return "NONPSEO:" + "|".join(sorted({self.last_op[u] for u in us}))


STATE = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
         "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "D.C.": "DC", "Florida": "FL",
         "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
         "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
         "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
         "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
         "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
         "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
         "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
         "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Puerto Rico": "PR",
         "Guam": "GU", "Virgin Islands": "VI"}


# ----------------------------------------------------------------------------------------------------
# (B1) ABET first-time accreditation (EAC/CAC, bachelor's)
# ----------------------------------------------------------------------------------------------------
ABET_CIP = {  # ABET discipline -> PSEO CIP-4 (CIP 2020); ambiguous disciplines left out (None)
    "Computer Science": "1107", "Cybersecurity": "1110", "Information Technology": "1101",
    "Information Systems": "1104", "Data Science": None, "General Criteria Only (CAC)": None,
    "Aerospace Engineering": "1402", "Agricultural Engineering": "1403", "Architectural Engineering": "1404",
    "Bioengineering and Biomedical Engineering": "1405", "Biological Engineering": "1445",
    "Ceramic Engineering": "1406", "Chemical, Biochemical, Biomolecular Engineering": "1407",
    "Civil Engineering": "1408", "Computer Engineering": "1409", "Software Engineering": "1409",
    "Construction Engineering": "1433", "Electrical and Electronics Engineering": "1410",
    "Telecommunications Engineering": "1410", "Engineering Management": "1515", "Engineering Mechanics": "1411",
    "Engineering, General Engineering, Engineering Physics, and Engineering Science": "1401",
    "Environmental Engineering": "1414", "Forest Engineering": "1434", "Geological Engineering": "1439",
    "Industrial Engineering": "1435", "Manufacturing Engineering": "1436", "Materials Engineering": "1418",
    "Mechanical Engineering": "1419", "Mechatronics and Robotics Engineering": "1442",
    "Metallurgical Engineering": "1420", "Mining Engineering": "1421",
    "Naval Architecture and Marine Engineering": "1422", "Nuclear and Radiological Engineering": "1423",
    "Ocean Engineering": "1424", "Petroleum Engineering": "1425", "Surveying and Geomatics Engineering": "1438",
    "Systems Engineering": "1427", "Cybersecurity Engineering": None, "Ecological Engineering": None,
    "Fire Protection Engineering": None, "General Criteria Only (EAC)": None, "Optical Engineering": None,
    "Optical and Photonic Engineering": None,
}


def load_abet() -> pd.DataFrame:
    rows = {}
    for f in sorted(ABET_DIR.glob("*.json")):
        for r in json.loads(f.read_text())["value"]:
            rows[json.dumps(r, sort_keys=True)] = r
    d = pd.DataFrame(list(rows.values()))
    d["first_year"] = d.accreditationDates.fillna("").map(
        lambda t: min([int(y) for y in re.findall(r"(?:19|20)\d\d", t)] or [np.nan]))
    return d


ALIAS = {  # (source name, state) -> IPEDS institution name (same state); identity hand-confirmed from official names
    ("University of Lowell", "MA"): "University of Massachusetts-Lowell",
    ("Pennsylvania State University, Behrend College", "PA"): "Pennsylvania State University-Penn State Erie-Behrend College",
    ("Penn State Altoona", "PA"): "Pennsylvania State University-Penn State Altoona",
    ("Pennsylvania State University, Wilkes-Barre Campus", "PA"): "Pennsylvania State University-Penn State Wilkes-Barre",
    ("Pennsylvania State University, Berks Campus, Berks-Lehigh Valley College", "PA"): "Pennsylvania State University-Penn State Berks",
    ("Pennsylvania State University, Harrisburg, The Capital College", "PA"): "Pennsylvania State University-Penn State Harrisburg",
    ("Miami University", "OH"): "Miami University-Oxford",
    ("University of Michigan", "MI"): "University of Michigan-Ann Arbor",
    ("University of St. Thomas - Minnesota", "MN"): "University of St Thomas",
    ("University of South Carolina", "SC"): "University of South Carolina-Columbia",
    ("University of Minnesota-Minneapolis", "MN"): "University of Minnesota-Twin Cities",
    ("North Carolina Agricultural and Technical State University", "NC"): "North Carolina A & T State University",
    ("Louisiana State University and A&M College", "LA"): "Louisiana State University and Agricultural & Mechanical College",
    ("Southern University and Agricultural & Mechanical College", "LA"): "Southern University and A & M College",
    ("Rutgers, The State University of New Jersey", "NJ"): "Rutgers University-New Brunswick",
    ("Purdue University at West Lafayette", "IN"): "Purdue University-Main Campus",
    ("University of Oklahoma", "OK"): "University of Oklahoma-Norman Campus",
    ("Iowa State University of Science and Technology", "IA"): "Iowa State University",
    ("The University of Texas at Brownsville & Texas Southmost College", "TX"): "The University of Texas at Brownsville",
    ("State University of New York at Farmingdale", "NY"): "Farmingdale State College",
    ("University at Albany - State University of New York", "NY"): "SUNY at Albany",
    ("Mankato State University", "MN"): "Minnesota State University-Mankato",
    ("University of the District of Columbia-Van Ness Campus", "DC"): "University of the District of Columbia",
    ("State University of New York at Plattsburgh", "NY"): "SUNY College at Plattsburgh",
    ("State University of New York at Oswego", "NY"): "SUNY College at Oswego",
    ("University of Pittsburgh at Johnstown", "PA"): "University of Pittsburgh-Johnstown",
    ("The Citadel", "SC"): "Citadel Military College of South Carolina",
    ("University of Northwestern", "MN"): "University of Northwestern-St Paul",
    ("Grace College & Seminary", "IN"): "Grace College and Theological Seminary",
    ("Anderson University (Indiana)", "IN"): "Anderson University",
    ("Anderson University (South Carolina)", "SC"): "Anderson University",
    ("Utah Tech University", "UT"): "Dixie State University",
    ("Monmouth College", "NJ"): "Monmouth University",
    ("Brigham Young University - College of Physical and Mathematical Sciences", "UT"): "Brigham Young University-Provo",
    ("Parks College of Engineering and Aviation, St. Louis University", "MO"): "Saint Louis University",
    ("Webb Institute of Naval Architecture", "NY"): "Webb Institute",
    ("The Cooper Union", "NY"): "Cooper Union for the Advancement of Science and Art",
    ("Drexel University, College of Information Science & Technology", "PA"): "Drexel University",
    ("LeMoyne-Owen College", "TN"): "Le Moyne-Owen College",
    ("Tulane University", "LA"): "Tulane University of Louisiana",
    # cross-state: ABET lists Kaplan University at its Chicago headquarters; IPEDS main campus is Davenport, IA
    ("Kaplan University", "IL"): ("Kaplan University", "IA"),
}


def design_b_abet(abet, ni, av, pseo_states, noise_tech):
    head("(B1) ABET FIRST-TIME ACCREDITATION, bachelor's EAC + CAC, 2002-2016 (ABET public API)")
    say(f"ABET US programme records: {len(abet)} unique rows; by commission x level: "
        f"{abet.groupby(['commissionName', 'degreeLevelCode']).size().to_dict()}")
    b = abet[(abet.degreeLevelCode == "B") & abet.commissionName.isin(["EAC", "CAC"])].copy()
    say(f"bachelor's EAC/CAC rows: {len(b)} (ETAC = engineering technology, CIP 15, left out by design; "
        f"ETAC bachelor's rows: {int(((abet.degreeLevelCode == 'B') & (abet.commissionName == 'ETAC')).sum())})")
    b["cip"] = b.disciplineName.map(ABET_CIP)
    say(f"  rows with a CIP-4 mapping: {int(b.cip.notna().sum())}; unmapped disciplines: "
        f"{b[b.cip.isna()].disciplineName.value_counts().to_dict()}")
    b = b[b.cip.notna() & b.first_year.notna()]
    cell = b.groupby(["organizationId", "cip"]).agg(
        name=("organizationName", "first"), state=("organizationStateCode", "first"),
        alt=("organizationAlternateName", "first"), first_year=("first_year", "min"),
        commission=("commissionName", "first"), progs=("programName", lambda s: "; ".join(sorted(set(s))))).reset_index()
    say(f"organisation x CIP-4 cells (first accreditation = earliest date over all programmes and intervals): {len(cell)}")
    cell["opeid"] = [ni.resolve([ALIAS[(n, st)][0]], ALIAS[(n, st)][1]) if isinstance(ALIAS.get((n, st)), tuple)
                     else ni.resolve([n] + ([a] if isinstance(a, str) and a else []), st, ALIAS.get((n, st)))
                     for n, st, a in zip(cell.name, cell.state, cell.alt)]
    st_ = cell.opeid.fillna("NONE").str.split(":").str[0].where(cell.opeid.fillna("").str.contains(":"), "PSEO")
    st_[cell.opeid.isna()] = "UNMATCHED"
    say(f"  organisations: {cell.organizationId.nunique()}; cells by match status: {st_.value_counts().to_dict()}")
    say(f"  ambiguous (several PSEO OPEIDs): {sorted(set(cell[cell.opeid.fillna('').str.startswith('AMBIG')].name))}")
    say(f"  unmatched organisations in PSEO states: "
        f"{sorted(set(cell[cell.opeid.isna() & cell.state.isin(pseo_states)].name))}")
    pc = cell[cell.opeid.notna() & ~cell.opeid.str.contains(":", na=False)]
    # first-time = earliest accreditation over every ABET organisation record mapped to the same institution x CIP-4
    pc = pc.groupby(["opeid", "cip"]).agg(name=("name", "first"), state=("state", "first"),
                                           first_year=("first_year", "min"), progs=("progs", "; ".join),
                                           n_orgs=("organizationId", "nunique")).reset_index()
    all_ev = cell[cell.first_year.between(2002, 2016)]
    say(f"first-time accreditations dated 2002-2016, all US organisations: {len(all_ev)} org x CIP-4 cells at "
        f"{all_ev.organizationId.nunique()} organisations; by year {dict(sorted(Counter(all_ev.first_year.astype(int)).items()))}")
    ev = pc[pc.first_year.between(2002, 2016)].copy()
    say(f"  at PSEO bachelor's institutions (after merging org records per institution x CIP-4): {len(ev)} cells at "
        f"{ev.opeid.nunique()} institutions")
    rows = []
    for r in ev.itertuples():
        e = int(r.first_year) + 1           # first graduating class covered: Oct 1 Y start -> spring Y+1 graduates
        u1 = usable_cells(av, r.opeid, e, "4", cips=[r.cip], h="y1")
        u5 = usable_cells(av, r.opeid, e, "4", cips=[r.cip], h="y5")
        us = usable_cells(av, r.opeid, e, "4", cips=[r.cip], h="y1", strict=True)
        any_rel = av[(av.institution == r.opeid) & (av.cip_level == "4") & (av.cip == r.cip) & av.rel_y1]
        rows.append(dict(opeid=r.opeid, name=r.name, state=r.state, cip=r.cip, first_year=int(r.first_year), e=e,
                         usable_y1=len(u1) > 0, usable_y5=len(u5) > 0, usable_strict=len(us) > 0,
                         any_release=len(any_rel) > 0,
                         any_pre_release=bool((any_rel.c + 2 <= e - 1).any()) if len(any_rel) else False,
                         npre=u1[u1.side == "pre"].c.nunique() if len(u1) else np.nan,
                         npost=u1[u1.side == "post"].c.nunique() if len(u1) else np.nan,
                         grads_med=float(u1.n_y1.median()) if len(u1) else np.nan, progs=r.progs))
    t = pd.DataFrame(rows)
    say(f"\n  PSEO cells with any released y1 window: {int(t.any_release.sum())}; with a released window wholly "
        f"before the first covered class: {int(t.any_pre_release.sum())}")
    u = t[t.usable_y1]
    say(f"USABLE (released y1 earnings in the matching CIP-4 before and after): {len(u)} cells at "
        f"{u.opeid.nunique()} institutions; y5: {int(t.usable_y5.sum())}; strict timing: {int(t.usable_strict.sum())}")
    if len(u):
        say(f"  by first-accreditation year: {dict(sorted(Counter(u.first_year).items()))}; with >=2 released pre "
            f"windows (pre-trend check possible): {int((u.npre >= 2).sum())}")
        say(f"  by CIP-4: {dict(Counter(u.cip).most_common())}; usable excluding IT/IS cells 11.01 and 11.04 (broader "
            f"than the accredited programme): {int((~u.cip.isin(['1101', '1104'])).sum())} cells at "
            f"{u[~u.cip.isin(['1101', '1104'])].opeid.nunique()} institutions")
        say(u[["first_year", "state", "opeid", "name", "cip", "npre", "npost", "grads_med", "progs"]]
            .sort_values(["first_year", "name"]).to_string(index=False))
    res = {}
    if len(u):
        res = power_block("B1 ABET", noise_tech, u.e.tolist(), u.grads_med.tolist(), n_inst=u.opeid.nunique(),
                          n_clusters=u.groupby(["opeid", "e"]).ngroups, npre=u.npre.mean(), npost=u.npost.mean(),
                          level_note="y1 log p50, CIP-4 cells in CIP 11/14/15", unit="cell")
    return t, ev, res


# ----------------------------------------------------------------------------------------------------
# (B2) AACSB first-time business accreditation (AACSB "newly accredited" pages, Internet Archive captures)
# ----------------------------------------------------------------------------------------------------
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
US_STATES = {v: k for k, v in STATE.items()}


def page_lines(path: Path) -> list[str]:
    raw = path.read_bytes()
    t = raw.decode("utf-8", errors="replace")
    if t.count("\ufffd") > 5:
        t = raw.decode("latin-1")
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>|</tr>|</div>|<li[^>]*>|</td>|<p[^>]*>|<h\d[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return [ln for ln in (re.sub(r"\s+", " ", x).strip() for x in t.split("\n")) if ln]


def parse_location(entry: str) -> tuple[str, str | None, bool | None]:
    """'Name (US-IL)' / '(U.S.- Texas)' / '(Texas - USA)' / '(United States - Pennsylvania)' / '(USA)' /
    'Name - New York, USA' / '(Country)' -> (name, state, is_us)"""
    e = re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", entry.strip()))
    mm = re.match(r"^(.*?)\s+-\s+([A-Za-z .]+),\s*USA$", e)
    if mm and mm.group(2).strip() in STATE:
        return mm.group(1).strip(), STATE[mm.group(2).strip()], True
    mm = re.match(r"^(.*?)\s+-\s+[^()]+$", e)
    if mm and re.search(r",\s*(?!USA)[A-Z][a-z]+", e.split(" - ")[-1]):
        return mm.group(1).strip(), None, False                       # 'Name - City, Country'
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*\)?\s*$", e)
    if not m:
        return e, None, None
    name, loc = m.group(1).strip(), m.group(2).strip()
    mm = re.match(r"(?i)^US-\s*([A-Z]{2})$", loc)
    if mm:
        return name, mm.group(1).upper(), True
    mm = re.match(r"(?i)^U\.?S\.?\s*-\s*(.+)$", loc) or re.match(r"(?i)^(.+?)\s*-\s*USA$", loc) \
        or re.match(r"(?i)^United States\s*-\s*(.+)$", loc)
    if mm:
        return name, STATE.get(mm.group(1).strip().rstrip(")").strip()), True
    if re.match(r"(?i)^(United States|USA|U\.S\.A?\.?)$", loc):
        return name, None, True
    if loc in STATE:
        return name, STATE[loc], True
    if re.search(r"(?i)\b(university|college|school|institute|ipade|campus)\b|/", loc) or len(loc) <= 6:
        return e, None, None                                             # parenthetical is part of the name
    return name, None, False                                             # another country


SECTION_BUS_INITIAL = re.compile(r"(?i)(initial business accreditation|newly accredited institutions\s*-\s*business|"
                                 r"achieving initial\s*accreditation|^business accreditation ratified by the board)")
SECTION_OTHER = re.compile(r"(?i)(accounting|reaffirm|maintenance|extension|continuous improvement|"
                           r"accredited institutions$|global listing|membership \||search schools|accreditation standards|"
                           r"^accreditation$|eligibility|staff contacts|copyright|newly accredited institutions$|"
                           r"print email|follow us|^about$)")
SKIP = re.compile(r"(?i)^(welcome|c ?ongratulations|undergraduate|master|doctoral|ratified|as of|newly accredited|"
                  r"business accreditation ratified)")


def parse_aacsb_page(path: Path) -> list[dict]:
    ts = re.search(r"_(\d{14})\.html$", path.name).group(1)
    cap_year = int(ts[:4])
    out, mode, lo_year, exact = [], None, None, False
    for ln in page_lines(path):
        dm = re.search(rf"(?i)ratified by the board\W+({MONTHS})\s*,?\s*(\d{{4}})", ln)
        sm = re.search(rf"(?i)(?:as of|since|in)\s+({MONTHS})\s*,?\s*(?:\d{{1,2}},\s*)?(\d{{4}})", ln)
        if dm:
            lo_year, exact = int(dm.group(2)), True
        elif sm:
            lo_year, exact = int(sm.group(2)), "since" not in ln.lower() and "as of" not in ln.lower()
        if SECTION_BUS_INITIAL.search(ln):
            mode = "bus"
            continue
        if SECTION_OTHER.search(ln) and not re.match(r"(?i)^ratified by the board", ln):
            mode = None
            continue
        if mode != "bus" or SKIP.match(ln) or len(ln) < 4 or len(ln) > 140:
            continue
        name, st, is_us = parse_location(ln)
        out.append(dict(file=path.name, cap_year=cap_year, lo_year=lo_year if lo_year else cap_year,
                        exact=bool(exact), raw=ln, name=name, state=st, is_us=is_us))
    return out


AACSB_ALIAS = {   # (AACSB entry name, stated state or '') -> (IPEDS name, state); identity from official names
    ("Bloomsburg University", ""): ("Bloomsburg University of Pennsylvania", "PA"),
    ("Kutztown University", ""): ("Kutztown University of Pennsylvania", "PA"),
    ("West Chester University", ""): ("West Chester University of Pennsylvania", "PA"),
    ("William Paterson University", ""): ("William Paterson University of New Jersey", "NJ"),
    ("The Pennsylvania State University Great Valley", "PA"): ("Pennsylvania State University-Penn State Great Valley", "PA"),
    ("The Pennsylvania State University at Erie", ""): ("Pennsylvania State University-Penn State Erie-Behrend College", "PA"),
    ("Mercer University-Macon and Atlanta Campuses", ""): ("Mercer University", "GA"),
    ("University of St. Thomas–Houston", ""): ("University of St Thomas", "TX"),
    ("U.S. Coast Guard Academy", ""): ("United States Coast Guard Academy", "CT"),
    ("Johns Hopkins Carey Business School", "MD"): ("Johns Hopkins University", "MD"),
}


AACSB_CONFIRM = set()   # name-only entries whose same name exists in several states, confirmed by hand


def design_b_aacsb(ni: "NameIndex", av, noise_bus):
    head("(B2) AACSB FIRST-TIME BUSINESS ACCREDITATION 2002-2016 (AACSB 'newly accredited' pages, Wayback captures)")
    files = sorted(AACSB_DIR.glob("*.html"))
    caps = Counter(int(re.search(r"_(\d{4})\d{10}\.html$", f.name).group(1)) for f in files)
    say(f"captures parsed: {len(files)}; by capture year: {dict(sorted(caps.items()))}")
    rows = [r for f in files for r in parse_aacsb_page(f)]
    d = pd.DataFrame(rows)
    labels = defaultdict(set)
    for f in files:
        for ln in page_lines(f):
            for mo, yr in re.findall(rf"(?i)(?:ratified by the board\W+|as of |since |in )({MONTHS})\s*,?\s*(?:\d{{1,2}},\s*)?(\d{{4}})", ln):
                labels[f.name[-19:-13]].add(f"{mo[:3]}{yr}")
    say("round labels seen, by capture month (YYYYMM: labels) -- gaps between captures can hide a round:")
    say("  " + "; ".join(f"{k}:{','.join(sorted(v, key=lambda z: (z[3:], z[:3])))}" for k, v in sorted(labels.items())))
    say(f"initial-business entries read (with repeats across captures): {len(d)}; distinct entry strings: {d.raw.nunique()}")
    # resolve to PSEO OPEIDs: exact normalised name + state; if no state, unique PSEO match across states
    pseo_states = sorted({st for (_, st) in ni.idx.keys()})
    res = []
    for r in d.drop_duplicates("raw").itertuples():
        nm = r.name
        if r.is_us is False:
            res.append((r.raw, None, "nonUS"))
            continue
        st0 = r.state if isinstance(r.state, str) else ""
        al = AACSB_ALIAS.get((nm, st0))
        if al:
            op = ni.resolve([al[0]], al[1])
        elif st0:
            op = ni.resolve([nm], st0)
        else:
            hits = {ni.resolve([nm], st) for st in pseo_states}
            hits = {h for h in hits if h}
            ps = {h for h in hits if ":" not in h}
            op = ps.pop() if len(ps) == 1 else (sorted(hits)[0] if hits and not ps else ("AMBIG" if ps else None))
        res.append((r.raw, op, "matched" if op and ":" not in op and op != "AMBIG" else ("nonpseo" if op else "unmatched")))
    m = pd.DataFrame(res, columns=["raw", "opeid", "status"])
    # name-only matches: how many IPEDS states carry the same normalised name (any institution, 1999-2019)?
    name_states = defaultdict(set)
    for (k, st_) in ni.idx.keys():
        name_states[k].add(st_)
    dd = d.drop_duplicates("raw").set_index("raw")
    m["no_state"] = [not isinstance(dd.loc[r, "state"], str) for r in m.raw]
    m["n_states"] = [len(name_states.get(key(dd.loc[r, "name"]), ())) for r in m.raw]
    m["aliased"] = [(dd.loc[r, "name"], dd.loc[r, "state"] if isinstance(dd.loc[r, "state"], str) else "") in AACSB_ALIAS
                    for r in m.raw]
    amb = m[(m.status == "matched") & m.no_state & ~m.aliased & (m.n_states > 1)]
    say(f"matched entries without a stated state: {int(((m.status == 'matched') & m.no_state).sum())}; of these, the "
        f"same normalised name exists in IPEDS in more than one state (dropped unless hand-confirmed in "
        f"AACSB_CONFIRM): {len(amb)} {sorted(amb.raw)}")
    say(f"  name-only matches (no state on the AACSB page), for audit: "
        f"{sorted(m[(m.status == 'matched') & m.no_state & ~m.aliased].raw)}")
    drop = set(amb.raw) - AACSB_CONFIRM
    m.loc[m.raw.isin(drop), "status"] = "ambiguous_name"
    d = d.merge(m[["raw", "opeid", "status"]], on="raw", how="left")
    first = d.groupby("raw").agg(name=("name", "first"), state=("state", "first"), is_us=("is_us", "first"),
                                 opeid=("opeid", "first"), status=("status", "first"),
                                 cap_year=("cap_year", "min"), lo_year=("lo_year", "min"), exact=("exact", "max")).reset_index()
    say(f"distinct entries by match status: {first.status.value_counts().to_dict()}")
    looks = first.name.str.contains(r"(?i)universit|college|institute|school|academy", regex=True)
    us_un = first[(first.status == "unmatched") & (first.is_us != False) & looks]
    say(f"  US-or-unknown institution-like entries not matched to any IPEDS name: {len(us_un)} "
        f"(stated US: {int((us_un.is_us == True).sum())}) -> audit list: {sorted(us_un.raw)}")
    ev = first[first.status == "matched"].copy()
    ev["e_lo"] = ev[["lo_year", "cap_year"]].min(axis=1).astype(int)
    ev["e_hi"] = ev.cap_year.astype(int)
    ev.loc[ev.exact, "e_hi"] = ev.loc[ev.exact, "e_lo"]
    ev = ev.sort_values("e_lo").groupby("opeid").first().reset_index()     # one first-time event per institution
    ev = ev[ev.e_lo.between(2002, 2016)]
    say(f"first-time business accreditations 2002-2016 at PSEO bachelor's institutions: {len(ev)}; "
        f"exact-dated {int(ev.exact.sum())}, interval-dated {int((~ev.exact).sum())}; "
        f"by year {dict(sorted(Counter(ev.e_lo).items()))}")
    rows = []
    for r in ev.itertuples():
        e_lo, e_hi = int(r.e_lo), int(r.e_hi)
        x2 = av[(av.institution == r.opeid) & (av.cip_level == "2") & (av.cip == "52") & av.rel_y1]
        pre = x2[x2.c + 2 <= e_lo - 1]
        post = x2[x2.c >= e_hi]
        x4 = av[(av.institution == r.opeid) & (av.cip_level == "4") & av.cip.str.startswith("52") & av.rel_y1]
        g4 = x4.groupby("cip").c.agg(lambda c: ((c + 2 <= e_lo - 1).any()) and ((c >= e_hi).any()))
        x2s = x2[(x2.c + 2 <= e_lo - 2) | (x2.c >= e_hi + 1)]
        rows.append(dict(opeid=r.opeid, name=r.name, state=r.state, e_lo=e_lo, e_hi=e_hi, exact=r.exact,
                         usable2=len(pre) > 0 and len(post) > 0, cells4=int(g4.sum()),
                         strict2=bool((x2s.c + 2 <= e_lo - 2).any() and (x2s.c >= e_hi + 1).any()),
                         y5=bool(len(av[(av.institution == r.opeid) & (av.cip_level == "2") & (av.cip == "52") & av.rel_y5
                                        & (av.c + 2 <= e_lo - 1)]) and
                                 len(av[(av.institution == r.opeid) & (av.cip_level == "2") & (av.cip == "52") & av.rel_y5
                                        & (av.c >= e_hi)])),
                         npre=pre.c.nunique(), npost=post.c.nunique(), grads=float(x2.n_y1.median()) if len(x2) else np.nan))
    t = pd.DataFrame(rows)
    u = t[t.usable2] if len(t) else t
    say(f"USABLE (business CIP-2 52 with released y1 earnings in a window before and one after): {len(u)} institutions; "
        f"CIP-4 52.xx cells usable: {int(t.cells4.sum()) if len(t) else 0}; y5: {int(t.y5.sum()) if len(t) else 0}; "
        f"strict timing: {int(t.strict2.sum()) if len(t) else 0}")
    if len(t):
        say(f"  usable with >=2 released pre windows (pre-trend check possible): {int((u.npre >= 2).sum())}")
        say(t.sort_values(["e_lo", "name"]).to_string(index=False))
    out = {}
    if len(u):
        out = power_block("B2 AACSB", noise_bus, u.e_hi.tolist(), u.grads.tolist(), n_inst=len(u),
                          n_clusters=len(u), npre=u.npre.mean(), npost=u.npost.mean(),
                          level_note="y1 log p50, business CIP-2 52 cells", unit="cell")
    return t, first, out


# ----------------------------------------------------------------------------------------------------
# (C) Nobel prizes x IPEDS bachelor's completions
# ----------------------------------------------------------------------------------------------------
NOBEL_CAT = {"Physics": "phy", "Chemistry": "che", "Physiology or Medicine": "med", "Economic Sciences": "eco"}
FIELD_CIP = {"phy": "4008", "che": "4005", "eco": "4506", "med": "26"}     # med -> all biology (CIP 26), 2-digit
# affiliation (name, city) at award time -> IPEDS institution name (state); None = not a degree-granting
# institution (lab, hospital, institute, firm). "med" marks medical-school affiliations mapped to the parent.
NOBEL_AFF = {
    ("St. Jude Children's Research Hospital", "Memphis, TN"): None,
    ("Argonne National Laboratory", "Argonne, IL"): None,
    ("Associated Universities Inc.", "Washington, D.C."): None,
    ("Bell Laboratories", "Holmdel, NJ"): None, ("Bell Laboratories", "Murray Hill, NJ"): None,
    ("Federal Reserve Bank of Minneapolis", "Minneapolis, MN"): None,
    ("Fred Hutchinson Cancer Research Center", "Seattle, WA"): None,
    ("Gladstone Institutes", "San Francisco, CA"): None,
    ("Howard Hughes Medical Institute", ""): None, ("Howard Hughes Medical Institute", "Durham, NC"): None,
    ("Janelia Research Campus, Howard Hughes Medical Institute", "Ashburn, VA"): None,
    ("Institute for Advanced Study", "Princeton, NJ"): None,
    ("Lawrence Berkeley National Laboratory", "Berkeley, CA"): None,
    ("Long Term Capital Management", "Greenwich, CT"): None,
    ("Marine Biological Laboratory (MBL)", "Woods Hole, MA"): None,
    ("Massachusetts General Hospital", "Boston, MA"): None,
    ("NASA Goddard Space Flight Center", "Greenbelt, MD"): None,
    ("National Institute of Standards and Technology", "Boulder, CO"): None,
    ("National Institute of Standards and Technology", "Gaithersburg, MD"): None,
    ("Parker Institute for Cancer Immunotherapy", "San Francisco, CA"): None,
    ("Space Telescope Science Institute", "Baltimore, MD"): None,
    ("Texas Instruments", "Dallas, TX"): None,
    ("The Molecular Sciences Institute", "Berkeley, CA"): None,
    ("Arizona State University", "Tempe, AZ"): ("Arizona State University-Tempe", "AZ"),
    ("Boston University Medical School", "Massachusetts, MA"): ("Boston University", "MA", "med"),
    ("Brandeis University", "Waltham, MA"): ("Brandeis University", "MA"),
    ("Brown University", "Providence, RI"): ("Brown University", "RI"),
    ("California Institute of Technology (Caltech)", "Pasadena, CA"): ("California Institute of Technology", "CA"),
    ("Carnegie Mellon University", "Pittsburgh, PA"): ("Carnegie Mellon University", "PA"),
    ("Columbia University", "New York, NY"): ("Columbia University in the City of New York", "NY"),
    ("Cornell University", "Ithaca, NY"): ("Cornell University", "NY"),
    ("Drew University", "Madison, NJ"): ("Drew University", "NJ"),
    ("Duke University Medical Center", "Durham, NC"): ("Duke University", "NC", "med"),
    ("Duke University School of Medicine", "Durham, NC"): ("Duke University", "NC", "med"),
    ("Enrico Fermi Institute, University of Chicago", "Chicago, IL"): ("University of Chicago", "IL"),
    ("George Mason University", "Fairfax, VA"): ("George Mason University", "VA"),
    ("Harvard Business School", "Boston, MA"): ("Harvard University", "MA"),
    ("Harvard Medical School", "Boston, MA"): ("Harvard University", "MA", "med"),
    ("Harvard University", "Cambridge, MA"): ("Harvard University", "MA"),
    ("Indiana University", "Bloomington, IN"): ("Indiana University-Bloomington", "IN"),
    ("Johns Hopkins University School of Medicine", "Baltimore, MD"): ("Johns Hopkins University", "MD", "med"),
    ("Johns Hopkins University", "Baltimore, MD"): ("Johns Hopkins University", "MD"),
    ("Massachusetts Institute of Technology (MIT)", "Cambridge, MA"): ("Massachusetts Institute of Technology", "MA"),
    ("NYU Stern School of Business", "New York, NY"): ("New York University", "NY"),
    ("New York University", "New York, NY"): ("New York University", "NY"),
    ("Northwestern University", "Evanston, IL"): ("Northwestern University", "IL"),
    ("Princeton University", "Princeton, NJ"): ("Princeton University", "NJ"),
    ("Purdue University", "West Lafayette, IN"): ("Purdue University-Main Campus", "IN"),
    ("Rice University", "Houston, TX"): ("Rice University", "TX"),
    ("Rockefeller University", "New York, NY"): ("The Rockefeller University", "NY"),
    ("SUNY Health Science Center", "Brooklyn, NY"): ("SUNY Downstate Medical Center", "NY", "med"),
    ("Stanford University School of Medicine", "Stanford, CA"): ("Stanford University", "CA", "med"),
    ("Stanford University", "Stanford, CA"): ("Stanford University", "CA"),
    ("The Scripps Research Institute", "La Jolla, CA"): ("The Scripps Research Institute", "CA"),
    ("University of California School of Medicine", "Los Angeles, CA"): ("University of California-Los Angeles", "CA", "med"),
    ("University of California School of Medicine", "San Francisco, CA"): ("University of California-San Francisco", "CA", "med"),
    ("University of California", "Berkeley, CA"): ("University of California-Berkeley", "CA"),
    ("University of California", "Irvine, CA"): ("University of California-Irvine", "CA"),
    ("University of California", "Los Angeles, CA"): ("University of California-Los Angeles", "CA"),
    ("University of California", "San Diego, CA"): ("University of California-San Diego", "CA"),
    ("University of California", "San Francisco, CA"): ("University of California-San Francisco", "CA"),
    ("University of California", "Santa Barbara, CA"): ("University of California-Santa Barbara", "CA"),
    ("University of California, Kavli Institute for Theoretical Physics", "Santa Barbara, CA"): ("University of California-Santa Barbara", "CA"),
    ("University of Chicago", "Chicago, IL"): ("University of Chicago", "IL"),
    ("University of Colorado", "Boulder, CO"): ("University of Colorado Boulder", "CO"),
    ("University of Colorado, JILA", "Boulder, CO"): ("University of Colorado Boulder", "CO"),
    ("University of Delaware", ""): ("University of Delaware", "DE"),
    ("University of Illinois", "Urbana, IL"): ("University of Illinois at Urbana-Champaign", "IL"),
    ("University of Maine", "Maine, ME"): ("University of Maine", "ME"),
    ("University of Maryland, Department of Economics and School of Public Policy", "College Park, MD"): ("University of Maryland-College Park", "MD"),
    ("University of Massachusetts Medical School", "Worcester, MA"): ("University of Massachusetts Medical School Worcester", "MA", "med"),
    ("University of Michigan", "Ann Arbor, MI"): ("University of Michigan-Ann Arbor", "MI"),
    ("University of Minnesota", "Minneapolis, MN"): ("University of Minnesota-Twin Cities", "MN"),
    ("University of Missouri", "Columbia"): ("University of Missouri-Columbia", "MO"),
    ("University of North Carolina", "Chapel Hill, NC"): ("University of North Carolina at Chapel Hill", "NC"),
    ("University of Pennsylvania", "Philadelphia, PA"): ("University of Pennsylvania", "PA"),
    ("University of Southern California", "Los Angeles, CA"): ("University of Southern California", "CA"),
    ("University of Texas MD Anderson Cancer Center", "Houston, TX"): ("The University of Texas MD Anderson Cancer Center", "TX", "med"),
    ("University of Texas Medical School at Houston", "Houston, TX"): ("The University of Texas Health Science Center at Houston", "TX", "med"),
    ("University of Texas Southwestern Medical Center at Dallas", "Dallas, TX"): ("University of Texas Southwestern Medical Center", "TX", "med"),
    ("University of Utah", "Salt Lake City, UT"): ("University of Utah", "UT"),
    ("University of Washington", "Seattle, WA"): ("University of Washington-Seattle Campus", "WA"),
    ("Virginia Commonwealth University", "Richmond, VA"): ("Virginia Commonwealth University", "VA"),
    ("Yale University", "New Haven, CT"): ("Yale University", "CT"),
}

C_FILES = {1990: "C8990CIP", 1992: "C1992_CIP", 1993: "C1993_CIP", 1994: "C1994_CIP", 1995: "C9495_A",
           1996: "C9596_A", 1997: "C9697_A", 1998: "C9798_A", 1999: "C9899_A",
           **{y: f"C{y}_A" for y in range(2000, 2023)}}


def load_completions() -> tuple[pd.DataFrame, pd.Series]:
    """bachelor's (AWLEVEL 5), first major, by UNITID x field for the four Nobel fields, 1990-2023 (no 1991 file).
    Total = CTOTALT, else CRACE24, else CTOTALM+CTOTALW, else CRACE15+CRACE16 (grand totals per the dictionaries)."""
    want = ["unitid", "cipcode", "awlevel", "majornum", "ctotalt", "crace24", "ctotalm", "ctotalw", "crace15", "crace16"]
    out, nat = [], {}
    paths = {y: C_DIR / f"{f}.zip" for y, f in C_FILES.items()}
    paths[2023] = RAW / "ipeds" / "C2023_A.zip"
    for y, pth in sorted(paths.items()):
        d = _read_zip_csv(pth, want)
        d = d[pd.to_numeric(d.awlevel, errors="coerce") == 5]
        if "majornum" in d:
            d = d[d.majornum.astype(str).str.strip() == "1"]
        if "ctotalt" in d:
            tot = pd.to_numeric(d.ctotalt, errors="coerce")
        elif "crace24" in d:
            tot = pd.to_numeric(d.crace24, errors="coerce")
        elif "ctotalm" in d:
            tot = pd.to_numeric(d.ctotalm, errors="coerce") + pd.to_numeric(d.ctotalw, errors="coerce")
        else:
            tot = pd.to_numeric(d.crace15, errors="coerce") + pd.to_numeric(d.crace16, errors="coerce")
        d = d.assign(n=tot.fillna(0), cip=d.cipcode.astype(str).str.replace(r"[^0-9]", "", regex=True))
        nat[y] = float(d.n[~d.cip.str.startswith("99")].sum())         # 99 / 99.0000 = grand-total rows
        rows = []
        for f, c in FIELD_CIP.items():
            x = d[d.cip.str.startswith(c)].groupby("unitid").n.sum()
            rows.append(pd.DataFrame({"unitid": x.index.str.strip(), "field": f, "year": y, "n": x.values}))
        out.append(pd.concat(rows))
    comp = pd.concat(out, ignore_index=True)
    return comp, pd.Series(nat).sort_index()


def nobel_events(ni_hd: pd.DataFrame) -> pd.DataFrame:
    L = json.loads(NOBEL.read_text())["laureates"]
    rows = []
    for l in L:
        for pz in l.get("nobelPrizes", []):
            y, cat = int(pz["awardYear"]), pz["category"]["en"]
            if cat not in NOBEL_CAT or not 1995 <= y <= 2018:
                continue
            for a in pz.get("affiliations", []) or []:
                rows.append(dict(year=y, field=NOBEL_CAT[cat], laureate=(l.get("knownName") or {}).get("en"),
                                 aff=(a.get("name") or {}).get("en", ""), city=(a.get("city") or {}).get("en", "") or "",
                                 country=(a.get("country") or {}).get("en", "")))
    return pd.DataFrame(rows)


def design_c(hd):
    head("(C) NOBEL PRIZES 1995-2018 x IPEDS BACHELOR'S COMPLETIONS (annual)")
    a = nobel_events(hd)
    say(f"prize-affiliation rows 1995-2018 in physics/chemistry/medicine/economics: {len(a)} "
        f"({a.laureate.nunique()} laureates); US affiliations: {int((a.country == 'USA').sum())}")
    us = a[a.country == "USA"].copy()
    miss = sorted({(r.aff, r.city) for r in us.itertuples() if (r.aff, r.city) not in NOBEL_AFF})
    if miss:
        say(f"!! US affiliations missing from the hand table: {miss}")
    us["tgt"] = [NOBEL_AFF.get((r.aff, r.city)) for r in us.itertuples()]
    dropped = us[us.tgt.isna()]
    say(f"  dropped as non-degree-granting (labs, hospitals, institutes, firms): {len(dropped)} rows: "
        f"{dict(Counter(dropped.aff).most_common())}")
    us = us[us.tgt.notna()].copy()
    idx = defaultdict(set)
    for nm, st, u in zip(hd.instnm, hd.stabbr, hd.unitid):
        idx[(key(nm), st)].add(u)
    us["unitid"] = [sorted(idx.get((key(m[0]), m[1]), {"?"}))[-1] if len(idx.get((key(m[0]), m[1]), ())) <= 1
                    else "AMBIG" for m in us.tgt]
    us["med_school"] = [len(m) > 2 and m[2] == "med" for m in us.tgt]
    bad = us[us.unitid.isin(["?", "AMBIG"])]
    if len(bad):
        say(f"!! unresolved IPEDS names: {sorted(set(m[0] for m in bad.tgt))}")
    say(f"  mapped to a UNITID: {int((~us.unitid.isin(['?', 'AMBIG'])).sum())} rows "
        f"(medical-school affiliations mapped to the parent: {int(us.med_school.sum())})")
    ev = us[~us.unitid.isin(["?", "AMBIG"])].groupby(["unitid", "field", "year"]).agg(
        inst=("tgt", lambda s: s.iloc[0][0]), laureates=("laureate", lambda s: "; ".join(sorted(set(s)))),
        med_only=("med_school", "all")).reset_index()
    say(f"distinct institution x field x year events: {len(ev)} at {ev.unitid.nunique()} institutions; "
        f"by field {ev.field.value_counts().to_dict()}")
    cells = ev.groupby(["unitid", "field"]).size()
    say(f"distinct institution x field cells: {len(cells)}; cells with >1 prize 1995-2018: {int((cells > 1).sum())} "
        f"(max {int(cells.max())})")

    comp, nat = load_completions()
    say("\nnational bachelor's completions (first major, all fields), smoothness check (thousands):")
    say("  " + ", ".join(f"{y}:{v/1e3:.0f}" for y, v in nat.items()))
    yrs = sorted(comp.year.unique())
    say(f"completion years available: {yrs[0]}-{yrs[-1]}, missing: {[y for y in range(yrs[0], yrs[-1] + 1) if y not in yrs]}")
    # FIREWALL: event side reads only whether completions are positive in each year
    pos = comp[comp.n > 0].groupby(["unitid", "field"]).year.agg(lambda s: set(s)).to_dict()
    rows = []
    for r in ev.itertuples():
        have = pos.get((r.unitid, r.field), set())
        pre, post = range(r.year - 4, r.year + 1), range(r.year + 1, r.year + 6)
        same = ev[(ev.unitid == r.unitid) & (ev.field == r.field) & (ev.year != r.year)].year
        rows.append(dict(unitid=r.unitid, inst=r.inst, field=r.field, year=r.year, laureates=r.laureates,
                         med_only=r.med_only,
                         strict=all(y in have for y in pre) and all(y in have for y in post),
                         relaxed=sum(y in have for y in pre) >= 4 and sum(y in have for y in post) >= 4,
                         clean_prior5=not ((same >= r.year - 5) & (same < r.year)).any(),
                         clean_window=not ((same >= r.year - 5) & (same <= r.year + 5)).any()))
    t = pd.DataFrame(rows)
    say(f"\nevents with bachelor's completions in the field in all of t-4..t and t+1..t+5 (strict): {int(t.strict.sum())}; "
        f">=4 of 5 years on each side (relaxed): {int(t.relaxed.sum())}")
    for lab, m in [("strict", t.strict), ("relaxed", t.relaxed)]:
        u = t[m]
        say(f"  {lab}: {len(u)} events, {u.groupby(['unitid', 'field']).ngroups} cells, {u.unitid.nunique()} institutions; "
            f"clean (no prize in the cell in the prior 5 years): {int(u.clean_prior5.sum())}; "
            f"clean over t-5..t+5: {int(u.clean_window.sum())}; excluding medical-school-only: "
            f"{int((u.clean_prior5 & ~u.med_only).sum())}")
        say(f"    by field (clean prior-5): {u[u.clean_prior5].field.value_counts().to_dict()}")
    say(t.sort_values(["field", "year"]).to_string(index=False))

    # ---- noise: all institution x field cells in the four fields (no event information) ----
    x = comp[comp.n > 0].copy()
    x["y"] = np.log(x.n)
    x["r"] = x.y - x.groupby(["field", "year"]).y.transform("mean")
    g = x.groupby(["unitid", "field"])
    dev = x.r - g.r.transform("mean")
    s2_within = float((dev ** 2).sum() / (g.r.count() - 1).clip(lower=0).sum())
    xs = x.sort_values(["unitid", "field", "year"])
    xs["dy"] = xs.groupby(["unitid", "field"]).y.diff()
    xs["prev_year"] = xs.groupby(["unitid", "field"]).year.shift()
    d1 = xs[(xs.year - xs.prev_year) == 1]
    d1r = d1.dy - d1.groupby(["field", "year"]).dy.transform("mean")
    say(f"\nNOISE (C), all institution x field cells with positive completions, four fields:")
    say(f"  literal: year-to-year variance of log completions (consecutive-year differences) = {d1.dy.var():.4f} "
        f"(SD {d1.dy.std():.4f}); net of field x year = {d1r.var():.4f} (SD {d1r.std():.4f}); {len(d1)} pairs")
    say(f"  within-cell residual variance after cell and field x year effects = {s2_within:.4f} (SD {np.sqrt(s2_within):.4f})")
    hd19 = _read_zip_csv(HD_DIR / "HD2019.zip", ["unitid", "c18basic"])
    r1 = set(hd19[hd19.c18basic.str.strip() == "15"].unitid.str.strip())
    say(f"  R1 (Carnegie 2018 basic = 15, doctoral very high research) institutions: {len(r1)}; "
        f"event institutions that are R1: {len(set(t.unitid) & r1)} of {t.unitid.nunique()}")
    piv = x.pivot_table(index=["unitid", "field"], columns="year", values="r")

    def placebo_var(sp: int, sub=None) -> tuple[float, int]:
        cols_pre = [y for y in range(sp - 4, sp + 1)]
        cols_post = [y for y in range(sp + 1, sp + 6)]
        if not all(c in piv.columns for c in cols_pre + cols_post):
            cols_pre = [c for c in cols_pre if c in piv.columns]
        q = piv[[c for c in cols_pre + cols_post if c in piv.columns]].dropna()
        if sub is not None:
            q = q[q.index.get_level_values(0).isin(sub)]
        con = q[[c for c in cols_post if c in q.columns]].mean(axis=1) - q[cols_pre].mean(axis=1)
        return float(con.var(ddof=1)), int(len(con))

    res = {}
    for lab, m in [("strict", t.strict), ("relaxed", t.relaxed)]:
        u = t[m & t.clean_prior5]
        if u.empty:
            continue
        va = [placebo_var(int(e)) for e in u.year]
        vr = [placebo_var(int(e), r1) for e in u.year]
        V_all, V_r1 = float(np.mean([v[0] for v in va])), float(np.mean([v[0] for v in vr]))
        n = len(u)
        res[lab] = dict(n=n, n_inst=u.unitid.nunique(), V_all=V_all, V_r1=V_r1, mde_all=mde(V_all, n),
                        mde_r1=mde(V_r1, n), mde_iid=Z * np.sqrt(s2_within * (1 / 5 + 1 / 5) / n),
                        mde_inst=mde(V_r1, u.unitid.nunique()))
        say(f"\nPOWER (C, {lab}, clean prior-5 events, N={n} at {u.unitid.nunique()} institutions):")
        say(f"  placebo 5-yr post minus 5-yr pre contrast of log completions at the events' years: all cells var {V_all:.4f} "
            f"(SD {np.sqrt(V_all):.4f}, ~{int(np.mean([v[1] for v in va]))} cells); R1 cells var {V_r1:.4f} "
            f"(SD {np.sqrt(V_r1):.4f}, ~{int(np.mean([v[1] for v in vr]))} cells)")
        say(f"  MDE with institutions as units (R1 noise, N={u.unitid.nunique()}) = {res[lab]['mde_inst']:.4f} log points   "
            f"<- headline (conservative); events as independent units {res[lab]['mde_r1']:.4f}; all-cell noise "
            f"{res[lab]['mde_all']:.4f}; iid formula {res[lab]['mde_iid']:.4f}")
    # scale: within-institution SD of field-adjusted department size, R1 institutions, 2000-2019 mean
    sz = x[x.year.between(2000, 2019) & x.unitid.isin(r1)].groupby(["unitid", "field"]).r.mean().reset_index()
    sz["dev"] = sz.r - sz.groupby("unitid").r.transform("mean")
    res["scale_dept_within_r1"] = float(sz[sz.groupby("unitid").r.transform("count") >= 3].dev.std())
    say(f"  scale: within-institution SD of field-adjusted log department size, R1 (2000-19 means): "
        f"{res['scale_dept_within_r1']:.3f}")
    return t, res


def main():
    only = {a.lstrip("-") for a in sys.argv[1:]} & {"a", "b", "b2", "c"}
    run = only or {"a", "b", "b2", "c"}
    p = load_pseo()
    av = availability(p)
    hd = load_hd()
    out = {}
    if run & {"a", "b", "b2"}:
        say(f"PSEO V4.14.1 bachelor's, institution level, 3-year windows {COHORTS}: {len(p)} rows "
            f"({(p.cip_level == '4').sum()} CIP-4, {(p.cip_level == '2').sum()} CIP-2); released y1 "
            f"{int(p.rel_y1.sum())}, y5 {int(p.rel_y5.sum())}")
    if "a" in run:
        out["A"] = design_a(hd, av, pseo_noise(p, "y1"), None)[1]
    ins = pd.read_csv(PSEO_I, dtype=str, encoding="utf-8-sig")
    ni = NameIndex(hd, set(av.institution))
    if "b" in run:
        p_tech = p[p.cip.str[:2].isin(["11", "14", "15"])]
        out["B1"] = design_b_abet(load_abet(), ni, av, set(ins.institution_state), pseo_noise(p_tech, "y1"))[2]
    if "b2" in run:
        out["B2"] = design_b_aacsb(ni, av, pseo_noise(p[p.cip == "52"], "y1", cip_level="2"))[2]
    if "c" in run:
        out["C"] = design_c(hd)[1]
    head("SUMMARY")
    if "A" in out and out["A"]:
        a = out["A"]
        say(f"(A) name shocks: {a['n_units']} merger-free usable institutions ({a['n_cells']} CIP-4 cells, "
            f"{a['n_clusters']} state x year clusters); MDE {a['headline']:.3f} log points "
            f"(conservative {a['mde_cluster']:.3f}); SD of institution effects {a['sd_inst']:.3f} -> ratio "
            f"{a['headline'] / a['sd_inst']:.2f}")
    if "B1" in out and "B2" in out and out["B1"] and out["B2"]:
        b1, b2 = out["B1"], out["B2"]
        n = b1["n_units"] + b2["n_units"]
        V = (b1["n_units"] * b1["V_size"] + b2["n_units"] * b2["V_size"]) / n
        sd_dept = pseo_scales(pseo_noise(p, "y1"))["sd_dept_within"]
        say(f"(B) credential shocks: ABET {b1['n_units']} cells (MDE {b1['headline']:.3f}), AACSB {b2['n_units']} "
            f"institutions (MDE {b2['headline']:.3f}); pooled N={n} cells ({b1['n_clusters'] + b2['n_clusters']} "
            f"institution x year clusters): MDE {mde(V, n):.3f} log points; within-institution "
            f"SD of department effects {sd_dept:.3f} -> ratio pooled {mde(V, n) / sd_dept:.2f}, ABET "
            f"{b1['headline'] / sd_dept:.2f}, AACSB {b2['headline'] / sd_dept:.2f}")
    if "C" in out and out["C"]:
        c = out["C"]
        for lab in ("strict", "relaxed"):
            if lab in c:
                say(f"(C) Nobel x completions, {lab}: {c[lab]['n']} clean events at {c[lab]['n_inst']} institutions; "
                    f"MDE {c[lab]['mde_inst']:.3f} log points with institutions as units (events as units "
                    f"{c[lab]['mde_r1']:.3f}; R1 noise); within-R1 SD of department size "
                    f"{c['scale_dept_within_r1']:.3f} (not used for the verdict)")


if __name__ == "__main__":
    main()
