"""Wapman et al. (2022) release adapter: 2026 upstream files -> the v1 file formats the scripts read.

Background (data/sources.csv, section 1). The repository was built on the Zenodo v1 archive
(10.5281/zenodo.6941651), whose ``ranks.csv`` / ``edge_lists.csv`` (dated 2021-12-08) predate the published
analysis: an 81-field taxonomy with ", General" names, a ``Rank`` that is not the published ordinal (per-field
Spearman with the published ``OrdinalPrestigeRank``: median 0.96, minimum 0.77; academia-wide 0.956), and an edge
list that kept only (doctoral institution, employer) pairs with at least one man and one woman (Total >= 2; an
upstream bug, fixed 2022-09-22). The upstream GitHub repository (LarremoreLab/us-faculty-hiring-networks, commit
841e9c9, 2026-08-22) regenerated all four files: ``data/raw/wapman2026/``.

Every existing script reads ``data/raw/wapman2022/``. This module regenerates that directory from
``data/raw/wapman2026/`` in the v1 column formats, so the scripts run unchanged:

* ``ranks.csv``  - ``Rank, InstitutionId, InstitutionName, TaxonomyValue, TaxonomyLevel``, one row per ranked
  (institution, network) of ``institution-stats.csv`` (12,669 rows, 116 networks). ``Rank`` = the published
  ``OrdinalPrestigeRank`` (0 = most prestigious, contiguous 0..n-1). ``TaxonomyLevel`` values as in v1
  (Academia / Domain / Field); ``TaxonomyValue`` = the 2026 (published) taxonomy names, so the v1 renames apply
  (``src/crosswalks/fields.py``: ``WAPMAN_FIELD_RENAMES_2026``, ``WAPMAN_DOMAIN_RENAMES_2026``).
* ``edge_lists.csv`` - ``Total, Women, Men, DegreeInstitutionId, DegreeInstitutionName, InstitutionId,
  InstitutionName, TaxonomyValue, TaxonomyLevel`` (ids as floats, counts as integers, as in v1). Default
  ``edges="network"``: the rows of ``edge-lists.csv`` whose employing AND doctoral institution are both ranked in
  that network - the network the published ranks are computed on (SpringRank, alpha = 1e-3, on exactly these rows
  reproduces ``OrdinalPrestigeRank`` with Spearman >= 0.9997 in all 116 networks; ``check()`` recomputes this).
  The v1 file was also (almost) restricted to US ranked institutions at both ends (8 of its 319 doctoral ids were
  unranked); the 2026 file adds every doctorate origin, including non-US ones. ``edges="universe"`` keeps rows
  whose two ends are ranked in any network; ``edges="all"`` keeps all 405,410 rows.
* ``InstitutionName`` - the institution ids are the same in both releases (every one of the 356 shared ids
  carries the same institution under a v1 long name and a 2026 short name, e.g. 82 'Georgia Institute of
  Technology' / 'Georgia Tech'), and the whole name join to College Scorecard / PSEO / IPEDS (scripts/55, 59, 75,
  78 and src/crosswalks/institutions.py) is keyed on the v1 long names. The name of an id is therefore its v1
  name (v1 ranks.csv, else v1 edge_lists.csv); ids absent from v1 keep the 2026 name (listed in the README).
* ``stats.csv``, ``institution-stats.csv``, ``yearly-stats.csv`` - the 2026 files, copied unchanged. Their columns
  are a superset of the v1 columns the scripts read (scripts/56: stats.csv ``Doctorate (US)``, ``SelfHires``;
  scripts/75: institution-stats.csv ``TaxonomyLevel, TaxonomyValue, OrdinalPrestigeRank, ProductionRank``), but
  some meanings changed (upstream changelog): attrition columns are now in explicit faculty / faculty-year units,
  ``ProductionRank`` is blank for ranked institutions that produced no faculty in the network, the empirical
  ``FractionUpHierarchyHires`` is restored, and institution-stats.csv now has every ranked institution and its
  ids (v1: 9,832 rows, no id columns).
* ``RELEASE`` - a one-line marker read by :func:`current_release` (scripts gate their v1-only reproduction
  asserts on it); ``README.md`` - says the directory is generated and how.

Run:  python -m src.wapman_release [--edges network|universe|all] [--check]
The output is deterministic (fixed sort order, fixed float format): a re-run writes byte-identical files.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SRC_DIR = RAW / "wapman2026"           # upstream 2026 files (upstream names)
V1_DIR = RAW / "wapman2022_v1"         # archived Zenodo v1 files (names by id)
OUT_DIR = RAW / "wapman2022"           # generated: what every script reads
UPSTREAM = "LarremoreLab/us-faculty-hiring-networks"
UPSTREAM_COMMIT = "841e9c96f949677aadbffded10a002586ff65cc4"
UPSTREAM_DATE = "2026-08-22"
RELEASE_2026 = "wapman2026"
RELEASE_V1 = "v1"
COPY_AS_IS = ("stats.csv", "institution-stats.csv", "yearly-stats.csv")
LEVEL_ORDER = {"Academia": 0, "Domain": 1, "Field": 2}


# ---------------------------------------------------------------------------------------------------------
# release flag (read by scripts that pin v1 reproduction values)
# ---------------------------------------------------------------------------------------------------------
def current_release(wapman_dir: Path = OUT_DIR) -> str:
    """'wapman2026' if data/raw/wapman2022/ was generated by this module, else 'v1' (the Zenodo v1 files)."""
    p = Path(wapman_dir) / "RELEASE"
    if p.exists():
        tok = p.read_text(encoding="utf-8").split()
        if tok:
            return tok[0]
    return RELEASE_V1


def is_v1(wapman_dir: Path = OUT_DIR) -> bool:
    return current_release(wapman_dir) == RELEASE_V1


def v1_assert(cond, msg: str = "") -> None:
    """A check pinned to the v1 run (a published v1 number, a v1 sample size, or a condition the script's fixed
    wording relies on). Under the v1 release it is the original hard assert. Under the 2026 release it does not
    stop the script; a check that is not met is printed as '[wapman2026] v1-pinned check not met: ...' so every
    such case can be listed."""
    if is_v1():
        assert cond, msg
    elif not cond:
        print(f"[wapman2026] v1-pinned check not met: {msg}", flush=True)


def with_release_note(md: str) -> str:
    """Result write-ups: unchanged under v1; under the 2026 release a fixed note is inserted after the title line
    saying which data and which name join produced the file and that fixed v1 wording was not rewritten."""
    if is_v1():
        return md
    from .crosswalks.institutions import namejoin_mode
    note = ("> **Wapman 2026 re-baseline (generated note).** Regenerated by this script on the 2026 upstream "
            "regeneration of the Wapman et al. data (`data/raw/wapman2026/`, written in the v1 formats to "
            "`data/raw/wapman2022/` by `src/wapman_release.py`); Wapman-Scorecard name join: "
            f"`{namejoin_mode()}` (`src/crosswalks/wapman_ipeds_aliases.csv`). Every number is recomputed. Fixed "
            "sentences written for the v1 run (headings, verdict and sample-size words, statements about the v1 "
            "edge list) were not rewritten and may no longer hold; checks pinned to v1 values that are not met are "
            "printed in the run log"
            ".\n")
    head, sep, rest = md.partition("\n")
    return head + sep + "\n" + note + ("\n" + rest if rest else "")


# ---------------------------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------------------------
def v1_names(v1_dir: Path = V1_DIR) -> pd.Series:
    """InstitutionId -> v1 InstitutionName (ranks.csv first, then both ends of edge_lists.csv); one name per id."""
    r = pd.read_csv(v1_dir / "ranks.csv")
    e = pd.read_csv(v1_dir / "edge_lists.csv")
    parts = [r[["InstitutionId", "InstitutionName"]],
             e[["InstitutionId", "InstitutionName"]],
             e[["DegreeInstitutionId", "DegreeInstitutionName"]].set_axis(["InstitutionId", "InstitutionName"], axis=1)]
    m = pd.concat(parts, ignore_index=True).dropna()
    m["InstitutionId"] = m.InstitutionId.astype(np.int64)
    m = m.drop_duplicates()
    assert not m.InstitutionId.duplicated().any(), "a v1 institution id carries two names"
    return m.set_index("InstitutionId").InstitutionName.sort_index()


def _name_map(ids, names26: pd.Series, v1: pd.Series) -> pd.Series:
    ids = pd.Index(sorted(set(int(i) for i in ids)))
    return pd.Series([v1.get(i, names26.get(i)) for i in ids], index=ids)


def build(edges: str = "network", src_dir: Path = SRC_DIR, v1_dir: Path = V1_DIR,
          out_dir: Path = OUT_DIR) -> dict:
    assert edges in ("network", "universe", "all"), edges
    ist = pd.read_csv(src_dir / "institution-stats.csv")
    el = pd.read_csv(src_dir / "edge-lists.csv")
    assert el.DegreeInstitutionId.notna().all() and (el.Total >= 1).all()
    v1 = v1_names(v1_dir)
    n26 = pd.concat([ist[["InstitutionId", "InstitutionName"]], el[["InstitutionId", "InstitutionName"]],
                     el[["DegreeInstitutionId", "DegreeInstitutionName"]].set_axis(
                         ["InstitutionId", "InstitutionName"], axis=1)]).drop_duplicates()
    assert not n26.InstitutionId.duplicated().any(), "a 2026 institution id carries two names"
    n26 = n26.set_index("InstitutionId").InstitutionName

    # ---- ranks.csv ----
    r = ist[["OrdinalPrestigeRank", "InstitutionId", "TaxonomyValue", "TaxonomyLevel"]].copy()
    names = _name_map(r.InstitutionId, n26, v1)
    r["InstitutionName"] = r.InstitutionId.map(names)
    r["_lv"] = r.TaxonomyLevel.map(LEVEL_ORDER)
    assert r._lv.notna().all()
    r = r.sort_values(["_lv", "TaxonomyValue", "OrdinalPrestigeRank"], kind="mergesort")
    g = r.groupby(["TaxonomyLevel", "TaxonomyValue"]).OrdinalPrestigeRank
    assert (g.min() == 0).all() and ((g.max() + 1) == g.size()).all() and not r.duplicated(
        ["TaxonomyLevel", "TaxonomyValue", "OrdinalPrestigeRank"]).any(), "OrdinalPrestigeRank not contiguous"
    ranks = pd.DataFrame({"Rank": r.OrdinalPrestigeRank.astype(np.int64),
                          "InstitutionId": r.InstitutionId.astype(float),
                          "InstitutionName": r.InstitutionName,
                          "TaxonomyValue": r.TaxonomyValue, "TaxonomyLevel": r.TaxonomyLevel})

    # ---- edge_lists.csv ----
    e = el.copy()
    if edges == "network":
        key = ist[["TaxonomyLevel", "TaxonomyValue", "InstitutionId"]]
        e = e.merge(key, on=["TaxonomyLevel", "TaxonomyValue", "InstitutionId"], how="inner")
        e = e.merge(key.rename(columns={"InstitutionId": "DegreeInstitutionId"}),
                    on=["TaxonomyLevel", "TaxonomyValue", "DegreeInstitutionId"], how="inner")
    elif edges == "universe":
        univ = set(ist.InstitutionId)
        e = e[e.InstitutionId.isin(univ) & e.DegreeInstitutionId.isin(univ)]
    enames = _name_map(pd.concat([e.InstitutionId, e.DegreeInstitutionId]), n26, v1)
    e = e.assign(_lv=e.TaxonomyLevel.map(LEVEL_ORDER),
                 InstitutionName=e.InstitutionId.map(enames),
                 DegreeInstitutionName=e.DegreeInstitutionId.map(enames))
    e = e.sort_values(["_lv", "TaxonomyValue", "DegreeInstitutionId", "InstitutionId"], kind="mergesort")
    edges_df = pd.DataFrame({"Total": e.Total.astype(np.int64), "Women": e.Women.astype(np.int64),
                             "Men": e.Men.astype(np.int64),
                             "DegreeInstitutionId": e.DegreeInstitutionId.astype(float),
                             "DegreeInstitutionName": e.DegreeInstitutionName,
                             "InstitutionId": e.InstitutionId.astype(float), "InstitutionName": e.InstitutionName,
                             "TaxonomyValue": e.TaxonomyValue, "TaxonomyLevel": e.TaxonomyLevel})

    # ---- write ----
    out_dir.mkdir(parents=True, exist_ok=True)
    ranks.to_csv(out_dir / "ranks.csv", index=False)
    edges_df.to_csv(out_dir / "edge_lists.csv", index=False)
    for f in COPY_AS_IS:
        shutil.copyfile(src_dir / f, out_dir / f)
    info = dict(edges=edges, n_ranks=len(ranks), n_edges=len(edges_df), hires=int(edges_df.Total.sum()),
                n_networks=int(ranks.groupby(["TaxonomyLevel", "TaxonomyValue"]).ngroups),
                ids_ranked=int(ranks.InstitutionId.nunique()),
                ids_2026_name=sorted(int(i) for i in names.index if i not in v1.index),
                ids_v1_dropped=sorted(int(i) for i in set(pd.read_csv(v1_dir / "ranks.csv").InstitutionId.dropna()
                                                          .astype(np.int64)) - set(ist.InstitutionId)),
                n26=n26, v1=v1)
    (out_dir / "RELEASE").write_text(
        f"{RELEASE_2026} {UPSTREAM}@{UPSTREAM_COMMIT[:7]} {UPSTREAM_DATE} edges={edges}\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_readme(info, src_dir, out_dir), encoding="utf-8")
    return info


def _md5(p: Path) -> str:
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def _readme(info: dict, src_dir: Path, out_dir: Path) -> str:
    n26, v1 = info["n26"], info["v1"]
    new = "\n".join(f"  - {i}: {n26.get(i)}" for i in info["ids_2026_name"])
    drop = "\n".join(f"  - {i}: {v1.get(i, '(no v1 name)')}" for i in info["ids_v1_dropped"])
    files = "\n".join(f"  - `{f}` md5 `{_md5(out_dir / f)}`" for f in ("ranks.csv", "edge_lists.csv") + COPY_AS_IS)
    srcs = "\n".join(f"  - `{f}` md5 `{_md5(src_dir / f)}`"
                     for f in ("edge-lists.csv", "institution-stats.csv", "stats.csv", "yearly-stats.csv"))
    return f"""# data/raw/wapman2022/ — GENERATED, do not edit

This directory is written by `src/wapman_release.py` (`python -m src.wapman_release`) from the
upstream 2026 regeneration in `data/raw/wapman2026/` ({UPSTREAM}, commit {UPSTREAM_COMMIT[:7]}, {UPSTREAM_DATE}).
It keeps the v1 (Zenodo 10.5281/zenodo.6941651) file names and column formats so every script runs unchanged.
The original v1 files are in `data/raw/wapman2022_v1/`. Provenance: `data/sources.csv`, section 1.

- `ranks.csv`: {info['n_ranks']:,} rows, {info['n_networks']} networks, {info['ids_ranked']} ranked institutions.
  `Rank` = published `OrdinalPrestigeRank` (0 = most prestigious). `TaxonomyValue` = 2026 (published) taxonomy.
- `edge_lists.csv`: {info['n_edges']:,} rows, {info['hires']:,} faculty, edges mode `{info['edges']}`
  (`network` = rows whose employing and doctoral institutions are both ranked in that network; the published
  ranks are SpringRank on exactly these rows). No Total threshold (Total >= 1).
- `InstitutionName` = the v1 name of the same `InstitutionId` (ids are stable across the releases); ids with no
  v1 name keep their 2026 name:
{new}
- v1-ranked institutions that are not ranked in any 2026 network:
{drop}
- `stats.csv`, `institution-stats.csv`, `yearly-stats.csv`: the 2026 files, unchanged (see the upstream
  changelog for changed column meanings).
- `RELEASE`: marker read by `src.wapman_release.current_release()`.

Generated files:
{files}

Inputs (`data/raw/wapman2026/`):
{srcs}
"""


# ---------------------------------------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------------------------------------
def check(out_dir: Path = OUT_DIR, src_dir: Path = SRC_DIR) -> pd.DataFrame:
    """Recompute SpringRank (alpha = 1e-3, self-hires dropped) on every network of the generated edge list and
    compare it with the published rank; check the crosswalk field names against the generated ranks."""
    import importlib.util
    from scipy.sparse import csr_matrix
    from scipy.stats import spearmanr
    from .ar_pipeline.springrank import springrank
    from .crosswalks import fields as F

    r = pd.read_csv(out_dir / "ranks.csv")
    e = pd.read_csv(out_dir / "edge_lists.csv")
    rows = []
    for (lv, tv), g in r.groupby(["TaxonomyLevel", "TaxonomyValue"]):
        d = e[(e.TaxonomyLevel == lv) & (e.TaxonomyValue == tv) & (e.DegreeInstitutionId != e.InstitutionId)]
        ids = np.array(sorted(set(d.DegreeInstitutionId) | set(d.InstitutionId)))
        pos = {v: i for i, v in enumerate(ids)}
        A = csr_matrix((d.Total.to_numpy(float), (d.DegreeInstitutionId.map(pos), d.InstitutionId.map(pos))),
                       shape=(len(ids), len(ids)))
        s = pd.Series(springrank(A, alpha=1e-3), index=ids)
        gi = g.set_index("InstitutionId").Rank
        c = gi.index.intersection(s.index)
        rows.append(dict(level=lv, value=tv, n_ranked=len(gi), n_in_edges=len(c),
                         rho=float(spearmanr(s[c], -gi[c])[0])))
    res = pd.DataFrame(rows)
    spec = importlib.util.spec_from_file_location("cw24", ROOT / "scripts" / "24_crosswalk_audit.py")
    cw24 = importlib.util.module_from_spec(spec); spec.loader.exec_module(cw24)
    have = set(r[r.TaxonomyLevel == "Field"].TaxonomyValue)
    missing = sorted({f["wapman_field"] for f in F.ALL_FIELDS + cw24.RECOVER} - have)
    assert set(missing) <= set(F.WAPMAN_FIELDS_DROPPED_2026), f"crosswalk field not in ranks.csv: {missing}"
    print(f"networks {len(res)}; Spearman(public-edge SpringRank, published rank): min {res.rho.min():.5f}, "
          f"median {res.rho.median():.6f}; ranked institutions without a non-self edge: "
          f"{int((res.n_ranked - res.n_in_edges).sum())}; crosswalk fields absent from ranks.csv: {missing}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", default="network", choices=["network", "universe", "all"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    info = build(edges=a.edges)
    print(f"wrote {OUT_DIR}: ranks {info['n_ranks']:,} rows, edges {info['n_edges']:,} rows / {info['hires']:,} "
          f"faculty ({info['edges']}); 2026-only names: {len(info['ids_2026_name'])}; "
          f"v1 ids dropped: {len(info['ids_v1_dropped'])}")
    for f in ("ranks.csv", "edge_lists.csv") + COPY_AS_IS + ("RELEASE", "README.md"):
        print(f"  {f} {_md5(OUT_DIR / f)}")
    if a.check:
        check()


if __name__ == "__main__":
    main()
