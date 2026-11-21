"""Main-text figures 2 and 3 of the paper (paper/nhb/main.tex).

Draws only. Nothing is re-estimated and no random number is drawn. Every plotted number is read from a table that an
analysis script wrote (data/interim/*.csv) or from a table row of a result file (*_RESULT.md), selected by an exact
key with an assertion that exactly one row matches, and asserted against the value the paper or its SI table
prints, to the printed precision. The asserts are hard: the paper's values are those of the 2026 Wapman release with
the repaired name join, so the script stops under any other release.

Style: scripts/figstyle.py, shared with scripts/83_nexus_figures.py (Figs. 1, 4 and 5).

Figures (vector PDF + 300-dpi PNG in outputs/figures/wapman2026/):
  nexus_fig_academic  Fig. 2, academic information inside a university (scripts/85,
                      data/interim/positive_control_prediction_summary.csv).
      A  within-university correlations of the department hiring rank F with NRC research measures, beside the
         within-university correlation of F with four-year pay on the same programmes; 95% university-cluster
         bootstrap intervals (2,000 draws). Rows: section P1 (primary cells: FE-only base, same-name fields, one
         programme) and the revision-2 row that controls allocated faculty and PhDs graduated (section P1 sens.).
      B  gain in out-of-sample R^2 of log four-year pay: F with field-specific slopes (pre-specified), and the
         post hoc, exploratory decomposition (field-specific slopes on G alone; the mean z(F) of the university's
         other programmes; the department's deviation z(F) - mean z(F), one slope), for task 1 (whole universities
         held out) and task 2 (one programme held out within a university); university-cluster bootstrap intervals.
  nexus_fig_gradient  Fig. 3, what the department adds: the pay gradient per within-field SD.
      A  US, 4,645 programmes: slope with field fixed effects only (across universities; SELECTIVITY_RESULT.md gives
         a point estimate and a CR1 SE to 3 decimals, so it is drawn as a point) and with university and field fixed
         effects (SELECTIVITY_DEEP_RESULT.md, 999-draw university bootstrap).
      B  within-university slopes: US university + field FE; main specification (gap_checks_summary.csv, G1 main);
         main plus the production rank (G1 rev. 1); main divided by the reliability of residual F, public-edge and
         extrapolated (SELECTIVITY_DEEP_RESULT.md, main row, column beta / lambda; points only). UK (uk_triad_summary.csv,
         scripts/76): REF 2021 with provider and subject FE and with subject slopes on G and selectivity (cluster
         bootstrap), REF 2014 (cluster-robust CR1 interval, dashed), the intervals Table S of the SI prints.

Run: python scripts/86_nexus_figures_extra.py (a re-run writes byte-identical files).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from src.wapman_release import is_v1 as _wapman_is_v1                       # noqa: E402
import figstyle as fs                                                         # noqa: E402

import matplotlib.pyplot as plt                                               # noqa: E402
from matplotlib.lines import Line2D                                           # noqa: E402

INTERIM = ROOT / "data" / "interim"
FIGDIR = ROOT / "outputs" / "figures" / "wapman2026"
MM = fs.MM
fs.apply()

if _wapman_is_v1():
    raise SystemExit("scripts/86 draws the values of the 2026 Wapman release; data/raw/wapman2022 is v1")


def near(a, b, nd, what):
    """hard check: a value read from a table prints as the value b of the paper (or SI table) at nd decimals"""
    assert round(a, nd) == round(b, nd) or abs(a - b) <= 0.5 * 10 ** -nd + 1e-12, f"{what}: {a!r} vs paper {b!r}"


def one(df, what, **keys):
    x = df
    for col, val in keys.items():
        x = x[x[col] == val]
    assert len(x) == 1, f"{what}: {keys} matched {len(x)} rows"
    return x.iloc[0]


def md_row(path, pattern, what):
    """the single line of a result file that matches a regular expression (anchored, whole line)"""
    hits = re.findall(pattern, (ROOT / path).read_text(encoding="utf-8"), flags=re.M)
    assert len(hits) == 1, f"{what}: {len(hits)} matching lines in {path}"
    return hits[0]


# ------------------------------------------------------------------------------------------------------------------
# Fig. 2: academic information inside a university (scripts/85)
# ------------------------------------------------------------------------------------------------------------------
def fig_academic():
    P = pd.read_csv(INTERIM / "positive_control_prediction_summary.csv")
    PRIM = "FE-only base, same-name fields, one programme"
    CTRL = "+ normal scores of allocated faculty and PhDs graduated as controls"
    # label, NRC measure name in the table, paper / SI-table values (measure est, lo, hi; pay est, lo, hi)
    measures = [
        ("Publications per faculty (primary)", "publications per allocated faculty",
         (0.187, 0.135, 0.241), (0.037, -0.019, 0.096)),                       # PC1
        ("Citations per publication", "citations per publication",
         (0.156, 0.093, 0.219), (0.038, -0.026, 0.101)),                       # PC1 / SI Table P1
        ("Share of faculty with grants", "share of faculty with grants",
         (0.112, 0.055, 0.168), (0.038, -0.019, 0.097)),
        ("Awards per faculty", "awards per allocated faculty",
         (0.188, 0.125, 0.251), (0.037, -0.020, 0.099)),
        ("NRC R-ranking", "R-ranking midpoint (sign reversed)",
         (0.401, 0.351, 0.446), (0.035, -0.023, 0.094)),
        ("NRC S-ranking", "S-ranking midpoint (sign reversed)",
         (0.279, 0.225, 0.328), (0.035, -0.022, 0.094)),
        ("NRC research-activity ranking", "research-activity ranking midpoint (sign reversed)",
         (0.225, 0.170, 0.281), (0.035, -0.023, 0.095)),
    ]
    rowsA = []
    for lab, m, sm, sp in measures:
        rm = one(P, lab, section="P1", quantity=f"within(F, {m})", specification=PRIM)
        rp = one(P, lab + " (pay)", section="P1", quantity=f"within(F, pay) on the {m} cells", specification="same cells")
        assert rm.ci_kind == "bootstrap" and rp.ci_kind == "bootstrap" and rm["sample"] == rp["sample"], lab
        for got, want, w in zip((rm.est, rm.lo, rm.hi, rp.est, rp.lo, rp.hi), sm + sp,
                                ("est", "lo", "hi", "pay est", "pay lo", "pay hi")):
            near(float(got), want, 3, f"{lab} {w}")
        rowsA.append((lab, rm, rp))
    assert rowsA[0][1]["sample"] == "1,484 programmes, 173 universities, 24 fields"
    rm = one(P, "controls", section="P1 sens.", quantity="within(F, publications per allocated faculty)",
             specification=CTRL)
    rp = one(P, "controls (pay)", section="P1 sens.", quantity="within(F, pay) on the same cells", specification=CTRL)
    for got, want, w in zip((rm.est, rm.lo, rm.hi, rp.est), (0.142, 0.089, 0.192, 0.038),
                            ("est", "lo", "hi", "pay est")):
        near(float(got), want, 3, f"controls {w}")                              # PC1 / SI Table P1
    near(float(rp.lo), -0.020, 3, "controls pay lo"); near(float(rp.hi), 0.096, 3, "controls pay hi")
    rowsA.append(("Publications, net of faculty size\nand PhDs graduated", rm, rp))

    # panel B: R^2 gains, task 1 (a new university) and task 2 (a known university)
    T1, T2 = "P2 task 1", "P2 task 2"
    UB = "university bootstrap"
    dev = "gain from the department's deviation z(F) - mean z(F)"
    rowsB = [
        ("F, field-specific slopes", fs.TOTAL,
         one(P, "t1 F", section=T1, quantity="gain from F", specification="U+D minus U (interval of record, revision 2)"),
         one(P, "t2 F", section=T2, quantity="gain from F", specification="with minus without"),
         (0.0136, 0.0082, 0.0188), (0.0159, 0.0113, 0.0207)),
        ("G, field-specific slopes, no F", fs.GRANK,
         one(P, "t1 G", section=T1, quantity="gain from field-specific slopes on G alone (no F)",
             specification="U + field x G"),
         one(P, "t2 G", section=T2, quantity="gain from field-specific slopes on G alone (no F)",
             specification="+ field x G"),
         (0.0142, 0.0083, 0.0199), (0.0144, 0.0092, 0.0198)),
        ("University part of F: mean F of\nthe university's other programmes", fs.ACROSS,
         one(P, "t1 mean", section=T1, quantity="gain from the mean z(F) of the university's other programmes",
             specification="field-specific slopes (university part of F)"),
         one(P, "t2 mean", section=T2, quantity="gain from the other programmes' mean z(F)",
             specification="field-specific slopes (university part of F)"),
         (0.0165, 0.0104, 0.0224), (0.0164, 0.0109, 0.0221)),
        ("Department's own deviation\nfrom that mean", fs.WITHIN,
         one(P, "t1 dev", section=T1, quantity=dev, specification="one common slope"),
         one(P, "t2 dev", section=T2, quantity=dev, specification="one common slope"),
         (0.0002, -0.0002, 0.0006), (0.0014, 0.0005, 0.0023)),
    ]
    for lab, col, r1, r2, s1, s2 in rowsB:                                       # PC2 / SI Table P2
        assert r1.ci_kind == UB and r2.ci_kind == UB, lab
        for r, s, t in ((r1, s1, "task 1"), (r2, s2, "task 2")):
            for got, want, w in zip((r.est, r.lo, r.hi), s, ("est", "lo", "hi")):
                near(float(got), want, 4, f"{lab} {t} {w}")
    assert rowsB[0][2]["sample"] == "3,961 programmes, 214 universities, 53 fields"
    assert rowsB[0][3]["sample"] == "3,935 programmes, 201 universities, 53 fields"

    fig = plt.figure(figsize=(fs.COL1, 124 * MM), layout="constrained")
    gs = fig.add_gridspec(2, 1, height_ratios=[9.4, 6.6])

    ax = fig.add_subplot(gs[0, 0])
    fs.value_grid(ax, "x")
    n = len(rowsA)
    ys = np.arange(n)[::-1].astype(float)
    ys[-1] -= 0.35                                                  # the control row sits below a thin rule
    d = 0.17
    for y, (lab, rm, rp) in zip(ys, rowsA):
        fs.hinterval(ax, y + d, float(rm.est), float(rm.lo), float(rm.hi), color=fs.RESEARCH, marker="^",
                     s=fs.S_PT + 4)
        fs.hinterval(ax, y - d, float(rp.est), float(rp.lo), float(rp.hi), color=fs.WITHIN, marker="s",
                     s=fs.S_PT - 2)
    ax.axhline((ys[-1] + ys[-2]) / 2, color=fs.DGREY, lw=0.5, ls=(0, (3, 2)))
    ax.axvline(0, color=fs.BLACK, lw=0.6, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rowsA])
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.tick_params(axis="y", length=0, pad=2)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.1, 0.5)
    ax.set_ylim(ys[-1] - 0.55, ys[0] + 0.5)
    ax.set_xticks(np.arange(-0.1, 0.51, 0.1))
    ax.set_xlabel("Correlation within universities")
    ax.legend(handles=[Line2D([], [], marker="^", color=fs.RESEARCH, mec="white", mew=0.4, ms=fs.MS + 0.6,
                              lw=fs.LW_CI, label="F with the NRC research measure"),
                       Line2D([], [], marker="s", color=fs.WITHIN, mec="white", mew=0.4, ms=fs.MS,
                              lw=fs.LW_CI, label="F with graduates' pay, same programmes")],
              loc="upper center", bbox_to_anchor=(0.30, -0.15), ncol=1)
    fs.panel_title(ax, "A", "Research and pay")

    ax = fig.add_subplot(gs[1, 0])
    fs.value_grid(ax, "x")
    nb = len(rowsB)
    ysb = 1.3 * np.arange(nb)[::-1].astype(float)
    ysb[1:] -= 0.45                                                 # the exploratory rows sit below a thin rule
    for y, (lab, col, r1, r2, s1, s2) in zip(ysb, rowsB):
        fs.hinterval(ax, y + d, 100 * float(r1.est), 100 * float(r1.lo), 100 * float(r1.hi), color=col,
                     marker="o")
        fs.hinterval(ax, y - d, 100 * float(r2.est), 100 * float(r2.lo), 100 * float(r2.hi), color=col,
                     marker="o", filled=False)
    ax.axhline((ysb[0] + ysb[1]) / 2, color=fs.DGREY, lw=0.5, ls=(0, (3, 2)))
    ax.text(2.48, (ysb[0] + ysb[1]) / 2 - 0.06, "exploratory decomposition", fontsize=fs.FS_SMALL, color=fs.DGREY,
            style="italic", ha="right", va="top")
    ax.axvline(0, color=fs.BLACK, lw=0.6, zorder=1)
    ax.set_yticks(ysb)
    ax.set_yticklabels([r[0] for r in rowsB])
    for tl, r in zip(ax.get_yticklabels(), rowsB):
        tl.set_color(r[1] if r[1] != fs.GRANK else fs.GRANK_TXT)
    ax.tick_params(axis="y", length=0, pad=2)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.25, 2.5)
    ax.set_ylim(ysb[-1] - 0.55, ysb[0] + 0.5)
    ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0, 2.5])
    ax.set_xlabel("Gain in out-of-sample $R^2$ (points)")
    ax.legend(handles=[Line2D([], [], marker="o", color=fs.DGREY, mec="white", mew=0.4, ms=fs.MS, lw=fs.LW_CI,
                              label="task 1: a new university"),
                       Line2D([], [], marker="o", color=fs.DGREY, mfc="white", mec=fs.DGREY, mew=0.9, ms=fs.MS,
                              lw=fs.LW_CI, label="task 2: a known university")],
              loc="upper center", bbox_to_anchor=(0.30, -0.22), ncol=2, columnspacing=1.0)
    fs.panel_title(ax, "B", "Predicting pay")
    fs.save(fig, FIGDIR, "nexus_fig_academic", ROOT)
    return rowsA, rowsB


# ------------------------------------------------------------------------------------------------------------------
# Fig. 3: what the department adds (the pay gradient per within-field SD)
# ------------------------------------------------------------------------------------------------------------------
def fig_gradient():
    # US, field fixed effects only (across universities): point and CR1 SE to 3 decimals
    fe = md_row("SELECTIVITY_RESULT.md",
                r"^\| no institution FE \(field FE only\) — comparator \| (\d+) \| (\d+) \| (\d+) \| "
                r"([+-]\d\.\d{3}) \((\d\.\d{3})\) \|", "field FE only")
    assert fe[:3] == ("4645", "251", "55"), fe
    fe_b, fe_se = float(fe[3]), float(fe[4])
    near(fe_b, 0.077, 3, "D3 field FE only"); near(fe_se, 0.005, 3, "D3 field FE only SE")
    # US, university and field fixed effects, and the main row's reliability-corrected slopes
    ab = md_row("SELECTIVITY_DEEP_RESULT.md",
                r"^\| \(a\) institution FE \+ field FE \+ β z\(F\) \[scripts/55 \(a\)\] \| 4,645 \| 251 \| 55 \| 55 \| "
                r"([+-]\d\.\d{4}) \(\d\.\d{4}\) \| \[([+-]\d\.\d{4}), ([+-]\d\.\d{4})\] \|", "univ + field FE")
    a_b, a_lo, a_hi = (float(v) for v in ab)
    for got, want, w in zip((a_b, a_lo, a_hi), (0.0104, 0.0036, 0.0169), ("est", "lo", "hi")):
        near(got, want, 4, f"D3 university + field FE {w}")
    mr = md_row("SELECTIVITY_DEEP_RESULT.md",
                r"^\| \(a\) \+ field × \{SAT, ADM, inst\. Pell, brand G\} \[main\] \| 3,961 \| 214 \| 53 \| 265 \| "
                r"([+-]\d\.\d{4}) \(\d\.\d{4}\) \| \[([+-]\d\.\d{4}), ([+-]\d\.\d{4})\] \| \d\.\d{2} \| "
                r"([+-]\d\.\d{4}), ([+-]\d\.\d{4}) \|$", "main row")
    c_lb, c_ext = float(mr[3]), float(mr[4])
    near(c_lb, 0.0085, 4, "D5 corrected (public-edge)"); near(c_ext, 0.0078, 4, "D5 corrected (extrapolated)")

    G = pd.read_csv(INTERIM / "gap_checks_summary.csv")
    gm = one(G, "main", section="G1 main", quantity="slope per SD: original F")
    gp = one(G, "production", section="G1 rev. 1", quantity="slope per SD: F | field x production rank (in design)")
    for r, s, w in ((gm, (0.0056, -0.0017, 0.0132), "D3 main"), (gp, (0.0048, -0.0027, 0.0132), "D4 production")):
        assert r.kind == "bootstrap" and str(r.k) == "3,961 programmes, 214 institutions, 53 fields", w
        for got, want, x in zip((r.est, r.lo, r.hi), s, ("est", "lo", "hi")):
            near(float(got), want, 4, f"{w} {x}")
    near(float(gm.est), float(mr[0]), 4, "main slope: csv vs result file")
    lam_lb = float(one(G, "lambda LB", section="G1 coverage",
                       quantity="scripts/58 residual-F reliability lambda_LB (main spec, z(F))").est)
    lam_ext = float(one(G, "lambda EXT", section="G1 coverage",
                        quantity="scripts/58 residual-F reliability lambda_EXT (main spec, z(F))").est)
    near(lam_lb, 0.654, 3, "M5 lambda LB"); near(lam_ext, 0.719, 3, "M5 lambda EXT")
    near(float(gm.est) / lam_lb, c_lb, 4, "corrected = main / lambda (LB)")         # consistency only
    near(float(gm.est) / lam_ext, c_ext, 4, "corrected = main / lambda (EXT)")

    U = pd.read_csv(INTERIM / "uk_triad_summary.csv")
    u21 = one(U, "REF 2021", section="T2a",
              quantity="within-provider slope of log pay per SD of REF GPA rank (cluster bootstrap)")
    uct = one(U, "REF 2021 + controls", section="T2a",
              quantity="  + subject x {zG, zS} slopes (US main-spec analogue) (cluster bootstrap)")
    u14 = one(U, "REF 2014", section="REF2014",
              quantity="within-provider slope of log pay per SD of REF 2014 GPA rank")
    assert (u21.ci, uct.ci, u14.ci) == ("bootstrap", "bootstrap", "CR1")
    assert u21.k == "900 programmes, 116 providers, 15 subjects" and uct.k == "893 programmes, 114 providers, 15 subjects"
    assert u14.k == "871 programmes, 112 providers, 15 subjects"
    for r, s, w in ((u21, (0.0178, 0.0063, 0.0305), "D6"), (uct, (0.0123, 0.0017, 0.0240), "D6b controls"),
                    (u14, (0.0315, 0.0185, 0.0446), "D6b REF 2014 (CR1)")):
        for got, want, x in zip((r.est, r.lo, r.hi), s, ("est", "lo", "hi")):
            near(float(got), want, 4, f"{w} {x}")

    fig = plt.figure(figsize=(fs.COL1, 96 * MM), layout="constrained")
    gs = fig.add_gridspec(2, 1, height_ratios=[2.5, 9.2])

    # A: across vs within universities, same US programmes
    ax = fig.add_subplot(gs[0, 0])
    fs.value_grid(ax, "x")
    fs.hinterval(ax, 1, fe_b, color=fs.ACROSS, marker="o")
    fs.hinterval(ax, 0, a_b, a_lo, a_hi, color=fs.WITHIN, marker="s", s=fs.S_PT - 2)
    ax.text(fe_b - 0.003, 1, f"{fs.fmt(fe_b)}", fontsize=fs.FS_SMALL, color=fs.ACROSS, va="center", ha="right")
    ax.text(a_hi + 0.003, 0, f"{fs.fmt(a_b, 4)}", fontsize=fs.FS_SMALL, color=fs.WITHIN, va="center", ha="left")
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["Across (field FE only)", "Within (university and field FE)"])
    ax.tick_params(axis="y", length=0, pad=2)
    ax.spines["left"].set_visible(False)
    ax.axvline(0, color=fs.BLACK, lw=0.6, zorder=1)
    ax.set_xlim(-0.004, 0.09)
    ax.set_ylim(-0.6, 1.6)
    ax.set_xticks(np.arange(0, 0.091, 0.02))
    fs.panel_title(ax, "A", "US: across and within")

    # B: within-university gradients
    ax = fig.add_subplot(gs[1, 0])
    fs.value_grid(ax, "x")
    us = [("University and field FE", a_b, a_lo, a_hi, "ci"),
          ("Main specification", *(float(v) for v in (gm.est, gm.lo, gm.hi)), "ci"),
          ("Main, plus doctoral production", *(float(v) for v in (gp.est, gp.lo, gp.hi)), "ci"),
          (f"Main, reliability-corrected ({lam_lb:.2f})", c_lb, None, None, "point"),
          (f"Main, reliability-corrected ({lam_ext:.2f})", c_ext, None, None, "point")]
    uk = [("University and subject FE, REF 2021", *(float(v) for v in (u21.est, u21.lo, u21.hi)), "ci"),
          ("REF 2021, plus G and selectivity", *(float(v) for v in (uct.est, uct.lo, uct.hi)), "ci"),
          ("University and subject FE, REF 2014", *(float(v) for v in (u14.est, u14.lo, u14.hi)), "cr1")]
    rows, ys, heads = [], [], []
    y = 0.0
    for head, block in (("UK: REF rating, 5-year pay", uk), ("US: hiring rank F, 4-year pay", us)):
        for r in block[::-1]:
            rows.append(r); ys.append(y); y += 1.0
        heads.append((head, y - 0.15)); y += 0.9
    for (lab, e, lo, hi, kind), yy in zip(rows, ys):
        if kind == "point":
            fs.hinterval(ax, yy, e, color=fs.WITHIN, marker="s", filled=False, s=fs.S_PT - 2)
            ax.text(e + 0.0024, yy, fs.fmt(e, 4), fontsize=fs.FS_SMALL, color=fs.WITHIN, va="center", ha="left")
        else:
            fs.hinterval(ax, yy, e, lo, hi, color=fs.WITHIN, marker="s", s=fs.S_PT - 2, dashed=(kind == "cr1"))
            ax.text(hi + 0.0015, yy, fs.fmt(e, 4), fontsize=fs.FS_SMALL, color=fs.WITHIN, va="center", ha="left")
    for head, yy in heads:
        ax.text(-0.0062, yy, head, fontsize=fs.FS_SMALL, fontweight="bold", ha="right", va="center",
                transform=ax.transData)
    ax.axhline(heads[0][1] + 0.5, color=fs.DGREY, lw=0.5)
    ax.axvline(0, color=fs.BLACK, lw=0.6, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.tick_params(axis="y", length=0, pad=2)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.005, 0.055)
    ax.set_ylim(-0.6, heads[-1][1] + 0.6)
    ax.set_xticks(np.arange(0, 0.051, 0.01))
    ax.set_xlabel("Change in log pay per within-field SD")
    ax.legend(handles=[Line2D([], [], marker="s", color=fs.WITHIN, mec="white", mew=0.4, ms=fs.MS, lw=fs.LW_CI,
                              label="bootstrap interval"),
                       Line2D([], [], marker="s", color=fs.WITHIN, mec="white", mew=0.4, ms=fs.MS, lw=fs.LW_CI,
                              ls=(0, (2.2, 1.2)), label="cluster-robust interval"),
                       Line2D([], [], marker="s", ls="", mfc="white", mec=fs.WITHIN, mew=0.9, ms=fs.MS,
                              label="point only")],
              loc="upper center", bbox_to_anchor=(0.25, -0.13), ncol=3, columnspacing=0.9, handlelength=1.6)
    fs.panel_title(ax, "B", "Within universities: all specifications")
    fs.save(fig, FIGDIR, "nexus_fig_gradient", ROOT)


if __name__ == "__main__":
    fig_academic()
    fig_gradient()
