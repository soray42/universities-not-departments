"""82 -- Nobel prizes and bachelor's completions: a stacked event study (design C of scripts/80).

QUESTION. Does a sudden rise in a department's academic reputation (a Nobel prize to a member of the department)
attract students into that field at that university? Outcome: IPEDS bachelor's completions in the field at the
institution (annual, 1990-2023, no 1991 file). Events and crosswalk are imported from scripts/80 (not edited).

PRE-SPECIFICATION (written verbatim, as given by the project owner, into this docstring and into NOBEL_RESULT.md on
2026-11-14, before any outcome data were read by this script; anything else is exploratory):

Units:
- Institution × field cells for physics, chemistry, physiology/medicine (mapped to the biology/biomedical CIPs scripts/80 used) and economics.
- Outcome: log bachelor's completions in the field at the institution, by year.

Treatment:
- The prize year t, announced in October.
- Primary effect window: years t+2 to t+5. A student who picks the major after the prize graduates about 2 to 4 years later.
- Event time runs from t−5 to t+5. Use clean events only: no prize in the same cell in the prior 5 years.

Estimator:
- Stacked event study, one stack per event.
- Controls: the same field at not-yet-treated and never-treated US institutions with completions in all years of the window, plus the institution's other fields (a triple difference) as a second specification.
- Fixed effects: stack × cell, and stack × year.
- Cluster by institution. Use a wild cluster bootstrap if there are fewer than 50 clusters.

Secondary outcomes:
- (a) the field's share of the institution's bachelor's completions;
- (b) completions at the bachelor's level of the most closely related field, as a spillover check.

Report:
- the average t+2..t+5 effect, the event-time path, the joint pre-trend test (t−5..t−1) and the MDE;
- prize-field breakdowns, descriptive only.

Verdict:
- "invalid (pre-trend)" if the pre-trend p < 0.10;
- otherwise "positive" if the CI is above 0, "negative" if it is below 0, "null" if the CI includes 0 and the MDE ≤ 0.10, and "underpowered" otherwise.

State plainly that completions measure quantity, not the quality of entrants, and that repeat winners cluster at a few elite universities.

END OF PRE-SPECIFICATION.

OPERATIONAL DEFINITIONS (fixed on 2026-11-14 after metadata checks only -- which CIP codes exist in each completions
file, no completion counts -- and before any outcome data were read; they settle choices that the pre-specification
leaves open; everything not covered by the pre-specification or by this block is exploratory):
O1 Events and crosswalk, imported from scripts/80 (not edited): s80.design_c(s80.load_hd()) gives the 134
   institution x field x year events (nobelprize.org affiliations at award time, 1995-2018, hand table NOBEL_AFF,
   medical schools mapped to the parent university) with the flags strict (positive completions in the field in
   every year t-4..t and t+1..t+5) and clean_prior5. The sample is the events with strict and clean_prior5
   (asserted: 88 events at 42 institutions). Fields and CIPs are s80.FIELD_CIP: physics 40.08, chemistry 40.05,
   economics 45.06, physiology/medicine -> all of biology (CIP 26, 2-digit). "Treated" below means a prize in this
   imported list (1995-2018); prizes before 1995 or after 2018 are not tracked in the primary analysis (see E1).
O2 Outcome data. Bachelor's (AWLEVEL 5), first-major completions by UNITID from the IPEDS C files of scripts/80
   (s80.load_completions for the four fields, reused unchanged; the same files and grand-total column rule for the
   other series, asserted equal on the four fields). Year y = academic year ending June y, so year t lies wholly
   before the October announcement of year t. There is no 1991 file. Institution total = sum over all CIP rows
   except the CIP 99 grand-total rows (as in the national totals of scripts/80); its agreement with the 99 rows is
   printed.
O3 Stacks. For event (i, f, t) the stack's years are those tau in t-5..t+5 that have a completions file and in which
   the treated cell has positive completions (event time e = tau - t). Controls (spec 1): cells (j, f), j != i, at
   institutions in the 50 states or DC (IPEDS HD state, latest of 1999-2019), with positive completions in f in
   every one of the stack's years and no prize in (j, f) in the imported list in any year <= t+5 (never treated, or
   first treated after t+5). Every stack is therefore balanced.
O4 Regression. OLS, unweighted, of y on event-time dummies D_e = 1[treated cell] x 1[tau - t = e],
   e in {-5..-1, 1..5}, reference e = 0, with stack x cell and stack x year fixed effects. Average t+2..t+5 effect
   theta = (b2 + b3 + b4 + b5) / 4. Pre-trend test: joint Wald test of b-5 = ... = b-1 = 0.
O5 Spec 2 (triple difference). The institution's other fields = all its other bachelor's first-major completions,
   pooled (rest = institution total - field). The triple difference with stack x cell, stack x institution x year
   and stack x (field or rest) x year effects equals the O4 regression on y = log(field) - log(rest) with
   stack x institution and stack x year effects, which is how it is run. Same stacks and cells as spec 1.
O6 Inference. Clusters = institutions (UNITID). The "fewer than 50 clusters" rule is applied to the number of
   treated institutions (42): with one treated cell per stack the information about theta comes from the treated
   clusters (MacKinnon and Webb 2017); total clusters are printed. Hence wild cluster restricted (WCR) bootstrap-t,
   Webb six-point weights, 9999 replicates for theta, its MDE and the pre-trend test, 1999 for each event-time
   coefficient. 95% CI = inversion of the WCR test (basis of the verdict). Pre-trend p = WCR bootstrap of the joint
   Wald statistic (CR1 variance) with b-5..b-1 restricted to 0. CR1 standard errors (factor G/(G-1) (N-1)/(N-K);
   cell effects nested in clusters) and CR1 CIs are printed alongside. MDE = (q + 0.842) x SE_CR1, q = 95% quantile
   of |t*| of the WCR bootstrap at theta = 0. Random numbers: numpy SeedSequence([82, crc32(tag)]).
O7 Verdict. Applied once: spec 1, primary outcome (log completions). Spec 2 is reported with the same statistics and
   the label the same rule would give, without a separate verdict. The MDE <= 0.10 benchmark is in log points and is
   used for log outcomes only.
O8 Secondary outcomes. (a) share = 100 x field completions / institution total (percentage points), same stacks and
   cells as spec 1; the 0.10 rule does not apply; reported with CI, pre-trend p and MDE. (b) Related field: the
   first candidate in the ordered list below that the treated institution offers (positive completions) in every
   year of the stack for at least half of the field's events in the 88-event sample (after the exclusions below);
   if none reaches half, the candidate with the most such events. Candidates (closeness judgment, fixed here):
   physics -> 40.02 astronomy and astrophysics, 14.12 engineering physics, 27 mathematics and statistics;
   chemistry -> 26.02 biochemistry, biophysics and molecular biology, 14.07 chemical engineering; medicine
   (biology) -> 40.05 chemistry, 14.05 biomedical engineering, 42 psychology; economics -> 52.06 business/managerial
   economics, 52.08 finance, 52 business (all). Stack years = the spec 1 stack years in which the candidate's CIP
   exists in the file (a code absent from a file counts as missing for everyone). Treated unit = (i, related field);
   controls = (j, related field), US as in O3, positive completions in every stack year, no prize in (j, f) through
   t+5. When the related CIP is (part of) another prize field's outcome (26.02 inside medicine's CIP 26; 40.05 =
   chemistry), the event is dropped if (i, that field) has a prize in t-5..t+5, and controls must also have no prize
   in (j, that field) through t+5. The verdict rule's label is printed for (b), without a separate verdict.
O9 Field breakdowns (descriptive only): the O4 regression on each field's stacks (controls as in O3), same
   statistics, no verdict.
O10 Self-check asserted at run time: the fast WCR algebra (cluster-level aggregates, no N x replicates arrays) is
   compared with brute-force dummy-variable regressions with explicit bootstrap samples on a small subsample (point
   estimate, CR1 SE, bootstrap t and Wald statistics agree to 1e-8).
E  Exploratory (pre-declared, no verdict). E1 extended prize screening: prizes 1990-1994 and 2019-2023 read from the
   same nobelprize.org file and mapped through the imported NOBEL_AFF table only (affiliations not in it are listed,
   not mapped); events with such a prize in the cell in t-5..t-1 and control cells with such a prize through t+5
   are dropped. E2 events clean over the whole window t-5..t+5 (imported clean_window). E3 controls restricted to
   R1 institutions (Carnegie 2018 basic = 15, as in scripts/80). E4 post-minus-pre contrast from the spec 1
   regression: mean(b2..b5) - mean(b-5..b-1, b0 = 0). E5 excluding medical-school-only events.

END OF OPERATIONAL DEFINITIONS.

REVISION 1 (2026-11-14; made after the results had been seen, once an independent re-computation had reproduced
the spec 1 estimate and its WCR interval; the pre-specification, O1-O10, the verdict and every pre-specified
estimate are unchanged):
R1.1 E1 also maps eight US prize-affiliation rows that the imported NOBEL_AFF table lacks (SUPP_AFF below). Each was
     checked against the affiliation string and city in the on-disk nobelprize.org file and against the IPEDS
     directory name. "City University of New York" (Markowitz, 1990) is mapped to Baruch College: Baruch's Zicklin
     School of Business states that he was Marvin Speiser Distinguished Professor of Finance and Economics there
     when he won the prize (zicklin.baruch.cuny.edu, "Nobel Winner Harry Markowitz, Former Zicklin Professor,
     Dies"). The E1 screen with the original table alone is still computed and printed.
R1.2 The RESULT file states the scope of the result: graduates in t+2..t+5 were mostly already enrolled when the
     prize was announced, so the window tests the major choices of enrolled students, not the response of new
     entrants.
R1.3 The RESULT file reports the MDE with degrees of freedom also reduced for the cell fixed effects, and notes that
     prizes before 1990 are not screened anywhere.
END OF REVISION 1.

Run: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I -B scripts/82_nobel_event_study.py
Memory: single process, BLAS capped at 3 threads; bootstrap on cluster-level aggregates in chunks; peak well under
1 GB.
"""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "3"                                   # memory/CPU cap; set before numpy is imported

import io
import sys
import json
import zlib
import hashlib
import contextlib
import importlib.util
import resource
from collections import Counter as Counter_
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2, t as tdist

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s80 = _load("s80", "80_causal_feasibility.py")     # events, crosswalk, completions loader (not edited)

SEED = 82
RUN_DATE = "2026-11-14"
B_MAIN = 9999            # WCR replicates: theta, MDE, pre-trend test
B_PATH = 1999            # WCR replicates: each event-time coefficient
CHUNK = 500              # bootstrap replicates per block
Z80 = 0.841621           # 80% power
BENCH = 0.10             # verdict benchmark for the MDE (log points)
PRE_ALPHA = 0.10
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
EVT = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]                 # event-time dummies; e = 0 is the reference
PRE = [-5, -4, -3, -2, -1]
POST = [2, 3, 4, 5]
FIELDS = ["phy", "che", "med", "eco"]
FNAME = {"phy": "physics", "che": "chemistry", "med": "physiology/medicine", "eco": "economics"}
FCIP = {"phy": "40.08", "che": "40.05", "med": "26 (all biology)", "eco": "45.06"}
RELATED = {   # O8: ordered candidates (closeness judgment fixed before outcomes)
    "phy": [("4002", "40.02 astronomy and astrophysics"), ("1412", "14.12 engineering physics"),
            ("27", "27 mathematics and statistics")],
    "che": [("2602", "26.02 biochemistry, biophysics and molecular biology"), ("1407", "14.07 chemical engineering")],
    "med": [("4005", "40.05 chemistry"), ("1405", "14.05 biomedical engineering"), ("42", "42 psychology")],
    "eco": [("5206", "52.06 business/managerial economics"), ("5208", "52.08 finance"), ("52", "52 business (all)")],
}
# revision 1 (R1.1, added after the results had been seen): E1 affiliations missing from the imported NOBEL_AFF table.
# key = (award year, field, affiliation string, city) exactly as in the nobelprize.org file -> (IPEDS name, state)
SUPP_AFF = {
    (1990, "eco", "City University of New York", "New York, NY"): ("CUNY Bernard M Baruch College", "NY"),
    (1993, "eco", "Washington University", "St. Louis, MO"): ("Washington University in St Louis", "MO"),
    (2022, "eco", "Washington University", "St. Louis, MO"): ("Washington University in St Louis", "MO"),
    (1993, "med", "Massachusetts Institute of Technology (MIT), Center for Cancer Research", "Cambridge, MA"):
        ("Massachusetts Institute of Technology", "MA"),
    (2019, "che", "University of Texas", "Austin, TX"): ("The University of Texas at Austin", "TX"),
    (2019, "che", "Binghamton University, State University of New York", "New York, NY"): ("SUNY at Binghamton", "NY"),
    (2023, "med", "Penn Institute for RNA Innovations, University of Pennsylvania", "Philadelphia, PA"):
        ("University of Pennsylvania", "PA"),
    (2023, "phy", "The Ohio State University", "Columbus, OH"): ("Ohio State University-Main Campus", "OH"),
}
SERIES = {**{f: s80.FIELD_CIP[f] for f in FIELDS}, **{c: c for f in FIELDS for c, _ in RELATED[f]}}
TERRITORIES = {"PR", "GU", "VI", "AS", "MP", "FM", "MH", "PW"}
OUT_MD = ROOT / "NOBEL_RESULT.md"
OUT_EST = ROOT / "data" / "interim" / "nobel_event_study_estimates.csv"
OUT_STK = ROOT / "data" / "interim" / "nobel_event_study_stacks.csv"
LOG = []


def say(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)


def head(t):
    say("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def rng_for(tag: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SEED, zlib.crc32(tag.encode())]))


def draws(tag: str, B: int, G: int):
    rng = rng_for(tag)
    for s0 in range(0, B, CHUNK):
        yield WEBB[rng.integers(6, size=(min(CHUNK, B - s0), G))]


def fm(v, d=3):
    return "—" if v is None or not np.isfinite(v) else f"{v:+.{d}f}"


def fu(v, d=3):
    return "—" if v is None or not np.isfinite(v) else f"{v:.{d}f}"


def fp(p):
    return "—" if p is None or not np.isfinite(p) else (f"{p:.3f}" if p >= 0.001 else "<0.001")


# =============================================================================================
# data: events (scripts/80), completions series, states
# =============================================================================================
def load_series():
    """Same files, filters and grand-total column rule as s80.load_completions, for more CIP prefixes plus the
    institution total (all rows except CIP 99), the CIP 99 rows themselves and the CIP 95 rows (checks)."""
    want = ["unitid", "cipcode", "awlevel", "majornum", "ctotalt", "crace24", "ctotalm", "ctotalw", "crace15", "crace16"]
    paths = {y: s80.C_DIR / f"{f}.zip" for y, f in s80.C_FILES.items()}
    paths[2023] = s80.RAW / "ipeds" / "C2023_A.zip"
    out, exists = [], {}
    for y, pth in sorted(paths.items()):
        d = s80._read_zip_csv(pth, want)
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

        def agg(mask, key):
            x = d[mask].groupby("unitid").n.sum()
            out.append(pd.DataFrame({"unitid": x.index.str.strip(), "series": key, "year": y, "n": x.values}))

        is99 = d.cip.str.startswith("99")
        agg(~is99, "tot")
        agg(is99, "g99")
        agg(d.cip.str.startswith("95"), "c95")
        for k, pre in SERIES.items():
            m = d.cip.str.startswith(pre)
            exists[(k, y)] = bool(m.any())
            agg(m, k)
    return pd.concat(out, ignore_index=True), exists, sorted(paths)


class Data:
    def __init__(self):
        head("DATA: events and crosswalk imported from scripts/80; IPEDS bachelor's completions")
        self.hd = s80.load_hd()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            t80, self.res80 = s80.design_c(self.hd)
        self.t80 = t80.reset_index(drop=True)
        assert len(self.t80) == 134, len(self.t80)
        smp = self.t80[self.t80.strict & self.t80.clean_prior5].copy()
        assert len(smp) == 88 and smp.unitid.nunique() == 42, (len(smp), smp.unitid.nunique())
        self.sample = smp.sort_values(["field", "year", "unitid"]).reset_index(drop=True)
        say(f"scripts/80 design_c (output captured, {len(buf.getvalue().splitlines())} lines): {len(self.t80)} "
            f"institution x field x year events 1995-2018 at {self.t80.unitid.nunique()} institutions; strict "
            f"(completions in t-4..t and t+1..t+5): {int(self.t80.strict.sum())}; strict and clean of a prior prize "
            f"in t-5..t-1: {len(smp)} events at {smp.unitid.nunique()} institutions, "
            f"{smp.groupby(['unitid', 'field']).ngroups} cells")
        say(f"  sample by field: {dict((f, int((smp.field == f).sum())) for f in FIELDS)}; event years "
            f"{int(smp.year.min())}-{int(smp.year.max())}; clean over t-5..t+5: {int(smp.clean_window.sum())}; "
            f"medical-school-only: {int(smp.med_only.sum())}")
        # completions
        comp80, _ = s80.load_completions()
        long, self.exists, self.years = load_series()
        long = long.groupby(["series", "unitid", "year"], as_index=False).n.sum()
        self.uids = sorted(long.unitid.unique())
        self.uix = {u: k for k, u in enumerate(self.uids)}
        self.yix = {y: k for k, y in enumerate(self.years)}
        self.arr = {}
        for k, g in long.groupby("series"):
            a = np.zeros((len(self.uids), len(self.years)))
            a[g.unitid.map(self.uix).to_numpy(), g.year.map(self.yix).to_numpy()] = g.n.to_numpy()
            self.arr[k] = a
        c80 = comp80.groupby(["field", "unitid", "year"], as_index=False).n.sum()
        for f in FIELDS:
            g = c80[c80.field == f]
            a = np.zeros_like(self.arr[f])
            a[g.unitid.map(self.uix).to_numpy(), g.year.map(self.yix).to_numpy()] = g.n.to_numpy()
            assert np.array_equal(a, self.arr[f]), f
        say(f"completions: files for years {self.years[0]}-{self.years[-1]} (missing: "
            f"{[y for y in range(self.years[0], self.years[-1] + 1) if y not in self.yix]}); {len(self.uids)} UNITIDs; "
            f"the four prize-field series equal s80.load_completions exactly")
        for k in SERIES:
            miss = [y for y in self.years if not self.exists[(k, y)]]
            if miss:
                say(f"  CIP prefix {k}: absent from the files of {miss} (counts as missing for everyone)")
        # denominator check: total (all rows except 99) vs the 99 grand-total rows
        tot, g99, c95 = self.arr["tot"], self.arr["g99"], self.arr["c95"]
        has99 = g99 > 0
        agree = np.abs(tot - g99) <= 0.5
        agree95 = np.abs(tot - c95 - g99) <= 0.5
        say(f"denominator check over institution-years with a CIP 99 row ({int(has99.sum())}): total of non-99 rows "
            f"equals the 99 row in {agree[has99].mean():.4f}; non-99 minus CIP 95 rows equals it in "
            f"{agree95[has99].mean():.4f}")
        byy = [(y, float(agree[:, k][has99[:, k]].mean()) if has99[:, k].any() else np.nan,
                int(has99[:, k].sum())) for y, k in self.yix.items()]
        say("  share agreeing by year (institution-years with a 99 row): " +
            ", ".join(f"{y}:{a:.3f}({n})" for y, a, n in byy))
        self.denom_agree = float(agree[has99].mean())
        self.denom_min_year = min((a, y) for y, a, n in byy if np.isfinite(a))
        nat95 = c95.sum(0)
        say(f"  CIP 95 rows, national sum by year (where present): " +
            ", ".join(f"{y}:{nat95[k]:.0f}" for y, k in self.yix.items() if nat95[k] > 0))
        # states (US = 50 states + DC) and R1
        st = self.hd.sort_values("year").groupby("unitid").stabbr.last()
        self.us = np.array([(u in st.index) and isinstance(st.get(u), str) and st.get(u) not in TERRITORIES
                            for u in self.uids])
        self.has_state = np.array([u in st.index for u in self.uids])
        hd19 = s80._read_zip_csv(s80.HD_DIR / "HD2019.zip", ["unitid", "c18basic"])
        r1 = set(hd19[hd19.c18basic.str.strip() == "15"].unitid.str.strip())
        self.r1 = np.array([u in r1 for u in self.uids])
        say(f"US (50 states + DC) UNITIDs with an IPEDS HD state: {int(self.us.sum())}; R1 (Carnegie 2018 basic 15): "
            f"{int(self.r1.sum())}")
        # treatment histories (imported list, all 134 events)
        self.first = {f: np.full(len(self.uids), np.inf) for f in FIELDS}
        for r in self.t80.itertuples():
            if r.unitid in self.uix:
                k = self.uix[r.unitid]
                self.first[r.field][k] = min(self.first[r.field][k], r.year)
        self.prizes = {}
        for r in self.t80.itertuples():
            self.prizes.setdefault((r.unitid, r.field), []).append(int(r.year))
        self.ext = self.extended_prizes()

    def extended_prizes(self) -> pd.DataFrame:
        """E1: prizes 1990-1994 and 2019-2023 mapped through the imported NOBEL_AFF table only."""
        L = json.loads(s80.NOBEL.read_text())["laureates"]
        rows = []
        for l in L:
            for pz in l.get("nobelPrizes", []):
                y, cat = int(pz["awardYear"]), pz["category"]["en"]
                if cat not in s80.NOBEL_CAT or not (1990 <= y <= 1994 or 2019 <= y <= 2023):
                    continue
                for a in pz.get("affiliations", []) or []:
                    rows.append(dict(year=y, field=s80.NOBEL_CAT[cat],
                                     laureate=(l.get("knownName") or {}).get("en"),
                                     aff=(a.get("name") or {}).get("en", ""),
                                     city=(a.get("city") or {}).get("en", "") or "",
                                     country=(a.get("country") or {}).get("en", "")))
        x = pd.DataFrame(rows)
        us = x[x.country == "USA"].copy()
        idx = {}
        for nm, st, u in zip(self.hd.instnm, self.hd.stabbr, self.hd.unitid):
            idx.setdefault((s80.key(nm), st), set()).add(u)
        mapped, unm, nondeg, supp = [], [], 0, []
        for r in us.sort_values(["year", "field", "aff"]).itertuples():
            k = (r.aff, r.city)
            ks = (int(r.year), r.field, r.aff, r.city)
            if k not in s80.NOBEL_AFF:
                unm.append(f"{r.year} {r.field} {r.aff} ({r.city}) [{r.laureate}]")
                if ks in SUPP_AFF:                       # revision 1 (R1.1)
                    tg = SUPP_AFF[ks]
                    us_ = idx.get((s80.key(tg[0]), tg[1]), set())
                    assert len(us_) == 1, ks
                    supp.append(dict(unitid=sorted(us_)[0], field=r.field, year=int(r.year), aff=r.aff,
                                     laureate=r.laureate, ipeds=tg[0]))
                continue
            tg = s80.NOBEL_AFF[k]
            if tg is None:
                nondeg += 1
                continue
            us_ = idx.get((s80.key(tg[0]), tg[1]), set())
            if len(us_) != 1:
                unm.append(f"{r.year} {r.field} {r.aff} ({r.city}) [unresolved IPEDS name]")
                continue
            mapped.append(dict(unitid=sorted(us_)[0], field=r.field, year=r.year))
        assert len(supp) == len(SUPP_AFF), (len(supp), len(SUPP_AFF))
        m = pd.DataFrame(mapped).drop_duplicates() if mapped else pd.DataFrame(columns=["unitid", "field", "year"])
        sp = pd.DataFrame(supp)
        m_rev = pd.concat([m, sp[["unitid", "field", "year"]]], ignore_index=True).drop_duplicates()
        old = set(map(tuple, m[["unitid", "field", "year"]].to_numpy()))
        new_ev = [tuple(x) for x in sp[["unitid", "field", "year"]].drop_duplicates().to_numpy() if tuple(x) not in old]
        old_cells = {(u, f) for u, f, _ in old}
        new_cells = sorted({(u, f) for u, f, _ in new_ev if (u, f) not in old_cells})
        self.ext_rev = m_rev.reset_index(drop=True)
        self.supp_info = dict(rows=len(sp), events=int(sp[["unitid", "field", "year"]].drop_duplicates().shape[0]),
                              cells=int(sp[["unitid", "field"]].drop_duplicates().shape[0]), new_events=len(new_ev),
                              new_cells=len(new_cells), already=[f"{r.ipeds} {r.field} {r.year}" for r in sp.itertuples()
                                                                 if (r.unitid, r.field, r.year) in old],
                              list=[f"{r.ipeds} ({r.unitid}) {r.field} {r.year} [{r.laureate}; '{r.aff}']"
                                    for r in sp.itertuples()], total=len(m_rev))
        say(f"E1 extended prize list (1990-1994, 2019-2023): {len(x)} prize-affiliation rows in the four fields, "
            f"{len(us)} US; mapped through NOBEL_AFF to {len(m)} institution x field x year prizes; "
            f"non-degree-granting {nondeg}; not in the table (not mapped) {len(unm)}:")
        for s_ in unm:
            say("    " + s_)
        self.ext_unmapped = unm
        si = self.supp_info
        say(f"  revision 1, added after the results had been seen: SUPP_AFF maps {si['rows']} of these rows = {si['events']} "
            f"institution x field x year prizes in {si['cells']} cells; new relative to the table-only list: "
            f"{si['new_events']} prizes, {si['new_cells']} new cells; already mapped through another laureate's "
            f"affiliation: {si['already']}; revised extended list: {si['total']} prizes")
        for s_ in si["list"]:
            say("    + " + s_)
        return m


# =============================================================================================
# stacks
# =============================================================================================
def build_stacks(D: Data, evs: pd.DataFrame, ctrl_extra=None, first=None, tag="") -> list:
    """O3: one stack per event; balanced; controls = same field, US, positive in every stack year, untreated <= t+5."""
    first = D.first if first is None else first
    out = []
    for r in evs.itertuples():
        f, t, i = r.field, int(r.year), D.uix[r.unitid]
        A = D.arr[f]
        yrs = [y for y in range(t - 5, t + 6) if y in D.yix and A[i, D.yix[y]] > 0]
        assert t in yrs
        cols = [D.yix[y] for y in yrs]
        m = (A[:, cols] > 0).all(1) & D.us & ~(first[f] <= t + 5)
        m[i] = False
        if ctrl_extra is not None:
            m &= ctrl_extra
        out.append(dict(unitid=r.unitid, inst=r.inst, field=f, t=t, i=i, yrs=yrs, cols=cols,
                        ctrl=np.flatnonzero(m), ycode=f, med_only=bool(r.med_only),
                        clean_window=bool(r.clean_window)))
    return out


def stacks_related(D: Data, evs: pd.DataFrame, choice: dict) -> tuple[list, pd.DataFrame]:
    """O8 (b): spillover stacks for each event in the related field chosen for its prize field."""
    out, rows = [], []
    for r in evs.itertuples():
        f, t, i = r.field, int(r.year), D.uix[r.unitid]
        rc = choice[f]
        g = next((ff for ff, c in s80.FIELD_CIP.items() if rc.startswith(c)), None)    # prize field containing rc
        A = D.arr[f]
        yrs0 = [y for y in range(t - 5, t + 6) if y in D.yix and A[i, D.yix[y]] > 0]
        yrs = [y for y in yrs0 if D.exists[(rc, y)]]
        cols = [D.yix[y] for y in yrs]
        R = D.arr[rc]
        excl = g is not None and any(t - 5 <= y <= t + 5 for y in D.prizes.get((r.unitid, g), []))
        offered = bool((R[i, cols] > 0).all())
        rows.append(dict(unitid=r.unitid, field=f, t=t, related=rc, excluded=excl, offered=offered))
        if excl or not offered:
            continue
        m = (R[:, cols] > 0).all(1) & D.us & ~(D.first[f] <= t + 5)
        if g is not None:
            m &= ~(D.first[g] <= t + 5)
        m[i] = False
        out.append(dict(unitid=r.unitid, inst=r.inst, field=f, t=t, i=i, yrs=yrs, cols=cols, ctrl=np.flatnonzero(m),
                        ycode=rc, med_only=bool(r.med_only), clean_window=bool(r.clean_window)))
    return out, pd.DataFrame(rows)


def related_availability(D: Data) -> tuple[dict, list]:
    """O8 (b) selection from availability (positivity) counts only."""
    choice, lines = {}, []
    for f in FIELDS:
        evf = D.sample[D.sample.field == f]
        need = int(np.ceil(len(evf) / 2))
        cnt = []
        for rc, lab in RELATED[f]:
            _, tab = stacks_related(D, evf, {f: rc})
            n_ok = int((~tab.excluded & tab.offered).sum())
            cnt.append((rc, lab, n_ok, int(tab.excluded.sum())))
        pick = next((c for c in cnt if c[2] >= need), None)
        rule = "first candidate offered in every stack year for at least half of the field's events"
        if pick is None:
            pick = max(cnt, key=lambda c: c[2])
            rule = "no candidate reaches half; candidate with the most such events"
        choice[f] = pick[0]
        lines.append(dict(field=f, n_events=len(evf), need=need, cands=cnt, pick=pick, rule=rule))
        say(f"  {FNAME[f]} ({len(evf)} events, half = {need}): " +
            "; ".join(f"{lab}: offered in all stack years at {n} events (excluded by own-prize rule: {x})"
                      for rc, lab, n, x in cnt) + f" -> {pick[1]} ({rule})")
    return choice, lines


def y_log(D, st, rows):
    return np.log(D.arr[st["ycode"]][rows][:, st["cols"]])


def y_ddd(D, st, rows):
    n = D.arr[st["field"]][rows][:, st["cols"]]
    rest = D.arr["tot"][rows][:, st["cols"]] - n
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(n) - np.log(rest)


def y_share(D, st, rows):
    n = D.arr[st["field"]][rows][:, st["cols"]]
    tot = D.arr["tot"][rows][:, st["cols"]]
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100.0 * n / tot


def assemble(D: Data, stacks: list, yfun) -> dict:
    parts = {k: [] for k in ("s", "cell", "l", "e", "D", "uid", "y")}
    T_s, n_s, dropped = [], [], 0
    c0 = l0 = 0
    for s, st in enumerate(stacks):
        rows = np.concatenate([[st["i"]], st["ctrl"]]).astype(np.int64)
        Y = yfun(D, st, rows)
        ok = np.isfinite(Y).all(1)
        assert ok[0], ("treated outcome not finite", st["unitid"], st["field"], st["t"])
        dropped += int((~ok).sum())
        rows, Y = rows[ok], Y[ok]
        n, T = Y.shape
        e = np.array(st["yrs"]) - st["t"]
        parts["s"].append(np.full(n * T, s))
        parts["cell"].append(c0 + np.repeat(np.arange(n), T))
        parts["l"].append(l0 + np.tile(np.arange(T), n))
        parts["e"].append(np.tile(e, n))
        parts["D"].append(np.repeat(np.r_[1.0, np.zeros(n - 1)], T))
        parts["uid"].append(np.repeat(rows, T))
        parts["y"].append(Y.ravel())
        T_s.append(T)
        n_s.append(n)
        c0 += n
        l0 += T
    out = {k: np.concatenate(v) for k, v in parts.items()}
    out.update(T_s=np.array(T_s), n_s=np.array(n_s), S=len(stacks), L=l0, C=c0, dropped=dropped,
               stacks=stacks)
    return out


# =============================================================================================
# stacked regression with stack x cell and stack x year effects; CR1; fast WCR bootstrap
# =============================================================================================
def gsum(idx, v, n):
    if v.ndim == 1:
        return np.bincount(idx, weights=v, minlength=n)
    return np.column_stack([np.bincount(idx, weights=v[:, j], minlength=n) for j in range(v.shape[1])])


class Fit:
    def __init__(self, a: dict):
        self.a = a
        self.N = len(a["y"])
        self.S, self.L, self.C = a["S"], a["L"], a["C"]
        self.T_s, self.n_s = a["T_s"], a["n_s"]
        self.s, self.cell, self.l, self.e = a["s"], a["cell"], a["l"], a["e"]
        uq, self.cl = np.unique(a["uid"], return_inverse=True)
        self.G = len(uq)
        self.uid_cl = uq
        self.G_treated = len(np.unique(a["uid"][a["D"] == 1]))
        self.T_cell = np.bincount(self.cell, minlength=self.C).astype(float)
        self.n_l = np.repeat(self.n_s, self.T_s).astype(float)
        self.l0 = np.r_[0, np.cumsum(self.T_s)[:-1]]
        self.stack_of_l = np.repeat(np.arange(self.S), self.T_s)
        X = np.column_stack([a["D"] * (self.e == ev) for ev in EVT]).astype(float)
        self.k = X.shape[1]
        self.X = X
        self.Xt = self.dm(X)
        self.yt = self.dm(a["y"])
        assert np.abs(self.dm(self.Xt) - self.Xt).max() < 1e-10
        XtX = self.Xt.T @ self.Xt
        self.A = np.linalg.inv(XtX)
        self.beta = self.A @ (self.Xt.T @ self.yt)
        self.res = self.yt - self.Xt @ self.beta
        self.Kdof = self.k + int(np.sum(self.T_s - 1))
        self.scale = self.G / (self.G - 1) * (self.N - 1) / (self.N - self.Kdof)
        # revision 1 (R1.3): factor with the C cell effects also counted in K
        self.scale_cell = self.G / (self.G - 1) * (self.N - 1) / (self.N - self.Kdof - self.C)
        Sg = gsum(self.cl, self.Xt * self.res[:, None], self.G)
        self.V = self.scale * self.A @ (Sg.T @ Sg) @ self.A

    def dm(self, v):
        """exact two-way within transformation for balanced stacks (cell and stack-year effects)"""
        cm = gsum(self.cell, v, self.C)
        ym = gsum(self.l, v, self.L)
        sm = gsum(self.s, v, self.S)
        if v.ndim == 1:
            return v - (cm / self.T_cell)[self.cell] - (ym / self.n_l)[self.l] + \
                (sm / (self.n_s * self.T_s))[self.s]
        return v - (cm / self.T_cell[:, None])[self.cell] - (ym / self.n_l[:, None])[self.l] + \
            (sm / (self.n_s * self.T_s)[:, None])[self.s]

    def glsum(self, v):
        return np.bincount(self.cl * self.L + self.l, weights=v, minlength=self.G * self.L).reshape(self.G, self.L)

    def qmul(self, H):
        """H (G x L) times the pseudo-inverse of Z'M_C Z (block-diagonal by stack: (I - 11'/T) / n_s)"""
        out = np.empty_like(H)
        for s in range(self.S):
            sl = slice(self.l0[s], self.l0[s] + self.T_s[s])
            h = H[:, sl]
            out[:, sl] = (h - h.mean(1, keepdims=True)) / self.n_s[s]
        return out

    # ---- one linear combination c'beta: WCR bootstrap-t with test inversion ----
    def prep_lin(self, c):
        c = np.asarray(c, float)
        Ac = self.A @ c
        u = self.Xt @ Ac
        om = float(c @ Ac)
        th = float(c @ self.beta)
        se = float(np.sqrt(c @ self.V @ c))
        E0 = self.res + u * th / om                     # restricted residuals at theta0 = 0
        H = self.glsum(u)
        P = gsum(self.cl, self.Xt * u[:, None], self.G)
        return dict(c=c, th=th, se=se, om=om, a0=gsum(self.cl, u * E0, self.G), a1=gsum(self.cl, u * u, self.G) / om,
                    H=H, K0=self.glsum(E0), P=P, J0=gsum(self.cl, self.Xt * E0[:, None], self.G),
                    Hq=self.qmul(H), APt=self.A @ P.T)

    def parts_lin(self, pr, V):
        """for replicate weights V (R x G): theta* - theta0 = B0 - theta0 B1; sum of squared CR scores
        = q0 - theta0 q1 + theta0^2 q2 (restricted residuals are linear in theta0)"""
        B0, B1 = V @ pr["a0"], V @ pr["a1"]
        S0 = V * pr["a0"][None, :] - (V @ pr["K0"]) @ pr["Hq"].T - (V @ pr["J0"]) @ pr["APt"]
        S1 = V * pr["a1"][None, :] - ((V @ pr["H"]) / pr["om"]) @ pr["Hq"].T - ((V @ pr["P"]) / pr["om"]) @ pr["APt"]
        return B0, B1, (S0 * S0).sum(1), 2.0 * (S0 * S1).sum(1), (S1 * S1).sum(1)

    def infer_lin(self, c, B, tag):
        pr = self.prep_lin(c)
        acc = [[] for _ in range(5)]
        for V in draws(tag, B, self.G):
            for j, x in enumerate(self.parts_lin(pr, V)):
                acc[j].append(x)
        inv = dict(zip(("B0", "B1", "q0", "q1", "q2"), (np.concatenate(x) for x in acc)))
        th, se = pr["th"], pr["se"]
        t0 = inv["B0"] / np.sqrt(self.scale * inv["q0"])
        p0 = float((1 + np.sum(np.abs(t0) >= abs(th / se) - 1e-12)) / (1 + B))
        q95 = float(np.quantile(np.abs(t0), 0.95))
        ci = invert(inv, th, se, self.scale, B)
        assert abs(ci["p0"] - p0) < 1e-12, (tag, ci["p0"], p0)
        tq = float(tdist.ppf(0.975, self.G - 1))
        return dict(theta=th, se=se, lo=ci["lo"], hi=ci["hi"], connected=ci["connected"], p=p0, q95=q95,
                    mde=(q95 + Z80) * se, lo_cr1=th - tq * se, hi_cr1=th + tq * se,
                    p_cr1=float(2 * tdist.sf(abs(th / se), self.G - 1)), mde_cr1=(tq + Z80) * se, B=B,
                    mde_dofcell=(q95 + Z80) * se * float(np.sqrt(self.scale_cell / self.scale)))

    # ---- joint Wald test of C'beta = 0: WCR bootstrap ----
    def prep_joint(self, Cm):
        Cm = np.asarray(Cm, float)
        AC = self.A @ Cm
        U = self.Xt @ AC
        Om = Cm.T @ AC
        th = Cm.T @ self.beta
        Vh = Cm.T @ self.V @ Cm
        W = float(th @ np.linalg.solve(Vh, th))
        E = self.res + U @ np.linalg.solve(Om, th)
        m = Cm.shape[1]
        return dict(m=m, W=W, a=gsum(self.cl, U * E[:, None], self.G), K=self.glsum(E),
                    J=gsum(self.cl, self.Xt * E[:, None], self.G),
                    Hq=[self.qmul(self.glsum(U[:, j])) for j in range(m)],
                    APt=[self.A @ gsum(self.cl, self.Xt * U[:, [j]], self.G).T for j in range(m)])

    def parts_joint(self, pr, V):
        num = V @ pr["a"]
        VK, VJ = V @ pr["K"], V @ pr["J"]
        S = np.stack([V * pr["a"][:, j][None, :] - VK @ pr["Hq"][j].T - VJ @ pr["APt"][j] for j in range(pr["m"])], -1)
        M = self.scale * np.einsum("rgj,rgk->rjk", S, S)
        return np.einsum("rj,rj->r", num, np.linalg.solve(M, num[..., None])[..., 0])

    def infer_joint(self, Cm, B, tag):
        pr = self.prep_joint(Cm)
        Ws = np.concatenate([self.parts_joint(pr, V) for V in draws(tag, B, self.G)])
        p = float((1 + np.sum(Ws >= pr["W"] * (1 - 1e-12))) / (1 + B))
        return dict(W=pr["W"], p=p, p_chi2=float(chi2.sf(pr["W"], pr["m"])), m=pr["m"], B=B)


def wcr_pvals(inv, th, se, scale, B, b0):
    b0 = np.atleast_1d(np.asarray(b0, float))
    out = np.empty(len(b0))
    for s0 in range(0, len(b0), 50):
        bb = b0[s0:s0 + 50][:, None]
        num = inv["B0"][None, :] - bb * inv["B1"][None, :]
        den = np.sqrt(np.maximum(scale * (inv["q0"][None, :] - bb * inv["q1"][None, :] + bb ** 2 * inv["q2"][None, :]),
                                 1e-300))
        tobs = np.abs(th - bb) / se
        out[s0:s0 + 50] = (1 + (np.abs(num / den) >= tobs - 1e-12).sum(1)) / (1 + B)
    return out


def invert(inv, th, se, scale, B, alpha=0.05):
    """95% set {theta0: WCR p(theta0) > alpha}: grid over theta +/- 12 SE (60 SE if an edge is accepted), then
    bisection at the outermost accepted points; reports the hull and whether accepted grid points are contiguous."""
    p0 = float(wcr_pvals(inv, th, se, scale, B, [0.0])[0])
    for span in (12.0, 60.0):
        g = th + se * np.linspace(-span, span, 1201)
        acc = wcr_pvals(inv, th, se, scale, B, g) > alpha
        if not (acc[0] or acc[-1]):
            break
    idx = np.flatnonzero(acc)
    connected = bool(len(idx) and (idx[-1] - idx[0] + 1 == len(idx)))

    def bis(a_in, b_out):
        for _ in range(40):
            mid = 0.5 * (a_in + b_out)
            if wcr_pvals(inv, th, se, scale, B, [mid])[0] > alpha:
                a_in = mid
            else:
                b_out = mid
        return 0.5 * (a_in + b_out)

    lo = -np.inf if acc[0] else bis(g[idx[0]], g[idx[0] - 1])
    hi = np.inf if acc[-1] else bis(g[idx[-1]], g[idx[-1] + 1])
    return dict(lo=float(lo), hi=float(hi), connected=connected, p0=p0)


def cvec(weights: dict) -> np.ndarray:
    c = np.zeros(len(EVT))
    for e, w in weights.items():
        c[EVT.index(e)] = w
    return c


C_AVG = cvec({e: 0.25 for e in POST})
C_PRE = np.column_stack([cvec({e: 1.0}) for e in PRE])
C_E4 = cvec({**{e: 0.25 for e in POST}, **{e: -1.0 / 6 for e in PRE}})


# =============================================================================================
# O10 self-check: brute-force dummy regressions with explicit bootstrap samples
# =============================================================================================
def selfcheck(D: Data, stacks: list):
    head("O10 SELF-CHECK: fast WCR algebra vs brute-force dummy regressions (small subsample)")
    full = [st for st in stacks if len(st["yrs"]) == 11 and st["field"] == "che"][:3]
    inter = sorted(set(full[0]["ctrl"]) & set(full[1]["ctrl"]) & set(full[2]["ctrl"]))[:12]
    sub = []
    for st in full:
        own = sorted(set(st["ctrl"]) - set(inter))[:3]
        sub.append({**st, "ctrl": np.array(inter + own, dtype=np.int64)})
    a = assemble(D, sub, y_log)
    F_ = Fit(a)
    N = F_.N
    Fm = np.zeros((N, a["C"] + a["L"]))
    Fm[np.arange(N), a["cell"]] = 1.0
    Fm[np.arange(N), a["C"] + a["l"]] = 1.0
    MF = np.eye(N) - Fm @ np.linalg.pinv(Fm)
    Xb, yb = MF @ F_.X, MF @ a["y"]
    Ab = np.linalg.inv(Xb.T @ Xb)
    bb = Ab @ Xb.T @ yb
    eb = yb - Xb @ bb

    def cr1(Xb_, e_):
        Sg = gsum(F_.cl, Xb_ * e_[:, None], F_.G)
        return F_.scale * Ab @ (Sg.T @ Sg) @ Ab

    Vb = cr1(Xb, eb)
    d_beta = float(np.abs(bb - F_.beta).max())
    d_se = float(np.abs(np.sqrt(np.diag(Vb)) - np.sqrt(np.diag(F_.V))).max())
    rng = rng_for("selfcheck")
    Vw = WEBB[rng.integers(6, size=(20, F_.G))]
    # scalar combination, restricted at theta0
    th0 = 0.05
    c = C_AVG
    om = float(c @ Ab @ c)
    br = bb - Ab @ c * (float(c @ bb) - th0) / om
    er = yb - Xb @ br
    yfit = a["y"] - er
    t_bf = []
    for v in Vw:
        ys = yfit + v[F_.cl] * er
        ytb = MF @ ys
        bs = Ab @ Xb.T @ ytb
        es = ytb - Xb @ bs
        Vs = cr1(Xb, es)
        t_bf.append((float(c @ bs) - th0) / np.sqrt(float(c @ Vs @ c)))
    pr = F_.prep_lin(c)
    B0, B1, q0, q1, q2 = F_.parts_lin(pr, Vw)
    t_fast = (B0 - th0 * B1) / np.sqrt(F_.scale * (q0 - th0 * q1 + th0 ** 2 * q2))
    d_t = float(np.abs(np.array(t_bf) - t_fast).max())
    # joint pre-trend Wald
    Cm = C_PRE
    thj = Cm.T @ bb
    brj = bb - Ab @ Cm @ np.linalg.solve(Cm.T @ Ab @ Cm, thj)
    erj = yb - Xb @ brj
    yfj = a["y"] - erj
    W_bf = []
    for v in Vw:
        ys = yfj + v[F_.cl] * erj
        ytb = MF @ ys
        bs = Ab @ Xb.T @ ytb
        es = ytb - Xb @ bs
        Vs = Cm.T @ cr1(Xb, es) @ Cm
        ts = Cm.T @ bs
        W_bf.append(float(ts @ np.linalg.solve(Vs, ts)))
    W_fast = F_.parts_joint(F_.prep_joint(Cm), Vw)
    d_W = float(np.max(np.abs(np.array(W_bf) - W_fast) / np.maximum(1.0, np.abs(W_fast))))
    say(f"subsample: 3 chemistry stacks ({', '.join(f'{st['inst']} {st['t']}' for st in sub)}), {N} rows, "
        f"{F_.G} clusters; max |diff|: beta {d_beta:.1e}, CR1 SE {d_se:.1e}, bootstrap t (theta0 = 0.05, 20 draws) "
        f"{d_t:.1e}, bootstrap Wald (relative) {d_W:.1e}")
    assert max(d_beta, d_se, d_t, d_W) < 1e-8
    return dict(d_beta=d_beta, d_se=d_se, d_t=d_t, d_W=d_W, N=N, G=F_.G)


# =============================================================================================
# running a specification
# =============================================================================================
def run_spec(name: str, a: dict, path: bool = False, extra: dict | None = None, log_outcome: bool = True) -> dict:
    F = Fit(a)
    F.X = None
    out = dict(name=name, N=F.N, S=F.S, G=F.G, Gt=F.G_treated, C=F.C, dropped=a["dropped"],
               n_ctrl=a["n_s"] - 1, T_s=a["T_s"], log_outcome=log_outcome)
    out["avg"] = F.infer_lin(C_AVG, B_MAIN, f"avg:{name}")
    out["pre"] = F.infer_joint(C_PRE, B_MAIN, f"pre:{name}")
    out["beta"] = dict(zip(EVT, F.beta))
    out["se"] = dict(zip(EVT, np.sqrt(np.diag(F.V))))
    out["n_e"] = {e: int(sum(1 for st, T in zip(a["stacks"], a["T_s"]) if (st["t"] + e) in st["yrs"])) for e in EVT}
    if path:
        out["path"] = {e: F.infer_lin(cvec({e: 1.0}), B_PATH, f"path:{name}:{e}") for e in EVT}
    for lab, c in (extra or {}).items():
        out[lab] = F.infer_lin(c, B_MAIN, f"{lab}:{name}")
    av, pr = out["avg"], out["pre"]
    out["label"] = verdict(pr["p"], av["lo"], av["hi"], av["mde"], log_outcome)
    out["label_dofcell"] = verdict(pr["p"], av["lo"], av["hi"], av["mde_dofcell"], log_outcome)   # revision 1
    # post hoc, reporting only: the label under the literal reading (total clusters >= 50 -> CR1 inference)
    out["label_cr1"] = verdict(pr["p_chi2"], av["lo_cr1"], av["hi_cr1"], av["mde_cr1"], log_outcome)
    if path:
        out["n_path_excl0"] = [e for e in EVT if out["path"][e]["lo"] > 0 or out["path"][e]["hi"] < 0]
    say(f"[{name}] theta(t+2..t+5) = {fm(av['theta'])} [WCR {fm(av['lo'])}, {fm(av['hi'])}]"
        f"{'' if av['connected'] else ' (accepted set not contiguous)'}, CR1 SE {fu(av['se'])} "
        f"(CR1 CI [{fm(av['lo_cr1'])}, {fm(av['hi_cr1'])}]), WCR p(theta=0) {fp(av['p'])}, q95 {av['q95']:.2f}, "
        f"MDE {fu(av['mde'])}; pre-trend Wald {pr['W']:.2f} (5 df), WCR p {fp(pr['p'])} (chi2 p {fp(pr['p_chi2'])}); "
        f"rule label: {out['label']}")
    say(f"    revision 1, added after the results had been seen: MDE with the cell effects also counted in the CR1 degrees of "
        f"freedom = {fu(av['mde_dofcell'])} (label with it: "
        f"{verdict(pr['p'], av['lo'], av['hi'], av['mde_dofcell'], log_outcome)})")
    say(f"    CR1-only reading (post hoc, reporting only): MDE (t_.975 + 0.842) x SE = {fu(av['mde_cr1'])}; label with "
        f"CR1 CI, chi2 pre-trend p and this MDE: {out['label_cr1']}")
    say(f"    stacks {F.S}, treated institutions {F.G_treated}, clusters {F.G}, cells {F.C}, rows {F.N}; controls per "
        f"stack median {int(np.median(out['n_ctrl']))} (min {int(out['n_ctrl'].min())}, max "
        f"{int(out['n_ctrl'].max())}); control cells dropped for a non-finite outcome: {a['dropped']}")
    if path:
        say("    event-time path (reference e = 0): " + "; ".join(
            f"e={e:+d}: {fm(out['path'][e]['theta'])} [{fm(out['path'][e]['lo'])}, {fm(out['path'][e]['hi'])}]"
            for e in EVT))
    del F
    return out


def verdict(pre_p, lo, hi, mde, log_outcome=True) -> str:
    if pre_p < PRE_ALPHA:
        return "invalid (pre-trend)"
    if lo > 0:
        return "positive"
    if hi < 0:
        return "negative"
    if not log_outcome:
        return "CI includes 0 (MDE rule n/a)"
    return "null" if mde <= BENCH else "underpowered"


# =============================================================================================
# main
# =============================================================================================
def main():
    src = Path(__file__).read_text()
    pre_txt = src[src.index("Units:\n"):src.index("END OF PRE-SPECIFICATION.")].rstrip() + "\n"
    op_txt = src[src.index("OPERATIONAL DEFINITIONS (fixed"):src.index("END OF OPERATIONAL DEFINITIONS.")].rstrip() + "\n"
    md5s = dict(pre=hashlib.md5(pre_txt.encode()).hexdigest(), op=hashlib.md5(op_txt.encode()).hexdigest())
    say(f"pre-specification md5 {md5s['pre']}; operational definitions md5 {md5s['op']}")
    D = Data()
    smp = D.sample
    R = dict(md5s=md5s, pre_txt=pre_txt, op_txt=op_txt, supp=D.supp_info)

    head("DESCRIPTIVES: events, repeat winners, stacks")
    def ranked(df):
        x = df.groupby("inst").size().rename("n").reset_index()
        x["neg"] = -x.n
        return x.sort_values(["neg", "inst"]).set_index("inst").n

    per_inst = ranked(D.t80)
    per_inst88 = ranked(smp)
    cells = D.t80.groupby(["unitid", "field"]).size()
    top5_134 = int(per_inst.head(5).sum())
    top5_88 = int(per_inst88.head(5).sum())
    R["repeat"] = dict(n134=len(D.t80), ninst134=D.t80.unitid.nunique(), top5_134=top5_134,
                       top5_names=list(per_inst.head(5).index), top5_counts=list(per_inst.head(5).values),
                       top5_88=top5_88, top5_88_names=list(per_inst88.head(5).index),
                       top5_88_counts=list(per_inst88.head(5).values),
                       cells=len(cells), multi=int((cells > 1).sum()), maxc=int(cells.max()),
                       inst_ge3=int((per_inst >= 3).sum()), inst_1=int((per_inst == 1).sum()),
                       tie5_134=int((per_inst == per_inst.iloc[4]).sum()), k5_134=int(per_inst.iloc[4]),
                       tie5_88=int((per_inst88 == per_inst88.iloc[4]).sum()), k5_88=int(per_inst88.iloc[4]))
    say(f"all 134 events: top 5 institutions {dict(per_inst.head(5))} = {top5_134} events "
        f"({top5_134 / len(D.t80):.0%}); institutions with >= 3 events: {R['repeat']['inst_ge3']}, with 1: "
        f"{R['repeat']['inst_1']}; cells {len(cells)}, with > 1 prize {R['repeat']['multi']} (max {R['repeat']['maxc']})")
    say(f"88-event sample: top 5 institutions {dict(per_inst88.head(5))} = {top5_88} events ({top5_88 / 88:.0%}); "
        f"institutions with the 5th-ranked count ({R['repeat']['k5_88']}): {R['repeat']['tie5_88']}; in the 134: "
        f"{R['repeat']['tie5_134']} at {R['repeat']['k5_134']}")
    say(f"88-event sample, all institutions with >= 3 events: {dict(per_inst88[per_inst88 >= 3])}")
    stacks1 = build_stacks(D, smp)
    T = np.array([len(st["yrs"]) for st in stacks1])
    no5 = [st for st in stacks1 if (st["t"] - 5) not in st["yrs"]]
    no5_file = sum(1 for st in no5 if (st["t"] - 5) not in D.yix)
    R["stk"] = dict(n=len(stacks1), T11=int((T == 11).sum()), T10=int((T == 10).sum()), no5_file=no5_file,
                    no5_zero=len(no5) - no5_file,
                    nctrl_med=int(np.median([len(st["ctrl"]) for st in stacks1])),
                    nctrl_min=int(min(len(st["ctrl"]) for st in stacks1)),
                    nctrl_max=int(max(len(st["ctrl"]) for st in stacks1)),
                    by_field={f: (int(np.median([len(st["ctrl"]) for st in stacks1 if st["field"] == f])),
                                  sum(1 for st in stacks1 if st["field"] == f)) for f in FIELDS})
    tsize = np.array([D.arr[st["field"]][st["i"], D.yix[st["t"]]] for st in stacks1])
    csize = np.array([np.median(D.arr[st["field"]][st["ctrl"], D.yix[st["t"]]]) for st in stacks1])
    R["stk"].update(tsize_med=float(np.median(tsize)), tsize_min=float(tsize.min()), tsize_max=float(tsize.max()),
                    csize_med=float(np.median(csize)))
    say(f"spec 1 stacks: {len(stacks1)}; 11 years {R['stk']['T11']}, 10 years {R['stk']['T10']} (t-5 missing: no "
        f"1991 file {no5_file}, treated cell zero at t-5 {R['stk']['no5_zero']}); controls per stack median "
        f"{R['stk']['nctrl_med']} (min {R['stk']['nctrl_min']}, max {R['stk']['nctrl_max']}); by field (median "
        f"controls, stacks): {R['stk']['by_field']}")
    say(f"treated cells' completions in year t: median {np.median(tsize):.0f} (min {tsize.min():.0f}, max "
        f"{tsize.max():.0f}); median control cell in year t (median over stacks): {np.median(csize):.0f}")
    pd.DataFrame([dict(field=st["field"], unitid=st["unitid"], inst=st["inst"], t=st["t"], years=len(st["yrs"]),
                       first_year=min(st["yrs"]), n_controls=len(st["ctrl"]), med_only=st["med_only"],
                       clean_window=st["clean_window"],
                       treated_completions_t=float(D.arr[st["field"]][st["i"], D.yix[st["t"]]]))
                  for st in stacks1]).to_csv(OUT_STK, index=False)

    R["check"] = selfcheck(D, stacks1)
    # denominator check restricted to the institution-years that enter the spec 1 stacks (share and DDD outcomes)
    used = np.zeros_like(D.arr["tot"], dtype=bool)
    for st_ in stacks1:
        used[np.ix_(np.r_[st_["i"], st_["ctrl"]], st_["cols"])] = True
    has99 = D.arr["g99"] > 0
    agree = np.abs(D.arr["tot"] - D.arr["g99"]) <= 0.5
    only95 = has99 & ~agree & (np.abs(D.arr["tot"] - D.arr["c95"]) <= 0.5)
    first_win = min(min(st_["yrs"]) for st_ in stacks1)
    R["denom"] = dict(agree=D.denom_agree, min_year=D.denom_min_year, used=int(used.sum()),
                      used99=int((used & has99).sum()), used_agree=float(agree[used & has99].mean()),
                      used_bad=int((used & has99 & ~agree).sum()), only95=int(only95.sum()),
                      bad_all=int((has99 & ~agree).sum()), first_win=first_win,
                      bad1990=int((has99 & ~agree)[:, D.yix[1990]].sum()))
    say(f"denominator, institution-years in the spec 1 stacks: {R['denom']['used']} ({R['denom']['used99']} with a "
        f"99 row); total equals the 99 row in {R['denom']['used_agree']:.4f} ({R['denom']['used_bad']} disagree). "
        f"Of all {R['denom']['bad_all']} disagreeing institution-years, {R['denom']['only95']} report only CIP 95 "
        f"rows (95.0000 and 95.9500 both present, so the sum double-counts; no field completions, so never in a "
        f"stack) and {R['denom']['bad1990']} are in 1990; the earliest stack year is {first_win}")
    pct = []
    for st_ in stacks1:
        pct.append(100 * D.arr[st_["field"]][st_["i"], D.yix[st_["t"]]] / D.arr["tot"][st_["i"], D.yix[st_["t"]]])
    R["stk"]["share_med"] = float(np.median(pct))
    say(f"treated cells' share of the institution's bachelor's completions in year t: median {np.median(pct):.2f} pp "
        f"(min {min(pct):.2f}, max {max(pct):.2f})")
    R["res80"] = D.res80

    head("SPEC 1 (primary): log completions, same field at not-yet/never-treated US institutions")
    R["s1"] = run_spec("spec1", assemble(D, stacks1, y_log), path=True, extra={"E4": C_E4})
    head("SPEC 2: triple difference, log(field) - log(rest of the institution)")
    R["s2"] = run_spec("spec2_ddd", assemble(D, stacks1, y_ddd), path=True)
    zr = Counter_()
    for st_ in stacks1:
        rows_ = st_["ctrl"]
        rest_ = D.arr["tot"][rows_][:, st_["cols"]] - D.arr[st_["field"]][rows_][:, st_["cols"]]
        zr[st_["field"]] += int((rest_ <= 0).any(1).sum())
    R["ddd_drop"] = dict(zr)
    say(f"spec 2: control cells with no bachelor's completions outside the field in some stack year (rest = 0, "
        f"log undefined, dropped): {dict(zr)} (total {sum(zr.values())})")
    assert sum(zr.values()) == R["s2"]["dropped"]
    head("SECONDARY (a): field share of the institution's bachelor's completions (percentage points)")
    R["sa"] = run_spec("share", assemble(D, stacks1, y_share), path=True, log_outcome=False)
    head("SECONDARY (b): related field (spillover check); selection from availability counts (O8)")
    choice, sel = related_availability(D)
    R["choice"], R["sel"] = choice, sel
    stacksB, tabB = stacks_related(D, smp, choice)
    R["b_tab"] = dict(n=len(stacksB), excluded=int(tabB.excluded.sum()),
                      not_offered=int((~tabB.excluded & ~tabB.offered).sum()),
                      by_field={f: sum(1 for st in stacksB if st["field"] == f) for f in FIELDS})
    say(f"spillover stacks: {len(stacksB)} of 88 (excluded by the own-prize rule {R['b_tab']['excluded']}, related "
        f"field not offered in every stack year {R['b_tab']['not_offered']}); by field {R['b_tab']['by_field']}")
    R["sb"] = run_spec("spillover", assemble(D, stacksB, y_log), path=True)

    head("FIELD BREAKDOWNS (descriptive only): spec 1 on each field's stacks")
    R["fields"] = {}
    for f in FIELDS:
        sf = [st for st in stacks1 if st["field"] == f]
        R["fields"][f] = run_spec(f"field:{f}", assemble(D, sf, y_log))

    head("EXPLORATORY E1-E5 (pre-declared, no verdict)")

    def e1(ext: pd.DataFrame, name: str, lab: str):
        first_ext = {f: D.first[f].copy() for f in FIELDS}
        for r in ext.itertuples():
            if r.unitid in D.uix:
                k = D.uix[r.unitid]
                first_ext[r.field][k] = min(first_ext[r.field][k], r.year)
        ext_set = {}
        for r in ext.itertuples():
            ext_set.setdefault((r.unitid, r.field), []).append(int(r.year))
        drop_e1 = [i for i, r in enumerate(smp.itertuples())
                   if any(r.year - 5 <= y <= r.year - 1 for y in ext_set.get((r.unitid, r.field), []))]
        st_e1 = build_stacks(D, smp.drop(index=drop_e1), first=first_ext)
        nctrl_lost = sum(len(a_["ctrl"]) - len(b_["ctrl"]) for a_, b_ in
                         zip([st for k, st in enumerate(stacks1) if k not in set(drop_e1)], st_e1))
        info = dict(dropped_events=len(drop_e1), ctrl_lost=nctrl_lost, mapped=len(ext),
                    dropped_list=[f"{smp.inst[i]} {smp.field[i]} {smp.year[i]}" for i in drop_e1])
        say(f"E1 ({lab}): extended-list prizes {len(ext)}; events dropped (extended-list prize in the cell in "
            f"t-5..t-1): {len(drop_e1)} {info['dropped_list']}; control cells removed (extended-list prize through "
            f"t+5): {nctrl_lost}")
        return run_spec(name, assemble(D, st_e1, y_log)), info

    R["E1_orig"], R["e1_info_orig"] = e1(D.ext, "E1_extended_screen", "NOBEL_AFF table only, as first run")
    R["E1"], R["e1_info"] = e1(D.ext_rev, "E1_rev1_extended_screen",
                               "revision 1, added after the results had been seen: NOBEL_AFF + SUPP_AFF")
    R["e1_info"]["unmapped"] = len(D.ext_unmapped) - D.supp_info["rows"]
    R["e1_info_orig"]["unmapped"] = len(D.ext_unmapped)
    R["E2"] = run_spec("E2_clean_window", assemble(D, [st for st in stacks1 if st["clean_window"]], y_log))
    st_e3 = build_stacks(D, smp, ctrl_extra=D.r1)
    R["E3"] = run_spec("E3_R1_controls", assemble(D, st_e3, y_log))
    R["E5"] = run_spec("E5_no_med_school_only", assemble(D, [st for st in stacks1 if not st["med_only"]], y_log))
    e4 = R["s1"]["E4"]
    say(f"E4 (spec 1): mean(b2..b5) - mean(b-5..b-1, b0=0) = {fm(e4['theta'])} [WCR {fm(e4['lo'])}, {fm(e4['hi'])}], "
        f"CR1 SE {fu(e4['se'])}, MDE {fu(e4['mde'])}")

    head("VERDICT (pre-specified rule, spec 1, log completions)")
    R["verdict"] = R["s1"]["label"]
    say(f"VERDICT: {R['verdict']}")
    write_outputs(R)
    say(f"(peak RSS printed to stderr)")
    print(f"peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MB", file=sys.stderr)


def est_rows(R) -> pd.DataFrame:
    rows = []

    def add(spec, quantity, r, extra=None):
        rows.append(dict(spec=spec, quantity=quantity, estimate=r["theta"], se_cr1=r["se"], lo_wcr=r["lo"],
                         hi_wcr=r["hi"], lo_cr1=r["lo_cr1"], hi_cr1=r["hi_cr1"], p_wcr=r["p"], p_cr1=r["p_cr1"],
                         mde=r["mde"], mde_cr1=r["mde_cr1"], mde_dofcell=r["mde_dofcell"], B=r["B"],
                         **(extra or {})))

    for key in ("s1", "s2", "sa", "sb", "E1", "E1_orig", "E2", "E3", "E5") + tuple(f"f_{f}" for f in FIELDS):
        x = R["fields"][key[2:]] if key.startswith("f_") else R[key]
        ex = dict(pre_W=x["pre"]["W"], pre_p_wcr=x["pre"]["p"], pre_p_chi2=x["pre"]["p_chi2"], label=x["label"],
                  label_cr1=x["label_cr1"],
                  stacks=x["S"], treated_inst=x["Gt"], clusters=x["G"], rows=x["N"])
        add(x["name"], "avg t+2..t+5", x["avg"], ex)
        for e in EVT:
            if "path" in x:
                add(x["name"], f"b{e:+d}", x["path"][e])
    add("spec1", "E4 post minus pre mean", R["s1"]["E4"])
    return pd.DataFrame(rows)


def write_outputs(R):
    est = est_rows(R)
    est.to_csv(OUT_EST, index=False, float_format="%.10g")
    s1, s2, sa, sb = R["s1"], R["s2"], R["sa"], R["sb"]
    a1, p1 = s1["avg"], s1["pre"]
    L = []
    A_ = L.append

    def ci(r, d=3):
        return f"[{fm(r['lo'], d)}, {fm(r['hi'], d)}]"

    def line(x, unit="log points"):
        a, p = x["avg"], x["pre"]
        return (f"{fm(a['theta'])} {unit}, 95% CI (WCR inversion) {ci(a)}, CR1 SE {fu(a['se'])}, WCR p(0) = "
                f"{fp(a['p'])}, MDE {fu(a['mde'])}; pre-trend p = {fp(p['p'])} (joint Wald {p['W']:.2f}, 5 df; "
                f"chi2 p {fp(p['p_chi2'])}); {x['S']} stacks, {x['Gt']} treated institutions, {x['G']} clusters")

    rp = R["repeat"]
    st = R["stk"]
    r80 = R["res80"]["strict"]
    A_("# Nobel prizes and bachelor's completions: stacked event study (design C)")
    A_("")
    A_("Script: `scripts/82_nobel_event_study.py` (seeded with numpy SeedSequence; outputs byte-identical on re-run). "
       "Run it with `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I -B scripts/82_nobel_event_study.py`. It imports "
       "scripts/80 (events, affiliation crosswalk, completions loader) and does not edit it. Outputs: this file, "
       "`data/interim/nobel_event_study_estimates.csv` (every estimate) and `data/interim/nobel_event_study_stacks.csv` "
       "(one row per stack). Not causal beyond the design's assumptions. Computed by the script "
       f"on {RUN_DATE}.")
    A_("")
    A_(f"**Timing of the rules.** The pre-specification (verbatim from the project owner; md5 `{R['md5s']['pre']}`) "
       f"was written into the script docstring and into this file on {RUN_DATE} before any outcome data were read. "
       f"The operational definitions O1-O10 and the exploratory list E1-E5 (md5 `{R['md5s']['op']}`) were added the "
       "same day, also before any outcome data were read, after two kinds of look: CAUSAL_FEASIBILITY.md and "
       "scripts/80 (event counts and projected MDEs, no effects), and which CIP codes exist in each completions file "
       "(and how many institutions report each; no completion counts). Both timing claims are self-reported: the script was not committed or hashed in git before the "
       "estimating run. Everything not in either block is labelled exploratory. Revision 1 "
       "was made the same day after the results had been seen, once an independent re-computation had reproduced the "
       "spec 1 estimate and its WCR interval; its three changes are listed under 'Revision 1' below. It "
       "changes the exploratory E1 screen and adds text; the pre-specification, the operational definitions, the "
       "verdict and every pre-specified estimate are unchanged.")
    A_("")
    A_("## Answer")
    A_("")
    pct = 100 * (np.exp(a1["theta"]) - 1)
    A_(f"**Key question: does a Nobel prize to a member of a department draw more students into that field at that "
       f"university?** Pre-set verdict (spec 1, log bachelor's completions): **{R['verdict']}**. The average effect "
       f"over t+2..t+5, relative to year t, is {fm(a1['theta'])} log points (about {pct:+.1f}%), with 95% CI "
       f"(WCR inversion) {ci(a1)} and MDE {fu(a1['mde'])}. The joint pre-trend test (t−5..t−1) gives p = "
       f"{fp(p1['p'])}. The sample is {s1['S']} clean events at {s1['Gt']} institutions, with "
       f"{st['nctrl_med']} control cells in the median stack.")
    if R["verdict"] == "invalid (pre-trend)":
        A_(f"Because the pre-trend p is below {PRE_ALPHA:.2f}, the rule classifies the design as invalid for this "
           "sample: the prize departments' completions were already moving differently from the controls' before the "
           "prize, so the post-prize average is not read as an effect.")
    elif R["verdict"] == "underpowered":
        A_(f"The CI includes 0 and the MDE exceeds {BENCH:.2f}. Effects up to about {fu(a1['mde'])} log points, in "
           "either direction, are therefore not ruled out at the pre-set power.")
    elif R["verdict"] == "null":
        A_(f"The CI includes 0 and the MDE is at most {BENCH:.2f}. An average effect of {fu(a1['mde'])} log points "
           "would have been detected with 80% power, and none is found.")
    else:
        A_(f"The CI lies {'above' if R['verdict'] == 'positive' else 'below'} 0.")
    A_(f"The CI excludes average effects above {fm(a1['hi'])} log points (about {100 * (np.exp(a1['hi']) - 1):+.1f}%) "
       f"and below {fm(a1['lo'])} (about {100 * (np.exp(a1['lo']) - 1):+.1f}%). The rule's 'fewer than 50 clusters' was "
       f"applied to the {s1['Gt']} treated institutions (O6). Read literally, the count is the {s1['G']} institution "
       f"clusters, and CR1 inference would apply: CI [{fm(a1['lo_cr1'])}, {fm(a1['hi_cr1'])}], chi2 pre-trend p "
       f"{fp(p1['p_chi2'])}, MDE {fu(a1['mde_cr1'])}, label **{s1['label_cr1']}**"
       f"{' (the same)' if s1['label_cr1'] == R['verdict'] else ' (different)'}. The triple difference, which "
       f"nets out institution-wide changes, gives {fm(s2['avg']['theta'])} {ci(s2['avg'])}.")
    oth = [("spec 2", s2), ("(b) spillover", sb)] + [(f"{FNAME[f]} (descriptive)", x) for f, x in R["fields"].items()] + \
          [(f"{k} (exploratory)", R[k]) for k in ("E1", "E2", "E3", "E5")]
    excl = [lab for lab, x in oth if x["avg"]["lo"] > 0 or x["avg"]["hi"] < 0]
    lo_ = min(oth, key=lambda z: z[1]["avg"]["theta"])
    hi_ = max(oth, key=lambda z: z[1]["avg"]["theta"])
    A_(f"Of the {len(oth)} other log-point averages (spec 2, (b), the four fields, E1-E3 and E5), "
       f"{len(excl)} have a WCR CI that excludes 0{(': ' + ', '.join(excl)) if excl else ''}. The lowest is "
       f"{lo_[0]} at {fm(lo_[1]['avg']['theta'])} {ci(lo_[1]['avg'])} and the highest {hi_[0]} at "
       f"{fm(hi_[1]['avg']['theta'])} {ci(hi_[1]['avg'])}. The share outcome (a) gives "
       f"{fm(sa['avg']['theta'])} percentage points {ci(sa['avg'])}.")
    A_("")
    A_("**Scope (revision 1, added after the results had been seen).** IPEDS year y covers July y−1 to June y. A student who "
       "first enrols in autumn t+1, after the October-t announcement, can complete a four-year degree in IPEDS year "
       "t+5 at the earliest, and many take longer. Graduates in t+2..t+4 were all enrolled before the prize, and "
       "in t+5 only the on-time graduates of the first post-prize entering class appear. The t+2..t+5 window "
       "therefore mainly measures whether students already enrolled when the prize was announced chose or switched "
       "into the field. The null applies to that channel only. Whether a prize draws more new entrants to the "
       "university and field is not tested, because most of them graduate after t+5, outside the pre-set window.")
    A_("")
    items = []
    items.append(
        f"**Sample.** The sample is the 88 clean events imported from scripts/80 (prize in t, no prize in the same "
        f"cell in t−5..t−1, completions in t−4..t+5) at 42 institutions, one stack per event. "
        f"{st['T11']} stacks have all 11 years. {st['T10']} have 10, because t−5 is missing"
        + (f": in {st['no5_file']} the 1991 file does not exist, and in {st['no5_zero']} the treated cell has no "
           f"graduates in t−5. " if st['no5_zero'] else f" (1991, for which there is no file). ")
        + f"The median "
        f"stack has {st['nctrl_med']} control cells (min {st['nctrl_min']}, max {st['nctrl_max']}). Across all "
        f"stacks there are {s1['G']} institution clusters, {s1['Gt']} of them treated, and {s1['N']:,} cell-years. "
        f"Treated departments are large: median {st['tsize_med']:.0f} bachelor's completions in year t (range "
        f"{st['tsize_min']:.0f}-{st['tsize_max']:.0f}), against {st['csize_med']:.0f} for the median control cell. "
        f"In year t the median treated department accounts for {st['share_med']:.2f}% of its institution's "
        f"bachelor's completions.")
    items.append(f"**Spec 1 (primary).** θ = {line(s1)}. Verdict: **{R['verdict']}**.")
    dd = R["ddd_drop"]
    items.append(f"**Spec 2 (triple difference, field vs the rest of the institution).** θ = {line(s2)}. The same "
                 f"rule would give: {s2['label']} (no separate verdict). {sum(dd.values())} control cells of spec 1 "
                 f"are dropped here, because the institution had no bachelor's completions outside the field in some "
                 f"stack year, so log(rest) is undefined ("
                 + ", ".join(f"{FNAME[f]} {n}" for f, n in dd.items() if n) + "). This departs from O5's 'same cells'.")
    pe = [(lab, x) for lab, x in (("spec 1", s1), ("spec 2", s2), ("(a)", sa), ("(b)", sb))]
    items.append("**Event-time path** (table below). Individual coefficients whose 95% CI excludes 0: " + "; ".join(
        f"{lab}: " + (", ".join(f"e = {e:+d} ({fm(x['path'][e]['theta'])} {ci(x['path'][e])})" for e in x["n_path_excl0"])
                      if x["n_path_excl0"] else "none") for lab, x in pe)
        + f". That is {sum(len(x['n_path_excl0']) for _, x in pe)} of {10 * len(pe)} coefficients; about "
          f"{0.05 * 10 * len(pe):.0f} are expected at the 5% level if every coefficient were 0. The pre-registered "
          f"tests are the average and the joint pre-trend test.")
    items.append(f"**Secondary (a): share of the institution's bachelor's completions.** θ = "
                 f"{line(sa, 'percentage points')}. Label: {sa['label']}. The 0.10 MDE rule is in log points and does "
                 f"not apply.")
    chs = "; ".join(f"{FNAME[x['field']]} → {x['pick'][1]} ({x['pick'][2]} of {x['n_events']} events offered it in "
                    f"every stack year)" for x in R["sel"])
    items.append(f"**Secondary (b): most closely related field (spillover).** Fields chosen by the O8 availability "
                 f"rule: {chs}. {R['b_tab']['n']} of the 88 events enter: {R['b_tab']['excluded']} are excluded by the "
                 f"own-prize rule and {R['b_tab']['not_offered']} lack the related field in some stack year. θ = "
                 f"{line(sb)}. The same rule would give: {sb['label']} (no separate verdict).")
    fb = "; ".join(f"{FNAME[f]} {fm(x['avg']['theta'])} {ci(x['avg'])} (pre-trend p {fp(x['pre']['p'])}, chi2 "
                   f"{fp(x['pre']['p_chi2'])}; {x['S']} stacks at {x['Gt']} institutions)" for f, x in R["fields"].items())
    gts = [x["Gt"] for x in R["fields"].values()]
    items.append(f"**Prize-field breakdowns (descriptive only; WCR CIs).** {fb}. With {min(gts)}-{max(gts)} treated "
                 f"institutions per field, the WCR and the CR1 chi2 pre-trend p-values can differ widely.")
    e4 = s1["E4"]
    si = R["supp"]
    items.append(
        f"**Exploratory (no verdict).** "
        f"E1, extended prize screening (revision 1, added after the results had been seen): {R['e1_info']['mapped']} prizes from "
        f"1990-94 and 2019-23 are mapped. These are the {R['e1_info_orig']['mapped']} from the imported table plus "
        f"{si['new_events']} new prizes in {si['new_cells']} new cells from the {si['rows']} SUPP_AFF rows; "
        f"{', '.join(si['already'])} was already mapped through another laureate's affiliation. "
        f"{R['e1_info']['dropped_events']} event{'s' if R['e1_info']['dropped_events'] != 1 else ''} and "
        f"{R['e1_info']['ctrl_lost']} control cell-stacks are dropped. The result is {fm(R['E1']['avg']['theta'])} "
        f"{ci(R['E1']['avg'])}, pre-trend p {fp(R['E1']['pre']['p'])}. The first run, with the imported table only "
        f"({R['e1_info_orig']['ctrl_lost']} control cell-stacks dropped), gave {fm(R['E1_orig']['avg']['theta'])} "
        f"{ci(R['E1_orig']['avg'])}. The {R['e1_info']['unmapped']} affiliations still unmapped are listed in the "
        f"script output. Prizes before 1990 are not screened anywhere (revision 1, added after the results had been seen): a "
        f"department with an earlier prize counts as never treated. "
        f"E2, events clean over the whole window ({R['E2']['S']} stacks): {fm(R['E2']['avg']['theta'])} "
        f"{ci(R['E2']['avg'])}, pre-trend p {fp(R['E2']['pre']['p'])}. "
        f"E3, R1 controls only (median {int(np.median(R['E3']['n_ctrl']))} per stack): {fm(R['E3']['avg']['theta'])} "
        f"{ci(R['E3']['avg'])}, pre-trend p {fp(R['E3']['pre']['p'])}. "
        f"E4, the post mean minus the pre mean, spec 1: {fm(e4['theta'])} {ci(e4)}, MDE {fu(e4['mde'])}. "
        f"E5, without medical-school-only events ({R['E5']['S']} stacks): {fm(R['E5']['avg']['theta'])} "
        f"{ci(R['E5']['avg'])}, pre-trend p {fp(R['E5']['pre']['p'])}.")
    items.append(
        f"**Power against the feasibility projection.** scripts/80 projected an MDE of {r80['mde_inst']:.3f} with "
        f"institutions as units and {r80['mde_r1']:.3f} with events as units. The realised spec 1 MDE is "
        f"{fu(a1['mde'])}. It is computed as (q + 0.842) × SE_CR1, where q = {a1['q95']:.2f} is the 95% quantile of "
        f"|t*| from the WCR bootstrap. Revision 1, added after the results had been seen: if the CR1 degrees of freedom are also "
        f"reduced for the {s1['C']:,} cell fixed effects (instead of treating them as nested in the clusters), the MDE "
        f"is {fu(a1['mde_dofcell'])}. The verdict is unchanged ({s1['label_dofcell']}); the WCR p-values and CI do "
        f"not depend on this factor.")
    items.append(
        f"**What the outcome measures.** Completions measure quantity, not the quality of entrants. A prize could "
        f"change who enrols in a field without changing how many graduate, and these data cannot see that. Repeat "
        f"winners cluster at a few elite universities. Of the 134 events in 1995-2018, {rp['top5_134']} "
        f"({rp['top5_134'] / rp['n134']:.0%}) are at five institutions: "
        f"{', '.join(f'{n} {c}' for n, c in zip(rp['top5_names'], rp['top5_counts']))}"
        + (f" ({rp['tie5_134']} institutions share the fifth-ranked count of {rp['k5_134']}; ties are broken "
           f"alphabetically)" if rp['tie5_134'] > 1 else "") + f". {rp['inst_ge3']} of the {rp['ninst134']} "
        f"institutions have 3 or more events and {rp['inst_1']} have one. "
        f"{rp['multi']} of {rp['cells']} cells have more than one prize (up to {rp['maxc']}). In the 88-event sample "
        f"the five institutions with the most events hold {rp['top5_88']} events ({rp['top5_88'] / 88:.0%}): "
        f"{', '.join(f'{n} {c}' for n, c in zip(rp['top5_88_names'], rp['top5_88_counts']))}"
        + (f" ({rp['tie5_88']} institutions share the fifth-ranked count of {rp['k5_88']}; ties are broken "
           f"alphabetically)" if rp['tie5_88'] > 1 else "") + ". Their departments are "
        f"large and may be capacity-limited, and the treated set is not a random draw of departments.")
    ck = R["check"]
    items.append(
        f"**Checks.** The four prize-field series equal s80.load_completions exactly. The institution total (all CIP "
        f"rows except 99) equals the CIP 99 grand-total row in {R['denom']['agree']:.4f} of institution-years that "
        f"have one; the lowest year is {R['denom']['min_year'][1]} ({R['denom']['min_year'][0]:.3f}). Of the "
        f"{R['denom']['bad_all']} disagreeing institution-years, {R['denom']['bad1990']} are in 1990, which lies in "
        f"no stack (the earliest stack year is {R['denom']['first_win']}), and {R['denom']['only95']} report only "
        f"CIP 95 rows (95.0000 and 95.9500, so the sum counts them twice). These have no field completions and "
        f"never enter a stack. Over the {R['denom']['used99']} institution-years that do enter the spec 1 stacks, "
        f"agreement is {R['denom']['used_agree']:.4f} ({R['denom']['used_bad']} disagree). The fast WCR "
        f"algebra matches brute-force dummy regressions with explicit bootstrap samples on a {ck['N']}-row "
        f"subsample: max differences are {ck['d_beta']:.0e} (β), {ck['d_se']:.0e} (CR1 SE), {ck['d_t']:.0e} "
        f"(bootstrap t) and {ck['d_W']:.0e} (bootstrap Wald, relative).")
    for k, it in enumerate(items, 1):
        A_(f"{k}. {it}")
    A_("")
    A_("## Key numbers")
    A_("")
    A_("θ = mean of the event-time coefficients for t+2..t+5, relative to year t (e = 0). CI = inversion of the wild "
       f"cluster restricted bootstrap test (Webb weights, {B_MAIN} replicates, clusters = institutions). p(0) = WCR "
       f"bootstrap p of θ = 0. Pre-trend p = WCR bootstrap p of the joint Wald test of b−5..b−1 = 0 ({B_MAIN} "
       "replicates). MDE = (q + 0.842) × SE_CR1 (80% power, 5% two-sided). Units: log points, except share "
       "(percentage points). 'Label, CR1 reading' is post hoc: the rule applied with the CR1 CI, the chi2 pre-trend p "
       "and MDE = (t_.975 + 0.842) × SE_CR1, i.e. the literal count of all institution clusters (>= 50).")
    A_("")
    A_("| spec | outcome | θ | 95% CI (WCR) | CR1 SE | CR1 95% CI | p(0) | pre-trend p | MDE | label | "
       "label, CR1 reading | stacks | treated inst. | clusters |")
    A_("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    def row(lab, outc, x, label=None, show_cr1=True):
        a, p = x["avg"], x["pre"]
        A_(f"| {lab} | {outc} | {fm(a['theta'])} | {ci(a)} | {fu(a['se'])} | [{fm(a['lo_cr1'])}, {fm(a['hi_cr1'])}] | "
           f"{fp(a['p'])} | {fp(p['p'])} | {fu(a['mde'])} | {label or x['label']} | {x['label_cr1'] if show_cr1 else '—'} | {x['S']} | "
           f"{x['Gt']} | {x['G']} |")

    row("spec 1 (primary, verdict)", "log completions", s1, f"**{R['verdict']}**")
    row("spec 2 (triple difference)", "log(field) − log(rest)", s2, f"{s2['label']} (rule shown, no verdict)")
    row("(a) share", "100 × field / total", sa)
    row("(b) spillover", "log related-field completions", sb, f"{sb['label']} (rule shown, no verdict)")
    for f, x in R["fields"].items():
        row(f"field: {FNAME[f]} (descriptive)", "log completions", x, "descriptive", show_cr1=False)
    for k, lab in (("E1", "E1 extended prize screening (revision 1, post hoc)"),
                   ("E1_orig", "E1 as first run (imported table only)"), ("E2", "E2 clean over t−5..t+5"),
                   ("E3", "E3 R1 controls only"), ("E5", "E5 without medical-school-only events")):
        row(f"{lab} (exploratory)", "log completions", R[k], "exploratory", show_cr1=False)
    A_("")
    A_("## Event-time path")
    A_("")
    A_(f"Coefficients relative to year t (e = 0, the last academic year that ends before the October "
       f"announcement). CIs from WCR inversion, {B_PATH} replicates each. n = stacks observing that event time.")
    A_("")
    A_("| e | spec 1 | spec 2 (DDD) | (a) share, pp | (b) spillover | n (spec 1) |")
    A_("|---|---|---|---|---|---|")
    for e in EVT:
        cells_ = [f"{fm(x['path'][e]['theta'])} {ci(x['path'][e])}" for x in (s1, s2, sa, sb)]
        A_(f"| {e:+d} | " + " | ".join(cells_) + f" | {s1['n_e'][e]} |")
    A_("")
    A_("## Method")
    A_("")
    A_("- **Events.** `s80.design_c` gives 134 institution × field × year prizes (nobelprize.org affiliation at award "
       "time, 1995-2018, US degree-granting institutions; medical schools mapped to the parent university). The "
       "sample is its 88 events with completions in t−4..t+5 and no prize in the cell in t−5..t−1.")
    A_("- **Outcome.** IPEDS bachelor's (AWLEVEL 5) first-major completions, from the annual C files used by "
       "scripts/80, with the same grand-total column rule. Physics 40.08, chemistry 40.05, economics 45.06, and "
       "medicine mapped to all of biology (CIP 26). Year y is the academic year ending in June y.")
    A_("- **Stacks.** Years t−5..t+5 with a file and a positive treated cell. Controls are the same field at US "
       "institutions (50 states + DC) with positive completions in every stack year and no prize in that cell up to "
       "t+5 (never treated, or not yet treated). Every stack is balanced.")
    A_("- **Regression.** OLS on ten event-time dummies (reference e = 0), with stack × cell and stack × year effects, "
       "via the exact two-way within transformation per stack. θ = (b2 + b3 + b4 + b5) / 4.")
    A_("- **Inference.** Errors are clustered by institution. With one treated cell per stack, the number of treated "
       f"institutions ({s1['Gt']}) is the cluster count that governs inference, and it is below 50, so wild cluster "
       "restricted bootstrap-t (Webb six-point weights) is used, with CIs by test inversion. The bootstrap is "
       "computed exactly from cluster-level aggregates: with the restricted residuals e_r, the FE-orthogonal score "
       "vector u = X̃(X̃'X̃)⁻¹c and the stack × year dummies Z, each replicate's θ* and CR1 variance are linear and "
       "quadratic forms in the cluster weights. CR1 uses the factor G/(G−1)·(N−1)/(N−K), with K = 10 + Σ(T_s − 1); "
       "cell effects are nested in clusters.")
    A_("- **Spec 2.** DiD on log(field) − log(rest of the institution's bachelor's completions). This equals the "
       "triple difference with stack × institution × year and stack × (field or rest) × year effects.")
    A_("- **Secondary.** (a) 100 × field / institution total (all CIP rows except 99). (b) The related field is "
       "picked by the O8 availability rule, from candidates ordered by closeness. When the related CIP belongs to "
       "another prize field's outcome, own-prize exclusions apply on both the treated and control side.")
    A_("")
    si = R["supp"]
    A_("## Revision 1, added after the results had been seen")
    A_("")
    A_("Made on the run date after the results had been seen. An independent re-computation reproduced the spec 1 estimate "
       "and its WCR interval; three minor changes followed. Each is labelled 'revision 1' "
       "where it appears above, and in the script.")
    A_("")
    A_(f"1. **E1 mapping.** {si['rows']} US prize-affiliation rows that the imported NOBEL_AFF table lacks are now "
       f"mapped (script table SUPP_AFF): " + "; ".join(si["list"]) + ". Each was checked against the affiliation "
       "string and city in the on-disk nobelprize.org file and the IPEDS directory name. 'City University of New "
       "York' (Markowitz, 1990) is mapped to Baruch College. Baruch's Zicklin School of Business states that he was "
       "Marvin Speiser Distinguished Professor of Finance and Economics there when he won the prize "
       "(zicklin.baruch.cuny.edu, 'Nobel Winner Harry Markowitz, Former Zicklin Professor, Dies'); nobelprize.org "
       "itself refused scripted requests. "
       f"E1 is now {fm(R['E1']['avg']['theta'])} {ci(R['E1']['avg'])} ({R['e1_info']['ctrl_lost']} control "
       f"cell-stacks dropped), against {fm(R['E1_orig']['avg']['theta'])} {ci(R['E1_orig']['avg'])} "
       f"({R['e1_info_orig']['ctrl_lost']}) in the first run.")
    A_("2. **Scope.** The t+2..t+5 window mainly captures students who were already enrolled when the prize was "
       "announced. The null applies to that channel, not to new entrants (paragraph 'Scope' in the Answer).")
    A_(f"3. **Notes.** With the cell fixed effects also counted in the CR1 degrees of freedom, the spec 1 MDE is "
       f"{fu(s1['avg']['mde_dofcell'])}, and the verdict is unchanged. Prizes before 1990 are not screened anywhere.")
    A_("")
    A_(f"## Pre-specification (verbatim; md5 of the block `{R['md5s']['pre']}`)")
    A_("")
    A_(R["pre_txt"].rstrip())
    A_("")
    A_(f"## Operational definitions and exploratory list (verbatim; md5 of the block `{R['md5s']['op']}`)")
    A_("")
    A_("```")
    A_(R["op_txt"].rstrip())
    A_("```")
    txt = "\n".join(L) + "\n"
    OUT_MD.write_text(txt)
    say("\n" + "=" * 100 + "\nNOBEL_RESULT.md as written:\n" + "=" * 100)
    print(txt, flush=True)


if __name__ == "__main__":
    main()
