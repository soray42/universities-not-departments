r"""scripts/78_gap_checks.py -- four gap checks (G1-G4): the US department slope net of PhD production, the CS sample
gap, the UK/US triad in one statistic at both levels with reliability ceilings, and a coefficient-stability bound on
the UK department slope.

The block between the PRESPEC marker lines is the binding text, copied verbatim; it was fixed on 2026-11-14
before any data were read for this script. The block between the CHOICES marker lines records implementation choices
made the same day, after reading the code and the existing write-ups (SELECTIVITY_DEEP_RESULT.md, UK_TRIAD_RESULT.md,
THEORY_TESTS_RESULT.md section T0, CS_ADMISSION_RESULT.md including its table of the top-50 CS departments missing
from the scripts/58 sample) and before the first data run of this script. main() refuses to run if the SHA-256 of
either block differs from PRESPEC_SHA256 / CHOICES_SHA256. Anything not named in either block is labelled exploratory.

General rules (not part of the binding tests): public data only, all already on disk; every number in
GAP_CHECKS_RESULT.md is printed by this script; seeded and byte-identical on a second run; existing scripts imported,
never edited; descriptive, non-causal language; nulls reported with their MDE.

-----BEGIN PRESPEC-----
G1 — US department slope net of PhD production. Re-estimate the scripts/58 main within-institution specification (same programmes, same controls, same inference) with F replaced by (a) F residualised on production as in scripts/75 T0, (b) the degree-corrected F of scripts/75. Report the slope per SD, its CI, the MDE (2.8 SE), and the change from the original slope with a paired interval. Rule: "robust to production" if the paired change CI includes 0 and the new point estimate is >= half the original; "production-driven" if the new CI upper bound is below half the original; otherwise "inconclusive". Also report the CS remainder under (a) and (b).

G2 — CS sample gap. First diagnose why the 21 highest-ranked CS departments are missing (for each: is it missing from Wapman, from Scorecard FoS earnings, from the name join, or dropped for missing SAT_AVG/ADM_RATE in the 2026 institution file?). Print the table. If the main cause is missing selectivity and scripts/68's era-matched SAT/ADM restores them, re-estimate the CS remainder on the enlarged sample (same spec otherwise) and report old vs new with intervals. If the gap cannot be fixed with data on disk, say so and stop G2 there. Do not guess any institution's status.

G3 — Triad in one statistic at both levels, with reliability ceilings. UK (scripts/76 cells): compute both across-university-within-subject and within-university (provider and subject fixed effects removed) agreement for the three pairs (REF-pay, REF-intake, pay-intake) using the SAME statistic at both levels: Pearson correlation of rank-normal scores (normal scores within subject for the across level; residualised normal scores for the within level). Use the intake band score or the 'low'=1 recode as the primary intake measure (state which; 'low'=0 as sensitivity), because the zero floor attenuates within-university correlations. Disattenuate each within-university correlation by the within-university reliabilities: REF from the REF2014-REF2021 within-provider test-retest (0.536 or recomputed), pay from scripts/73-style median sampling noise, intake from cohort-to-cohort within-provider stability if computable (state the assumption; if not computable, report the ceiling with intake reliability = 1 and flag it). Cluster bootstrap by provider (2,000 replicates). Rule, per pair: "agree less within universities" only if the upper bound of the disattenuated within-university correlation is below the point estimate of the across-university correlation; "cannot distinguish" otherwise. US analogue (F-pay only; US intake exists only at institution level): within-institution correlation of residualised F with residualised pay on the scripts/58 sample, disattenuated by the residual-F reliability scripts/58/56 report (~0.3 at the lower bound), versus the across-institution within-field coupling; same rule.

G4 — Bound on the UK department slope (optional row). Oster (2019) delta-style bound for the scripts/76 within-university REF slope using the programme intake measure as the observed control (R_max = 1.3 x R-squared of the controlled model, and R_max = 1 as a sensitivity). Label it a bound under named assumptions, not a causal estimate.
-----END PRESPEC-----

-----BEGIN CHOICES-----
C0. Reproduction first. Every design is rebuilt from the imported functions of scripts/55, 58, 68, 73, 75 and 76 and
    checked against their published numbers before anything is changed: scripts/58 main spec FE2 +0.0084
    [+0.0000, +0.0164] (2,889 programmes, 168 institutions, 47 fields); CS remainder +0.050 [+0.012, +0.096]
    (128 programmes; the 4/1/5-year average of the main-spec per-field beta_f on the common programmes); scripts/75 T0
    means Spearman(F, p) +0.441 and, on the scripts/28 common cells, mean c_F +0.387, c_DC +0.325, c_perp +0.232;
    scripts/76 within-provider triad +0.109 / +0.146 / +0.261 (864 programmes), T4 Spearman means +0.580 / +0.643 /
    +0.694, REF test-retest +0.536 (814 programmes), intake-control slopes +0.0187 -> +0.0075.
C1. G1 variants. (a) F_perp = residual of rank(F) on rank(p) and rank(x) over each Wapman field's ranked institutions
    with p (scripts/75 T0(b) exactly; p = log(1 + IPEDS research doctorates), x = log((d_out+1)/(d_in+1))). (b) F_DC =
    theta of scripts/75's degree-corrected Bradley-Terry fit with the +1 degree convention (T0's primary), entered as
    its within-field rank among the field's ranked institutions in the public network (like-for-like with F, an
    ordinal rank); raw theta is a sensitivity. Each enters fe_build in place of prestige_score and is z-scored within
    field on the sample, as F is. Cells: the main-spec cells restricted to programmes where F, F_perp and F_DC all
    exist, then scripts/58's sample rules re-applied; 'original' in the rule is F on these identical cells (the
    full-sample value is printed beside it), so every variant shares cells and bootstrap draws. Inference: scripts/58's
    own institution cluster bootstrap (fe_group_boot, seed [58, 3, 1], B = 999), so the original interval reproduces
    and the change is paired; SE = SD of the draws; MDE = 2.80 SE; the MDE of the paired change is printed as well.
    One verdict per variant. CS remainder: scripts/58's per-field main spec on the common programmes at 4, 1 and 5
    years, fe_boot_pf seed [58, 11], B = 999, a field counted in a draw with >= 8 distinct institutions, the three
    horizons averaged per draw; same coverage restriction; the CS change is paired.
C2. G2. The 50 highest-ranked Wapman CS departments are ranked by prestige_score among departments with one; a
    department is missing if it is not in the CS rows of the CS-remainder sample (common programmes). Each missing
    department gets the first stage at which it fails, in pipeline order: (1) Wapman (no field rank, or no academia
    rank G), (2) Scorecard FoS (no bachelor's CS row with a released 4-year median under any name rule), (3) name join
    (a CS row with a released 4-year median exists under the scripts/34 campus or city rules; or, with no rule match,
    a row found by a printed token search, listed as such), (4) 2026 selectivity (SAT_AVG, ADM_RATE or PCTPELL
    missing: the institution controls fe_build requires for the main spec), (5) 1-year or 5-year median not
    released, (6) scripts/58 sample rules. Secondary flags (2026 SAT_AVG and era-matched SAT_AVG of the matched
    UNITID) are printed for every row. Main cause = the largest of the stage categories (the three name-join kinds
    pooled). The branch fires only if the main cause is stage (4) and scripts/68's version-E controls exist for those
    departments. If it fires: CS remainder with version-E SAT_AVG, ADM_RATE and PCTPELL (scripts/68 era_table, falls
    2014-15) for every institution, reported as 2026 controls on the old sample, E on the programmes complete under
    both, and E on the enlarged sample. If it does not fire, the same re-estimate is run as an exploratory, partial
    row. The name join is not repaired (a join-rule change, not 'same spec otherwise').
C3. G3 UK. Cells: scripts/76's T3(a) cells (clean subjects; ref_gpa, pay, top, score known; >= 15 providers per
    subject; singletons dropped iteratively; 864 programmes). Primary intake = the share with >= 360 points with
    'low' band cells coded as 1 graduate (same construct as scripts/76's S-LEO; the zero floor falls from 47% to 13%
    of programmes); 'low' = 0 is the pre-specified sensitivity; the band score ('low' = 1) is exploratory. Normal
    scores: Blom, midranks for ties, within subject over the cells, then standardised to mean 0, SD 1 within subject;
    computed once and held fixed in the bootstrap. Across = Pearson of the normal scores over all cells (subject means
    removed); within = Pearson of their residuals on provider + subject fixed effects (scripts/76 fe_resid). Checks:
    across on the T4 cells; mean over subjects of the per-subject Pearson.
    Reliabilities of the within-level residuals: REF = within-provider correlation of the residualised normal scores of
    REF 2021 and REF 2014 GPA on the cells with both (subjects >= 15 providers, singletons dropped), read as a
    test-retest reliability (assumes parallel measures of a stable standing; real change lowers it and raises the
    disattenuated value). Pay = 1 - sum_i s2_i M_ii / sum_i e_i^2, with e the FE residual of the pay normal score,
    M_ii = 1 - leverage of the provider + subject FE design, and s2_i the scripts/73-style noise variance of the
    programme's mean log median: per cohort SE = 1.2533 (UQ - LQ) / 1.349 / sqrt(n) / median with n =
    grads_earnings_include (where a cohort's quartiles are not released, the subject's median relative IQR), summed
    over the K released cohorts / K^2, converted to normal-score units by dividing by the within-subject variance of
    pay (delta method under within-subject normality). Intake = odd/even cohort split-half (cohorts 2013+2015 vs
    2014+2016, pooled counts, same 'low' coding), normal scores within subject, within-provider correlation r_h of
    the residuals on the cells with both halves defined, Spearman-Brown 2 r_h / (1 + r_h) (assumes the halves are
    parallel with independent errors and the programme's intake is stable over the four cohorts). Disattenuated
    within r_c = r / sqrt(rel_x rel_y); ceiling = sqrt(rel_x rel_y). Bootstrap: 2,000 provider cluster replicates
    (a provider drawn twice enters as two providers); every reliability and correlation is recomputed in each
    replicate; a replicate in which a needed reliability is <= 0 or undefined gets r_c = +inf (it counts on the
    'cannot distinguish' side and is not dropped; the count is printed). Upper bound = 97.5th percentile.
    Pay and intake come from the same LEO rows, so their errors may be correlated (caveat).
    G3 US. Cells: scripts/58's main-spec cells (2,889). Normal scores within field of F and log pay (as above).
    Across = pooled Pearson. Within (primary) = residuals on institution FE + field FE + field x {zSAT, zADM,
    zPCTPELL, zG} (the main design of fe_build). Residual-F reliability = scripts/58's lambda (fe_fit formula, relF_LB
    of scripts/56) computed on this design, so it belongs to the residual that is correlated; lambda_EXT is a
    sensitivity. The rule uses r / sqrt(lambda_LB) (pay reliability 1, as the binding text names only F); a version
    that also divides by sqrt(rel_pay) (scripts/73 se_main of each programme, same formula as the UK pay reliability)
    is exploratory, and so is the institution + field FE-only (UK-parallel) residualisation. Institution cluster
    bootstrap, 2,000 replicates, lambda and rel_pay recomputed in each.
C4. G4. Cells and specification of scripts/76 T2(a) with the intake control (clean subjects, ref_gpa, pay, top;
    subject x z(intake) slopes; 'top' with 'low' = 0, the scripts/76 measure), so the reproduced +0.0187 -> +0.0075 is
    the base; 'low' = 1 is a sensitivity. R-squared = total R-squared with the provider and subject fixed effects
    included (as scripts/58's oster()); short model = provider FE + subject FE + beta z; R_max = min(1, 1.3 R_long)
    and R_max = 1; reported: delta* (beta = 0) and beta*(delta = 1) (Oster's approximation, as scripts/58), with a
    provider cluster bootstrap (2,000) interval for beta*; if 1.3 R_long >= 1 the two rows coincide and this is said.
    The within R-squared version (fixed effects partialled out) is exploratory.
C5. Seeds. G1 and G2 reuse scripts/58's bootstrap functions and seeds (a single generator per specification group, as
    scripts/58 did), which is needed for the original intervals to reproduce and the changes to be paired; this is a
    single process, so it does not depend on a worker count. Every new bootstrap (G3, G4) uses one child of
    numpy SeedSequence(78) per named analysis and one grandchild per replicate. BLAS: 8 threads set before numpy is
    imported; model fits run under threadpool_limits(1). Single process. The result file carries no timings, memory
    figures or run dates.
-----END CHOICES-----

-----BEGIN AMENDMENT A1-----
A1 (2026-11-14, after the first coverage count and before any slope, correlation or bound was computed). On the 2,889
    main-spec programmes F_perp exists for all 2,889 and F_DC for 2,176 (the other departments are ranked by Wapman
    but have no edge in the public field network). Variant (a) is therefore estimated on the full main-spec cells,
    which is the binding text's 'same programmes', with the original on the same cells and the same draws (this is
    the row the G1 rule is applied to for (a)); the C1 common-cell version of (a) is reported beside it as a
    sensitivity. Variant (b) stays on the C1 common cells (F, F_perp and F_DC all exist), with the original
    re-estimated there; its rule is applied there. The CS remainder follows the same split.
-----END AMENDMENT A1-----

REVISION 1 (2026-11-14; added after results were seen; outside the hashed blocks, which are
unchanged). G1: production adjusted inside the scripts/58 design (field x ranks of production and export ratio as
further field-specific slopes; production only), F_perp kept as the pre-specified, flagged variant, and its
within-design correlation with the production rank reported. G2: the kind of name difference is read from the
Scorecard name (Columbia: city qualifier). G3 UK: a simulation-calibrated test of rho_within = rho_between on the real
layout (spawned worker processes, SeedSequence per data set), calibrated estimates of rho_within / rho_between, the
size of the pre-specified rule under the calibrated null, the linear within-subject z version as co-primary, two
robustness subsets, pure between-provider correlations, corrected subset labels. G3 US: lambda with the full
leverage, jackknife intervals for the reliabilities. G4: wording. Every pre-specified verdict is kept.

REVISION 2 (2026-11-14; added after results were seen; outside the hashed blocks). G3 US: the like-for-like FE-only
contrast (institution + field FE within, the plain within-field coupling between), across-level reliabilities, and a
simulation-calibrated test of rho_within = rho_between on the real US layout (F with classical error at the scripts/56
lower-bound reliability, extrapolated as a sensitivity; pay with the scripts/73 noise), with calibrated rho_within /
rho_between and the false-positive rate of the pre-specified rule; the controlled version is kept as the stricter
contrast. G2: whether scripts/59's name aliases (imported) recover the name-join CS departments. No earlier number
or verdict changes.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    # resource rule: 8 in the main process (model fits run under 1 thread); revision 1: 1 in the spawned
    # simulation workers ('__mp_main__'), so their results do not depend on threading
    os.environ[_v] = "1" if __name__ == "__mp_main__" else "8"
import re
import sys
import time
import pickle
import hashlib
import zipfile
import warnings
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, norm, spearmanr
from threadpoolctl import threadpool_limits

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.wapman_release import with_release_note, v1_assert, is_v1   # 2026 re-baseline (no-op under v1)  # noqa: E402

PRESPEC_SHA256 = "cdae7424a98a7ba1e6389d60dabe06fc3f339ec279c9cac4ab3a97077d29d129"
CHOICES_SHA256 = "505b9e0625761d532d0080464a64809bf2a7e795ba5c5eb922c7ad34d7b98eba"
A1_SHA256 = "9d1a08a172e39c4562438c4f86466e2687e0ad752bb96a54a8dc8528fe64c9cf"


def _block(begin: str, end: str) -> str:
    return __doc__.split(begin + "\n", 1)[1].split(end, 1)[0]


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T0_ = time.time()


def _xtx_stack(X, idx):
    """np.stack([X[r].T @ X[r] for r in idx]) filled into one preallocated array (same values, half the transient
    memory; 2026 re-baseline under a 3 GB address-space cap)."""
    A = np.empty((len(idx), X.shape[1], X.shape[1]))
    for i, r in enumerate(idx):
        A[i] = X[r].T @ X[r]
    return A


def stage(msg: str):
    print(f"[{time.time() - T0_:7.1f}s] {msg}", flush=True)


# revision 1: the G3 calibration simulation runs in spawned worker processes, which import this file as
# '__mp_main__'; they need only numpy / pandas / scipy, so the existing scripts are not loaded there
_WORKER = __name__ == "__mp_main__"
if not _WORKER:
    s58 = _load("s58", "58_selectivity_deep.py")      # within-institution design, bootstrap (not edited)
    s55 = s58.s55
    s75 = _load("s75", "75_theory_tests.py")          # T0: production, export ratio, degree-corrected BT (not edited)
    s76 = _load("s76", "76_uk_triad.py")              # UK panel, REF, LEO (not edited); loads scripts/62
    s62 = s76.s62
    s68 = _load("s68", "68_era_selectivity.py")       # era-matched Scorecard controls (not edited)
    s73 = _load("s73", "73_earnings_reliability.py")  # programme-median noise (not edited)

SEED = 78
B = 2000                                          # G3 / G4 replicates (pre-specified for G3)
Z80 = 0.8416212335729143
MDE_K = 1.959963984540054 + Z80                   # 2.80
CS = "computer_science"
INST_SLOPES = ["SAT_AVG", "ADM_RATE", "PCTPELL"]   # = s58.INST_SLOPES (asserted in main)
MAIN_SLOPES = INST_SLOPES + ["G"]
HZ3 = ["FE2_h3y4", "FE2_h3y1", "FE2_h3y5"]       # main spec per field on the common programmes, 4 / 1 / 5 years
OUT_MD = ROOT / "GAP_CHECKS_RESULT.md"
OUT_CSV = ROOT / "data" / "interim" / "gap_checks_summary.csv"
OUT_GAP = ROOT / "data" / "interim" / "gap_checks_cs_gap.csv"
DEVCACHE = os.environ.get("GAP78_DEVCACHE")       # development shortcut only (pickle dir); reported runs do not set it

# one SeedSequence child per named analysis of the new bootstraps, in this fixed order (names only appended)
ANALYSES = ["g3_uk", "g3_us", "g4",
            # revision 1 (appended: earlier children and draws unchanged)
            "g3_rob", "g3_sim_cal", "g3_sim_null", "g3_sim_size", "g3_sim_alt", "g3_sim_altfin",
            "g3_sim_cal_t0", "g3_sim_size_t0",
            # revision 2 (appended)
            "us_sim_cal", "us_sim_null", "us_sim_size", "us_sim_alt", "us_sim_altfin",
            "us_sim_cal_ext", "us_sim_null_ext", "us_sim_size_ext", "us_sim_alt_ext", "us_sim_altfin_ext"]
_KIDS = dict(zip(ANALYSES, np.random.SeedSequence(SEED).spawn(len(ANALYSES))))


def rep_gens(name: str, n: int | None = None) -> list:
    """One generator per replicate: grandchildren of the analysis' SeedSequence child (B of them by default)."""
    return [np.random.default_rng(s) for s in _KIDS[name].spawn(B if n is None else n)]


def _trim():
    """Return freed heap memory to the OS before worker processes start (revision 2; no effect on results)."""
    import gc
    import ctypes
    gc.collect()
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except OSError:
        pass


def cached(tag: str, fn):
    if DEVCACHE:
        p = Path(DEVCACHE) / f"{tag}.pkl"
        if p.exists():
            with open(p, "rb") as f:
                return pickle.load(f)
        out = fn()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump(out, f)
        return out
    return fn()


def pct(bs, q):
    bs = np.asarray(bs, float)
    return float(np.percentile(bs[~np.isnan(bs)], q))


def summ(est, bs) -> dict:
    """Percentile CI, SE = SD of the draws (NaN draws dropped; +inf draws kept for percentiles only)."""
    bs = np.asarray(bs, float)
    ok = ~np.isnan(bs)
    fin = np.isfinite(bs)
    se = float(np.std(bs[fin], ddof=1)) if fin.sum() > 2 else np.nan
    return dict(est=float(est), lo=float(np.percentile(bs[ok], 2.5)), hi=float(np.percentile(bs[ok], 97.5)),
                se=se, mde=MDE_K * se, nfail=int((~ok).sum()), ninf=int((ok & ~fin).sum()))


def blom(x: np.ndarray) -> np.ndarray:
    """Rank-normal (Blom) scores, midranks for ties."""
    r = rankdata(x)
    return norm.ppf((r - 0.375) / (len(x) + 0.25))


def ns_within(df: pd.DataFrame, col: str, grp: str, ddof: int) -> np.ndarray:
    """Blom scores within group, standardised to mean 0, SD 1 (given ddof) within the group."""
    out = np.empty(len(df))
    for _, ix in df.groupby(grp).indices.items():
        v = blom(df[col].to_numpy(float)[ix])
        out[ix] = (v - v.mean()) / v.std(ddof=ddof)
    return out


def corr(a, b, w=None) -> float:
    if w is None:
        a = a - a.mean(); b = b - b.mean()
        return float(a @ b / np.sqrt((a @ a) * (b @ b)))
    sw = w.sum()
    a = a - (w @ a) / sw; b = b - (w @ b) / sw
    return float((w * a) @ b / np.sqrt(((w * a) @ a) * ((w * b) @ b)))


# =============================================================================================================
# US data: scripts/58 cells (scripts/55 cells + 1-yr / 5-yr medians), as s58.compute() builds them
# =============================================================================================================
def us_cells():
    ar = s58.load_ar_wapman(fields=s58.FIELDS66)
    er = s58.load_er_scorecard("undergrad", fields=s58.FIELDS66)
    inst = s55.load_institutions()
    cells = s55.build_cells(ar, er, inst)
    n0 = len(cells)
    for tag, ec, cc in s58.HORIZONS:
        e = s58.load_er_scorecard("undergrad", earn_col=ec, count_col=cc, fields=s58.FIELDS66)
        cells = cells.merge(e[["inst_key", "field", "earnings", "cohort_n"]].rename(
            columns={"earnings": tag, "cohort_n": f"{tag}_n"}), on=["field", "inst_key"], how="left")
    assert len(cells) == n0 and cells.INSTNM.notna().all()
    return cells, ar, er[er.field == CS].copy(), inst


# =============================================================================================================
# G1: scripts/75 T0 objects (F_perp, F_DC) per Wapman field
# =============================================================================================================
def t0_objects():
    """Per field key: the field's ranked institutions with F (pct), p, x, F_perp (residual of rank(F) on rank(p),
    rank(x)), theta (+1 convention) and its within-field rank among ranked network nodes; exactly scripts/75 T0(b)."""
    e, r = s75.wapman()
    F66 = s58.FIELDS66
    wf2key = {f["wapman_field"]: f["key"] for f in F66}
    fl = sorted(set(e[e.TaxonomyLevel == "Field"].TaxonomyValue.unique()) & set(wf2key))
    doct, sc_keys = s75.ipeds_doctorates(F66)
    out, gmax = {}, 0.0
    for f in fl:
        key = wf2key[f]
        net = s75.field_net("Field", f)
        x = r[(r.TaxonomyLevel == "Field") & (r.TaxonomyValue == f)].copy()
        N = len(x)
        x["F"] = 1.0 - x.Rank / (N - 1)
        x["inst_key"] = x.InstitutionName.map(s75.norm)
        pos = pd.Series(np.arange(net["n"]), index=net["nodes"])
        dout = np.bincount(net["src"], net["tot"], net["n"])
        din = np.bincount(net["dst"], net["tot"], net["n"])
        ni = x.InstitutionId.map(pos)
        x["in_net"] = ni.notna()
        x["dout"] = np.where(ni.notna(), dout[ni.fillna(0).astype(int)], 0.0)
        x["din"] = np.where(ni.notna(), din[ni.fillna(0).astype(int)], 0.0)
        x["x"] = np.log((x.dout + 1) / (x.din + 1))
        dd = doct[doct.field == key].set_index("inst_key").doct
        x["doct"] = x.inst_key.map(dd)
        x.loc[x.doct.isna() & x.inst_key.isin(sc_keys), "doct"] = 0.0
        x["p"] = np.log1p(x.doct)
        th, npairs, uninf, gm = s75.bt_offset(net["A"])
        gmax = max(gmax, gm)
        x["theta"] = x.InstitutionId.map(pd.Series(th, index=net["nodes"]))
        x["theta_rank"] = np.nan
        m = x.theta.notna()
        x.loc[m, "theta_rank"] = s75.rk(x.loc[m, "theta"].to_numpy(float))
        xr = x.dropna(subset=["p"])
        x["Fperp"] = np.nan
        if len(xr) >= s75.MIN_INST_T1:
            Xd = np.column_stack([np.ones(len(xr)), s75.rk(xr.p), s75.rk(xr.x)])
            yF = s75.rk(xr.F)
            x.loc[xr.index, "Fperp"] = yF - Xd @ np.linalg.lstsq(Xd, yF, rcond=None)[0]
        rp = s75.spear(xr.F, xr.p) if len(xr) >= s75.MIN_INST_T1 else np.nan
        out[key] = dict(x=x, wf=f, r_p=rp)
    return out, gmax


def t0_reproduce(T0):
    """scripts/75 T0(a) mean Spearman(F, p) and T0(b) mean c_F, c_DC, c_perp on the scripts/28 common cells."""
    rp = [v["r_p"] for v in T0.values() if np.isfinite(v["r_p"])]
    s28 = s75.mod("s28")
    t = s28.build_table()
    wf2key = {f["wapman_field"]: f["key"] for f in s28.FIELDS66}
    key2wf = {v: k for k, v in wf2key.items()}
    t = t[t.field.isin(set(key2wf))]
    counts = t.groupby("field").size()
    e, _ = s75.wapman()
    an = s75.field_net("Academia", "Academia")
    gth, *_ = s75.bt_offset(an["A"])
    akey = pd.Series([s75.norm(nm) for nm in an["names"]], index=an["nodes"])
    GDC = pd.Series(gth, index=akey.values)
    GDC = GDC[~GDC.index.duplicated()]
    cF, cDC, cP, ncell = [], [], [], 0
    for k in sorted(counts[counts >= 8].index):
        if k not in T0:
            continue
        x = T0[k]["x"]
        xx = x.set_index("inst_key")
        xx = xx[~xx.index.duplicated()]
        c = t[t.field == k][["inst_key", "F", "G", "y"]].copy()
        c["FDC"] = c.inst_key.map(xx.InstitutionId).map(pd.Series(x.theta.to_numpy(), index=x.InstitutionId.to_numpy()).dropna())
        c["Fperp"] = c.inst_key.map(xx.Fperp)
        c["GDC"] = c.inst_key.map(GDC)
        c = c.dropna(subset=["F", "FDC", "Fperp", "GDC", "G", "y"])
        if len(c) >= 8:
            cF.append(s75.spear(c.F, c.y)); cDC.append(s75.spear(c.FDC, c.y)); cP.append(s75.spear(c.Fperp, c.y))
            ncell += len(c)
    return dict(mean_r_p=float(np.mean(rp)), n_r_p=len(rp), c_F=float(np.mean(cF)), c_DC=float(np.mean(cDC)),
                c_perp=float(np.mean(cP)), k=len(cF), cells=ncell)


def add_t0_cols(cells: pd.DataFrame, T0: dict) -> pd.DataFrame:
    c = cells.copy()
    for col in ("Fperp", "FDCr", "FDCt", "p_log", "x_exp", "rank_p", "rank_x"):
        c[col] = np.nan
    for k, v in T0.items():
        x = v["x"].copy()
        # revision 1: ranks of production p and export ratio x over the field's ranked institutions with p (the
        # set scripts/75 T0 residualises on), for the in-design production adjustment
        xr = x.dropna(subset=["p"])
        if len(xr) >= s75.MIN_INST_T1:
            x.loc[xr.index, "rank_p"] = s75.rk(xr.p.to_numpy(float))
            x.loc[xr.index, "rank_x"] = s75.rk(xr.x.to_numpy(float))
        else:
            x["rank_p"], x["rank_x"] = np.nan, np.nan
        xx = x.set_index("inst_key")
        xx = xx[~xx.index.duplicated()]
        m = c.field == k
        ik = c.loc[m, "inst_key"]
        c.loc[m, "Fperp"] = ik.map(xx.Fperp).to_numpy()
        c.loc[m, "FDCr"] = ik.map(xx.theta_rank).to_numpy()
        c.loc[m, "FDCt"] = ik.map(xx.theta).to_numpy()
        c.loc[m, "p_log"] = ik.map(xx.p).to_numpy()
        c.loc[m, "x_exp"] = ik.map(xx.x).to_numpy()
        c.loc[m, "rank_p"] = ik.map(xx.rank_p).to_numpy()
        c.loc[m, "rank_x"] = ik.map(xx.rank_x).to_numpy()
    return c


# =============================================================================================================
# G1 / G2 estimation helpers (scripts/58 functions, scripts/58 seeds)
# =============================================================================================================
def with_F(cells: pd.DataFrame, col: str) -> pd.DataFrame:
    c = cells.copy()
    c["prestige_score"] = c[col]
    return c


def main_fit(cells_list: list, seed=(58, 3, 1), b=None, slopes_list=None) -> list:
    """scripts/58 main spec (FE2) on each cells table; the tables must give identical samples. Common beta,
    CR1 SE (fe_fit) and the institution cluster bootstrap of fe_group_boot (same draws for every table).
    slopes_list (revision 1): field-specific slope covariates per table (default: the main spec's)."""
    b = s58.B_FE if b is None else b
    slopes_list = slopes_list or [MAIN_SLOPES] * len(cells_list)
    Ms = [s58.fe_build(c, sl, [], "earnings", per_field=False) for c, sl in zip(cells_list, slopes_list)]
    for M in Ms[1:]:
        assert M["d"].inst_key.equals(Ms[0]["d"].inst_key) and M["d"].field.equals(Ms[0]["d"].field)
    fits = [s58.fe_fit(M) for M in Ms]
    bb = s58.fe_group_boot(Ms, list(seed), b)
    out = []
    for M, f, j in zip(Ms, fits, range(len(Ms))):
        out.append(dict(beta=f["beta"], se_cr1=f["se"], bs=bb[:, j], n=f["n_cells"], G=f["n_inst"],
                        k=f["n_fields"], M=M))
    return out


def cs_remainder(cells_list: list, seed=(58, 11), b=None, extra=()) -> list:
    """CS row of scripts/58's per-field main spec on the common programmes, averaged over the 4-, 1- and 5-year
    outcomes per bootstrap draw (fe_boot_pf, seed [58, 11]: the same institution draws at every horizon and, on
    identical cells, for every table)."""
    b = s58.B_FE if b is None else b
    # revision 1: extra field-specific slopes; a field counts in a draw with >= (field parameters + 2) distinct
    # institutions, scripts/58's rule (8 for the main spec, + 1 per extra slope)
    md = s58.FE_PF_MIN_DISTINCT + len(extra)
    res = []
    for c in cells_list:
        pts, draws, nb, keys = [], [], None, None
        for name in HZ3:
            sl, nd, yv = s58.FE_SPECS[name]
            Mf = s58.fe_build(c, list(sl) + list(extra), nd, yv, per_field=True)
            r_ = s58.fe_fit(Mf)
            bb = s58.fe_boot_pf(Mf, list(seed), b, md)
            j = Mf["fields"].index(CS)
            pts.append(float(r_["beta_f"][CS]))
            draws.append(bb[:, j])
            if nb is None:
                nb = int(r_["n_by_field"][CS])
                keys = (Mf["d"].inst_key.copy(), Mf["d"].field.copy(), int(Mf["cnt"].size), len(Mf["y"]),
                        len(Mf["fields"]))
                cs_keys = sorted(Mf["d"].inst_key[Mf["d"].field == CS])
            del Mf, bb
        A = np.mean(np.column_stack(draws), axis=1)
        res.append(dict(beta=float(np.mean(pts)), per_h=pts, bs=A, n_cs=nb, cs_keys=cs_keys, keys=keys))
    for r_ in res[1:]:
        assert r_["keys"][0].equals(res[0]["keys"][0]) and r_["keys"][1].equals(res[0]["keys"][1])
    return res


# =============================================================================================================
# G2: CS sample gap
# =============================================================================================================
STOP = {"university", "college", "the", "of", "at", "in", "and", "campus", "main"}
STAGES = ["Wapman", "Scorecard FoS earnings", "name join", "2026 selectivity", "1-yr / 5-yr median", "sample rules",
          "undetermined"]


def fos_cs_rows() -> pd.DataFrame:
    """Every bachelor's (CREDLEV 3) Scorecard FoS row in the CS field's CIP codes, released or not."""
    use = ["UNITID", "INSTNM", "CIPCODE", "CREDLEV", "EARN_MDN_4YR", "EARN_COUNT_WNE_4YR", "EARN_MDN_1YR",
           "EARN_MDN_5YR"]
    d = pd.read_csv(s58.FOS_FILE, usecols=use, dtype=str)
    d = d[d.CREDLEV == "3"].copy()
    d["field"] = d.CIPCODE.astype(str).str.zfill(4).map(s58.F.cip4_to_field_key(s58.FIELDS66))
    d = d[d.field == CS].copy()
    for c in ("EARN_MDN_4YR", "EARN_COUNT_WNE_4YR", "EARN_MDN_1YR", "EARN_MDN_5YR"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.reset_index(drop=True)


def era_controls() -> pd.DataFrame:
    """scripts/68 version E (falls 2014-15; Pell AY 2014-15, 2015-16) per UNITID."""
    ys = sorted(set(s68.ERA_FOS["falls"]) | {a + 1 for a in s68.ERA_FOS["pell"]} | set(s68.ERA_FOS["ctl"]))
    H = s68.read_hist(ys)
    E = s68.era_table(H, **s68.ERA_FOS)
    E["UNITID"] = E.UNITID.astype(str)
    return E[["UNITID", "SAT_AVG", "ADM_RATE", "PCTPELL"]]


def _tok(name: str) -> set:
    return set(s75.norm(str(name)).split()) - STOP


def cs_gap_table(cells, ar, inst, fos, E, h3_keys, y4_keys) -> pd.DataFrame:
    """One row per top-50 Wapman CS department missing from the CS-remainder sample: first failing stage."""
    s34 = _load("s34", "34_cs_ranking.py")
    a = ar[(ar.field == CS) & ar.prestige_score.notna()].drop_duplicates("inst_key").copy()
    a["wrank"] = a.prestige_score.rank(ascending=False, method="min").astype(int)
    top = a[a.wrank <= 50].sort_values(["wrank", "inst_key"])
    assert len(top) == 50, len(top)
    gen = s55._s28.load_generic().drop_duplicates("inst_key").set_index("inst_key").g_rank
    fos = fos.copy()
    fos["coh"] = fos.EARN_COUNT_WNE_4YR.fillna(0.0)
    for k in ("k_exact", "k_campus", "k_city"):
        fos[k] = fos.INSTNM.map(getattr(s34, k))
    rel = fos[fos.EARN_MDN_4YR.notna()]
    fos_tok = {nm: _tok(nm) for nm in fos.INSTNM.unique()}
    ii = inst.set_index("UNITID")
    Ei = E.set_index("UNITID")
    cc = cells[cells.field == CS].drop_duplicates("inst_key").set_index("inst_key")
    rows = []
    for _, r in top.iterrows():
        k = r.inst_key
        rec = dict(wrank=int(r.wrank), wapman=str(r.institution_name), inst_key=k, in_h3=k in h3_keys, in_y4=k in y4_keys,
                   stage="", detail="", scorecard="", unitid="", sat26="", satE="", search="")
        if rec["in_h3"]:
            rows.append(rec)
            continue
        uid = ""
        if not np.isfinite(gen.get(k, np.nan)):
            rec.update(stage="Wapman", detail="no Wapman academia rank (G)")
        if k in cc.index:
            uid, rec["scorecard"] = str(cc.loc[k, "UNITID"]), str(cc.loc[k, "INSTNM"])
            if not rec["stage"]:
                miss4 = [v for v in INST_SLOPES if not np.isfinite(cc.loc[k, v])]
                miss5 = [v for v in ("earn1", "earn5") if not np.isfinite(cc.loc[k, v])]
                if miss4:
                    rec.update(stage="2026 selectivity", detail=", ".join(miss4) + " missing (2026 file)")
                elif miss5:
                    rec.update(stage="1-yr / 5-yr median", detail=", ".join(
                        {"earn1": "1-yr", "earn5": "5-yr"}[v] for v in miss5) + " median not released")
                else:
                    rec.update(stage="sample rules", detail="dropped by the scripts/58 sample rules")
        else:
            wk = s34.k_exact(r.institution_name)
            assert not (rel.k_exact == wk).any(), ("exact match should be in the cells", wk)
            hit = s34.best(rel, wk)
            if hit is not None:
                uid, rec["scorecard"] = str(hit.UNITID), str(hit.INSTNM)
                # revision 1: the kind is read from the Scorecard name (scripts/34's k_campus rule also strips
                # 'in the City of New York', a city qualifier)
                kind = ("campus suffix" if re.search(r"campus$", str(hit.INSTNM), flags=re.I)
                        else "city / branch qualifier")
                if not rec["stage"]:
                    rec.update(stage="name join", detail=f"Scorecard name differs ({kind}; scripts/34 rule)")
            else:
                hit_any = s34.best(fos, wk)
                if hit_any is not None:
                    uid, rec["scorecard"] = str(hit_any.UNITID), str(hit_any.INSTNM)
                    if not rec["stage"]:
                        rec.update(stage="Scorecard FoS earnings", detail="CS row found by a scripts/34 rule, "
                                   "4-yr median not released")
                else:
                    t_full = _tok(r.institution_name)
                    head = re.split(r",| - |-", str(r.institution_name))[0]
                    hits, used = [], ""
                    for lab, tk in (("full name", t_full), ("name before the first comma / hyphen", _tok(head))):
                        if tk:
                            hits = sorted(nm for nm, ft in fos_tok.items() if tk <= ft)
                            if hits:
                                used = f"tokens {sorted(tk)} ({lab})"
                                break
                    rec["search"] = f"{used}: {'; '.join(hits)}" if hits else "token search: no CS row"
                    hr = rel[rel.INSTNM.isin(hits)]
                    if len(hits) == 1 and len(hr):
                        h_ = hr.sort_values("coh", ascending=False).iloc[0]
                        uid, rec["scorecard"] = str(h_.UNITID), str(h_.INSTNM)
                        if not rec["stage"]:
                            rec.update(stage="name join", detail="no scripts/34 rule match; one CS row with a "
                                       "released 4-yr median found by the token search")
                    elif len(hits) >= 1 and not len(hr):
                        if not rec["stage"]:
                            rec.update(stage="Scorecard FoS earnings", detail="token-search CS rows have no "
                                       "released 4-yr median")
                    elif len(hits) > 1:
                        if not rec["stage"]:
                            rec.update(stage="undetermined", detail="several token-search CS rows; not assigned")
                    elif not rec["stage"]:
                        rec.update(stage="Scorecard FoS earnings", detail="no bachelor's CS row found by the "
                                   "scripts/34 rules or the token search")
        rec["unitid"] = uid
        if uid:
            s26 = ii.SAT_AVG.get(uid, np.nan) if uid in ii.index else np.nan
            sE = Ei.SAT_AVG.get(uid, np.nan) if uid in Ei.index else np.nan
            rec["sat26"] = "yes" if np.isfinite(s26) else "no"
            rec["satE"] = "yes" if np.isfinite(sE) else "no"
        rows.append(rec)
    T = pd.DataFrame(rows)
    return T


def run_g1(cells: pd.DataFrame, T0: dict) -> dict:
    c = add_t0_cols(cells, T0)
    R = {}
    stage("G1: main spec, full cells: F (reproduction) and F_perp (A1: the rule's row for (a))")
    full = main_fit([with_F(c, "prestige_score"), with_F(c, "Fperp")])
    R["full"] = full
    M0 = full[0]["M"]
    d0 = M0["d"]                                          # carries Fperp, FDCr, FDCt (copied from the cells)
    R["cov"] = dict(n=len(d0), fperp=int(d0.Fperp.notna().sum()), fdc=int(d0.FDCr.notna().sum()),
                    fdc_inst=int(d0[d0.FDCr.notna()].inst_key.nunique()), inst=int(d0.inst_key.nunique()))
    # scripts/58's residual-F reliability (lambda) of the original main spec, from fe_fit with relF
    Rl = pd.read_csv(s58.REL_CSV)
    Rl = Rl[Rl.unit == "field"].set_index("field")
    rel = {"LB": Rl["relF_LB"].to_dict(), "EXT": Rl["relF_EXT"].to_dict()}
    f0 = s58.fe_fit(M0, rel)
    R["lam58"] = dict(LB=f0["lam_LB"], EXT=f0["lam_EXT"], resid_share=f0["resid_var_share"])
    R["rel"] = rel
    stage("G1: common cells (F, F_perp, F_DC all exist): F, F_perp, F_DC rank, F_DC theta")
    cc = c[c.Fperp.notna() & c.FDCr.notna()]
    com = main_fit([with_F(cc, v) for v in ("prestige_score", "Fperp", "FDCr", "FDCt")])
    R["com"] = com
    stage("G1: CS remainder, full common-programme cells: F (reproduction), F_perp")
    R["cs_full"] = cs_remainder([with_F(c, "prestige_score"), with_F(c, "Fperp")])
    stage("G1: CS remainder on the common cells: F, F_perp, F_DC rank, F_DC theta")
    R["cs_com"] = cs_remainder([with_F(cc, v) for v in ("prestige_score", "Fperp", "FDCr", "FDCt")])
    # descriptive: within-field Spearman of F with F_perp / F_DC on the main-spec cells
    R["rho"] = {v: float(np.mean([spearmanr(g.prestige_score, g[v])[0] for _, g in d0.dropna(subset=[v]).groupby("field")
                                   if len(g) >= 3])) for v in ("Fperp", "FDCr")}
    return R


def run_g1_rev1(cells: pd.DataFrame, T0: dict, R1: dict) -> dict:
    """Revision 1 (added after results were seen): the production adjustment inside the scripts/58
    design. F_perp is a residual over all of a field's ranked institutions; inside the within-institution design it
    need not be orthogonal to production. Here F stays as it is and field x {rank of production, rank of export ratio}
    (or field x rank of production only) enter the main specification as further field-specific slopes, so the slope
    of F is its partial slope net of production within the design (Frisch-Waugh-Lovell). Same cells, same draws
    (fe_group_boot seed [58, 3, 1]; fe_boot_pf seed [58, 11]) as the original, so every change is paired."""
    c = add_t0_cols(cells, T0)
    R = {}
    cF = with_F(c, "prestige_score")
    stage("G1 rev. 1: main spec + field x {production rank, export-ratio rank} / + field x production rank")
    des = main_fit([cF, cF], slopes_list=[MAIN_SLOPES + ["rank_p", "rank_x"], MAIN_SLOPES + ["rank_p"]])
    M0 = R1["full"][0]["M"]
    for r_ in des:
        assert r_["M"]["d"].inst_key.equals(M0["d"].inst_key) and r_["M"]["d"].field.equals(M0["d"].field)
        r_.pop("M")
    R["design"] = des
    # within the design (institution FE, field FE, field x traits removed): correlation of F_perp, and of F, with
    # the production and export-ratio ranks (all z-scored within field on the sample, as fe_build does)
    d = M0["d"][["field", "inst_key", "prestige_score", "Fperp"]].merge(
        c[["field", "inst_key", "rank_p", "rank_x"]], on=["field", "inst_key"], how="left")
    assert len(d) == len(M0["d"]) and d.inst_key.equals(M0["d"].inst_key.reset_index(drop=True))
    j = M0["names"].index("beta")
    Xo = np.delete(M0["X"], j, axis=1)
    g_, cnt = M0["groups"], M0["cnt"]

    def res(col):
        v = d.groupby("field")[col].transform(lambda s: (s - s.mean()) / s.std()).to_numpy()
        v = v - (np.bincount(g_, v, cnt.size) / cnt)[g_]
        return v - Xo @ np.linalg.lstsq(Xo, v, rcond=None)[0]
    rr = {col: res(col) for col in ("prestige_score", "Fperp", "rank_p", "rank_x")}
    R["pcorr"] = {(a_, b_): corr(rr[a_], rr[b_]) for a_ in ("Fperp", "prestige_score") for b_ in ("rank_p", "rank_x")}
    stage("G1 rev. 1: CS remainder with field x {production, export-ratio ranks} / field x production rank")
    R["cs_design"] = [cs_remainder([cF], extra=("rank_p", "rank_x"))[0], cs_remainder([cF], extra=("rank_p",))[0]]
    k0 = R1["cs_full"][0]["keys"]
    for r_ in R["cs_design"]:
        assert r_["keys"][0].equals(k0[0]) and r_["keys"][1].equals(k0[1])
    return R


def run_g2(cells, ar, inst, R1) -> dict:
    stage("G2: diagnosis of the top-50 CS departments missing from the CS-remainder sample")
    fos = cached("fos_cs", fos_cs_rows)
    E = cached("era_E", era_controls)
    h3_keys = set(R1["cs_full"][0]["cs_keys"])
    y4 = s58.fe_build(cells, MAIN_SLOPES, [], "earnings", per_field=False)["d"]
    y4_keys = set(y4.inst_key[y4.field == CS])
    T = cs_gap_table(cells, ar, inst, fos, E, h3_keys, y4_keys)
    miss = T[~T.in_h3]
    cnt = miss.stage.value_counts().reindex(STAGES).fillna(0).astype(int)
    top_stage = cnt.idxmax()
    fires = bool(top_stage == "2026 selectivity" and (cnt == cnt.max()).sum() == 1)
    sel = miss[miss.stage == "2026 selectivity"]
    restored = bool(len(sel) and (sel.satE == "yes").all())
    out = dict(T=T, n_missing=len(miss), counts=cnt, main=top_stage, fires=bool(fires and restored),
               main_unique=bool((cnt == cnt.max()).sum() == 1), sel_restored=restored, n_sel=len(sel),
               n_sel_E=int((sel.satE == "yes").sum()))
    # re-estimate with era-matched controls (pre-specified if the branch fires; exploratory otherwise)
    stage("G2: CS remainder with version-E controls (old sample / complete under both / enlarged)")
    ce = cells.copy()
    ce["UNITID"] = ce.UNITID.astype(str)
    Ei = E.set_index("UNITID")
    for v in INST_SLOPES:
        ce[v + "_26"] = ce[v]
        ce[v] = ce.UNITID.map(Ei[v])
    both = ce[[v + "_26" for v in INST_SLOPES]].notna().all(axis=1) & ce[INST_SLOPES].notna().all(axis=1)
    out["E_common"] = cs_remainder([ce[both]])[0]
    out["E_enl"] = cs_remainder([ce])[0]
    out["old"] = R1["cs_full"][0]
    a = ar[(ar.field == CS)].drop_duplicates("inst_key").set_index("inst_key")
    for tag in ("old", "E_common", "E_enl"):
        ks = set(out[tag]["cs_keys"])
        out[f"{tag}_top50"] = int(sum(1 for k in ks if k in a.index and str(a.loc[k, "institution_name"]) in set(T.wapman)))
    out["restored_names"] = sorted(set(T.wapman[(~T.in_h3)]) & {str(a.loc[k, "institution_name"]) for k in out["E_enl"]["cs_keys"] if k in a.index})
    out["E_cov"] = dict(n_cells=len(ce), both=int(both.sum()), E_only=int((ce[INST_SLOPES].notna().all(axis=1) & ~both).sum()))

    def why(key):
        r_ = ce[(ce.field == CS) & (ce.inst_key == key)]
        if not len(r_):
            return "not in the cells"
        r_ = r_.iloc[0]
        m_ = [f"era-matched {v}" for v in INST_SLOPES if not np.isfinite(r_[v])] + \
             [lab_ for v, lab_ in (("earn1", "1-yr median"), ("earn5", "5-yr median"), ("G", "brand G"))
              if not np.isfinite(r_[v])]
        return ", ".join(m_) + " missing" if m_ else "scripts/58 sample rules"
    enl = set(out["E_enl"]["cs_keys"])
    out["sel_not_restored"] = [(r_.wapman, why(r_.inst_key)) for r_ in sel.itertuples() if r_.inst_key not in enl]
    out["old_lost"] = [(r_.wapman, why(r_.inst_key)) for r_ in T[T.in_h3].itertuples() if r_.inst_key not in enl]
    return out


# =============================================================================================================
# UK data: scripts/76 panel and a per-cohort read of the LEO file (quartiles, band counts with 'low' kept)
# =============================================================================================================
def uk_panel():
    sub, pu, inst = s76.load_ref()
    sub14, pu14 = s76.load_ref14()
    leo, prov = s76.load_leo_prov()
    P = s76.build_panel(leo, prov, pu, inst)
    del leo
    pa = s76.load_pa_raw(set(P.ukprn))
    P = s76.add_revision_cols(P, pu, pu14, pa)
    return P


def leo_cohort_rows(ukprns: set) -> tuple[pd.DataFrame, pd.DataFrame]:
    """YAG 5, cohorts 2013/14-2016/17, provider x CAH2 rows of the given providers: all-graduate rows with the
    released median, quartiles and earnings count per cohort; prior-attainment band rows per cohort with the
    'low' code kept (as scripts/76 load_pa_raw, not pooled)."""
    keep = ["academic_year", "YAG", "ukprn", "cah2_subject_name", "grads", "grads_earnings_include", "earnings_LQ",
            "earnings_median", "earnings_UQ", "characteristic_type", "characteristic_value"]
    z = zipfile.ZipFile(s62.LEO_ZIP)
    name = [n for n in z.namelist() if n.startswith("provider_data")][0]
    al, pa = [], []
    for ch in pd.read_csv(z.open(name), encoding="latin-1", dtype=str, usecols=keep, chunksize=200000):
        ch = ch[(ch.YAG == "5") & ch.ukprn.isin(ukprns) & (ch.cah2_subject_name != "Total")
                & ch.characteristic_type.isin(["All graduates", "prior_attainment_code"])]
        coh = ch.academic_year.str[:4].astype(int)
        ch = ch[coh.isin(s62.COHORTS)].assign(cohort=coh[coh.isin(s62.COHORTS)])
        al.append(ch[ch.characteristic_type == "All graduates"])
        pa.append(ch[ch.characteristic_type == "prior_attainment_code"])
    A = pd.concat(al, ignore_index=True).rename(columns={"cah2_subject_name": "subject"})
    Pa = pd.concat(pa, ignore_index=True).rename(columns={"cah2_subject_name": "subject"})
    assert not A.duplicated(["ukprn", "subject", "cohort"]).any()
    for c in ("earnings_LQ", "earnings_median", "earnings_UQ", "grads_earnings_include", "grads"):
        A[c] = pd.to_numeric(A[c], errors="coerce")
    Pa["band"] = Pa.characteristic_value.str.replace("prior_attainment_", "PA", regex=False).replace(
        {"Not known": "PA_NK"})
    assert not Pa.duplicated(["ukprn", "subject", "cohort", "band"]).any()
    codes = set(Pa.grads[~Pa.grads.str.fullmatch(r"\d+")])
    assert codes <= {"low"}, codes
    Pa["num"] = pd.to_numeric(Pa.grads, errors="coerce").fillna(0.0)
    Pa["nlow"] = (Pa.grads == "low").astype(float)
    return A[["ukprn", "subject", "cohort", "earnings_LQ", "earnings_median", "earnings_UQ",
              "grads_earnings_include", "grads"]], Pa[["ukprn", "subject", "cohort", "band", "num", "nlow"]]


def s76_fe_sample(P, mapset, need, zsrc="ref_gpa", zfun=None, extra_z=()):
    """scripts/76 analyse()'s nested fe_sample, re-stated (it cannot be imported)."""
    zfun = zfun or s76.zrank
    x = P[P.xw.isin(mapset)].dropna(subset=need)
    x = x[x.groupby("subject").ukprn.transform("size") >= s76.NMIN].copy()
    x["z"] = x.groupby("subject")[zsrc].transform(lambda v: pd.Series(zfun(v.values), index=v.index))
    for c in extra_z:
        x["z_" + c] = x.groupby("subject")[c].transform(lambda v: pd.Series(s76.zrank(v.values), index=v.index))
    return s76.drop_singletons(x)


def inter(df, cols):
    """scripts/76 analyse()'s nested inter: subject x column interaction columns."""
    out = []
    for c in cols:
        for s in sorted(df.subject.unique()):
            nm = f"{c}|{s}"
            df[nm] = np.where(df.subject == s, df[c], 0.0)
            out.append(nm)
    return out


def intake_from_counts(Pa: pd.DataFrame, cohorts, f: int) -> pd.Series:
    """Share with >= 360 points (bands 1-2 over known bands 1-9) from pooled band counts, 'low' = f graduates."""
    x = Pa[Pa.cohort.isin(cohorts)]
    b = (x.num + f * x.nlow).groupby([x.ukprn, x.subject, x.band]).sum().unstack("band")
    b = b.reindex(columns=s62.PA_ALL).fillna(0.0)
    kn = b[s62.PA_ALL[:-1]].sum(axis=1)
    return (b.PA1 + b.PA2) / kn.where(kn > 0)


def score_from_counts(Pa: pd.DataFrame, cohorts, f: int) -> pd.Series:
    x = Pa[Pa.cohort.isin(cohorts)]
    b = (x.num + f * x.nlow).groupby([x.ukprn, x.subject, x.band]).sum().unstack("band")
    b = b.reindex(columns=s62.PA_ALL).fillna(0.0)
    k6 = b[["PA1", "PA2", "PA3", "PA4", "PA5", "PA6"]].sum(axis=1)
    return (5 * b.PA1 + 4 * b.PA2 + 3 * b.PA3 + 2 * b.PA4 + 1 * b.PA5) / k6.where(k6 > 0)


# =============================================================================================================
# G3 UK: same statistic at both levels, reliabilities of the within-level residuals, provider cluster bootstrap
# =============================================================================================================
def fac(v) -> np.ndarray:
    return pd.factorize(np.asarray(v), sort=True)[0]


def fe2_leverage(pid: np.ndarray, sid: np.ndarray) -> np.ndarray:
    """Diagonal of the hat matrix of provider + subject fixed effects (FWL: provider means, then the
    within-provider-demeaned subject dummies)."""
    G = pid.max() + 1
    S = np.zeros((len(sid), sid.max() + 1))
    S[np.arange(len(sid)), sid] = 1.0
    St = s76._demean(S[:, 1:], pid, G)
    Q = np.linalg.pinv(St.T @ St, hermitian=True)
    cnt = np.bincount(pid, minlength=G).astype(float)
    return 1.0 / cnt[pid] + ((St @ Q) * St).sum(axis=1)


def sb(r: float) -> float:
    return 2 * r / (1 + r) if np.isfinite(r) and r > -1 else np.nan


def disatt(r, ra, rb) -> float:
    if not (np.isfinite(ra) and np.isfinite(rb)) or ra <= 0 or rb <= 0:
        return np.inf
    return r / np.sqrt(ra * rb)


UK_VARS = ["ref", "pay", "int1", "int0", "score1"]          # intake: 'low'=1 share (primary), 'low'=0, band score
UK_INTAKE = {"int1": "share >= 360 points, 'low' = 1 (primary)", "int0": "share >= 360 points, 'low' = 0 (sens.)",
             "score1": "mean band score, 'low' = 1 (exploratory)"}


def pay_noise(A: pd.DataFrame, cells: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame, dict]:
    """scripts/73-style sampling variance of each programme's mean log median (LEO, YAG5, cohorts 2013-16): per cohort
    SE = 1.2533 (UQ - LQ) / 1.349 / sqrt(n) / median, n = grads_earnings_include (the subject's median relative IQR
    where a cohort's quartiles are not released); variance of the mean over the K released cohorts = sum SE^2 / K^2.
    Returns the variances aligned with `cells`, the per-cohort rows and checks (the mean log median must reproduce
    the panel's pay)."""
    key = pd.MultiIndex.from_frame(cells[["ukprn", "subject"]])
    a = A.merge(cells[["ukprn", "subject"]], on=["ukprn", "subject"])
    a = a[a.earnings_median > 0].copy()
    a["ly"] = np.log(a.earnings_median)
    chk = {}
    pay_chk = a.groupby(["ukprn", "subject"]).ly.mean().reindex(key).to_numpy()
    chk["pay_maxdiff"] = float(np.nanmax(np.abs(pay_chk - cells.pay.to_numpy())))
    assert chk["pay_maxdiff"] < 1e-12 and np.isfinite(pay_chk).all()
    okq = a.earnings_LQ.notna() & a.earnings_UQ.notna() & (a.earnings_UQ >= a.earnings_LQ)
    a["riqr"] = np.where(okq, (a.earnings_UQ - a.earnings_LQ) / a.earnings_median, np.nan)
    a["riqr_used"] = a.riqr.fillna(a.subject.map(a.groupby("subject").riqr.median()))
    okn = a.grads_earnings_include > 0
    chk["pay_cohorts"], chk["pay_cohorts_noquart"], chk["pay_cohorts_non"] = len(a), int((~okq).sum()), int((~okn).sum())
    assert okn.all(), "released median without an earnings count"
    a["se2"] = (s73.MED_SE * a.riqr_used / s73.IQR_Z) ** 2 / a.grads_earnings_include
    g_ = a.groupby(["ukprn", "subject"])
    s2 = (g_.se2.sum() / g_.se2.size() ** 2).reindex(key).to_numpy()
    assert np.isfinite(s2).all()
    return s2, a, chk


def lin_within(df: pd.DataFrame, col: str, grp: str, ddof: int = 0) -> np.ndarray:
    """Revision 1: linear within-group z-scores (mean 0, SD 1 with the given ddof)."""
    out = np.empty(len(df))
    for _, ix in df.groupby(grp).indices.items():
        v = df[col].to_numpy(float)[ix]
        out[ix] = (v - v.mean()) / v.std(ddof=ddof)
    return out


def uk_g3_data(P: pd.DataFrame, A: pd.DataFrame, Pa: pd.DataFrame, filt=None) -> dict:
    """filt (revision 1): a row filter applied to the G3 cells before scripts/76's singleton rule is re-applied; the
    whole pipeline (scores, subsets, reliabilities) is then rebuilt on the remaining cells."""
    d6 = s76_fe_sample(P, ["clean"], ["ref_gpa", "pay", "top", "score"])
    if filt is not None:
        d6 = s76.drop_singletons(d6[filt(d6)].copy())
    d6 = d6.sort_values(["ukprn", "subject"]).reset_index(drop=True)
    pid, sid = fac(d6.ukprn), fac(d6.subject)
    chk = {}
    chk["wtriad"] = s76.corr_cols(s76.fe_resid(d6[["z", "pay", "top"]].values.astype(float), pid, sid))
    chk["n6"], chk["G6"] = len(d6), int(pid.max() + 1)
    key = pd.MultiIndex.from_frame(d6[["ukprn", "subject"]])
    # pay per cohort: released medians reproduce the panel's pay; scripts/73-style noise of the mean log median
    s2_log, a, pchk = pay_noise(A, d6)
    chk.update(pchk)
    chk["pay_relse_median"] = float(np.median(np.sqrt(s2_log)))
    # intake: pooled shares reproduce scripts/76's columns; odd / even cohort halves
    for f, col in ((0, "top_l0"), (1, "top_l1")):
        v = intake_from_counts(Pa, s62.COHORTS, f).reindex(key).to_numpy()
        chk[f"int{f}_maxdiff"] = float(np.nanmax(np.abs(v - d6[col].to_numpy())))
        assert chk[f"int{f}_maxdiff"] < 1e-12
    v = score_from_counts(Pa, s62.COHORTS, 1).reindex(key).to_numpy()
    chk["score1_maxdiff"] = float(np.nanmax(np.abs(v - d6["score_l1"].to_numpy())))
    assert chk["score1_maxdiff"] < 1e-12
    assert np.allclose(d6.top_l0, d6.top)
    HA, HB = [2013, 2015], [2014, 2016]
    halves = {"int1": (intake_from_counts(Pa, HA, 1), intake_from_counts(Pa, HB, 1)),
              "int0": (intake_from_counts(Pa, HA, 0), intake_from_counts(Pa, HB, 0)),
              "score1": (score_from_counts(Pa, HA, 1), score_from_counts(Pa, HB, 1))}
    # normal scores (fixed in the bootstrap)
    d = d6.assign(ref=d6.ref_gpa, int1=d6.top_l1, int0=d6.top_l0, score1=d6.score_l1)
    Z = np.column_stack([ns_within(d, v, "subject", 0) for v in UK_VARS])
    var_pay = d.groupby("subject").pay.transform(lambda v: v.var(ddof=0)).to_numpy()
    s2z = s2_log / var_pay
    # REF 2021 / 2014 test-retest subset (subjects >= 15 providers, singletons dropped)
    dr = d[d.ref14_gpa.notna()].copy()
    dr = dr[dr.groupby("subject").ukprn.transform("size") >= s76.NMIN]
    dr = s76.drop_singletons(dr).sort_values(["ukprn", "subject"])
    ref_idx = dr.index.to_numpy()
    ZR = np.column_stack([ns_within(dr.reset_index(drop=True), c, "subject", 0) for c in ("ref_gpa", "ref14_gpa")])
    # intake split-half subsets
    H = {}
    for v, (sa, sb_) in halves.items():
        x = d.assign(hA=sa.reindex(key).to_numpy(), hB=sb_.reindex(key).to_numpy())
        x = x[x.hA.notna() & x.hB.notna()]
        x = x[x.groupby("subject").ukprn.transform("size") >= 2]
        H[v] = (x.index.to_numpy(), np.column_stack([ns_within(x.reset_index(drop=True), c, "subject", 0)
                                                      for c in ("hA", "hB")]))
    # pay split-half (exploratory check of the noise-based reliability): odd / even cohort mean log medians
    pA = a[a.cohort.isin(HA)].groupby(["ukprn", "subject"]).ly.mean().reindex(key).to_numpy()
    pB = a[a.cohort.isin(HB)].groupby(["ukprn", "subject"]).ly.mean().reindex(key).to_numpy()
    xp = d.assign(hA=pA, hB=pB)
    xp = xp[xp.hA.notna() & xp.hB.notna()]
    xp = xp[xp.groupby("subject").ukprn.transform("size") >= 2]
    H["pay_half"] = (xp.index.to_numpy(), np.column_stack([ns_within(xp.reset_index(drop=True), c, "subject", 0)
                                                            for c in ("hA", "hB")]))
    # revision 1: linear within-subject z version of the same pipeline (REF GPA, pay, intake share 'low' = 1)
    ZL = np.column_stack([lin_within(d, v, "subject") for v in ("ref", "pay", "int1")])
    ZRL = np.column_stack([lin_within(dr.reset_index(drop=True), c, "subject") for c in ("ref_gpa", "ref14_gpa")])
    xh = d.assign(hA=halves["int1"][0].reindex(key).to_numpy(), hB=halves["int1"][1].reindex(key).to_numpy())
    xh = xh[xh.hA.notna() & xh.hB.notna()]
    xh = xh[xh.groupby("subject").ukprn.transform("size") >= 2]
    HL = (xh.index.to_numpy(), np.column_stack([lin_within(xh.reset_index(drop=True), c, "subject")
                                                for c in ("hA", "hB")]))
    sizes = {"ref": (len(ref_idx), int(d.loc[ref_idx].ukprn.nunique()))}
    for v in H:
        sizes[v] = (len(H[v][0]), int(d.loc[H[v][0]].ukprn.nunique()))
    # within-provider share of the variance of each normal score (calibration target of the simulation)
    Rq = s76.fe_resid(Z[:, :3], pid, sid)
    Zq = Z[:, :3] - pd.DataFrame(Z[:, :3]).groupby(sid).transform("mean").to_numpy()
    q_obs = (Rq ** 2).sum(0) / (Zq ** 2).sum(0)
    out = dict(d=d, pid=pid, sid=sid, Z=Z, s2z=s2z, ref_idx=ref_idx, ZR=ZR, H=H, chk=chk, ZL=ZL, ZRL=ZRL, HL=HL,
               sizes=sizes, q_obs=q_obs, s2_log=s2_log, pay_rows=a)
    if filt is not None:
        return out
    # scripts/76 REF test-retest reproduction (its own cells and z-ranks)
    dc = P[P.xw == "clean"].dropna(subset=["ref_gpa", "ref14_gpa", "pay"])
    dc = dc[dc.groupby("subject").ukprn.transform("size") >= s76.NMIN].copy()
    for zc_, src in [("z", "ref_gpa"), ("z14", "ref14_gpa")]:
        dc[zc_] = dc.groupby("subject")[src].transform(lambda v: pd.Series(s76.zrank(v.values), index=v.index))
    dc = s76.drop_singletons(dc).sort_values(["ukprn", "subject"]).reset_index(drop=True)
    Rc = s76.fe_resid(dc[["z", "z14"]].values.astype(float), fac(dc.ukprn), fac(dc.subject))
    chk["rel76"], chk["rel76_n"] = corr(Rc[:, 0], Rc[:, 1]), len(dc)
    # T4 reproduction and the T4-cell version of the across level
    c4 = s76.subject_cells(P, ["ref_gpa", "pay", "top"], list(s76.CLEAN), primary=False)
    chk["t4"] = np.mean([[spearmanr(g[a_], g[b_])[0] for a_, b_ in (("ref_gpa", "pay"), ("ref_gpa", "top"),
                                                                     ("pay", "top"))] for g in c4.values()], axis=0)
    z4 = pd.concat(c4.values()).reset_index(drop=True)
    z4 = z4.assign(ref=z4.ref_gpa, int1=z4.top_l1)
    Z4 = np.column_stack([ns_within(z4, v, "subject", 0) for v in ("ref", "pay", "int1")])
    chk["t4_n"] = len(z4)
    chk["across_t4cells"] = np.array([corr(Z4[:, i], Z4[:, j]) for i, j in ((0, 1), (0, 2), (1, 2))])
    chk["zero_share"] = dict(int0=float((d.top_l0 == 0).mean()), int1=float((d.top_l1 == 0).mean()))
    # per-subject Pearson of the normal scores, mean over subjects (exploratory)
    chk["across_subjmean"] = {v: np.mean([[corr(Z[ix, 0], Z[ix, 1]), corr(Z[ix, 0], Z[ix, j]), corr(Z[ix, 1], Z[ix, j])]
                                          for ix in d.groupby("subject").indices.values()], axis=0)
                              for v, j in (("int1", 2), ("int0", 3), ("score1", 4))}
    return out


def uk_stats(D: dict, rows: np.ndarray, newp: np.ndarray, rel_ref_fixed: float | None = None) -> dict:
    """Across / within correlations, reliabilities and disattenuated within correlations on a set of rows
    (rows may repeat; newp gives each row's provider copy)."""
    sid = fac(D["sid"][rows])
    pid = fac(newp)
    Z = D["Z"][rows]
    S = sid.max() + 1
    cntS = np.bincount(sid, minlength=S).astype(float)
    Za = Z - np.column_stack([np.bincount(sid, Z[:, j], S) / cntS for j in range(Z.shape[1])])[sid]
    Rw = s76.fe_resid(Z, pid, sid)
    lev = fe2_leverage(pid, sid)
    out = {}
    out["rel_pay"] = 1.0 - float((D["s2z"][rows] * (1.0 - lev)) @ np.ones(len(rows))) / float(Rw[:, 1] @ Rw[:, 1])

    def sub_rel(idx_all, Zsub):
        pos = {v: i for i, v in enumerate(idx_all)}
        m = np.array([r_ in pos for r_ in rows])
        if m.sum() < 4:
            return np.nan
        loc = np.array([pos[r_] for r_ in rows[m]])
        Rs = s76.fe_resid(Zsub[loc], fac(newp[m]), fac(D["sid"][rows[m]]))
        return corr(Rs[:, 0], Rs[:, 1])

    out["rel_ref"] = sub_rel(D["ref_idx"], D["ZR"]) if rel_ref_fixed is None else rel_ref_fixed
    for v in ("int1", "int0", "score1", "pay_half"):
        r_ = sub_rel(*D["H"][v])
        out[f"r_half_{v}"] = r_
        out[f"rel_{v}"] = sb(r_)
    for v, j in (("int1", 2), ("int0", 3), ("score1", 4)):
        for pair, (i, k, ra, rb) in {"REF-pay": (0, 1, "rel_ref", "rel_pay"),
                                     "REF-intake": (0, j, "rel_ref", f"rel_{v}"),
                                     "pay-intake": (1, j, "rel_pay", f"rel_{v}")}.items():
            if pair == "REF-pay" and v != "int1":
                continue
            tag = pair if pair == "REF-pay" else f"{pair}|{v}"
            out[f"across|{tag}"] = corr(Za[:, i], Za[:, k])
            out[f"within|{tag}"] = corr(Rw[:, i], Rw[:, k])
            out[f"ceil|{tag}"] = np.sqrt(out[ra] * out[rb]) if (out[ra] > 0 and out[rb] > 0) else np.nan
            out[f"dis|{tag}"] = disatt(out[f"within|{tag}"], out[ra], out[rb])
    # ---- revision 1: pure between-provider correlation (provider means of the subject-demeaned scores) and the
    # linear within-subject z version (REF, pay, intake 'low' = 1) of the whole pipeline
    G = pid.max() + 1
    cG = np.bincount(pid, minlength=G).astype(float)
    Zl = D["ZL"][rows]
    Zla = Zl - np.column_stack([np.bincount(sid, Zl[:, j], S) / cntS for j in range(3)])[sid]
    Rwl = s76.fe_resid(Zl, pid, sid)
    out["rel_pay_lin"] = 1.0 - float((D["s2z"][rows] * (1.0 - lev)) @ np.ones(len(rows))) / float(Rwl[:, 1] @ Rwl[:, 1])
    out["rel_ref_lin"] = sub_rel(D["ref_idx"], D["ZRL"]) if rel_ref_fixed is None else rel_ref_fixed
    out["rel_int1_lin"] = sb(sub_rel(*D["HL"]))
    for nm_, ZZ, (i_ref, i_pay, i_int) in (("", Za, (0, 1, 2)), ("_lin", Zla, (0, 1, 2))):
        Pm = np.column_stack([np.bincount(pid, ZZ[:, j], G) for j in range(ZZ.shape[1])]) / cG[:, None]
        for pair, (i, k) in {"REF-pay": (i_ref, i_pay), "REF-intake": (i_ref, i_int),
                             "pay-intake": (i_pay, i_int)}.items():
            out[f"between{nm_}|{pair}"] = corr(Pm[:, i], Pm[:, k])
    rl = {0: out["rel_ref_lin"], 1: out["rel_pay_lin"], 2: out["rel_int1_lin"]}
    for pair, (i, k) in {"REF-pay": (0, 1), "REF-intake": (0, 2), "pay-intake": (1, 2)}.items():
        out[f"across_lin|{pair}"] = corr(Zla[:, i], Zla[:, k])
        out[f"within_lin|{pair}"] = corr(Rwl[:, i], Rwl[:, k])
        out[f"dis_lin|{pair}"] = disatt(out[f"within_lin|{pair}"], rl[i], rl[k])
    return out


def run_g3_uk(D: dict) -> dict:
    n = len(D["d"])
    G = int(D["pid"].max() + 1)
    groups = [np.flatnonzero(D["pid"] == g) for g in range(G)]
    pt = uk_stats(D, np.arange(n), D["pid"])
    pt_fix = uk_stats(D, np.arange(n), D["pid"], rel_ref_fixed=0.536)
    keys = list(pt)
    BS = np.full((B, len(keys)), np.nan)
    fixed_keys = [k for k in keys if k.startswith("dis|")]
    BSF = np.full((B, len(fixed_keys)), np.nan)
    for b, rng in enumerate(rep_gens("g3_uk")):
        draw = rng.integers(G, size=G)
        rows = np.concatenate([groups[g] for g in draw])
        newp = np.concatenate([np.full(len(groups[g]), k) for k, g in enumerate(draw)])
        s = uk_stats(D, rows, newp)
        BS[b] = [s[k] for k in keys]
        sf = uk_stats(D, rows, newp, rel_ref_fixed=0.536)
        BSF[b] = [sf[k] for k in fixed_keys]
    return dict(pt=pt, keys=keys, bs=BS, pt_fix=pt_fix, fixed_keys=fixed_keys, bs_fix=BSF, n=n, G=G,
                S=int(D["sid"].max() + 1))


# =============================================================================================================
# G3 UK, revision 1 (added after results were seen): robustness subsets and a simulation-
# calibrated test of rho_within = rho_between on the real layout
# =============================================================================================================
B_ROB = 500                    # provider-bootstrap replicates of each robustness subset
SIM_CAL_ROUNDS, SIM_CAL_M = 12, 64       # calibration: rounds x simulated data sets per round
SIM_DAMP = 0.5                 # damping of the calibration updates (exponent of the multiplicative step)
SIM_NULL = 600                 # null draws for the calibrated p-values (>= 500)
SIM_SIZE, SIM_SIZE_B = 120, 200          # size check of the pre-specified rule: data sets x bootstrap replicates
SIM_ALTFIN = 300               # draws at the calibrated alternative (spread of the within statistic)
HA_MASK = np.array([True, False, True, False])   # cohorts 2013, 2015 vs 2014, 2016 (s62.COHORTS order)
PAIRS3 = {"REF-pay": (0, 1), "REF-intake": (0, 2), "pay-intake": (1, 2)}


def alias_check(R2: dict, inst: pd.DataFrame) -> dict:
    """Revision 2: can scripts/59's name aliases (4 for new PSEO institutions + 19 from its join audit, imported via
    s59.alias_full) recover the CS departments lost to the Scorecard name join? The maps are keyed by normalised
    non-Wapman names and point to normalised Wapman names; a department is recovered if its Scorecard institution's
    normalised name is a key that points to the department's Wapman name."""
    amap = s68.s59.alias_full()
    T = R2["T"]
    nj = T[(~T.in_h3) & (T.stage == "name join")]
    hits = [r.wapman for r in nj.itertuples() if amap.get(s75.norm(r.scorecard)) == r.inst_key]
    sc_keys = set(inst.INSTNM.map(s75.norm))
    return dict(n_map=len(amap), n_alias4=len(s68.s59.ALIAS), n_audit=len(s68.s59.JOIN_AUDIT), n_lost=len(nj),
                recovered=hits, keys_in_scorecard=int(len(set(amap) & sc_keys)))


def run_g3_rob(P, A, Pa) -> dict:
    """End-to-end re-runs on two subsets (cells re-selected with scripts/76's singleton rule, scores and reliabilities
    rebuilt): (i) programmes with an intake share > 0 ('low' = 1) -- a filter on a noisy variable, so it selects on
    measurement error as well as on intake; (ii) programmes with at least the median number of graduates in the
    earnings data (over the 864 G3 cells). Point estimates and a provider bootstrap (B_ROB) per subset."""
    subs = [("drop intake share = 0", lambda d: d.top_l1 > 0),
            ("graduates in the earnings data >= median", lambda d: d.n_earn >= d.n_earn.median())]
    out = {}
    for j, (lab, fl) in enumerate(subs):
        Dr = uk_g3_data(P, A, Pa, filt=fl)
        n, G = len(Dr["d"]), int(Dr["pid"].max() + 1)
        groups = [np.flatnonzero(Dr["pid"] == g) for g in range(G)]
        pt = uk_stats(Dr, np.arange(n), Dr["pid"])
        keys = [k for k in pt if k.startswith(("dis|", "dis_lin|", "across", "within"))]
        ss = np.random.SeedSequence(_KIDS["g3_rob"].entropy, spawn_key=_KIDS["g3_rob"].spawn_key + (j,))
        BS = np.full((B_ROB, len(keys)), np.nan)
        for b, s_ in enumerate(ss.spawn(B_ROB)):
            draw = np.random.default_rng(s_).integers(G, size=G)
            rows = np.concatenate([groups[g] for g in draw])
            newp = np.concatenate([np.full(len(groups[g]), k) for k, g in enumerate(draw)])
            s = uk_stats(Dr, rows, newp)
            BS[b] = [s[k] for k in keys]
        out[lab] = dict(pt=pt, keys=keys, bs=BS, n=n, G=G)
    return out


# ---------------- simulation (worker-safe: numpy / pandas / scipy only) ----------------
_SIM: dict = {}


def _sim_init(inp: dict):
    _SIM.clear()
    _SIM.update(inp)


def _dm_np(M, g, G):
    cnt = np.bincount(g, minlength=G).astype(float)
    return M - np.column_stack([np.bincount(g, M[:, j], G) for j in range(M.shape[1])])[g] / cnt[g, None]


def fe_res_np(M, pid, sid, lev=False):
    """Residuals on provider + subject FE (same algebra as scripts/76 fe_resid) and, optionally, the hat diagonal."""
    G, S = pid.max() + 1, sid.max() + 1
    Mw = _dm_np(M, pid, G)
    Sd = np.zeros((len(sid), S))
    Sd[np.arange(len(sid)), sid] = 1.0
    St = _dm_np(Sd[:, 1:], pid, G)
    Q = np.linalg.pinv(St.T @ St, hermitian=True)
    R = Mw - St @ (Q @ (St.T @ Mw))
    if not lev:
        return R
    cnt = np.bincount(pid, minlength=G).astype(float)
    return R, 1.0 / cnt[pid] + ((St @ Q) * St).sum(axis=1)


def scores_np(v, sid, kind):
    """Within-subject scores, standardised (ddof 0): 'b' = Blom normal scores (midranks), 'l' = linear z."""
    out = np.zeros(len(v))
    for s in range(sid.max() + 1):
        ix = np.flatnonzero(sid == s)
        x = blom(v[ix]) if kind == "b" else np.asarray(v[ix], float)
        sd = x.std()
        out[ix] = (x - x.mean()) / sd if sd > 0 else 0.0
    return out


def corrmat(r3):
    C = np.array([[1.0, r3[0], r3[1]], [r3[0], 1.0, r3[2]], [r3[1], r3[2], 1.0]])
    assert np.linalg.eigvalsh(C).min() > 1e-6, ("correlation matrix not positive definite", r3)
    return C


def rnd5(k, f):
    """LEO publication of a band count: 0 -> no row (0); 1-2 -> 'low' (coded f); else rounded to a multiple of 5."""
    out = 5.0 * np.round(k / 5.0)
    out = np.where((k >= 3) & (out == 0), 5.0, out)
    out = np.where((k >= 1) & (k <= 2), float(f), out)
    return np.where(k == 0, 0.0, out)


def sim_data(rng, par) -> dict:
    """One simulated data set on the real layout. Latent T_k = u_k[provider] + v_k[programme] for k = REF, pay, intake,
    var(u_k) = pi_k, var(v_k) = 1 - pi_k, corr(u) = rho_b, corr(v) = rho_w. REF 2021 and REF 2014 = T_ref + independent
    normal error (SD sig_ref). Pay: per released cohort, log median = sig_pay * T_pay + normal noise with the cohort's
    own scripts/73-style variance; mean over released cohorts. Intake: per cohort, graduates with >= 360 points ~
    Binomial(known graduates of that cohort, expit(mu_s + kappa_s (T_int + tau e_c))), e_c independent N(0, 1) per
    programme and cohort (cohort-to-cohort variation of the intake), split into bands 1 / 2 and the other bands
    multinomially with the subject's pooled band shares, each band count published as LEO does (rounded to 5,
    1-2 = 'low' coded 1), share pooled over cohorts as the real measure."""
    I = _SIM
    n, G = I["n"], I["G"]
    pi = np.asarray(par["pi"])
    u = rng.multivariate_normal(np.zeros(3), corrmat(par["rho_b"]), size=G) * np.sqrt(pi)
    v = rng.multivariate_normal(np.zeros(3), corrmat(par["rho_w"]), size=n) * np.sqrt(1 - pi)
    T = u[I["pid"]] + v
    e = rng.standard_normal((n, 2)) * par["sig_ref"]
    ref21, ref14 = T[:, 0] + e[:, 0], T[:, 0] + e[:, 1]
    ly = I["sig_pay"][:, None] * T[:, 1][:, None] + rng.standard_normal((n, 4)) * I["se"]
    ly = np.where(I["has_med"], ly, np.nan)
    pay = np.nanmean(ly, axis=1)
    Tc = T[:, 2][:, None] + par["tau"] * rng.standard_normal((n, 4))
    lp = np.asarray(par["mu"])[I["sid"]][:, None] + np.asarray(par["kappa"])[I["sid"]][:, None] * Tc
    p = 1.0 / (1.0 + np.exp(-lp))
    top = rng.binomial(I["NT"], p)
    p1 = rng.binomial(top, I["pa1"][:, None])
    p2 = top - p1
    low = rng.multinomial(I["NT"] - top, I["LOWP"][:, None, :])
    R12 = rnd5(p1, 1) + rnd5(p2, 1)
    RL = rnd5(low, 1).sum(axis=2)

    def share(mask):
        num = (R12 * mask).sum(axis=1)
        den = num + (RL * mask).sum(axis=1)
        return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)
    allm = np.ones(4, bool)
    intk, hA, hB = share(allm), share(HA_MASK), share(~HA_MASK)
    nmiss = int(np.isnan(intk).sum())
    if nmiss:                                   # a programme with no simulated graduate: subject median
        med = pd.Series(intk).groupby(I["sid"]).transform("median").to_numpy()
        intk = np.where(np.isnan(intk), med, intk)
    return dict(T=T, ref21=ref21, ref14=ref14, pay=pay, int=intk, hA=hA, hB=hB, nmiss=nmiss)


def sim_scores(X) -> dict:
    """Scores fixed for the data set (as the real pipeline: computed once, held fixed in the bootstrap)."""
    I = _SIM
    sid = I["sid"]
    var_p = pd.Series(X["pay"]).groupby(sid).transform(lambda v: v.var(ddof=0)).to_numpy()
    F = {"s2z": I["s2"] / var_p}
    ri = I["ref_idx"]
    sr = fac(sid[ri])
    okh = np.isfinite(X["hA"]) & np.isfinite(X["hB"])
    hi_ = np.flatnonzero(okh)
    cnt = pd.Series(sid[hi_]).map(pd.Series(sid[hi_]).value_counts()).to_numpy()
    hi_ = hi_[cnt >= 2]
    sh = fac(sid[hi_])
    F["pos_ref"] = np.full(I["n"], -1)
    F["pos_ref"][ri] = np.arange(len(ri))
    F["pos_h"] = np.full(I["n"], -1)
    F["pos_h"][hi_] = np.arange(len(hi_))
    for kind in ("b", "l"):
        F[kind] = dict(Z=np.column_stack([scores_np(X[k], sid, kind) for k in ("ref21", "pay", "int")]),
                       ZR=np.column_stack([scores_np(X[k][ri], sr, kind) for k in ("ref21", "ref14")]),
                       ZH=np.column_stack([scores_np(X[k][hi_], sh, kind) for k in ("hA", "hB")]))
    return F


def sim_eval(F, rows, newp) -> dict:
    """The G3 pipeline on a (possibly resampled) set of rows, Blom ('b') and linear ('l')."""
    I = _SIM
    sid = fac(I["sid"][rows])
    pid = fac(newp)
    S = sid.max() + 1
    cS = np.bincount(sid, minlength=S).astype(float)
    out = {}

    def subrel(pos, ZS):
        p_ = pos[rows]
        m = p_ >= 0
        R_ = fe_res_np(ZS[p_[m]], fac(newp[m]), fac(I["sid"][rows[m]]))
        return corr(R_[:, 0], R_[:, 1])
    for kind in ("b", "l"):
        Z = F[kind]["Z"][rows]
        Za = Z - np.column_stack([np.bincount(sid, Z[:, j], S) / cS for j in range(3)])[sid]
        Rw, h = fe_res_np(Z, pid, sid, lev=True)
        rel = {1: 1.0 - float(F["s2z"][rows] @ (1.0 - h)) / float(Rw[:, 1] @ Rw[:, 1]),
               0: subrel(F["pos_ref"], F[kind]["ZR"]), 2: sb(subrel(F["pos_h"], F[kind]["ZH"]))}
        for k_, nm in ((0, "ref"), (1, "pay"), (2, "int")):
            out[f"{kind}|rel_{nm}"] = rel[k_]
            out[f"{kind}|q_{nm}"] = float(Rw[:, k_] @ Rw[:, k_]) / float(Za[:, k_] @ Za[:, k_])
        for pair, (i, k) in PAIRS3.items():
            out[f"{kind}|a|{pair}"] = corr(Za[:, i], Za[:, k])
            out[f"{kind}|w|{pair}"] = corr(Rw[:, i], Rw[:, k])
            out[f"{kind}|wd|{pair}"] = disatt(out[f"{kind}|w|{pair}"], rel[i], rel[k])
    return out


def sim_task(args) -> dict:
    """One simulated data set: point statistics; with mode 'null' also the noise-free benchmarks; with mode 'size'
    also a provider bootstrap of the disattenuated within correlation and the pre-specified rule (i)."""
    ss, par, mode = args
    rng = np.random.default_rng(ss)
    I = _SIM
    X = sim_data(rng, par)
    F = sim_scores(X)
    n = I["n"]
    out = sim_eval(F, np.arange(n), I["pid"])
    out["nmiss"] = X["nmiss"]
    sid = I["sid"]
    # intake share moments per subject (calibration targets)
    sh = pd.Series(X["int"]).groupby(sid)
    out["int_mean"] = sh.mean().to_numpy()
    out["int_sd"] = sh.std(ddof=0).to_numpy()
    if mode == "null":
        for kind in ("b", "l"):
            Tz = np.column_stack([scores_np(X["T"][:, j], sid, kind) for j in range(3)])
            Rt = fe_res_np(Tz, I["pid"], sid)
            Zo = F[kind]["Z"]
            Ro = fe_res_np(Zo, I["pid"], sid)
            for k_, nm in ((0, "ref"), (1, "pay"), (2, "int")):
                out[f"{kind}|true_rel_{nm}"] = corr(Ro[:, k_], Rt[:, k_]) ** 2
            for pair, (i, k) in PAIRS3.items():
                out[f"{kind}|true_w|{pair}"] = corr(Rt[:, i], Rt[:, k])
    if mode == "size":
        G = I["G"]
        groups = I["groups"]
        bs = {f"{kind}|{pair}": [] for kind in ("b", "l") for pair in PAIRS3}
        for _ in range(SIM_SIZE_B):
            draw = rng.integers(G, size=G)
            rows = np.concatenate([groups[g] for g in draw])
            newp = np.concatenate([np.full(len(groups[g]), k) for k, g in enumerate(draw)])
            s = sim_eval(F, rows, newp)
            for kind in ("b", "l"):
                for pair in PAIRS3:
                    bs[f"{kind}|{pair}"].append(s[f"{kind}|wd|{pair}"])
        for kind in ("b", "l"):
            for pair in PAIRS3:
                v = np.asarray(bs[f"{kind}|{pair}"], float)
                hi = float(np.percentile(v[~np.isnan(v)], 97.5))
                out[f"{kind}|hi|{pair}"] = hi
                out[f"{kind}|rule_less|{pair}"] = float(hi < out[f"{kind}|a|{pair}"])
    return out


def sim_inputs(D: dict, Pa: pd.DataFrame) -> dict:
    """Real-layout inputs of the simulation (G3 cells): providers, subjects, REF 2014 subset, per-cohort pay noise,
    per-cohort known-band graduate counts ('low' counted as 1.5), the subjects' band shares."""
    d = D["d"]
    key = pd.MultiIndex.from_frame(d[["ukprn", "subject"]])
    a = D["pay_rows"]
    SE2 = a.pivot_table(index=["ukprn", "subject"], columns="cohort", values="se2").reindex(key).reindex(
        columns=s62.COHORTS).to_numpy()
    bands = s62.PA_ALL[:-1]
    x = Pa[Pa.band.isin(bands)]
    x = x.assign(cnt=x.num + 1.5 * x.nlow)
    NT = x.groupby(["ukprn", "subject", "cohort"]).cnt.sum().unstack("cohort").reindex(key).reindex(
        columns=s62.COHORTS).fillna(0.0).to_numpy()
    NT = np.round(NT).astype(np.int64)
    xs = x[pd.MultiIndex.from_frame(x[["ukprn", "subject"]]).isin(key)]
    bs_ = xs.groupby(["subject", "band"]).cnt.sum().unstack("band").reindex(columns=bands).fillna(0.0)
    lowp = bs_[bands[2:]].div(bs_[bands[2:]].sum(axis=1), axis=0)
    pa1 = bs_.PA1 / (bs_.PA1 + bs_.PA2)
    sid = D["sid"]
    subs = sorted(d.subject.unique())
    assert list(pd.Index(subs)) == list(pd.Index(sorted(d.subject.unique())))
    var_pay = d.groupby("subject").pay.transform(lambda v: v.var(ddof=0)).to_numpy()
    s2 = D["s2_log"]
    sig_pay = np.sqrt(np.maximum(var_pay - pd.Series(s2).groupby(sid).transform("mean").to_numpy(), 1e-8))
    G = int(D["pid"].max() + 1)
    return dict(n=len(d), G=G, pid=D["pid"], sid=sid, groups=[np.flatnonzero(D["pid"] == g) for g in range(G)],
                ref_idx=D["ref_idx"], se=np.sqrt(np.nan_to_num(SE2, nan=0.0)), has_med=np.isfinite(SE2), s2=s2,
                sig_pay=sig_pay, NT=NT, LOWP=lowp.loc[d.subject].to_numpy(), pa1=pa1.loc[d.subject].to_numpy())


def _logit(p):
    p = np.clip(p, 1e-3, 1 - 1e-3)
    return np.log(p / (1 - p))


def run_g3_sim(D: dict, Pa: pd.DataFrame, U: dict, workers: int) -> dict:
    """Parametric bootstrap of H0: rho_within = rho_between (per pair), through the full G3 pipeline on the real
    layout. Nuisance parameters are calibrated by matching simulated means to the observed values (indirect inference,
    SIM_CAL_ROUNDS rounds of SIM_CAL_M data sets): provider shares pi_k to the within-provider variance shares of
    the normal scores, sig_ref to the REF test-retest, the intake logit location / scale per subject to the subject
    mean and SD of the share, and rho (= rho_b = rho_w) to the across-provider correlations. The null distribution
    of the within-provider correlation then comes from SIM_NULL data sets; p = (1 + #{null <= observed}) / (1 + N).
    A calibrated estimate of rho_within frees rho_w and matches the observed within-provider correlations as well.
    The cohort noise tau of the latent intake is calibrated to the observed split-half reliability of the intake.
    workers = 1 runs the data sets in this process (same results: every data set has its own seed)."""
    import multiprocessing as mp
    from contextlib import ExitStack
    from concurrent.futures import ProcessPoolExecutor
    inp = sim_inputs(D, Pa)
    pt = U["pt"]
    d = D["d"]
    a_obs = np.array([pt["across|REF-pay"], pt["across|REF-intake|int1"], pt["across|pay-intake|int1"]])
    w_obs = np.array([pt["within|REF-pay"], pt["within|REF-intake|int1"], pt["within|pay-intake|int1"]])
    q_obs = np.asarray(D["q_obs"], float)
    rel_ref_obs = pt["rel_ref"]
    rel_int_obs = pt["rel_int1"]
    g_ = d.groupby("subject").top_l1
    m_obs, s_obs = g_.mean().to_numpy(), g_.std(ddof=0).to_numpy()
    lg = pd.Series(_logit(d.top_l1.to_numpy())).groupby(D["sid"])
    par = dict(pi=np.clip(1 - q_obs, 0.05, 0.95), sig_ref=float(np.sqrt(q_obs[0] * (1 / rel_ref_obs - 1))),
               rho_b=np.clip(a_obs / 0.9, -0.9, 0.9), rho_w=np.clip(a_obs / 0.9, -0.9, 0.9),
               mu=lg.median().to_numpy(), kappa=lg.std(ddof=0).to_numpy(), tau=0.5)
    pairs = list(PAIRS3)

    def mean_of(res, key):
        return np.mean([r[key] for r in res], axis=0)

    def update(par, res, free_w, fix_tau=False):
        """Damped multiplicative (additive for mu) moment-matching step."""
        q = np.array([mean_of(res, f"b|q_{k}") for k in ("ref", "pay", "int")])
        par = dict(par)
        dm_ = SIM_DAMP
        par["pi"] = np.clip(1 - (1 - par["pi"]) * (q_obs / q) ** dm_, 0.02, 0.98)
        rr = mean_of(res, "b|rel_ref")
        par["sig_ref"] = float(par["sig_ref"] * ((1 / rel_ref_obs - 1) / (1 / rr - 1)) ** (0.5 * dm_))
        ri = mean_of(res, "b|rel_int")
        if not fix_tau:
            par["tau"] = float(max(0.02, par["tau"] * ((1 / rel_int_obs - 1) / (1 / ri - 1)) ** dm_))
        a_ = np.array([mean_of(res, f"b|a|{p_}") for p_ in pairs])
        par["mu"] = par["mu"] + dm_ * (_logit(m_obs) - _logit(mean_of(res, "int_mean")))
        par["kappa"] = par["kappa"] * (s_obs / mean_of(res, "int_sd")) ** dm_
        if free_w:
            w_ = np.array([mean_of(res, f"b|w|{p_}") for p_ in pairs])
            par["rho_b"] = np.clip(par["rho_b"] * (a_obs / a_) ** dm_, -0.95, 0.95)
            par["rho_w"] = np.clip(par["rho_w"] * (w_obs / w_) ** dm_, -0.95, 0.95)
        else:
            par["rho_b"] = par["rho_w"] = np.clip(par["rho_b"] * (a_obs / a_) ** dm_, -0.95, 0.95)
        return par

    def fit_summary(res):
        return dict(a=np.array([mean_of(res, f"b|a|{p_}") for p_ in pairs]),
                    w=np.array([mean_of(res, f"b|w|{p_}") for p_ in pairs]),
                    q=np.array([mean_of(res, f"b|q_{k}") for k in ("ref", "pay", "int")]),
                    rel_ref=mean_of(res, "b|rel_ref"), rel_int=mean_of(res, "b|rel_int"),
                    rel_int_l=mean_of(res, "l|rel_int"),
                    a_l=np.array([mean_of(res, f"l|a|{p_}") for p_ in pairs]),
                    int_mean=mean_of(res, "int_mean"), int_sd=mean_of(res, "int_sd"))
    ctx = mp.get_context("spawn")
    _trim()
    out = dict(obs=dict(a=a_obs, w=w_obs, q=q_obs, rel_ref=rel_ref_obs, rel_int=rel_int_obs, m=m_obs, s=s_obs),
               workers=workers)
    with ExitStack() as st_:
        if workers > 1:
            ex = st_.enter_context(ProcessPoolExecutor(max_workers=workers, mp_context=ctx, initializer=_sim_init,
                                                       initargs=(inp,)))

            def run(seeds, par, mode):
                return list(ex.map(sim_task, [(s_, par, mode) for s_ in seeds], chunksize=4))
        else:
            _sim_init(inp)

            def run(seeds, par, mode):
                return [sim_task((s_, par, mode)) for s_ in seeds]
        for tag, free_w, kid in (("null", False, "g3_sim_cal"), ("alt", True, "g3_sim_alt")):
            if tag == "alt":
                par = dict(out["null"]["par"])
                w0 = np.array([mean_of(out["null"]["res"], f"b|w|{p_}") for p_ in pairs])
                par["rho_w"] = np.clip(par["rho_w"] * w_obs / w0, -0.95, 0.95)
            rounds = _KIDS[kid].spawn(SIM_CAL_ROUNDS)
            hist = []
            for r_, rs in enumerate(rounds):
                res = run(rs.spawn(SIM_CAL_M), par, "cal")
                hist.append(dict(par={k: np.array(v, float) for k, v in par.items()}, fit=fit_summary(res)))
                par = update(par, res, free_w)
            if tag == "null":
                stage(f"G3 rev. 1: null calibrated (rho = {np.round(par['rho_b'], 3)}); {SIM_NULL} null draws")
                res = run(_KIDS["g3_sim_null"].spawn(SIM_NULL), par, "null")
                stage(f"G3 rev. 1: size of the pre-specified rule, {SIM_SIZE} data sets x {SIM_SIZE_B} replicates")
                size = run(_KIDS["g3_sim_size"].spawn(SIM_SIZE), par, "size")
                out["null"] = dict(par=par, hist=hist, res=res, size=size, fit=fit_summary(res))
            else:
                stage(f"G3 rev. 1: alternative calibrated (rho_w = {np.round(par['rho_w'], 3)}); {SIM_ALTFIN} draws")
                res = run(_KIDS["g3_sim_altfin"].spawn(SIM_ALTFIN), par, "cal")
                out["alt"] = dict(par=par, hist=hist, res=res, fit=fit_summary(res))
        # sensitivity (revision 1): the same null calibration with the cohort noise of the intake held at its floor
        # (tau = 0.02, not matched to the observed split-half), then the size check; shows how the size of the
        # pre-specified rule depends on how much intake noise the model carries
        par = dict(out["null"]["hist"][0]["par"])
        par["tau"] = 0.02
        stage(f"G3 rev. 1: sensitivity with tau = 0.02: calibration and {SIM_SIZE} size data sets")
        for rs in _KIDS["g3_sim_cal_t0"].spawn(SIM_CAL_ROUNDS):
            res = run(rs.spawn(SIM_CAL_M), par, "cal")
            par = update(par, res, False, fix_tau=True)
        size = run(_KIDS["g3_sim_size_t0"].spawn(SIM_SIZE), par, "size")
        out["tau0"] = dict(par=par, size=size, fit=fit_summary(size))
    return out


# =============================================================================================================
# G3 US analogue: F-pay on the scripts/58 main-spec cells
# =============================================================================================================
def us_noise() -> pd.DataFrame:
    """scripts/73 programme SE of the Scorecard 4-yr median (se_main), per (field, inst_key)."""
    ps = s73.pseo_rows()
    disp = s73.field_dispersion(ps)
    prog = s73.pseo_prog_disp(ps)
    sc = s73.scorecard_programs(disp, prog)
    return sc[["field", "inst_key", "earnings", "se_main"]]


def us_g3_data(M0: dict, rel: dict, noise: pd.DataFrame) -> dict:
    d = M0["d"].reset_index(drop=True)
    g = M0["groups"]
    cnt = M0["cnt"]
    ic = pd.factorize(d.inst_key)[0]
    assert np.array_equal(ic, g)
    zF = ns_within(d.assign(ly=np.log(d.earnings)), "prestige_score", "field", 1)
    zY = ns_within(d.assign(ly=np.log(d.earnings)), "ly", "field", 1)

    def dm(v):
        s = np.bincount(g, v, cnt.size)
        return v - (s / cnt)[g]
    j = M0["names"].index("beta")
    Xmain = np.delete(M0["X"], j, axis=1)
    fe_cols = [i for i, nm in enumerate(M0["names"]) if nm.startswith("g_")]
    Xfe = M0["X"][:, fe_cols]
    nz = d.merge(noise, on=["field", "inst_key"], how="left", suffixes=("", "_73"))
    assert np.allclose(nz.earnings, nz.earnings_73, rtol=1e-12, atol=0), "scripts/73 programmes differ"
    s2_log = (nz.se_main / nz.earnings).to_numpy() ** 2
    var_ly = d.assign(ly=np.log(d.earnings)).groupby("field").ly.transform(lambda v: v.var(ddof=1)).to_numpy()
    s2z = s2_log / var_ly
    rf, e1 = {}, {}
    for tag in ("LB", "EXT"):
        r_ = np.array([rel[tag].get(f, np.nan) for f in M0["fields"]])
        r_ = np.where(np.isfinite(r_), r_, np.nanmean(r_))[M0["code"]]
        rf[tag] = (1 - r_) * (1 - 1 / cnt[g])
        e1[tag] = 1 - r_                                   # revision 1: error variance per cell (full-leverage lambda)
    fields = d.field.to_numpy()
    rho_sp = float(np.mean([spearmanr(x.prestige_score, x.earnings)[0] for _, x in d.groupby("field")]))
    return dict(d=d, g=g, G=int(cnt.size), cnt=cnt, zF=zF, zY=zY, zFd=dm(zF), zYd=dm(zY), X={"main": Xmain, "fe": Xfe},
                s2z=s2z, err=rf, e1=e1, fcode=pd.factorize(fields, sort=True)[0], rho_sp=rho_sp, s2_log=s2_log,
                n_noise=int(np.isfinite(s2_log).sum()))


def us_prep(D: dict) -> dict:
    """Per-institution cross-products for the cluster bootstrap (rows are already demeaned within institution)."""
    G, g = D["G"], D["g"]
    idx = [np.flatnonzero(g == k) for k in range(G)]
    P = {}
    for nm, X in D["X"].items():
        A = _xtx_stack(X, idx)
        bF = np.stack([X[r].T @ D["zFd"][r] for r in idx])
        bY = np.stack([X[r].T @ D["zYd"][r] for r in idx])
        P[nm] = (A, bF, bY)
    P["sFF"] = np.bincount(g, D["zFd"] ** 2, G)
    P["sYY"] = np.bincount(g, D["zYd"] ** 2, G)
    P["sFY"] = np.bincount(g, D["zFd"] * D["zYd"], G)
    P["err"] = {k: np.bincount(g, v, G) for k, v in D["err"].items()}
    P["inv_n"] = 1.0 / D["cnt"][g]
    return P


def us_stats(D: dict, P: dict, c: np.ndarray) -> dict:
    """c = times each institution is drawn (ones for the point estimate)."""
    out = {}
    w = c[D["g"]]
    # across: pooled Pearson of the within-field normal scores, field means removed (weighted)
    fc = D["fcode"]
    K = fc.max() + 1
    sw = np.bincount(fc, w, K)
    ok = sw > 0
    mF = np.where(ok, np.bincount(fc, w * D["zF"], K) / np.where(ok, sw, 1), 0.0)
    mY = np.where(ok, np.bincount(fc, w * D["zY"], K) / np.where(ok, sw, 1), 0.0)
    a, b = D["zF"] - mF[fc], D["zY"] - mY[fc]
    out["across"] = float((w * a) @ b / np.sqrt(((w * a) @ a) * ((w * b) @ b)))
    sFF, sYY, sFY = c @ P["sFF"], c @ P["sYY"], c @ P["sFY"]
    for nm in ("main", "fe"):
        A, bF, bY = P[nm]
        XtX = np.tensordot(c, A, axes=1)
        keep = np.diag(XtX) > 1e-10
        Q = np.linalg.pinv(XtX[np.ix_(keep, keep)], hermitian=True)
        vF, vY = (c @ bF)[keep], (c @ bY)[keep]
        rFF = sFF - vF @ Q @ vF
        rYY = sYY - vY @ Q @ vY
        rFY = sFY - vF @ Q @ vY
        r = float(rFY / np.sqrt(rFF * rYY))
        Xk = D["X"][nm][:, keep]
        h = ((Xk @ Q) * Xk).sum(axis=1)
        Mii = 1.0 - P["inv_n"] - h
        out[f"within|{nm}"] = r
        for tag in ("LB", "EXT"):
            out[f"lam_{tag}|{nm}"] = float(1.0 - (c @ P["err"][tag]) / rFF)
        out[f"rel_pay|{nm}"] = float(1.0 - (w * D["s2z"] * Mii).sum() / rYY)
        out[f"dis|{nm}"] = disatt(r, out[f"lam_LB|{nm}"], 1.0)
        out[f"dis_ext|{nm}"] = disatt(r, out[f"lam_EXT|{nm}"], 1.0)
        out[f"dis_pay|{nm}"] = disatt(r, out[f"lam_LB|{nm}"], out[f"rel_pay|{nm}"])
    # revision 2: across-level reliabilities (field-demeaned scores) and the across correlation corrected by them
    nf = np.bincount(fc, w, K)[fc]
    for tag in ("LB", "EXT"):
        out[f"relF_a_{tag}"] = float(1.0 - (w * D["e1"][tag] * (1 - 1 / np.maximum(nf, 1))).sum() / ((w * a) @ a))
    out["relY_a"] = float(1.0 - (w * D["s2z"] * (1 - 1 / np.maximum(nf, 1))).sum() / ((w * b) @ b))
    out["across_dis"] = disatt(out["across"], out["relF_a_LB"], out["relY_a"])
    out["across_dis_ext"] = disatt(out["across"], out["relF_a_EXT"], out["relY_a"])
    # revision 1: residual-F reliability with the full leverage (error variance kept by the annihilator, M_ii),
    # consistent with the pay reliability; scripts/58's lambda keeps only the institution-FE part (1 - 1/n_i)
    for nm in ("main", "fe"):
        A, bF, bY = P[nm]
        XtX = np.tensordot(c, A, axes=1)
        keep = np.diag(XtX) > 1e-10
        Q = np.linalg.pinv(XtX[np.ix_(keep, keep)], hermitian=True)
        vF = (c @ bF)[keep]
        rFF = sFF - vF @ Q @ vF
        Xk = D["X"][nm][:, keep]
        Mii = 1.0 - P["inv_n"] - ((Xk @ Q) * Xk).sum(axis=1)
        for tag in ("LB", "EXT"):
            out[f"lamfull_{tag}|{nm}"] = float(1.0 - (w * D["e1"][tag] * Mii).sum() / rFF)
        r = out[f"within|{nm}"]
        out[f"disfull|{nm}"] = disatt(r, out[f"lamfull_LB|{nm}"], 1.0)
        out[f"disfull_pay|{nm}"] = disatt(r, out[f"lamfull_LB|{nm}"], out[f"rel_pay|{nm}"])
    return out


def run_g3_us(D: dict) -> dict:
    P = us_prep(D)
    G = D["G"]
    pt = us_stats(D, P, np.ones(G))
    keys = list(pt)
    BS = np.full((B, len(keys)), np.nan)
    for b, rng in enumerate(rep_gens("g3_us")):
        c = np.bincount(rng.integers(0, G, G), minlength=G).astype(float)
        s = us_stats(D, P, c)
        BS[b] = [s[k] for k in keys]
    # revision 1: delete-one-institution jackknife (the reliabilities' bootstrap percentiles sit below their point
    # estimates: resampled institutions leave the 235 regressors fewer distinct institutions)
    JK = np.full((G, len(keys)), np.nan)
    for g in range(G):
        c = np.ones(G)
        c[g] = 0.0
        s = us_stats(D, P, c)
        JK[g] = [s[k] for k in keys]
    return dict(pt=pt, keys=keys, bs=BS, jk=JK, n=len(D["d"]), G=G, k=int(D["d"].field.nunique()))


def jack(est: float, v: np.ndarray) -> dict:
    """Delete-one jackknife SE and normal 95% interval (revision 1)."""
    v = np.asarray(v, float)
    G = len(v)
    se = float(np.sqrt((G - 1) / G * ((v - v.mean()) ** 2).sum()))
    return dict(est=float(est), lo=est - 1.959963984540054 * se, hi=est + 1.959963984540054 * se, se=se,
                mde=MDE_K * se)


# =============================================================================================================
# G3 US, revision 2 (added after results were seen): like-for-like FE-only contrast and a simulation-calibrated
# test of rho_within = rho_between on the real US layout (worker-safe: numpy / pandas / scipy only)
# =============================================================================================================
_USSIM: dict = {}
US_PAIR = "F-pay"


def _ussim_init(inp: dict):
    _USSIM.clear()
    _USSIM.update(inp)


def us_sim_inputs(D: dict, rel_tag: str) -> dict:
    """Real US layout (scripts/58 main-spec cells): institutions, fields, the FE-only design (field dummies demeaned
    within institution) and its per-institution cross-products, F's error variance per cell (1 - relF, scripts/56
    LB or EXT), the scripts/73 noise variance of each programme's log median, and each field's pay signal SD."""
    d = D["d"]
    g, G, cnt = D["g"], D["G"], D["cnt"]
    X = D["X"]["fe"]
    idx = [np.flatnonzero(g == k) for k in range(G)]
    ly = np.log(d.earnings.to_numpy(float))
    fc = D["fcode"]
    K = int(fc.max() + 1)
    s2 = D["s2_log"]
    var_f = pd.Series(ly).groupby(fc).transform(lambda v: v.var(ddof=1)).to_numpy()
    sig = np.sqrt(np.maximum(var_f - pd.Series(s2).groupby(fc).transform("mean").to_numpy(), 1e-8))
    return dict(n=len(d), G=G, K=K, g=g, fc=fc, cnt=cnt, inv_n=1.0 / cnt[g], X=X, A=_xtx_stack(X, idx),
                idx=idx, e1=D["e1"][rel_tag], s2=s2, sig=sig)


def _us_blom(v, fc, K):
    out = np.zeros(len(v))
    for f in range(K):
        ix = np.flatnonzero(fc == f)
        x = blom(v[ix])
        out[ix] = (x - x.mean()) / x.std(ddof=1)
    return out


def us_sim_fixed(zF, zY, s2_log) -> dict:
    """Quantities fixed for a data set (scores computed once and held fixed in its bootstrap, as for the real data)."""
    I = _USSIM
    g, G, cnt, fc = I["g"], I["G"], I["cnt"], I["fc"]
    F = dict(zF=zF, zY=zY)
    F["s2z"] = s2_log
    zFd = zF - (np.bincount(g, zF, G) / cnt)[g]
    zYd = zY - (np.bincount(g, zY, G) / cnt)[g]
    X = I["X"]
    F["bF"] = np.stack([X[r].T @ zFd[r] for r in I["idx"]])
    F["bY"] = np.stack([X[r].T @ zYd[r] for r in I["idx"]])
    F["sFF"], F["sYY"], F["sFY"] = (np.bincount(g, zFd ** 2, G), np.bincount(g, zYd ** 2, G),
                                     np.bincount(g, zFd * zYd, G))
    return F


def us_sim_eval(F, c) -> dict:
    """FE-only pipeline with institution weights c: across (within-field pooled Pearson) and within (institution +
    field FE) correlation of the normal scores; lambda (scripts/58 formula and full leverage), pay reliability,
    across-level reliabilities, disattenuated values at both levels."""
    I = _USSIM
    g, fc, K = I["g"], I["fc"], I["K"]
    w = c[g]
    sw = np.bincount(fc, w, K)
    ok = sw > 0
    mF = np.where(ok, np.bincount(fc, w * F["zF"], K) / np.where(ok, sw, 1), 0.0)
    mY = np.where(ok, np.bincount(fc, w * F["zY"], K) / np.where(ok, sw, 1), 0.0)
    a_, b_ = F["zF"] - mF[fc], F["zY"] - mY[fc]
    aa, bb = float((w * a_) @ a_), float((w * b_) @ b_)
    out = {"a": float((w * a_) @ b_ / np.sqrt(aa * bb))}
    nf = sw[fc]
    out["relF_a"] = 1.0 - float((w * I["e1"] * (1 - 1 / np.maximum(nf, 1))).sum()) / aa
    out["relY_a"] = 1.0 - float((w * F["s2z"] * (1 - 1 / np.maximum(nf, 1))).sum()) / bb
    XtX = np.tensordot(c, I["A"], axes=1)
    keep = np.diag(XtX) > 1e-10
    Q = np.linalg.pinv(XtX[np.ix_(keep, keep)], hermitian=True)
    vF, vY = (c @ F["bF"])[keep], (c @ F["bY"])[keep]
    rFF = c @ F["sFF"] - vF @ Q @ vF
    rYY = c @ F["sYY"] - vY @ Q @ vY
    rFY = c @ F["sFY"] - vF @ Q @ vY
    r = float(rFY / np.sqrt(rFF * rYY))
    Xk = I["X"][:, keep]
    Mii = 1.0 - I["inv_n"] - ((Xk @ Q) * Xk).sum(axis=1)
    out["w"] = r
    out["lam58"] = float(1.0 - (w * I["e1"] * (1 - I["inv_n"])).sum() / rFF)
    out["lamfull"] = float(1.0 - (w * I["e1"] * Mii).sum() / rFF)
    out["relY_w"] = float(1.0 - (w * F["s2z"] * Mii).sum() / rYY)
    out["qF"] = float(rFF / aa)
    out["qY"] = float(rYY / bb)
    out["wd"] = disatt(r, out["lam58"], 1.0)                            # the pre-specified correction (F only)
    out["wd_both"] = disatt(r, out["lamfull"], out["relY_w"])
    out["ad_both"] = disatt(out["a"], out["relF_a"], out["relY_a"])
    return out


def us_sim_task(args) -> dict:
    """One simulated US data set: latent T_k = u_k[institution] + v_k[programme] (k = F, pay), var(u) = pi_k,
    corr(u) = rho_b, corr(v) = rho_w; observed F = sqrt(rel_f) T_F + sqrt(1 - rel_f) e (classical error, the
    scripts/56 reliability of the field); log pay = sig_f T_pay + normal noise with the programme's scripts/73
    variance. Optionally a provider bootstrap of the pre-specified correction and rule (mode 'size')."""
    ss, par, mode = args
    I = _USSIM
    rng = np.random.default_rng(ss)
    n, G = I["n"], I["G"]
    pi = np.asarray(par["pi"])
    Cb = np.array([[1.0, par["rho_b"]], [par["rho_b"], 1.0]])
    Cw = np.array([[1.0, par["rho_w"]], [par["rho_w"], 1.0]])
    u = rng.multivariate_normal(np.zeros(2), Cb, size=G) * np.sqrt(pi)
    v = rng.multivariate_normal(np.zeros(2), Cw, size=n) * np.sqrt(1 - pi)
    T = u[I["g"]] + v
    Fo = np.sqrt(1 - I["e1"]) * T[:, 0] + np.sqrt(I["e1"]) * rng.standard_normal(n)
    y = I["sig"] * T[:, 1] + np.sqrt(I["s2"]) * rng.standard_normal(n)
    zF, zY = _us_blom(Fo, I["fc"], I["K"]), _us_blom(y, I["fc"], I["K"])
    var_y = pd.Series(y).groupby(I["fc"]).transform(lambda x: x.var(ddof=1)).to_numpy()
    F = us_sim_fixed(zF, zY, I["s2"] / var_y)
    out = us_sim_eval(F, np.ones(G))
    if mode == "size":
        hi = []
        for _ in range(SIM_SIZE_B):
            c = np.bincount(rng.integers(0, G, G), minlength=G).astype(float)
            hi.append(us_sim_eval(F, c)["wd"])
        hv = np.asarray(hi, float)
        out["hi"] = float(np.percentile(hv[~np.isnan(hv)], 97.5))
        out["rule_less"] = float(out["hi"] < out["a"])
    return out


def run_us_sim(D: dict, US: dict, workers: int) -> dict:
    """Revision 2: parametric bootstrap of H0 rho_within = rho_between for US F-pay on the FE-only contrast, with
    F's reliability at the scripts/56 lower bound (primary) and at the extrapolated value (sensitivity). Calibration
    as for the UK (damped moment matching): pi_F, pi_pay to the observed within-institution variance shares of the
    normal scores, rho (null) to the observed across correlation; alternative: rho_b and rho_w free, matched to
    the observed across and within correlations."""
    import multiprocessing as mp
    from contextlib import ExitStack
    from concurrent.futures import ProcessPoolExecutor
    pt = US["pt"]
    a_obs, w_obs = pt["across"], pt["within|fe"]
    P_ = us_prep(D)
    st = us_stats(D, P_, np.ones(D["G"]))
    del P_
    out = {"workers": workers, "obs": dict(a=a_obs, w=w_obs)}
    for tag, kids in (("LB", ("us_sim_cal", "us_sim_null", "us_sim_size", "us_sim_alt", "us_sim_altfin")),
                      ("EXT", ("us_sim_cal_ext", "us_sim_null_ext", "us_sim_size_ext", "us_sim_alt_ext",
                               "us_sim_altfin_ext"))):
        inp = us_sim_inputs(D, tag)
        # observed within-institution variance shares of the two normal scores on the FE-only design
        _ussim_init(inp)
        Fobs = us_sim_fixed(D["zF"], D["zY"], D["s2z"])
        ob = us_sim_eval(Fobs, np.ones(D["G"]))
        assert abs(ob["a"] - a_obs) < 1e-9 and abs(ob["w"] - w_obs) < 1e-9
        assert abs(ob["lam58"] - st[f"lam_{tag}|fe"]) < 1e-9 and abs(ob["lamfull"] - st[f"lamfull_{tag}|fe"]) < 1e-9
        q_obs = np.array([ob["qF"], ob["qY"]])
        res_obs = ob
        par = dict(pi=np.clip(1 - q_obs, 0.05, 0.95), rho_b=float(min(0.95, a_obs / 0.8)),
                   rho_w=float(min(0.95, a_obs / 0.8)))

        def mean_of(res, key):
            return float(np.mean([r[key] for r in res]))

        def update(par, res, free_w):
            par = dict(par)
            q = np.array([mean_of(res, "qF"), mean_of(res, "qY")])
            par["pi"] = np.clip(1 - (1 - par["pi"]) * (q_obs / q) ** SIM_DAMP, 0.02, 0.98)
            rb = float(np.clip(par["rho_b"] * (a_obs / mean_of(res, "a")) ** SIM_DAMP, -0.95, 0.95))
            if free_w:
                par["rho_w"] = float(np.clip(par["rho_w"] * (w_obs / mean_of(res, "w")) ** SIM_DAMP, -0.95, 0.95))
                par["rho_b"] = rb
            else:
                par["rho_b"] = par["rho_w"] = rb
            return par
        R = {"obs": res_obs, "q_obs": q_obs}
        ctx_ = mp.get_context("spawn")
        _trim()
        with ExitStack() as st_:
            if workers > 1:
                ex = st_.enter_context(ProcessPoolExecutor(max_workers=workers, mp_context=ctx_,
                                                           initializer=_ussim_init, initargs=(inp,)))

                def run(seeds, par, mode):
                    return list(ex.map(us_sim_task, [(s_, par, mode) for s_ in seeds], chunksize=4))
            else:
                def run(seeds, par, mode):
                    return [us_sim_task((s_, par, mode)) for s_ in seeds]
            for phase, free_w, kid in (("null", False, kids[0]), ("alt", True, kids[3])):
                if phase == "alt":
                    par = dict(R["null"]["par"])
                    par["rho_w"] = float(np.clip(par["rho_w"] * w_obs / mean_of(R["null"]["res"], "w"), -0.95, 0.95))
                for rs in _KIDS[kid].spawn(SIM_CAL_ROUNDS):
                    res = run(rs.spawn(SIM_CAL_M), par, "cal")
                    par = update(par, res, free_w)
                if phase == "null":
                    stage(f"G3 US rev. 2 [{tag}]: null calibrated (rho = {par['rho_b']:.3f}); {SIM_NULL} null draws")
                    res = run(_KIDS[kids[1]].spawn(SIM_NULL), par, "null")
                    size = run(_KIDS[kids[2]].spawn(SIM_SIZE), par, "size")
                    R["null"] = dict(par=par, res=res, size=size)
                else:
                    res = run(_KIDS[kids[4]].spawn(SIM_ALTFIN), par, "cal")
                    R["alt"] = dict(par=par, res=res)
        out[tag] = R
    return out


# =============================================================================================================
# G4: Oster (2019) bound on the UK within-university REF slope, intake as the observed control
# =============================================================================================================
def oster_stats(y, z, pid, sid, C, s2=None) -> dict:
    bs_, _, Us = s76.fe_point(y[:, None], z, pid, sid)
    bl_, _, Ul = s76.fe_point(y[:, None], z, pid, sid, C)
    b_s, b_l = float(bs_[0]), float(bl_[0])
    sst = float(((y - y.mean()) ** 2).sum())
    yw = s76.fe_resid(y[:, None], pid, sid)[:, 0]
    ssw = float(yw @ yw)
    rss_s, rss_l = float(Us[:, 0] @ Us[:, 0]), float(Ul[:, 0] @ Ul[:, 0])
    out = dict(b_short=b_s, b_long=b_l)
    # exploratory: the R-squared that pay could reach if everything but its sampling noise were explained
    noise = dict(tot=float(s2.sum()) / sst, win=float((s2 * (1 - fe2_leverage(pid, sid))).sum()) / ssw)
    for tag, ss in (("tot", sst), ("win", ssw)):
        r_s, r_l = 1 - rss_s / ss, 1 - rss_l / ss
        out[f"R_short_{tag}"], out[f"R_long_{tag}"] = r_s, r_l
        for rt, rmax in (("13", min(1.0, 1.3 * r_l)), ("1", 1.0), ("n", 1.0 - noise[tag])):
            out[f"rmax_{rt}_{tag}"] = rmax
            den = (b_s - b_l) * (rmax - r_l)
            out[f"delta_{rt}_{tag}"] = float(b_l * (r_l - r_s) / den) if den != 0 else np.nan
            out[f"bstar_{rt}_{tag}"] = float(b_l - (b_s - b_l) * (rmax - r_l) / (r_l - r_s)) if r_l != r_s else np.nan
    return out


def run_g4(P: pd.DataFrame, A: pd.DataFrame) -> dict:
    d5 = s76_fe_sample(P, ["clean"], ["ref_gpa", "pay", "top"], extra_z=("top", "top_l1"))
    d5 = d5.sort_values(["ukprn", "subject"]).reset_index(drop=True)
    s2, _, _ = pay_noise(A, d5)
    pid, sid = fac(d5.ukprn), fac(d5.subject)
    G = int(pid.max() + 1)
    groups = [np.flatnonzero(pid == g) for g in range(G)]
    y, z = d5.pay.to_numpy(float), d5.z.to_numpy(float)
    res = {}
    gens = rep_gens("g4")
    draws = [g_.integers(G, size=G) for g_ in gens]
    for tag, col in (("low0", "z_top"), ("low1", "z_top_l1")):
        C = d5[inter(d5, [col])].to_numpy(float)
        pt = oster_stats(y, z, pid, sid, C, s2)
        keys = list(pt)
        BS = np.full((B, len(keys)), np.nan)
        for b, draw in enumerate(draws):
            rows = np.concatenate([groups[g] for g in draw])
            newp = np.concatenate([np.full(len(groups[g]), k) for k, g in enumerate(draw)])
            s = oster_stats(y[rows], z[rows], newp, fac(sid[rows]), C[rows], s2[rows])
            BS[b] = [s[k] for k in keys]
        res[tag] = dict(pt=pt, keys=keys, bs=BS)
    res["n"], res["G"], res["S"] = len(d5), G, int(sid.max() + 1)
    return res


# =============================================================================================================
# key-number rows (every number in the write-up comes from these rows or from the G2 table)
# =============================================================================================================
def f3(x, d=3):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else (
        "+inf" if np.isinf(x) and x > 0 else f"{x:+.{d}f}")


def fci(lo, hi, d=3):
    return f"[{f3(lo, d)}, {f3(hi, d)}]"


class Rows:
    def __init__(self):
        self.r = []

    def put(self, sec, q, spec, est, lo=np.nan, hi=np.nan, kind="", se=np.nan, mde=np.nan, status="", verdict="",
            k="", d=4):
        self.r.append(dict(section=sec, quantity=q, spec=spec, est=est, lo=lo, hi=hi, kind=kind, se=se, mde=mde,
                           status=status, verdict=verdict, k=str(k), d=d))

    def putb(self, sec, q, spec, s, kind="bootstrap", status="", verdict="", k="", d=4):
        self.put(sec, q, spec, s["est"], s["lo"], s["hi"], kind, s["se"], s["mde"], status, verdict, k, d)

    def get(self, sec, q) -> dict:
        m = [x for x in self.r if x["section"] == sec and x["quantity"] == q]
        assert len(m) == 1, (sec, q, len(m))
        return m[0]

    def ec(self, sec, q, d=None) -> str:
        x = self.get(sec, q)
        d = x["d"] if d is None else d
        return f"{f3(x['est'], d)} {fci(x['lo'], x['hi'], d)}" if np.isfinite(x["lo"]) else f3(x["est"], d)

    def e(self, sec, q, d=None) -> str:
        x = self.get(sec, q)
        return f3(x["est"], x["d"] if d is None else d)

    def ci(self, sec, q, d=None) -> str:
        x = self.get(sec, q)
        return fci(x["lo"], x["hi"], x["d"] if d is None else d)

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.r)


def g1_rule(change: dict, new: dict, orig: float) -> str:
    if change["lo"] <= 0 <= change["hi"] and new["est"] >= orig / 2:
        return "robust to production"
    if new["hi"] < orig / 2:
        return "production-driven"
    return "inconclusive"


def g1_explain(ch: dict, new: dict, orig: float) -> str:
    half = orig / 2
    inc = ch["lo"] <= 0 <= ch["hi"]
    return (f"the paired change interval {'includes' if inc else 'excludes'} 0; the new slope {f3(new['est'], 4)} is "
            f"{'at or above' if new['est'] >= half else 'below'} half the original ({f3(half, 4)}); its upper bound "
            f"{f3(new['hi'], 4)} is {'below' if new['hi'] < half else 'above'} that half")


def g3_rule(dis_hi: float, across: float, unit: str = "universities") -> str:
    return f"agree less within {unit}" if dis_hi < across else "cannot distinguish"


def collect(ctx: dict) -> Rows:
    R = Rows()
    R1, R2, U, US, G4 = ctx["g1"], ctx["g2"], ctx["g3uk"], ctx["g3us"], ctx["g4"]
    # ---------------- G1 ----------------
    t0 = ctx["t0rep"]
    R.put("check", "scripts/75 T0(a): mean Spearman(F, log production p)", f"{t0['n_r_p']} fields; published +0.441",
          t0["mean_r_p"], status="check", d=3)
    for nm, pub in (("c_F", "+0.387"), ("c_DC", "+0.325"), ("c_perp", "+0.232")):
        R.put("check", f"scripts/75 T0(b): mean {nm} on the scripts/28 common cells",
              f"{t0['k']} fields, {t0['cells']} cells; published {pub}", t0[nm], status="check", d=3)
    R.put("check", "largest final max |gradient| of the degree-corrected BT fits", "asserted < 1e-6",
          ctx["t0_gmax"], status="check", d=10)
    full, com = R1["full"], R1["com"]
    cov = R1["cov"]
    kfull = f"{full[0]['n']:,} programmes, {full[0]['G']} institutions, {full[0]['k']} fields"
    kcom = f"{com[0]['n']:,} programmes, {com[0]['G']} institutions, {com[0]['k']} fields"
    R.put("G1 coverage", "main-spec programmes with F_perp", "of the scripts/58 main-spec cells", cov["fperp"],
          k=f"of {cov['n']}", d=0)
    R.put("G1 coverage", "main-spec programmes with F_DC", "ranked department in the public field network",
          cov["fdc"], k=f"of {cov['n']}; {cov['fdc_inst']} of {cov['inst']} institutions", d=0)
    R.put("G1 coverage", "mean within-field Spearman(F, F_perp)", "main-spec cells", R1["rho"]["Fperp"], d=3)
    R.put("G1 coverage", "mean within-field Spearman(F, F_DC)", "main-spec cells with F_DC", R1["rho"]["FDCr"], d=3)

    def g1_block(sec, lab, res, i0, i1, k, status, rule_on, orig_status=None):
        o = res[i0]
        s0 = summ(o["beta"], o["bs"])
        s1 = summ(res[i1]["beta"], res[i1]["bs"])
        ch = summ(res[i1]["beta"] - o["beta"], res[i1]["bs"] - o["bs"])
        if orig_status is not None:
            R.putb(sec, "slope per SD: original F", f"{lab.split(',')[0]}; CR1 SE {res[i0]['se_cr1']:.4f}", s0, k=k,
                   status=orig_status)
        v = g1_rule(ch, s1, o["beta"]) if rule_on else ""
        R.putb(sec, f"slope per SD: {ctx['g1lab'][i1]}", f"{lab}; CR1 SE {res[i1]['se_cr1']:.4f}", s1, k=k,
               status=status)
        R.putb(sec, f"change: {ctx['g1lab'][i1]} minus original", f"{lab}; paired (same draws)", ch, k=k,
               status=status, verdict=v)
        R.put(sec, f"half the original slope ({ctx['g1lab'][i1]} rule)", lab, o["beta"] / 2, k=k, status=status)
        return v
    ctx["g1v"] = {}
    ctx["g1v"]["a"] = g1_block("G1 main", "full main-spec cells (A1)", full, 0, 1, kfull, "pre", True, "check")
    ctx["g1v"]["b"] = g1_block("G1 common", "common cells, (b)", com, 0, 2, kcom, "pre", True, "pre")
    ctx["g1v"]["a_com"] = g1_block("G1 common", "common cells, (a) (C1 sensitivity)", com, 0, 1, kcom, "expl. (C)", False)
    ctx["g1v"]["b_t"] = g1_block("G1 common", "common cells, (b) raw theta (C1 sensitivity)", com, 0, 3, kcom,
                                 "expl. (C)", False)
    # CS remainder
    csf, csc = R1["cs_full"], R1["cs_com"]
    for sec, lab, res, pairs, st in (("G1 CS", "common programmes, full cells", csf, [1], "pre"),
                                     ("G1 CS common", "common programmes, common cells", csc, [1, 2, 3], "pre")):
        o = res[0]
        k0 = f"{o['n_cs']} CS programmes; {o['keys'][3]:,} programmes, {o['keys'][2]} institutions"
        R.putb(sec, "CS remainder: original F", lab + "; 4/1/5-yr average", summ(o["beta"], o["bs"]), k=k0,
               status="check" if sec == "G1 CS" else "pre", d=3)
        for i in pairs:
            nm = ctx["g1lab"][i]
            stt = st if not (sec == "G1 CS common" and i in (1, 3)) else "expl. (C)"
            R.putb(sec, f"CS remainder: {nm}", lab, summ(res[i]["beta"], res[i]["bs"]), k=f"{res[i]['n_cs']} CS programmes",
                   status=stt, d=3)
            R.putb(sec, f"CS change: {nm} minus original", lab + "; paired",
                   summ(res[i]["beta"] - o["beta"], res[i]["bs"] - o["bs"]), k=f"{res[i]['n_cs']} CS programmes",
                   status=stt, d=3)
    lam = R1["lam58"]
    R.put("G1 coverage", "scripts/58 residual-F reliability lambda_LB (main spec, z(F))", "LB (scripts/56 public-edge "
          "bound); published beta / lambda_LB = +0.0297", lam["LB"], status="check", d=3)
    R.put("G1 coverage", "scripts/58 residual-F reliability lambda_EXT (main spec, z(F))", "EXT; published beta / "
          "lambda_EXT = +0.0098", lam["EXT"], status="check", d=3)
    # ---------------- G2 ----------------
    cnt = R2["counts"]
    for s_ in STAGES:
        R.put("G2", f"missing top-50 CS departments: first failing stage = {s_}", "of the missing", int(cnt[s_]),
              status="pre", d=0)
    R.put("G2", "top-50 Wapman CS departments missing from the CS-remainder sample", "", R2["n_missing"],
          status="pre", d=0)
    for tag, lab, st in (("old", "2026 controls, old sample", "check"),
                         ("E_common", "version-E controls, programmes complete under both", ""),
                         ("E_enl", "version-E controls, enlarged sample", "")):
        st_ = st if st else ("pre" if R2["fires"] else "expl. (C)")
        r_ = R2[tag]
        R.putb("G2", f"CS remainder: {lab}", "4/1/5-yr average; scripts/58 bootstrap", summ(r_["beta"], r_["bs"]),
               k=f"{r_['n_cs']} CS programmes, {R2[tag + '_top50']} of them top-50; {r_['keys'][3]:,} programmes, "
                 f"{r_['keys'][2]} institutions", status=st_, d=3)
    # ---------------- G3 UK ----------------
    pt, keys, bs = U["pt"], U["keys"], U["bs"]

    def ub(k):
        return summ(pt[k], bs[:, keys.index(k)])
    kU = f"{U['n']} programmes, {U['G']} providers"
    for nm, lab in (("rel_ref", "REF: within-provider REF 2021-2014 test-retest (normal scores)"),
                    ("rel_pay", "pay: 1 - noise / residual variance (scripts/73-style median noise)"),
                    ("rel_int1", "intake ('low' = 1): odd/even cohort split-half, Spearman-Brown"),
                    ("rel_int0", "intake ('low' = 0): same"), ("rel_score1", "band score ('low' = 1): same"),
                    ("rel_pay_half", "pay: odd/even cohort split-half, Spearman-Brown (check)")):
        st = "pre" if nm in ("rel_ref", "rel_pay", "rel_int1") else ("sens" if nm == "rel_int0" else
                                                                      "expl. (C)" if nm == "rel_score1" else "")
        sz = ctx["uk_sizes"].get({"rel_ref": "ref", "rel_int1": "int1", "rel_int0": "int0", "rel_score1": "score1",
                                  "rel_pay_half": "pay_half"}.get(nm, ""), (U["n"], U["G"]))
        R.putb("G3 UK reliability", lab, "within-provider residuals", ub(nm),
               k=f"{sz[0]} programmes, {sz[1]} providers (revision 1: subset label)", status=st, d=3)
    ctx["g3v"] = {}
    for v, st in (("int1", "pre"), ("int0", "sens"), ("score1", "expl. (C)")):
        for pair in ("REF-pay", "REF-intake", "pay-intake"):
            if pair == "REF-pay" and v != "int1":
                continue
            tag = pair if pair == "REF-pay" else f"{pair}|{v}"
            lab = pair if pair == "REF-pay" else f"{pair} [{UK_INTAKE[v]}]"
            a_, w_, c_, d_ = ub(f"across|{tag}"), ub(f"within|{tag}"), ub(f"ceil|{tag}"), ub(f"dis|{tag}")
            verdict = g3_rule(d_["hi"], a_["est"])
            ctx["g3v"][tag] = verdict
            R.putb("G3 UK", f"{lab}: across providers within subject", "Pearson of within-subject normal scores", a_,
                   k=kU, status=st, d=3)
            R.putb("G3 UK", f"{lab}: within provider", "provider + subject FE removed", w_, k=kU, status=st, d=3)
            R.putb("G3 UK", f"{lab}: reliability ceiling", "sqrt(rel_x rel_y)", c_, k=kU, status=st, d=3)
            R.putb("G3 UK", f"{lab}: within provider, disattenuated", "r / sqrt(rel_x rel_y)", d_, k=kU, status=st,
                   verdict=verdict if st in ("pre", "sens") else "", d=3)
    fk, fbs = U["fixed_keys"], U["bs_fix"]
    for tag in ("REF-pay", "REF-intake|int1"):
        s_ = summ(U["pt_fix"][f"dis|{tag}"], fbs[:, fk.index(f"dis|{tag}")])
        a_ = summ(pt[f"across|{tag}"], bs[:, keys.index(f"across|{tag}")])
        R.putb("G3 UK", f"{tag.split('|')[0]}: within, disattenuated with REF reliability fixed at 0.536",
               "scripts/76 published test-retest (named in the binding text)", s_, k=kU, status="sens",
               verdict=g3_rule(s_["hi"], a_["est"]), d=3)
    ch = ctx["uk_chk"]
    for j, pair in enumerate(("REF-pay", "REF-intake", "pay-intake")):
        R.put("G3 UK", f"{pair}: across, T4 cells", "normal scores within subject on scripts/76 T4 cells "
              "(intake 'low' = 1)", ch["across_t4cells"][j], k=f"{ch['t4_n']} programmes", status="expl. (C)", d=3)
        R.put("G3 UK", f"{pair}: across, mean over subjects of the per-subject Pearson", "intake 'low' = 1",
              ch["across_subjmean"]["int1"][j], k=f"{U['S']} subjects", status="expl. (C)", d=3)
    R.put("check", "scripts/76 within-provider triad (z(REF rank), pay, intake share)", "published +0.109 / +0.146 / "
          "+0.261", ch["wtriad"][0], k=f"{ch['n6']} programmes; {ch['wtriad'][1]:+.3f} / {ch['wtriad'][2]:+.3f}",
          status="check", d=3)
    R.put("check", "scripts/76 T4 mean Spearman REF-pay", "published +0.580 / +0.643 / +0.694", ch["t4"][0],
          k=f"{ch['t4_n']} programmes; {ch['t4'][1]:+.3f} / {ch['t4'][2]:+.3f}", status="check", d=3)
    R.put("check", "scripts/76 REF 2014-2021 within-provider test-retest", "published +0.536", ch["rel76"],
          k=f"{ch['rel76_n']} programmes", status="check", d=3)
    R.put("check", "pay re-read from LEO: max |mean log median - scripts/76 pay|", "", ch["pay_maxdiff"], status="check",
          d=10)
    R.put("G3 UK", "share of G3 programmes with intake share 0", "'low' = 0 / 'low' = 1",
          ch["zero_share"]["int0"], k=f"'low' = 1: {ch['zero_share']['int1']:.3f}", d=3)
    R.put("G3 UK", "median noise SE of a programme's mean log median pay", "scripts/73-style", ch["pay_relse_median"],
          k=f"{ch['pay_cohorts']} programme-cohorts; quartiles missing in {ch['pay_cohorts_noquart']}", d=4)
    # ---------------- G3 US ----------------
    pt, keys, bs = US["pt"], US["keys"], US["bs"]

    def usb(k):
        return summ(pt[k], bs[:, keys.index(k)])

    def usj(k):
        return jack(pt[k], US["jk"][:, keys.index(k)])
    kS = f"{US['n']:,} programmes, {US['G']} institutions, {US['k']} fields"
    a_ = usb("across")
    R.putb("G3 US", "F-pay: across institutions within field", "Pearson of within-field normal scores", a_, k=kS,
           status="pre", d=3)
    R.put("G3 US", "F-pay: mean within-field Spearman (context)", "same cells", ctx["us_rho_sp"], k=kS, d=3)
    for nm, lab, st in (("main", "main-spec residuals (institution FE, field FE, field x {SAT, ADM, Pell, G})", "pre"),
                        ("fe", "institution + field FE only (UK-parallel)", "expl. (C)")):
        w_ = usb(f"within|{nm}")
        R.putb("G3 US", f"F-pay: within institution [{nm}]", lab, w_, k=kS, status=st, d=3)
        R.putb("G3 US", f"residual-F reliability lambda_LB [{nm}]", "scripts/58 formula on this design (revision 1: "
               "jackknife CI)", usj(f"lam_LB|{nm}"), kind="jackknife", k=kS, status=st, d=3)
        R.putb("G3 US", f"residual-F reliability lambda_EXT [{nm}]", "scripts/58 formula on this design (revision 1: "
               "jackknife CI)", usj(f"lam_EXT|{nm}"), kind="jackknife", k=kS, status="expl. (C)", d=3)
        R.putb("G3 US", f"pay reliability [{nm}]", "scripts/73 se_main; 1 - noise / residual variance (revision 1: "
               "jackknife CI)", usj(f"rel_pay|{nm}"), kind="jackknife", k=kS, status="expl. (C)", d=3)
        d1 = usb(f"dis|{nm}")
        v = g3_rule(d1["hi"], a_["est"], "institutions")
        ctx["g3v"][f"US|{nm}"] = v
        R.putb("G3 US", f"F-pay: within, disattenuated by lambda_LB [{nm}]", "r / sqrt(lambda_LB)", d1, k=kS, status=st,
               verdict=v if st == "pre" else "", d=3)
        d2 = usb(f"dis_ext|{nm}")
        ctx["g3v"][f"US_ext|{nm}"] = g3_rule(d2["hi"], a_["est"], "institutions")
        R.putb("G3 US", f"F-pay: within, disattenuated by lambda_EXT [{nm}]", "r / sqrt(lambda_EXT)", d2, k=kS,
               status="expl. (C)", d=3)
        d3 = usb(f"dis_pay|{nm}")
        ctx["g3v"][f"US_pay|{nm}"] = g3_rule(d3["hi"], a_["est"], "institutions")
        R.putb("G3 US", f"F-pay: within, disattenuated by lambda_LB and pay reliability [{nm}]",
               "r / sqrt(lambda_LB rel_pay)", d3, k=kS, status="expl. (C)", d=3)
    # ---------------- G4 ----------------
    kG = f"{G4['n']} programmes, {G4['G']} providers, {G4['S']} subjects"
    for tag, lab, st in (("low0", "intake share 'low' = 0 (scripts/76 control)", "pre"),
                         ("low1", "intake share 'low' = 1", "expl. (C)")):
        r_ = G4[tag]
        def gb(k):
            return summ(r_["pt"][k], r_["bs"][:, r_["keys"].index(k)])
        R.putb("G4", f"slope without intake control [{tag}]", lab + "; provider + subject FE", gb("b_short"), k=kG,
               status="check" if tag == "low0" else st)
        R.putb("G4", f"slope with subject x intake slopes [{tag}]", lab, gb("b_long"), k=kG,
               status="check" if tag == "low0" else st)
        for rt in ("tot", "win"):
            stt = st if rt == "tot" else "expl. (C)"
            R.put("G4", f"R-squared short / long [{tag}, {rt}]", "total (FE included)" if rt == "tot" else
                  "within (FE partialled out)", r_["pt"][f"R_short_{rt}"], k=f"long {r_['pt'][f'R_long_{rt}']:.4f}",
                  status=stt, d=4)
            for rmx in ("13", "1", "n"):
                rv_ = r_["pt"][f"rmax_{rmx}_{rt}"]
                rlab = {"13": f"R_max = min(1, 1.3 R_long) = {rv_:.4f}", "1": "R_max = 1",
                        "n": f"R_max = 1 - noise share = {rv_:.4f} (exploratory)"}[rmx]
                nm = {"13": "1.3x", "1": "1", "n": "noise ceiling"}[rmx]
                st3 = ("" if rmx == "n" else stt if rt == "win" or tag == "low1" else "pre" if rmx == "13" else "sens")
                R.putb("G4", f"beta*(delta = 1) [{tag}, {rt}, R_max {nm}]", rlab, gb(f"bstar_{rmx}_{rt}"), k=kG,
                       status=st3)
                dd = gb(f"delta_{rmx}_{rt}")
                dd.update(se=np.nan, mde=np.nan)          # a ratio with a heavy tail: percentile interval only
                R.putb("G4", f"delta* (beta = 0) [{tag}, {rt}, R_max {nm}]", rlab, dd, k=kG, status=st3, d=2)
    collect_rev1(ctx, R)
    collect_rev2(ctx, R)
    return R


RV = "rev. 1"          # status of every row added in revision 1 (added after results were seen)
RV2 = "rev. 2"         # status of every row added in revision 2 (added after results were seen)


def collect_rev2(ctx: dict, R: Rows):
    """Rows added in revision 2, added after results were seen (exploratory)."""
    US = ctx["g3us"]
    pt, keys, bs, jk = US["pt"], US["keys"], US["bs"], US["jk"]
    kS = f"{US['n']:,} programmes, {US['G']} institutions, {US['k']} fields"

    def ub(k):
        return summ(pt[k], bs[:, keys.index(k)])

    def uj(k):
        return jack(pt[k], jk[:, keys.index(k)])
    sec = "G3 US rev. 2"
    R.putb(sec, "FE-only contrast: across institutions within field (plain coupling)", "Pearson of within-field normal "
           "scores", ub("across"), k=kS, status=RV2, d=3)
    R.putb(sec, "FE-only contrast: within institution", "institution + field FE only", ub("within|fe"), k=kS,
           status=RV2, d=3)
    R.putb(sec, "FE-only contrast: within, corrected (lambda_LB full leverage)", "r / sqrt(lambda_LB)",
           ub("disfull|fe"), k=kS, status=RV2, d=3)
    R.putb(sec, "FE-only contrast: within, corrected for F and pay noise", "r / sqrt(lambda_LB x rel_pay)",
           ub("disfull_pay|fe"), k=kS, status=RV2, d=3)
    for k_, lab in (("relF_a_LB", "across-level reliability of F (LB)"), ("relF_a_EXT", "across-level reliability "
                    "of F (EXT)"), ("relY_a", "across-level reliability of pay")):
        R.putb(sec, f"FE-only contrast: {lab}", "1 - error / field-demeaned variance", uj(k_), kind="jackknife", k=kS,
               status=RV2, d=3)
    R.putb(sec, "FE-only contrast: across, corrected for F (LB) and pay noise", "a / sqrt(relF_a x relY_a)",
           ub("across_dis"), k=kS, status=RV2, d=3)
    R.putb(sec, "stricter within-institution contrast: within (main spec)", "net of field x {SAT, ADM, Pell, G} "
           "(the pre-specified residualisation)", ub("within|main"), k=kS, status=RV2, d=3)
    R.putb(sec, "stricter within-institution contrast: within, corrected (lambda_LB full leverage)", "main spec",
           ub("disfull|main"), k=kS, status=RV2, d=3)
    S = ctx["g3us_sim"]
    ctx["uscal"] = {}
    for tag, lab in (("LB", "F reliability at the lower bound (primary)"), ("EXT", "F reliability extrapolated "
                                                                                 "(sensitivity)")):
        Rt = S[tag]
        nul, alt = Rt["null"], Rt["alt"]
        N = len(nul["res"])
        rho0 = float(nul["par"]["rho_b"])
        sct = f"G3 US sim [{tag}]"
        obs = Rt["obs"]
        R.put(sct, "calibrated null rho (= rho_between = rho_within)", lab + "; matches the observed across "
              "correlation", rho0, k=f"{SIM_CAL_ROUNDS} x {SIM_CAL_M} calibration draws", status=RV2, d=3)
        out = {}
        for k_, lab2, ob in (("a", "across correlation", obs["a"]), ("w", "within-institution correlation", obs["w"]),
                             ("wd", "within, pre-specified correction (F only, scripts/58 lambda)", obs["wd"]),
                             ("wd_both", "within, corrected for F and pay noise", obs["wd_both"]),
                             ("ad_both", "across, corrected for F and pay noise", obs["ad_both"])):
            v = np.array([r[k_] for r in nul["res"]], float)
            pv = (1 + int((v <= ob).sum())) / (N + 1)
            out[k_] = pv
            R.put(sct, f"null {lab2}", f"observed {ob:+.3f}" + ("" if k_ in ("a", "ad_both") else
                  "; p = (1 + #null <= obs) / (1 + N)"), float(np.nanmean(v)), float(np.nanpercentile(v, 2.5)),
                  float(np.nanpercentile(v, 97.5)), "null 2.5-97.5%", k=f"{N} null draws", status=RV2,
                  verdict=("" if k_ in ("a", "ad_both") else f"p = {pv:.4f}"), d=3)
        for k_, lab2 in (("qF", "within-institution variance share of the F score"),
                         ("qY", "within-institution variance share of the pay score")):
            R.put(sct, f"model check: {lab2}", f"observed {obs[k_]:.3f}",
                  float(np.mean([r[k_] for r in nul["res"]])), k=f"pi = {nul['par']['pi'][0 if k_ == 'qF' else 1]:.3f}",
                  status=RV2, d=3)
        for k_, lab2 in (("lam58", "lambda_LB (scripts/58 formula)" if tag == "LB" else "lambda_EXT (scripts/58 formula)"),
                         ("relY_w", "within-institution pay reliability")):
            R.put(sct, f"model check: {lab2} under the null", f"observed {obs[k_]:.3f}",
                  float(np.mean([r[k_] for r in nul["res"]])), status=RV2, d=3)
        sz = np.array([r["rule_less"] for r in nul["size"]])
        out["size"] = float(sz.mean())
        out["size_se"] = float(np.sqrt(sz.mean() * (1 - sz.mean()) / len(sz)))
        R.put(sct, "share of null data sets where the pre-specified rule says 'agree less within'", f"FE-only "
              f"contrast; {SIM_SIZE_B}-replicate institution bootstrap per data set; SE = Monte Carlo SE",
              out["size"], kind="Monte Carlo", se=out["size_se"], k=f"{len(sz)} null data sets", status=RV2, d=3)
        wv = np.array([r["w"] for r in alt["res"]])
        rw, rb = float(alt["par"]["rho_w"]), float(alt["par"]["rho_b"])
        se = float(wv.std(ddof=1)) * rw / float(wv.mean())
        out.update(rw=rw, rb=rb, lo=rw - 1.959963984540054 * se, hi=rw + 1.959963984540054 * se, rho0=rho0, N=N)
        R.put(sct, "calibrated rho_within", "rho_within and rho_between free, matched to the observed within and "
              "across correlations; interval as for the UK", rw, out["lo"], out["hi"], "approx. normal (simulation)",
              k=f"fit: within {np.mean(wv):+.3f} vs {obs['w']:+.3f}", status=RV2, d=3)
        R.put(sct, "calibrated rho_between", "same calibration", rb,
              k=f"fit: across {np.mean([r['a'] for r in alt['res']]):+.3f} vs {obs['a']:+.3f}", status=RV2, d=3)
        ctx["uscal"][tag] = out
    al = ctx["alias"]
    R.put("G2 rev. 2", "name-join sensitivity: CS departments recovered by scripts/59's name aliases",
          f"{al['n_alias4']} + {al['n_audit']} = {al['n_map']} aliases imported (s59.alias_full); keyed by PSEO names",
          float(len(al["recovered"])), k=f"of {al['n_lost']} name-join departments; alias keys matching any 2026 "
          f"Scorecard institution name: {al['keys_in_scorecard']}", status=RV2, d=0)


def collect_rev1(ctx: dict, R: Rows):
    """Rows added in revision 1, after results were seen (exploratory)."""
    R1, Rr = ctx["g1"], ctx["g1r1"]
    lab = ctx["g1lab"]
    full = R1["full"]
    o = full[0]
    kfull = f"{o['n']:,} programmes, {o['G']} institutions, {o['k']} fields"
    ctx["g1v_r1"] = {}
    for i, (nm, sl) in enumerate((("F | field x {production rank, export-ratio rank} (in design)", "rank_p, rank_x"),
                                  ("F | field x production rank (in design)", "rank_p"))):
        r_ = Rr["design"][i]
        s1 = summ(r_["beta"], r_["bs"])
        ch = summ(r_["beta"] - o["beta"], r_["bs"] - o["bs"])
        v = g1_rule(ch, s1, o["beta"])
        ctx["g1v_r1"][i] = v
        R.putb("G1 rev. 1", f"slope per SD: {nm}", f"main spec + field x {{{sl}}}; CR1 SE {r_['se_cr1']:.4f}", s1,
               k=kfull, status=RV)
        R.putb("G1 rev. 1", f"change: {nm} minus original", "paired (same draws as the original)", ch, k=kfull,
               status=RV, verdict=f"{v} (rule applied in revision 1)")
    for (a_, b_), v in Rr["pcorr"].items():
        R.put("G1 rev. 1", f"within-design correlation of {'F_perp' if a_ == 'Fperp' else 'F'} with the "
              f"{'production' if b_ == 'rank_p' else 'export-ratio'} rank", "both residualised on institution FE, field "
              "FE and field x {SAT, ADM, Pell, G}; within-field z-scores", v, k=kfull, status=RV, d=3)
    c0 = R1["cs_full"][0]
    for i, nm in enumerate(("F | field x {production rank, export-ratio rank} (in design)",
                            "F | field x production rank (in design)")):
        r_ = Rr["cs_design"][i]
        R.putb("G1 rev. 1 CS", f"CS remainder: {nm}", "4/1/5-yr average; a field counts in a draw with >= "
               f"{8 + 2 - i} distinct institutions", summ(r_["beta"], r_["bs"]), k=f"{r_['n_cs']} CS programmes",
               status=RV, d=3)
        R.putb("G1 rev. 1 CS", f"CS change: {nm} minus original", "paired",
               summ(r_["beta"] - c0["beta"], r_["bs"] - c0["bs"]), k=f"{r_['n_cs']} CS programmes", status=RV, d=3)
    # ---------------- G3 UK: linear co-primary, between providers ----------------
    U = ctx["g3uk"]
    pt, keys, bs = U["pt"], U["keys"], U["bs"]

    def ub(k):
        return summ(pt[k], bs[:, keys.index(k)])
    kU = f"{U['n']} programmes, {U['G']} providers"
    sz = ctx["uk_sizes"]
    for nm, lab_, kk in (("rel_ref_lin", "REF test-retest, linear z", f"{sz['ref'][0]} programmes, {sz['ref'][1]} "
                          "providers"), ("rel_pay_lin", "pay noise reliability, linear z", kU),
                         ("rel_int1_lin", "intake split-half ('low' = 1), linear z", kU)):
        R.putb("G3 UK rev. 1", f"reliability: {lab_}", "within-provider residuals", ub(nm), k=kk, status=RV, d=3)
    ctx["g3v_lin"] = {}
    for pair in PAIRS3:
        a_, w_, d_ = ub(f"across_lin|{pair}"), ub(f"within_lin|{pair}"), ub(f"dis_lin|{pair}")
        v = g3_rule(d_["hi"], a_["est"])
        ctx["g3v_lin"][pair] = v
        R.putb("G3 UK rev. 1", f"{pair} (linear z, co-primary): across providers within subject", "Pearson of "
               "within-subject linear z-scores", a_, k=kU, status=RV, d=3)
        R.putb("G3 UK rev. 1", f"{pair} (linear z, co-primary): within provider", "provider + subject FE removed", w_,
               k=kU, status=RV, d=3)
        R.putb("G3 UK rev. 1", f"{pair} (linear z, co-primary): within provider, disattenuated", "r / sqrt(rel_x "
               "rel_y)", d_, k=kU, status=RV, verdict=f"{v} (pre-specified rule, revision-1 row)", d=3)
    for pair in PAIRS3:
        for nm, lab_ in (("between", "normal scores"), ("between_lin", "linear z")):
            R.putb("G3 UK rev. 1", f"{pair}: pure between-provider correlation ({lab_})", "provider means of the "
                   "subject-demeaned scores", ub(f"{nm}|{pair}"), k=f"{U['G']} providers", status=RV, d=3)
    # ---------------- G3 UK: calibration simulation ----------------
    S = ctx["g3sim"]
    nul, alt = S["null"], S["alt"]
    N = len(nul["res"])
    ctx["g3cal"] = {}
    obs_lin = {pair: (pt[f"within_lin|{pair}"], pt[f"dis_lin|{pair}"], pt[f"across_lin|{pair}"]) for pair in PAIRS3}
    for j, pair in enumerate(PAIRS3):
        tagb = pair if pair == "REF-pay" else f"{pair}|int1"
        rho0 = float(nul["par"]["rho_b"][j])
        R.put("G3 UK sim", f"{pair}: calibrated null rho (= rho_between = rho_within)", "matches the observed across "
              "correlation (normal scores)", rho0, k=f"{SIM_CAL_ROUNDS} x {SIM_CAL_M} calibration draws", status=RV,
              d=3)
        for kind, lab_, w_obs, wd_obs, a_obs in (("b", "normal scores", pt[f"within|{tagb}"], pt[f"dis|{tagb}"],
                                                   pt[f"across|{tagb}"]),
                                                  ("l", "linear z", *obs_lin[pair])):
            wn = np.array([r[f"{kind}|w|{pair}"] for r in nul["res"]])
            wdn = np.array([r[f"{kind}|wd|{pair}"] for r in nul["res"]])
            an = np.array([r[f"{kind}|a|{pair}"] for r in nul["res"]])
            p_w = (1 + int((wn <= w_obs).sum())) / (N + 1)
            p_wd = (1 + int((wdn <= wd_obs).sum())) / (N + 1)
            ctx["g3cal"][(kind, pair)] = dict(p_w=p_w, p_wd=p_wd)
            R.put("G3 UK sim", f"{pair} ({lab_}): null mean of the across correlation", f"observed {a_obs:+.3f}",
                  float(an.mean()), float(np.percentile(an, 2.5)), float(np.percentile(an, 97.5)), "null 2.5-97.5%",
                  k=f"{N} null draws", status=RV, d=3)
            R.put("G3 UK sim", f"{pair} ({lab_}): null within correlation", f"observed {w_obs:+.3f}; p = "
                  f"(1 + #null <= obs) / (1 + N)", float(wn.mean()), float(np.percentile(wn, 2.5)),
                  float(np.percentile(wn, 97.5)), "null 2.5-97.5%", k=f"{N} null draws", status=RV,
                  verdict=f"p = {p_w:.4f}", d=3)
            R.put("G3 UK sim", f"{pair} ({lab_}): null disattenuated within correlation", f"observed {wd_obs:+.3f}; "
                  f"planted rho {rho0:.3f}", float(np.nanmean(wdn)), float(np.nanpercentile(wdn, 2.5)),
                  float(np.nanpercentile(wdn, 97.5)), "null 2.5-97.5%", k=f"{N} null draws", status=RV,
                  verdict=f"p = {p_wd:.4f}", d=3)
            for tg_, src_, lab2 in (("", nul["size"], ""), ("_t0", S["tau0"]["size"], " [sensitivity: tau = 0.02]")):
                sz_ = np.array([r[f"{kind}|rule_less|{pair}"] for r in src_])
                ctx["g3cal"][(kind, pair)]["size" + tg_] = float(sz_.mean())
                ctx["g3cal"][(kind, pair)]["size_se" + tg_] = float(np.sqrt(sz_.mean() * (1 - sz_.mean()) / len(sz_)))
                R.put("G3 UK sim", f"{pair} ({lab_}): share of null data sets where the pre-specified rule says "
                      f"'agree less within'{lab2}", f"{SIM_SIZE_B}-replicate provider bootstrap per data set; SE = "
                      "Monte Carlo SE", float(sz_.mean()), kind="Monte Carlo",
                      se=float(np.sqrt(sz_.mean() * (1 - sz_.mean()) / len(sz_))), k=f"{len(sz_)} null data sets",
                      status=RV, d=3)
            tw = np.array([r[f"{kind}|true_w|{pair}"] for r in nul["res"]])
            R.put("G3 UK sim", f"{pair} ({lab_}): noise-free within correlation of the scores under the null",
                  f"planted rho {rho0:.3f}", float(tw.mean()), k=f"{N} null draws", status=RV, d=3)
    for kind, lab_ in (("b", "normal scores"), ("l", "linear z")):
        for nm in ("ref", "pay", "int"):
            est = np.array([r[f"{kind}|rel_{nm}"] for r in nul["res"]])
            tru = np.array([r[f"{kind}|true_rel_{nm}"] for r in nul["res"]])
            R.put("G3 UK sim", f"{nm} reliability ({lab_}) under the null: pipeline estimate (mean)", "true = squared "
                  "correlation of the observed and the noise-free within-provider residuals (k column)",
                  float(est.mean()), k=f"true {tru.mean():.3f}", status=RV, d=3)
    fit = nul["fit"]
    obs = S["obs"]
    for j, nm in enumerate(("REF", "pay", "intake")):
        R.put("G3 UK sim", f"model check: within-provider variance share of the {nm} score", f"observed "
              f"{obs['q'][j]:.3f}", float(fit["q"][j]), k=f"pi = {nul['par']['pi'][j]:.3f}", status=RV, d=3)
    R.put("G3 UK sim", "model check: REF test-retest under the null", f"observed {obs['rel_ref']:.3f}",
          float(fit["rel_ref"]), k=f"REF error SD {nul['par']['sig_ref']:.3f}", status=RV, d=3)
    R.put("G3 UK sim", "model check: intake split-half reliability (normal scores) under the null",
          f"observed {obs['rel_int']:.3f}", float(fit["rel_int"]), k=f"cohort noise tau {nul['par']['tau']:.3f}",
          status=RV, d=3)
    ft0 = S["tau0"]["fit"]
    R.put("G3 UK sim", "sensitivity tau = 0.02: intake split-half reliability (normal scores) under the null",
          f"observed {obs['rel_int']:.3f}", float(ft0["rel_int"]),
          k="null rho " + ", ".join(f"{v:.3f}" for v in S["tau0"]["par"]["rho_b"]), status=RV, d=3)
    R.put("G3 UK sim", "model check: largest |simulated - observed| subject mean intake share", "",
          float(np.max(np.abs(fit["int_mean"] - obs["m"]))), status=RV, d=4)
    R.put("G3 UK sim", "model check: largest |simulated / observed - 1| subject SD of the intake share", "",
          float(np.max(np.abs(fit["int_sd"] / obs["s"] - 1))), status=RV, d=4)
    # calibrated estimates (alternative: rho_within free)
    af = alt["fit"]
    for j, pair in enumerate(PAIRS3):
        wv = np.array([r[f"b|w|{pair}"] for r in alt["res"]])
        rw, rb = float(alt["par"]["rho_w"][j]), float(alt["par"]["rho_b"][j])
        kf = rw / float(wv.mean())
        se = float(wv.std(ddof=1)) * kf
        ctx["g3cal"][("cal", pair)] = dict(rw=rw, rb=rb, lo=rw - 1.959963984540054 * se,
                                           hi=rw + 1.959963984540054 * se)
        R.put("G3 UK sim", f"{pair}: calibrated rho_within", "simulation matches observed across and within "
              "correlations; interval = +-1.96 x simulated SD of the within correlation x (rho_w / its mean)", rw,
              rw - 1.959963984540054 * se, rw + 1.959963984540054 * se, "approx. normal (simulation)",
              k=f"fit: within {af['w'][j]:+.3f} vs {obs['w'][j]:+.3f}", status=RV, d=3)
        R.put("G3 UK sim", f"{pair}: calibrated rho_between", "same calibration", rb,
              k=f"fit: across {af['a'][j]:+.3f} vs {obs['a'][j]:+.3f}", status=RV, d=3)
    R.put("G3 UK sim", "simulated programmes without a graduate (filled by the subject median)", "all null draws",
          float(sum(r["nmiss"] for r in nul["res"])), k=f"{N} null draws x {ctx['g3uk']['n']} programmes",
          status=RV, d=0)
    # ---------------- G3 UK robustness ----------------
    for lab_, r_ in ctx["g3rob"].items():
        kr = f"{r_['n']} programmes, {r_['G']} providers"
        for pair in PAIRS3:
            tagb = pair if pair == "REF-pay" else f"{pair}|int1"
            for kind, ka, kd in (("normal scores", f"across|{tagb}", f"dis|{tagb}"),
                                 ("linear z", f"across_lin|{pair}", f"dis_lin|{pair}")):
                ac = r_["pt"][ka]
                dv = r_["bs"][:, r_["keys"].index(kd)]
                s_ = summ(r_["pt"][kd], dv)
                R.putb("G3 UK rob.", f"{lab_}: {pair} ({kind}) disattenuated within", f"across {ac:+.3f}; "
                       f"{B_ROB}-replicate provider bootstrap", s_, k=kr, status=RV,
                       verdict=g3_rule(s_["hi"], ac) + " (pre-specified rule)", d=3)
    # ---------------- G3 US: full-leverage lambda ----------------
    US = ctx["g3us"]
    pt, keys, bs = US["pt"], US["keys"], US["bs"]
    kS = f"{US['n']:,} programmes, {US['G']} institutions, {US['k']} fields"
    a_ = summ(pt["across"], bs[:, keys.index("across")])
    for nm, lab_ in (("main", "main spec"), ("fe", "institution + field FE")):
        for tag in ("LB", "EXT"):
            R.putb("G3 US rev. 1", f"residual-F reliability with full leverage, lambda_{tag} [{nm}]", f"{lab_}; "
                   "error variance kept by M_ii, as the pay reliability", jack(pt[f"lamfull_{tag}|{nm}"],
                                                                              US["jk"][:, keys.index(f"lamfull_{tag}|{nm}")]),
                   kind="jackknife", k=kS, status=RV, d=3)
        for k_, lab2 in (("disfull", "r / sqrt(lambda_LB full)"), ("disfull_pay", "r / sqrt(lambda_LB full x rel_pay)")):
            s_ = summ(pt[f"{k_}|{nm}"], bs[:, keys.index(f"{k_}|{nm}")])
            sj = jack(pt[f"{k_}|{nm}"], US["jk"][:, keys.index(f"{k_}|{nm}")])
            v = g3_rule(s_["hi"], a_["est"], "institutions")
            ctx["g3v"][f"US_{k_}|{nm}"] = v
            R.putb("G3 US rev. 1", f"F-pay within, disattenuated ({lab2}) [{nm}]", lab_ + "; bootstrap", s_, k=kS,
                   status=RV, verdict=f"{v} (pre-specified rule)", d=3)
            R.putb("G3 US rev. 1", f"F-pay within, disattenuated ({lab2}) [{nm}], jackknife", lab_, sj,
                   kind="jackknife", k=kS, status=RV, d=3)


# =============================================================================================================
# write-up
# =============================================================================================================
def md_table(R: Rows) -> list:
    L = ["| section | quantity | spec | estimate | 95% CI | CI kind | SE | MDE | status | verdict | k |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in R.r:
        x = {k_: (v_.replace("|", "\\|") if isinstance(v_, str) else v_) for k_, v_ in x.items()}
        d = x["d"]
        est = f"{x['est']:,.0f}" if d == 0 else (f"{x['est']:.2e}" if d >= 8 else f3(x["est"], d))
        ci_ = fci(x["lo"], x["hi"], d) if np.isfinite(x["lo"]) else "—"
        se = f"{x['se']:.4f}" if np.isfinite(x["se"]) else "—"
        mde = f"{x['mde']:.4f}" if np.isfinite(x["mde"]) else "—"
        L.append(f"| {x['section']} | {x['quantity']} | {x['spec'] or '—'} | {est} | {ci_} | {x['kind'] or '—'} | "
                 f"{se} | {mde} | {x['status'] or '—'} | {x['verdict'] or '—'} | {x['k'] or '—'} |".replace("|  |", "| — |"))
    return L


def write_md(ctx: dict, R: Rows) -> str:
    R1, R2, U, US, G4 = ctx["g1"], ctx["g2"], ctx["g3uk"], ctx["g3us"], ctx["g4"]
    v1, v3, vr1, vlin, cal = ctx["g1v"], ctx["g3v"], ctx["g1v_r1"], ctx["g3v_lin"], ctx["g3cal"]
    S = ctx["g3sim"]
    lab = ctx["g1lab"]
    A = []
    a = A.append
    g = R.get
    a("# Gap checks — is the US department slope a production artefact, why is the CS sample thin, and do the "
      "academic, employer and student rankings agree less within universities once measurement error is allowed "
      "for?\n")
    a("Script: `scripts/78_gap_checks.py` (seed 78; every number below is written by the script from its own "
      "computations; a second run gives a byte-identical file, see Method). Public data only, all already on disk: "
      "College Scorecard Field-of-Study and institution files, the Scorecard historical institution files "
      "(scripts/68), Wapman et al. (2022) ranks and public edges, IPEDS C2023_a doctorates (scripts/75), PSEO "
      "earnings quartiles (scripts/73), REF 2021 and REF 2014 results and the DfE LEO provider × subject file "
      "(scripts/76). Existing scripts are imported, not edited. Descriptive, not causal. Tables: "
      "`data/interim/gap_checks_summary.csv` (every key number), `data/interim/gap_checks_cs_gap.csv` (G2).\n")
    a("**This is revision 2.** An independent check went over the first version's results and code. What it led "
      "to is labelled *revision 1, added after results were seen* (status `rev. 1` in the "
      "table; list under Revision 1). Revision 2 adds a like-for-like US contrast with its own calibrated test and a "
      "name-join check; it is labelled *revision 2, added after results were seen* (status `rev. 2`; list under "
      "Revision 2). The pre-specified verdicts and every earlier number are kept as they were.\n")
    # ---------------- revision 2 numbers ----------------
    def gr(sec_, q_):
        return g(sec_, q_)
    u2 = {k_: gr("G3 US rev. 2", q_) for k_, q_ in (
        ("a", "FE-only contrast: across institutions within field (plain coupling)"),
        ("w", "FE-only contrast: within institution"),
        ("wd", "FE-only contrast: within, corrected (lambda_LB full leverage)"),
        ("wdb", "FE-only contrast: within, corrected for F and pay noise"),
        ("adb", "FE-only contrast: across, corrected for F (LB) and pay noise"),
        ("wm", "stricter within-institution contrast: within (main spec)"),
        ("wdm", "stricter within-institution contrast: within, corrected (lambda_LB full leverage)"))}
    uc = ctx["uscal"]
    al = ctx["alias"]
    v1_assert(uc["LB"]["w"] < 0.05 and uc["EXT"]["w"] < 0.05 and uc["LB"]["hi"] < uc["LB"]["rb"], "US calibrated test wording")
    # ---------------- G1 numbers ----------------
    fo, fa = g("G1 main", "slope per SD: original F"), g("G1 main", f"slope per SD: {lab[1]}")
    ch_a = g("G1 main", f"change: {lab[1]} minus original")
    fbo, fb = g("G1 common", "slope per SD: original F"), g("G1 common", f"slope per SD: {lab[2]}")
    ch_b = g("G1 common", f"change: {lab[2]} minus original")
    ft, ch_t = g("G1 common", f"slope per SD: {lab[3]}"), g("G1 common", f"change: {lab[3]} minus original")
    D1N = "F | field x {production rank, export-ratio rank} (in design)"
    D2N = "F | field x production rank (in design)"
    d1, dc1 = g("G1 rev. 1", f"slope per SD: {D1N}"), g("G1 rev. 1", f"change: {D1N} minus original")
    d2, dc2 = g("G1 rev. 1", f"slope per SD: {D2N}"), g("G1 rev. 1", f"change: {D2N} minus original")
    pcp = g("G1 rev. 1", "within-design correlation of F_perp with the production rank")["est"]
    pcx = g("G1 rev. 1", "within-design correlation of F_perp with the export-ratio rank")["est"]
    pFp = g("G1 rev. 1", "within-design correlation of F with the production rank")["est"]
    cs0, csa = g("G1 CS", "CS remainder: original F"), g("G1 CS", f"CS remainder: {lab[1]}")
    csd1, csdc1 = g("G1 rev. 1 CS", f"CS remainder: {D1N}"), g("G1 rev. 1 CS", f"CS change: {D1N} minus original")
    csd2, csdc2 = g("G1 rev. 1 CS", f"CS remainder: {D2N}"), g("G1 rev. 1 CS", f"CS change: {D2N} minus original")
    csc0, csb = g("G1 CS common", "CS remainder: original F"), g("G1 CS common", f"CS remainder: {lab[2]}")
    cschb = g("G1 CS common", f"CS change: {lab[2]} minus original")
    cov = R1["cov"]
    # ---------------- G3 numbers ----------------
    pairs = list(PAIRS3)
    tags = {"REF-pay": "REF-pay", "REF-intake": "REF-intake|int1", "pay-intake": "pay-intake|int1"}
    qn = {"REF-pay": "REF-pay", "REF-intake": f"REF-intake [{UK_INTAKE['int1']}]",
          "pay-intake": f"pay-intake [{UK_INTAKE['int1']}]"}
    ac = {p_: g("G3 UK", f"{qn[p_]}: across providers within subject") for p_ in pairs}
    wi = {p_: g("G3 UK", f"{qn[p_]}: within provider") for p_ in pairs}
    di = {p_: g("G3 UK", f"{qn[p_]}: within provider, disattenuated") for p_ in pairs}
    ce = {p_: g("G3 UK", f"{qn[p_]}: reliability ceiling") for p_ in pairs}
    rel = {k: g("G3 UK reliability", q) for k, q in (
        ("ref", "REF: within-provider REF 2021-2014 test-retest (normal scores)"),
        ("pay", "pay: 1 - noise / residual variance (scripts/73-style median noise)"),
        ("int", "intake ('low' = 1): odd/even cohort split-half, Spearman-Brown"),
        ("int0", "intake ('low' = 0): same"), ("score", "band score ('low' = 1): same"),
        ("payh", "pay: odd/even cohort split-half, Spearman-Brown (check)"))}
    lin = {p_: (g("G3 UK rev. 1", f"{p_} (linear z, co-primary): across providers within subject"),
                g("G3 UK rev. 1", f"{p_} (linear z, co-primary): within provider"),
                g("G3 UK rev. 1", f"{p_} (linear z, co-primary): within provider, disattenuated")) for p_ in pairs}
    rl = {k: g("G3 UK rev. 1", f"reliability: {q}") for k, q in (("ref", "REF test-retest, linear z"),
                                                                 ("pay", "pay noise reliability, linear z"),
                                                                 ("int", "intake split-half ('low' = 1), linear z"))}
    btw = {p_: g("G3 UK rev. 1", f"{p_}: pure between-provider correlation (normal scores)") for p_ in pairs}
    btl = {p_: g("G3 UK rev. 1", f"{p_}: pure between-provider correlation (linear z)") for p_ in pairs}
    nul = S["null"]
    N = len(nul["res"])
    rho0 = {p_: g("G3 UK sim", f"{p_}: calibrated null rho (= rho_between = rho_within)")["est"] for p_ in pairs}
    nw = {(k_, p_): g("G3 UK sim", f"{p_} ({'normal scores' if k_ == 'b' else 'linear z'}): null within correlation")
          for k_ in ("b", "l") for p_ in pairs}
    nwd = {(k_, p_): g("G3 UK sim", f"{p_} ({'normal scores' if k_ == 'b' else 'linear z'}): null disattenuated "
                       "within correlation") for k_ in ("b", "l") for p_ in pairs}
    ntw = {(k_, p_): g("G3 UK sim", f"{p_} ({'normal scores' if k_ == 'b' else 'linear z'}): noise-free within "
                       "correlation of the scores under the null") for k_ in ("b", "l") for p_ in pairs}
    na = {(k_, p_): g("G3 UK sim", f"{p_} ({'normal scores' if k_ == 'b' else 'linear z'}): null mean of the across "
                      "correlation") for k_ in ("b", "l") for p_ in pairs}
    srel = {(k_, nm): g("G3 UK sim", f"{nm} reliability ({'normal scores' if k_ == 'b' else 'linear z'}) under the "
                        "null: pipeline estimate (mean)") for k_ in ("b", "l") for nm in ("ref", "pay", "int")}
    cw = {p_: g("G3 UK sim", f"{p_}: calibrated rho_within") for p_ in pairs}
    cb = {p_: g("G3 UK sim", f"{p_}: calibrated rho_between") for p_ in pairs}
    pmax_b = max(cal[("b", p_)]["p_w"] for p_ in pairs)
    pmax_l = max(cal[("l", p_)]["p_w"] for p_ in pairs)
    size_b = {p_: cal[("b", p_)]["size"] for p_ in pairs}
    size_l = {p_: cal[("l", p_)]["size"] for p_ in pairs}
    se_b = {p_: cal[("b", p_)]["size_se"] for p_ in pairs}
    size_b0 = {p_: cal[("b", p_)]["size_t0"] for p_ in pairs}
    size_l0 = {p_: cal[("l", p_)]["size_t0"] for p_ in pairs}
    se_b0 = {p_: cal[("b", p_)]["size_se_t0"] for p_ in pairs}
    ri_t0 = g("G3 UK sim", "sensitivity tau = 0.02: intake split-half reliability (normal scores) under the null")
    up_t0 = [p_ for p_ in pairs if size_b0[p_] - size_b[p_] > 2 * np.sqrt(se_b[p_] ** 2 + se_b0[p_] ** 2)]
    sens_txt = (f"With the intake's cohort noise held at its floor (τ = 0.02; same calibration otherwise) the model's "
                f"intake split-half is {f3(ri_t0['est'])} against the observed {ri_t0['spec'].split(' ')[1]}, and the "
                f"rule's rates are " + ", ".join(f"{p_} {size_b0[p_]:.0%}" for p_ in pairs) + " (normal scores; linear "
                "z " + ", ".join(f"{size_l0[p_]:.0%}" for p_ in pairs) + ")")
    usa = g("G3 US", "F-pay: across institutions within field")
    usw = g("G3 US", "F-pay: within institution [main]")
    usl = g("G3 US", "residual-F reliability lambda_LB [main]")
    usd = g("G3 US", "F-pay: within, disattenuated by lambda_LB [main]")
    usrp = g("G3 US", "pay reliability [main]")
    usfe = g("G3 US", "F-pay: within, disattenuated by lambda_LB [fe]")
    uslf = g("G3 US rev. 1", "residual-F reliability with full leverage, lambda_LB [main]")
    uslf_fe = g("G3 US rev. 1", "residual-F reliability with full leverage, lambda_LB [fe]")
    usdf = g("G3 US rev. 1", "F-pay within, disattenuated (r / sqrt(lambda_LB full)) [main]")
    usdfp = g("G3 US rev. 1", "F-pay within, disattenuated (r / sqrt(lambda_LB full x rel_pay)) [main]")
    usdf_fe = g("G3 US rev. 1", "F-pay within, disattenuated (r / sqrt(lambda_LB full)) [fe]")
    usdfj = g("G3 US rev. 1", "F-pay within, disattenuated (r / sqrt(lambda_LB full)) [main], jackknife")
    # ---------------- guards: the prose below states these readings ----------------
    v1_assert(all(v3[k].startswith("agree less") for k in ("REF-pay", "REF-intake|int1", "pay-intake|int1", "US|main")), "G3 verdict wording")
    v1_assert(R2["main"] == "name join" and not R2["fires"], f"G2 main cause is the name join (now {R2['main']!r}, fires={R2['fires']})")
    v1_assert(v1["a"] == "inconclusive" and v1["b"] == "robust to production", f"G1 verdicts (now {v1['a']!r}, {v1['b']!r})")
    v1_assert(pcp < -0.2 and abs(pFp) < 1 and vr1[0] == "robust to production", f"G1 rev. 1 wording (now {pcp:+.3f}, {vr1[0]!r})")
    assert pmax_b < 0.05 and all(cw[p_]["hi"] < cb[p_]["est"] for p_ in pairs)
    assert max(size_b.values()) > 0.05
    # ---------------- answer ----------------
    a("## Answer\n")
    pw = ", ".join(f"{p_} p = {cal[('b', p_)]['p_w']:.4f}" for p_ in pairs)
    # 2026 re-baseline: alternative sentences where the v1 wording no longer holds (the v1 path is unchanged)
    _V1 = is_v1()
    _ee = g("G2", "CS remainder: version-E controls, enlarged sample")
    _g1_ans = (f"revision 1 finds that (a)'s variable is not production-free "
               f"inside the design, and the production adjustment inside the design leaves the US department slope at "
               f"{f3(d1['est'], 4)} {fci(d1['lo'], d1['hi'], 4)} (change {f3(dc1['est'], 4)} {fci(dc1['lo'], dc1['hi'], 4)}; "
               f"{vr1[0]} under the same rule). ") if _V1 else (
               f"under the 2026 release (complete hiring edges) the export-ratio rank is nearly a copy of F (THEORY_TESTS_RESULT.md "
               f"T0), so revision 1's adjustment for production and the export ratio ({f3(d1['est'], 4)} "
               f"{fci(d1['lo'], d1['hi'], 4)}) partials F out of itself and is not informative; with the production rank only, "
               f"the US department slope is {f3(d2['est'], 4)} {fci(d2['lo'], d2['hi'], 4)} (change {f3(dc2['est'], 4)} "
               f"{fci(dc2['lo'], dc2['hi'], 4)}; {vr1[1]} under the same rule). ")
    _g2_ans = ("G2: the CS gap is mainly a name-join gap, not a selectivity gap, so the "
               "pre-specified re-estimate does not run. ") if _V1 else (
               f"G2: with the name join repaired in the 2026 re-baseline no top-50 CS department is lost to it; the main "
               f"cause of the gap is {R2['main']}, so the pre-specified re-estimate runs (CS remainder with era-matched "
               f"controls on the enlarged sample {f3(_ee['est'])} {fci(_ee['lo'], _ee['hi'])}). ")
    a("**Key question: do four known gaps — PhD production inside the hiring rank, missing top CS departments, "
      "measurement error at the department level, and selection on unobservables in the UK — change the reading that "
      "academic, employer and student rankings agree about universities much more than about departments within "
      f"them?** They do not change that reading. G3, the direct test: the pre-specified rule says 'agree less within' "
      f"for all three UK pairs and for US F–pay. Revision 1 shows that rule is not a calibrated test (under "
      f"ρ_within = ρ_between it says 'agree less within' in up to {max(size_b.values()):.0%} of simulated data sets), "
      f"but a test calibrated by simulation on the real layout rejects ρ_within = ρ_between for every UK pair ({pw}; "
      f"{N} null draws, the smallest attainable p is {1 / (N + 1):.4f}), and the calibrated within-university "
      f"correlations ({', '.join(f'{f3(cw[p_]['est'])}' for p_ in pairs)}) sit far below the calibrated "
      f"between-university ones ({', '.join(f'{f3(cb[p_]['est'])}' for p_ in pairs)}). G1: the pre-specified "
      f"verdicts are (a) {v1['a']} and (b) {v1['b']}; " + _g1_ans + _g2_ans +
      f"G4: a bound that is robust only on the within-R² scale under the "
      f"1.3× rule. *Revision 2, added after results were seen:* in the like-for-like US contrast (institution and "
      f"field FE only within; the plain within-field coupling between) F and pay correlate {f3(u2['w']['est'])} "
      f"within institutions against {f3(u2['a']['est'])} across them ({f3(u2['wdb']['est'])} against "
      f"{f3(u2['adb']['est'])} with both levels corrected for measurement error); the calibrated test rejects "
      f"ρ_within = ρ_between (p = {uc['LB']['w']:.4f}), and the calibrated ρ_within is {f3(uc['LB']['rw'])} against "
      f"ρ_between {f3(uc['LB']['rb'])}.\n")
    # G1
    a(f"1. **G1 — US department slope net of PhD production. Pre-specified: (a) {v1['a']}, (b) {v1['b']}. Revision 1: "
      f"with production adjusted inside the design, {vr1[0]}.** scripts/58's main specification (institution FE, "
      f"field FE, field-specific slopes on SAT, admit rate, Pell share and brand G; its institution cluster bootstrap "
      f"and seed) reproduces {f3(fo['est'], 4)} {fci(fo['lo'], fo['hi'], 4)} on {fo['k']}. (a), as pre-specified: "
      f"with F replaced by F_perp (scripts/75 T0: the within-field residual of rank(F) on the ranks of log PhD "
      f"production and of the export ratio) the slope is {f3(fa['est'], 4)} {fci(fa['lo'], fa['hi'], 4)} (MDE "
      f"{fa['mde']:.4f}), change {f3(ch_a['est'], 4)} {fci(ch_a['lo'], ch_a['hi'], 4)} (MDE {ch_a['mde']:.4f}); "
      f"{g1_explain(ch_a, fa, fo['est'])} — **{v1['a']}**. *Revision 1, added after results were "
      f"seen:* F_perp is a residual over all of a field's ranked institutions, and inside this within-institution "
      f"design it is not orthogonal to production: net of the design's other terms it correlates {f3(pcp)} with the "
      f"production rank and {f3(pcx)} with the export-ratio rank (F itself: {f3(pFp)} with the production rank). Its "
      f"slope therefore mixes department standing with a negative production component and does not answer the "
      f"binding question. Keeping F and adding field-specific slopes on the production and export-ratio ranks to the "
      f"main specification (the partial slope of F net of production within the design) gives {f3(d1['est'], 4)} "
      f"{fci(d1['lo'], d1['hi'], 4)} (MDE {d1['mde']:.4f}), change {f3(dc1['est'], 4)} {fci(dc1['lo'], dc1['hi'], 4)} "
      f"(MDE {dc1['mde']:.4f}) — {vr1[0]} under the pre-specified rule, applied in revision 1; with the production "
      f"rank only {f3(d2['est'], 4)} {fci(d2['lo'], d2['hi'], 4)}, change {f3(dc2['est'], 4)} "
      f"{fci(dc2['lo'], dc2['hi'], 4)} ({vr1[1]}). "
      + ("" if _V1 else
         "*2026 re-baseline:* with complete hiring edges the export-ratio rank is nearly a copy of F (THEORY_TESTS_RESULT.md "
         "T0), so the two-rank adjustment partials F out of itself and is not informative; the production-only row is "
         "the informative in-design adjustment. The within-design correlations with the production rank are undefined "
         "(—) because in one field (communication_disorders) every main-spec programme has the same production rank. ")
      + f"From revision 1 on this in-design version is the primary production "
      f"adjustment; F_perp stays in the table as the pre-specified, flagged variant. Neither slope interval excludes 0 "
      f"by itself, as for F's own slope. (b), as pre-specified: the degree-corrected Bradley–Terry rank F_DC (+1 "
      f"degree convention, entered as its within-field rank) exists for {cov['fdc']:,} of the {cov['n']:,} programmes "
      + ("(the other departments have no edge in the public field network)" if _V1 or cov['fdc'] < cov['n'] else
         "(every department has an edge in the complete 2026 field network)")
      + f"; after scripts/58's sample rules "
      f"{fb['k']}. There F gives {f3(fbo['est'], 4)} {fci(fbo['lo'], fbo['hi'], 4)} and F_DC {f3(fb['est'], 4)} "
      f"{fci(fb['lo'], fb['hi'], 4)} (MDE {fb['mde']:.4f}); change {f3(ch_b['est'], 4)} "
      f"{fci(ch_b['lo'], ch_b['hi'], 4)} (MDE {ch_b['mde']:.4f}) — **{v1['b']}** under the rule, with a change "
      f"interval too wide to show that the two slopes are equal; raw theta {f3(ft['est'], 4)} "
      f"{fci(ft['lo'], ft['hi'], 4)}. CS remainder (scripts/58 per-field main spec, 4/1/5-year average; reported "
      f"without a rule, as the binding text asks): F {f3(cs0['est'])} {fci(cs0['lo'], cs0['hi'])} "
      f"({cs0['k'].split(';')[0]}); with production adjusted in the design {f3(csd1['est'])} "
      f"{fci(csd1['lo'], csd1['hi'])}, change {f3(csdc1['est'])} {fci(csdc1['lo'], csdc1['hi'])}; production only "
      f"{f3(csd2['est'])} {fci(csd2['lo'], csd2['hi'])}, change {f3(csdc2['est'])} {fci(csdc2['lo'], csdc2['hi'])} "
      f"(revision 1); F_DC rank on its {csc0['k'].split(';')[0]} {f3(csb['est'])} {fci(csb['lo'], csb['hi'])} against "
      f"F {f3(csc0['est'])} there (change {f3(cschb['est'])} {fci(cschb['lo'], cschb['hi'])}); the pre-specified "
      f"F_perp variant {f3(csa['est'])} {fci(csa['lo'], csa['hi'])}, flagged as above.\n")
    # G2
    T = R2["T"]
    miss = T[~T.in_h3]
    nj = miss[miss.stage == "name join"]
    n_campus = int(nj.detail.str.contains("campus suffix").sum())
    n_city = int(nj.detail.str.contains("city").sum())
    n_tok = int(nj.detail.str.contains("token").sum())
    sel = miss[miss.stage == "2026 selectivity"]
    hz = miss[miss.stage == "1-yr / 5-yr median"]
    cnt = R2["counts"]
    old, ec_, ee = (g("G2", "CS remainder: 2026 controls, old sample"),
                    g("G2", "CS remainder: version-E controls, programmes complete under both"),
                    g("G2", "CS remainder: version-E controls, enlarged sample"))
    nj_sat_no = int((nj.sat26 == "no").sum())
    v1_assert(int(cnt["name join"]) - n_tok > int(cnt["2026 selectivity"]), f"G2 counts wording ({dict(cnt)})")
    a(("2. **G2 — the CS gap is mainly a name-join gap; the pre-specified re-estimate does not run.** Of the 50 "
       if _V1 else
       f"2. **G2 — with the name join repaired (2026 re-baseline) the main cause of the CS gap is {R2['main']}; the "
       f"pre-specified re-estimate {'runs' if R2['fires'] else 'does not run'}.** Of the 50 ") +
      f"highest-ranked Wapman CS departments, {R2['n_missing']} are not in the CS-remainder sample (table below; each "
      f"assigned to the first stage at which it fails). Name join: {int(cnt['name join'])} (the Scorecard name carries "
      f"a campus suffix for {n_campus} and a city qualifier for {n_city} — Columbia's 'in the City of New York' "
      f"relabelled in revision 1 — and for {n_tok} no scripts/34 rule matches but a token search finds a single "
      f"Scorecard CS programme with a released median). 2026 selectivity: {int(cnt['2026 selectivity'])} "
      f"({'; '.join(sel.wapman)}), all with SAT_AVG missing in the 2026 institution file. 1-year or 5-year median "
      f"not released: {int(cnt['1-yr / 5-yr median'])} ({'; '.join(hz.wapman)}), which are in the 4-year main sample "
      f"but not on the common programmes behind the CS remainder. Missing from Wapman: {int(cnt['Wapman'])}; from the "
      f"Scorecard FoS earnings: {int(cnt['Scorecard FoS earnings'])}; undetermined: {int(cnt['undetermined'])}. The "
      f"main cause is the {R2['main']}, and the pre-specified branch {'fires' if R2['fires'] else 'does not fire'}"
      + ((f"; "
          f"with the {n_tok} token-search departments counted as undetermined it would still be the largest cause "
          f"({int(cnt['name join']) - n_tok} against {int(cnt['2026 selectivity'])}). The name join is not repaired "
          f"(Choices C2); {nj_sat_no} of the {len(nj)} name-join departments would also lack a 2026 SAT_AVG. Exploratory, "
          f"partial: with") if _V1 else
         (". The name join itself is repaired in the 2026 re-baseline (src/crosswalks/wapman_ipeds_aliases.csv; Choices C2 "
          "did not repair it), so no department is lost to it. As pre-specified, since the branch fires: with"))
      + f" scripts/68's era-matched controls for every institution the CS remainder is {f3(ee['est'])} "
      f"{fci(ee['lo'], ee['hi'])} on the enlarged sample ({ee['k'].split(';')[0]}), against {f3(old['est'])} "
      f"{fci(old['lo'], old['hi'])} with 2026 controls ({old['k'].split(';')[0]}) and {f3(ec_['est'])} "
      f"{fci(ec_['lo'], ec_['hi'])} with era-matched controls on the programmes complete under both. Restored: "
      f"{'; '.join(R2['restored_names'])}"
      + ("; not restored: " + "; ".join(f"{n_} ({w_})" for n_, w_ in R2["sel_not_restored"])
         if R2["sel_not_restored"] else "")
      + ("; lost under era-matched controls: " + "; ".join(f"{n_} ({w_})" for n_, w_ in R2["old_lost"])
         if R2["old_lost"] else "")
      + f". Closable with data on disk: missing selectivity, yes for {len(sel) - len(R2['sel_not_restored'])} of "
      f"{len(sel)}; unreleased medians, no; the name join, "
      + ("only by changing scripts/55's join rule. *Revision 2, "
         f"added after results were seen:* scripts/59's name aliases ({al['n_alias4']} for new PSEO institutions and "
         f"{al['n_audit']} from its join audit, imported) are keyed by PSEO institution names; they recover "
         f"{len(al['recovered'])} of the {al['n_lost']} name-join departments (their keys match "
         f"{al['keys_in_scorecard']} names in the 2026 Scorecard institution file in all), so an aliased join would "
         f"leave the US pair and the CS remainder unchanged and is not run.\n" if _V1 else
         "done (repaired in the 2026 re-baseline). *Revision 2, added after results were seen:* the check of scripts/59's "
         "name aliases is moot with the repaired join (no name-join department is left).\n"))
    # G3
    txt = []
    for p_ in pairs:
        txt.append(f"{p_}: across {f3(ac[p_]['est'])} {fci(ac[p_]['lo'], ac[p_]['hi'])}, within {f3(wi[p_]['est'])} "
                   f"{fci(wi[p_]['lo'], wi[p_]['hi'])}, ceiling {f3(ce[p_]['est'])}, disattenuated "
                   f"{f3(di[p_]['est'])} {fci(di[p_]['lo'], di[p_]['hi'])} — {v3[tags[p_]]}")
    nulltxt = []
    for p_ in pairs:
        assert wi[p_]["est"] < nw[("b", p_)]["lo"] and lin[p_][1]["est"] < nw[("l", p_)]["lo"]
        nulltxt.append(f"{p_}: observed within {f3(wi[p_]['est'])} against a null range "
                       f"{fci(nw[('b', p_)]['lo'], nw[('b', p_)]['hi'])} (null ρ {rho0[p_]:.3f}), p = "
                       f"{cal[('b', p_)]['p_w']:.4f}")
    caltxt = "; ".join(f"{p_} {f3(cw[p_]['est'])} {fci(cw[p_]['lo'], cw[p_]['hi'])} against {f3(cb[p_]['est'])}"
                       for p_ in pairs)
    lintxt = "; ".join(f"{p_}: across {f3(lin[p_][0]['est'])}, within {f3(lin[p_][1]['est'])}, disattenuated "
                       f"{f3(lin[p_][2]['est'])} {fci(lin[p_][2]['lo'], lin[p_][2]['hi'])} ({vlin[p_]}; calibrated p = "
                       f"{cal[('l', p_)]['p_w']:.4f})" for p_ in pairs)
    rob = ctx["g3rob"]
    robtxt = []
    for lab_, r_ in rob.items():
        parts = []
        for p_ in pairs:
            for kind in ("normal scores", "linear z"):
                x_ = g("G3 UK rob.", f"{lab_}: {p_} ({kind}) disattenuated within")
                parts.append(f"{p_} {'Blom' if kind == 'normal scores' else 'linear'} "
                             f"{x_['verdict'].split(' (')[0].replace('agree less within universities', 'agree less')}")
        robtxt.append(f"{lab_} ({r_['n']} programmes): " + ", ".join(parts))
        assert any("cannot" in x_ for x_ in parts)
    a(f"3. **G3 — Pre-specified: the UK rankings agree less within universities than across them for all three "
      f"pairs, and so do US department prestige and pay. Revision 1: that rule is miscalibrated, but a calibrated "
      f"test and calibrated estimates give the same direction for all three UK pairs.** UK, scripts/76's T3(a) cells "
      f"({U['n']} programmes, {U['G']} providers, {U['S']} subjects), Pearson correlation of within-subject rank-normal "
      f"scores across providers and of their provider- and subject-FE residuals within providers; primary intake = "
      f"share of graduates with ≥ 360 UCAS points with 'low' (1–2 graduate) band cells coded as 1 "
      f"({ctx['uk_chk']['zero_share']['int1']:.0%} of programmes at 0, against "
      f"{ctx['uk_chk']['zero_share']['int0']:.0%} with 'low' = 0). Within-provider reliabilities: REF "
      f"{f3(rel['ref']['est'])} {fci(rel['ref']['lo'], rel['ref']['hi'])} ({rel['ref']['k'].split(' (')[0]}), pay "
      f"{f3(rel['pay']['est'])} {fci(rel['pay']['lo'], rel['pay']['hi'])}, intake {f3(rel['int']['est'])} "
      f"{fci(rel['int']['lo'], rel['int']['hi'])}. " + "; ".join(txt) + ". *Revision 1, added "
      f"after results were seen.* (i) *The rule is not calibrated.* Under H0 (ρ_within = ρ_between, calibrated to "
      f"the observed across correlations on the real layout; Method) the pipeline's disattenuated within correlation "
      f"averages " + ", ".join(f"{f3(nwd[('b', p_)]['est'])}" for p_ in pairs) + " against planted "
      + ", ".join(f"{rho0[p_]:.3f}" for p_ in pairs) + ": the Blom scores alone lower the within correlation "
      f"(noise-free under H0: " + ", ".join(f"{f3(ntw[('b', p_)]['est'])}" for p_ in pairs) + "), and the split-half "
      f"overstates the intake reliability ({f3(srel[('b', 'int')]['est'])} estimated against "
      f"{srel[('b', 'int')]['k'].split(' ')[1]} true under the model). The pre-specified rule then says 'agree less "
      f"within' in " + ", ".join(f"{p_} {size_b[p_]:.0%}" for p_ in pairs) + " of null data sets against a nominal "
      f"5%: too often for " + ", ".join(p_ for p_ in pairs if size_b[p_] > 0.05) + " (and, in the linear version "
      f"below, for " + ", ".join(p_ for p_ in pairs if size_l[p_] > 0.05) + "), so it is not a calibrated test "
      f"(Monte Carlo SE of a rate: up to {max(se_b.values()) * 100:.0f} points over {SIM_SIZE} data sets). How far it "
      f"is off depends on the model: {sens_txt}. (ii) "
      f"*Calibrated test:* " + "; ".join(nulltxt) + ". Every observed within correlation lies below its whole null "
      f"range. (iii) *Calibrated estimates* (ρ_within and ρ_between both free, "
      f"matched to the observed within and across correlations): ρ_within against ρ_between {caltxt}. (iv) *Linear "
      f"within-subject z version, co-primary* (reliabilities REF {f3(rl['ref']['est'])}, pay {f3(rl['pay']['est'])}, "
      f"intake {f3(rl['int']['est'])}): {lintxt}. Under the model its intake split-half is the most inflated "
      f"({f3(srel[('l', 'int')]['est'])} against {srel[('l', 'int')]['k'].split(' ')[1]} true) and its pre-specified "
      f"rule says 'agree less within' in " + ", ".join(f"{size_l[p_]:.0%}" for p_ in pairs) + " of null data sets. "
      f"The linear statistics are not calibration targets, and the model reproduces them less well: linear intake "
      f"split-half {f3(srel[('l', 'int')]['est'])} simulated against {f3(rl['int']['est'])} observed; linear across "
      + ", ".join(f"{p_} {f3(na[('l', p_)]['est'])} against {f3(lin[p_][0]['est'])}" for p_ in pairs) + ". The linear "
      f"calibrated p-values rest on that weaker fit. "
      f"(v) *Robustness* (pre-specified rule, whole pipeline rebuilt): " + "; ".join(robtxt) + ". Dropping programmes "
      f"with an intake share of 0 selects on a noisy variable (the floor is partly measurement), so it also changes "
      f"the error structure; in both subsets the rule can no longer separate the levels for some intake pairs. "
      f"(vi) *Pure between-provider correlations* (provider means of the subject-demeaned scores): "
      + ", ".join(f"{p_} {f3(btw[p_]['est'])} {fci(btw[p_]['lo'], btw[p_]['hi'])}" for p_ in pairs) + " (linear z "
      + ", ".join(f"{f3(btl[p_]['est'])}" for p_ in pairs) + "). The 'across' statistic of the binding text is a "
      f"within-subject total correlation: it mixes between-provider and within-provider variation, and so lies "
      f"between the two. US analogue (scripts/58 main-spec cells, {US['n']:,} programmes): across institutions within "
      f"field {f3(usa['est'])} {fci(usa['lo'], usa['hi'])}; within institutions, net of the main specification, "
      f"{f3(usw['est'])} {fci(usw['lo'], usw['hi'])}; λ_LB {f3(usl['est'])} {fci(usl['lo'], usl['hi'])} (jackknife; "
      f"scripts/58's formula); disattenuated {f3(usd['est'])} {fci(usd['lo'], usd['hi'])} — **{v3['US|main']}** "
      f"(pre-specified). Revision 1: with the full-leverage λ_LB {f3(uslf['est'])} {fci(uslf['lo'], uslf['hi'])} "
      f"(jackknife) the disattenuated value is {f3(usdf['est'])} {fci(usdf['lo'], usdf['hi'])} (bootstrap; jackknife "
      f"{fci(usdfj['lo'], usdfj['hi'])}), {v3['US_disfull|main']}; also correcting for pay noise {f3(usdfp['est'])} "
      f"{fci(usdfp['lo'], usdfp['hi'])}; with institution and field FE only {f3(usdf_fe['est'])} "
      f"{fci(usdf_fe['lo'], usdf_fe['hi'])} (λ_LB full {f3(uslf_fe['est'])}), {v3['US_disfull|fe']}. "
      f"*Revision 2, added after results were seen:* the controlled within value above is net of field-specific "
      f"selectivity and G slopes while the across value is raw, so the like-for-like US contrast uses institution "
      f"and field FE only within and the plain within-field coupling between; the controlled version is kept as the "
      f"stricter within-institution contrast. Like for like: within {f3(u2['w']['est'])} "
      f"{fci(u2['w']['lo'], u2['w']['hi'])} against across {f3(u2['a']['est'])} {fci(u2['a']['lo'], u2['a']['hi'])}; "
      f"within corrected for F {f3(u2['wd']['est'])}, for F and pay {f3(u2['wdb']['est'])} "
      f"{fci(u2['wdb']['lo'], u2['wdb']['hi'])}, against across corrected for F and pay {f3(u2['adb']['est'])} "
      f"{fci(u2['adb']['lo'], u2['adb']['hi'])}. Calibrated on the real US layout as for the UK (F with classical "
      f"error at the scripts/56 lower-bound reliability; pay with the scripts/73 noise; {uc['LB']['N']} null draws): "
      f"the observed within correlation lies against a null range {fci(gr('G3 US sim [LB]', 'null within-institution correlation')['lo'], gr('G3 US sim [LB]', 'null within-institution correlation')['hi'])} "
      f"(null ρ {uc['LB']['rho0']:.3f}), p = {uc['LB']['w']:.4f}; calibrated ρ_within {f3(uc['LB']['rw'])} "
      f"{fci(uc['LB']['lo'], uc['LB']['hi'])} against ρ_between {f3(uc['LB']['rb'])}; the pre-specified rule says "
      f"'agree less within' in {uc['LB']['size']:.0%} (Monte Carlo SE {uc['LB']['size_se'] * 100:.0f} points) of null "
      f"data sets — it corrects F only, and pay noise then pulls the within value down — so it is not a calibrated "
      f"test here either. With F's extrapolated reliability (sensitivity): p = {uc['EXT']['w']:.4f}, ρ_within "
      f"{f3(uc['EXT']['rw'])} {fci(uc['EXT']['lo'], uc['EXT']['hi'])} against {f3(uc['EXT']['rb'])}, rule rate "
      f"{uc['EXT']['size']:.0%}. The stricter contrast: within {f3(u2['wm']['est'])} {fci(u2['wm']['lo'], u2['wm']['hi'])}, "
      f"corrected {f3(u2['wdm']['est'])} {fci(u2['wdm']['lo'], u2['wdm']['hi'])} (not simulated: the latent model has "
      f"no institution traits).\n")
    # G4
    def g4(q):
        return g("G4", q)
    bs0, bl0 = g4("slope without intake control [low0]"), g4("slope with subject x intake slopes [low0]")
    r0 = g4("R-squared short / long [low0, tot]")
    bst, dst = g4("beta*(delta = 1) [low0, tot, R_max 1.3x]"), g4("delta* (beta = 0) [low0, tot, R_max 1.3x]")
    bst1, dst1 = g4("beta*(delta = 1) [low1, tot, R_max 1.3x]"), g4("delta* (beta = 0) [low1, tot, R_max 1.3x]")
    bw, dw = g4("beta*(delta = 1) [low0, win, R_max 1.3x]"), g4("delta* (beta = 0) [low0, win, R_max 1.3x]")
    rw = g4("R-squared short / long [low0, win]")
    bn, dn = g4("beta*(delta = 1) [low0, tot, R_max noise ceiling]"), g4("delta* (beta = 0) [low0, tot, R_max noise ceiling]")
    bwn, dwn = g4("beta*(delta = 1) [low0, win, R_max noise ceiling]"), g4("delta* (beta = 0) [low0, win, R_max noise ceiling]")
    assert bn["est"] < 0 and bwn["est"] < 0 and bw["est"] > 0 and dn["est"] < 1 and dwn["est"] < 1 and dw["est"] > 1
    same = G4["low0"]["pt"]["rmax_13_tot"] >= 1.0
    a(f"4. **G4 — a bound under named assumptions, not an estimate: the UK department slope survives proportional "
      f"selection on unobservables only on the within-R² scale under the 1.3× rule.** scripts/76's within-university "
      f"REF slope ({G4['n']} programmes, {G4['G']} providers) is {f3(bs0['est'], 4)} without and {f3(bl0['est'], 4)} "
      f"with subject-specific slopes on the programme's intake share; total R² (provider and subject fixed effects "
      f"included) {r0['est']:.4f} → {r0['k'].split(' ')[1]}. "
      + (f"1.3 × {r0['k'].split(' ')[1]} exceeds 1, so the two pre-specified R_max values coincide at 1. " if same else "")
      + f"With total R² (scripts/58's convention) and R_max = 1, δ = 1 gives β* = {f3(bst['est'], 4)} "
      f"{fci(bst['lo'], bst['hi'], 4)} and δ* = {dst['est']:.2f} {fci(dst['lo'], dst['hi'], 2)}: below Oster's δ = 1 "
      f"benchmark, though the β* interval includes 0 and the δ* interval includes 1 ('low' = 1: β* "
      f"{f3(bst1['est'], 4)}, δ* {dst1['est']:.2f}). With R² measured within (fixed effects partialled out: "
      f"{rw['est']:.4f} → {rw['k'].split(' ')[1]}) and R_max = 1.3 × the within R², β* = {f3(bw['est'], 4)} "
      f"{fci(bw['lo'], bw['hi'], 4)} and δ* = {dw['est']:.2f} {fci(dw['lo'], dw['hi'], 2)}: robust by the same "
      f"benchmark, and this is the only setting in which it is. With R_max capped by measurement error (1 minus the "
      f"sampling-noise share of the variance: {G4['low0']['pt']['rmax_n_tot']:.4f} total, "
      f"{G4['low0']['pt']['rmax_n_win']:.4f} within) δ* = {dn['est']:.2f} and {dwn['est']:.2f} and β* = "
      f"{f3(bn['est'], 4)} and {f3(bwn['est'], 4)}, negative on both scales (revision 1 wording). The script uses "
      f"Oster's approximate formula (as scripts/58), not the exact cubic solution. Nothing here identifies a causal "
      f"effect.\n")
    ratio_ = [cw[p_]["est"] / cb[p_]["est"] for p_ in pairs]
    v1_assert(d1["lo"] <= 0 <= d1["hi"] and fo["lo"] <= 1e-4, "G1 reading wording")
    a("**Reading against the working headline.** G3 is the direct test of the headline. The pre-specified rule "
      "turned out not to be a calibrated test, so the revision-1 reading rests on the calibrated test: on the real "
      "layout, with each ranking's measured noise built in, data in which universities and their departments "
      "share one correlation would give within-university correlations far above the observed ones for all three "
      f"UK pairs, and the calibrated within-university correlations are {min(ratio_):.2f} to {max(ratio_):.2f} times "
      f"the calibrated between-university ones. "
      + ((f"G1 no longer shows a conflict: adjusted for production inside the "
          f"design, the US department slope is {f3(d1['est'], 4)} against {f3(fo['est'], 4)} (the CS remainder "
          f"{f3(csd1['est'])} against {f3(cs0['est'])}), and its interval, like that of F's own slope, includes 0. The CS "
          f"remainder is estimated without {int(R2['counts']['name join'])} top departments lost to the name join (G2).\n")
         if _V1 else
         (f"G1 shows no conflict: adjusted for production alone inside the design, the US department slope is "
          f"{f3(d2['est'], 4)} against {f3(fo['est'], 4)} (the CS remainder {f3(csd2['est'])} against {f3(cs0['est'])}), "
          f"and its interval, like that of F's own slope, includes 0; the adjustment that adds the export ratio is not "
          f"informative under the 2026 release. With the repaired name join no top CS department is lost to the join; "
          f"{R2['n_missing']} of the top 50 are missing for 2026 selectivity or unreleased medians (G2).\n")))
    # ---------------- prespec ----------------
    a("## Pre-specification, choices and deviations\n")
    a(f"The tests and decision rules below were fixed on 2026-11-14 before any data were read for this script and are "
      f"copied verbatim into the script's docstring (SHA-256 of the block `{PRESPEC_SHA256}`, checked at run time). "
      f"Implementation choices were recorded the same day, before the first data run, after reading "
      f"SELECTIVITY_DEEP_RESULT.md, UK_TRIAD_RESULT.md, THEORY_TESTS_RESULT.md (T0) and CS_ADMISSION_RESULT.md, "
      f"whose table of top-50 CS departments missing from the scripts/58 sample already showed the likely G2 "
      f"diagnosis (SHA-256 `{CHOICES_SHA256}`). Amendment A1 was made after a coverage count and before any slope, "
      f"correlation or bound was computed (SHA-256 `{A1_SHA256}`). Revision 1 (below) came after the results and an "
      f"independent check of them; it changes none of these blocks. File times "
      f"are the only timestamps. Status labels in the table: pre = a quantity named in the binding text; sens = a "
      f"sensitivity named in the binding text ('low' = 0 intake, R_max = 1, the published REF reliability 0.536); the "
      f"verdict column applies the binding rule on pre and sens rows (and, marked as such, on some revision-1 rows); "
      f"check = a reproduction of a published number; expl. (C) = exploratory, but fixed in advance in the "
      f"implementation choices; blank = exploratory, added after the first results; rev. 1 = added in revision 1, "
      f"after results were seen.\n")
    a("```text\n" + _block("-----BEGIN PRESPEC-----", "-----END PRESPEC-----") + "```\n")
    a("<details><summary>Implementation choices (C0–C5) and amendment A1, verbatim</summary>\n")
    a("```text\n" + _block("-----BEGIN CHOICES-----", "-----END CHOICES-----")
      + _block("-----BEGIN AMENDMENT A1-----", "-----END AMENDMENT A1-----") + "```\n")
    a("</details>\n")
    a("Deviations and clarifications (first version):\n")
    a("- **What preceded A1.** The development run that produced A1's coverage count also computed the scripts/75 T0 "
      "reproduction numbers (published values, check rows below). No new slope, correlation, reliability or bound "
      "was computed before A1.")
    a(f"- **A1 (G1 cells).** F_DC exists for {cov['fdc']:,} of the {cov['n']:,} main-spec programmes. (a) is judged on "
      f"all {cov['n']:,} (the binding text's 'same programmes'); (b) on the programmes where F, F_perp and F_DC all "
      "exist, with the original re-estimated there. The C1 common-cell version of (a) is a sensitivity.")
    a("- **Seeds of G1 and G2.** These reuse scripts/58's bootstrap functions and seeds (one generator per "
      "specification group, B = 999), not a SeedSequence child per replicate as the general rule asks; this is what "
      "makes the original intervals reproduce exactly and every change paired. That part runs in one process, so the "
      "draws do not depend on a worker count. G3 and G4 follow the general rule (SeedSequence(78), one grandchild "
      "per replicate, B = 2,000).")
    a("- **'The 21 highest-ranked CS departments'** is read as the top-50 Wapman CS departments that are not in the "
      "CS-remainder sample (the common programmes behind +0.050); the script asserts that there are 21.")
    a("- **G3 US.** The binding text names only the residual-F reliability, so the rule uses r / √λ_LB with pay "
      "reliability 1; the versions that also correct for pay noise are exploratory.")
    a(f"- **G3 provider count.** The UK G3 cells are scripts/76's T3(a) cells ({U['n']} programmes, {U['G']} providers); "
      f"its pre-specified T2(a) slope is on its own cells (UK_TRIAD_RESULT.md), and G4 uses the intake-control cells "
      f"({G4['n']} programmes, {G4['G']} providers).")
    if G4["low0"]["pt"]["rmax_13_tot"] >= 1.0:
        a("- **G4.** On these cells 1.3 × R² of the controlled model exceeds 1, so the pre-specified R_max = 1.3 R² "
          "and the sensitivity R_max = 1 are the same number. The noise-ceiling R_max and the within-R² version are "
          "exploratory additions.")
    a("")
    # ---------------- revision 1 ----------------
    sz = ctx["uk_sizes"]
    a("## Revision 2\n")
    a("Every item below is *revision 2, added after results were seen*. No pre-specified verdict and no earlier number "
      "changes.\n")
    a(f"1. **US F–pay, like-for-like contrast and calibrated test.** The within side uses institution and field FE "
      f"only and the between side the plain within-field coupling; the controlled (main-spec) within value is kept as "
      f"the stricter within-institution contrast. Added: across-level reliabilities and the across correlation "
      f"corrected for F and pay noise; a parametric bootstrap of ρ_within = ρ_between on the real US layout "
      f"({uc['LB']['N']} null draws per reliability variant; F's reliability at the scripts/56 lower bound, primary, "
      f"and extrapolated, sensitivity), the calibrated ρ_within and ρ_between, and the false-positive rate of the "
      f"pre-specified rule under the calibrated null.")
    a(f"2. **Name-join sensitivity.** scripts/59's {al['n_map']} name aliases (imported) recover "
      f"{len(al['recovered'])} of the {al['n_lost']} CS departments lost to the name join, so no aliased "
      f"re-estimate is run." + ("" if _V1 else " (2026 re-baseline: the join is repaired, so none is lost.)"))
    a("3. **Memory.** Freed heap memory is returned to the system before worker processes start (no effect on any "
      "number).\n")
    a("## Revision 1\n")
    a("Every item below is *revision 1, added after results were seen* and an independent check of them. Each "
      "finding was checked against the data before it was applied; the pre-specified verdicts above are unchanged.\n")
    a(f"1. **G3: the pre-specified rule is miscalibrated under its null (confirmed in direction; smaller in size).** "
      f"A parametric bootstrap of ρ_within = ρ_between on the real layout ({N} null data sets, calibrated as in "
      f"Method) shows that the pipeline's disattenuated within correlation does not recover the planted ρ (Blom "
      f"scores shrink the within correlation; the split-half overstates the intake reliability), and the rule says "
      f"'agree less within' in " + ", ".join(f"{p_} {size_b[p_]:.0%}" for p_ in pairs) + " of null data sets (normal "
      "scores; linear z: " + ", ".join(f"{p_} {size_l[p_]:.0%}" for p_ in pairs) + ") against a nominal 5%. "
      + sens_txt + (". The rate is higher for " + ", ".join(up_t0) + " when the model carries less intake noise"
                    if up_t0 else ". The rates do not differ beyond Monte Carlo error between the two models")
      + ". An independent simulation, which found larger rates for pay–intake, is in line with the "
      "low-noise version; with the intake noise matched to the observed split-half the rate is lower"
      + (" but still above 5%" if size_b["pay-intake"] > 0.05 else "") + ". Added: the "
      "calibrated test (p-values "
      "against the null distribution of the observed within correlation), calibrated estimates of ρ_within and "
      "ρ_between, the linear within-subject z version as co-primary, two robustness subsets, the pure "
      "between-provider correlations, and model checks of the simulation. The first version's caveat that leaving "
      "the across level undisattenuated is 'conservative' is withdrawn.")
    a(f"2. **G3 US: λ with the full leverage (applied).** λ now also uses the diagonal of the annihilator of the full "
      f"design (M_ii), as the pay reliability does: λ_LB = {f3(uslf['est'])} against {f3(usl['est'])} with "
      f"scripts/58's formula. The reliabilities get delete-one-institution jackknife intervals instead of bootstrap "
      f"percentiles, which sit below their point estimates. The FE-only US version is reported with both λ.")
    a(f"3. **G3 sample labels (corrected).** The REF reliability uses {sz['ref'][0]} programmes and {sz['ref'][1]} "
      f"providers, the 'low' = 0 intake split-half {sz['int0'][0]} programmes, the pay split-half {sz['pay_half'][0]}; "
      f"the first version labelled every reliability row with the full {U['n']} programmes.")
    a(f"4. **G1(a): F_perp is not 'F net of production' inside the design (confirmed).** Within the scripts/58 design "
      f"(institution FE, field FE and field × traits removed) F_perp correlates {f3(pcp)} with the production rank and "
      f"{f3(pcx)} with the export-ratio rank"
      + ("" if _V1 or np.isfinite(pcp) else " (the production-rank correlation is undefined under the 2026 release: "
                                             "one field has a constant production rank)")
      + f". Added: the production adjustment inside the design (field × production "
      f"and export-ratio ranks as further slopes; and production only), now the primary production adjustment; "
      f"F_perp is kept as the pre-specified, flagged variant. The first version's statements that the CS remainder "
      f"vanishes under (a) and that (a) and (b) conflict are withdrawn.")
    a("5. **G2: Columbia's Scorecard name carries a city qualifier ('in the City of New York'), not a campus suffix "
      "(corrected).** The kind is now read from the Scorecard name; scripts/34's campus rule strips that qualifier "
      f"too, which is where the first version's label came from. The stage counts are unchanged; within the "
      f"{int(cnt['name join'])} name-join departments the split is now {n_campus} campus suffix, {n_city} city "
      f"qualifier, {n_tok} token search." + ("" if _V1 else " (2026 re-baseline: with the repaired join no "
                                              "department is lost to it, so the split is empty.)"))
    a("6. **G4 wording (applied).** The bound is robust only on the within-R² scale under the 1.3× rule; with R_max "
      "at the measurement-error ceiling δ* is below 1 and β* negative on both scales; the script uses Oster's "
      "approximate formula (as scripts/58), not the exact cubic solution.\n")
    # ---------------- key numbers ----------------
    n_inf_uk = int(sum(np.isinf(U["bs"][:, j]).sum() for j, k in enumerate(U["keys"]) if k.startswith("dis"))
                   + np.isinf(U["bs_fix"]).sum())
    n_inf_us = int(sum(np.isinf(US["bs"][:, j]).sum() for j, k in enumerate(US["keys"]) if k.startswith("dis")))
    a("## Key numbers\n")
    a("CI = 95%. *CI kind*: bootstrap = percentile interval; G1/G2 rows use scripts/58's institution cluster "
      "bootstrap (B = 999; per-field rows count a field in a draw only with ≥ 8 distinct institutions, + 1 per extra "
      "field-specific slope), G3 rows a provider (UK) or institution (US) cluster bootstrap with every reliability "
      "recomputed in each replicate (B = 2,000; robustness subsets B = 500), G4 rows a provider cluster bootstrap "
      "(B = 2,000); jackknife = delete-one-institution jackknife, estimate ± 1.96 SE; null 2.5–97.5% = the range of "
      "the statistic over the simulated null data sets (not a CI). SE = SD of the draws (jackknife SE for jackknife "
      "rows); MDE = 2.80 SE (80% power, 5% two-sided). Changes are paired (same draws). A disattenuated value is +inf "
      f"in a replicate where a needed reliability is ≤ 0; such replicates are kept (G3 UK: {n_inf_uk}, G3 US: "
      f"{n_inf_us} replicate values of this kind over all disattenuated rows). *status*: see the pre-specification "
      "section. k = sample.\n")
    A.extend(md_table(R))
    a("")
    # ---------------- G2 table ----------------
    cnt = R2["counts"]
    miss = R2["T"][~R2["T"].in_h3]
    a("## G2 — top-50 Wapman CS departments missing from the CS-remainder sample\n")
    a("rank = rank of the Wapman CS prestige score among departments with one (1 = top). Stage = first stage at which "
      "the department fails, in pipeline order (Wapman → Scorecard FoS earnings → name join → 2026 selectivity → "
      "1-/5-year medians → sample rules). Scorecard = the institution found (exact name, scripts/34 rule or the "
      "printed token search); the kind of name difference is read from the Scorecard name (revision 1). SAT 2026 / "
      "SAT era = whether that UNITID has SAT_AVG in the 2026 institution file / in scripts/68's era-matched controls "
      "(falls 2014–15). in 4-yr = in scripts/58's 4-year main sample.\n")
    a("| rank | Wapman department | stage | detail | Scorecard | UNITID | SAT 2026 | SAT era | in 4-yr | token search |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for _, r_ in miss.iterrows():
        a(f"| {r_.wrank} | {r_.wapman} | {r_.stage} | {r_.detail} | {r_.scorecard or '—'} | {r_.unitid or '—'} | "
          f"{r_.sat26 or '—'} | {r_.satE or '—'} | {'yes' if r_.in_y4 else 'no'} | {r_.search or '—'} |")
    a("")
    a("Counts: " + "; ".join(f"{s_} {int(cnt[s_])}" for s_ in STAGES) + f". Main cause: {R2['main']}; the "
      f"pre-specified branch {'fires' if R2['fires'] else 'does not fire'}.\n")
    # ---------------- method ----------------
    a("## Method\n")
    a("- **G1.** Cells: scripts/55's cells with scripts/58's 1- and 5-year medians (`s55.build_cells`, "
      "`s58.load_er_scorecard`), the main specification `s58.fe_build(cells, [SAT_AVG, ADM_RATE, PCTPELL, G], [], "
      "earnings)`. F_perp and F_DC come from scripts/75's own functions (`ipeds_doctorates`, `field_net`, "
      "`bt_offset` with the +1 degree convention and ridge 1e-3, `rk`): per Wapman field, F_perp = residual of rank(F) "
      "on rank(log(1 + research doctorates)) and rank(log((d_out + 1)/(d_in + 1))) over the field's ranked "
      "institutions with a doctorate count; F_DC = theta, and its rank among the field's ranked institutions in the "
      "public network. These reproduce scripts/75 T0 (check rows). The variant replaces `prestige_score` and is "
      "z-scored within field on the sample like F. Common slope and CR1 SE from `s58.fe_fit`; bootstrap "
      "`s58.fe_group_boot` with seed [58, 3, 1] (scripts/58's draws for the main spec; every variant on the same cells "
      "gets the same draws). CS remainder: `s58.fe_build(..., per_field=True)` for FE2_h3y4/y1/y5, `s58.fe_boot_pf` "
      "with seed [58, 11], ≥ 8 distinct institutions, horizons averaged per draw. Rule as pre-specified, with "
      "'original' = F on the same cells. *Revision 1:* the in-design production adjustment keeps F and adds the ranks "
      "of production and of the export ratio (over the same institutions T0 uses) as further field-specific slopes "
      "in fe_build, so β is the partial slope of F net of them within the design; the same seeds give the same "
      "draws, so the changes are paired with the original. The within-design correlations residualise the "
      "within-field z-scores on institution FE, field FE and the field × trait slopes.")
    a("- **G2.** Every bachelor's CS row of the FoS file (released or not) is matched to the Wapman name by exact "
      "normalised name (scripts/55's join), then by scripts/34's campus and city rules (`k_campus`, `k_city`, `best`), "
      "then by a token search (normalised name tokens without 'university', 'college', 'of', 'the', 'at', 'in', "
      "'and', 'campus', 'main', full name first, then the part before the first comma or hyphen; accepted only if "
      "exactly one Scorecard institution matches). Era-matched controls: `s68.read_hist` + `s68.era_table` (version E). "
      "The exploratory re-estimate replaces SAT_AVG, ADM_RATE and PCTPELL by their version-E values for every "
      "institution and re-runs the CS remainder (same functions and seed).")
    a("- **G3 UK.** Panel from scripts/76's functions (`load_ref`, `load_ref14`, `load_leo_prov`, `build_panel`, "
      "`load_pa_raw`, `add_revision_cols`); cells = scripts/76's T3(a) cells (its nested `fe_sample` re-stated). A "
      "second read of the LEO file keeps, per cohort, the median, lower and upper quartile and earnings count of the "
      "all-graduate row and the prior-attainment band counts with the 'low' code; the mean log median reproduces "
      "scripts/76's pay exactly and the pooled shares its intake columns. Blom scores within subject, standardised. "
      "Within = residuals on provider + subject FE (`s76.fe_resid`). Reliabilities as in Choices C3: pay noise per "
      "cohort SE = 1.2533 (UQ − LQ)/1.349/√n/median (scripts/73's SE of a median), mean over the released cohorts, "
      "divided by the within-subject variance of pay, kept by the exact diagonal of the FE annihilator; REF = "
      "within-provider correlation of residualised REF 2021 and REF 2014 scores; intake = odd/even cohort split-half "
      "with Spearman–Brown. Disattenuated r = r/√(rel_x rel_y). Provider cluster bootstrap (a provider drawn twice "
      "enters twice, with its own FE), scores fixed, everything else recomputed. *Revision 1:* the linear version "
      "replaces the Blom scores by within-subject z-scores of REF GPA, pay and the intake share (and of the REF 2014 "
      "and half-sample variables) and is otherwise identical; the pure between-provider correlation is the Pearson "
      "correlation, over providers, of the provider means of the subject-demeaned scores; the robustness subsets "
      "rebuild the whole pipeline after the filter (scripts/76's singleton rule re-applied).")
    a(f"- **G3 UK calibration (revision 1).** Latent scores T_k = u_k[provider] + v_k[programme] for REF, pay and "
      f"intake on the real {U['n']} programmes and {U['G']} providers, var(u_k) = π_k, var(v_k) = 1 − π_k, "
      f"corr(u) = ρ_between, corr(v) = ρ_within (3 × 3). Measurement as the data are made: REF 2021 and REF 2014 = "
      f"T_REF + independent normal error (the REF 2014 subset as observed); pay = mean over each programme's released "
      f"cohorts of log medians with that cohort's own noise variance (the scripts/73-style SE above); intake = per "
      f"cohort, graduates with ≥ 360 points ~ Binomial(known graduates of the cohort, expit(μ_s + κ_s T_int)), split "
      f"into bands with the subject's pooled band shares, every band count published as LEO does (rounded to 5, "
      f"1–2 = 'low' coded 1), shares pooled over cohorts and over the odd/even halves. Each simulated data set goes "
      f"through the whole pipeline (scores, reliabilities, both versions). Nuisance parameters are calibrated by "
      f"indirect inference ({SIM_CAL_ROUNDS} rounds of {SIM_CAL_M} data sets): π_k to the observed within-provider "
      f"variance share of each normal score, the REF error SD to the observed REF test–retest, μ_s and κ_s to each "
      f"subject's mean and SD of the observed share, and under H0 a common ρ per pair (ρ_within = ρ_between) to the "
      f"observed across correlation. Null: {N} data sets; p = (1 + #{{null ≤ observed}})/(1 + {N}), one-sided. Size "
      f"of the pre-specified rule: {SIM_SIZE} null data sets, each with its own {SIM_SIZE_B}-replicate provider "
      f"bootstrap. Calibrated estimates free ρ_within and match the observed within correlations as well "
      f"({SIM_CAL_ROUNDS} × {SIM_CAL_M}, then {SIM_ALTFIN} data sets); their approximate interval is ± 1.96 × the "
      f"simulated SD of the within correlation × (ρ_within / its simulated mean). Seeds: one SeedSequence(78) child "
      f"per stage and one grandchild per data set; the data sets run in {S['workers']} spawned worker processes and "
      f"the results do not depend on the number of workers.")
    a("- **G3 US.** Cells and design = scripts/58's main specification. Blom scores of F and log pay within field "
      "(SD 1, ddof 1 as fe_build). Within = residuals on institution FE and the main-spec regressors. λ = 1 − "
      "Σ(1 − rel_f)(1 − 1/n_i) / (residual SS of the F score), scripts/58's formula with scripts/56's relF_LB / "
      "relF_EXT; revision 1 adds λ_full = 1 − Σ(1 − rel_f) M_ii / (residual SS), M_ii the diagonal of the full "
      "annihilator. Pay reliability from scripts/73's per-programme se_main (`pseo_rows`, `field_dispersion`, "
      "`pseo_prog_disp`, `scorecard_programs`; its programmes reproduce the earnings exactly). Institution cluster "
      "bootstrap through per-institution cross-products; revision 1: delete-one-institution jackknife for the "
      "reliabilities.")
    a(f"- **G3 US calibration (revision 2).** Latent scores T_k = u_k[institution] + v_k[programme] for F and pay on "
      f"the real {US['n']:,} programmes and {US['G']} institutions, var(u_k) = π_k, corr(u) = ρ_between, corr(v) = "
      f"ρ_within. Observed F = √rel_f T_F + √(1 − rel_f) e, rel_f the field's scripts/56 reliability (LB primary, EXT "
      f"sensitivity), classical error as scripts/58's λ assumes; log pay = σ_f T_pay + normal noise with the "
      f"programme's scripts/73 variance, σ_f the field's signal SD. The layout is the released programmes, so "
      f"suppression is conditioned on; the medians are released to the dollar, so rounding is not modelled; the "
      f"Scorecard's documented differential-privacy perturbation is not modelled. Each data set goes through the "
      f"FE-only pipeline (Blom scores within field, institution and field FE, λ, pay and across-level reliabilities). "
      f"Calibration ({SIM_CAL_ROUNDS} rounds of {SIM_CAL_M}): π_F, π_pay to the observed within-institution variance "
      f"shares of the two scores, ρ to the observed across correlation (null), and ρ_within to the observed within "
      f"correlation (alternative, {SIM_ALTFIN} final draws). Size: {SIM_SIZE} null data sets, each with a "
      f"{SIM_SIZE_B}-replicate institution bootstrap of the pre-specified correction. Seeds and workers as for the UK "
      f"({ctx['g3us_sim']['workers']} spawned worker processes).")
    a("- **G4.** scripts/76's T2(a) intake-control cells and specification (`s76.fe_point`); total and within R²; "
      "δ* = β̃(R̃ − Ṙ)/((β̇ − β̃)(R_max − R̃)) and β*(δ = 1) = β̃ − (β̇ − β̃)(R_max − R̃)/(R̃ − Ṙ) (Oster's "
      "approximation, as in scripts/58, not the exact cubic solution), dot = without, tilde = with the intake slopes.")
    a("- **Reproducibility.** BLAS environment set to 8 threads before numpy is imported and every fit run under one "
      "BLAS thread; the simulation workers run with one BLAS thread. Two consecutive runs give byte-identical "
      "write-up and tables (md5 compared).\n")
    # ---------------- caveats ----------------
    a("## Caveats\n")
    a(f"- **F_perp is not production-free inside the design (revision 1).** scripts/75 T0 residualises rank(F) on the "
      f"ranks of production and the export ratio over all of a field's ranked institutions. Inside the "
      + (f"within-institution design that orthogonality does not hold (correlation {f3(pcp)} with the production rank), "
         f"so the F_perp slope mixes F with a negative production component; the in-design adjustment is the clean "
         if _V1 or np.isfinite(pcp) else
         f"within-institution design that orthogonality need not hold (under the 2026 release its correlation with the "
         f"production rank is undefined because one field has a constant production rank, and it is {f3(pcx)} with the "
         f"export-ratio rank), so the F_perp slope can mix F with production; the in-design adjustment is the clean ")
      + f"version of the binding text's question. The export ratio is itself a crude measure of the direction of "
      f"exchange, so controlling for it also removes part of the prestige ordering (the production-only row avoids "
      f"that).")
    a(f"- **F_DC changes the sample.** {cov['n'] - cov['fdc']:,} of the {cov['n']:,} main-spec programmes have no "
      "edge in the public field network and drop out of (b); on the remaining programmes F's own slope is "
      f"{f3(fbo['est'], 4)}, larger than on the full sample, so (b) is judged against that."
      if _V1 or cov['fdc'] < cov['n'] else
      f"- **F_DC and the sample.** Under the 2026 release every one of the {cov['n']:,} main-spec programmes has an "
      f"edge in the complete public field network, so (b) uses the full sample and F's own slope there is the "
      f"full-sample {f3(fbo['est'], 4)}.")
    a("- **G2 is a diagnosis of one sample.** The name join (scripts/55) is shared by every scripts/58 estimate, not "
      "only by CS; repairing it is a change of join rule and would move all of them. The token search identifies two "
      "Scorecard institutions by name tokens (listed); that identification is by name only."
      if _V1 else
      "- **G2 is a diagnosis of one sample.** The name join (scripts/55) is shared by every scripts/58 estimate, not "
      "only by CS; the 2026 re-baseline repairs it (explicit UNITID-anchored aliases), which moves all of them "
      "(WAPMAN_REBASELINE_RESULT.md).")
    a("- **The pre-specified G3 rule is not a calibrated test (revision 1).** Its verdicts are kept because they are "
      "the pre-specified ones, but under the calibrated null the rule says 'agree less within' more often than 5% for "
      + ", ".join(p_ for p_ in pairs if size_b[p_] > 0.05) + " (normal scores) and "
      + ", ".join(p_ for p_ in pairs if size_l[p_] > 0.05) + " (linear z); the calibrated test and the calibrated "
      "estimates are the revision-1 reading. The calibration "
      "rests on a model: classical normal REF error, normal sampling noise of medians, binomial intake counts with "
      "the subject's band mix and LEO rounding, and multivariate-normal latent scores with one provider share per "
      "variable, plus cohort-to-cohort intake noise. The model checks (simulated against observed across "
      "correlations, variance shares, REF test–retest, intake split-half and intake moments) are in the table; the "
      "linear version's statistics are not calibration targets and serve as an out-of-sample check, which the model "
      "passes less well for the intake pairs.")
    a(f"- **Reliabilities.** The intake split-half overstates the reliability of the intake score with respect to the "
      f"latent intake under the simulation model ({f3(srel[('b', 'int')]['est'])} estimated against "
      f"{srel[('b', 'int')]['k'].split(' ')[1]} true for normal scores, {f3(srel[('l', 'int')]['est'])} against "
      f"{srel[('l', 'int')]['k'].split(' ')[1]} for linear z). The split-half measures how reproducible the score is "
      f"across cohorts, not how closely it follows the latent intake: the share is a floored, nonlinear function of "
      f"the latent, its binomial noise is uneven across programmes of different size, and it is published in rounded "
      f"bands; the script does not separate these ingredients. The REF test–retest treats real change between REF "
      f"2014 and REF 2021 as error. "
      "Pay noise uses the normal approximation to the SE of a median. Intake and pay come from the same LEO rows, so "
      "their errors may be correlated.")
    a("- **The across statistic is a within-subject total correlation.** It mixes between-provider and "
      "within-provider variation; the pure between-provider correlations (provider means) are higher. Comparing a "
      "corrected within value with an uncorrected across value is not conservative in general (revision 1 withdraws "
      "that claim); the calibrated test compares like with like by running the same pipeline on data whose two "
      "levels have the same correlation.")
    a(f"- **US reliabilities and calibration.** The bootstrap percentiles of λ and of the pay reliability sit below "
      f"their point estimates (institutions drawn with replacement leave the {ctx['us_npar']} regressors fewer distinct "
      "institutions), so their intervals are jackknife intervals from revision 1 on. Revision 2 calibrates the US "
      "FE-only contrast by simulation under a classical-error model for F; the Wapman rank's error is a network "
      "estimation error, which that model only approximates, and the controlled contrast is not simulated.")
    a("- **G4 is a bound under named assumptions.** Proportional selection (δ), the R_max convention (total vs "
      "within R²) and Oster's approximation all matter; the intake share is a coarse, floor-affected measure of the "
      "programme's students. Nothing in this file is causal.\n")
    return "\n".join(A) + "\n"


def main():
    assert _sha(_block("-----BEGIN PRESPEC-----", "-----END PRESPEC-----")) == PRESPEC_SHA256, "PRESPEC block changed"
    assert _sha(_block("-----BEGIN CHOICES-----", "-----END CHOICES-----")) == CHOICES_SHA256, "CHOICES block changed"
    assert _sha(_block("-----BEGIN AMENDMENT A1-----", "-----END AMENDMENT A1-----")) == A1_SHA256, "A1 changed"
    assert INST_SLOPES == list(s58.INST_SLOPES)
    workers = int(os.environ.get("GAP78_WORKERS", "2"))
    assert 1 <= workers <= 6
    ctx = dict(g1lab=["F", "F_perp (a)", "F_DC rank (b)", "F_DC raw theta (b, sensitivity)"])
    if DEVCACHE and os.environ.get("GAP78_WRITEONLY"):          # development shortcut only: re-render the write-up
        with open(Path(DEVCACHE) / "ctx.pkl", "rb") as f:
            ctx = pickle.load(f)
        R = collect(ctx)
        OUT_MD.write_text(with_release_note(write_md(ctx, R)), encoding="utf-8")
        R.frame().drop(columns=["d"]).to_csv(OUT_CSV, index=False, float_format="%.10g")
        return
    with threadpool_limits(limits=1, user_api="blas"):
        stage("US cells and scripts/75 T0 objects")
        cells, ar, er_cs, inst = cached("us_cells", us_cells)
        T0, gmax = cached("t0", t0_objects)
        assert gmax < 1e-6
        t0rep = cached("t0rep", lambda: t0_reproduce(T0))
        for k, pub, tol in (("mean_r_p", 0.441, 5e-4), ("c_F", 0.387, 5e-4), ("c_DC", 0.325, 5e-4),
                            ("c_perp", 0.232, 5e-4)):
            v1_assert(abs(t0rep[k] - pub) < tol, f"T0 reproduction {k}: {t0rep[k]:.4f} vs v1 {pub}")
        v1_assert(t0rep["k"] == 56 and t0rep["cells"] == 2628, f"T0 k / cells (now {t0rep['k']} / {t0rep['cells']})")
        ctx.update(t0rep=t0rep, t0_gmax=gmax)
        R1 = cached("g1", lambda: run_g1(cells, T0))
        f0 = R1["full"][0]
        v1_assert((f0["n"], f0["G"], f0["k"]) == (2889, 168, 47), f"main-spec sample (now {f0['n']}, {f0['G']}, {f0['k']})")
        v1_assert(abs(f0["beta"] - 0.0084) < 5e-5 and abs(pct(f0["bs"], 2.5) - 0.0) < 5e-5
                  and abs(pct(f0["bs"], 97.5) - 0.0164) < 5e-5, f"main-spec slope (now {f0['beta']:+.4f})")
        c0 = R1["cs_full"][0]
        v1_assert(c0["n_cs"] == 128 and abs(c0["beta"] - 0.050) < 5e-4 and abs(pct(c0["bs"], 2.5) - 0.012) < 5e-4
                  and abs(pct(c0["bs"], 97.5) - 0.096) < 5e-4, f"CS remainder (now {c0['n_cs']}, {c0['beta']:+.3f})")
        ctx["g1"] = R1
        ctx["g1r1"] = cached("g1r1", lambda: run_g1_rev1(cells, T0, R1))
        R2 = cached("g2", lambda: run_g2(cells, ar, inst, R1))
        v1_assert(R2["n_missing"] == 21, f"top-50 CS departments missing (now {R2['n_missing']})")
        ctx["g2"] = R2
        ctx["alias"] = alias_check(R2, inst)
        stage("G3 US: scripts/73 programme noise, F-pay at both levels")
        noise = cached("us_noise", us_noise)
        D = us_g3_data(R1["full"][0]["M"], R1["rel"], noise)
        assert D["n_noise"] == len(D["d"])
        ctx["us_rho_sp"] = D["rho_sp"]
        ctx["us_npar"] = len(R1["full"][0]["M"]["names"])
        ctx["g3us"] = run_g3_us(D)
        stage(f"G3 US rev. 2: calibration simulation, FE-only contrast ({workers} worker processes)")
        ctx["g3us_sim"] = cached("g3us_sim", lambda: run_us_sim(D, ctx["g3us"], workers))
        del D, noise
        stage("UK panel (scripts/76) and per-cohort LEO rows")
        P = cached("uk_panel", uk_panel)
        Arows, Pa = cached("leo_coh", lambda: leo_cohort_rows(set(P.ukprn)))
        UD = uk_g3_data(P, Arows, Pa)
        ch = UD["chk"]
        assert ch["n6"] == 864 and np.allclose(ch["wtriad"], [0.109, 0.146, 0.261], atol=5e-4)
        assert np.allclose(ch["t4"], [0.580, 0.643, 0.694], atol=5e-4) and ch["t4_n"] == 876
        assert abs(ch["rel76"] - 0.536) < 5e-4 and ch["rel76_n"] == 814
        ctx["uk_chk"] = ch
        stage("G3 UK: provider cluster bootstrap")
        ctx["g3uk"] = run_g3_uk(UD)
        ctx["uk_sizes"] = UD["sizes"]
        stage(f"G3 UK rev. 1: calibration simulation ({workers} worker processes)")
        ctx["g3sim"] = run_g3_sim(UD, Pa, ctx["g3uk"], workers)
        stage("G3 UK rev. 1: robustness subsets")
        ctx["g3rob"] = run_g3_rob(P, Arows, Pa)
        stage("G4: Oster bound")
        G4 = run_g4(P, Arows)
        assert abs(G4["low0"]["pt"]["b_short"] - 0.0187) < 5e-5 and abs(G4["low0"]["pt"]["b_long"] - 0.0075) < 5e-5
        ctx["g4"] = G4
    if DEVCACHE:
        with open(Path(DEVCACHE) / "ctx.pkl", "wb") as f:
            pickle.dump(ctx, f)
    stage("write-up")
    R = collect(ctx)
    df = R.frame().drop(columns=["d"])
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, float_format="%.10g")
    R2["T"].to_csv(OUT_GAP, index=False)
    OUT_MD.write_text(with_release_note(write_md(ctx, R)), encoding="utf-8")
    for p in (OUT_MD, OUT_CSV, OUT_GAP):
        print(p.name, hashlib.md5(p.read_bytes()).hexdigest())
    stage("done")


if __name__ == "__main__":
    main()
