r"""scripts/85_positive_control_prediction.py -- referee analyses P1 (positive control: does the within-university
residual of the Wapman field rank F carry academic information, measured by the NRC (2010) research-doctorate data?)
and P2 (does F help predict a programme's log 4-year median pay out of sample, for a new university and within a
university?).

Dated 2026-11-17. The block between the PRESPEC marker lines is the binding text, copied verbatim
before any outcome was computed for this script. (A first copy, written to this file and to the result file before
the NRC file was downloaded, also carried a dating sentence and a one-line reminder that anything else is exploratory
inside the markers; both were moved outside the markers before any outcome was computed.) Anything not named in the
PRESPEC block is labelled exploratory. The block between the CHOICES marker lines records implementation choices made
the same day after reading the NRC workbook's Guide sheet and counting coverage (programmes, fields, universities,
matched cells; no correlation, R-squared or other outcome) and before the first outcome was computed. compute()
refuses to run if the SHA-256 of either block differs from PRESPEC_SHA256 / CHOICES_SHA256.

General rules: public data only; every number in POSITIVE_CONTROL_PREDICTION_RESULT.md is written by
this script from its own computations; seeded with numpy SeedSequence(85); byte-identical on a second run; existing
scripts imported, never edited; descriptive, non-causal language. Run:
  prlimit --as=2500000000 .venv/bin/python scripts/85_positive_control_prediction.py

-----BEGIN PRESPEC-----
P1 — Positive control: does department standing within a university carry academic information?
- Question: does the within-university residual of F predict an independent department-level academic outcome?
- If it does, the weak within-university agreement with pay is not because the residual indicator lacks signal.
- Preferred outcome: the National Research Council (2010) "A Data-Based Assessment of Research-Doctorate Programs" program-level data. It is a public Excel file from the National Academies / nap.edu. Use research measures such as publications per faculty, citations per publication, the share of faculty with grants, and the R or S ranking ranges.
  - Download it, add provenance (URL, date, md5) to data/raw/SOURCES.md, and map NRC fields to the Wapman fields.
  - Document the map and keep only clean matches.
- Design: university and field fixed effects. Use the same within statistic as G3, i.e. the correlation of FE residuals of normal scores.
  - Compute the within-university correlation of F with each NRC research measure, next to the across-university correlation and next to the within-university correlation of F with pay on the same cells.
- Rule: the "positive control passes" if the within-university correlation of F with the primary NRC research measure (publications per faculty, or the NRC R-ranking midpoint, whichever you name first) has a 95% university-cluster bootstrap CI above 0 and is larger than the within-university F–pay correlation on the same cells (paired bootstrap difference CI above 0).
- If NRC data cannot be obtained or matched for at least 10 fields, say so and stop P1. Do not substitute circular measures such as PhD production or hiring counts.

P2 — Out-of-sample prediction.
- Task: predict a programme's log 4-year median pay from information an applicant has. Use grouped cross-validation that holds out whole universities: 10 folds, repeated 5 times with seeded splits. Never estimate anything from the held-out university's pay.
- Model U (university information): field effects plus the university-level covariates G, SAT, admission rate, Pell share, control, state earnings level, and the university's mean pay in its OTHER fields in the training data.
  - The leave-field-out mean of the held-out university's other programmes is not allowed, because it would use held-out pay. Use only university-level covariates for held-out universities.
- Model U+D: U plus F, with field-specific slopes where estimable.
- Report the out-of-sample R² of both models, the gain from adding F, and a fold-bootstrap CI for the gain.
- Second task, within university (state its different question): hold out one programme at a time within universities that have at least 3 programmes. Predict its pay from the university's other programmes (their mean residual after field effects) plus field effects, with and without F. Report the R² gain.
- Rule: "department adds little out of sample" if the gain's upper bound is below 0.01 in R² on both tasks; otherwise report the gain size.

Rules:
- Public data only. Every number in the RESULT file is printed by the script. Seed with SeedSequence(85).
- Memory: run python under `prlimit --as=2500000000`, check `free -m` first, use at most 4 worker processes, and test small first. Run the final script twice to confirm byte-identical output.
-----END PRESPEC-----

-----BEGIN CHOICES-----
C0. Reproduction first. The script rebuilds, with the logic of scripts/paper_checks/c_headline.py and us_between.py
    (re-implemented here: c_headline.py runs and writes files when imported), the main-spec sample (3,961 programmes,
    214 universities, 53 fields) and the FE-only sample (4,645 / 251 / 55) on the 2026 Wapman release with the repaired
    name join, and asserts scripts/78's G3 US values on the main-spec cells (across +0.4477, within with university +
    field FE +0.0465) with the P1 code itself before any NRC number is computed.
C1. NRC file. data/raw/nrc2010/ResDocTableMac8_4-29-11.xls (the macro-free 'Excel 2008 for Mac' format of the revised
    4/29/2011 Excel data table; sheet 'Master', 5,004 programmes x 72 columns), md5 asserted at run time; the Windows
    workbook is read as well and its Master values asserted identical. Nothing is downloaded by the script. 'N/D' and
    'Not Ranked' are missing. No measure column used here carries the workbook's yellow imputation flag (only the
    columns for first-year full support and academic plans do).
C2. Measures. Primary, named first as the rule requires: publications per allocated faculty ('Average Number of
    Publications (2000-2006) per Allocated Faculty, 2006'). It is named rather than the R-ranking midpoint because,
    per the workbook's Guide sheet, the R and S rankings weight 20 characteristics that include the average number of
    PhDs graduated 2002-2006 and the share of graduates with academic plans, i.e. PhD production and academic
    placement, the circular measures the binding text excludes. Secondary (named in the binding text; reported, no rule):
    citations per publication (N/D in the humanities and computer science, so it has its own cells), share of faculty
    with grants, R-ranking midpoint and S-ranking midpoint ((5th + 95th percentile) / 2, sign reversed so that higher
    = better). Exploratory: midpoint of the research-activity dimensional ranking (built from the research
    characteristics only), awards per allocated faculty.
C3. Field map, one rule. Tier S (primary): the NRC field names the same discipline as the Wapman field and no part of
    it belongs to another field of the 107-field 2026 Wapman taxonomy. Tier L (exploratory, added to tier S): the NRC
    field contains the Wapman field's discipline but spans other Wapman fields or differs in scope (merged
    departments, wider or narrower names, umbrella programmes). The two lists, each mapping with its reason, are in
    NRC_FIELD_MAP; NRC fields with no field in the US pay cells are not mapped.
C4. Institution map. NRC 'Institution Name' (stripped) -> IPEDS UNITID: (a) exact match of the normalised name (upper
    case, '&' -> 'AND', non-alphanumerics -> space, tokens THE / AT / OF / AND / IN dropped) to exactly one normalised
    INSTNM of IPEDS HD2006 (the NRC data year 2005-06); (b) otherwise a hand-checked alias in NRC_ALIASES (HD2006
    name and city listed); (c) labels that join two or more institutions (joint programmes) are excluded; (d) UNITID ->
    university key through the Scorecard FoS INSTNM and the project normaliser (the join behind the US cells), one key
    per UNITID asserted, and no two NRC labels may share a key. NRC programmes whose website is on a campus with its
    own IPEDS UNITID (kumc.edu, University of Kansas Medical Center; hmc.psu.edu, Penn State Hershey College of
    Medicine) are excluded.
C5. Programme rule. A cell (university, Wapman field) is matched only if exactly one NRC programme of the mapped NRC
    field(s) at that university survives C4; cells with two or more are excluded. Exploratory: the allocated-faculty-
    weighted mean of each measure over the university's programmes in the field.
C6. P1 cells and statistic. Primary base: the FE-only sample (4,645): the statistic uses university and field fixed
    effects only, so the selectivity controls that define the main-spec sample are not needed, and requiring them
    drops the University of California campuses (SAT_AVG missing), which NRC covers. The main-spec base (3,961) is the
    named sensitivity. Per measure: base programmes with a tier-S clean match and the measure released, then
    scripts/58's sample rules re-applied (university >= 2 programmes, field >= 15 universities, iterated). Normal
    scores: Blom (midranks for ties) within field over these cells for F, log 4-year pay and the measure, standardised
    to mean 0 and SD 1 (ddof = 1) within field, computed once and held fixed in the bootstrap (as G3). Within =
    Pearson correlation of the residuals of the normal scores on university + field fixed effects; across = Pearson
    correlation of the within-field normal scores over all cells with field means removed (G3's across statistic).
    Reported per measure: within(F, measure), across(F, measure), within(F, pay) and across(F, pay) on the same cells,
    the paired difference within(F, measure) - within(F, pay), and (exploratory) within(measure, pay). Inference:
    2,000 university-cluster bootstrap draws (a university drawn k times enters with weight k; fixed effects re-fitted
    in every draw), 95% percentile intervals; SE = SD of the draws, MDE = 2.80 SE. The rule is applied to the primary
    measure on the primary base only.
C7. P2 task 1 (new university). Cells: the main-spec sample (3,961), with CONTROL and ST_EARN from scripts/55's
    load_institutions (imported, not edited; ST_EARN = leave-one-out mean log MD_EARN_WNE_P10 of the state's other
    predominantly-bachelor's institutions, so a university's own pay never enters its state level); programmes missing
    either are dropped and counted. y = log 4-year median. Model U: field dummies + G, SAT_AVG, ADM_RATE, PCTPELL,
    ST_EARN (each z-scored over the sample's universities) + a private-control dummy (CONTROL 2 or 3), common slopes.
    The university's mean pay in its other fields cannot be formed for a held-out university without its own pay;
    following the binding text's sub-bullet, held-out universities get the university-level covariates only, so this
    term enters task 2, where the other programmes are observed. Model U+D: U + z(F) x field dummy for every field with
    >= 15 training programmes, and one pooled z(F) slope for programmes in the other fields; z(F) = within-field
    z-score of F over the sample (F carries no pay). OLS on the training universities only. Folds: in repeat r (r = 0..4)
    the sorted universities are permuted with the r-th grandchild generator of SeedSequence(85)'s 'p2_splits' child,
    fold = position mod 10. R-squared (primary) = 1 - sum (y - yhat)^2 / sum (y - ybar)^2 over all programmes of a
    repeat, ybar = the sample mean; averaged over the 5 repeats; gain = R-squared(U+D) - R-squared(U). Fold bootstrap:
    2,000 draws; in each, every repeat's 10 folds are drawn with replacement, the gain is recomputed from the drawn
    folds' sums of squares (denominator included) and averaged over the repeats; 95% percentile interval.
    Exploratory: R-squared on the field-demeaned scale (denominator sum (y - field mean)^2), a common F slope, field-
    specific slopes on SAT_AVG, ADM_RATE, PCTPELL and G in both models (scripts/58's main design), and a university-
    cluster bootstrap of the held-out errors.
C8. P2 task 2 (a different question: given what a university's other departments pay, does a department's standing
    help predict its own pay?). Cells: main-spec programmes at universities with >= 3 programmes. For each held-out
    programme i, training = all other cells: field effects mu_f = mean log pay of the field's training programmes;
    r_j = y_j - mu_f(j); m_j = mean of r over the other training programmes of j's university (i excluded); without F:
    r_j = a + g m_j; with F: + z(F)_j x field dummy (fields with >= 15 training programmes; one pooled slope otherwise)
    + d zbar_j, zbar_j = mean z(F) over the same other programmes; OLS on the training cells; yhat_i = mu_f(i) + a +
    g m_i (+ the F terms), with m_i and zbar_i over all of i's university's other programmes. R-squared as in C7 over
    the held-out programmes (ybar = mean over the task-2 cells); gain; 95% interval from 2,000 university-cluster
    bootstrap draws of the held-out errors (predictions fixed). Exploratory: field-demeaned R-squared, a common F slope.
C9. Rules as written. P1 passes if the lower bound of within(F, publications per faculty) > 0 and the lower bound of the
    paired difference > 0 (primary base and map). P2: 'department adds little out of sample' if the upper bound of the
    gain interval is below 0.01 in both tasks; otherwise the gain sizes are reported. If fewer than 10 fields are
    matched under C3-C6, P1 stops and says so.
C10. Seeds and run. One child of numpy SeedSequence(85) per named analysis in a fixed order (names only appended), one
    grandchild per replicate or repeat. Single process, BLAS 1 thread. Outputs carry no timings, memory figures or run
    dates. Outputs: POSITIVE_CONTROL_PREDICTION_RESULT.md, data/interim/positive_control_prediction_summary.csv (every
    key number), data/interim/nrc_institution_map.csv (labels and UNITIDs only; no NRC values are written, since the
    data table may not be redistributed).
-----END CHOICES-----

REVISION 1 (2026-11-17; after the first, development-size run had been seen; outside the hashed blocks, which are
unchanged). (i) gens() rebuilds each analysis' replicate generators from its spawn key: SeedSequence.spawn is stateful,
so the exploratory task-1 variants had been given other fold splits than the primary model (every pre-specified
quantity used the first spawn of its own child, so its draws are unchanged). (ii) Task-2 variants that locate the gain
from F: F as the within-university deviation only; field-specific slopes on the other programmes' mean residual, with
F as in the primary model or as the deviation only. (iii) Task 1: field-specific selectivity slopes with one common F
slope. All are labelled rev. 1 and carry no rule.

REVISION 2 (2026-11-17; added after the results had been seen; outside the hashed blocks, which are
unchanged; every addition is post hoc and carries no rule; the pre-specified verdicts are kept). P1: a version that
controls the department's allocated faculty and PhD production; a version that drops programmes whose names carry a
merged or adjacent discipline (NAME_DROP_ALL / NAME_DROP_FIELD); four branch-campus hosts the C4 list missed are
excluded everywhere (none is in a same-name field, which is asserted); the scope of the P1 cells in the F
distribution. Tier S is called 'same-name fields' and tier L 'wider or merged fields' in the result file. P2: a
university-cluster bootstrap for every R-squared gain (the pre-specified fold-bootstrap row is kept and carries the
verdict); task-1 decomposition rows (field-specific G slopes, the mean F of the university's other programmes, the
department's within-university deviation); ridge versions with the penalty chosen by inner grouped CV; folds grouped by
OPEID6 (Rutgers campuses share earnings); the primary gain without ST_EARN; matching task-2 rows.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"                          # C10: single thread (prlimit + multi-thread OpenBLAS fails here)
os.environ["GAP_NAMEJOIN"] = "repaired"           # C0: the repaired Wapman-Scorecard name join
import re
import sys
import hashlib
import zipfile
import warnings
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, norm

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
sys.path.insert(0, str(ROOT))
from src.crosswalks import fields as Fx                                              # noqa: E402
from src.crosswalks.institutions import normalize_institution_name as norm_name     # noqa: E402

# Digests of the two blocks as released. As fixed on 2026-11-17 they were 3660a463d13f... (PRESPEC) and
# 0c56d57f6c5b... (CHOICES); for the public release one working instruction about file editing and commits was
# removed from PRESPEC and "the task" was replaced by "the binding text" in CHOICES.
PRESPEC_SHA256 = "bd4072ce3089aef715a07f689ec636a8e19e9bb2f9b59b4108802fc2c859a214"
CHOICES_SHA256 = "21703cdc7a1f799f86b8c97d7b19aec5dab52adc2ef17ed5ebb499cfe4331a6e"
SEED = 85
B = int(os.environ.get("GAP85_B", "2000"))        # development shortcut only; reported runs do not set GAP85_B
Z975 = 1.959963984540054
MDE_K = Z975 + 0.8416212335729143                 # 2.80
NRC_DIR = RAW / "nrc2010"
NRC_FILE = NRC_DIR / "ResDocTableMac8_4-29-11.xls"
NRC_WIN = NRC_DIR / "ResDocTableWin_4-29-11.xls"
NRC_MD5 = {NRC_FILE.name: "b0d74e43c33d0e9eadf561296468a619", NRC_WIN.name: "7778874192f287cdf41d20bafc55a716"}
OUT_MD = ROOT / "POSITIVE_CONTROL_PREDICTION_RESULT.md"
OUT_CSV = ROOT / "data" / "interim" / "positive_control_prediction_summary.csv"
OUT_MAP = ROOT / "data" / "interim" / "nrc_institution_map.csv"
NMIN_FIELD = 15                                   # scripts/58: a field needs >= 15 universities
EST_MIN = 15                                      # C7 / C8: field-specific F slope if >= 15 training programmes
P2_FOLDS, P2_REPEATS = 10, 5

# one SeedSequence(85) child per named analysis, fixed order (names only appended)
ANALYSES = ["p1_pubs", "p1_cites", "p1_grants", "p1_rmid", "p1_smid", "p1_ramid", "p1_awards",
            "p1_pubs_main", "p1_pubs_tierL", "p1_pubs_wmean",
            "p2_splits", "p2_foldboot", "p2_t1_uboot", "p2_t2_uboot",
            # revision 2 (appended: earlier children and draws unchanged)
            "p1_pubs_ctrl", "p1_pubs_clean", "p2_ridge_inner", "p2_splits_opeid6", "p2_t1_oboot",
            "p1_pubs_clean2"]
_KIDS = dict(zip(ANALYSES, np.random.SeedSequence(SEED).spawn(len(ANALYSES))))


def gens(name: str, n: int) -> list:
    """Grandchildren 0..n-1 of the analysis' child, built from its spawn key so that every call returns the same
    generators (SeedSequence.spawn is stateful; revision 1, see the result file)."""
    kid = _KIDS[name]
    return [np.random.default_rng(np.random.SeedSequence(kid.entropy, spawn_key=kid.spawn_key + (j,)))
            for j in range(n)]


def _block(begin: str, end: str) -> str:
    return __doc__.split(begin + "\n", 1)[1].split(end, 1)[0]


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def blom(x: np.ndarray) -> np.ndarray:
    """Rank-normal (Blom) scores, midranks for ties (scripts/78)."""
    r = rankdata(x)
    return norm.ppf((r - 0.375) / (len(x) + 0.25))


def ns_within(v: np.ndarray, grp: np.ndarray) -> np.ndarray:
    """Blom scores within group, standardised to mean 0, SD 1 (ddof = 1) within the group (scripts/78 ns_within)."""
    out = np.empty(len(v))
    for k in np.unique(grp):
        ix = np.flatnonzero(grp == k)
        b = blom(v[ix])
        out[ix] = (b - b.mean()) / b.std(ddof=1)
    return out


def summ(est, bs) -> dict:
    bs = np.asarray(bs, float)
    ok = np.isfinite(bs)
    se = float(np.std(bs[ok], ddof=1))
    return dict(est=float(est), lo=float(np.percentile(bs[ok], 2.5)), hi=float(np.percentile(bs[ok], 97.5)),
                se=se, mde=MDE_K * se, nfail=int((~ok).sum()))


def fe_rules(df: pd.DataFrame, ukey: str = "inst_key") -> pd.DataFrame:
    """scripts/58 fe_sample rules: university >= 2 programmes, field >= 15 universities, iterated."""
    d = df
    while True:
        n0 = len(d)
        d = d[d.groupby(ukey).field.transform("size") >= 2]
        d = d[d.groupby("field")[ukey].transform("size") >= NMIN_FIELD]
        if len(d) == n0:
            return d


# =============================================================================================================
# C0: US cells (scripts/paper_checks/c_headline.py and us_between.py, re-implemented)
# =============================================================================================================
def build_us() -> dict:
    cw24 = _load("cw24", "24_crosswalk_audit.py")
    fields66 = Fx.ALL_FIELDS + cw24.RECOVER
    wf2key = {f["wapman_field"]: f["key"] for f in fields66}
    cip2key = {}
    for f in fields66:
        for c in f["cip4"]:
            cip2key[c] = f["key"]
    ist = pd.read_csv(RAW / "wapman2026/institution-stats.csv")
    v1r = pd.read_csv(RAW / "wapman2022_v1/ranks.csv")
    v1e = pd.read_csv(RAW / "wapman2022_v1/edge_lists.csv")
    v1n = pd.concat([v1r[["InstitutionId", "InstitutionName"]], v1e[["InstitutionId", "InstitutionName"]],
                     v1e[["DegreeInstitutionId", "DegreeInstitutionName"]].set_axis(["InstitutionId", "InstitutionName"],
                                                                                   axis=1)]).dropna()
    v1n = v1n.assign(InstitutionId=v1n.InstitutionId.astype(int)).drop_duplicates("InstitutionId")
    v1n = v1n.set_index("InstitutionId").InstitutionName
    ist["name"] = [v1n.get(i, n) for i, n in zip(ist.InstitutionId, ist.InstitutionName)]
    ist["inst_key"] = ist.name.map(norm_name)
    fr = ist[(ist.TaxonomyLevel == "Field") & ist.TaxonomyValue.isin(wf2key)].copy()
    fr["field"] = fr.TaxonomyValue.map(wf2key)
    fr["F"] = -fr.OrdinalPrestigeRank.astype(float)
    assert not fr.duplicated(["inst_key", "field"]).any()
    ac = ist[ist.TaxonomyLevel == "Academia"][["inst_key", "OrdinalPrestigeRank"]]
    ac = ac.assign(G=-ac.OrdinalPrestigeRank.astype(float))
    fos_all = pd.read_csv(RAW / "scorecard_fos/Most-Recent-Cohorts-Field-of-Study.csv",
                          usecols=["UNITID", "INSTNM", "CIPCODE", "CREDLEV", "EARN_MDN_4YR", "EARN_COUNT_WNE_4YR"],
                          dtype=str)
    names = fos_all[["UNITID", "INSTNM"]].drop_duplicates()
    names = names.assign(inst_key=names.INSTNM.map(norm_name))
    u2k = names.groupby("UNITID").inst_key.agg(lambda s: sorted(set(s)))
    assert (u2k.map(len) == 1).all(), "a UNITID with two university keys"
    u2k = u2k.map(lambda s: s[0])
    fos = fos_all[fos_all.CREDLEV == "3"].copy()
    del fos_all
    fos["field"] = fos.CIPCODE.str.zfill(4).map(cip2key)
    fos = fos[fos.field.notna()].copy()
    fos["earn"] = pd.to_numeric(fos.EARN_MDN_4YR, errors="coerce")
    fos = fos.dropna(subset=["earn"])
    fos["w"] = pd.to_numeric(fos.EARN_COUNT_WNE_4YR, errors="coerce").fillna(1.0).clip(lower=1.0)
    fos["inst_key"] = fos.INSTNM.map(norm_name)
    fos["we"] = fos.earn * fos.w
    er = fos.groupby(["field", "inst_key"], sort=False).agg(UNITID=("UNITID", "first"), we=("we", "sum"),
                                                            ws=("w", "sum")).reset_index()
    er["earnings"] = er.we / er.ws
    inst = pd.read_csv(RAW / "scorecard_inst/Most-Recent-Cohorts-Institution.csv",
                       usecols=["UNITID", "SAT_AVG", "ADM_RATE", "PCTPELL"], dtype=str)
    for c in ["SAT_AVG", "ADM_RATE", "PCTPELL"]:
        inst[c] = pd.to_numeric(inst[c], errors="coerce")
    cells = fr[["inst_key", "field", "F"]].merge(er[["inst_key", "field", "UNITID", "earnings"]],
                                                 on=["inst_key", "field"], how="inner")
    cells = cells.merge(inst, on="UNITID", how="left").merge(ac[["inst_key", "G"]], on="inst_key", how="left")
    d = cells.dropna(subset=["earnings", "F", "SAT_AVG", "ADM_RATE", "PCTPELL", "G"])
    d = fe_rules(d[d.earnings > 0])
    d = d.sort_values(["field", "inst_key"]).reset_index(drop=True)
    f = cells.dropna(subset=["earnings", "F"])
    f = fe_rules(f[f.earnings > 0]).sort_values(["field", "inst_key"]).reset_index(drop=True)
    shape = lambda x: (len(x), x.inst_key.nunique(), x.field.nunique())   # noqa: E731
    assert shape(d) == (3961, 214, 53), shape(d)
    assert shape(f) == (4645, 251, 55), shape(f)
    for x in (d, f):
        x["ly"] = np.log(x.earnings.to_numpy())
    return dict(main=d, fe=f, u2k=u2k)


# =============================================================================================================
# C1-C5: NRC data table, field map, institution map, programme rule
# =============================================================================================================
PUBS = "Average Number of Publications (2000-2006) per Allocated Faculty, 2006"
CITES = "Average Citations per Publication"
GRANTS = "Percent of Faculty with Grants, 2006"
AWARDS = "Awards per Allocated Faculty Member, 2006"
ALLOC = "Number of Allocated Faculty, 2006"
RANGES = {"R": ("R Rankings: 5th Percentile", "R Rankings: 95th Percentile"),
          "S": ("S Rankings: 5th Percentile", "S Rankings: 95th Percentile"),
          "RA": ("Research Activity: 5th Percentile", "Research Activity: 95th Percentile")}
# key -> (label, status); status: pre = the rule's primary measure; named = named in the binding text; expl.
MEASURES = {"pubs": ("publications per allocated faculty", "pre"),
            "cites": ("citations per publication", "named"),
            "grants": ("share of faculty with grants", "named"),
            "rmid": ("R-ranking midpoint (sign reversed)", "named"),
            "smid": ("S-ranking midpoint (sign reversed)", "named"),
            "ramid": ("research-activity ranking midpoint (sign reversed)", "expl."),
            "awards": ("awards per allocated faculty", "expl.")}

# C3: NRC field -> (US field key, tier, reason). Tier S = same discipline, no part in another Wapman field.
NRC_FIELD_MAP = [
    ("Computer Sciences", "computer_science", "S", "same discipline"),
    ("Mathematics", "mathematics", "S", "same discipline (NRC Applied Mathematics is a separate NRC field)"),
    ("Statistics and Probability", "statistics", "S",
     "same name; a few NRC biostatistics programmes sit here too (most are in NRC Public Health; Wapman has a "
     "separate Biostatistics field; count in the P1 detail)"),
    ("Computer Engineering", "computer_engineering", "S", "same discipline"),
    ("Mechanical Engineering", "mechanical_engineering", "S", "same discipline"),
    ("Chemical Engineering", "chemical_engineering", "S", "same discipline"),
    ("Aerospace Engineering", "aerospace_engineering", "S", "same discipline"),
    ("Biomedical Engineering and Bioengineering", "biomedical_engineering", "S", "same discipline"),
    ("Materials Science and Engineering", "materials_science", "S", "same discipline (Wapman 'Materials Engineering')"),
    ("Physics", "physics", "S", "same discipline (astronomy separate on both sides)"),
    ("Chemistry", "chemistry", "S", "same discipline"),
    ("Microbiology", "microbiology", "S", "same discipline (immunology separate on both sides)"),
    ("Physiology", "physiology", "S", "same discipline"),
    ("Nutrition", "nutrition", "S", "same discipline (Wapman 'Nutrition Sciences')"),
    ("Food Science", "food_science", "S", "same discipline"),
    ("Forestry and Forest Sciences", "forestry", "S", "same discipline (Wapman 'Forestry and Forest Resources')"),
    ("Nursing", "nursing", "S", "same discipline"),
    ("English Language and Literature", "english", "S", "same discipline"),
    ("History", "history", "S", "same discipline"),
    ("Philosophy", "philosophy", "S", "same discipline"),
    ("Economics", "economics", "S", "same discipline (agricultural economics separate on both sides)"),
    ("Political Science", "political_science", "S", "same discipline"),
    ("Sociology", "sociology", "S", "same discipline"),
    ("Anthropology", "anthropology", "S", "same discipline"),
    ("Linguistics", "linguistics", "S", "same discipline"),
    ("Geography", "geography", "S", "same discipline"),
    ("Psychology", "psychology", "S", "same discipline"),
    ("Electrical and Computer Engineering", "electrical_engineering", "L",
     "merged field: also covers Wapman Computer Engineering"),
    ("Civil and Environmental Engineering", "civil_engineering", "L",
     "merged field: also covers Wapman Environmental Engineering"),
    ("Operations Research, Systems Engineering and Industrial Engineering", "industrial_engineering", "L",
     "merged field: also covers Wapman Operations Research and Systems Engineering"),
    ("Biochemistry, Biophysics, and Structural Biology", "biochemistry", "L",
     "merged field: also covers Wapman Biophysics"),
    ("Public Health", "public_health", "L",
     "holds epidemiology, biostatistics and environmental-health programmes (separate Wapman fields)"),
    ("Animal Sciences", "animal_sciences", "L", "holds zoology and wildlife / fisheries programmes"),
    ("Earth Sciences", "earth_sciences", "L", "Wapman 'Geology'; the NRC field is wider (geophysics, geochemistry)"),
    ("Spanish and Portuguese Language and Literature", "spanish", "L", "adds Portuguese"),
    ("Music (except performance)", "music", "L", "excludes performance programmes"),
    ("Kinesiology", "kinesiology", "L", "the Wapman field is wider ('Exercise Science, Kinesiology, Rehab, Health')"),
    ("Theatre and Performance Studies", "theatre", "L",
     "Wapman 'Theatre Literature, History and Criticism'; adds performance studies"),
    ("Biology/Integrated Biology/Integrated Biomedical Sciences", "biology", "L",
     "holds medical-school umbrella programmes as well as general biology"),
    ("Plant Sciences", "agronomy", "L", "spans Wapman Agronomy, Horticulture, Plant Pathology and Plant Sciences"),
]

# C4 (b): hand-checked aliases, NRC label -> (HD2006 UNITID, HD2006 INSTNM, HD2006 CITY); asserted against HD2006
NRC_ALIASES = {
    "ARIZONA STATE UNIVERSITY": ("104151", "Arizona State University at the Tempe Campus", "Tempe"),
    "AUBURN UNIVERSITY": ("100858", "Auburn University Main Campus", "Auburn University"),
    "BOWLING GREEN STATE UNIVERSITY": ("201441", "Bowling Green State University-Main Campus", "Bowling Green"),
    "CITY UNIVERSITY OF NEW YORK GRAD. CENTER": ("190576", "CUNY Graduate School and University Center", "New York"),
    "GEORGIA INSTITUTE OF TECHNOLOGY": ("139755", "Georgia Institute of Technology-Main Campus", "Atlanta"),
    "KENT STATE UNIVERSITY MAIN CAMPUS": ("203517", "Kent State University-Kent Campus", "Kent"),
    "MIAMI UNIVERSITY": ("204024", "Miami University-Oxford", "Oxford"),
    "MT. SINAI SCHOOL OF MEDICINE": ("193405", "Mount Sinai School of Medicine", "New York"),
    "NORTH CAROLINA STATE UNIVERSITY": ("199193", "North Carolina State University at Raleigh", "Raleigh"),
    "PENN STATE UNIVERSITY": ("214777", "Pennsylvania State University-Penn State Main Campus", "University Park"),
    "RUTGERS THE STATE UNIVERSITY OF NEW JERSEY NEW BRUNSWICK CAMPUS":
        ("186380", "Rutgers University-New Brunswick/Piscataway", "New Brunswick"),
    "RUTGERS THE STATE UNIVERSITY OF NEW JERSEY NEWARK CAMPUS": ("186399", "Rutgers University-Newark", "Newark"),
    "STATE UNIVERSITY OF NEW YORK AT ALBANY": ("196060", "SUNY at Albany", "Albany"),
    "STATE UNIVERSITY OF NEW YORK AT BINGHAMTON": ("196079", "SUNY at Binghamton", "Binghamton"),
    "STATE UNIVERSITY OF NEW YORK AT BUFFALO": ("196088", "SUNY at Buffalo", "Buffalo"),
    "STATE UNIVERSITY OF NEW YORK AT STONY BROOK": ("196097", "Stony Brook University", "Stony Brook"),
    "SYRACUSE UNIVERSITY MAIN CAMPUS": ("196413", "Syracuse University", "Syracuse"),
    "TULANE UNIVERSITY": ("160755", "Tulane University of Louisiana", "New Orleans"),
    "UNIVERSITY OF AKRON": ("200800", "University of Akron Main Campus", "Akron"),
    "UNIVERSITY OF COLORADO DENVER (UNIVERSITY OF COLORADO AT DENVER AND HEALTH SCIENCES CENTER)":
        ("126562", "University of Colorado at Denver and Health Sciences Center", "Denver"),
    "UNIVERSITY OF KANSAS": ("155317", "University of Kansas Main Campus", "Lawrence"),
    "UNIVERSITY OF MASSACHUSETTS AT WORCESTER":
        ("166708", "University of Massachusetts Medical School Worcester", "Worcester"),
    "UNIVERSITY OF MISSISSIPPI": ("176017", "University of Mississippi Main Campus", "University"),
    "UNIVERSITY OF MISSOURI - SAINT LOUIS": ("178420", "University of Missouri-St Louis", "Saint Louis"),
    "UNIVERSITY OF MONTANA - MISSOULA": ("180489", "The University of Montana", "Missoula"),
    "UNIVERSITY OF NEW HAMPSHIRE": ("183044", "University of New Hampshire-Main Campus", "Durham"),
    "UNIVERSITY OF NORTH DAKOTA MAIN CAMPUS": ("200280", "University of North Dakota", "Grand Forks"),
    "UNIVERSITY OF PITTSBURGH PITTSBURGH CAMPUS": ("215293", "University of Pittsburgh-Main Campus", "Pittsburgh"),
    "UNIVERSITY OF TOLEDO": ("206084", "University of Toledo-Main Campus", "Toledo"),
    "UNIVERSITY OF VIRGINIA": ("234076", "University of Virginia-Main Campus", "Charlottesville"),
    "UNIVERSITY OF WASHINGTON": ("236948", "University of Washington-Seattle Campus", "Seattle"),
}
# C4 (c): labels that join two or more institutions (joint programmes)
NRC_JOINT = [
    "GEORGIA INSTITUTE OF TECHNOLOGY - EMORY UNIVERSITY",
    "GEORGIA STATE UNIVERSITY / GEORGIA TECH",
    "RUTGERS-NEW BRUNSWICK AND UNIVERSITY OF MEDICINE AND DENTISTRY OF NEW JERSEY-PISCATAWAY",
    "SAN DIEGO STATE UNIVERSITY-UNIVERSITY OF CALIFORNIA DAVIS",
    "SAN DIEGO STATE UNIVERSITY-UNIVERSITY OF CALIFORNIA SAN DIEGO",
    "SAN DIEGO STATE UNIVERSITY-UNIVERSITY OF CALIFORNIA SANTA BARBARA",
    "THE UNIVERSITY OF ALABAMA AT BIRMINGHAM (UAB)/THE UNIVERSITY OF ALABAMA IN HUNTSVILLE (UAH)",
    "UC BERKELEY/UC SAN FRANCISCO",
    "UC IRVINE - UC RIVERSIDE - UC SAN DIEGO",
    "UC IRVINE - UC SAN DIEGO",
    "UNIVERSITY OF ALABAMA AT BIRMINGHAM (UAB)/THE UNIVERSITY OF ALABAMA IN HUNTSVILLE (UAH))/UNIVERSITY OF ALABAMA (UA)",
    "UNIVERSITY OF MARYLAND BALTIMORE COUNTY/UNIV. MD BALTIMORE/UNIV. MD EASTERN SHORE/UNIV. MD COLLEGE PARK",
    "UNIVERSITY OF MARYLAND BALTIMORE COUNTY/UNIVERSITY OF MARYLAND BALTIMORE",
    "UNIVERSITY OF TEXAS HLTH SCI CNTR. AT HOUSTON\\UNIV. OF TEXAS M.D. ANDERSON CANCER CNTR.(UTHSCH\\UTMDACC)",
]
# C4: programme websites on a campus with its own IPEDS UNITID (HD2006)
SEPARATE_CAMPUS_HOSTS_C4 = {"kumc.edu": ("155326", "University of Kansas Medical Center"),
                            "hmc.psu.edu": ("214616",
                                            "Pennsylvania State University-Penn State Hershey College of Medicine")}
# revision 2: four branch campuses the C4 list missed (found by an independent check), each a separate HD2006 UNITID
SEPARATE_CAMPUS_HOSTS = dict(SEPARATE_CAMPUS_HOSTS_C4, **{
    "hbg.psu.edu": ("214713", "Pennsylvania State University-Penn State Harrisburg"),
    "healthsciences.okstate.edu": ("207315", "Oklahoma State University Center for Health Sciences"),
    "hsc.unt.edu": ("228909", "University of North Texas Health Science Center"),
    "hsc.utoledo.edu": ("203951", "University of Toledo-Health Science Campus")})
# revision 2: NRC programme names that carry a merged or adjacent discipline (a list for all fields, plus
# field-specific names); in aerospace engineering only names merged with mechanical engineering or biomedicine count
NAME_DROP_ALL = (r"aerospace|aeronaut|astronom|immunol|patholog|industrial|ocean|information|health|medical|ideas|"
                 r"biological anthropology|comparative|exercise|biochem|biomolecular|biological eng|environmental|cell|"
                 r"molecular|genetic|decision|management|foods|interdepartmental|international")
NAME_DROP_FIELD = {"computer_science": r"computer engineering|computational science", "economics": r"business",
                   "sociology": r"anthropology", "mechanical_engineering": r"materials science|engineering \(other\)",
                   "biomedical_engineering": r"biosystems", "chemical_engineering": r"paper and imaging"}


def name_flag(field: str, name: str) -> bool:
    n = str(name).lower()
    if field == "aerospace_engineering":
        return re.search(r"mechanic(?:al)? eng|biomed", n) is not None
    if re.search(NAME_DROP_ALL, n):
        return True
    extra = NAME_DROP_FIELD.get(field)
    return extra is not None and re.search(extra, n) is not None


def host_match(h: str, hosts) -> bool:
    return any(h == x or h.endswith("." + x) for x in hosts)


def nz(s: str) -> str:
    s = s.upper().replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    return " ".join(t for t in s.split() if t not in {"THE", "AT", "OF", "AND", "IN"})


def read_master(path: Path) -> pd.DataFrame:
    m = pd.read_excel(path, sheet_name="Master", engine="xlrd")
    m.columns = [" ".join(str(c).split()) for c in m.columns]
    return m


def nrc_load() -> dict:
    for p in (NRC_FILE, NRC_WIN):
        assert _md5(p) == NRC_MD5[p.name], f"md5 of {p.name} differs from the data/sources.csv record"
    m = read_master(NRC_FILE)
    w = read_master(NRC_WIN)
    assert m.shape == w.shape == (5004, 72)
    same = 0
    for a, b in zip(m.columns, w.columns):
        sa, sb = m[a].astype(str).str.strip(), w[b].astype(str).str.strip()
        va, vb = pd.to_numeric(sa, errors="coerce"), pd.to_numeric(sb, errors="coerce")
        assert ((sa == sb) | np.isclose(va, vb, rtol=1e-12, atol=0)).all(), f"Master column {a} differs"
        same += 1
    hdr_diff = int(sum(a != b for a, b in zip(m.columns, w.columns)))
    del w
    m["inst"] = m["Institution Name"].astype(str).str.strip()
    m["host"] = (m["Program Website"].astype(str).str.strip().str.lower()
                 .str.replace(r"^https?://", "", regex=True).str.split("/").str[0])
    num = lambda c: pd.to_numeric(m[c].astype(str).str.strip(), errors="coerce")   # noqa: E731
    m["pubs"], m["cites"], m["grants"], m["awards"], m["alloc"] = num(PUBS), num(CITES), num(GRANTS), num(AWARDS), \
        num(ALLOC)
    m["phds"] = num("Average Number of Ph.D.s Graduated, 2002-2006")      # revision 2: a control only
    for k, (c5, c95) in RANGES.items():
        m[k.lower() + "mid"] = -(num(c5) + num(c95)) / 2.0
    info = dict(n_prog=len(m), n_fields=int(m.Field.nunique()), n_labels=int(m.inst.nunique()), same_cols=same,
                hdr_diff=hdr_diff, n_unranked=int(num(RANGES["R"][0]).isna().sum()),
                n_cites_nd=int(m.cites.isna().sum()))
    return dict(m=m, info=info)


def nrc_institutions(m: pd.DataFrame, u2k: pd.Series) -> tuple[pd.DataFrame, dict]:
    with zipfile.ZipFile(RAW / "ipeds_hd/HD2006.zip") as z:
        hd = pd.read_csv(z.open("hd2006.csv"), encoding="latin-1", dtype=str)
    hd["k"] = hd.INSTNM.map(nz)
    byk = hd.groupby("k").UNITID.agg(list)
    hd_name = dict(zip(hd.UNITID, hd.INSTNM))
    hd_city = dict(zip(hd.UNITID, hd.CITY))
    for lab, (u, nm, city) in NRC_ALIASES.items():
        assert hd_name.get(u) == nm and hd_city.get(u) == city, f"alias {lab}: HD2006 has {hd_name.get(u)}"
    for host, (u, nm) in SEPARATE_CAMPUS_HOSTS.items():
        assert hd_name.get(u) == nm, host
    labels = sorted(m.inst.unique())
    assert set(NRC_JOINT) <= set(labels) and len(NRC_JOINT) == 14
    rows = []
    for lab in labels:
        if lab in NRC_JOINT:
            rows.append((lab, None, "joint programme label (excluded)"))
            continue
        if lab in NRC_ALIASES:
            rows.append((lab, NRC_ALIASES[lab][0], "hand-checked alias"))
            continue
        u = byk.get(nz(lab), [])
        if len(u) == 1:
            rows.append((lab, u[0], "exact normalised HD2006 name"))
        else:
            rows.append((lab, None, f"unmatched ({len(u)} HD2006 names)"))
    im = pd.DataFrame(rows, columns=["nrc_label", "UNITID", "how"])
    im["hd2006_name"] = im.UNITID.map(hd_name)
    im["inst_key"] = im.UNITID.map(u2k)
    k = im.dropna(subset=["inst_key"])
    assert not k.inst_key.duplicated().any(), "two NRC labels on one university key"
    st = dict(n_labels=len(im), n_auto=int((im.how == "exact normalised HD2006 name").sum()),
              n_alias=int((im.how == "hand-checked alias").sum()), n_joint=int((im.how.str.startswith("joint")).sum()),
              n_unmatched=int(im.how.str.startswith("unmatched").sum()), n_key=int(im.inst_key.notna().sum()),
              unmatched=sorted(im.loc[im.how.str.startswith("unmatched"), "nrc_label"]))
    return im, st


def nrc_cells(m: pd.DataFrame, im: pd.DataFrame, tiers: tuple, rule: str,
              hosts=None) -> tuple[pd.DataFrame, dict]:
    """Per (inst_key, field): the NRC measures under the field tiers and the programme rule (C3-C5)."""
    hosts = SEPARATE_CAMPUS_HOSTS if hosts is None else hosts
    fmap = {}
    for nf, key, tier, _ in NRC_FIELD_MAP:
        if tier in tiers:
            hits = [f for f in m.Field.unique() if f == nf or (nf.startswith("Biology/") and f.startswith(nf))]
            assert len(hits) == 1, nf
            fmap[hits[0]] = key
    x = m.merge(im[["nrc_label", "inst_key", "UNITID"]], left_on="inst", right_on="nrc_label", how="left")
    x["field"] = x.Field.map(fmap)
    x = x[x.field.notna() & x.inst_key.notna()].copy()
    # a host counts only where its campus is not the label's own UNITID (revision 2: UNT HSC's own programmes)
    sep = pd.Series([any(host_match(h, [hx]) and hu != u for hx, (hu, _) in hosts.items())
                     for h, u in zip(x.host, x.UNITID)], index=x.index)
    n_sep = int(sep.sum())
    x = x[~sep]
    cnt = x.groupby(["inst_key", "field"]).size().rename("nprog")
    x = x.merge(cnt.reset_index(), on=["inst_key", "field"])
    mk = list(MEASURES) + ["alloc", "phds"]
    if rule == "one":
        out = x[x.nprog == 1][["inst_key", "field", "Program Name"] + mk].rename(columns={"Program Name": "pname"})
    else:
        def wm(g):
            w = g.alloc.fillna(0).clip(lower=0).to_numpy()
            r = {}
            for c in mk:
                v = g[c].to_numpy(float)
                ok = np.isfinite(v) & (w > 0)
                r[c] = float((w[ok] * v[ok]).sum() / w[ok].sum()) if ok.any() else np.nan
            return pd.Series(r)
        out = x.groupby(["inst_key", "field"]).apply(wm).reset_index()
    st = dict(n_sep=n_sep, n_cells_any=int(len(cnt)), n_cells_one=int((cnt == 1).sum()),
              n_cells_multi=int((cnt > 1).sum()))
    return out.sort_values(["inst_key", "field"]).reset_index(drop=True), st


# =============================================================================================================
# C6: P1 statistic (G3's: correlations of university + field FE residuals of within-field normal scores)
# =============================================================================================================
def p1_prep(c: pd.DataFrame, cols: list, ctrl=()) -> dict:
    c = c.sort_values(["field", "inst_key"]).reset_index(drop=True)
    g = pd.factorize(c.inst_key, sort=True)[0]
    fc = pd.factorize(c.field, sort=True)[0]
    G, K = int(g.max() + 1), int(fc.max() + 1)
    fa = c.field.to_numpy()
    Z = np.column_stack([ns_within(c[k].to_numpy(float), fa) for k in cols])
    cnt = np.bincount(g, minlength=G).astype(float)

    def dm(M):
        s = np.zeros((G, M.shape[1]))
        np.add.at(s, g, M)
        return M - (s / cnt[:, None])[g]
    X = np.eye(K)[fc][:, 1:]                       # field FE (first field = reference)
    if ctrl:                                       # revision 2: within-field normal scores of control variables
        X = np.hstack([X, np.column_stack([ns_within(c[k].to_numpy(float), fa) for k in ctrl])])
    Zd, Xd = dm(Z), dm(X)
    idx = [np.flatnonzero(g == k) for k in range(G)]
    A = np.stack([Xd[r].T @ Xd[r] for r in idx])
    Bm = np.stack([Xd[r].T @ Zd[r] for r in idx])
    S = np.stack([Zd[r].T @ Zd[r] for r in idx])
    return dict(c=c, g=g, fc=fc, G=G, K=K, Z=Z, A=A, Bm=Bm, S=S, cols=cols, shape=(len(c), G, K))


def p1_stats(P: dict, cw: np.ndarray) -> np.ndarray:
    """Within and across correlation matrices for university weights cw (ones = point estimate)."""
    XtX = np.tensordot(cw, P["A"], axes=1)
    keep = np.diag(XtX) > 1e-10
    Q = np.linalg.pinv(XtX[np.ix_(keep, keep)], rcond=1e-10, hermitian=True)
    Bt = np.tensordot(cw, P["Bm"], axes=1)[keep]
    R = np.tensordot(cw, P["S"], axes=1) - Bt.T @ Q @ Bt
    w = cw[P["g"]]
    fc, K, Z = P["fc"], P["K"], P["Z"]
    sw = np.bincount(fc, w, K)
    okf = sw > 0
    mz = np.stack([np.where(okf, np.bincount(fc, w * Z[:, j], K) / np.where(okf, sw, 1.0), 0.0)
                   for j in range(Z.shape[1])], axis=1)
    a = Z - mz[fc]
    C = (w[:, None] * a).T @ a
    dR, dC = np.sqrt(np.diag(R)), np.sqrt(np.diag(C))
    return np.stack([R / np.outer(dR, dR), C / np.outer(dC, dC)])


def p1_run(c: pd.DataFrame, name: str, ctrl=()) -> dict:
    """cols = F, log pay, measure. Point estimates and B university-cluster draws (C6)."""
    P = p1_prep(c, ["F", "ly", "meas"], ctrl)
    pt = p1_stats(P, np.ones(P["G"]))
    G = P["G"]
    bs = np.empty((B, 2, 3, 3))
    for b, rng in enumerate(gens(name, B)):
        cw = np.bincount(rng.integers(0, G, G), minlength=G).astype(float)
        bs[b] = p1_stats(P, cw)
    res = {}
    for lev, li in (("w", 0), ("a", 1)):
        for nm, (i, j) in (("FN", (0, 2)), ("FY", (0, 1)), ("NY", (2, 1))):
            res[f"{lev}_{nm}"] = summ(pt[li, i, j], bs[:, li, i, j])
    res["diff"] = summ(pt[0, 0, 2] - pt[0, 0, 1], bs[:, 0, 0, 2] - bs[:, 0, 0, 1])
    res["shape"] = P["shape"]
    res["fields"] = P["c"].groupby("field").size().sort_index()
    return res


def p1_cells(base: pd.DataFrame, nrc: pd.DataFrame, meas: str, need=()) -> pd.DataFrame:
    keep = ["inst_key", "field", meas] + [k for k in need if k != meas]
    x = base[["inst_key", "field", "F", "ly"]].merge(nrc[keep], on=["inst_key", "field"], how="inner")
    x = x.rename(columns={meas: "meas"})
    ok = np.isfinite(x.meas.to_numpy(float))
    for k in need:
        ok &= np.isfinite(x[k].to_numpy(float))
    return fe_rules(x[ok])


# =============================================================================================================
# C7: P2 task 1 -- grouped cross-validation over universities (revision 2: term-based designs, ridge, OPEID6 folds)
# =============================================================================================================
def zwithin(v: np.ndarray, fc: np.ndarray) -> np.ndarray:
    out = np.empty(len(v))
    for k in np.unique(fc):
        ix = fc == k
        out[ix] = (v[ix] - v[ix].mean()) / v[ix].std(ddof=1)
    return out


def others_mean(v: np.ndarray, g: np.ndarray, G: int) -> np.ndarray:
    """Mean of v over the other programmes of the same university (uses no pay when v carries none)."""
    s, c = np.bincount(g, v, G), np.bincount(g, minlength=G).astype(float)
    return (s[g] - v) / (c[g] - 1)


COV6 = ["G", "SAT_AVG", "ADM_RATE", "PCTPELL", "ST_EARN", "private"]
# name -> (terms added to field dummies + covariates, status)
T1_MODELS = {"U": ((), "pre"), "UD": (("fF",), "pre"), "UDc": (("cF",), "expl. (C)"),
             "Ufc": (("fcov",), "expl. (C)"), "Ufc+fF": (("fcov", "fF"), "expl. (C)"),
             "Ufc+cF": (("fcov", "cF"), "rev. 1 (post hoc)"),
             "UfG": (("fG",), "rev. 2 (post hoc)"), "UfG+fF": (("fG", "fF"), "rev. 2 (post hoc)"),
             "U+fzb": (("fzb",), "rev. 2 (post hoc)"), "U+cdev": (("cdev",), "rev. 2 (post hoc)"),
             "U+fdev": (("fdev",), "rev. 2 (post hoc)"), "UfG+cdev": (("fG", "cdev"), "rev. 2 (post hoc)"),
             "Ufc+cdev": (("fcov", "cdev"), "rev. 2 (post hoc)")}
LAMS = [0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0]   # revision 2: ridge grid (inner grouped CV picks one)


def p2_data(d: pd.DataFrame, s55) -> dict:
    inst = s55.load_institutions()[["UNITID", "CONTROL", "ST_EARN"]]
    x = d.merge(inst, on="UNITID", how="left")
    n0 = len(x)
    x = x.dropna(subset=["CONTROL", "ST_EARN"]).sort_values(["field", "inst_key"]).reset_index(drop=True)
    op = pd.read_csv(RAW / "scorecard_inst/Most-Recent-Cohorts-Institution.csv", usecols=["UNITID", "OPEID6"],
                     dtype=str)
    x = x.merge(op, on="UNITID", how="left")
    assert x.OPEID6.notna().all()
    g = pd.factorize(x.inst_key, sort=True)[0]
    fc = pd.factorize(x.field, sort=True)[0]
    G, K = int(g.max() + 1), int(fc.max() + 1)
    u = x.groupby("inst_key", sort=True).first()
    for c in ["G", "SAT_AVG", "ADM_RATE", "PCTPELL", "ST_EARN", "CONTROL", "OPEID6"]:
        assert (x.groupby("inst_key")[c].nunique() == 1).all(), f"{c} varies within a university"
    zu = lambda c: ((u[c] - u[c].mean()) / u[c].std(ddof=1)).to_numpy()[g]   # noqa: E731
    cov = {c: zu(c) for c in ["G", "SAT_AVG", "ADM_RATE", "PCTPELL", "ST_EARN"]}
    cov["private"] = (u.CONTROL.isin([2, 3]).astype(float)).to_numpy()[g]
    y = x.ly.to_numpy()
    zF = zwithin(x.F.to_numpy(float), fc)
    zb = others_mean(zF, g, G)
    oc = pd.factorize(x.OPEID6, sort=True)[0]
    multi = x.groupby("OPEID6").inst_key.nunique()
    return dict(x=x, y=y, g=g, fc=fc, G=G, K=K, cov=cov, zF=zF, zb=zb, dev=zF - zb, ocode=oc, O=int(oc.max() + 1),
                n_drop=n0 - len(x), n_private=int(u.CONTROL.isin([2, 3]).sum()),
                op_multi={k: sorted(x[x.OPEID6 == k].inst_key.unique()) for k in multi[multi > 1].index},
                op_same={k: (int(len(pv)), int((pv.nunique(axis=1) == 1).sum())) for k in multi[multi > 1].index
                         for pv in [x[x.OPEID6 == k].pivot_table(index="field", columns="inst_key",
                                                                 values="earnings").dropna()]})


def t1_X(D: dict, tr: np.ndarray, terms, covs) -> tuple[np.ndarray, int]:
    fc, K, zF, cov = D["fc"], D["K"], D["zF"], D["cov"]
    Xf = np.eye(K)[fc]
    est = np.bincount(fc[tr], minlength=K) >= EST_MIN

    def fs(v):
        return [Xf[:, est] * v[:, None], (v * (~est[fc]))[:, None]]
    cols = [Xf, np.column_stack([cov[c] for c in covs])]
    nb = K + len(covs)
    for t in terms:
        if t == "fcov":                             # scripts/58's field-specific selectivity slopes
            cols += [Xf[:, est] * cov[c][:, None] for c in ["SAT_AVG", "ADM_RATE", "PCTPELL", "G"]]
        elif t == "fG":
            cols.append(Xf[:, est] * cov["G"][:, None])
        elif t == "fF":
            cols += fs(zF)
        elif t == "cF":
            cols.append(zF[:, None])
        elif t == "fzb":
            cols += fs(D["zb"])
        elif t == "cdev":
            cols.append(D["dev"][:, None])
        elif t == "fdev":
            cols += fs(D["dev"])
        else:
            raise ValueError(t)
    return np.hstack(cols), nb


def ridge_fit(X, y, tr, nb, inner) -> tuple[np.ndarray, float]:
    """Revision 2: ridge on every column beyond field dummies + covariates; lambda by inner grouped 5-fold CV over
    the training units (the outer fold's design is kept inside)."""
    P = np.r_[np.zeros(nb), np.ones(X.shape[1] - nb)]
    Xt, yt, it = X[tr], y[tr], inner[tr]
    A, b = Xt.T @ Xt, Xt.T @ yt
    parts = [(Xt[it == j], yt[it == j]) for j in range(5)]
    Aj = [q[0].T @ q[0] for q in parts]
    bj = [q[0].T @ q[1] for q in parts]
    jit = 1e-8 * np.eye(len(A))
    best = None
    for lam in LAMS:
        sse = 0.0
        for j in range(5):
            beta = np.linalg.solve(A - Aj[j] + lam * np.diag(P) + jit, b - bj[j])
            res = parts[j][1] - parts[j][0] @ beta
            sse += float(res @ res)
        if best is None or sse < best[0]:
            best = (sse, lam)
    return np.linalg.solve(A + best[1] * np.diag(P) + jit, b), best[1]


def p2_task1(D: dict, models, covs=COV6, unit: str = "univ", splits: str = "p2_splits", ridge: bool = False) -> dict:
    y, fc, K, n = D["y"], D["fc"], D["K"], len(D["y"])
    uc, U = (D["g"], D["G"]) if unit == "univ" else (D["ocode"], D["O"])
    R = P2_REPEATS
    E = {m: np.zeros((R, n)) for m in models}
    folds = np.zeros((R, n), int)
    lams = []
    inner_g = gens("p2_ridge_inner", R * P2_FOLDS) if ridge else None
    for r, rng in enumerate(gens(splits, R)):
        perm = rng.permutation(U)
        fold_u = np.empty(U, int)
        fold_u[perm] = np.arange(U) % P2_FOLDS
        fold = fold_u[uc]
        folds[r] = fold
        for k in range(P2_FOLDS):
            te = fold == k
            tr = ~te
            assert (np.bincount(fc[tr], minlength=K) > 0).all(), "a field without training programmes"
            if ridge:
                tu = np.unique(uc[tr])
                pu = inner_g[r * P2_FOLDS + k].permutation(len(tu))
                inner_u = np.full(U, -1)
                inner_u[tu[pu]] = np.arange(len(tu)) % 5
                inner = inner_u[uc]
            for m in models:
                X, nb = t1_X(D, tr, T1_MODELS[m][0], covs)
                if ridge and X.shape[1] > nb:
                    beta, lam = ridge_fit(X, y, tr, nb, inner)
                    lams.append(lam)
                else:
                    beta = np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]
                E[m][r, te] = y[te] - X[te] @ beta
    return dict(E=E, folds=folds, unit=unit, lams=lams)


def t1_point(D: dict, T: dict, m: str, scale: str = "tot") -> float:
    y, fc, K = D["y"], D["fc"], D["K"]
    den = (y - y.mean()) ** 2 if scale == "tot" else (y - (np.bincount(fc, y, K) / np.bincount(fc, minlength=K))[fc]) ** 2
    return float(np.mean(1 - (T["E"][m] ** 2).sum(1) / den.sum()))


def fold_boot(D: dict, T: dict) -> dict:
    """C7 fold bootstrap of the primary U / U+D (pre-specified; carries the verdict)."""
    y = D["y"]
    R = P2_REPEATS
    sse = {m: np.stack([np.bincount(T["folds"][r], T["E"][m][r] ** 2, P2_FOLDS) for r in range(R)])
           for m in ("U", "UD")}
    sst = np.stack([np.bincount(T["folds"][r], (y - y.mean()) ** 2, P2_FOLDS) for r in range(R)])
    res = {k: np.empty(B) for k in ("gain_tot", "r2_U_tot", "r2_UD_tot")}
    for b, rng in enumerate(gens("p2_foldboot", B)):
        acc = {k: 0.0 for k in res}
        for r in range(R):
            ix = rng.integers(0, P2_FOLDS, P2_FOLDS)
            su, sd, st = sse["U"][r, ix].sum(), sse["UD"][r, ix].sum(), sst[r, ix].sum()
            acc["gain_tot"] += (su - sd) / st
            acc["r2_U_tot"] += 1 - su / st
            acc["r2_UD_tot"] += 1 - sd / st
        for k in res:
            res[k][b] = acc[k] / R
    pt = dict(gain_tot=t1_point(D, T, "UD") - t1_point(D, T, "U"), r2_U_tot=t1_point(D, T, "U"),
              r2_UD_tot=t1_point(D, T, "UD"))
    return {k: summ(pt[k], v) for k, v in res.items()}


def cluster_boot(D: dict, T: dict, pairs: list, levels: list, name: str, unit: str = "univ") -> dict:
    """University- (or OPEID6-) cluster bootstrap of the held-out errors, predictions fixed; per-unit squared errors
    averaged over the repeats. pairs = [(with, without, scale)], levels = [model]."""
    y, fc, K = D["y"], D["fc"], D["K"]
    uc, U = (D["g"], D["G"]) if unit == "univ" else (D["ocode"], D["O"])
    sst_u = np.bincount(uc, (y - y.mean()) ** 2, U)
    fm = (np.bincount(fc, y, K) / np.bincount(fc, minlength=K))[fc]
    sstf_u = np.bincount(uc, (y - fm) ** 2, U)
    eu = {m: np.mean([np.bincount(uc, T["E"][m][r] ** 2, U) for r in range(P2_REPEATS)], axis=0) for m in T["E"]}
    W = np.stack([np.bincount(rng.integers(0, U, U), minlength=U).astype(float) for rng in gens(name, B)])
    out = {}
    one = np.ones(U)
    for a, b0, sc in pairs:
        den = sst_u if sc == "tot" else sstf_u
        d = eu[b0] - eu[a]
        out[(a, b0, sc)] = summ((one @ d) / (one @ den), (W @ d) / (W @ den))
    for m in levels:
        out[m] = summ(1 - (one @ eu[m]) / (one @ sst_u), 1 - (W @ eu[m]) / (W @ sst_u))
    return out


# =============================================================================================================
# C8: P2 task 2 -- one programme held out at a time, within universities with >= 3 programmes
# =============================================================================================================
T2_GAINS = {  # name -> (model with F, model without F, status)
    "gain": ("UD", "U", "pre"),                          # C8 primary: field-specific F slopes + zbar
    "gainc": ("UDc", "U", "expl. (C)"),                  # C8 exploratory: common F slope + zbar
    "gaindev": ("dev", "U", "rev. 1 (post hoc)"),        # common slope on zF - zbar only
    "gainm": ("Umd", "Um", "rev. 1 (post hoc)"),         # field-specific slopes on m in both models
    "gainmdev": ("Umdev", "Um", "rev. 1 (post hoc)"),    # as gainm, F as zF - zbar only
    "gainfdev": ("fdev", "U", "rev. 2 (post hoc)"),      # field-specific slopes on zF - zbar
    "gainmfdev": ("Umfdev", "Um", "rev. 2 (post hoc)"),  # field-specific slopes on m and on zF - zbar
    "gainzb": ("Uzb", "U", "rev. 2 (post hoc)"),         # field-specific slopes on zbar (university part of F)
    "gainG": ("UfG", "U", "rev. 2 (post hoc)"),          # field-specific slopes on G (no F)
    "gainGdev": ("UfGdev", "UfG", "rev. 2 (post hoc)"),  # deviation on top of field-specific G slopes
    "gainGF": ("UfGfF", "UfG", "rev. 2 (post hoc)"),     # primary F terms on top of field-specific G slopes
}


def p2_task2(d: pd.DataFrame) -> dict:
    u3 = d.groupby("inst_key").field.transform("size") >= 3
    x = d[u3].sort_values(["field", "inst_key"]).reset_index(drop=True)
    y = x.ly.to_numpy()
    g = pd.factorize(x.inst_key, sort=True)[0]
    fc = pd.factorize(x.field, sort=True)[0]
    G, K, n = int(g.max() + 1), int(fc.max() + 1), len(x)
    zF = zwithin(x.F.to_numpy(float), fc)
    uG = x.groupby("inst_key", sort=True).G.first()
    zG = ((uG - uG.mean()) / uG.std(ddof=1)).to_numpy()[g]
    Xf = np.eye(K)[fc]
    nf_all, sf_all = np.bincount(fc, minlength=K).astype(float), np.bincount(fc, y, K)
    nu_all = np.bincount(g, minlength=G).astype(float)
    models = ["U", "UD", "UDc", "dev", "Um", "Umd", "Umdev", "fdev", "Umfdev", "Uzb", "UfG", "UfGdev", "UfGfF"]
    E = {k: np.empty(n) for k in models}
    for i in range(n):
        tr = np.ones(n)
        tr[i] = 0.0
        nf, sf = nf_all.copy(), sf_all.copy()
        nf[fc[i]] -= 1
        sf[fc[i]] -= y[i]
        mu = sf / nf
        r = y - mu[fc]
        nu = nu_all.copy()
        nu[g[i]] -= 1
        su, sz = np.bincount(g, r * tr, G), np.bincount(g, zF * tr, G)
        den = nu[g] - tr
        m = (su[g] - r * tr) / den
        zb = (sz[g] - zF * tr) / den
        est = nf >= EST_MIN
        one = np.ones(n)

        def fs(v):
            return np.column_stack([Xf[:, est] * v[:, None], v * (~est[fc])])
        fF = fs(zF)
        Xm = np.column_stack([one, fs(m)])
        X = {"U": np.column_stack([one, m]),
             "UD": np.column_stack([one, m, fF, zb]),
             "UDc": np.column_stack([one, m, zF, zb]),
             "dev": np.column_stack([one, m, zF - zb]),
             "Um": Xm,
             "Umd": np.column_stack([Xm, fF, zb]),
             "Umdev": np.column_stack([Xm, zF - zb]),
             "fdev": np.column_stack([one, m, fs(zF - zb)]),
             "Umfdev": np.column_stack([Xm, fs(zF - zb)]),
             "Uzb": np.column_stack([one, m, fs(zb)]),
             "UfG": np.column_stack([one, m, fs(zG)])}
        X["UfGdev"] = np.column_stack([X["UfG"], zF - zb])
        X["UfGfF"] = np.column_stack([X["UfG"], fF, zb])
        trm = tr > 0
        for k in models:
            Xk = X[k]
            beta = np.linalg.lstsq(Xk[trm], r[trm], rcond=None)[0]
            E[k][i] = r[i] - Xk[i] @ beta
    fm = (sf_all / nf_all)[fc]
    sst, sstf = float(((y - y.mean()) ** 2).sum()), float(((y - fm) ** 2).sum())
    out = dict(n=n, G=G, K=K, sst=sst, sstf=sstf)
    for k in models:
        out[f"r2_{k}_tot"] = 1 - float(E[k] @ E[k]) / sst
        out[f"r2_{k}_fd"] = 1 - float(E[k] @ E[k]) / sstf
    sst_u = np.bincount(g, (y - y.mean()) ** 2, G)
    sstf_u = np.bincount(g, (y - fm) ** 2, G)
    e_u = {k: np.bincount(g, E[k] ** 2, G) for k in models}
    keys = [f"{gn}_{sc}" for gn in T2_GAINS for sc in ("tot", "fd")] + [f"r2_{k}_tot" for k in models]
    bs = {k: np.empty(B) for k in keys}
    for b, rng in enumerate(gens("p2_t2_uboot", B)):
        cw = np.bincount(rng.integers(0, G, G), minlength=G).astype(float)
        st, sf2 = cw @ sst_u, cw @ sstf_u
        ee = {k: cw @ e_u[k] for k in models}
        for gn, (a, b0, _) in T2_GAINS.items():
            bs[f"{gn}_tot"][b] = (ee[b0] - ee[a]) / st
            bs[f"{gn}_fd"][b] = (ee[b0] - ee[a]) / sf2
        for k in models:
            bs[f"r2_{k}_tot"][b] = 1 - ee[k] / st
    pt = {}
    for gn, (a, b0, _) in T2_GAINS.items():
        for sc in ("tot", "fd"):
            pt[f"{gn}_{sc}"] = out[f"r2_{a}_{sc}"] - out[f"r2_{b0}_{sc}"]
    for k in models:
        pt[f"r2_{k}_tot"] = out[f"r2_{k}_tot"]
    out["S"] = {k: summ(pt[k], bs[k]) for k in keys}
    return out


# =============================================================================================================
# key-number rows (every number in the write-up comes from these rows or from the printed tables)
# =============================================================================================================
def f3(x, d=3):
    return "—" if x is None or not np.isfinite(x) else f"{x:+.{d}f}"


def fci(lo, hi, d=3):
    return "—" if lo is None or not np.isfinite(lo) else f"[{lo:+.{d}f}, {hi:+.{d}f}]"


def fn(n: int) -> str:
    return f"{n:,}"


class Rows:
    def __init__(self):
        self.r = []

    def put(self, sec, q, spec, s=None, est=np.nan, kind="", status="", verdict="", sample="", d=3):
        if s is not None:
            row = dict(est=s["est"], lo=s["lo"], hi=s["hi"], se=s["se"], mde=s["mde"])
            kind = kind or "bootstrap"
        else:
            row = dict(est=est, lo=np.nan, hi=np.nan, se=np.nan, mde=np.nan)
        self.r.append(dict(section=sec, quantity=q, specification=spec, **row, ci_kind=kind, status=status,
                           verdict=verdict, sample=sample, digits=d))

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.r)

    def md(self) -> list:
        L = ["| Section | Quantity | Specification | Estimate | 95% CI | CI kind | SE | MDE | Status | Verdict | Sample |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in self.r:
            d = x["digits"]
            se = "—" if not np.isfinite(x["se"]) else f"{x['se']:.4f}"
            mde = "—" if not np.isfinite(x["mde"]) else f"{x['mde']:.4f}"
            L.append(f"| {x['section']} | {x['quantity']} | {x['specification']} | {f3(x['est'], d)} | "
                     f"{fci(x['lo'], x['hi'], d)} | {x['ci_kind'] or '—'} | {se} | {mde} | "
                     f"{x['status'] or '—'} | {x['verdict'] or '—'} | {x['sample']} |")
        return L


TIER_NAME = {"S": "same-name", "L": "wider or merged"}
R2 = "rev. 2 (post hoc)"


# =============================================================================================================
# main
# =============================================================================================================
def compute() -> dict:
    assert _sha(_block("-----BEGIN PRESPEC-----", "-----END PRESPEC-----")) == PRESPEC_SHA256, "PRESPEC changed"
    assert _sha(_block("-----BEGIN CHOICES-----", "-----END CHOICES-----")) == CHOICES_SHA256, "CHOICES changed"
    ctx = {}
    US = build_us()
    # C0: reproduce scripts/78 G3 US (rev. 2, FE-only contrast on the main-spec cells) with the P1 code
    P = p1_prep(US["main"], ["F", "ly"])
    pt = p1_stats(P, np.ones(P["G"]))
    ctx["c0"] = dict(across=float(pt[1, 0, 1]), within=float(pt[0, 0, 1]))
    assert abs(ctx["c0"]["across"] - 0.4477474234) < 5e-4 and abs(ctx["c0"]["within"] - 0.0465032568) < 5e-4, ctx["c0"]
    P = p1_prep(US["fe"], ["F", "ly"])
    pt = p1_stats(P, np.ones(P["G"]))
    ctx["c0_fe"] = dict(across=float(pt[1, 0, 1]), within=float(pt[0, 0, 1]))
    print(f"C0 main-spec 3,961: across {ctx['c0']['across']:+.4f} within {ctx['c0']['within']:+.4f}; "
          f"FE-only 4,645: across {ctx['c0_fe']['across']:+.4f} within {ctx['c0_fe']['within']:+.4f}", flush=True)

    # ---------------- P1 ----------------
    NRC = nrc_load()
    m = NRC["m"]
    ctx["nrc"] = NRC["info"]
    ctx["nrc"]["n_biostat_stats"] = int((m.Field.eq("Statistics and Probability")
                                         & m["Program Name"].astype(str).str.contains("biostat", case=False)).sum())
    im, ist = nrc_institutions(m, US["u2k"])
    ctx["inst"] = ist
    im[["nrc_label", "how", "UNITID", "hd2006_name", "inst_key"]].to_csv(OUT_MAP, index=False)
    nrcS, stS = nrc_cells(m, im, ("S",), "one")
    nrcS4, stS4 = nrc_cells(m, im, ("S",), "one", hosts=SEPARATE_CAMPUS_HOSTS_C4)
    assert nrcS.equals(nrcS4), "revision 2: an added host touches a same-name cell"
    nrcSL, stSL = nrc_cells(m, im, ("S", "L"), "one")
    nrcSL4, stSL4 = nrc_cells(m, im, ("S", "L"), "one", hosts=SEPARATE_CAMPUS_HOSTS_C4)
    nrcW, _ = nrc_cells(m, im, ("S",), "wmean")
    ctx["cells_st"] = dict(S=stS, SL=stSL, S4=stS4, SL4=stSL4)
    cov = []
    for nf, key, tier, why in NRC_FIELD_MAP:
        src = nrcS if tier == "S" else nrcSL
        pre = US["fe"].merge(src[src.field == key][["inst_key", "field", "pubs"]], on=["inst_key", "field"])
        pre = pre[np.isfinite(pre.pubs)]
        cov.append(dict(nrc=nf, key=key, tier=tier, why=why, base_n=int((US["fe"].field == key).sum()),
                        matched=len(pre)))
    ctx["cov"] = cov
    c_pri = p1_cells(US["fe"], nrcS, "pubs")
    ctx["p1_nfields"] = int(c_pri.field.nunique())
    ctx["p1_stop"] = ctx["p1_nfields"] < 10
    P1 = {}
    if not ctx["p1_stop"]:
        for k in MEASURES:
            P1[k] = p1_run(p1_cells(US["fe"], nrcS, k), "p1_" + k)
            s = P1[k]
            print(f"P1 {k:7s} n={s['shape']}: within F-N {s['w_FN']['est']:+.3f} [{s['w_FN']['lo']:+.3f}, "
                  f"{s['w_FN']['hi']:+.3f}] F-Y {s['w_FY']['est']:+.3f} diff {s['diff']['est']:+.3f} "
                  f"[{s['diff']['lo']:+.3f}, {s['diff']['hi']:+.3f}] across F-N {s['a_FN']['est']:+.3f}", flush=True)
        P1["pubs_main"] = p1_run(p1_cells(US["main"], nrcS, "pubs"), "p1_pubs_main")
        P1["pubs_tierL"] = p1_run(p1_cells(US["fe"], nrcSL, "pubs"), "p1_pubs_tierL")
        P1["pubs_wmean"] = p1_run(p1_cells(US["fe"], nrcW, "pubs"), "p1_pubs_wmean")
        # revision 2: tier S + L with the C4 host list (the value before the four hosts were added), point only
        cl4 = p1_cells(US["fe"], nrcSL4, "pubs")
        P = p1_prep(cl4, ["F", "ly", "meas"])
        pt = p1_stats(P, np.ones(P["G"]))
        P1["pubs_tierL_c4"] = dict(w_FN=float(pt[0, 0, 2]), w_FY=float(pt[0, 0, 1]), shape=P["shape"])
        # revision 2: allocated faculty and PhD production as controls
        cc = p1_cells(US["fe"], nrcS, "pubs", need=("alloc", "phds"))
        P1["pubs_ctrl"] = p1_run(cc, "p1_pubs_ctrl", ctrl=("alloc", "phds"))
        P = p1_prep(cc, ["F", "ly", "meas"])
        pt = p1_stats(P, np.ones(P["G"]))
        P1["pubs_ctrl"]["w_FN_unc"], P1["pubs_ctrl"]["w_FY_unc"] = float(pt[0, 0, 2]), float(pt[0, 0, 1])
        # revision 2: programmes whose names carry a merged or adjacent discipline dropped
        fl_all = np.array([re.search(NAME_DROP_ALL, str(nm).lower()) is not None if f != "aerospace_engineering"
                           else name_flag(f, nm) for f, nm in zip(nrcS.field, nrcS.pname)])
        fl_ext = np.array([name_flag(f, nm) for f, nm in zip(nrcS.field, nrcS.pname)])
        P1["pubs_clean"] = p1_run(p1_cells(US["fe"], nrcS[~fl_all], "pubs"), "p1_pubs_clean")
        P1["pubs_clean2"] = p1_run(p1_cells(US["fe"], nrcS[~fl_ext], "pubs"), "p1_pubs_clean2")
        ctx["n_flag"] = (int(fl_all.sum()), int(fl_ext.sum()))
        prim_keys = c_pri[["inst_key", "field"]]
        ctx["n_flag_pri"] = int(prim_keys.merge(nrcS[fl_ext][["inst_key", "field"]]).shape[0])
        ctx["n_biostat_pri"] = int(prim_keys.merge(nrcS[nrcS.pname.astype(str).str.contains("biostat", case=False)]
                                                   [["inst_key", "field"]]).shape[0])
        for k in ("pubs_main", "pubs_tierL", "pubs_wmean", "pubs_ctrl", "pubs_clean", "pubs_clean2"):
            s = P1[k]
            print(f"P1 {k:11s} n={s['shape']}: within F-N {s['w_FN']['est']:+.3f} [{s['w_FN']['lo']:+.3f}, "
                  f"{s['w_FN']['hi']:+.3f}] F-Y {s['w_FY']['est']:+.3f} diff {s['diff']['est']:+.3f} "
                  f"[{s['diff']['lo']:+.3f}, {s['diff']['hi']:+.3f}]", flush=True)
        # revision 2: scope -- where the P1 cells sit in the within-field distribution of F (FE-only base)
        fe = US["fe"].copy()
        fe["pct"] = (fe.groupby("field").F.rank(method="average") - 0.5) / fe.groupby("field").F.transform("size")
        sc = c_pri.merge(fe[["inst_key", "field", "pct"]], on=["inst_key", "field"])
        base24 = fe[fe.field.isin(c_pri.field.unique())]
        ctx["scope"] = dict(med=float(sc.pct.median()), top=float((sc.pct > 0.5).mean()),
                            q25=float(sc.pct.quantile(0.25)), cover=len(c_pri) / len(base24), n_base=len(base24))
        p = P1["pubs"]
        ctx["p1_pass"] = bool(p["w_FN"]["lo"] > 0 and p["diff"]["lo"] > 0)
    ctx["P1"] = P1

    # ---------------- P2 ----------------
    s55 = _load("s55", "55_selectivity.py")
    D = p2_data(US["main"], s55)
    ctx["p2d"] = dict(n=len(D["y"]), G=D["G"], K=D["K"], O=D["O"], n_drop=D["n_drop"], n_private=D["n_private"],
                      op_multi=D["op_multi"], op_same=D["op_same"])
    T1 = p2_task1(D, list(T1_MODELS))
    FB = fold_boot(D, T1)
    pairs = [("UD", "U", "tot"), ("UD", "U", "fd"), ("UDc", "U", "tot"), ("Ufc+fF", "Ufc", "tot"),
             ("Ufc+cF", "Ufc", "tot"), ("UfG", "U", "tot"), ("UfG+fF", "UfG", "tot"), ("U+fzb", "U", "tot"),
             ("U+cdev", "U", "tot"), ("U+fdev", "U", "tot"), ("UfG+cdev", "UfG", "tot"), ("Ufc+cdev", "Ufc", "tot")]
    CB = cluster_boot(D, T1, pairs, ["U", "UD", "Ufc", "Ufc+fF", "UfG"], "p2_t1_uboot")
    print(f"P2 task 1: R2 U {FB['r2_U_tot']['est']:.4f} UD {FB['r2_UD_tot']['est']:.4f} gain "
          f"{FB['gain_tot']['est']:+.4f} fold [{FB['gain_tot']['lo']:+.4f}, {FB['gain_tot']['hi']:+.4f}] univ "
          f"[{CB[('UD', 'U', 'tot')]['lo']:+.4f}, {CB[('UD', 'U', 'tot')]['hi']:+.4f}]", flush=True)
    for a, b0, sc in pairs:
        x = CB[(a, b0, sc)]
        print(f"   {a:9s} - {b0:4s} [{sc}] {x['est']:+.4f} [{x['lo']:+.4f}, {x['hi']:+.4f}]", flush=True)
    TR = p2_task1(D, ["U", "UD", "Ufc", "Ufc+fF", "Ufc+cF"], ridge=True)
    CBR = cluster_boot(D, TR, [("UD", "U", "tot"), ("Ufc+fF", "Ufc", "tot"), ("Ufc+cF", "Ufc", "tot")], ["Ufc"],
                       "p2_t1_uboot")
    lam = np.array(TR["lams"])
    ctx["ridge_lam"] = dict(min=float(lam.min()), med=float(np.median(lam)), max=float(lam.max()))
    TO = p2_task1(D, ["U", "UD"], unit="opeid6", splits="p2_splits_opeid6")
    CBO = cluster_boot(D, TO, [("UD", "U", "tot")], ["U", "UD"], "p2_t1_oboot", unit="opeid6")
    TS = p2_task1(D, ["U", "UD"], covs=[c for c in COV6 if c != "ST_EARN"])
    CBS = cluster_boot(D, TS, [("UD", "U", "tot")], ["U", "UD"], "p2_t1_uboot")
    for nm_, X_, k_ in (("ridge", CBR, ("UD", "U", "tot")), ("ridge", CBR, ("Ufc+fF", "Ufc", "tot")),
                        ("ridge", CBR, ("Ufc+cF", "Ufc", "tot")), ("opeid6", CBO, ("UD", "U", "tot")),
                        ("noST", CBS, ("UD", "U", "tot"))):
        x = X_[k_]
        print(f"   {nm_:6s} {k_[0]} - {k_[1]}: {x['est']:+.4f} [{x['lo']:+.4f}, {x['hi']:+.4f}]", flush=True)
    T2 = p2_task2(US["main"])
    S2 = T2["S"]
    print(f"P2 task 2: R2 U {T2['r2_U_tot']:.4f} UD {T2['r2_UD_tot']:.4f} gain {S2['gain_tot']['est']:+.4f} "
          f"[{S2['gain_tot']['lo']:+.4f}, {S2['gain_tot']['hi']:+.4f}]", flush=True)
    for gn in T2_GAINS:
        x = S2[f"{gn}_tot"]
        print(f"   {gn:10s} {x['est']:+.4f} [{x['lo']:+.4f}, {x['hi']:+.4f}]", flush=True)
    ctx.update(T1=T1, FB=FB, CB=CB, CBR=CBR, CBO=CBO, CBS=CBS, T2=T2)
    ctx["p2_little"] = bool(FB["gain_tot"]["hi"] < 0.01 and S2["gain_tot"]["hi"] < 0.01)
    ctx["p2_little_u"] = bool(CB[("UD", "U", "tot")]["hi"] < 0.01 and S2["gain_tot"]["hi"] < 0.01)
    return ctx


def collect(ctx: dict) -> Rows:
    R = Rows()
    nm = lambda s: f"{fn(s[0])} programmes, {fn(s[1])} universities, {s[2]} fields"   # noqa: E731
    R.put("C0", "F-pay across universities within field (main-spec cells)", "Pearson of within-field normal scores",
          est=ctx["c0"]["across"], status="check", sample="3,961 programmes, 214 universities, 53 fields")
    R.put("C0", "F-pay within universities (main-spec cells)", "university + field FE residuals of normal scores",
          est=ctx["c0"]["within"], status="check", sample="3,961 programmes, 214 universities, 53 fields")
    R.put("C0", "F-pay across universities within field (FE-only cells)", "as above", est=ctx["c0_fe"]["across"],
          status="expl.", sample="4,645 programmes, 251 universities, 55 fields")
    R.put("C0", "F-pay within universities (FE-only cells)", "as above", est=ctx["c0_fe"]["within"], status="expl.",
          sample="4,645 programmes, 251 universities, 55 fields")
    P1 = ctx["P1"]
    if not ctx["p1_stop"]:
        for k, (lab, st) in MEASURES.items():
            s = P1[k]
            smp = nm(s["shape"])
            v = ("positive control passes" if ctx["p1_pass"] else "positive control does not pass") if k == "pubs" \
                else ""
            spec = "FE-only base, same-name fields, one programme"
            R.put("P1", f"within(F, {lab})", spec, s["w_FN"], status=st, verdict=v, sample=smp)
            R.put("P1", f"across(F, {lab})", "same cells", s["a_FN"], status=st, sample=smp)
            R.put("P1", f"within(F, pay) on the {lab} cells", "same cells", s["w_FY"], status=st, sample=smp)
            R.put("P1", f"across(F, pay) on the {lab} cells", "same cells", s["a_FY"], status=st, sample=smp)
            R.put("P1", f"within(F, {lab}) - within(F, pay)", "paired, same draws", s["diff"], status=st,
                  verdict=v, sample=smp)
            R.put("P1", f"within({lab}, pay)", "same cells", s["w_NY"], status="expl. (C)", sample=smp)
        for k, spec, st in (("pubs_main", "main-spec base (3,961), same-name fields, one programme", "sens"),
                            ("pubs_tierL", "FE-only base, same-name + wider or merged fields, one programme",
                             "expl. (C)"),
                            ("pubs_wmean", "FE-only base, same-name fields, allocated-faculty-weighted mean",
                             "expl. (C)"),
                            ("pubs_ctrl", "+ normal scores of allocated faculty and PhDs graduated as controls", R2),
                            ("pubs_clean", "programmes with a merged or adjacent name dropped (list for all fields)",
                             R2),
                            ("pubs_clean2", "as above + field-specific names", R2)):
            s = P1[k]
            smp = nm(s["shape"])
            R.put("P1 sens.", "within(F, publications per allocated faculty)", spec, s["w_FN"], status=st, sample=smp)
            R.put("P1 sens.", "within(F, pay) on the same cells", spec, s["w_FY"], status=st, sample=smp)
            R.put("P1 sens.", "within(F, publications) - within(F, pay)", spec, s["diff"], status=st, sample=smp)
        c4 = P1["pubs_tierL_c4"]
        R.put("P1 sens.", "within(F, publications), wider or merged fields, C4 host list", "value before revision 2",
              est=c4["w_FN"], status=R2, sample=nm(c4["shape"]))
        c = P1["pubs_ctrl"]
        R.put("P1 sens.", "within(F, publications) on the control cells, no controls", "same cells as the control row",
              est=c["w_FN_unc"], status=R2, sample=nm(c["shape"]))
        sc = ctx["scope"]
        R.put("P1 scope", "median within-field percentile of F, primary P1 cells", "percentile in the FE-only base",
              est=sc["med"], status=R2, sample=nm(P1["pubs"]["shape"]))
        R.put("P1 scope", "share of primary P1 cells above their field's median F", "FE-only base", est=sc["top"],
              status=R2, sample=nm(P1["pubs"]["shape"]))
    FB, CB, CBR, CBO, CBS, T2 = ctx["FB"], ctx["CB"], ctx["CBR"], ctx["CBO"], ctx["CBS"], ctx["T2"]
    p2v = "department adds little out of sample" if ctx["p2_little"] else "gain not below 0.01 (size reported)"
    s1 = f"{fn(ctx['p2d']['n'])} programmes, {ctx['p2d']['G']} universities, {ctx['p2d']['K']} fields"
    s1o = f"{fn(ctx['p2d']['n'])} programmes, {ctx['p2d']['O']} OPEID6 groups"
    s2 = f"{fn(T2['n'])} programmes, {T2['G']} universities, {T2['K']} fields"
    ub, fk, ob = "university bootstrap", "fold bootstrap", "OPEID6 bootstrap"
    cvs = f"{P2_FOLDS}-fold x {P2_REPEATS} grouped CV, total scale"
    R.put("P2 task 1", "R-squared, model U", cvs, CB["U"], kind=ub, status="pre", sample=s1, d=4)
    R.put("P2 task 1", "R-squared, model U+D", "same folds", CB["UD"], kind=ub, status="pre", sample=s1, d=4)
    R.put("P2 task 1", "gain from F", "U+D minus U (pre-specified interval)", FB["gain_tot"], kind=fk, status="pre",
          verdict=p2v, sample=s1, d=4)
    R.put("P2 task 1", "gain from F", "U+D minus U (interval of record, revision 2)", CB[("UD", "U", "tot")], kind=ub,
          status="pre", sample=s1, d=4)
    T1rows = [(("UD", "U", "fd"), "gain from F, field-demeaned scale", "denominator sum (y - field mean)^2",
               "expl. (C)"),
              (("UDc", "U", "tot"), "gain from F, common F slope", "U + one z(F) slope", "expl. (C)"),
              (("Ufc+fF", "Ufc", "tot"), "gain from F, field-specific selectivity slopes in both",
               "field x {SAT, ADM, Pell, G}; F field-specific", "expl. (C)"),
              (("Ufc+cF", "Ufc", "tot"), "gain from F, field-specific selectivity slopes, one common F slope",
               "U+D minus U", "rev. 1 (post hoc)"),
              (("UfG", "U", "tot"), "gain from field-specific slopes on G alone (no F)", "U + field x G", R2),
              (("UfG+fF", "UfG", "tot"), "gain from F on top of field-specific G slopes", "F field-specific", R2),
              (("U+fzb", "U", "tot"), "gain from the mean z(F) of the university's other programmes",
               "field-specific slopes (university part of F)", R2),
              (("U+cdev", "U", "tot"), "gain from the department's deviation z(F) - mean z(F)", "one common slope",
               R2),
              (("U+fdev", "U", "tot"), "gain from the deviation", "field-specific slopes", R2),
              (("UfG+cdev", "UfG", "tot"), "gain from the deviation on top of field-specific G slopes",
               "one common slope", R2),
              (("Ufc+cdev", "Ufc", "tot"), "gain from the deviation on top of field-specific selectivity slopes",
               "one common slope", R2)]
    for key, q, spec, st in T1rows:
        R.put("P2 task 1", q, spec, CB[key], kind=ub, status=st, sample=s1, d=4)
    R.put("P2 task 1", "R-squared, model U with field-specific selectivity slopes", "field x {SAT, ADM, Pell, G}",
          CB["Ufc"], kind=ub, status="expl. (C)", sample=s1, d=4)
    R.put("P2 task 1", "R-squared, that model + F (field-specific slopes)", "same folds", CB["Ufc+fF"], kind=ub,
          status="expl. (C)", sample=s1, d=4)
    R.put("P2 task 1", "R-squared, U + field-specific G slopes", "same folds", CB["UfG"], kind=ub, status=R2,
          sample=s1, d=4)
    R.put("P2 task 1", "ridge: gain from F (field-specific slopes) over U", "penalty by inner grouped 5-fold CV",
          CBR[("UD", "U", "tot")], kind=ub, status=R2, sample=s1, d=4)
    R.put("P2 task 1", "ridge: gain from F, field-specific selectivity slopes in both", "F field-specific",
          CBR[("Ufc+fF", "Ufc", "tot")], kind=ub, status=R2, sample=s1, d=4)
    R.put("P2 task 1", "ridge: gain from F, field-specific selectivity slopes, one common F slope", "F common",
          CBR[("Ufc+cF", "Ufc", "tot")], kind=ub, status=R2, sample=s1, d=4)
    R.put("P2 task 1", "gain from F, folds grouped by OPEID6", "U+D minus U", CBO[("UD", "U", "tot")], kind=ob,
          status=R2, sample=s1o, d=4)
    R.put("P2 task 1", "gain from F, ST_EARN removed from both models", "U+D minus U", CBS[("UD", "U", "tot")],
          kind=ub, status=R2, sample=s1, d=4)
    S2 = T2["S"]
    R.put("P2 task 2", "R-squared, without F", "field effects + other programmes' mean residual m", S2["r2_U_tot"],
          kind=ub, status="pre", sample=s2, d=4)
    R.put("P2 task 2", "R-squared, with F", "+ field-specific z(F) slopes + other programmes' mean z(F)",
          S2["r2_UD_tot"], kind=ub, status="pre", sample=s2, d=4)
    R.put("P2 task 2", "gain from F", "with minus without", S2["gain_tot"], kind=ub, status="pre", verdict=p2v,
          sample=s2, d=4)
    R.put("P2 task 2", "gain from F, field-demeaned scale", "denominator sum (y - field mean)^2", S2["gain_fd"],
          kind=ub, status="expl. (C)", sample=s2, d=4)
    T2rows = [("gainc", "gain from F, common F slope", "+ one z(F) slope + mean z(F)"),
              ("gaindev", "gain from the department's deviation z(F) - mean z(F)", "one common slope"),
              ("gainfdev", "gain from the deviation", "field-specific slopes"),
              ("gainm", "gain from F as in the primary model, field-specific slopes on m in both",
               "upper bound: contains university terms"),
              ("gainmdev", "gain from the deviation, field-specific slopes on m", "one common slope"),
              ("gainmfdev", "gain from the deviation, field-specific slopes on m", "field-specific slopes"),
              ("gainzb", "gain from the other programmes' mean z(F)", "field-specific slopes (university part of F)"),
              ("gainG", "gain from field-specific slopes on G alone (no F)", "+ field x G"),
              ("gainGdev", "gain from the deviation on top of field-specific G slopes", "one common slope"),
              ("gainGF", "gain from F as in the primary model on top of field-specific G slopes", "")]
    for gn, q, spec in T2rows:
        R.put("P2 task 2", q, spec, S2[f"{gn}_tot"], kind=ub, status=T2_GAINS[gn][2], sample=s2, d=4)
    R.put("P2 task 2", "R-squared, without F, field-specific slopes on m", "field x m", S2["r2_Um_tot"], kind=ub,
          status="rev. 1 (post hoc)", sample=s2, d=4)
    return R


def write_outputs(ctx: dict) -> None:
    R = collect(ctx)
    R.frame().drop(columns="digits").to_csv(OUT_CSV, index=False, float_format="%.6f")
    pre = _block("-----BEGIN PRESPEC-----", "-----END PRESPEC-----")
    cho = _block("-----BEGIN CHOICES-----", "-----END CHOICES-----")
    P1, FB, CB, CBR, CBO, CBS, T2 = (ctx[k] for k in ("P1", "FB", "CB", "CBR", "CBO", "CBS", "T2"))
    S2 = T2["S"]
    ci = lambda s, d=3: fci(s["lo"], s["hi"], d)                                       # noqa: E731
    e = lambda s, d=3: f3(s["est"], d)                                                 # noqa: E731
    r4 = lambda s: f"{s['est']:.4f}"                                                    # noqa: E731
    pts = lambda v: f"{v * 100:.2f}"                                                    # noqa: E731
    nfo, ist = ctx["nrc"], ctx["inst"]
    g1f, g1u, g2 = FB["gain_tot"], CB[("UD", "U", "tot")], S2["gain_tot"]
    dev1 = [CB[k]["est"] for k in (("U+cdev", "U", "tot"), ("U+fdev", "U", "tot"), ("UfG+cdev", "UfG", "tot"),
                                   ("Ufc+cdev", "Ufc", "tot"))]
    dev2 = [S2[f"{k}_tot"]["est"] for k in ("gaindev", "gainfdev", "gainmdev", "gainmfdev", "gainGdev")]
    dev2_pos = dev2
    dev = [f"**DEVELOPMENT RUN: GAP85_B = {B}; not a reported result.**", ""] if "GAP85_B" in os.environ else []
    L = ["# Positive control and out-of-sample prediction — does a department's standing within its university carry "
         "academic information, and does it help predict its graduates' pay out of sample?", ""] + dev + [
         "Script: `scripts/85_positive_control_prediction.py` (numpy SeedSequence(85); every number below is written by "
         "the script from its own computations; a second run gives a byte-identical file). Public data only: the National "
         "Research Council's *A Data-Based Assessment of Research-Doctorate Programs* Excel data table (revised 4/29/2011; "
         "nap.edu; provenance, md5 and terms of use in `data/sources.csv` section 10n), the 2026 Wapman et al. release "
         "(repaired name join), the College Scorecard Field-of-Study and institution files and IPEDS HD2006. Existing "
         "scripts are imported (scripts/24 for the field crosswalk, scripts/55 for the institution covariates), not "
         "edited. Descriptive, not causal. Tables: `data/interim/positive_control_prediction_summary.csv` (every key "
         "number), `data/interim/nrc_institution_map.csv` (NRC label to UNITID; no NRC values, which may not be "
         "redistributed).", "",
         "**Revision 1** (after the first, development-size run had been seen; status `rev. 1 (post hoc)`): the "
         "replicate generators are rebuilt from each analysis' spawn key, because `SeedSequence.spawn` is stateful and "
         "gave the exploratory task-1 variants other fold splits than the primary model (the pre-specified quantities "
         "used the first spawn of their own child, so their draws are the same); and four task-2 variants and one "
         "task-1 variant were added to locate the gain from F.", "",
         "**Revision 2, added after the results had been seen** (status `rev. 2 (post hoc)`). An "
         "independent re-computation reproduced P1 and P2 and found no critical issue. Every addition below is post hoc "
         "and carries no rule; the pre-specified verdicts are unchanged. P2: every R² gain now carries a "
         "university-cluster bootstrap interval (the pre-specified fold-bootstrap interval of the primary gain is kept "
         "and still carries the verdict); task-1 rows that split F into its university part and the department's "
         "within-university deviation, with matching task-2 rows; ridge versions; folds grouped by OPEID6; the gain "
         "without the state earnings level. P1: a version controlling the department's allocated faculty and PhD "
         "production; a version dropping programmes whose names carry a merged or adjacent discipline; four branch-"
         "campus hosts the C4 list missed are now excluded (none is in a same-name field, so the primary P1 cells are "
         "unchanged; asserted); the scope of the P1 cells. Tier S of the choices is called 'same-name fields' and tier "
         "L 'wider or merged fields' here. Memory: every analysis run of this script ran under `prlimit "
         "--as=2500000000` "
         "(a few small development calls, such as version checks and listings of field names, institution labels "
         "and programme hostnames, did not).", "",
         "## Answer", ""]
    if ctx["p1_stop"]:
        L += [f"**P1 stops:** only {ctx['p1_nfields']} fields have clean NRC matches (fewer than 10).", ""]
    else:
        p = P1["pubs"]
        sh = p["shape"]
        dz = [MEASURES[k][0] + " " + ci(P1[k]["diff"]) for k in MEASURES if k != "pubs" and P1[k]["diff"]["lo"] <= 0]
        dztxt = (" The paired difference from the F–pay correlation excludes 0 for every other measure"
                 + (" except the " + "; ".join(dz) if dz else "") + " (the rule applies to publications only).")
        c, cl, sc = P1["pubs_ctrl"], P1["pubs_clean"], ctx["scope"]
        L += [(f"**P1 — positive control: {'passes' if ctx['p1_pass'] else 'does not pass'}.** On "
               f"{fn(sh[0])} programmes ({sh[1]} universities, {sh[2]} fields) of the FE-only sample with a clean "
               f"one-to-one NRC match in a same-name field, the within-university correlation of F with publications "
               f"per allocated faculty (the primary measure, named first) is {e(p['w_FN'])} {ci(p['w_FN'])}, against "
               f"{e(p['w_FY'])} {ci(p['w_FY'])} for F and pay on the same cells; the paired difference is "
               f"{e(p['diff'])} {ci(p['diff'])}. Across universities the two correlations are {e(p['a_FN'])} "
               f"(publications) and {e(p['a_FY'])} (pay). The within-university correlation of F is positive for every "
               f"NRC measure: citations per publication {e(P1['cites']['w_FN'])} {ci(P1['cites']['w_FN'])}, share of "
               f"faculty with grants {e(P1['grants']['w_FN'])} {ci(P1['grants']['w_FN'])}, R-ranking midpoint "
               f"{e(P1['rmid']['w_FN'])} {ci(P1['rmid']['w_FN'])} and S-ranking midpoint {e(P1['smid']['w_FN'])} "
               f"{ci(P1['smid']['w_FN'])} (both rankings also weight PhD production and academic placement, so they "
               f"are partly circular here), and, exploratory, research-activity ranking midpoint "
               f"{e(P1['ramid']['w_FN'])} and awards per faculty {e(P1['awards']['w_FN'])}." + dztxt +
               f" On the main-spec cells (named sensitivity) the publications correlation is "
               f"{e(P1['pubs_main']['w_FN'])} against {e(P1['pubs_main']['w_FY'])} for pay (difference "
               f"{e(P1['pubs_main']['diff'])} {ci(P1['pubs_main']['diff'])}). The NRC research measures are not "
               f"positively related to pay inside universities either (exploratory): publications per faculty "
               f"{e(p['w_NY'])} {ci(p['w_NY'])}, share of faculty with grants {e(P1['grants']['w_NY'])} "
               f"{ci(P1['grants']['w_NY'])}, citations per publication {e(P1['cites']['w_NY'])} "
               f"{ci(P1['cites']['w_NY'])}."), "",
              (f"*Revision 2, added after the results had been seen.* With the department's allocated "
               f"faculty and PhD production as controls ({fn(c['shape'][0])} programmes), the within-university "
               f"correlation of F with publications falls from {f3(c['w_FN_unc'])} to {e(c['w_FN'])} {ci(c['w_FN'])} "
               f"and its difference from the F–pay correlation is {e(c['diff'])} {ci(c['diff'])}. Dropping programmes "
               f"whose names carry a merged or adjacent discipline (the list for all fields; {fn(cl['shape'][0])} "
               f"programmes, {cl['shape'][1]} universities, {cl['shape'][2]} fields) gives {e(cl['w_FN'])} and a "
               f"difference of {e(cl['diff'])} {ci(cl['diff'])}; with field-specific names added, {e(P1['pubs_clean2']['w_FN'])} "
               f"and {e(P1['pubs_clean2']['diff'])} {ci(P1['pubs_clean2']['diff'])}. Scope: these are NRC-covered "
               f"doctoral departments, {sc['cover'] * 100:.0f}% of the FE-only programmes in their {sh[2]} fields, and "
               f"they sit in the upper part of the F distribution (median within-field percentile {sc['med']:.2f}; "
               f"{sc['top'] * 100:.0f}% above their field's median). P1 rules out that the within-university residual "
               f"of F is noise for these departments; it does not rule out that noise in the pay measure hides a "
               f"relation with pay."), ""]
    L += [f"**P2 — out-of-sample prediction: {'department adds little out of sample' if ctx['p2_little'] else 'the pre-specified rule does not say the department adds little'}.** "
          f"Task 1 (a new university; whole universities held out, {P2_FOLDS} folds x {P2_REPEATS} repeats; "
          f"{fn(ctx['p2d']['n'])} programmes): model U (field effects, G, SAT, admission rate, Pell share, control, "
          f"state earnings level) reaches an out-of-sample R² of {r4(CB['U'])}, and adding F with field-specific "
          f"slopes raises it to {r4(CB['UD'])}: a gain of {e(g1f, 4)}, {ci(g1f, 4)} by the pre-specified fold "
          f"bootstrap and {ci(g1u, 4)} by a university-cluster bootstrap (revision 2, the interval of record). Task 2 "
          f"(a different question: given what a university's other departments pay, does a department's standing help "
          f"predict its own pay? One programme held out at a time, universities with ≥ 3 programmes, {fn(T2['n'])} "
          f"programmes): R² {r4(S2['r2_U_tot'])} without F and {r4(S2['r2_UD_tot'])} with it, a gain of {e(g2, 4)} "
          f"{ci(g2, 4)} (university-cluster bootstrap). Both upper bounds exceed 0.01 (task 1 alone is enough, "
          f"since the rule needs both tasks below it), so the gains are reported as sizes: about {g1f['est'] * 100:.1f} "
          f"and {g2['est'] * 100:.1f} points of R². The post hoc rows below show that these points are not department "
          f"information.", ""]
    L += ["*Where the P2 gain comes from (revision 1 and revision 2, post hoc, no rule).* "
          f"Task 1: field-specific slopes on the university's academy-wide rank G alone, with no F, add "
          f"{e(CB[('UfG', 'U', 'tot')], 4)} {ci(CB[('UfG', 'U', 'tot')], 4)}, as much as F does; the mean z(F) of the "
          f"university's other programmes with field-specific slopes (the university part of F) adds "
          f"{e(CB[('U+fzb', 'U', 'tot')], 4)} {ci(CB[('U+fzb', 'U', 'tot')], 4)}; the department's within-university "
          f"deviation z(F) minus that mean adds {e(CB[('U+cdev', 'U', 'tot')], 4)} {ci(CB[('U+cdev', 'U', 'tot')], 4)} "
          f"with one slope, {e(CB[('U+fdev', 'U', 'tot')], 4)} {ci(CB[('U+fdev', 'U', 'tot')], 4)} with field-specific "
          f"slopes and {e(CB[('UfG+cdev', 'UfG', 'tot')], 4)} {ci(CB[('UfG+cdev', 'UfG', 'tot')], 4)} on top of "
          f"field-specific G slopes. Giving U field-specific slopes on SAT, admission rate, Pell share and G lifts its "
          f"R² to {r4(CB['Ufc'])}, above the primary U+D ({r4(CB['UD'])}), and F then adds about 0: "
          f"{e(CB[('Ufc+cF', 'Ufc', 'tot')], 4)} {ci(CB[('Ufc+cF', 'Ufc', 'tot')], 4)} with one slope, and "
          f"{e(CBR[('Ufc+fF', 'Ufc', 'tot')], 4)} {ci(CBR[('Ufc+fF', 'Ufc', 'tot')], 4)} (field-specific slopes) and "
          f"{e(CBR[('Ufc+cF', 'Ufc', 'tot')], 4)} {ci(CBR[('Ufc+cF', 'Ufc', 'tot')], 4)} (one slope) under ridge "
          f"with the penalty chosen by inner grouped CV (λ from {ctx['ridge_lam']['min']:g} to "
          f"{ctx['ridge_lam']['max']:g}, median {ctx['ridge_lam']['med']:g}). The unpenalised field-specific version, "
          f"{e(CB[('Ufc+fF', 'Ufc', 'tot')], 4)} {ci(CB[('Ufc+fF', 'Ufc', 'tot')], 4)}, measures the cost of one "
          f"unpenalised slope per field, not a loss from F. Task 2: the deviation adds {e(S2['gaindev_tot'], 4)} "
          f"{ci(S2['gaindev_tot'], 4)} (one slope), {e(S2['gainfdev_tot'], 4)} (field-specific slopes), "
          f"{e(S2['gainmdev_tot'], 4)} and {e(S2['gainmfdev_tot'], 4)} with field-specific slopes on the other "
          f"programmes' mean residual m, and {e(S2['gainGdev_tot'], 4)} on top of field-specific G slopes; field-"
          f"specific G slopes alone add {e(S2['gainG_tot'], 4)} and the other programmes' mean z(F) "
          f"{e(S2['gainzb_tot'], 4)}. The {e(S2['gainm_tot'], 4)} {ci(S2['gainm_tot'], 4)} that the primary F terms "
          f"add over field-specific slopes on m is an upper bound for the department: it still contains university "
          f"terms (the mean z(F) and the university part of each z(F)). So the department's own information adds "
          f"about 0 in task 1 (at most {pts(max(dev1))} points across the four deviation rows) and about "
          f"{pts(min(dev2_pos))}–{pts(max(dev2_pos))} points in task 2.", ""]
    osm = "; ".join(f"{', '.join(ctx['p2d']['op_multi'][k])} (OPEID6 {k}): identical earnings in {v[1]} of {v[0]} "
                    f"common fields" for k, v in ctx["p2d"]["op_same"].items())
    L += [f"*Checks on task 1 (revision 2, post hoc).* University keys that share an OPEID6 in the task-1 cells: "
          f"{osm}; so university-grouped folds can put "
          f"one campus's pay in training for the other; with folds grouped by OPEID6 ({ctx['p2d']['O']} groups) the "
          f"gain is {e(CBO[('UD', 'U', 'tot')], 4)} {ci(CBO[('UD', 'U', 'tot')], 4)}. The state earnings level of a "
          f"training university includes the institution-wide earnings of held-out institutions in its state (never "
          f"its own); with ST_EARN removed from both models the gain is {e(CBS[('UD', 'U', 'tot')], 4)} "
          f"{ci(CBS[('UD', 'U', 'tot')], 4)}. Ridge on the primary comparison: {e(CBR[('UD', 'U', 'tot')], 4)} "
          f"{ci(CBR[('UD', 'U', 'tot')], 4)}.", ""]
    p1r = ("P1 answers the question it was asked: for NRC-covered doctoral departments the indicator is not the problem. "
           "Inside a university, the departments that Wapman's hiring network ranks higher are the ones the NRC's "
           "independent data credit with more publications, citations, grants and awards per faculty member, while the "
           "same residual barely moves with graduates' pay, and the NRC research measures are not positively related to "
           "pay there either. "
           if (not ctx["p1_stop"] and ctx["p1_pass"]) else "")
    L += ["**Reading.** " + p1r +
          f"P2's pre-specified rule does not return 'adds little': with field-specific slopes F adds "
          f"{g1f['est'] * 100:.1f} and {g2['est'] * 100:.1f} points of R². The post hoc rows show what those points "
          f"are: field-specific pricing of the university's standing, which G or the university's other departments "
          f"carry as well as F does. The part of F that belongs to the department, its position among its own "
          f"university's departments, adds about 0 for a new university and about {pts(min(dev2_pos))}–"
          f"{pts(max(dev2_pos))} points within a university.", ""]
    L += ["## Pre-specification, choices and deviations", "",
          "The rules below were fixed on 2026-11-17 before any outcome was computed for this script and are copied "
          f"verbatim into the script's docstring (SHA-256 of the block `{PRESPEC_SHA256}`, checked at run time). A first "
          "copy, written before the NRC file was downloaded, also carried a dating sentence and a reminder that anything "
          "else is exploratory inside the markers; both were moved outside the markers before any outcome was computed. "
          "The implementation choices C0–C10 were recorded the same day after reading the NRC workbook's Guide sheet and "
          "counting coverage, and before the first outcome was computed (SHA-256 "
          f"`{CHOICES_SHA256}`). Status labels: pre = named in the binding text and carrying its rule; named = an NRC "
          "measure the binding text names, reported without a rule; sens = the sensitivity named in C6; check = a "
          "reproduction of a published number; expl. (C) = exploratory, fixed in advance in the choices; expl. = "
          "exploratory context; rev. 1 (post hoc) = added after the first results were seen; rev. 2 (post hoc) = "
          "added in revision 2, after the results had been seen.", "",
          "```text", pre.rstrip("\n"), "```", "",
          "<details><summary>Implementation choices C0–C10, verbatim</summary>", "", "```text", cho.rstrip("\n"), "```",
          "", "</details>", "",
          "**Deviations.** None from the binding text. One reading is stated in C7: the binding text lists the "
          "university's mean pay in its other fields under model U and then forbids it for held-out universities; task "
          "1 follows the sub-bullet (covariates only for held-out universities), and the other-fields mean enters task "
          "2, where it is observed. Revision 2 corrects C4's host list (four branch campuses with their own UNITID; no "
          "effect on the same-name cells).", ""]
    L += ["## Key numbers", "",
          f"CI = 95% percentile interval. P1: {fn(B)} university-cluster bootstrap draws, normal scores held fixed, "
          f"fixed effects re-fitted in each draw. P2 task 1: the pre-specified fold bootstrap ({fn(B)} draws; each "
          f"repeat's {P2_FOLDS} folds drawn with replacement; gain from the drawn folds' sums; mean over the "
          f"{P2_REPEATS} repeats) on the primary gain only; every other task-1 interval is a university-cluster "
          f"bootstrap of the held-out errors ({fn(B)} draws, the same draws for every row; per-university squared "
          f"errors averaged over the repeats; OPEID6-cluster for the OPEID6 row). P2 task 2: {fn(B)} university-cluster "
          "draws of the held-out errors. SE = SD of the draws; MDE = 2.80 SE. Within = correlation of university + "
          "field FE residuals of within-field normal scores (G3's statistic); across = correlation of the within-field "
          "normal scores, field means removed.", ""]
    L += R.md() + [""]
    # ---------------- P1 detail ----------------
    st = ctx["cells_st"]
    L += ["## P1 detail — data, maps, cells", "",
          f"NRC data table: {fn(nfo['n_prog'])} programmes, {nfo['n_fields']} fields, {nfo['n_labels']} institution "
          f"labels (including joint programmes); {nfo['n_unranked']} programmes are 'Not Ranked' (no R / S / "
          f"dimensional ranges); citations per publication is 'N/D' for {fn(nfo['n_cites_nd'])} programmes (humanities "
          f"and computer science). Humanities publications are counted from résumés (five per book plus articles, "
          f"1986–2006), other fields from Thomson Reuters articles 2000–2006 (computer science adds refereed "
          f"conference papers); within-field normal scores make the scales comparable. The Windows workbook's Master "
          f"sheet has the same values in all {nfo['same_cols']} columns ({nfo['hdr_diff']} header differs in "
          f"punctuation). NRC 'Statistics and Probability' holds {nfo['n_biostat_stats']} programmes named "
          f"biostatistics ({ctx['n_biostat_pri']} in the primary P1 cells).", "",
          f"Institution map (C4): {ist['n_labels']} labels; {ist['n_auto']} matched by exact normalised HD2006 name, "
          f"{ist['n_alias']} by hand-checked alias, {ist['n_joint']} joint-programme labels excluded, "
          f"{ist['n_unmatched']} unmatched ({'; '.join(ist['unmatched'])}); {ist['n_key']} labels reach a Scorecard "
          f"university key. Programmes on a separately listed campus excluded (revision 2 list: "
          f"{', '.join(sorted(SEPARATE_CAMPUS_HOSTS))}): {st['S']['n_sep']} in same-name fields (C4 list: "
          f"{st['S4']['n_sep']}), {st['SL']['n_sep']} in all mapped fields (C4 list: {st['SL4']['n_sep']}). Same-name "
          f"(university, field) cells with an NRC programme: {fn(st['S']['n_cells_any'])}, of which "
          f"{fn(st['S']['n_cells_one'])} have exactly one programme (kept) and {fn(st['S']['n_cells_multi'])} two or "
          f"more (excluded). Revision 2 name screen: {ctx['n_flag'][0]} kept same-name programmes carry a merged or "
          f"adjacent discipline in their name under the list for all fields, {ctx['n_flag'][1]} with field-specific "
          f"names added ({ctx['n_flag_pri']} in the primary P1 cells).", "",
          "Field map (C3). *Base cells* = FE-only programmes in the field; *matched* = those with a clean one-programme "
          "NRC match and a released publications value, before the sample rules; the primary P1 cells are the same-name "
          "fields after the rules.", "",
          "| NRC field | US field key | Tier | Reason | Base cells | Matched |", "|---|---|---|---|---|---|"]
    for c in ctx["cov"]:
        L.append(f"| {c['nrc']} | {c['key']} | {TIER_NAME[c['tier']]} | {c['why']} | {c['base_n']} | {c['matched']} |")
    if not ctx["p1_stop"]:
        fl = P1["pubs"]["fields"]
        L += ["", f"Primary P1 cells by field (after the sample rules; {len(fl)} fields): "
              + ", ".join(f"{k} {v}" for k, v in fl.items()) + ".", ""]
    # ---------------- P2 detail ----------------
    om = "; ".join(f"{k}: {', '.join(v)}" for k, v in ctx["p2d"]["op_multi"].items())
    L += ["## P2 detail", "",
          f"Task 1 cells: the main-spec sample with control and state earnings level ({fn(ctx['p2d']['n'])} "
          f"programmes, {ctx['p2d']['G']} universities, {ctx['p2d']['K']} fields; {ctx['p2d']['n_drop']} dropped for "
          f"missing covariates; {ctx['p2d']['n_private']} private universities). OPEID6 groups with more than one "
          f"university key: {om}. On the field-demeaned scale (share of the within-field variance; exploratory) the "
          f"primary gain is {e(CB[('UD', 'U', 'fd')], 4)} {ci(CB[('UD', 'U', 'fd')], 4)}. Revision-2 terms: the "
          f"mean z(F) of the university's other programmes (no pay enters it) and the deviation z(F) minus that mean; "
          f"field-specific slopes are estimated for fields with ≥ {EST_MIN} training programmes, pooled otherwise. "
          f"Ridge: every term beyond the field dummies and the six covariates is penalised; λ from "
          f"{{{', '.join(f'{v:g}' for v in LAMS)}}} by inner 5-fold CV over the training universities, within the outer "
          f"fold's design.", "",
          f"Task 2 cells: main-spec programmes at universities with ≥ 3 programmes ({fn(T2['n'])} programmes, "
          f"{T2['G']} universities, {T2['K']} fields). Field-demeaned scale: gain {e(S2['gain_fd'], 4)} "
          f"{ci(S2['gain_fd'], 4)}. Models: 'dev' adds one slope on z(F) minus the mean z(F) of the university's other "
          f"programmes (the department's position inside its university); 'm × field' replaces the single slope on the "
          f"other programmes' mean residual by field-specific slopes; 'G × field' adds field-specific slopes on G.", "",
          "## Method notes", "",
          "- P1 normal scores are recomputed on each analysis' own cells (Blom, midranks, standardised within field), "
          "so the F–pay correlation beside each NRC measure is on exactly those cells. A university drawn k times "
          "enters with weight k; its fixed effect is re-fitted. Controls (revision 2) enter as within-field normal "
          "scores beside the field fixed effects.",
          "- P2 never uses a held-out university's pay (task 1) or a held-out programme's pay (task 2) in any estimate: "
          "field effects, slopes and, in task 2, the other programmes' means of every training row are recomputed "
          "without it. z(F) is standardised within field over the whole sample, which uses no pay. The state earnings "
          "level is scripts/55's leave-one-out state mean of institution-wide earnings; it includes other institutions' "
          "earnings, held-out ones among them (see the check above).",
          "- The result file carries no timings, memory figures or run dates; BLAS runs single-threaded.", ""]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(R.md()))


def main():
    ctx = compute()
    write_outputs(ctx)


if __name__ == "__main__":
    main()
