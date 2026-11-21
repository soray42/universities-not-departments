r"""scripts/84_test_calibration.py -- four referee gaps in the simulation-calibrated test of scripts/78 (G3): its size
when the nuisance parameters are re-estimated in every data set (T1), null models with field-specific university
loadings and with correlated pay-intake error (T2), the US headline on the largest (FE-only) sample (T3), and the UK
contrast with REF 2014 in place of REF 2021 (T4).

The block between the PRESPEC marker lines is the binding text, copied verbatim; it was fixed on 2026-11-16
before any outcome of this script was computed. The block between the CHOICES marker lines records implementation
choices made the same day, after reading scripts/78 and GAP_CHECKS_RESULT.md and timing the simulation code, and
before any T1-T4 outcome was computed. main() refuses to run if the SHA-256 of either block differs from
PRESPEC_SHA256 / CHOICES_SHA256. Anything not named in either block is labelled exploratory.

General rules (not part of the binding tests): public data only, all already on disk; every number in
TEST_CALIBRATION_RESULT.md is printed by this script; scripts/78 is imported, never edited (nor is any other script);
seeded so that a second run gives a byte-identical file; simulation loops in fork worker processes (up to 4, 2 if
less than 5 GB is available), one SeedSequence(84) descendant per replicate so that results do not depend on the
number of workers; run under `prlimit --as=2500000000`; descriptive, non-causal language.

-----BEGIN PRESPEC-----
T1 — Size audit of the calibrated test.
- For UK REF–pay, UK REF–intake, UK pay–intake and US F–pay (FE-only):
  - generate M = 200 data sets under H0 (ρ_within = ρ_between) on the real layout, at the fitted nuisance parameters;
  - in EACH data set, re-estimate the nuisance parameters exactly as scripts/78 does on real data;
  - run the full calibrated test with B = 200 inner null draws;
  - record rejection at the 5% level.
- Report the empirical size with its Monte Carlo SE.
- Repeat at two perturbed nuisance settings (reliabilities at the ends of their 95% intervals).
- Rule: "calibrated" if size ≤ 0.075; "liberal" otherwise.
- Also report power against the observed configuration, i.e. the fitted within and between values.

T2 — Heterogeneous loadings and correlated errors.
- Re-run the calibrated test on the real data with null models that
  - (a) let the university component load differently by field, with field-specific loadings drawn so that the across-university coupling varies across fields as much as observed (match the observed between-field SD of field-level coupling);
  - (b) add correlated measurement error between UK pay and intake, which come from the same LEO rows, at ρ_e = 0.2 and 0.5.
- Report p and the null range for each.
- Rule: the headline "rejects equal agreement" holds if p < 0.05 under (a), (b, 0.2) and (b, 0.5) for US F–pay and UK REF–pay.

T3 — Headline on the largest US sample.
- Compute the across and within correlations and the calibrated test on the FE-only sample, which does not need SAT: 4,645 programmes, 251 universities, 55 fields (see scripts/paper_checks/us_between.py, which rebuilds it).
- Report them next to the 3,961-programme main sample.
- Rule: the reading holds if the within value stays below the null range and p < 0.05.

T4 — UK REF 2014.
- Run the UK two-level contrast (across and within, the same statistic, plus the calibrated test) with REF 2014 in place of REF 2021, on REF 2014's own sample and on the sample common to both exercises.
- Compare the two exercises on the common sample with a paired cluster bootstrap.
- Same reading rule as T3.
-----END PRESPEC-----

-----BEGIN CHOICES-----
C0. Reproduction first. scripts/78's G3 calibration is re-run with its own functions (sim_task, us_sim_task,
    sim_inputs, us_sim_inputs) and its own seeds (the SeedSequence(78) children g3_sim_cal, g3_sim_null, g3_sim_alt,
    us_sim_cal, us_sim_null, us_sim_alt); its nested update rules are re-stated here. It must reproduce
    gap_checks_summary.csv: UK null rho +0.706 / +0.819 / +0.802, null within ranges and p = 0.0017; calibrated
    rho_within / rho_between +0.160 / +0.854, +0.350 / +0.899, +0.314 / +0.892; US (LB, FE-only, 3,961 cells) null
    rho +0.551, null within range [+0.282, +0.340], p = 0.0017, rho_within / rho_between +0.081 / +0.701. The
    reproduced null parameter sets are 'the fitted nuisance parameters' of T1 (H0) and the reproduced alternative
    parameter sets 'the observed configuration' (T1 power). The skipped size checks of scripts/78 use other seeds,
    so skipping them changes no draw.
C1. Lean evaluators. All new simulation (T1-T4) uses Blom-only re-implementations of scripts/78's generator and
    pipeline (same random-number calls in the same order; vectorised midranks; the provider + subject FE projection
    precomputed for fixed layouts); the linear-z statistics, which the calibration never uses, are not computed.
    At run time they are checked against scripts/78's sim_task / us_sim_task on 8 seeds (every shared statistic;
    the largest absolute difference is printed and must be < 1e-9).
C2. T1 layouts and the inner test. UK: the 864 G3 cells, one joint H0 for the three pairs (rho_within = rho_between
    for every pair, at scripts/78's fitted null); each pair's rejection is read off the same 200 data sets. US: the
    3,961 main-spec cells, FE-only contrast, F's reliability at the scripts/56 lower bound (scripts/78's primary).
    In every simulated data set the calibrated test is run as scripts/78 runs it on the real data: the targets
    (UK: across and within correlations, within-provider variance shares of the three normal scores, REF test-retest,
    intake split-half reliability, subject mean and SD of the intake share; US: across and within correlations and
    the two within-institution variance shares) and the starting values are computed from that data set; the
    data-dependent inputs are re-derived from it (UK: each subject's pay signal SD, each cohort's known-band graduate
    count, the subjects' band shares, from the simulated published band counts with 'low' counted as 1.5; US: each
    field's pay signal SD); then 12 rounds x 64 data sets of damped moment matching (damping 0.5) and B = 200 null
    draws. What an analyst treats as known stays at the published values: the per-cohort pay SEs (UK), the
    per-programme pay noise and F's per-field reliability (US), the REF 2014 subset, the release pattern of cohorts.
    p = (1 + #{null within <= observed within}) / (1 + B), one-sided; reject at the 5% level if p <= 0.05 (at most 9
    of 200 null draws at or below). Size = share of rejections over M = 200, Monte Carlo SE = sqrt(s(1 - s)/M).
    An inner test that fails (any exception, e.g. a correlation matrix that is not positive definite after the
    +-0.95 clips) is counted and reported; it counts as a rejection in a size and as a non-rejection in a power.
C3. T1 perturbed settings. 'low' = every reliability at the lower end of its 95% interval in gap_checks_summary.csv,
    'high' = every one at the upper end. Only the generating truth moves; the inner test is unchanged. UK: REF
    test-retest [+0.452, +0.587] (carried by the REF error SD) and intake split-half [+0.384, +0.637] (carried by
    the intake cohort noise tau) become the calibration targets of the generating model (12 x 64 from the fitted
    null, every other target as observed); pay reliability [+0.795, +0.862] around +0.836: the true per-cohort noise
    variance is multiplied by c = (1 - end) / (1 - 0.836) and each subject's signal SD set so that its pay variance
    is unchanged. US: F's per-cell error variance (1 - relF) multiplied by c_F = (1 - end) / (1 - 0.688) (FE-only
    lambda_LB with full leverage, [+0.667, +0.710]) and the pay noise variance by c_Y = (1 - end) / (1 - 0.548)
    (FE-only pay reliability, [+0.512, +0.585]), each field's pay signal SD set so that its pay variance is
    unchanged, pi and rho re-matched (12 x 64 from the fitted null). The generating values reached are printed.
C4. T1 power: data generated at the reproduced calibrated alternative (UK: rho_within and rho_between free for all
    three pairs with the alternative's other parameters; US: rho_within, rho_between and pi of the alternative),
    M = 200, the same inner test.
C5. T2 (a). Field-level coupling = Pearson correlation, over the cells of one field (US) or subject (UK), of the
    within-field normal scores (the across statistic computed within one field); between-field SD = SD (ddof 1,
    unweighted) over the 53 US fields / 15 UK subjects; UK: the three pairs. Null model: T_k = m_kf u_k[university]
    + v_k, m_kf = exp(s eta_kf - s^2) (so E m^2 = 1), eta_kf independent N(0, 1) across variables and fields and
    redrawn in every simulated data set (independent loadings are the form that can lower the within-university
    correlation under equal agreement); one dispersion s per country (UK: common to REF, pay and intake). s is
    matched through the pipeline, so sampling noise is on both sides: target = observed between-field variance of
    the coupling (UK: mean over the three pairs); sampling floor V0 = its simulated mean at s = 0 under the
    reproduced homogeneous null (128 data sets). If the observed value is at or below V0, s = 0 and (a) is the
    baseline null (said so). Otherwise s starts at 0.3 and, in each of the 12 rounds, s^2 is multiplied by
    ((V_obs - V0) / (V_sim - V0))^0.5 (ratio clipped to [1/4, 4]) while pi, rho and the other nuisance parameters
    are matched as in scripts/78 (from scripts/78's starting values). Then 600 null draws (as scripts/78); p and
    the null range. The achieved SD per pair is printed.
C6. T2 (b), UK only (US F and pay come from different sources, so there is no US (b); the US rule reads on (a)
    alone). In each released cohort of each programme the pay noise of the cohort's log median is
    se_c (rho_e zeta_c + sqrt(1 - rho_e^2) xi_c), xi_c the model's own standard normal draw and zeta_c the cohort's
    standardised intake error: delta_c = the cohort's realised share with >= 360 points (graduates with >= 360 points
    over known-band graduates, before publication rounding) minus the programme's latent expected share
    expit(mu_s + kappa_s T_int), divided by sqrt(p(1 - p)/N_c + (kappa_s p(1 - p) tau)^2) (binomial plus cohort
    noise, delta method); zeta_c = 0 where N_c = 0. The pay noise variance is unchanged. rho_e = +0.2 and +0.5
    (pre-specified); -0.2 and -0.5 are exploratory. Every nuisance parameter is re-matched as in scripts/78 with
    rho_e held fixed; 600 null draws. The realised error correlations are printed (per cohort, and between the
    within-provider errors of the pay and intake normal scores). T2 rule: holds if p < 0.05 for UK REF-pay under (a),
    (b, +0.2) and (b, +0.5) and for US F-pay under (a); every pair is reported.
C7. Null range = the 2.5-97.5% range of the null distribution of the within-university correlation (scripts/78's
    definition); its minimum is printed as well. 'Below the null range' = below its 2.5% point.
C8. T3. FE-only sample = s58.fe_build(cells, [], [], 'earnings') on scripts/78's US cells (scripts/58's fe_sample
    rules without the selectivity controls), expected 4,645 programmes, 251 universities, 55 fields; reliabilities
    and pay noise as scripts/78 (us_g3_data; a field without a scripts/56 reliability gets the mean, count printed).
    Across and within (institution + field FE) with an institution cluster bootstrap (2,000 replicates) on both
    samples; the calibrated test (scripts/78's US schedule, F at the lower bound, 600 null draws) on the FE-only
    sample; the main sample's test is the C0 reproduction. Rule as written, applied to the FE-only sample.
C9. T4. REF 2014's own sample: scripts/76's rules with REF 2014 GPA in place of REF 2021 (clean subjects; REF 2014
    GPA, pay, intake share, band score known; >= 15 providers per subject; singletons dropped), REF 2021 as the
    test-retest partner of the REF reliability. Common sample: the cells with both REF scores under the same rules
    (built from either exercise's sample; asserted identical). Statistics as scripts/78 G3 (Blom scores within
    subject; across; within provider + subject FE; reliabilities; disattenuated within), with a provider cluster
    bootstrap (2,000). Calibrated test (scripts/78's UK null schedule, 600 null draws) with REF 2014 on its own
    sample and on the common sample; REF 2021 on the common sample is exploratory. Paired comparison: on the common
    sample, one set of 2,000 provider draws for both exercises; REF 2014 minus REF 2021 for the across, within and
    disattenuated within correlations of REF-pay and REF-intake, percentile intervals. Verdict per pair with the T3
    rule; the reading rests on REF-pay (REF-intake reported with its verdict; pay-intake does not involve REF).
C10. Seeds and workers. One child of SeedSequence(84) per named analysis (fixed list, names only appended), one
    descendant per data set; fork worker processes, up to 4 (2 if `free -m` shows less than 5 GB available);
    BLAS 1 thread everywhere. The result file carries no timings, memory figures, worker counts or run dates.
-----END CHOICES-----

-----BEGIN AMENDMENT A1-----
A1 (2026-11-16, after a development run and before any T2 (a) p-value was computed). A development run (2 to 12
calibration rounds, 40 null draws) printed p-values for T2 (b), T3 and T4 (all at their minimum attainable value) and,
for T2 (a), only the calibrated dispersion s, which ran away (US s = 9.5). With C5's loadings exp(s eta - s^2) the
simulated between-field SD of the coupling cannot reach the observed one (US F-pay: observed 0.237, sampling floor
0.147, at most about 0.174 over s; UK REF-pay / REF-intake / pay-intake: observed 0.163 / 0.113 / 0.286, at most
about 0.14 / 0.16 / 0.17; grids at fixed pi and rho), and as s grows every loading tends to 0, so the university
component vanishes and such a null rejects trivially. C5's multiplicative s update is therefore replaced by a fixed
grid and the family of loadings is widened; C5 is otherwise unchanged (coupling statistic, independent loadings
redrawn in every data set, one s per country, 600 null draws).
  Families, in this order: (L) C5's m = exp(s eta - s^2) for every variable; (N) m = 1 + s eta for every variable
  (sign-varying, mean 1); (P) m = 1 + s eta for pay only (the other variables load 1). Grid s in {0.1, 0.2, 0.3,
  0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5}. At each grid point the other nuisance parameters are re-matched by
  scripts/78's null schedule from scripts/78's starting values (12 x 64); then 64 check data sets give the simulated
  SD of the coupling per pair (root mean of its between-field variance), the across correlations and the
  within-university variance shares q. A point matches SD if the simulated SD of the rule's pair (US F-pay; UK
  REF-pay) is at least the observed one; matches across if every simulated across correlation is within 0.01 of the
  observed one; matches shares if every q is within 0.01 of the observed one and pi < 0.98 for every variable. A
  point whose fit fails (an exception) matches nothing.
  Selection: (1) the smallest s of the first family, in the order above, with a point matching SD, across and
  shares: that null is (a). (2) Otherwise the smallest s of the first family with a point matching SD and across:
  (a) is that null, its share misfit is printed, and the share-consistent null of the same family (largest s
  matching across and shares) is reported beside it as exploratory. (3) Otherwise '(a) not implementable as
  written; rule not evaluable', and two nulls are reported: the point with the largest SD of the rule's pair among
  those matching across, and the share-consistent null of family (L). Each reported null gets 600 null draws (new
  seeds, the grid point's matched parameters); p and the null range as in C7. The whole grid table is printed.
-----END AMENDMENT A1-----

REVISION 1 (2026-11-17; added after results were seen; outside the hashed blocks, which are
unchanged). T1: Clopper-Pearson intervals for every size and power, the binary size reading kept only where the
interval lies wholly on one side of 0.075, corrected wording of what the perturbed settings misspecify, the share of
H0 data sets at the floor p. T2 (a): A1 rows labelled post hoc (a scratch diagnostic and a development run preceded the reported
run), a null for every grid point matching the spread and the across correlations, a denser US grid (family N,
s 0.62-0.68) locating where the rejection fails, no (a) conclusions for the intake pairs, the share-consistent null
described as effectively homogeneous. T2 (b): uninformative for REF-pay. T4: a re-measurement, not an independent
replication. A summary of how far the observed within values sit below the nulls. The joint audit (heterogeneous
loadings plus misspecified noise) is not run. No earlier number or pre-specified verdict changes.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "NUMEXPR_MAX_THREADS"):
    os.environ[_v] = "1"                          # BLAS 1 thread everywhere (C10), set before numpy is imported
import ctypes
try:                                              # fewer malloc arenas: address-space cap of 2.5 GB per process
    ctypes.CDLL("libc.so.6").mallopt(-8, 2)       # M_ARENA_MAX = 2 (no effect on any number)
except (OSError, AttributeError):
    pass
import sys
import time
import pickle
import hashlib
import warnings
import importlib.util
import multiprocessing as mp
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy.stats import norm
from threadpoolctl import threadpool_limits

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PRESPEC_SHA256 = "93e7fbcd54586fea22f6c34dc9217093625ff74081572ee22de9cd483d1ebfe7"
CHOICES_SHA256 = "c6f5555f2627877dc6f54bf00c99edd27d20413814fec2a1e8faf40edfebab02"
A1_SHA256 = "de0461c25bedafb847307dac63756a9209b7f5540657509e8cf4cf4a648317b9"


def _block(begin: str, end: str) -> str:
    return __doc__.split(begin + "\n", 1)[1].split(end, 1)[0]


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s78 = _load("s78", "78_gap_checks.py")            # scripts/78 (not edited); it loads scripts/58, 62, 68, 73, 75, 76
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"                          # scripts/78 sets 8 at import; numpy is already loaded with 1
s58, s76, s62 = s78.s58, s78.s76, s78.s62
T0_ = time.time()


def stage(msg: str):
    print(f"[{time.time() - T0_:7.1f}s] {msg}", flush=True)


# ---- sizes (pre-specified); GAP84_* overrides are a development shortcut only (reported runs do not set them)
_DEVKEYS = ("GAP84_M", "GAP84_B", "GAP84_NULL", "GAP84_BOOT", "GAP84_ROUNDS")
DEVRUN = any(os.environ.get(k) for k in _DEVKEYS)
M_OUT = int(os.environ.get("GAP84_M", 200))              # T1 outer data sets per setting
B_IN = int(os.environ.get("GAP84_B", 200))               # T1 inner null draws
NULL_N = int(os.environ.get("GAP84_NULL", s78.SIM_NULL))  # null draws of a calibrated test on real data (600)
B_BOOT = int(os.environ.get("GAP84_BOOT", 2000))          # cluster bootstrap replicates (T3, T4)
CAL_R = int(os.environ.get("GAP84_ROUNDS", s78.SIM_CAL_ROUNDS))   # 12 calibration rounds
CAL_M, DAMP = s78.SIM_CAL_M, s78.SIM_DAMP                # 64 data sets per round, damping 0.5
FLOOR_N = 128                                            # T2 (a): data sets for the sampling floor V0
FASTCHK_N = 8                                            # C1: seeds of the lean-evaluator check
ALPHA = 0.05
OUT_DIR = Path(os.environ.get("GAP84_OUT", str(ROOT)))   # development runs write elsewhere
OUT_MD = OUT_DIR / "TEST_CALIBRATION_RESULT.md"
OUT_CSV = (OUT_DIR / "data" / "interim" if OUT_DIR == ROOT else OUT_DIR) / "test_calibration_summary.csv"
DEVCACHE = os.environ.get("GAP84_DEVCACHE")              # development shortcut only (pickled loader output)
GAP_CSV = ROOT / "data" / "interim" / "gap_checks_summary.csv"
PAIRS = list(s78.PAIRS3)                                 # REF-pay, REF-intake, pay-intake
RHO_E = [0.2, 0.5, -0.2, -0.5]                           # T2 (b): first two pre-specified, last two exploratory

ANALYSES = ["fastcheck",
            "t1_uk_dgp_low", "t1_uk_dgp_high", "t1_us_dgp_low", "t1_us_dgp_high",
            "t1_uk_base", "t1_uk_low", "t1_uk_high", "t1_uk_power",
            "t1_us_base", "t1_us_low", "t1_us_high", "t1_us_power",
            "t2_us_a_floor", "t2_us_a_cal", "t2_us_a_null", "t2_uk_a_floor", "t2_uk_a_cal", "t2_uk_a_null",
            "t2_uk_b+0.2_cal", "t2_uk_b+0.2_null", "t2_uk_b+0.5_cal", "t2_uk_b+0.5_null",
            "t2_uk_b-0.2_cal", "t2_uk_b-0.2_null", "t2_uk_b-0.5_cal", "t2_uk_b-0.5_null",
            "t3_boot_fe", "t3_boot_main", "t3_cal", "t3_null",
            "t4_boot_own", "t4_boot_common", "t4_own_cal", "t4_own_null", "t4_c14_cal", "t4_c14_null",
            "t4_c21_cal", "t4_c21_null",
            # amendment A1 (appended)
            "t2_uk_a_grid", "t2_us_a_grid", "t2_uk_a_null2", "t2_us_a_null2",
            # revision 1 (appended)
            "t2_uk_a_all", "t2_us_a_all", "t2_us_a_dense", "t2_us_a_dense_null"]
DENSE_S = [0.62, 0.64, 0.66, 0.68]                                     # revision 1: US family N between 0.6 and 0.7
GRID_S = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5]     # A1
FAMS = ["L", "N", "P"]                                                 # A1: loading families, in this order
FAM_LAB = {"L": "exp(s eta - s^2), every variable (C5)", "N": "1 + s eta, every variable",
           "P": "1 + s eta, pay only"}
_ROOT_SS = np.random.SeedSequence(84)
KID = {nm: np.random.SeedSequence(_ROOT_SS.entropy, spawn_key=(i,)) for i, nm in enumerate(ANALYSES)}


def sk(ss: np.random.SeedSequence, i: int) -> np.random.SeedSequence:
    """Child i of a SeedSequence by explicit spawn key (= the i-th child .spawn() gives; independent of call order)."""
    return np.random.SeedSequence(ss.entropy, spawn_key=tuple(ss.spawn_key) + (i,), pool_size=ss.pool_size)


def kids(ss, n: int) -> list:
    return [sk(ss, i) for i in range(n)]


def k78(name: str) -> np.random.SeedSequence:
    """scripts/78's SeedSequence(78) child of a named analysis (C0 reproduction)."""
    return np.random.SeedSequence(78, spawn_key=(s78.ANALYSES.index(name),))


assert all(sk(np.random.SeedSequence(5), i).generate_state(2).tolist() == c.generate_state(2).tolist()
           for i, c in enumerate(np.random.SeedSequence(5).spawn(3)))
assert k78("g3_sim_cal").generate_state(2).tolist() == s78._KIDS["g3_sim_cal"].generate_state(2).tolist()


# =============================================================================================================
# lean evaluators (C1): Blom-only re-implementations of scripts/78's generator and pipeline
# =============================================================================================================
def gmid(v: np.ndarray, gid: np.ndarray) -> np.ndarray:
    """Midranks (1-based, ties averaged) of v within groups gid: scipy rankdata('average') per group, vectorised."""
    n = len(v)
    o = np.lexsort((v, gid))
    vs, gs = v[o], gid[o]
    pos = np.arange(n)
    newg = np.ones(n, bool)
    newg[1:] = gs[1:] != gs[:-1]
    gstart = np.maximum.accumulate(np.where(newg, pos, 0))
    newr = newg.copy()
    newr[1:] |= vs[1:] != vs[:-1]
    rs = pos[newr]
    re_ = np.r_[rs[1:], n] - 1
    rid = np.cumsum(newr) - 1
    r = np.empty(n)
    r[o] = (rs[rid] + re_[rid]) / 2.0 - gstart + 1.0
    return r


def gblom(v, gid, K: int, ddof: int) -> np.ndarray:
    """Blom scores within groups, standardised to mean 0, SD 1 (given ddof) within the group."""
    v = np.asarray(v, float)
    ng = np.bincount(gid, minlength=K).astype(float)
    x = norm.ppf((gmid(v, gid) - 0.375) / (ng[gid] + 0.25))
    xc = x - (np.bincount(gid, x, K) / ng)[gid]
    sd = np.sqrt(np.bincount(gid, xc * xc, K) / (ng - ddof))[gid]
    return np.where(sd > 0, xc / np.where(sd > 0, sd, 1.0), 0.0)


def gvar(v, gid, K: int, ddof: int) -> np.ndarray:
    ng = np.bincount(gid, minlength=K).astype(float)
    vc = v - (np.bincount(gid, v, K) / ng)[gid]
    return np.bincount(gid, vc * vc, K) / (ng - ddof)


def fe_proj(pid: np.ndarray, sid: np.ndarray) -> dict:
    """Provider + subject FE of a fixed layout, precomputed (scripts/78 fe_res_np algebra)."""
    G, S = int(pid.max() + 1), int(sid.max() + 1)
    cnt = np.bincount(pid, minlength=G).astype(float)
    Sd = np.zeros((len(sid), S))
    Sd[np.arange(len(sid)), sid] = 1.0
    St = s78._dm_np(Sd[:, 1:], pid, G)
    Q = np.linalg.pinv(St.T @ St, hermitian=True)
    return dict(pid=pid, G=G, St=St, Q=Q, h=1.0 / cnt[pid] + ((St @ Q) * St).sum(axis=1))


def fe_apply(Pj: dict, M: np.ndarray) -> np.ndarray:
    Mw = s78._dm_np(M, Pj["pid"], Pj["G"])
    return Mw - Pj["St"] @ (Pj["Q"] @ (Pj["St"].T @ Mw))


def corr(a, b) -> float:
    return s78.corr(a, b)


def _xstream(ss) -> np.random.Generator:
    """Extra random stream of a data set (T2 (a) loadings), so that the scripts/78 stream itself is unchanged."""
    return np.random.default_rng(sk(ss, 999983))


def loadings(eta: np.ndarray, s_: float, fam: str, j_pay: int) -> np.ndarray:
    """Field-specific loadings of the university component (C5; families of amendment A1)."""
    if fam == "L":
        return np.exp(s_ * eta - s_ ** 2)
    if fam == "N":
        return 1.0 + s_ * eta
    m = np.ones_like(eta)
    m[:, j_pay] = 1.0 + s_ * eta[:, j_pay]
    return m


# ---------------- UK ----------------
def uk_layout(D: dict, inp: dict) -> dict:
    """Real UK layout: scripts/78 sim_inputs plus the fixed FE projections and the real per-subject pay moments."""
    d = D["d"]
    sid, pid = inp["sid"], inp["pid"]
    S = int(sid.max() + 1)
    ri = inp["ref_idx"]
    L = dict(inp)
    L.update(S=S, cS=np.bincount(sid, minlength=S).astype(float),
             var_pay=d.groupby("subject").pay.transform(lambda v: v.var(ddof=0)).to_numpy(),
             ms2=pd.Series(D["s2_log"]).groupby(sid).transform("mean").to_numpy(),
             full=fe_proj(pid, sid), sr=s78.fac(sid[ri]), refP=fe_proj(s78.fac(pid[ri]), s78.fac(sid[ri])))
    L["Sr"] = int(L["sr"].max() + 1)
    L.pop("groups", None)
    return L


def uk_gen(L: dict, ss, par: dict, opt: dict | None = None) -> dict:
    """scripts/78 sim_data with the same random-number calls in the same order. opt: pay_c (true pay noise variance
    x c, each subject's signal SD set so that its pay variance is unchanged; T1), load_s (field-specific university
    loadings; T2 (a)), rho_e (pay-intake error correlation; T2 (b)), keep_err. Also returns the published band
    counts with 'low' counted as 1.5 (inputs of the inner test)."""
    opt = opt or {}
    rng = np.random.default_rng(ss)
    n, G, sid = L["n"], L["G"], L["sid"]
    pi = np.asarray(par["pi"])
    u = rng.multivariate_normal(np.zeros(3), s78.corrmat(par["rho_b"]), size=G) * np.sqrt(pi)
    v = rng.multivariate_normal(np.zeros(3), s78.corrmat(par["rho_w"]), size=n) * np.sqrt(1 - pi)
    s_ = float(opt.get("load_s", 0.0))
    if s_ > 0:
        m = loadings(_xstream(ss).standard_normal((L["S"], 3)), s_, opt.get("load_fam", "L"), 1)
        T = m[sid] * u[L["pid"]] + v
    else:
        T = u[L["pid"]] + v
    e = rng.standard_normal((n, 2)) * par["sig_ref"]
    ref21, ref14 = T[:, 0] + e[:, 0], T[:, 0] + e[:, 1]
    c_ = float(opt.get("pay_c", 1.0))
    if c_ == 1.0:
        se, sig_pay = L["se"], L["sig_pay"]
    else:
        se = L["se"] * np.sqrt(c_)
        sig_pay = np.sqrt(np.maximum(L["var_pay"] - c_ * L["ms2"], 1e-8))
    xi = rng.standard_normal((n, 4))
    Tc = T[:, 2][:, None] + par["tau"] * rng.standard_normal((n, 4))
    mu_, ka_ = np.asarray(par["mu"])[sid][:, None], np.asarray(par["kappa"])[sid][:, None]
    p = 1.0 / (1.0 + np.exp(-(mu_ + ka_ * Tc)))
    NT = L["NT"]
    top = rng.binomial(NT, p)
    p1 = rng.binomial(top, L["pa1"][:, None])
    p2 = top - p1
    low = rng.multinomial(NT - top, L["LOWP"][:, None, :])
    re_ = float(opt.get("rho_e", 0.0))
    out = {}
    if re_ != 0.0:
        p0 = 1.0 / (1.0 + np.exp(-(mu_ + ka_ * T[:, 2][:, None])))
        ntf = NT.astype(float)
        dl = np.where(NT > 0, top / np.where(NT > 0, ntf, 1.0), 0.0) - p0
        sdz = np.sqrt(p0 * (1 - p0) / np.where(NT > 0, ntf, 1.0) + (ka_ * p0 * (1 - p0) * par["tau"]) ** 2)
        zeta = np.where(NT > 0, dl / sdz, 0.0)
        noise = se * (re_ * zeta + np.sqrt(1 - re_ ** 2) * xi)
        if opt.get("keep_err"):
            ok = L["has_med"] & (NT > 0)
            out["err_cohort_corr"] = corr(noise[ok], dl[ok])
    else:
        noise = xi * se
    ly = sig_pay[:, None] * T[:, 1][:, None] + noise
    ly = np.where(L["has_med"], ly, np.nan)
    pay = np.nanmean(ly, axis=1)
    R12 = s78.rnd5(p1, 1) + s78.rnd5(p2, 1)
    RL = s78.rnd5(low, 1).sum(axis=2)

    def share(mask):
        num = (R12 * mask).sum(axis=1)
        den = num + (RL * mask).sum(axis=1)
        return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)
    intk, hA, hB = share(np.ones(4, bool)), share(s78.HA_MASK), share(~s78.HA_MASK)
    nmiss = int(np.isnan(intk).sum())
    if nmiss:
        med = pd.Series(intk).groupby(sid).transform("median").to_numpy()
        intk = np.where(np.isnan(intk), med, intk)
    out.update(T=T, ref21=ref21, ref14=ref14, pay=pay, int=intk, hA=hA, hB=hB, nmiss=nmiss,
               pub=(s78.rnd5(p1, 1.5), s78.rnd5(p2, 1.5), s78.rnd5(low, 1.5)))
    return out


def uk_eval(L: dict, X: dict, cf: bool = False, err: bool = False) -> dict:
    """scripts/78 sim_scores + sim_eval, Blom ('b') statistics only, on the full rows (no resampling)."""
    sid, S, pid = L["sid"], L["S"], L["pid"]
    Z = np.column_stack([gblom(X[k], sid, S, 0) for k in ("ref21", "pay", "int")])
    s2z = L["s2"] / gvar(np.asarray(X["pay"], float), sid, S, 0)[sid]
    ri = L["ref_idx"]
    ZR = np.column_stack([gblom(X[k][ri], L["sr"], L["Sr"], 0) for k in ("ref21", "ref14")])
    okh = np.isfinite(X["hA"]) & np.isfinite(X["hB"])
    hi_ = np.flatnonzero(okh)
    cnt = np.bincount(sid[hi_], minlength=S)[sid[hi_]]
    hi_ = hi_[cnt >= 2]
    sh = s78.fac(sid[hi_])
    ZH = np.column_stack([gblom(X[k][hi_], sh, int(sh.max() + 1), 0) for k in ("hA", "hB")])
    Za = Z - np.column_stack([np.bincount(sid, Z[:, j], S) / L["cS"] for j in range(3)])[sid]
    Rw = fe_apply(L["full"], Z)
    Rr = fe_apply(L["refP"], ZR)
    Rh = s78.fe_res_np(ZH, s78.fac(pid[hi_]), sh)
    rel = {1: 1.0 - float(s2z @ (1.0 - L["full"]["h"])) / float(Rw[:, 1] @ Rw[:, 1]),
           0: corr(Rr[:, 0], Rr[:, 1]), 2: s78.sb(corr(Rh[:, 0], Rh[:, 1]))}
    out = {}
    for k_, nm in ((0, "ref"), (1, "pay"), (2, "int")):
        out[f"b|rel_{nm}"] = rel[k_]
        out[f"b|q_{nm}"] = float(Rw[:, k_] @ Rw[:, k_]) / float(Za[:, k_] @ Za[:, k_])
    for pair, (i, k) in s78.PAIRS3.items():
        out[f"b|a|{pair}"] = corr(Za[:, i], Za[:, k])
        out[f"b|w|{pair}"] = corr(Rw[:, i], Rw[:, k])
        out[f"b|wd|{pair}"] = s78.disatt(out[f"b|w|{pair}"], rel[i], rel[k])
        if cf:                                     # T2 (a): between-subject variance of the subject-level coupling
            num = np.bincount(sid, Za[:, i] * Za[:, k], S)
            den = np.sqrt(np.bincount(sid, Za[:, i] ** 2, S) * np.bincount(sid, Za[:, k] ** 2, S))
            out[f"cfv|{pair}"] = float(np.var(num / den, ddof=1))
    xi_ = np.asarray(X["int"], float)
    mI = np.bincount(sid, xi_, S) / L["cS"]
    out["int_mean"] = mI
    out["int_sd"] = np.sqrt(np.bincount(sid, (xi_ - mI[sid]) ** 2, S) / L["cS"])
    out["nmiss"] = X.get("nmiss", 0)
    if err:                                        # T2 (b): realised error correlations
        Zt = np.column_stack([gblom(X["T"][:, j], sid, S, 0) for j in range(3)])
        E = Rw - fe_apply(L["full"], Zt)
        out["err_within_corr"] = corr(E[:, 1], E[:, 2])
        out["err_cohort_corr"] = X.get("err_cohort_corr", np.nan)
    return out


def uk_real_X(D: dict) -> dict:
    d = D["d"]
    return dict(ref21=d.ref.to_numpy(float), ref14=d.ref14_gpa.to_numpy(float), pay=d.pay.to_numpy(float),
                int=d.int1.to_numpy(float), hA=D["hA"], hB=D["hB"], nmiss=0)


def uk_targets(ev: dict, X: dict, L: dict) -> tuple[dict, dict]:
    """Calibration targets and starting values from one data set, as scripts/78 run_g3_sim takes them from the real
    data."""
    a = np.array([ev[f"b|a|{p_}"] for p_ in PAIRS])
    w = np.array([ev[f"b|w|{p_}"] for p_ in PAIRS])
    q = np.array([ev["b|q_ref"], ev["b|q_pay"], ev["b|q_int"]])
    obs = dict(a=a, w=w, q=q, rel_ref=ev["b|rel_ref"], rel_int=ev["b|rel_int"], m=ev["int_mean"], s=ev["int_sd"])
    lg = pd.Series(s78._logit(np.asarray(X["int"], float))).groupby(L["sid"])
    par = dict(pi=np.clip(1 - q, 0.05, 0.95), sig_ref=float(np.sqrt(q[0] * (1 / obs["rel_ref"] - 1))),
               rho_b=np.clip(a / 0.9, -0.9, 0.9), rho_w=np.clip(a / 0.9, -0.9, 0.9),
               mu=lg.median().to_numpy(), kappa=lg.std(ddof=0).to_numpy(), tau=0.5)
    return obs, par


def _mean(res, key):
    return np.mean([r[key] for r in res], axis=0)


def uk_update(par: dict, res: list, obs: dict, free_w: bool, fix_tau: bool = False) -> dict:
    """scripts/78 run_g3_sim's nested update(), re-stated: damped multiplicative (additive for mu) moment matching."""
    q = np.array([_mean(res, f"b|q_{k}") for k in ("ref", "pay", "int")])
    par = dict(par)
    dm_ = DAMP
    par["pi"] = np.clip(1 - (1 - par["pi"]) * (obs["q"] / q) ** dm_, 0.02, 0.98)
    rr = _mean(res, "b|rel_ref")
    par["sig_ref"] = float(par["sig_ref"] * ((1 / obs["rel_ref"] - 1) / (1 / rr - 1)) ** (0.5 * dm_))
    ri = _mean(res, "b|rel_int")
    if not fix_tau:
        par["tau"] = float(max(0.02, par["tau"] * ((1 / obs["rel_int"] - 1) / (1 / ri - 1)) ** dm_))
    a_ = np.array([_mean(res, f"b|a|{p_}") for p_ in PAIRS])
    par["mu"] = par["mu"] + dm_ * (s78._logit(obs["m"]) - s78._logit(_mean(res, "int_mean")))
    par["kappa"] = par["kappa"] * (obs["s"] / _mean(res, "int_sd")) ** dm_
    if free_w:
        w_ = np.array([_mean(res, f"b|w|{p_}") for p_ in PAIRS])
        par["rho_b"] = np.clip(par["rho_b"] * (obs["a"] / a_) ** dm_, -0.95, 0.95)
        par["rho_w"] = np.clip(par["rho_w"] * (obs["w"] / w_) ** dm_, -0.95, 0.95)
    else:
        par["rho_b"] = par["rho_w"] = np.clip(par["rho_b"] * (obs["a"] / a_) ** dm_, -0.95, 0.95)
    return par


def uk_inner_layout(L: dict, X: dict) -> dict:
    """The data-dependent inputs of scripts/78 sim_inputs re-derived from one simulated data set: each subject's pay
    signal SD (published noise), the known-band graduates per cohort and the subjects' band shares from the
    published band counts ('low' counted as 1.5)."""
    sid, S = L["sid"], L["S"]
    Lin = dict(L)
    Lin["sig_pay"] = np.sqrt(np.maximum(gvar(np.asarray(X["pay"], float), sid, S, 0)[sid] - L["ms2"], 1e-8))
    q1, q2, ql = X["pub"]
    Lin["NT"] = np.round(q1 + q2 + ql.sum(axis=2)).astype(np.int64)
    A1, A2 = np.bincount(sid, q1.sum(axis=1), S), np.bincount(sid, q2.sum(axis=1), S)
    LB = np.column_stack([np.bincount(sid, ql[:, :, b].sum(axis=1), S) for b in range(ql.shape[2])])
    Lin["pa1"] = (A1 / (A1 + A2))[sid]
    Lin["LOWP"] = (LB / LB.sum(axis=1, keepdims=True))[sid]
    return Lin


# ---------------- US ----------------
def us_layout(D: dict, rel_tag: str = "LB") -> dict:
    """Real US layout: scripts/78 us_sim_inputs plus the FE-only projection for c = 1, precomputed."""
    inp = s78.us_sim_inputs(D, rel_tag)
    G = inp["G"]
    XtX = np.tensordot(np.ones(G), inp["A"], axes=1)
    keep = np.diag(XtX) > 1e-10
    Q = np.linalg.pinv(XtX[np.ix_(keep, keep)], hermitian=True)
    Xk = inp["X"][:, keep]
    fc, K = inp["fc"], inp["K"]
    ly = np.log(D["d"].earnings.to_numpy(float))
    L = {k: v for k, v in inp.items() if k not in ("A", "idx", "X")}
    L.update(Xk=Xk, Q=Q, Mii=1.0 - inp["inv_n"] - ((Xk @ Q) * Xk).sum(axis=1), cK=np.bincount(fc, minlength=K).astype(float),
             var_f=gvar(ly, fc, K, 1)[fc], ms2f=pd.Series(inp["s2"]).groupby(fc).transform("mean").to_numpy())
    return L


def us_gen(L: dict, ss, par: dict, opt: dict | None = None):
    """scripts/78 us_sim_task's data generation (same random-number calls). opt: cF / cY (true error / noise
    variance x c; T1), load_s (T2 (a)). Returns the within-field Blom scores, the analyst's s2z (published noise)
    and log pay."""
    opt = opt or {}
    rng = np.random.default_rng(ss)
    n, G, g, fc, K = L["n"], L["G"], L["g"], L["fc"], L["K"]
    pi = np.asarray(par["pi"])
    Cb = np.array([[1.0, par["rho_b"]], [par["rho_b"], 1.0]])
    Cw = np.array([[1.0, par["rho_w"]], [par["rho_w"], 1.0]])
    u = rng.multivariate_normal(np.zeros(2), Cb, size=G) * np.sqrt(pi)
    v = rng.multivariate_normal(np.zeros(2), Cw, size=n) * np.sqrt(1 - pi)
    s_ = float(opt.get("load_s", 0.0))
    if s_ > 0:
        m = loadings(_xstream(ss).standard_normal((K, 2)), s_, opt.get("load_fam", "L"), 1)
        T = m[fc] * u[g] + v
    else:
        T = u[g] + v
    cF, cY = float(opt.get("cF", 1.0)), float(opt.get("cY", 1.0))
    e1 = L["e1"] if cF == 1.0 else np.minimum(L["e1"] * cF, 0.999)
    Fo = np.sqrt(1 - e1) * T[:, 0] + np.sqrt(e1) * rng.standard_normal(n)
    if cY == 1.0:
        s2, sig = L["s2"], L["sig"]
    else:
        s2, sig = L["s2"] * cY, np.sqrt(np.maximum(L["var_f"] - cY * L["ms2f"], 1e-8))
    y = sig * T[:, 1] + np.sqrt(s2) * rng.standard_normal(n)
    zF, zY = gblom(Fo, fc, K, 1), gblom(y, fc, K, 1)
    return zF, zY, L["s2"] / gvar(y, fc, K, 1)[fc], y


def us_eval(L: dict, zF, zY, s2z, cf: bool = False) -> dict:
    """scripts/78 us_sim_fixed + us_sim_eval with c = 1 (no resampling), the statistics the test uses."""
    g, G, fc, K = L["g"], L["G"], L["fc"], L["K"]
    cnt = L["cnt"]
    a_ = zF - (np.bincount(fc, zF, K) / L["cK"])[fc]
    b_ = zY - (np.bincount(fc, zY, K) / L["cK"])[fc]
    aa, bb = float(a_ @ a_), float(b_ @ b_)
    out = {"a": float(a_ @ b_ / np.sqrt(aa * bb))}
    zFd = zF - (np.bincount(g, zF, G) / cnt)[g]
    zYd = zY - (np.bincount(g, zY, G) / cnt)[g]
    vF, vY = L["Xk"].T @ zFd, L["Xk"].T @ zYd
    rFF = float(zFd @ zFd - vF @ L["Q"] @ vF)
    rYY = float(zYd @ zYd - vY @ L["Q"] @ vY)
    rFY = float(zFd @ zYd - vF @ L["Q"] @ vY)
    out["w"] = rFY / np.sqrt(rFF * rYY)
    out["lam58"] = float(1.0 - (L["e1"] * (1 - L["inv_n"])).sum() / rFF)
    out["lamfull"] = float(1.0 - (L["e1"] * L["Mii"]).sum() / rFF)
    out["relY_w"] = float(1.0 - (s2z * L["Mii"]).sum() / rYY)
    out["qF"], out["qY"] = rFF / aa, rYY / bb
    if cf:
        num = np.bincount(fc, a_ * b_, K)
        den = np.sqrt(np.bincount(fc, a_ ** 2, K) * np.bincount(fc, b_ ** 2, K))
        out["cfv"] = float(np.var(num / den, ddof=1))
    return out


def us_update(par: dict, res: list, obs: dict, free_w: bool) -> dict:
    """scripts/78 run_us_sim's nested update(), re-stated."""
    par = dict(par)
    q = np.array([_mean(res, "qF"), _mean(res, "qY")])
    par["pi"] = np.clip(1 - (1 - par["pi"]) * (obs["q"] / q) ** DAMP, 0.02, 0.98)
    rb = float(np.clip(par["rho_b"] * (obs["a"] / _mean(res, "a")) ** DAMP, -0.95, 0.95))
    if free_w:
        par["rho_w"] = float(np.clip(par["rho_w"] * (obs["w"] / _mean(res, "w")) ** DAMP, -0.95, 0.95))
        par["rho_b"] = rb
    else:
        par["rho_b"] = par["rho_w"] = rb
    return par


def us_start(obs: dict) -> dict:
    return dict(pi=np.clip(1 - obs["q"], 0.05, 0.95), rho_b=float(min(0.95, obs["a"] / 0.8)),
                rho_w=float(min(0.95, obs["a"] / 0.8)))


def us_obs(ev: dict) -> dict:
    return dict(a=ev["a"], w=ev["w"], q=np.array([ev["qF"], ev["qY"]]))


# =============================================================================================================
# worker tasks (fork: workers inherit LAY and scripts/78's _SIM / _USSIM, set before the pool is created)
# =============================================================================================================
LAY: dict = {}
EX: ProcessPoolExecutor | None = None


def run_pool(fn, tasks: list, chunksize: int = 4) -> list:
    if EX is None:
        return [fn(t) for t in tasks]
    return list(EX.map(fn, tasks, chunksize=chunksize))


def t_s78uk(t):
    return s78.sim_task(t)


def t_s78us(t):
    return s78.us_sim_task(t)


class SimFail(Exception):
    pass


def t_uk(t):
    key, ss, par, opt, fl = t
    L = LAY[key]
    try:
        return uk_eval(L, uk_gen(L, ss, par, opt), cf=fl.get("cf", False), err=fl.get("err", False))
    except Exception as e_:
        return {"fail": f"{type(e_).__name__}: {e_}"[:120]}


def t_us(t):
    key, ss, par, opt, fl = t
    L = LAY[key]
    try:
        zF, zY, s2z, _ = us_gen(L, ss, par, opt)
        return us_eval(L, zF, zY, s2z, cf=fl.get("cf", False))
    except Exception as e_:
        return {"fail": f"{type(e_).__name__}: {e_}"[:120]}


def run_sims(fn, tasks: list) -> list:
    """run_pool for simulation tasks; raises SimFail if any data set failed."""
    res = run_pool(fn, tasks)
    bad = [r["fail"] for r in res if "fail" in r]
    if bad:
        raise SimFail(f"{len(bad)} of {len(res)} data sets failed: {bad[0]}")
    return res


def t1_uk(t):
    """One T1 data set (UK): generate on the real layout, then the full calibrated test re-estimated on it (C2)."""
    key, so, par_gen, opt_gen = t
    L = LAY[key]
    try:
        X = uk_gen(L, sk(so, 0), par_gen, opt_gen)
        ev = uk_eval(L, X)
        obs, par = uk_targets(ev, X, L)
        Lin = uk_inner_layout(L, X)
        kc, kn = sk(so, 1), sk(so, 2)
        for r in range(CAL_R):
            rs = sk(kc, r)
            res = [uk_eval(Lin, uk_gen(Lin, sk(rs, j), par)) for j in range(CAL_M)]
            par = uk_update(par, res, obs, False)
        nul = np.array([[e[f"b|w|{p_}"] for p_ in PAIRS]
                        for e in (uk_eval(Lin, uk_gen(Lin, sk(kn, b), par)) for b in range(B_IN))])
        k_ = (nul <= obs["w"][None, :]).sum(axis=0)
        return dict(ok=True, p=(1 + k_) / (1 + B_IN), w=obs["w"], a=obs["a"], rho=np.asarray(par["rho_b"]),
                    rel_ref=obs["rel_ref"], rel_int=obs["rel_int"], rel_pay=ev["b|rel_pay"], err="")
    except Exception as e_:                                    # counted (C2)
        return dict(ok=False, err=f"{type(e_).__name__}: {e_}"[:120])


def t1_us(t):
    """One T1 data set (US, FE-only contrast)."""
    key, so, par_gen, opt_gen = t
    L = LAY[key]
    try:
        zF, zY, s2z, y = us_gen(L, sk(so, 0), par_gen, opt_gen)
        ev = us_eval(L, zF, zY, s2z)
        obs = us_obs(ev)
        par = us_start(obs)
        Lin = dict(L, sig=np.sqrt(np.maximum(gvar(y, L["fc"], L["K"], 1)[L["fc"]] - L["ms2f"], 1e-8)))
        kc, kn = sk(so, 1), sk(so, 2)
        for r in range(CAL_R):
            rs = sk(kc, r)
            res = [us_eval(Lin, *us_gen(Lin, sk(rs, j), par)[:3]) for j in range(CAL_M)]
            par = us_update(par, res, obs, False)
        nul = np.array([us_eval(Lin, *us_gen(Lin, sk(kn, b), par)[:3])["w"] for b in range(B_IN)])
        k_ = int((nul <= obs["w"]).sum())
        return dict(ok=True, p=np.array([(1 + k_) / (1 + B_IN)]), w=np.array([obs["w"]]), a=np.array([obs["a"]]),
                    rho=np.array([par["rho_b"]]), lam=ev["lamfull"], relY=ev["relY_w"], err="")
    except Exception as e_:
        return dict(ok=False, err=f"{type(e_).__name__}: {e_}"[:120])


UKB_KEYS = ["across|REF-pay", "within|REF-pay", "dis|REF-pay", "across|REF-intake|int1", "within|REF-intake|int1",
            "dis|REF-intake|int1", "across|pay-intake|int1", "within|pay-intake|int1", "dis|pay-intake|int1",
            "rel_ref", "rel_pay", "rel_int1"]


def t_ukboot(t):
    """Provider cluster bootstrap (scripts/78 run_g3_uk's resampling) of several UK data sets on identical cells:
    the same draws for each (paired)."""
    keys, seeds = t
    Ds = [LAY[k] for k in keys]
    pid = Ds[0]["pid"]
    G = int(pid.max() + 1)
    groups = [np.flatnonzero(pid == g) for g in range(G)]
    out = []
    for s_ in seeds:
        draw = np.random.default_rng(s_).integers(G, size=G)
        rows = np.concatenate([groups[g] for g in draw])
        newp = np.concatenate([np.full(len(groups[g]), k) for k, g in enumerate(draw)])
        out.append([[s78.uk_stats(D, rows, newp)[k] for k in UKB_KEYS] for D in Ds])
    return out


def t_usboot(t):
    """Institution cluster bootstrap (scripts/78 run_g3_us's resampling) of the across and FE-only within
    correlations."""
    key, seeds = t
    D, P = LAY[key]
    out = []
    for s_ in seeds:
        c = np.bincount(np.random.default_rng(s_).integers(0, D["G"], D["G"]), minlength=D["G"]).astype(float)
        st = s78.us_stats(D, P, c)
        out.append((st["across"], st["within|fe"]))
    return out


def boot_chunks(kid: str, n: int, size: int = 50) -> list:
    s_ = kids(KID[kid], n)
    return [s_[i:i + size] for i in range(0, n, size)]


# =============================================================================================================
# data (loaded in short-lived child processes: the parent stays small before the worker pool forks)
# =============================================================================================================
def _in_child(fn):
    with ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context("fork")) as ex:
        return ex.submit(fn).result()


def load_uk() -> dict:
    with threadpool_limits(limits=1, user_api="blas"):
        # scripts/78 uk_panel(), re-stated with memory trims between its steps (same calls, same result)
        sub, pu, inst = s76.load_ref()
        s78._trim()
        sub14, pu14 = s76.load_ref14()
        s78._trim()
        leo, prov = s76.load_leo_prov()
        s78._trim()
        P = s76.build_panel(leo, prov, pu, inst)
        del leo
        s78._trim()
        pa = s76.load_pa_raw(set(P.ukprn))
        P = s76.add_revision_cols(P, pu, pu14, pa)
        del pa
        s78._trim()
        A, Pa = s78.leo_cohort_rows(set(P.ukprn))
        UD = s78.uk_g3_data(P, A, Pa)
        ch = UD["chk"]
        assert ch["n6"] == 864 and np.allclose(ch["wtriad"], [0.109, 0.146, 0.261], atol=5e-4)
        assert abs(ch["rel76"] - 0.536) < 5e-4 and ch["rel76_n"] == 814
        P14 = P.assign(ref_gpa=P.ref14_gpa, ref14_gpa=P.ref_gpa)          # REF 2014 in place of REF 2021 (C9)
        out = {"uk": UD,
               "uk14": s78.uk_g3_data(P14, A, Pa, filt=lambda d: pd.Series(True, index=d.index)),
               "uk21c": s78.uk_g3_data(P, A, Pa, filt=lambda d: d.ref14_gpa.notna()),
               "uk14c": s78.uk_g3_data(P14, A, Pa, filt=lambda d: d.ref14_gpa.notna())}
        a_, b_ = out["uk21c"]["d"], out["uk14c"]["d"]
        assert a_[["ukprn", "subject"]].equals(b_[["ukprn", "subject"]]), "common samples differ"
        assert np.allclose(a_.ref_gpa, b_.ref14_gpa) and np.allclose(a_.ref14_gpa, b_.ref_gpa)
        res = {}
        for k, D in out.items():
            key = pd.MultiIndex.from_frame(D["d"][["ukprn", "subject"]])
            D["hA"] = s78.intake_from_counts(Pa, [2013, 2015], 1).reindex(key).to_numpy()
            D["hB"] = s78.intake_from_counts(Pa, [2014, 2016], 1).reindex(key).to_numpy()
            inp = s78.sim_inputs(D, Pa)
            pt = s78.uk_stats(D, np.arange(len(D["d"])), D["pid"])
            D.pop("pay_rows", None)
            D["d"] = D["d"][["ukprn", "subject", "ref", "ref_gpa", "ref14_gpa", "pay", "int1", "top_l1"]].copy()
            res[k] = dict(D=D, inp=inp, pt=pt, n=len(D["d"]), G=int(D["pid"].max() + 1),
                          S=int(D["sid"].max() + 1), n_ref=int(len(D["ref_idx"])),
                          G_ref=int(D["d"].ukprn.iloc[D["ref_idx"]].nunique()))
        return res


def load_us() -> dict:
    with threadpool_limits(limits=1, user_api="blas"):
        cells, ar, er_cs, inst = s78.us_cells()
        del ar, er_cs, inst
        noise = s78.us_noise()
        Rl = pd.read_csv(s58.REL_CSV)
        Rl = Rl[Rl.unit == "field"].set_index("field")
        rel = {"LB": Rl["relF_LB"].to_dict(), "EXT": Rl["relF_EXT"].to_dict()}
        res = {}
        for k, sl in (("us_main", s78.MAIN_SLOPES), ("us_fe", [])):
            M0 = s58.fe_build(cells, list(sl), [], "earnings", per_field=False)
            D = s78.us_g3_data(M0, rel, noise)
            assert D["n_noise"] == len(D["d"])
            pt = s78.us_stats(D, s78.us_prep(D), np.ones(D["G"])) if k == "us_main" else None
            fl = sorted(D["d"].field.unique())
            nimp = int(sum(1 for f in fl if not np.isfinite(rel["LB"].get(f, np.nan))))
            D["X"] = {"main": D["X"]["fe"], "fe": D["X"]["fe"]}        # lean copy (only the FE-only contrast is used)
            D["d"] = D["d"][["field", "inst_key", "earnings", "prestige_score"]].copy()
            res[k] = dict(D=D, pt=pt, n=len(D["d"]), G=int(D["G"]), K=len(fl), n_imputed=nimp)
            del M0
        return res


# =============================================================================================================
# calibrated tests on real data (tasks in the pool)
# =============================================================================================================
def null_summary(null_w: np.ndarray, obs_w: float) -> dict:
    v = np.asarray(null_w, float)
    k_ = int((v <= obs_w).sum())
    return dict(obs=float(obs_w), p=(1 + k_) / (1 + len(v)), k=k_, n=len(v), mean=float(v.mean()),
                lo=float(np.percentile(v, 2.5)), hi=float(np.percentile(v, 97.5)), min=float(v.min()),
                q05=float(np.percentile(v, 5.0)), sd=float(np.std(v, ddof=1)))        # q05, sd: revision 1


def uk_match(key: str, obs: dict, par: dict, kid, opt: dict | None = None) -> dict:
    """scripts/78's UK null schedule (CAL_R rounds x CAL_M data sets, damped matching) at fixed model options."""
    opt = dict(opt or {})
    for r in range(CAL_R):
        rs = sk(kid, r)
        par = uk_update(par, run_sims(t_uk, [(key, sk(rs, j), par, opt, {}) for j in range(CAL_M)]), obs, False)
    return par


def us_match(key: str, obs: dict, par: dict, kid, opt: dict | None = None) -> dict:
    opt = dict(opt or {})
    for r in range(CAL_R):
        rs = sk(kid, r)
        par = us_update(par, run_sims(t_us, [(key, sk(rs, j), par, opt, {}) for j in range(CAL_M)]), obs, False)
    return par


def uk_null(key: str, obs: dict, par: dict, null_kid: str, opt: dict | None = None, err: bool = False,
            cf: bool = False, ss=None) -> dict:
    ss = KID[null_kid] if ss is None else ss
    nul = run_sims(t_uk, [(key, s, par, dict(opt or {}), {"cf": cf, "err": err}) for s in kids(ss, NULL_N)])
    out = dict(par=par, opt=dict(opt or {}),
               pairs={p_: null_summary([e[f"b|w|{p_}"] for e in nul], obs["w"][i]) for i, p_ in enumerate(PAIRS)},
               a_null={p_: float(np.mean([e[f"b|a|{p_}"] for e in nul])) for p_ in PAIRS},
               rel_ref=float(_mean(nul, "b|rel_ref")), rel_int=float(_mean(nul, "b|rel_int")),
               rel_pay=float(_mean(nul, "b|rel_pay")),
               q=np.array([_mean(nul, f"b|q_{k}") for k in ("ref", "pay", "int")]))
    if cf:
        out["sd_sim"] = {p_: float(np.sqrt(np.mean([e[f"cfv|{p_}"] for e in nul]))) for p_ in PAIRS}
    if err:
        out["err_within"] = float(np.nanmean([e["err_within_corr"] for e in nul]))
        out["err_cohort"] = float(np.nanmean([e["err_cohort_corr"] for e in nul]))
    return out


def us_null(key: str, obs: dict, par: dict, null_kid: str, opt: dict | None = None, cf: bool = False,
            ss=None) -> dict:
    ss = KID[null_kid] if ss is None else ss
    nul = run_sims(t_us, [(key, s, par, dict(opt or {}), {"cf": cf}) for s in kids(ss, NULL_N)])
    out = dict(par=par, opt=dict(opt or {}), pair=null_summary([e["w"] for e in nul], obs["w"]),
               a_null=float(_mean(nul, "a")), q=np.array([_mean(nul, "qF"), _mean(nul, "qY")]),
               lam=float(_mean(nul, "lamfull")), relY=float(_mean(nul, "relY_w")))
    if cf:
        out["sd_sim"] = float(np.sqrt(_mean(nul, "cfv")))
    return out


def uk_test(key: str, obs: dict, par: dict, cal_kid: str, null_kid: str, opt: dict | None = None,
            err: bool = False) -> dict:
    """The calibrated test of scripts/78 on one real UK layout: null schedule, then NULL_N null draws. A failed
    simulation is recorded, not fatal."""
    try:
        par = uk_match(key, obs, par, KID[cal_kid], opt)
        return dict(ok=True, **uk_null(key, obs, par, null_kid, opt, err=err))
    except (SimFail, FloatingPointError, ValueError) as e_:
        return dict(ok=False, err=str(e_)[:160])


def us_test(key: str, obs: dict, par: dict, cal_kid: str, null_kid: str) -> dict:
    try:
        par = us_match(key, obs, par, KID[cal_kid])
        return dict(ok=True, **us_null(key, obs, par, null_kid))
    except (SimFail, FloatingPointError, ValueError) as e_:
        return dict(ok=False, err=str(e_)[:160])


def a_grid(cty: str, key: str, obs: dict, par0: dict, sd_obs: dict) -> dict:
    """Amendment A1: the loading grid. At each (family, s) the other nuisance parameters are re-matched (scripts/78's
    null schedule from its starting values), then CAL_M check data sets give the coupling SD per pair, the across
    correlations and the within-university variance shares."""
    kid = KID[f"t2_{cty}_a_grid"]
    pairs = PAIRS if cty == "uk" else ["F-pay"]
    rule = "REF-pay" if cty == "uk" else "F-pay"
    a_obs = {p_: float(obs["a"][i]) for i, p_ in enumerate(PAIRS)} if cty == "uk" else {"F-pay": float(obs["a"])}
    rows = []
    for fi, fam in enumerate(FAMS):
        for gi, s_ in enumerate(GRID_S):
            kk = sk(sk(kid, fi), gi)
            opt = {"load_s": s_, "load_fam": fam}
            row = dict(fam=fam, s=s_, ok=False, opt=opt)
            try:
                if cty == "uk":
                    par = uk_match(key, obs, dict(par0), kk, opt)
                    chk = run_sims(t_uk, [(key, x, par, opt, {"cf": True}) for x in kids(sk(kk, CAL_R), CAL_M)])
                    sd = {p_: float(np.sqrt(np.mean([e[f"cfv|{p_}"] for e in chk]))) for p_ in PAIRS}
                    a_ = {p_: float(np.mean([e[f"b|a|{p_}"] for e in chk])) for p_ in PAIRS}
                    q = np.array([_mean(chk, f"b|q_{k}") for k in ("ref", "pay", "int")])
                else:
                    par = us_match(key, obs, dict(par0), kk, opt)
                    chk = run_sims(t_us, [(key, x, par, opt, {"cf": True}) for x in kids(sk(kk, CAL_R), CAL_M)])
                    sd = {"F-pay": float(np.sqrt(_mean(chk, "cfv")))}
                    a_ = {"F-pay": float(_mean(chk, "a"))}
                    q = np.array([_mean(chk, "qF"), _mean(chk, "qY")])
                pi = np.asarray(par["pi"], float)
                row.update(ok=True, par=par, sd=sd, a=a_, q=q, pi=pi,
                           m_sd=sd[rule] >= sd_obs[rule],
                           m_a=all(abs(a_[p_] - a_obs[p_]) <= 0.01 for p_ in pairs),
                           m_q=bool(np.all(np.abs(q - obs["q"]) <= 0.01) and np.all(pi < 0.98)))
            except (SimFail, FloatingPointError, ValueError) as e_:
                row.update(err=str(e_)[:160], m_sd=False, m_a=False, m_q=False)
            rows.append(row)
            if row["ok"]:
                print(f"   A1 grid {cty} {fam} s={s_:.2f}: SD {row['sd'][rule]:.3f} (obs {sd_obs[rule]:.3f}) "
                      f"match SD/across/shares {row['m_sd']}/{row['m_a']}/{row['m_q']}", flush=True)
            else:
                print(f"   A1 grid {cty} {fam} s={s_:.2f}: fit failed", flush=True)
    sel = None
    for fam in FAMS:
        c = [r for r in rows if r["fam"] == fam and r["m_sd"] and r["m_a"] and r["m_q"]]
        if c:
            sel = dict(case=1, pick=min(c, key=lambda r: r["s"]), alt=None)
            break
    if sel is None:
        for fam in FAMS:
            c = [r for r in rows if r["fam"] == fam and r["m_sd"] and r["m_a"]]
            if c:
                alt = [r for r in rows if r["fam"] == fam and r["m_a"] and r["m_q"]]
                sel = dict(case=2, pick=min(c, key=lambda r: r["s"]),
                           alt=max(alt, key=lambda r: r["s"]) if alt else None)
                break
    if sel is None:
        c = [r for r in rows if r["m_a"]]
        alt = [r for r in rows if r["fam"] == "L" and r["m_a"] and r["m_q"]]
        sel = dict(case=3, pick=max(c, key=lambda r: r["sd"][rule]) if c else None,
                   alt=max(alt, key=lambda r: r["s"]) if alt else None)
    return dict(rows=rows, sel=sel, rule=rule)


# =============================================================================================================
# C0: scripts/78's calibration, reproduced with its own functions and seeds
# =============================================================================================================
def repro_uk(R: dict) -> dict:
    D, pt = R["D"], R["pt"]
    d = D["d"]
    a_obs = np.array([pt["across|REF-pay"], pt["across|REF-intake|int1"], pt["across|pay-intake|int1"]])
    w_obs = np.array([pt["within|REF-pay"], pt["within|REF-intake|int1"], pt["within|pay-intake|int1"]])
    q_obs = np.asarray(D["q_obs"], float)
    g_ = d.groupby("subject").top_l1
    obs = dict(a=a_obs, w=w_obs, q=q_obs, rel_ref=pt["rel_ref"], rel_int=pt["rel_int1"],
               m=g_.mean().to_numpy(), s=g_.std(ddof=0).to_numpy())
    lg = pd.Series(s78._logit(d.top_l1.to_numpy())).groupby(D["sid"])
    par = dict(pi=np.clip(1 - q_obs, 0.05, 0.95), sig_ref=float(np.sqrt(q_obs[0] * (1 / obs["rel_ref"] - 1))),
               rho_b=np.clip(a_obs / 0.9, -0.9, 0.9), rho_w=np.clip(a_obs / 0.9, -0.9, 0.9),
               mu=lg.median().to_numpy(), kappa=lg.std(ddof=0).to_numpy(), tau=0.5)
    for r in range(CAL_R):
        rs = sk(k78("g3_sim_cal"), r)
        par = uk_update(par, run_pool(t_s78uk, [(sk(rs, j), par, "cal") for j in range(CAL_M)]), obs, False)
    nres = run_pool(t_s78uk, [(s, par, "null") for s in kids(k78("g3_sim_null"), s78.SIM_NULL)])
    out = dict(obs=obs, null=par, nsum={p_: null_summary([e[f"b|w|{p_}"] for e in nres], w_obs[i])
                                         for i, p_ in enumerate(PAIRS)})
    alt = dict(par)
    w0 = np.array([_mean(nres, f"b|w|{p_}") for p_ in PAIRS])
    alt["rho_w"] = np.clip(alt["rho_w"] * w_obs / w0, -0.95, 0.95)
    for r in range(CAL_R):
        rs = sk(k78("g3_sim_alt"), r)
        alt = uk_update(alt, run_pool(t_s78uk, [(sk(rs, j), alt, "cal") for j in range(CAL_M)]), obs, True)
    out["alt"] = alt
    return out


def repro_us(R: dict) -> dict:
    D, pt = R["D"], R["pt"]
    ob = s78.us_sim_eval(s78.us_sim_fixed(D["zF"], D["zY"], D["s2z"]), np.ones(D["G"]))
    obs = dict(a=pt["across"], w=pt["within|fe"], q=np.array([ob["qF"], ob["qY"]]))
    par = dict(pi=np.clip(1 - obs["q"], 0.05, 0.95), rho_b=float(min(0.95, obs["a"] / 0.8)),
               rho_w=float(min(0.95, obs["a"] / 0.8)))
    for r in range(CAL_R):
        rs = sk(k78("us_sim_cal"), r)
        par = us_update(par, run_pool(t_s78us, [(sk(rs, j), par, "cal") for j in range(CAL_M)]), obs, False)
    nres = run_pool(t_s78us, [(s, par, "null") for s in kids(k78("us_sim_null"), s78.SIM_NULL)])
    out = dict(obs=obs, null=par, nsum=null_summary([e["w"] for e in nres], obs["w"]),
               a_null=float(_mean(nres, "a")))
    alt = dict(par)
    alt["rho_w"] = float(np.clip(alt["rho_w"] * obs["w"] / _mean(nres, "w"), -0.95, 0.95))
    for r in range(CAL_R):
        rs = sk(k78("us_sim_alt"), r)
        alt = us_update(alt, run_pool(t_s78us, [(sk(rs, j), alt, "cal") for j in range(CAL_M)]), obs, True)
    out["alt"] = alt
    return out


def fast_check(UKR: dict, USR: dict) -> dict:
    """C1: the lean evaluators against scripts/78's sim_task / us_sim_task on FASTCHK_N seeds."""
    Lk, Lu = LAY["uk"], LAY["us_main"]
    X = uk_real_X(UKR["uk"]["D"])
    obs, par = uk_targets(uk_eval(Lk, X), X, Lk)
    par["rho_b"] = par["rho_w"] = np.array([0.7, 0.8, 0.8])
    upar = dict(pi=np.array([0.8, 0.7]), rho_b=0.55, rho_w=0.55)
    mx_uk = mx_us = 0.0
    for s in kids(KID["fastcheck"], FASTCHK_N):
        a = s78.sim_task((s, par, "cal"))
        b = uk_eval(Lk, uk_gen(Lk, s, par))
        for k_, v in b.items():
            if k_ in a:
                mx_uk = max(mx_uk, float(np.max(np.abs(np.asarray(a[k_], float) - np.asarray(v, float)))))
        a = s78.us_sim_task((s, upar, "cal"))
        zF, zY, s2z, _ = us_gen(Lu, s, upar)
        b = us_eval(Lu, zF, zY, s2z)
        for k_ in ("a", "w", "lam58", "lamfull", "relY_w", "qF", "qY"):
            mx_us = max(mx_us, abs(float(a[k_]) - float(b[k_])))
    assert mx_uk < 1e-9 and mx_us < 1e-9, (mx_uk, mx_us)
    return dict(uk=mx_uk, us=mx_us)


# =============================================================================================================
# T1-T4 drivers
# =============================================================================================================
def gap_row(sec: str, q: str) -> dict:
    c = pd.read_csv(GAP_CSV)
    m = c[(c.section == sec) & (c.quantity == q)]
    assert len(m) == 1, (sec, q)
    return m.iloc[0].to_dict()


def size_summary(res: list, power: bool) -> dict:
    npair = len(res[0]["p"]) if res[0]["ok"] else len([r for r in res if r["ok"]][0]["p"])
    ok = np.array([r["ok"] for r in res])
    rej = np.zeros((len(res), npair))
    for i, r in enumerate(res):
        rej[i] = (np.asarray(r["p"]) <= ALPHA) if r["ok"] else (0.0 if power else 1.0)
    M = len(res)
    s = rej.mean(axis=0)
    pfl = np.array([np.asarray(r["p"]) <= 1.0 / (1 + B_IN) + 1e-12 for r in res if r["ok"]], float)
    return dict(rate=s, se=np.sqrt(s * (1 - s) / M), M=M, fail=int((~ok).sum()), k=np.round(s * M).astype(int),
                floor=pfl.mean(axis=0),                                    # revision 1: share at the floor p
                errs=sorted({r["err"] for r in res if not r["ok"]}),
                w_mean=np.mean([r["w"] for r in res if r["ok"]], axis=0),
                rho_mean=np.mean([r["rho"] for r in res if r["ok"]], axis=0))


def run_t1(ctx: dict) -> dict:
    out = {}
    U, S = ctx["c0_uk"], ctx["c0_us"]
    iv = ctx["iv"]
    # perturbed generating settings (C3)
    for tag in ("low", "high"):
        j = 0 if tag == "low" else 1
        obs_t = dict(U["obs"], rel_ref=iv["uk_ref"][1 + j], rel_int=iv["uk_int"][1 + j])
        opt = {"pay_c": (1 - iv["uk_pay"][1 + j]) / (1 - iv["uk_pay"][0])}
        par = dict(U["null"])
        kid = KID[f"t1_uk_dgp_{tag}"]
        for r in range(CAL_R):
            par = uk_update(par, run_sims(t_uk, [("uk", sk(sk(kid, r), m_), par, opt, {}) for m_ in range(CAL_M)]),
                            obs_t, False)
        fit = run_sims(t_uk, [("uk", s, par, opt, {}) for s in kids(sk(kid, CAL_R), CAL_M)])
        out[f"uk_dgp_{tag}"] = dict(par=par, opt=opt, target=(obs_t["rel_ref"], obs_t["rel_int"]),
                                    rel_ref=float(_mean(fit, "b|rel_ref")), rel_int=float(_mean(fit, "b|rel_int")),
                                    rel_pay=float(_mean(fit, "b|rel_pay")),
                                    a=np.array([_mean(fit, f"b|a|{p_}") for p_ in PAIRS]))
        opt = {"cF": (1 - iv["us_lam"][1 + j]) / (1 - iv["us_lam"][0]),
               "cY": (1 - iv["us_pay"][1 + j]) / (1 - iv["us_pay"][0])}
        par = dict(S["null"])
        kid = KID[f"t1_us_dgp_{tag}"]
        for r in range(CAL_R):
            par = us_update(par, run_sims(t_us, [("us_main", sk(sk(kid, r), m_), par, opt, {})
                                                 for m_ in range(CAL_M)]), S["obs"], False)
        fit = run_sims(t_us, [("us_main", s, par, opt, {}) for s in kids(sk(kid, CAL_R), CAL_M)])
        out[f"us_dgp_{tag}"] = dict(par=par, opt=opt, a=float(_mean(fit, "a")), lam=float(_mean(fit, "lamfull")),
                                    relY=float(_mean(fit, "relY_w")),
                                    q=np.array([_mean(fit, "qF"), _mean(fit, "qY")]))
        stage(f"T1: {tag} generating settings calibrated (UK rho {np.round(out[f'uk_dgp_{tag}']['par']['rho_b'], 3)}, "
              f"US rho {out[f'us_dgp_{tag}']['par']['rho_b']:.3f})")
    settings = {"base": (U["null"], {}, S["null"], {}),
                "low": (out["uk_dgp_low"]["par"], out["uk_dgp_low"]["opt"], out["us_dgp_low"]["par"],
                        out["us_dgp_low"]["opt"]),
                "high": (out["uk_dgp_high"]["par"], out["uk_dgp_high"]["opt"], out["us_dgp_high"]["par"],
                         out["us_dgp_high"]["opt"]),
                "power": (U["alt"], {}, S["alt"], {})}
    for tag, (pu, ou, ps, os_) in settings.items():
        stage(f"T1 {tag}: {M_OUT} UK and {M_OUT} US data sets, each with its own calibrated test "
              f"({CAL_R} x {CAL_M} + {B_IN})")
        ruk = run_pool(t1_uk, [("uk", s, pu, ou) for s in kids(KID[f"t1_uk_{tag}"], M_OUT)], chunksize=1)
        rus = run_pool(t1_us, [("us_main", s, ps, os_) for s in kids(KID[f"t1_us_{tag}"], M_OUT)], chunksize=1)
        out[tag] = dict(uk=size_summary(ruk, tag == "power"), us=size_summary(rus, tag == "power"))
        stage(f"T1 {tag}: UK {np.round(out[tag]['uk']['rate'], 3)} (failures {out[tag]['uk']['fail']}), "
              f"US {np.round(out[tag]['us']['rate'], 3)} (failures {out[tag]['us']['fail']})")
    return out


def run_t2(ctx: dict) -> dict:
    out = {}
    Lk, Lu = LAY["uk"], LAY["us_main"]
    Xk = uk_real_X(ctx["UKR"]["uk"]["D"])
    evk = uk_eval(Lk, Xk, cf=True)
    obs_k, par_k = uk_targets(evk, Xk, Lk)
    Du = ctx["USR"]["us_main"]["D"]
    evu = us_eval(Lu, Du["zF"], Du["zY"], Du["s2z"], cf=True)
    obs_u = us_obs(evu)
    par_u = us_start(obs_u)
    out["obs_uk"], out["obs_us"] = obs_k, obs_u
    # (a) heterogeneous university loadings (C5, amendment A1)
    sd_k = {p_: float(np.sqrt(evk[f"cfv|{p_}"])) for p_ in PAIRS}
    sd_u = {"F-pay": float(np.sqrt(evu["cfv"]))}
    flk = run_sims(t_uk, [("uk", s, ctx["c0_uk"]["null"], {}, {"cf": True}) for s in kids(KID["t2_uk_a_floor"], FLOOR_N)])
    flu = run_sims(t_us, [("us_main", s, ctx["c0_us"]["null"], {}, {"cf": True}) for s in kids(KID["t2_us_a_floor"], FLOOR_N)])
    for cty, key, obs, par0, sd_obs, flo, nullf in (
            ("uk", "uk", obs_k, par_k, sd_k, {p_: float(np.sqrt(_mean(flk, f"cfv|{p_}"))) for p_ in PAIRS}, uk_null),
            ("us", "us_main", obs_u, par_u, sd_u, {"F-pay": float(np.sqrt(_mean(flu, "cfv")))}, us_null)):
        stage(f"T2 (a) {cty}: A1 loading grid ({len(FAMS)} families x {len(GRID_S)} values)")
        G_ = a_grid(cty, key, obs, par0, sd_obs)
        res = dict(sd_obs=sd_obs, floor=flo, grid=G_)
        for tag, r_, nk in (("pick", G_["sel"]["pick"], f"t2_{cty}_a_null"), ("alt", G_["sel"]["alt"], f"t2_{cty}_a_null2")):
            if r_ is None:
                continue
            try:
                kw = dict(cf=True)
                res[tag] = dict(ok=True, fam=r_["fam"], s=r_["s"], **nullf(key, obs, r_["par"], nk, r_["opt"], **kw))
            except (SimFail, FloatingPointError, ValueError) as e_:
                res[tag] = dict(ok=False, fam=r_["fam"], s=r_["s"], err=str(e_)[:160])
        # revision 1: a null for every grid point matching the spread (A1's across criterion shown beside it)
        allp = []
        for i_, r_ in enumerate(G_["rows"]):
            if not (r_["ok"] and r_["m_sd"]):
                continue
            pk = G_["sel"]["pick"]
            if pk is not None and r_["fam"] == pk["fam"] and r_["s"] == pk["s"] and res.get("pick", {}).get("ok"):
                allp.append(dict(fam=r_["fam"], s=r_["s"], row=r_, null=res["pick"], reused=True))
                continue
            try:
                nn = nullf(key, obs, r_["par"], None, r_["opt"], cf=True, ss=sk(KID[f"t2_{cty}_a_all"], i_))
                allp.append(dict(fam=r_["fam"], s=r_["s"], row=r_, null=nn, reused=False))
            except (SimFail, FloatingPointError, ValueError) as e_:
                allp.append(dict(fam=r_["fam"], s=r_["s"], row=r_, null=None, err=str(e_)[:120]))
        res["all"] = allp
        if cty == "us":                    # revision 1: denser US grid, family N, between s = 0.6 and 0.7
            dense = []
            for i_, s_ in enumerate(DENSE_S):
                opt = {"load_s": s_, "load_fam": "N"}
                kk = sk(KID["t2_us_a_dense"], i_)
                row = dict(fam="N", s=s_)
                try:
                    par = us_match(key, obs, dict(par0), kk, opt)
                    chk = run_sims(t_us, [(key, x, par, opt, {"cf": True}) for x in kids(sk(kk, CAL_R), CAL_M)])
                    row.update(ok=True, sd=float(np.sqrt(_mean(chk, "cfv"))), a=float(_mean(chk, "a")),
                               q=np.array([_mean(chk, "qF"), _mean(chk, "qY")]), pi=np.asarray(par["pi"], float),
                               null=us_null(key, obs, par, None, opt, cf=True, ss=sk(KID["t2_us_a_dense_null"], i_)))
                except (SimFail, FloatingPointError, ValueError) as e_:
                    row.update(ok=False, err=str(e_)[:120])
                dense.append(row)
            res["dense"] = dense
        out[f"{cty}_a"] = res
        stage(f"T2 (a) {cty}: case {G_['sel']['case']}")
    # (b) correlated pay-intake error, UK (C6)
    for re_ in RHO_E:
        out[f"uk_b{re_:+.1f}"] = uk_test("uk", obs_k, par_k, f"t2_uk_b{re_:+.1f}_cal", f"t2_uk_b{re_:+.1f}_null",
                                         opt={"rho_e": re_, "keep_err": True}, err=True)
        stage(f"T2 (b) rho_e = {re_:+.1f}: done")
    return out


def run_t3(ctx: dict) -> dict:
    out = {}
    for key in ("us_main", "us_fe"):
        D = ctx["USR"][key]["D"]
        L = LAY[key]
        ev = us_eval(L, D["zF"], D["zY"], D["s2z"])
        Dl, P = LAY[key + "_boot"]
        pt = s78.us_stats(Dl, P, np.ones(Dl["G"]))
        assert abs(pt["across"] - ev["a"]) < 1e-9 and abs(pt["within|fe"] - ev["w"]) < 1e-9
        bs = [x for ch in run_pool(t_usboot, [(key + "_boot", c) for c in boot_chunks(
            "t3_boot_main" if key == "us_main" else "t3_boot_fe", B_BOOT)], chunksize=1) for x in ch]
        bs = np.array(bs)
        out[key] = dict(a=s78.summ(ev["a"], bs[:, 0]), w=s78.summ(ev["w"], bs[:, 1]), ev=ev)
    D = ctx["USR"]["us_fe"]["D"]
    obs = us_obs(out["us_fe"]["ev"])
    out["test_fe"] = us_test("us_fe", obs, us_start(obs), "t3_cal", "t3_null")
    stage("T3: FE-only calibrated test done")
    return out


def run_t4(ctx: dict) -> dict:
    out = {}
    for key, (ck, nk) in (("uk14", ("t4_own_cal", "t4_own_null")), ("uk14c", ("t4_c14_cal", "t4_c14_null")),
                          ("uk21c", ("t4_c21_cal", "t4_c21_null"))):
        R = ctx["UKR"][key]
        L = LAY[key]
        X = uk_real_X(R["D"])
        ev = uk_eval(L, X)
        obs, par = uk_targets(ev, X, L)
        out[key] = dict(ev=ev, obs=obs, test=uk_test(key, obs, par, ck, nk))
        stage(f"T4 {key}: calibrated test done")
    own = np.array([x[0] for ch in run_pool(t_ukboot, [(("uk14D",), c) for c in boot_chunks("t4_boot_own", B_BOOT)],
                                                chunksize=1) for x in ch])
    com = np.array([x for ch in run_pool(t_ukboot, [(("uk14cD", "uk21cD"), c) for c in boot_chunks(
        "t4_boot_common", B_BOOT)], chunksize=1) for x in ch])
    out["boot_own"], out["boot_c14"], out["boot_c21"] = own, com[:, 0], com[:, 1]
    return out


# =============================================================================================================
# main
# =============================================================================================================
def mem_available_mb() -> float:
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable"):
            return int(line.split()[1]) / 1024.0
    return 0.0


def vmsize() -> str:
    return [x for x in open("/proc/self/status").read().splitlines() if x.startswith("VmSize")][0]


def intervals() -> dict:
    """The 95% intervals of the reliabilities (C3), from scripts/78's summary table."""
    iv = {}
    for k, sec, q in (("uk_ref", "G3 UK reliability", "REF: within-provider REF 2021-2014 test-retest (normal scores)"),
                      ("uk_pay", "G3 UK reliability", "pay: 1 - noise / residual variance (scripts/73-style median noise)"),
                      ("uk_int", "G3 UK reliability", "intake ('low' = 1): odd/even cohort split-half, Spearman-Brown"),
                      ("us_lam", "G3 US rev. 1", "residual-F reliability with full leverage, lambda_LB [fe]"),
                      ("us_pay", "G3 US", "pay reliability [fe]")):
        r = gap_row(sec, q)
        iv[k] = (float(r["est"]), float(r["lo"]), float(r["hi"]))
    return iv


def repro_checks(ctx: dict) -> list:
    """C0: reproduced values against gap_checks_summary.csv (asserted in a reported run)."""
    U, S = ctx["c0_uk"], ctx["c0_us"]
    rows = []
    for i, p_ in enumerate(PAIRS):
        rows.append((f"UK {p_}: null rho", float(U["null"]["rho_b"][i]),
                     float(gap_row("G3 UK sim", f"{p_}: calibrated null rho (= rho_between = rho_within)")["est"])))
        g = gap_row("G3 UK sim", f"{p_} (normal scores): null within correlation")
        ns = U["nsum"][p_]
        rows += [(f"UK {p_}: null within, mean", ns["mean"], float(g["est"])),
                 (f"UK {p_}: null within, 2.5%", ns["lo"], float(g["lo"])),
                 (f"UK {p_}: null within, 97.5%", ns["hi"], float(g["hi"])),
                 (f"UK {p_}: p", ns["p"], float(g["verdict"].split("= ")[1])),
                 (f"UK {p_}: calibrated rho_within", float(U["alt"]["rho_w"][i]),
                  float(gap_row("G3 UK sim", f"{p_}: calibrated rho_within")["est"])),
                 (f"UK {p_}: calibrated rho_between", float(U["alt"]["rho_b"][i]),
                  float(gap_row("G3 UK sim", f"{p_}: calibrated rho_between")["est"]))]
    g = gap_row("G3 US sim [LB]", "null within-institution correlation")
    rows += [("US F-pay: null rho", float(S["null"]["rho_b"]),
              float(gap_row("G3 US sim [LB]", "calibrated null rho (= rho_between = rho_within)")["est"])),
             ("US F-pay: null within, mean", S["nsum"]["mean"], float(g["est"])),
             ("US F-pay: null within, 2.5%", S["nsum"]["lo"], float(g["lo"])),
             ("US F-pay: null within, 97.5%", S["nsum"]["hi"], float(g["hi"])),
             ("US F-pay: p", S["nsum"]["p"], float(g["verdict"].split("= ")[1])),
             ("US F-pay: calibrated rho_within", float(S["alt"]["rho_w"]),
              float(gap_row("G3 US sim [LB]", "calibrated rho_within")["est"])),
             ("US F-pay: calibrated rho_between", float(S["alt"]["rho_b"]),
              float(gap_row("G3 US sim [LB]", "calibrated rho_between")["est"]))]
    return rows


def main():
    global EX
    assert _sha(_block("-----BEGIN PRESPEC-----", "-----END PRESPEC-----")) == PRESPEC_SHA256, "PRESPEC block changed"
    assert _sha(_block("-----BEGIN CHOICES-----", "-----END CHOICES-----")) == CHOICES_SHA256, "CHOICES block changed"
    assert _sha(_block("-----BEGIN AMENDMENT A1-----", "-----END AMENDMENT A1-----")) == A1_SHA256, "A1 changed"
    avail = mem_available_mb()
    workers = int(os.environ.get("GAP84_WORKERS", "4" if avail >= 5000 else "2"))
    assert 1 <= workers <= 4
    stage(f"available memory {avail:.0f} MB -> {workers} worker processes (fork)")
    ctx = {}
    cache = Path(DEVCACHE) / "load.pkl" if DEVCACHE else None
    if DEVCACHE and os.environ.get("GAP84_WRITEONLY"):          # development shortcut only: re-render the write-up
        with open(cache, "rb") as f:
            ctx["UKR"], ctx["USR"] = pickle.load(f)
        with open(Path(DEVCACHE) / "ctx.pkl", "rb") as f:
            ctx.update(pickle.load(f))
        write_all(ctx)
        return
    if cache is not None and cache.exists():
        with open(cache, "rb") as f:
            UKR, USR = pickle.load(f)
    else:
        stage("UK data: scripts/76 panel, LEO cohorts, G3 cells, REF 2014 samples (child process)")
        UKR = _in_child(load_uk)
        stage("US data: scripts/58 cells, main-spec and FE-only samples (child process)")
        USR = _in_child(load_us)
        if cache is not None:
            cache.parent.mkdir(parents=True, exist_ok=True)
            with open(cache, "wb") as f:
                pickle.dump((UKR, USR), f)
    ctx["UKR"], ctx["USR"] = UKR, USR
    with threadpool_limits(limits=1, user_api="blas"):
        for k in ("uk", "uk14", "uk14c", "uk21c"):
            LAY[k] = uk_layout(UKR[k]["D"], UKR[k]["inp"])
            LAY[k + "D"] = UKR[k]["D"]
            ev = uk_eval(LAY[k], uk_real_X(UKR[k]["D"]))
            pt = UKR[k]["pt"]
            for a_, b_ in (("b|a|REF-pay", "across|REF-pay"), ("b|a|REF-intake", "across|REF-intake|int1"),
                           ("b|a|pay-intake", "across|pay-intake|int1"), ("b|w|REF-pay", "within|REF-pay"),
                           ("b|w|REF-intake", "within|REF-intake|int1"), ("b|w|pay-intake", "within|pay-intake|int1"),
                           ("b|rel_ref", "rel_ref"), ("b|rel_pay", "rel_pay"), ("b|rel_int", "rel_int1")):
                assert abs(ev[a_] - pt[b_]) < 1e-9, (k, a_, ev[a_], pt[b_])
            assert np.allclose([ev["b|q_ref"], ev["b|q_pay"], ev["b|q_int"]], UKR[k]["D"]["q_obs"], atol=1e-9, rtol=0)
        for k in ("us_main", "us_fe"):
            LAY[k] = us_layout(USR[k]["D"], "LB")
            LAY[k + "_boot"] = (USR[k]["D"], s78.us_prep(USR[k]["D"]))
        pt = USR["us_main"]["pt"]
        Du = USR["us_main"]["D"]
        ev = us_eval(LAY["us_main"], Du["zF"], Du["zY"], Du["s2z"])
        assert abs(ev["a"] - pt["across"]) < 1e-9 and abs(ev["w"] - pt["within|fe"]) < 1e-9
        assert abs(ev["lamfull"] - pt["lamfull_LB|fe"]) < 1e-9 and abs(ev["relY_w"] - pt["rel_pay|fe"]) < 1e-9
        s78._sim_init(UKR["uk"]["inp"])
        s78._ussim_init(s78.us_sim_inputs(Du, "LB"))
        ctx["fast"] = fast_check(UKR, USR)
        stage(f"C1 lean evaluators: max |difference| UK {ctx['fast']['uk']:.2e}, US {ctx['fast']['us']:.2e}")
    ctx["iv"] = intervals()
    s78._trim()
    stage(f"parent before the pool: {vmsize()}")
    EX = ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork"))
    try:
        with threadpool_limits(limits=1, user_api="blas"):
            stage("C0: scripts/78 UK calibration, its seeds and functions")
            ctx["c0_uk"] = repro_uk(UKR["uk"])
            stage("C0: scripts/78 US calibration (LB, FE-only)")
            ctx["c0_us"] = repro_us(USR["us_main"])
            ctx["c0_rows"] = repro_checks(ctx)
            for nm, got, pub in ctx["c0_rows"]:
                ok = abs((round(got, 4) if nm.endswith(": p") else got) - pub) < 5e-7
                print(f"   C0 {nm}: {got:+.6f} (scripts/78 {pub:+.6f}){'' if ok else '  <-- differs'}")
                assert ok or DEVRUN, nm
            stage("T3: US FE-only sample")
            ctx["t3"] = run_t3(ctx)
            stage("T4: UK REF 2014")
            ctx["t4"] = run_t4(ctx)
            stage("T2: heterogeneous loadings, correlated pay-intake error")
            ctx["t2"] = run_t2(ctx)
            stage("T1: size audit")
            ctx["t1"] = run_t1(ctx)
    finally:
        EX.shutdown()
        EX = None
    if DEVCACHE:
        with open(Path(DEVCACHE) / "ctx.pkl", "wb") as f:
            pickle.dump({k: v for k, v in ctx.items() if k not in ("UKR", "USR")}, f)
    stage("write-up")
    write_all(ctx)
    stage("done")


# =============================================================================================================
# write-up (house style of GAP_CHECKS_RESULT.md)
# =============================================================================================================
f3, fci, Rows, md_table = s78.f3, s78.fci, s78.Rows, s78.md_table
PLAB = {"REF-pay": "REF–pay", "REF-intake": "REF–intake", "pay-intake": "pay–intake", "F-pay": "F–pay"}
SETLAB = {"base": "fitted nuisance parameters", "low": "every reliability at the lower end of its 95% interval",
          "high": "every reliability at the upper end of its 95% interval"}


def pf(p: float) -> str:
    return f"{p:.4f}"


def nr(x: dict) -> str:
    return f"[{f3(x['lo'])}, {f3(x['hi'])}]"


def reading(x: dict) -> bool:
    """T3 / T4 rule: the observed within value below the null range (its 2.5% point) and p < 0.05."""
    return bool(x["obs"] < x["lo"] and x["p"] < ALPHA)


def t1_verdict(rate: float) -> str:
    return "calibrated" if rate <= 0.075 + 1e-12 else "liberal"


def cp(k: int, n: int) -> tuple[float, float]:
    """Clopper-Pearson 95% interval of a binomial share (revision 1)."""
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return lo, hi


def cp_reading(lo: float, hi: float) -> str:
    """Revision 1: the binary size reading only where the interval lies wholly on one side of 0.075."""
    if hi <= 0.075:
        return "below 0.075"
    if lo > 0.075:
        return "above 0.075 (liberal)"
    return "not separable from 0.075"


def z_shift(size: float, sd: float, M: int) -> float:
    """Revision 1: shift of a normal null that turns a 5% test into one of the given size, sd x (z(size) - z(0.05))."""
    q = float(np.clip(size, 0.5 / M, 1 - 0.5 / M))
    return float(sd * (norm.ppf(q) - norm.ppf(ALPHA)))


REV = "rev. 1"


def write_all(ctx: dict):
    R = Rows()
    UKR, USR, T1, T2, T3, T4 = ctx["UKR"], ctx["USR"], ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"]
    nuk = f"{UKR['uk']['n']:,} programmes, {UKR['uk']['G']} providers, {UKR['uk']['S']} subjects"
    nus = f"{USR['us_main']['n']:,} programmes, {USR['us_main']['G']} universities, {USR['us_main']['K']} fields"
    nfe = f"{USR['us_fe']['n']:,} programmes, {USR['us_fe']['G']} universities, {USR['us_fe']['K']} fields"
    # ---------------- checks
    for nm, got, pub in ctx["c0_rows"]:
        R.put("check C0", nm, f"scripts/78 published {pub:+.4f}" if not nm.endswith(": p") else
              f"scripts/78 published {pub:.4f} (4 decimals)", got, status="check", d=4)
    R.put("check C1", "lean evaluators: largest |difference| from scripts/78 sim_task (UK)",
          f"{FASTCHK_N} seeds, every shared statistic", ctx["fast"]["uk"], status="check", d=8)
    R.put("check C1", "lean evaluators: largest |difference| from scripts/78 us_sim_task (US)",
          f"{FASTCHK_N} seeds, every shared statistic", ctx["fast"]["us"], status="check", d=8)
    # ---------------- T1
    iv = ctx["iv"]
    for tag in ("low", "high"):
        j = 1 if tag == "low" else 2
        G_ = T1[f"uk_dgp_{tag}"]
        R.put(f"T1 setting {tag}", "UK: REF test-retest of the generating model", f"target {iv['uk_ref'][j]:+.3f} "
              f"(interval end); pipeline mean over {CAL_M} check data sets", G_["rel_ref"], status="choice",
              k=f"REF error SD {G_['par']['sig_ref']:.3f}")
        R.put(f"T1 setting {tag}", "UK: intake split-half of the generating model", f"target {iv['uk_int'][j]:+.3f}",
              G_["rel_int"], status="choice", k=f"tau {G_['par']['tau']:.3f}")
        R.put(f"T1 setting {tag}", "UK: true pay noise variance factor c", f"(1 - {iv['uk_pay'][j]:.3f}) / (1 - "
              f"{iv['uk_pay'][0]:.3f}); the analyst keeps the published SEs", G_["opt"]["pay_c"], status="choice",
              k=f"analyst's pay reliability (mean) {G_['rel_pay']:+.3f}")
        R.put(f"T1 setting {tag}", "UK: null rho of the generating model", "re-matched to the observed across "
              "correlations", float(np.mean(G_["par"]["rho_b"])), status="choice",
              k="REF–pay / REF–intake / pay–intake " + ", ".join(f"{x:+.3f}" for x in G_["par"]["rho_b"]))
        G_ = T1[f"us_dgp_{tag}"]
        R.put(f"T1 setting {tag}", "US: true F error variance factor c_F", f"(1 - {iv['us_lam'][j]:.3f}) / (1 - "
              f"{iv['us_lam'][0]:.3f}); the analyst keeps the scripts/56 reliabilities", G_["opt"]["cF"],
              status="choice", k=f"analyst's lambda (mean) {G_['lam']:+.3f}")
        R.put(f"T1 setting {tag}", "US: true pay noise variance factor c_Y", f"(1 - {iv['us_pay'][j]:.3f}) / (1 - "
              f"{iv['us_pay'][0]:.3f}); the analyst keeps the scripts/73 noise", G_["opt"]["cY"], status="choice",
              k=f"analyst's pay reliability (mean) {G_['relY']:+.3f}")
        R.put(f"T1 setting {tag}", "US: null rho of the generating model", "re-matched to the observed across "
              "correlation", float(G_["par"]["rho_b"]), status="choice", k=f"pi {G_['par']['pi'][0]:.3f}, "
              f"{G_['par']['pi'][1]:.3f}")
    for tag in ("base", "low", "high", "power"):
        for cty, pairs in (("uk", PAIRS), ("us", ["F-pay"])):
            x = T1[tag][cty]
            for i, p_ in enumerate(pairs):
                lab = ("UK " if cty == "uk" else "US ") + PLAB[p_]
                lo_, hi_ = cp(int(x["k"][i]), x["M"])
                if tag == "power":
                    R.put("T1 power", f"{lab}: power at the fitted within and between values",
                          "share of data sets with p <= 0.05; SE = Monte Carlo SE; rev. 1: Clopper–Pearson 95% "
                          "interval", x["rate"][i], lo_, hi_, kind="Monte Carlo (Clopper–Pearson)", se=x["se"][i],
                          status="pre", k=f"{x['M']} data sets; failed {x['fail']}", d=3)
                else:
                    R.put(f"T1 size {tag}", f"{lab}: empirical size at 5%", SETLAB[tag] + "; SE = Monte Carlo SE; "
                          "rev. 1: Clopper–Pearson 95% interval", x["rate"][i], lo_, hi_,
                          kind="Monte Carlo (Clopper–Pearson)", se=x["se"][i], status="pre",
                          verdict=f"{t1_verdict(x['rate'][i])} (pre-specified, point); rev. 1: {cp_reading(lo_, hi_)}",
                          k=f"{x['M']} data sets; failed {x['fail']}", d=3)
                    R.put(f"T1 floor {tag}", f"{lab}: share of H0 data sets at the floor p = 1/{1 + B_IN}",
                          SETLAB[tag] + f"; about 1/{1 + B_IN} = {1 / (1 + B_IN):.3f} for a calibrated test",
                          float(x["floor"][i]), kind="Monte Carlo", status=REV,
                          k=f"{x['M'] - x['fail']} data sets with a test", d=3)
    # ---------------- T2
    ob = T2["obs_uk"]
    for cty in ("uk", "us"):
        A = T2[f"{cty}_a"]
        for p_, v in A["sd_obs"].items():
            R.put("T2 (a)", f"{'UK' if cty == 'uk' else 'US'} {PLAB[p_]}: between-field SD of field-level coupling",
                  "observed; sampling floor = simulated SD at s = 0 under scripts/78's null (k column)", v,
                  status="pre", k=f"floor {A['floor'][p_]:.3f}", d=3)
        sel = A["grid"]["sel"]
        for tag in ("pick", "alt"):
            if tag not in A:
                continue
            x = A[tag]
            role = {1: "verdict null (A1 case 1)", 2: "verdict null (A1 case 2: shares not matched)",
                    3: "largest SD matching across (A1 case 3)"}[sel["case"]] if tag == "pick" else \
                "share-consistent null (exploratory)"
            st = "post hoc (A1)" if (tag == "pick" and sel["case"] in (1, 2)) else "post hoc (A1), expl."
            if not x["ok"]:
                R.put("T2 (a)", f"{cty.upper()}: {role}", f"family {x['fam']}, s = {x['s']}", np.nan, status=st,
                      verdict="failed", k=x["err"][:60])
                continue
            pairs = PAIRS if cty == "uk" else ["F-pay"]
            for i, p_ in enumerate(pairs):
                ns = x["pairs"][p_] if cty == "uk" else x["pair"]
                sdv = x["sd_sim"][p_] if cty == "uk" else x["sd_sim"]
                R.put("T2 (a)", f"{cty.upper()} {PLAB[p_]}: {role}", f"loadings {FAM_LAB[x['fam']]}, s = {x['s']}; "
                      f"observed within {f3(ns['obs'])}; null 2.5-97.5%", ns["mean"], ns["lo"], ns["hi"],
                      kind="null 2.5-97.5%", status=st, verdict=f"p = {pf(ns['p'])}",
                      k=f"{ns['n']} null draws; null min {f3(ns['min'])}; coupling SD {sdv:.3f}")
            qo = np.asarray(ob["q"] if cty == "uk" else T2["obs_us"]["q"])
            R.put("T2 (a)", f"{cty.upper()}: {role}: largest |within share - observed|", "variance shares q",
                  float(np.max(np.abs(np.asarray(x["q"]) - qo))), status=st,
                  k="pi " + ", ".join(f"{v:.3f}" for v in np.asarray(x["par"]["pi"])), d=3)
    for re_ in RHO_E:
        x = T2[f"uk_b{re_:+.1f}"]
        st = "pre" if re_ > 0 else "expl."
        if not x["ok"]:
            R.put("T2 (b)", f"rho_e = {re_:+.1f}", "calibrated test", np.nan, status=st, verdict="failed",
                  k=x["err"][:60])
            continue
        for p_ in PAIRS:
            ns = x["pairs"][p_]
            R.put("T2 (b)", f"UK {PLAB[p_]}, rho_e = {re_:+.1f}", f"observed within {f3(ns['obs'])}; null 2.5-97.5%",
                  ns["mean"], ns["lo"], ns["hi"], kind="null 2.5-97.5%", status=st, verdict=f"p = {pf(ns['p'])}",
                  k=f"{ns['n']} null draws; null min {f3(ns['min'])}; null rho {x['par']['rho_b'][PAIRS.index(p_)]:+.3f}")
        R.put("T2 (b)", f"rho_e = {re_:+.1f}: realised correlation of the cohort errors", "pay noise vs intake share "
              "deviation, per programme-cohort (null mean)", x["err_cohort"], status=st, d=3)
        R.put("T2 (b)", f"rho_e = {re_:+.1f}: realised correlation of the within-provider score errors",
              "pay vs intake normal scores, observed minus noise-free residuals (null mean)", x["err_within"],
              status=st, d=3)
    t2a_uk, t2a_us = T2["uk_a"], T2["us_a"]
    ev_a = {c_: (T2[f"{c_}_a"]["grid"]["sel"]["case"] in (1, 2) and T2[f"{c_}_a"].get("pick", {}).get("ok", False))
            for c_ in ("uk", "us")}
    p_a_uk = t2a_uk["pick"]["pairs"]["REF-pay"]["p"] if ev_a["uk"] else np.nan
    p_a_us = t2a_us["pick"]["pair"]["p"] if ev_a["us"] else np.nan
    p_b = {re_: (T2[f"uk_b{re_:+.1f}"]["pairs"]["REF-pay"]["p"] if T2[f"uk_b{re_:+.1f}"]["ok"] else np.nan)
           for re_ in RHO_E}
    t2_eval = ev_a["uk"] and ev_a["us"] and all(np.isfinite(p_b[r_]) for r_ in (0.2, 0.5))
    t2_hold = t2_eval and p_a_uk < ALPHA and p_a_us < ALPHA and p_b[0.2] < ALPHA and p_b[0.5] < ALPHA
    t2_v = ("holds" if t2_hold else "does not hold") if t2_eval else "not evaluable"
    for cty in ("uk", "us"):                                   # revision 1: every SD + across grid point
        A = T2[f"{cty}_a"]
        for x in A.get("all", []):
            ao = T2["obs_uk"]["a"] if cty == "uk" else np.array([T2["obs_us"]["a"]])
            afit = float(np.max(np.abs(np.array([x["row"]["a"][p_] for p_ in (PAIRS if cty == "uk" else ["F-pay"])]) - ao)))
            qfit = float(np.max(np.abs(x["row"]["q"] - (T2["obs_uk"] if cty == "uk" else T2["obs_us"])["q"])))
            nm = (f"{cty.upper()}: grid point {x['fam']} s = {x['s']} (matches SD; across fit {afit:.3f}"
                  f"{', within 0.01' if x['row']['m_a'] else ''}; shares fit {qfit:.3f})")
            if x["null"] is None:
                R.put("T2 (a) all", nm, "", np.nan, status="post hoc (A1), rev. 1", verdict="failed")
                continue
            pairs = PAIRS if cty == "uk" else ["F-pay"]
            for p_ in pairs:
                ns = x["null"]["pairs"][p_] if cty == "uk" else x["null"]["pair"]
                sdv = x["null"]["sd_sim"][p_] if cty == "uk" else x["null"]["sd_sim"]
                R.put("T2 (a) all", f"{nm}: {PLAB[p_]}", f"observed within {f3(ns['obs'])}; null 2.5-97.5%"
                      + ("" if p_ in ("REF-pay", "F-pay") else "; not interpreted (grid matched on REF–pay)"),
                      ns["mean"], ns["lo"], ns["hi"], kind="null 2.5-97.5%", status="post hoc (A1), rev. 1",
                      verdict=f"p = {pf(ns['p'])}", k=f"{ns['n']} null draws; coupling SD {sdv:.3f}"
                      + (" (verdict null)" if x["reused"] else ""))
        for x in A.get("dense", []):
            nm = f"US: dense grid N s = {x['s']}"
            if not x["ok"]:
                R.put("T2 (a) dense", nm, "", np.nan, status="post hoc (A1), rev. 1", verdict="failed")
                continue
            ns = x["null"]["pair"]
            R.put("T2 (a) dense", f"{nm}: F–pay", f"observed within {f3(ns['obs'])}; null 2.5-97.5%; across fit "
                  f"{abs(x['a'] - float(T2['obs_us']['a'])):.3f}, shares fit {float(np.max(np.abs(x['q'] - T2['obs_us']['q']))):.3f}",
                  ns["mean"], ns["lo"], ns["hi"], kind="null 2.5-97.5%", status="post hoc (A1), rev. 1",
                  verdict=f"p = {pf(ns['p'])}", k=f"{ns['n']} null draws; coupling SD {x['null']['sd_sim']:.3f} "
                  f"(= {x['null']['sd_sim'] / A['sd_obs']['F-pay']:.2f} x observed)")
    R.put("T2 rule", "headline 'rejects equal agreement'", "UK REF–pay under (a), (b, +0.2), (b, +0.5); US F–pay "
          "under (a); rev. 1: (a) is a post hoc null (A1)", np.nan, status="pre", verdict=t2_v,
          k=f"p: UK (a) {pf(p_a_uk) if np.isfinite(p_a_uk) else '—'}, (b+0.2) {pf(p_b[0.2])}, (b+0.5) {pf(p_b[0.5])}; "
            f"US (a) {pf(p_a_us) if np.isfinite(p_a_us) else '—'}")
    # ---------------- T3
    for key, lab, nn in (("us_main", "main sample (scripts/58, SAT required)", nus), ("us_fe", "FE-only sample", nfe)):
        x = T3[key]
        st = "pre"
        R.putb("T3", f"{lab}: across universities within field", "Pearson of within-field normal scores", x["a"],
               status=st, k=nn)
        R.putb("T3", f"{lab}: within university", "university + field FE only", x["w"], status=st, k=nn)
    c0 = ctx["c0_us"]
    R.put("T3", "main sample: calibrated null rho", "C0 reproduction of scripts/78 (F at the lower bound)",
          float(c0["null"]["rho_b"]), status="pre", k=nus)
    R.put("T3", "main sample: calibrated test", f"observed within {f3(c0['nsum']['obs'])}; null 2.5-97.5%",
          c0["nsum"]["mean"], c0["nsum"]["lo"], c0["nsum"]["hi"], kind="null 2.5-97.5%", status="pre",
          verdict=f"p = {pf(c0['nsum']['p'])}; reading {'holds' if reading(c0['nsum']) else 'does not hold'}",
          k=f"{c0['nsum']['n']} null draws; null min {f3(c0['nsum']['min'])}")
    x = T3["test_fe"]
    if x["ok"]:
        R.put("T3", "FE-only sample: calibrated null rho", "scripts/78's US schedule, F at the lower bound",
              float(x["par"]["rho_b"]), status="pre", k=f"null across {f3(x['a_null'])} vs observed {f3(T3['us_fe']['a']['est'])}")
        R.put("T3", "FE-only sample: calibrated test", f"observed within {f3(x['pair']['obs'])}; null 2.5-97.5%",
              x["pair"]["mean"], x["pair"]["lo"], x["pair"]["hi"], kind="null 2.5-97.5%", status="pre",
              verdict=f"p = {pf(x['pair']['p'])}; reading {'holds' if reading(x['pair']) else 'does not hold'}",
              k=f"{x['pair']['n']} null draws; null min {f3(x['pair']['min'])}")
    R.put("T3", "FE-only sample: fields without a scripts/56 reliability (mean imputed)", "of the sample's fields",
          USR["us_fe"]["n_imputed"], status="pre", k=f"of {USR['us_fe']['K']}", d=0)
    # ---------------- T4
    lab4 = {"uk14": "REF 2014, own sample", "uk14c": "REF 2014, common sample", "uk21c": "REF 2021, common sample"}
    n4 = {k: f"{UKR[k]['n']:,} programmes, {UKR[k]['G']} providers, {UKR[k]['S']} subjects" for k in lab4}
    bk = {"uk14": T4["boot_own"], "uk14c": T4["boot_c14"], "uk21c": T4["boot_c21"]}
    for key in ("uk14", "uk14c", "uk21c"):
        ev = T4[key]["ev"]
        st = "expl." if key == "uk21c" else "pre"
        for i, p_ in enumerate(PAIRS):
            j = {"REF-pay": 0, "REF-intake": 3, "pay-intake": 6}[p_]
            for nm, off, val in (("across providers within subject", 0, ev[f"b|a|{p_}"]),
                                 ("within provider", 1, ev[f"b|w|{p_}"]),
                                 ("within provider, disattenuated", 2, ev[f"b|wd|{p_}"])):
                R.putb("T4", f"{lab4[key]}: {PLAB[p_]}, {nm}", "Blom scores within subject (scripts/78 G3)",
                       s78.summ(val, bk[key][:, j + off]), status=st, k=n4[key])
        R.putb("T4", f"{lab4[key]}: REF test-retest reliability (REF 2021 vs 2014)", "within-provider residuals",
               s78.summ(ev["b|rel_ref"], bk[key][:, 9]), status=st,
               k=f"{UKR[key]['n_ref']:,} programmes, {UKR[key]['G_ref']} providers")
        x = T4[key]["test"]
        if not x["ok"]:
            R.put("T4", f"{lab4[key]}: calibrated test", "", np.nan, status=st, verdict="failed", k=x["err"][:60])
            continue
        for i, p_ in enumerate(PAIRS):
            ns = x["pairs"][p_]
            R.put("T4", f"{lab4[key]}: {PLAB[p_]}, calibrated test", f"observed within {f3(ns['obs'])}; null rho "
                  f"{x['par']['rho_b'][i]:+.3f}; null 2.5-97.5%", ns["mean"], ns["lo"], ns["hi"],
                  kind="null 2.5-97.5%", status=st,
                  verdict=f"p = {pf(ns['p'])}; reading {'holds' if reading(ns) else 'does not hold'}",
                  k=f"{ns['n']} null draws; null min {f3(ns['min'])}")
    for p_ in ("REF-pay", "REF-intake"):
        j = {"REF-pay": 0, "REF-intake": 3}[p_]
        for nm, off, kk in (("across", 0, "b|a|"), ("within", 1, "b|w|"), ("within, disattenuated", 2, "b|wd|")):
            est = T4["uk14c"]["ev"][f"{kk}{p_}"] - T4["uk21c"]["ev"][f"{kk}{p_}"]
            R.putb("T4 paired", f"common sample: {PLAB[p_]} {nm}, REF 2014 minus REF 2021",
                   "paired provider cluster bootstrap (same draws)",
                   s78.summ(est, T4["boot_c14"][:, j + off] - T4["boot_c21"][:, j + off]), status="pre", k=n4["uk14c"])
    # ---------------- revision 1: how far the observed within values sit below the nulls
    rob = {}
    hom = [("UK REF–pay", ctx["c0_uk"]["nsum"]["REF-pay"]), ("UK REF–intake", ctx["c0_uk"]["nsum"]["REF-intake"]),
           ("UK pay–intake", ctx["c0_uk"]["nsum"]["pay-intake"]), ("US F–pay, main sample", ctx["c0_us"]["nsum"])]
    if T3["test_fe"]["ok"]:
        hom.append(("US F–pay, FE-only sample (T3)", T3["test_fe"]["pair"]))
    rob["hom"] = []
    for nm, ns in hom:
        mg = ns["q05"] - ns["obs"]
        rob["hom"].append((nm, mg, mg / ns["sd"]))
        R.put("Robustness", f"{nm}: observed within below the null's 5% point", "homogeneous calibrated null "
              "(scripts/78's model); null SDs in the k column", mg, status=REV,
              k=f"{mg / ns['sd']:.1f} null SDs; null 5% point {f3(ns['q05'])}, null SD {ns['sd']:.3f}", d=3)
    rob["shift"] = []
    sdc = {"REF-pay": ctx["c0_uk"]["nsum"]["REF-pay"]["sd"], "REF-intake": ctx["c0_uk"]["nsum"]["REF-intake"]["sd"],
           "pay-intake": ctx["c0_uk"]["nsum"]["pay-intake"]["sd"], "F-pay": ctx["c0_us"]["nsum"]["sd"]}
    for tag in ("low", "high"):
        for c_, pp in (("uk", PAIRS), ("us", ["F-pay"])):
            x = T1[tag][c_]
            for i, p_ in enumerate(pp):
                sh = z_shift(float(x["rate"][i]), sdc[p_], x["M"])
                rob["shift"].append((tag, p_, sh))
                R.put("Robustness", f"{'UK' if c_ == 'uk' else 'US'} {PLAB[p_]}: shift of the null implied by the "
                      f"T1 {tag} size", "normal approximation: null SD x (z(size) - z(0.05)), null SD of scripts/78's "
                      "null", sh, status=REV, k=f"size {x['rate'][i]:.3f}", d=3)
    rob["het"] = []
    for c_, p_ in (("uk", "REF-pay"), ("us", "F-pay")):
        A = T2[f"{c_}_a"]
        if A.get("pick", {}).get("ok"):
            ns = A["pick"]["pairs"][p_] if c_ == "uk" else A["pick"]["pair"]
            mg = ns["q05"] - ns["obs"]
            rob["het"].append((c_, p_, mg, mg / ns["sd"]))
            R.put("Robustness", f"{'UK' if c_ == 'uk' else 'US'} {PLAB[p_]}: observed within below the 5% point of "
                  f"A1's verdict null", f"loadings {FAM_LAB[A['pick']['fam']]}, s = {A['pick']['s']}", mg,
                  status="post hoc (A1), rev. 1", k=f"{mg / ns['sd']:.1f} null SDs; null 5% point {f3(ns['q05'])}, "
                  f"null SD {ns['sd']:.3f}", d=3)
    # ---------------- text
    md = render(ctx, R, dict(t2_v=t2_v, p_a_uk=p_a_uk, p_a_us=p_a_us, p_b=p_b, nuk=nuk, nus=nus, nfe=nfe, n4=n4,
                             rob=rob))
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    R.frame().drop(columns=["d"]).to_csv(OUT_CSV, index=False, float_format="%.10g")
    for p_ in (OUT_MD, OUT_CSV):
        print(p_.name, hashlib.md5(p_.read_bytes()).hexdigest())


def render(ctx: dict, R: Rows, V: dict) -> str:
    T1, T2, T3, T4 = ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"]
    iv = ctx["iv"]
    L = []
    L.append("# Test calibration — the size of the simulation-calibrated test, heterogeneous null models, the "
             "largest US sample and REF 2014")
    L.append("")
    L.append("Script: `scripts/84_test_calibration.py` (seed 84; every number below is written by the script from its "
             "own computations; a second run gives a byte-identical file, see Method). It closes four referee gaps in "
             "the simulation-calibrated test of `scripts/78_gap_checks.py` (G3, GAP_CHECKS_RESULT.md revisions 1–2), "
             "whose functions it imports without editing them. Public data only, all already on disk (the Wapman et "
             "al. 2026 release with the repaired name join, College Scorecard, scripts/73 noise, REF 2021 and REF 2014, "
             "the DfE LEO provider × subject file). Descriptive, not causal. Table: "
             "`data/interim/test_calibration_summary.csv` (every key number).")
    L.append("")
    # ---- answer
    L.append("## Answer")
    L.append("")
    base, low, high, pw = T1["base"], T1["low"], T1["high"], T1["power"]
    vt = [t1_verdict(x) for tag in ("base", "low", "high") for x in list(T1[tag]["uk"]["rate"]) + list(T1[tag]["us"]["rate"])]
    lib = [f"{('UK ' + PLAB[p_]) if c_ == 'uk' else 'US F–pay'} ({tag})" for tag in ("base", "low", "high")
           for c_, pp in (("uk", PAIRS), ("us", ["F-pay"])) for i, p_ in enumerate(pp)
           if t1_verdict(T1[tag][c_]["rate"][i]) == "liberal"]

    def sz(tag):
        x, y = T1[tag]["uk"], T1[tag]["us"]
        return (", ".join(f"{PLAB[p_]} {x['rate'][i]:.3f} ({x['se'][i]:.3f})" for i, p_ in enumerate(PAIRS)) +
                f"; US F–pay {y['rate'][0]:.3f} ({y['se'][0]:.3f})")
    nfail = sum(T1[t]["uk"]["fail"] + T1[t]["us"]["fail"] for t in ("base", "low", "high", "power"))
    RV1 = "*Revision 1, added after results were seen:*"

    def szc(tag):
        out = []
        for c_, pp in (("uk", PAIRS), ("us", ["F-pay"])):
            x = T1[tag][c_]
            for i, p_ in enumerate(pp):
                lo_, hi_ = cp(int(x["k"][i]), x["M"])
                out.append(f"{'UK ' if c_ == 'uk' else 'US '}{PLAB[p_]} {x['rate'][i]:.3f} [{lo_:.3f}, {hi_:.3f}]")
        return ", ".join(out)

    def side(want):
        out = []
        for tag in ("base", "low", "high"):
            for c_, pp in (("uk", PAIRS), ("us", ["F-pay"])):
                x = T1[tag][c_]
                for i, p_ in enumerate(pp):
                    if cp_reading(*cp(int(x["k"][i]), x["M"])).startswith(want):
                        out.append(f"{'UK ' if c_ == 'uk' else 'US '}{PLAB[p_]} ({tag})")
        return "; ".join(out) if out else "none"

    def flo(tag):
        x, y = T1[tag]["uk"], T1[tag]["us"]
        return ", ".join(f"{PLAB[p_]} {x['floor'][i]:.3f}" for i, p_ in enumerate(PAIRS)) + f", US {y['floor'][0]:.3f}"
    b0 = T1["base"]["uk"]
    blo, bhi = cp(int(b0["k"][0]), b0["M"])
    gl, gh, ul, uh = T1["uk_dgp_low"]["opt"], T1["uk_dgp_high"]["opt"], T1["us_dgp_low"]["opt"], T1["us_dgp_high"]["opt"]
    L.append(f"1. **T1 — size audit. Pre-specified rule applied to the point estimates: "
             f"{'calibrated for all four pairs in all three settings' if not lib else 'liberal for ' + '; '.join(lib)} "
             f"(size ≤ 0.075).** In each of M = {M_OUT} data sets simulated under ρ_within = ρ_between on the "
             f"real layout, the nuisance parameters were re-estimated from that data set exactly as scripts/78 "
             f"estimates them on the real data ({CAL_R} rounds × {CAL_M} data sets of damped moment matching from "
             f"data-based starting values) and the full test was run with B = {B_IN} null draws. {RV1} empirical "
             f"sizes at 5% with Clopper–Pearson 95% intervals — at the fitted nuisance parameters (scripts/78's null): "
             f"{szc('base')}; every reliability at the lower end of its 95% interval: {szc('low')}; at the upper end: "
             f"{szc('high')}. With M = {M_OUT} an interval around {b0['rate'][0]:.3f} runs from {blo:.3f} to "
             f"{bhi:.3f}, so the audit cannot separate a size of 0.05 from one of 0.10, and the binary reading is "
             f"dropped wherever the interval straddles 0.075. The interval lies wholly above 0.075 (liberal) for "
             f"{side('above')} and wholly below for {side('below')}; every other size is not separable from 0.075. "
             f"What the perturbed settings move (corrected wording): in the UK the REF and intake reliabilities are "
             f"re-estimated by the inner test, so putting them at the ends of their intervals moves the true parameter "
             f"point and the test re-fits to it; that is not a misspecification. Only the UK pay noise (true variance "
             f"× {gl['pay_c']:.2f} at the low and × {gh['pay_c']:.2f} at the high setting, while the analyst keeps the "
             f"published SEs) and the US F error and pay noise (× {ul['cF']:.3f} / {uh['cF']:.3f} and × "
             f"{ul['cY']:.3f} / {uh['cY']:.3f}, about ±8%) are misspecified for the analyst. Share of H0 data sets in "
             f"which the inner test reaches its floor p = 1/{1 + B_IN} (about {1 / (1 + B_IN):.3f} for a calibrated "
             f"test): fitted {flo('base')}; low {flo('low')}; high {flo('high')}. Power against the fitted within and "
             f"between values (scripts/78's calibrated alternative): {szc('power')}. Inner tests that failed: "
             f"{nfail} of {8 * M_OUT}.")
    A_uk, A_us = T2["uk_a"], T2["us_a"]

    def a_txt(cty, A):
        sel = A["grid"]["sel"]
        if sel["pick"] is None or "pick" not in A or not A["pick"]["ok"]:
            return f"{cty}: no null to report"
        x = A["pick"]
        p_ = "REF-pay" if cty == "UK" else "F-pay"
        ns = x["pairs"][p_] if cty == "UK" else x["pair"]
        sdv = x["sd_sim"][p_] if cty == "UK" else x["sd_sim"]
        return (f"{cty} {FAM_LAB[x['fam']]}, s = {x['s']} (coupling SD {sdv:.3f} against {A['sd_obs'][p_]:.3f} "
                f"observed; largest within-share misfit "
                f"{float(np.max(np.abs(np.asarray(x['q']) - np.asarray((T2['obs_uk'] if cty == 'UK' else T2['obs_us'])['q'])))):.3f}): "
                f"{PLAB[p_]} observed within {f3(ns['obs'])} against a null range {nr(ns)}, p = {pf(ns['p'])}")

    def alt_txt(cty, A):
        if "alt" not in A or not A["alt"]["ok"]:
            return f"{cty}: none"
        y = A["alt"]
        p_ = "REF-pay" if cty == "UK" else "F-pay"
        ys = y["pairs"][p_] if cty == "UK" else y["pair"]
        sdv = y["sd_sim"][p_] if cty == "UK" else y["sd_sim"]
        return (f"{cty} {y['fam']} s = {y['s']}, coupling SD {sdv:.3f} against a floor of {A['floor'][p_]:.3f}, "
                f"{PLAB[p_]} p = {pf(ys['p'])}")

    def allp(cty, A, first_only):
        p_ = "REF-pay" if cty == "UK" else "F-pay"
        xs = [x for x in A.get("all", []) if x["null"] is not None]
        if first_only:
            xs = [min([x for x in xs if x["fam"] == f_], key=lambda x: x["s"]) for f_ in FAMS
                  if any(x["fam"] == f_ for x in xs)]
        else:
            xs = [x for x in xs if x["row"]["m_a"]]
        if not xs:
            return "none"
        pv = [(x["null"]["pairs"][p_] if cty == "UK" else x["null"]["pair"])["p"] for x in xs]
        return (f"p {pf(min(pv))}–{pf(max(pv))} on " + ", ".join(f"{x['fam']}{x['s']}" for x in xs))

    def boundary(A):
        pts = [(x["s"], x["null"]["sd_sim"], x["null"]["pair"]["p"]) for x in A.get("all", [])
               if x["fam"] == "N" and x["null"] is not None]
        pts += [(x["s"], x["null"]["sd_sim"], x["null"]["pair"]["p"]) for x in A.get("dense", []) if x["ok"]]
        pts = sorted(pts)
        so = A["sd_obs"]["F-pay"]
        fail = [x for x in pts if x[2] >= ALPHA]
        if not fail:
            return f"on family N the p-value stays below 0.05 at every point up to s = {pts[-1][0]}" if pts else ""
        f0 = fail[0]
        ok_ = [x for x in pts if x[0] < f0[0]]
        t = (f"on family N (the verdict family) the p-value first reaches 0.05 at s = {f0[0]} (p = {pf(f0[2])}, "
             f"coupling SD {f0[1]:.3f}, {f0[1] / so:.2f} times the observed {so:.3f})")
        if ok_:
            t += (f"; the last point below 0.05 is s = {ok_[-1][0]} (p = {pf(ok_[-1][2])}, SD {ok_[-1][1]:.3f}, "
                  f"{ok_[-1][1] / so:.2f} times the observed)")
        return t + "; further out: " + ", ".join(f"s = {x[0]} p = {pf(x[2])}" for x in pts if x[0] > f0[0])
    case = {c_: T2[f"{c_}_a"]["grid"]["sel"]["case"] for c_ in ("uk", "us")}
    b2, b5 = T2["uk_b+0.2"], T2["uk_b+0.5"]
    c0n = ctx["c0_uk"]["nsum"]
    L.append(f"2. **T2 — heterogeneous loadings and correlated errors. Under the pre-specified rule the headline "
             f"'rejects equal agreement' {V['t2_v']} (p < 0.05 for UK REF–pay under (a), (b, +0.2) and (b, +0.5) and "
             f"for US F–pay under (a)); (a) rests on a post hoc null.** (a) The pre-specified loading family cannot "
             f"reproduce how much the across-university coupling varies over fields (observed between-field SD "
             f"{A_us['sd_obs']['F-pay']:.3f} for US F–pay, sampling floor {A_us['floor']['F-pay']:.3f}; "
             f"{A_uk['sd_obs']['REF-pay']:.3f} for UK REF–pay, floor {A_uk['floor']['REF-pay']:.3f}), so amendment A1 "
             f"widened the family and selected the verdict nulls (UK case {case['uk']}, US case {case['us']}: no grid "
             f"point matches the spread, the across correlations and the within-university variance shares together): "
             f"{a_txt('UK', A_uk)}; {a_txt('US', A_us)}. {RV1} A1 is post hoc. It followed a scratch diagnostic (2026-11-16 "
             f"09:58), which had printed, at fixed π and ρ, the simulated mean within correlation under several "
             f"loadings next to the known observed values, and the 10:06 development run already applied A1 and "
             f"computed T2 (a) p-values with 40 null draws before the reported run; A1 was not changed afterwards, "
             f"but every (a) row is labelled post hoc (A1). Every grid point that matches the observed spread gets "
             f"its own {NULL_N}-draw null (table in the grid section). The smallest such point of each family: UK REF–pay "
             f"{allp('UK', A_uk, True)}; US F–pay {allp('US', A_us, True)}. Those that also meet A1's across "
             f"criterion: UK {allp('UK', A_uk, False)}; US {allp('US', A_us, False)}. Where the US rejection fails, "
             f"with the denser grid: {boundary(A_us)}. The intake pairs are not interpreted "
             f"under (a): the grid matches REF–pay's spread only. The 'share-consistent' nulls sit at the sampling "
             f"floor of the spread ({alt_txt('UK', A_uk)}; {alt_txt('US', A_us)}), so they are effectively the "
             f"homogeneous null. (b) Correlated pay–intake error (UK; the US has no shared source) is uninformative "
             f"for REF–pay: its null range is {nr(b2['pairs']['REF-pay']) if b2['ok'] else '—'} at ρ_e = +0.2 and "
             f"{nr(b5['pairs']['REF-pay']) if b5['ok'] else '—'} at +0.5 against {nr(c0n['REF-pay'])} under "
             f"scripts/78's null (p = {pf(b2['pairs']['REF-pay']['p']) if b2['ok'] else '—'} and "
             f"{pf(b5['pairs']['REF-pay']['p']) if b5['ok'] else '—'}); it moves the pay–intake null (null mean "
             f"{f3(c0n['pay-intake']['mean'])} → {f3(b2['pairs']['pay-intake']['mean']) if b2['ok'] else '—'} and "
             f"{f3(b5['pairs']['pay-intake']['mean']) if b5['ok'] else '—'}); realised error correlation "
             f"{b2['err_cohort']:+.2f} / {b5['err_cohort']:+.2f} per cohort.")
    fe, mn = T3["test_fe"], ctx["c0_us"]["nsum"]
    if fe["ok"]:
        L.append(f"3. **T3 — the largest US sample. The reading {'holds' if reading(fe['pair']) else 'does not hold'} "
                 f"on the FE-only sample (rule: within below the null range and p < 0.05).** FE-only sample "
                 f"({V['nfe']}): across {s78.Rows.ec(R, 'T3', 'FE-only sample: across universities within field', 3)}, "
                 f"within {s78.Rows.ec(R, 'T3', 'FE-only sample: within university', 3)}; calibrated null ρ "
                 f"{f3(fe['par']['rho_b'])}, null range of the within correlation {nr(fe['pair'])}, p = "
                 f"{pf(fe['pair']['p'])}. Main sample ({V['nus']}): across "
                 f"{s78.Rows.ec(R, 'T3', 'main sample (scripts/58, SAT required): across universities within field', 3)}, "
                 f"within {s78.Rows.ec(R, 'T3', 'main sample (scripts/58, SAT required): within university', 3)}; "
                 f"null range {nr(mn)}, p = {pf(mn['p'])} (scripts/78, reproduced).")
    else:
        L.append(f"3. **T3 — the calibrated test on the FE-only sample failed** ({fe['err'][:80]}).")

    def t4p(key, p_):
        x = T4[key]["test"]
        if not x["ok"]:
            return "test failed"
        ns = x["pairs"][p_]
        return (f"across {f3(T4[key]['ev'][f'b|a|{p_}'])}, within {f3(ns['obs'])} against a null range {nr(ns)}, "
                f"p = {pf(ns['p'])} (reading {'holds' if reading(ns) else 'does not hold'})")
    rp = [T4[k]["test"]["ok"] and reading(T4[k]["test"]["pairs"]["REF-pay"]) for k in ("uk14", "uk14c")]
    L.append(f"4. **T4 — REF 2014. The reading {'holds' if all(rp) else 'does not hold'} for REF–pay on REF 2014's "
             f"own sample and on the common sample (same rule as T3; the reading rests on REF–pay).** Own sample "
             f"({V['n4']['uk14']}): REF–pay {t4p('uk14', 'REF-pay')}; REF–intake {t4p('uk14', 'REF-intake')}. Common "
             f"sample ({V['n4']['uk14c']}), REF 2014: REF–pay {t4p('uk14c', 'REF-pay')}; REF–intake "
             f"{t4p('uk14c', 'REF-intake')}; REF 2021 on the same cells (exploratory): REF–pay {t4p('uk21c', 'REF-pay')}. "
             f"Paired differences, REF 2014 minus REF 2021 (provider cluster bootstrap, same draws): REF–pay across "
             f"{R.ec('T4 paired', 'common sample: REF–pay across, REF 2014 minus REF 2021', 3)}, within "
             f"{R.ec('T4 paired', 'common sample: REF–pay within, REF 2014 minus REF 2021', 3)}; REF–intake across "
             f"{R.ec('T4 paired', 'common sample: REF–intake across, REF 2014 minus REF 2021', 3)}, within "
             f"{R.ec('T4 paired', 'common sample: REF–intake within, REF 2014 minus REF 2021', 3)}. {RV1} REF 2014 "
             f"is a re-measurement of academic standing on largely the same cells (the common sample holds "
             f"{ctx['UKR']['uk14c']['n']:,} of REF 2014's {ctx['UKR']['uk14']['n']:,} and of REF 2021's "
             f"{ctx['UKR']['uk']['n']:,} programmes, with the same pay and intake), not an independent replication.")
    rob = V["rob"]
    hm = [x[1] for x in rob["hom"]]
    hs = [x[2] for x in rob["hom"]]
    sl = [x[2] for x in rob["shift"] if x[0] == "low"]
    het = {c_: (mg, z_) for c_, p_, mg, z_ in rob["het"]}
    for c_ in ("uk", "us"):
        het.setdefault(c_, (np.nan, np.nan))
    L.append(f"5. **How robust the rejection is (revision 1, added after results were seen).** Under the homogeneous null (scripts/78's model; the "
             f"three UK pairs, US F–pay on the main sample and on the FE-only sample) the observed within value lies "
             f"{min(hm):.2f}–{max(hm):.2f} (correlation units) below the null's 5% point, i.e. {min(hs):.0f}–"
             f"{max(hs):.0f} null SDs. T1's worst setting (every reliability at the lower end of its interval) moves "
             f"the null by only about {min(sl):.3f}–{max(sl):.3f} (normal approximation: null SD × (z(size) − "
             f"z(0.05))). So the rejection does not rest on the calibration of the test. It rests on the latent "
             f"structure: under heterogeneous loadings (A1's verdict nulls, post hoc) the margin is about "
             f"{het['us'][1]:.1f} null SDs for US F–pay ({het['us'][0]:.3f}) and {het['uk'][1]:.1f} for UK REF–pay "
             f"({het['uk'][0]:.3f}). Not run: a joint size audit under heterogeneous loadings plus misspecified "
             f"noise.")
    L.append("")
    # ---- pre-specification
    L.append("## Pre-specification, amendment and deviations")
    L.append("")
    L.append("The binding text below was fixed on 2026-11-16 before any outcome of this script was computed and is "
             f"copied verbatim into the script's docstring (SHA-256 `{PRESPEC_SHA256}`, checked at run time). The "
             f"implementation choices C0–C10 were recorded the same day, after reading scripts/78 and "
             f"GAP_CHECKS_RESULT.md and timing the simulation code, before any T1–T4 outcome was computed (SHA-256 "
             f"`{CHOICES_SHA256}`). Amendment A1 (T2 (a) only) was made after a development run and before any T2 (a) "
             f"p-value was computed (SHA-256 `{A1_SHA256}`); it says what that run had printed. *Revision 1, "
             f"added after results were seen:* A1 is post hoc (see Revision 1, item 2). File "
             f"times are the only timestamps. Status labels in the table: pre = "
             f"a quantity named in the binding text; post hoc (A1) = a T2 (a) null or grid point that rests on "
             f"amendment A1; choice = a quantity fixed in C0–C10 that the binding text does not name; check = a "
             f"reproduction of scripts/78; expl. = exploratory (named as such in C6, C9 or A1); rev. 1 = added in "
             f"revision 1, after results were seen.")
    L.append("")
    L.append("```text")
    L.append(_block("-----BEGIN PRESPEC-----", "-----END PRESPEC-----").rstrip("\n"))
    L.append("```")
    L.append("")
    L.append("<details><summary>Implementation choices (C0–C10) and amendment A1, verbatim</summary>")
    L.append("")
    L.append("```text")
    L.append(_block("-----BEGIN CHOICES-----", "-----END CHOICES-----").rstrip("\n"))
    L.append(_block("-----BEGIN AMENDMENT A1-----", "-----END AMENDMENT A1-----").rstrip("\n"))
    L.append("```")
    L.append("")
    L.append("</details>")
    L.append("")
    L.append("Deviations and clarifications:")
    L.append("")
    L.append("- **A1 (T2 (a)).** C5's loadings exp(sη − s²) cannot reach the observed spread of field-level coupling, "
             "and its multiplicative update of s ran away in a development run; A1 replaces the update by a fixed "
             "grid over three loading families and states how the verdict null is selected. The grid is in its own "
             "section below. *Revision 1, added after results were seen:* A1 is post hoc. Before "
             "it was written, a scratch diagnostic (2026-11-16 09:58) had printed, at fixed π and ρ and for "
             "lognormal and sign-varying loadings, the simulated between-field SD of the coupling and the simulated "
             "mean within correlation, next to the observed values already known; after it was written, the 10:06 "
             "development run (12 calibration rounds, 40 null draws) applied A1 and computed and rendered T2 (a) "
             "p-values and null ranges before the reported run. A1 was not changed after either.")
    L.append("- **T2 (b) and the US.** The binding text lists US F–pay in the (b) rule, but (b) is defined for UK pay "
             "and intake (the same LEO rows); US F and pay come from different sources, so the US part of the rule "
             "reads on (a) alone (C6).")
    L.append("- **'Rejection at the 5% level'** is p ≤ 0.05 with p = (1 + #{null ≤ observed})/(1 + B): with B = 200, "
             "at most 9 of 200 null draws at or below the observed within correlation. The T2–T4 rules use p < 0.05 "
             "with 600 null draws, so the smallest attainable p is 1/601 = 0.0017.")
    L.append("- **scripts/78 reproduction (C0).** Every reproduced value agrees with gap_checks_summary.csv to "
             "within 5e-7 (the p-values to the 4 decimals scripts/78 prints); the check rows are in the table. "
             "The UK panel of scripts/78's uk_panel() is rebuilt with the same scripts/76 calls, with freed memory "
             "returned to the system between them (no effect on any number).")
    L.append("")
    L.append("## Revision 1")
    L.append("")
    L.append("Every item below is *revision 1, added after results were seen*. An independent "
             "re-computation reproduced T3 and T4, confirmed that T1 refits the nuisance parameters as scripts/78 does, "
             "and found no computational error; the changes below concern interpretation and disclosure. No "
             "pre-specified verdict and no earlier number changes; the new rows carry the status rev. 1.")
    L.append("")
    L.append("1. **T1.** Clopper–Pearson 95% intervals for every size and power; with M = 200 they cannot separate a "
             "size of 0.05 from one of 0.10, so the binary 'calibrated / liberal' reading is kept only where the "
             "interval lies wholly on one side of 0.075 (verdict column: pre-specified reading on the point "
             "estimate, then the revision-1 reading). Corrected wording of the perturbed settings: the UK REF and "
             "intake reliabilities are re-estimated by the inner test, so moving them moves the true parameter "
             "point, not the analyst's assumption; only the UK pay noise and the US F and pay noise are "
             "misspecified for the analyst. Added: the share of H0 data sets in which the inner test reaches its "
             "floor p.")
    L.append("2. **T2 (a).** The A1 rows are labelled post hoc (A1), and what preceded A1 is disclosed (deviations "
             "above). Added: a 600-draw null for every grid point that matches the observed spread (with its "
             "across and share fit), a denser US grid for family N between s = 0.6 and 0.7 that locates where the "
             "rejection fails, and the statement that the share-consistent nulls sit at the sampling floor of the "
             "spread (effectively homogeneous). The (a) conclusions for the intake pairs are withdrawn: the grid "
             "matches REF–pay's spread only.")
    L.append("3. **T2 (b)** is uninformative for REF–pay: its null range is unchanged from scripts/78's null.")
    L.append("4. **T4** is a re-measurement of academic standing on largely the same cells, not an independent "
             "replication.")
    L.append("5. **Robustness summary** (Answer, item 5; rows 'Robustness'): margins of the observed within values "
             "below the nulls' 5% points, in correlation units and null SDs, and the shift of the null implied by "
             "T1's worst setting.")
    L.append("6. **Not run:** a joint size audit under heterogeneous loadings plus misspecified noise.")
    L.append("")
    # ---- table
    L.append("## Key numbers")
    L.append("")
    L.append("CI = 95%. *CI kind*: bootstrap = percentile interval of a cluster bootstrap (providers for the UK, "
             f"universities for the US; {B_BOOT:,} replicates, every reliability recomputed in each); null "
             "2.5–97.5% = the range of the within-university correlation over the simulated null data sets (not a "
             "CI; the estimate column is the null mean and the observed value is in the spec column); Monte Carlo = "
             "a share over simulated data sets with its Monte Carlo SE. SE = SD of the draws; MDE = 2.80 SE. *status*: "
             "see the pre-specification section. k = sample or simulation size.")
    L.append("")
    L += md_table(R)
    L.append("")
    # ---- A1 grid
    L.append("## T2 (a): loading grid (amendment A1)")
    L.append("")
    L.append("At each point the other nuisance parameters are re-matched by scripts/78's null schedule; the "
             f"statistics are means over {CAL_M} check data sets. SD = between-field SD of the field-level coupling "
             "(the rule's pair: UK REF–pay, US F–pay; the other UK pairs in brackets); across = largest |simulated − "
             "observed| over the pairs; shares = largest |simulated − observed| within-university variance share; "
             "π = the largest university variance share. Matches: SD / across (≤ 0.01) / shares (≤ 0.01 and π < 0.98).")
    L.append("")
    L.append("| country | family | s | SD | across | shares | π max | matches |")
    L.append("|---|---|---|---|---|---|---|---|")
    for cty in ("uk", "us"):
        A = T2[f"{cty}_a"]
        obs = T2["obs_uk"] if cty == "uk" else T2["obs_us"]
        ao = {p_: float(obs["a"][i]) for i, p_ in enumerate(PAIRS)} if cty == "uk" else {"F-pay": float(obs["a"])}
        for r in A["grid"]["rows"]:
            if not r["ok"]:
                L.append(f"| {cty.upper()} | {r['fam']} | {r['s']} | fit failed | — | — | — | — |")
                continue
            rule = A["grid"]["rule"]
            sd = f"{r['sd'][rule]:.3f}" + (f" ({r['sd']['REF-intake']:.3f}, {r['sd']['pay-intake']:.3f})" if cty == "uk" else "")
            L.append(f"| {cty.upper()} | {r['fam']} | {r['s']} | {sd} | "
                     f"{max(abs(r['a'][p_] - ao[p_]) for p_ in ao):.3f} | {float(np.max(np.abs(r['q'] - obs['q']))):.3f} | "
                     f"{float(np.max(r['pi'])):.3f} | {'/'.join('yes' if r[k] else 'no' for k in ('m_sd', 'm_a', 'm_q'))} |")
    L.append("")
    L.append("*Revision 1, added after results were seen:* every grid point that matches the "
             f"observed spread, with its own null ({NULL_N} draws; the verdict null reused where it is the same "
             "point). p for the rule's pair; the intake pairs (UK) are not interpreted under (a). across / shares = "
             "fit as above; A1 = meets A1's across criterion (≤ 0.01).")
    L.append("")
    L.append("| country | family | s | coupling SD | across | shares | A1 across | observed within | null 2.5–97.5% | p | "
             "p REF–intake / pay–intake |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for cty in ("uk", "us"):
        A = T2[f"{cty}_a"]
        obs = T2["obs_uk"] if cty == "uk" else T2["obs_us"]
        ao = {p_: float(obs["a"][i]) for i, p_ in enumerate(PAIRS)} if cty == "uk" else {"F-pay": float(obs["a"])}
        for x in A.get("all", []):
            r = x["row"]
            if x["null"] is None:
                L.append(f"| {cty.upper()} | {x['fam']} | {x['s']} | — | — | — | — | — | null failed | — | — |")
                continue
            rule = A["grid"]["rule"]
            ns = x["null"]["pairs"][rule] if cty == "uk" else x["null"]["pair"]
            sdv = x["null"]["sd_sim"][rule] if cty == "uk" else x["null"]["sd_sim"]
            ext = (f"{pf(x['null']['pairs']['REF-intake']['p'])} / {pf(x['null']['pairs']['pay-intake']['p'])}"
                   if cty == "uk" else "—")
            L.append(f"| {cty.upper()} | {x['fam']} | {x['s']} | {sdv:.3f} | "
                     f"{max(abs(r['a'][p_] - ao[p_]) for p_ in ao):.3f} | {float(np.max(np.abs(r['q'] - obs['q']))):.3f} | "
                     f"{'yes' if r['m_a'] else 'no'} | {f3(ns['obs'])} | {nr(ns)} | {pf(ns['p'])} | {ext} |")
    L.append("")
    if A_us.get("dense"):
        L.append(f"Denser US grid, family N (revision 1): coupling SD relative to the observed {A_us['sd_obs']['F-pay']:.3f}.")
        L.append("")
        L.append("| s | coupling SD | SD / observed | across | shares | π max | null 2.5–97.5% | p |")
        L.append("|---|---|---|---|---|---|---|---|")
        for x in A_us["dense"]:
            if not x["ok"]:
                L.append(f"| {x['s']} | fit failed | — | — | — | — | — | — |")
                continue
            ns = x["null"]["pair"]
            L.append(f"| {x['s']} | {x['null']['sd_sim']:.3f} | {x['null']['sd_sim'] / A_us['sd_obs']['F-pay']:.2f} | "
                     f"{abs(x['a'] - float(T2['obs_us']['a'])):.3f} | {float(np.max(np.abs(x['q'] - T2['obs_us']['q']))):.3f} | "
                     f"{float(np.max(x['pi'])):.3f} | {nr(ns)} | {pf(ns['p'])} |")
        L.append("")
    L.append(f"Observed SD: UK REF–pay {A_uk['sd_obs']['REF-pay']:.3f} (REF–intake {A_uk['sd_obs']['REF-intake']:.3f}, "
             f"pay–intake {A_uk['sd_obs']['pay-intake']:.3f}); US F–pay {A_us['sd_obs']['F-pay']:.3f}. Families: "
             + "; ".join(f"{k} = {v}" for k, v in FAM_LAB.items()) + ".")
    L.append("")
    # ---- method
    L.append("## Method")
    L.append("")
    L.append("- **C0, the base of T1.** scripts/78's G3 calibration is re-run with its own functions (`sim_task`, "
             "`us_sim_task`, `sim_inputs`, `us_sim_inputs`) and its own SeedSequence(78) children; its nested update "
             "rules are re-stated here. The reproduced null parameter sets (ρ_within = ρ_between, matched to the "
             "observed across correlations, variance shares, REF test-retest, intake split-half and intake moments) "
             "generate the T1 size data sets; the reproduced alternative (ρ_within and ρ_between free) generates the "
             "power data sets.")
    L.append("- **C1, lean evaluators.** The new simulations use Blom-only re-implementations of scripts/78's "
             "generator and pipeline (vectorised midranks, the provider + subject FE projection precomputed for the "
             "fixed layout), with the same random-number calls in the same order; they agree with scripts/78's "
             "functions to rounding error (check rows).")
    L.append("- **T1.** Per data set: generate on the real layout; compute the targets and starting values from that "
             "data set; re-derive the data-dependent inputs (UK: subject pay signal SD, known-band graduates per "
             "cohort and the subjects' band shares from the simulated published band counts with 'low' = 1.5; US: "
             "field pay signal SD); run scripts/78's null schedule (12 × 64, damping 0.5) and 200 null draws; reject "
             "if p ≤ 0.05. Perturbed settings move only the generating truth (UK REF error SD and intake cohort noise "
             "re-calibrated to the interval ends; UK pay, US F and US pay noise variances scaled so that the "
             "reliability equals the interval end on the real layout, signal SDs set to keep each subject's or "
             "field's pay variance); the inner test keeps the published noise and reliabilities. Failed inner tests "
             "count as rejections in a size and as non-rejections in a power.")
    L.append("- **T2 (a).** Field-level coupling = the across statistic computed within one field (subject); its "
             "between-field SD is matched through the pipeline (A1 grid). Loadings are independent across variables "
             "and fields and redrawn in every data set. **(b).** In each released cohort the pay noise is "
             "se_c(ρ_e ζ_c + √(1 − ρ_e²) ξ_c), ζ_c the cohort's standardised intake error (realised share minus the "
             "latent expected share, binomial plus cohort noise); all nuisance parameters re-matched with ρ_e fixed; "
             "600 null draws.")
    L.append("- **T3.** FE-only sample = `s58.fe_build(cells, [], [], 'earnings')` on scripts/78's cells "
             "(scripts/58's sample rules without the selectivity controls); scores, λ and pay noise as scripts/78 "
             "(`us_g3_data`); scripts/78's US calibration (F at the lower bound) with new seeds.")
    L.append("- **T4.** REF 2014 GPA (scripts/76's CLEAN14 mapping) in place of REF 2021 in scripts/78's G3 pipeline "
             "(`uk_g3_data` on the panel with the two REF columns swapped, so REF 2021 is the test-retest partner); "
             "the common sample is the largest set of cells with both REF scores satisfying scripts/76's rules "
             "(built from either exercise's sample and asserted identical). Calibrated tests as scripts/78's UK null "
             "with new seeds; the paired comparison uses one set of provider draws for both exercises.")
    L.append(f"- **Seeds and reproducibility.** One child of SeedSequence(84) per named analysis and one descendant "
             f"per data set; fork worker processes; BLAS 1 thread; results do not depend on the number of workers. "
             f"Two consecutive runs give byte-identical write-up and table (md5 compared).")
    L.append("")
    L.append("## Caveats")
    L.append("")
    L.append("- **Every test here is model-based.** The size audit asks whether the calibrated test holds its level "
             "when its own model is true with nuisance parameters near the fitted ones; it does not cover "
             "misspecifications outside the perturbations named in T1 and T2 (for example non-normal latent scores, "
             "or error in F that is not classical).")
    L.append("- **T2 (a) is a family, not a single model.** No grid point matched the spread of coupling, the across "
             "correlations and the within-university variance shares together in either country, so the verdict "
             "null (A1 case 2) carries more within-university variance than the data show; extra within variance "
             "that is uncorrelated between the two rankings lowers the null within correlation, so this works "
             "against the headline, and the share-consistent null is printed beside it (revision 1: it sits at the "
             "sampling floor of the spread, so it is effectively homogeneous; the verdict null is post hoc, A1). "
             "Under equal agreement the "
             "observed spread of field-level coupling is larger than loading heterogeneity alone produces at the "
             "observed variance shares." if (case["uk"] == 2 and case["us"] == 2) else
             "- **T2 (a) is a family, not a single model.** See the A1 case of each country in the table and the "
             "grid section.")
    c0n = ctx["c0_uk"]["nsum"]["pay-intake"]["mean"]
    bpi = {re_: (T2[f"uk_b{re_:+.1f}"]["pairs"]["pay-intake"]["mean"] if T2[f"uk_b{re_:+.1f}"]["ok"] else np.nan)
           for re_ in RHO_E}
    L.append("- **T2 (b).** The correlation is put on the cohort errors that the model has (the pay noise of a "
             "cohort's median and the deviation of the cohort's intake share from its latent mean); binomial noise "
             "and rounding dilute it (realised correlations in the table). The null mean of the pay–intake within "
             f"correlation is {f3(c0n)} under scripts/78's null and " +
             ", ".join(f"{f3(bpi[r_])} at ρ_e = {r_:+.1f}" for r_ in RHO_E) +
             "; positive ρ_e is therefore not a stress test for pay–intake, and REF–pay is affected only through the "
             "joint calibration.")
    L.append("- **T4.** The REF reliability is a test-retest correlation between the two exercises, so it is the same "
             "number whichever exercise is primary; real change between 2014 and 2021 counts as error. REF 2014's own "
             f"sample has {ctx['UKR']['uk14']['n']:,} programmes ({ctx['UKR']['uk14']['G']} providers) against "
             f"{ctx['UKR']['uk']['n']:,} ({ctx['UKR']['uk']['G']}) for REF 2021; the common sample has "
             f"{ctx['UKR']['uk14c']['n']:,} ({ctx['UKR']['uk14c']['G']}).")
    L.append("- **Not run (revision 1).** The size of the calibrated test when heterogeneous loadings and misspecified "
             "noise act together was not audited; T1 audits misspecified noise under homogeneous loadings, and T2 (a) "
             "runs heterogeneous nulls with the published noise.")
    L.append("- **Monte Carlo error.** A T1 size of 0.05 has a Monte Carlo SE of about 0.015 with M = 200, so the "
             "0.075 bound is about 1.7 SE above the nominal level; with B = 200 inner draws the inner p-value is "
             "itself coarse (steps of 1/201).")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    main()
