"""Wapman-matched UNITIDs that share an OPEID6 in Scorecard FoS: identical pooled earnings across ranked campuses?"""
import os, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ["GAP_NAMEJOIN"] = "repaired"
from src.crosswalks import institutions as I

R = str(__import__("pathlib").Path(__file__).resolve().parents[2]) + "/data/raw/"
fos = pd.read_csv(R + "scorecard_fos/Most-Recent-Cohorts-Field-of-Study.csv",
                  usecols=["UNITID", "OPEID6", "INSTNM", "CIPCODE", "CREDLEV", "EARN_MDN_4YR"], dtype=str)
rk = pd.read_csv(R + "wapman2022/ranks.csv")
wn = rk.drop_duplicates("InstitutionId").set_index(rk.drop_duplicates("InstitutionId").InstitutionId.astype(int)).InstitutionName
wk = {I.normalize_institution_name(n): w for w, n in wn.items()}
u = fos.drop_duplicates("UNITID").copy()
u["wid"] = u.INSTNM.map(I.normalize_institution_name).map(wk)
mu = u.dropna(subset=["wid"])
g = mu.groupby("OPEID6").wid.nunique()
multi = g[g > 1].index
print("OPEID6 groups with >1 Wapman-matched UNITID:", len(multi))
os.environ["GAP_NAMEJOIN"] = "v1"; I._repair_map.cache_clear()
wk1 = {I.normalize_institution_name(n): w for w, n in wn.items()}
u["wid_v1"] = u.INSTNM.map(I.normalize_institution_name).map(wk1)
b = fos[(fos.CREDLEV == "3")].copy()
b["e"] = pd.to_numeric(b.EARN_MDN_4YR, errors="coerce")
for o in multi:
    s = mu[mu.OPEID6 == o]
    print(f"OPEID6 {o}:", [(r.UNITID, r.INSTNM, int(r.wid), "v1-matched" if pd.notna(u.set_index('UNITID').wid_v1.get(r.UNITID)) else "added by repair") for r in s.itertuples()])
    bb = b[b.UNITID.isin(s.UNITID)].pivot_table(index="CIPCODE", columns="UNITID", values="e")
    ids = list(s.UNITID)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            x = bb[[ids[i], ids[j]]].dropna() if ids[i] in bb and ids[j] in bb else pd.DataFrame()
            if len(x):
                print(f"   {ids[i]} vs {ids[j]}: shared bachelor CIPs with 4-yr medians {len(x)}, identical {int((x.iloc[:,0]==x.iloc[:,1]).sum())}")
