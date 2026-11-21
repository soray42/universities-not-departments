"""Institution-name normalization for joining Wapman prestige (named institutions)
to College Scorecard (``UNITID`` / ``INSTNM``).

The Wapman Zenodo tables key institutions by name; Scorecard keys by IPEDS ``UNITID``
with an ``INSTNM`` string. There is no shared numeric id, so the Tier-0 join is on a
normalized name. This module centralizes that normalization plus a small alias table
for the handful of names that differ in surface form across the two sources.

Keep this conservative: it is better to drop an ambiguous institution from the
within-field correlation than to mis-join it. The scripts report match rates and
unmatched names so coverage is auditable.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

# Common surface-form differences (normalized-key -> canonical normalized-key).
# Extend as the Tier-0 unmatched list reveals real cases.
_ALIASES: dict[str, str] = {
    "mit": "massachusetts institute of technology",
    "caltech": "california institute of technology",
    "uc berkeley": "university of california berkeley",
    "uc los angeles": "university of california los angeles",
    "ucla": "university of california los angeles",
    "penn": "university of pennsylvania",
    "upenn": "university of pennsylvania",
    "uiuc": "university of illinois urbana champaign",
    "university of illinois at urbana champaign": "university of illinois urbana champaign",
    "ohio state": "ohio state university",
    "the ohio state university": "ohio state university",
    "texas a m university": "texas a and m university",
    "suny stony brook": "stony brook university",
    "university of texas at austin": "university of texas austin",
    "university of michigan ann arbor": "university of michigan",
    "university of wisconsin madison": "university of wisconsin",
    "university of minnesota twin cities": "university of minnesota",
}

# Tokens stripped as noise during normalization.
_STOPWORDS = {"the", "at", "of", "and"}


# ---------------------------------------------------------------------------------------------------------
# Wapman <-> IPEDS name-join repair (UNITID-anchored, explicit, switchable).
# src/crosswalks/wapman_ipeds_aliases.csv lists every Wapman-ranked institution whose name has no exact
# normalised match among the College Scorecard FoS names (77 of 368 under the 2026 release): 65 are paired
# with one IPEDS UNITID, checked by hand against the official HD2023 / HD2019 names, IALIAS, city, state and
# Carnegie class and against the other Wapman institutions of the same system (column `evidence`); 12 are
# left unmatched (no unique UNITID; reason given). For a paired row, the normalised official names of that
# UNITID (HD2023, HD2019 and the Scorecard FoS INSTNM) map to the Wapman institution's key, so any source that
# carries the official name (Scorecard FoS / institution files, IPEDS) joins to Wapman; Wapman keys themselves
# are unchanged. No generic suffix stripping is done. verify_wapman_ipeds_aliases() re-checks every pair
# against the raw files (names, one UNITID per key, no collision with another institution).
# Switch: environment variable GAP_NAMEJOIN=v1 turns the repair off (the pre-2026 join, for comparisons).
# ---------------------------------------------------------------------------------------------------------
ALIAS_CSV = Path(__file__).resolve().parent / "wapman_ipeds_aliases.csv"
NAMEJOIN_ENV = "GAP_NAMEJOIN"


def namejoin_mode() -> str:
    """'repaired' (default) or 'v1' (the pre-repair exact-name join), from $GAP_NAMEJOIN."""
    m = os.environ.get(NAMEJOIN_ENV, "repaired").strip().lower()
    assert m in ("repaired", "v1"), f"{NAMEJOIN_ENV} must be 'repaired' or 'v1', not {m!r}"
    return m


def wapman_ipeds_aliases():
    """The curated table (pandas DataFrame; rows with kind 'left unmatched' have no UNITID)."""
    import pandas as pd
    return pd.read_csv(ALIAS_CSV, dtype=str, keep_default_na=False)


@lru_cache(maxsize=1)
def _repair_map() -> dict:
    import csv
    out: dict[str, str] = {}
    with open(ALIAS_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r["unitid"]:
                continue
            tgt = _base_key(r["wapman_name"])
            for src in (r["ipeds_name_hd2023"], r["ipeds_name_hd2019"], r["scorecard_fos_name"]):
                k = _base_key(src)
                if k and k != tgt:
                    assert out.get(k, tgt) == tgt, f"alias source {src!r} maps to two Wapman institutions"
                    out[k] = tgt
    return out


def normalize_institution_name(name: str) -> str:
    """Return a normalized key for an institution name.

    Steps: lowercase; map '&'->'and'; drop punctuation; drop generic stopwords
    ('the','at','of','and'); collapse whitespace; apply the alias table. The result
    is a stable key to join Wapman names against Scorecard ``INSTNM``. Unless
    GAP_NAMEJOIN=v1, the official IPEDS names of the UNITIDs in wapman_ipeds_aliases.csv
    then map to the key of their Wapman institution (see above).
    """
    key = _base_key(name)
    if key and namejoin_mode() == "repaired":
        return _repair_map().get(key, key)
    return key


def _base_key(name: str) -> str:
    """The pre-repair normaliser (unchanged since Tier 0)."""
    if not isinstance(name, str):
        return ""
    s = name.lower().strip()
    s = s.replace("&", " and ")
    s = s.replace("-", " ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)        # drop punctuation
    s = re.sub(r"\s+", " ", s).strip()
    if s in _ALIASES:                          # alias on the pre-stopword form too
        s = _ALIASES[s]
    tokens = [t for t in s.split(" ") if t not in _STOPWORDS]
    key = " ".join(tokens)
    return _ALIASES.get(key, key)


def verify_wapman_ipeds_aliases(raw_dir=None) -> dict:
    """Re-check every paired row of wapman_ipeds_aliases.csv against the raw files: the UNITID exists in HD2023
    and in the Scorecard FoS file with exactly the recorded names (HD2019 too, where recorded); the Wapman name
    is in the generated ranks.csv under that wapman_id; each alias source key belongs to that UNITID only among
    all FoS UNITIDs; no Wapman id or UNITID is used twice; and, with the repair on, every Wapman key maps to
    at most one FoS UNITID. Returns match counts with the repair off and on."""
    import zipfile
    import pandas as pd
    root = Path(__file__).resolve().parents[2]
    raw = Path(raw_dir) if raw_dir else root / "data" / "raw"
    t = wapman_ipeds_aliases()
    p = t[t.unitid != ""]
    assert not p.wapman_id.duplicated().any() and not p.unitid.duplicated().any()

    def _hd(path, member, enc):
        with zipfile.ZipFile(path) as z:
            d = pd.read_csv(z.open(member), dtype=str, encoding=enc, encoding_errors="replace",
                            usecols=lambda c: c.strip().lstrip("\ufeff").upper() in ("UNITID", "INSTNM"))
        d.columns = [c.strip().lstrip("\ufeff").upper() for c in d.columns]
        return d.set_index("UNITID").INSTNM
    hd23 = _hd(raw / "local_demand_geo" / "HD2023.zip", "HD2023.csv", "utf-8-sig")
    hd19 = _hd(raw / "ipeds_hd" / "HD2019.zip", "hd2019.csv", "latin-1")
    fos = pd.read_csv(raw / "scorecard_fos" / "Most-Recent-Cohorts-Field-of-Study.csv",
                      usecols=["UNITID", "INSTNM"], dtype=str).dropna().drop_duplicates()
    assert not fos.UNITID.duplicated().any()
    fosn = fos.set_index("UNITID").INSTNM
    rk = pd.read_csv(raw / "wapman2022" / "ranks.csv", usecols=["InstitutionId", "InstitutionName"]).drop_duplicates()
    rk = dict(zip(rk.InstitutionId.astype(int).astype(str), rk.InstitutionName))
    for r in p.itertuples():
        assert hd23.get(r.unitid) == r.ipeds_name_hd2023, (r.wapman_id, r.unitid, "HD2023 name")
        assert fosn.get(r.unitid) == r.scorecard_fos_name, (r.wapman_id, r.unitid, "FoS name")
        assert r.ipeds_name_hd2019 == "" or hd19.get(r.unitid) == r.ipeds_name_hd2019, (r.wapman_id, "HD2019")
        assert rk.get(r.wapman_id) == r.wapman_name, (r.wapman_id, "Wapman name")
    for r in t[t.unitid == ""].itertuples():
        assert rk.get(r.wapman_id) == r.wapman_name, (r.wapman_id, "Wapman name")
    base = fos.assign(k=fos.INSTNM.map(_base_key))
    units = base.groupby("k").UNITID.apply(set)
    for r in p.itertuples():
        for src in (r.ipeds_name_hd2023, r.ipeds_name_hd2019, r.scorecard_fos_name):
            k = _base_key(src)
            if k:
                assert units.get(k, set()) <= {r.unitid}, (r.wapman_id, src, "key shared with another UNITID")
    wk = {_base_key(n) for n in rk.values()}
    rep = _repair_map()
    base["k2"] = base.k.map(lambda k: rep.get(k, k))
    n2 = base.groupby("k2").UNITID.nunique()
    assert (n2[n2.index.isin(wk)] <= 1).all(), "a Wapman key maps to more than one UNITID"
    return dict(n_wapman=len(wk), matched_v1=int(sum(k in set(base.k) for k in wk)),
                matched_repaired=int(sum(k in set(base.k2) for k in wk)), n_pairs=len(p),
                n_left=int((t.unitid == "").sum()))


def build_name_index(names) -> dict[str, str]:
    """Map normalized-key -> original name, for an iterable of institution names.
    Later duplicates are kept under their key (last wins); collisions are rare after
    normalization and surfaced by the caller comparing index size to input size."""
    return {normalize_institution_name(n): n for n in names if isinstance(n, str) and n.strip()}
