"""Paper check (2026-11-15): US sample-flow counts for the SI sample-flow table, from the independent rebuild of the
scripts/55/58 cells by c_headline.py (paper_checks_cells_repaired.csv; 2026 release, repaired join) and the gap map
of scripts/24 (outputs/expanded66_gap_map.csv).
Run: python scripts/paper_checks/sample_flow.py (after c_headline.py)"""
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
c = pd.read_csv(ROOT / "data/interim/paper_checks_cells_repaired.csv")
print(f"matched (field x university, released 4-yr median): {len(c)} programmes, {c.inst_key.nunique()} universities, "
      f"{c.field.nunique()} fields")
g = pd.read_csv(ROOT / "outputs" / "expanded66_gap_map.csv")
print(f"gap map: {len(g)} rows, {int(g.n_institutions.sum())} programmes; fields with >= 15 universities "
      f"{int((g.n_institutions >= 15).sum())} ({int(g.n_institutions[g.n_institutions >= 15].sum())} programmes); "
      f">= 8: {int((g.n_institutions >= 8).sum())}")
k = c.groupby("field").inst_key.transform("size")
cc = c[k >= 15]
print(f"canonical (fields with >= 15 universities): {len(cc)} programmes, {cc.inst_key.nunique()} universities, "
      f"{cc.field.nunique()} fields")
