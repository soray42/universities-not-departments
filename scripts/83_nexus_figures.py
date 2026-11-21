"""Main-text figures 1, 4 and 5 of the paper (paper/nhb/main.tex).

Draws only. Nothing is re-estimated and no random number is drawn. Every plotted number is read from a table that
an analysis script wrote (data/interim/*.csv), selected by an exact key with an assertion that exactly one row
matches, and the values that the text quotes are asserted against the values printed in the paper, to the
printed precision.

Figures (vector PDF + 300-dpi PNG). The style (font, sizes, colour per concept, interval and marker conventions,
panel letters) comes from scripts/figstyle.py, shared with scripts/86_nexus_figures_extra.py. In the paper,
nexus_fig1 is Fig. 1, nexus_fig2 is Fig. 4 and nexus_fig3 is Fig. 5 (Figs. 2 and 3 come from scripts/86):
  nexus_fig1  between- vs within-university agreement: US hiring rank F vs pay and the three UK pairs (REF, pay,
              intake); observed correlations with 95% cluster-bootstrap CIs, and the central 95% of the simulated
              within-university correlation under rho_within = rho_between (600 null draws on the real layout).
              Source: data/interim/gap_checks_summary.csv (scripts/78). Column meanings (scripts/78, R.put):
              est = point estimate (for 'null ...' rows: the mean over the null draws); lo, hi = 95% interval
              (for kind == 'null 2.5-97.5%': the 2.5th and 97.5th percentiles of the null draws, not a CI);
              verdict carries the calibrated p for null-within rows. The CSV holds no individual null draws and no
              null minimum or maximum, so the figure shows the central 95% band and the null mean only.
  nexus_fig2  field map: (A) US within-field Spearman coupling of F with 4-year pay, 52 fields (55 under the 2026
              release; the panel labels print the count), +-1.96 institution
              bootstrap SE (data/interim/selectivity_fields.csv, scripts/55); (B) UK within-subject coupling of the
              university-wide hiring rank G with 5-year pay, 33 subjects, with the subjects paid on national scales
              marked and the two group means with their two-stage bootstrap CIs
              (data/interim/uk_leo_subject_coupling.csv and uk_leo_summary.csv, scripts/62).
  nexus_fig3  years since graduation: (A) US mean coupling of F and of G at 1, 5 and 10 years (PSEO V4.14.1 fixed
              cohorts, 40 fields; levels drawn without intervals), (B) US standardised rank-regression loadings
              b_F and b_G with two-way (field, institution) cluster CIs (data/interim/pseo_refresh.csv, scripts/59,
              variant 'new' = V4.14.1), (C) UK coupling of G at YAG 1, 3, 5 with two-stage bootstrap CIs
              (uk_leo_summary.csv, scripts/62).

Outputs: outputs/figures/wapman2026/nexus_fig{1,2,3}.pdf and .png (outputs/figures/ under the v1 data). PDF/PNG
metadata dates are suppressed, so re-runs are byte-identical.
Run: python scripts/83_nexus_figures.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
FIGDIR = ROOT / "outputs" / "figures"
# Under the 2026 Wapman release (src/wapman_release.py) the figures go to outputs/figures/wapman2026/, the files the
# paper includes; checks pinned to values of the v1 data report a mismatch instead of stopping (v1_assert).
import sys                                                                    # noqa: E402
sys.path.insert(0, str(ROOT))
from src.wapman_release import is_v1 as _wapman_is_v1, v1_assert            # noqa: E402
if not _wapman_is_v1():
    FIGDIR = FIGDIR / "wapman2026"

# ------------------------------------------------------------------------------------------------------------------
# house style: the shared module scripts/figstyle.py (styling only; see its docstring for the conventions)
# ------------------------------------------------------------------------------------------------------------------
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs                                                         # noqa: E402

fs.apply()
MM, COL1, COL2 = fs.MM, fs.COL1, fs.COL2
BLACK, DGREY, MGREY, LGREY = fs.BLACK, fs.DGREY, fs.MGREY, fs.LGREY
panel_title, fmt = fs.panel_title, fs.fmt


def save(fig, name):
    fs.save(fig, FIGDIR, name, ROOT)


def near(a, b, nd, what):
    """assert that a value read from a table prints as the paper's value b at nd decimals"""
    v1_assert(round(a, nd) == round(b, nd) or abs(a - b) <= 0.5 * 10 ** -nd + 1e-12, f"{what}: {a!r} vs v1 value {b!r}")


# ------------------------------------------------------------------------------------------------------------------
# Figure 1: between- vs within-university agreement (scripts/78)
# ------------------------------------------------------------------------------------------------------------------
def gap_row(G, section, quantity):
    x = G[(G.section == section) & (G.quantity == quantity)]
    assert len(x) == 1, f"gap_checks_summary: {section!r} / {quantity!r} matched {len(x)} rows"
    return x.iloc[0]


def fig1():
    G = pd.read_csv(INTERIM / "gap_checks_summary.csv")
    PR = "[share >= 360 points, 'low' = 1 (primary)]"
    pairs = [
        # label, across row, within row, null-within row
        ("US: hiring rank F\nvs pay", ("G3 US rev. 2", "FE-only contrast: across institutions within field (plain coupling)"),
         ("G3 US rev. 2", "FE-only contrast: within institution"),
         ("G3 US sim [LB]", "null within-institution correlation")),
        ("UK: REF rating\nvs pay", ("G3 UK", "REF-pay: across providers within subject"),
         ("G3 UK", "REF-pay: within provider"),
         ("G3 UK sim", "REF-pay (normal scores): null within correlation")),
        ("UK: REF rating\nvs intake", ("G3 UK", f"REF-intake {PR}: across providers within subject"),
         ("G3 UK", f"REF-intake {PR}: within provider"),
         ("G3 UK sim", "REF-intake (normal scores): null within correlation")),
        ("UK: pay\nvs intake", ("G3 UK", f"pay-intake {PR}: across providers within subject"),
         ("G3 UK", f"pay-intake {PR}: within provider"),
         ("G3 UK sim", "pay-intake (normal scores): null within correlation")),
    ]
    # v1-data values of H1, H2, H6-H9 (observed values and 95% cluster-bootstrap CIs), H3/H10 (calibrated p)
    sheet = [((0.470, 0.412, 0.528), (0.071, 0.038, 0.106)),
             ((0.625, 0.556, 0.681), (0.103, 0.028, 0.173)),
             ((0.677, 0.615, 0.725), (0.150, 0.072, 0.223)),
             ((0.699, 0.616, 0.763), (0.166, 0.065, 0.270))]
    rows = []
    for (lab, a, w, n), (sa, sw) in zip(pairs, sheet):
        ra, rw, rn = gap_row(G, *a), gap_row(G, *w), gap_row(G, *n)
        assert ra.kind == "bootstrap" and rw.kind == "bootstrap" and rn.kind == "null 2.5-97.5%"
        for r, s, what in ((ra, sa, "across"), (rw, sw, "within")):
            for col, v in zip(("est", "lo", "hi"), s):
                near(float(r[col]), v, 3, f"{lab} {what} {col}")
        v1_assert(str(rn.verdict).strip() == "p = 0.0017", f"{lab}: calibrated p {rn.verdict!r} vs v1 value 'p = 0.0017'")
        assert str(rn.k).strip() == "600 null draws", (lab, rn.k)
        v1_assert(float(rw.est) < float(rn.lo), f"{lab}: observed within lies inside the null band")
        rows.append(dict(lab=lab, a=(ra.est, ra.lo, ra.hi), w=(rw.est, rw.lo, rw.hi), n=(rn.est, rn.lo, rn.hi)))
    near(float(rows[0]["n"][1]), 0.209, 3, "US null lo")           # H3: null range [0.209, 0.278]
    near(float(rows[0]["n"][2]), 0.278, 3, "US null hi")

    fig, ax = plt.subplots(figsize=(COL1, 88 * MM), layout="constrained")
    k = len(rows)
    # academic-employer pairs on top; the two intake pairs (supporting evidence) below a gap, drawn lighter
    ys = np.array([3.9, 2.9, 1.0, 0.0])
    alphas = [1.0, 1.0, 0.45, 0.45]
    dA, dW = 0.17, -0.13
    fs.value_grid(ax, "x")
    for j, (y, r, al) in enumerate(zip(ys, rows, alphas)):
        # simulated null: central 95% of the 600 within values, drawn as a band at the within row, mean as a tick
        n_m, n_lo, n_hi = (float(v) for v in r["n"])
        ax.add_patch(plt.Rectangle((n_lo, y + dW - 0.085), n_hi - n_lo, 0.17, facecolor=fs.NULL_FILL,
                                   edgecolor=fs.NULL_EDGE, lw=0.5, zorder=1, alpha=max(al, 0.6)))
        ax.plot([n_m, n_m], [y + dW - 0.085, y + dW + 0.085], color=DGREY, lw=0.8, zorder=2, alpha=max(al, 0.6))
        a_e, a_lo, a_hi = (float(v) for v in r["a"])
        w_e, w_lo, w_hi = (float(v) for v in r["w"])
        fs.hinterval(ax, y + dA, a_e, a_lo, a_hi, color=fs.ACROSS, marker="o", alpha=al)
        fs.hinterval(ax, y + dW, w_e, w_lo, w_hi, color=fs.WITHIN, marker="s", s=fs.S_PT - 2, alpha=al)
        ax.text(a_hi + 0.012, y + dA, fmt(a_e), fontsize=fs.FS_SMALL, va="center", ha="left", color=fs.ACROSS,
                alpha=al)
        ax.text(w_e, y + dW - 0.23, fmt(w_e), fontsize=fs.FS_SMALL, va="center", ha="center", color=fs.WITHIN,
                alpha=al)
    ax.axhline((ys[0] + ys[1]) / 2, color=DGREY, lw=0.5)       # US above, UK below
    ax.axhline((ys[1] + ys[2]) / 2 + 0.05, color=DGREY, lw=0.5, ls=(0, (3, 2)))
    ax.text(0.0, (ys[1] + ys[2]) / 2 - 0.12, "  supporting: UK intake", fontsize=fs.FS_SMALL, color=DGREY,
            va="top", ha="left", style="italic")
    ax.set_yticks(ys)
    ax.set_yticklabels([r["lab"] for r in rows], fontsize=fs.FS_SMALL)
    for tl, al in zip(ax.get_yticklabels(), alphas):
        if al < 1:
            tl.set_color(DGREY)
    ax.tick_params(axis="y", length=0, pad=2)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0.0, 0.92)
    ax.set_ylim(-0.66, ys[0] + 0.55)
    ax.set_xticks(np.arange(0, 0.81, 0.2))
    ax.set_xlabel("Correlation of normal scores")
    handles = [Line2D([], [], marker="o", color=fs.ACROSS, mec="white", mew=0.4, ms=fs.MS + 0.3, lw=fs.LW_CI,
                      label="across universities, within field or subject"),
               Line2D([], [], marker="s", color=fs.WITHIN, mec="white", mew=0.4, ms=fs.MS, lw=fs.LW_CI,
                      label="within universities"),
               Patch(facecolor=fs.NULL_FILL, edgecolor=fs.NULL_EDGE, lw=0.5,
                     label="within, simulated with equal agreement at both\nlevels (central 95% of draws; tick: mean)")]
    fig.legend(handles=handles, loc="outside lower center", ncol=1, handlelength=1.8)
    save(fig, "nexus_fig1")
    return rows


# ------------------------------------------------------------------------------------------------------------------
# Figure 2: field map, US and UK
# ------------------------------------------------------------------------------------------------------------------
def uk_summary():
    u = pd.read_csv(INTERIM / "uk_leo_summary.csv")

    def get(q):
        x = u[u.quantity == q]
        assert len(x) == 1, f"uk_leo_summary: {q!r} matched {len(x)} rows"
        r = x.iloc[0]
        return float(r.est), float(r.lo), float(r.hi), (int(r.k) if np.isfinite(r.k) else None)
    return get


def fig2():
    s = pd.read_csv(INTERIM / "selectivity_fields.csv")
    s = s[s.n >= 15].sort_values("rho_raw").reset_index(drop=True)       # canonical US sample: >= 15 institutions
    assert s.rho_raw.notna().all() and s.se_rho_raw.notna().all()
    v1_assert(len(s) == 52, f"US fields with n >= 15: {len(s)} vs v1 value 52")
    near(float(s.rho_raw.mean()), 0.419, 3, "US mean coupling (D1)")
    cs = s[s.field == "computer_science"].iloc[0]; nu = s[s.field == "nursing"].iloc[0]
    near(float(cs.rho_raw), 0.71, 2, "CS coupling (D1)"); near(float(nu.rho_raw), 0.07, 2, "nursing coupling (D1)")
    D1 = (0.419, 0.355, 0.482)          # joint institution-bootstrap CI of the mean (SELECTIVITY_DEEP_RESULT; D1)
    if not _wapman_is_v1():             # 2026 release: the same row of the regenerated SELECTIVITY_DEEP_RESULT.md
        import re
        hit = re.findall(r"^\| mean ρ\(F, Y\), full sample \(= gap-map baseline\) \| full sample \| (\d+) \| "
                         r"([+-]\d\.\d{3}) \[([+-]\d\.\d{3}), ([+-]\d\.\d{3})\] \|",
                         (ROOT / "SELECTIVITY_DEEP_RESULT.md").read_text(encoding="utf-8"), flags=re.M)
        assert len(hit) == 1 and int(hit[0][0]) == len(s), hit
        D1 = tuple(float(v) for v in hit[0][1:])

    sc = pd.read_csv(INTERIM / "uk_leo_subject_coupling.csv").dropna(subset=["raw"])
    sc = sc.sort_values("raw").reset_index(drop=True)
    assert len(sc) == 33
    U = uk_summary()
    core_m = U("raw coupling YAG5: setting-priced (core) mean")
    oth_m = U("raw coupling YAG5: others mean (vs core)")
    for got, want, what in [(core_m[0], 0.120, "P1 core"), (core_m[1], -0.033, "P1 core lo"), (core_m[2], 0.258, "P1 core hi"),
                            (oth_m[0], 0.523, "P1 others"), (oth_m[1], 0.439, "P1 others lo"), (oth_m[2], 0.585, "P1 others hi")]:
        near(got, want, 3, what)
    core = sc[sc.setting == "core"]
    assert set(core.subject) == {"Nursing and midwifery", "Medicine and dentistry", "Education and teaching"}
    assert abs(core.raw.mean() - core_m[0]) < 5e-4 and abs(sc[sc.setting != "core"].raw.mean() - oth_m[0]) < 5e-4

    fig = plt.figure(figsize=(COL2, 172 * MM), layout="constrained")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0])
    ax = fig.add_subplot(gs[0, 0])
    k = len(s)
    fs.value_grid(ax, "x")
    for i, r in s.iterrows():
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color=fs.BAND, lw=0, zorder=0)
        lo, hi = np.clip(r.rho_raw - 1.96 * r.se_rho_raw, -1, 1), np.clip(r.rho_raw + 1.96 * r.se_rho_raw, -1, 1)
        ax.plot([lo, hi], [i, i], color=fs.ACROSS, alpha=0.4, lw=fs.LW_THIN, solid_capstyle="butt", zorder=2)
        ax.scatter(r.rho_raw, i, s=4 + 0.25 * r.n, color=fs.ACROSS, edgecolor="white", lw=0.3, zorder=3)
    ysum = k + 1.0                                       # summary row above the fields
    ax.axvspan(D1[1], D1[2], color=fs.ACROSS, alpha=0.08, lw=0, zorder=0.5)
    ax.axvline(D1[0], color=fs.ACROSS, lw=0.7, ls=(0, (4, 2)), zorder=1)
    fs.hinterval(ax, ysum, D1[0], D1[1], D1[2], color=fs.ACROSS, marker="D", s=fs.S_MEAN, edge=BLACK)
    ax.text(D1[2] + 0.03, ysum, f"{fmt(D1[0])}", fontsize=fs.FS_SMALL,
            va="center", ha="left", color=fs.ACROSS)
    ax.axhline(k - 0.1, color=DGREY, lw=0.5)
    ax.axvline(0, color=BLACK, lw=0.6, zorder=1)
    ax.set_yticks(list(range(k)) + [ysum])
    ax.set_yticklabels(list(s.label) + [f"Mean, {k} fields"], fontsize=fs.FS_SMALL)   # k = len(s): 52 / 55
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.tick_params(axis="y", length=0, pad=1.5)
    ax.spines["left"].set_visible(False)
    ax.set_ylim(-0.7, ysum + 0.8)
    ax.set_xlim(-1.0, 1.0)
    ax.set_xticks(np.arange(-1.0, 1.01, 0.5))
    ax.set_xlabel("Spearman correlation across universities,\nhiring rank F vs 4-year median pay")
    sizes = [Line2D([], [], marker="o", ls="", color=fs.ACROSS, mec="white", mew=0.3, ms=np.sqrt(4 + 0.25 * nn),
                    label=f"{nn}") for nn in (20, 60, 150)]
    ax.legend(handles=sizes, loc="upper left", bbox_to_anchor=(0.0, 0.83), title="universities\nper field",
              ncol=1, handletextpad=0.3, labelspacing=0.3, alignment="left")
    panel_title(ax, "A", f"US, {k} fields: department rank F")

    ax = fig.add_subplot(gs[0, 1])
    k2 = len(sc)
    fs.value_grid(ax, "x")
    for i, r in sc.iterrows():
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color=fs.BAND, lw=0, zorder=0)
        if r.setting == "core":
            ax.scatter(r.raw, i, s=fs.S_PT, marker="^", color=fs.NATIONAL, edgecolor=BLACK, lw=0.5, zorder=3)
        elif r.setting == "broad":
            ax.scatter(r.raw, i, s=fs.S_PT, marker="^", facecolor="white", edgecolor=fs.NATIONAL_TXT, lw=0.9,
                       zorder=3)
        else:
            ax.scatter(r.raw, i, s=fs.S_PT - 4, marker="o", color=fs.GRANK, edgecolor="white", lw=0.3, zorder=3)
    ys_ = {"core": k2 + 2.0, "other": k2 + 1.0}             # two summary rows above the subjects
    for (est, lo, hi, kk), col, fc, key in [(core_m, fs.NATIONAL_TXT, fs.NATIONAL, "core"),
                                            (oth_m, fs.GRANK, fs.GRANK, "other")]:
        yy = ys_[key]
        ax.vlines(est, -0.7, k2 - 0.1, color=col, lw=0.6, ls=(0, (4, 2)), zorder=1)
        ax.plot([lo, hi], [yy, yy], color=col, lw=fs.LW_CI, solid_capstyle="butt", zorder=3)
        ax.scatter(est, yy, s=fs.S_MEAN, marker="D", color=fc, edgecolor=BLACK, lw=0.5, zorder=4)
        ax.text(hi + 0.025, yy, f"{fmt(est)}", fontsize=fs.FS_SMALL, va="center",
                ha="left", color=col)
    ax.axhline(k2 - 0.1, color=DGREY, lw=0.5)
    ax.axvline(0, color=BLACK, lw=0.6, zorder=1)
    ax.set_yticks(list(range(k2)) + [ys_["other"], ys_["core"]])
    short = {"Geography, earth and environmental studies": "Geography, earth and environment",
             "Sociology, social policy and anthropology": "Sociology, social policy, anthropology",
             "Pharmacology, toxicology and pharmacy": "Pharmacology, toxicology, pharmacy",
             "Media, journalism and communications": "Media, journalism, communications",
             "Agriculture, food and related studies": "Agriculture, food and related",
             "General, applied and forensic sciences": "General, applied, forensic sciences",
             "Architecture, building and planning": "Architecture, building, planning"}
    ax.set_yticklabels([short.get(x, x) for x in sc.subject] + ["Mean, other subjects (30)",
                                                                  "Mean, national pay scales (3)"],
                       fontsize=fs.FS_SMALL)
    tls = ax.get_yticklabels()
    for tl, st in zip(tls[:k2], sc.setting):
        if st in ("core", "broad"):
            tl.set_color(fs.NATIONAL_TXT)
    tls[-1].set_fontweight("bold"); tls[-1].set_color(fs.NATIONAL_TXT); tls[-2].set_fontweight("bold")
    ax.tick_params(axis="y", length=0, pad=1.5)
    ax.spines["left"].set_visible(False)
    ax.set_ylim(-0.7, k2 + 2.8)
    ax.set_xlim(-0.3, 1.0)
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("Spearman correlation across universities,\nuniversity-wide hiring rank G vs 5-year median pay")
    ax.legend(handles=[Line2D([], [], marker="^", ls="", color=fs.NATIONAL, mec=BLACK, mew=0.5, ms=fs.MS + 0.4,
                              label="paid largely on national scales"),
                       Line2D([], [], marker="^", ls="", mfc="white", mec=fs.NATIONAL_TXT, mew=0.9,
                              ms=fs.MS + 0.4, label="allied health (partly national bands)"),
                       Line2D([], [], marker="o", ls="", color=fs.GRANK, mec="white", mew=0.3, ms=fs.MS - 0.4,
                              label="other subject")],
              loc="upper center", bbox_to_anchor=(0.3, -0.088), ncol=1)
    panel_title(ax, "B", "UK, 33 subjects: university rank G")
    save(fig, "nexus_fig2")
    return s, sc


# ------------------------------------------------------------------------------------------------------------------
# Figure 3: years since graduation
# ------------------------------------------------------------------------------------------------------------------
def fig3():
    P = pd.read_csv(INTERIM / "pseo_refresh.csv")
    P = P[P.variant == "new"]                                   # V4.14.1, the PSEO release used in the paper
    TW = " [two-way field x institution cluster variance]"

    def prow(section, stat, horizon=None, quantile=None):
        x = P[(P.section == section) & (P.stat == stat)]
        if horizon is not None:
            x = x[x.horizon == horizon]
        if quantile is not None:
            x = x[x["quantile"] == quantile]
        assert len(x) == 1, f"pseo_refresh: {stat} {horizon} {quantile} matched {len(x)}"
        r = x.iloc[0]
        return float(r.estimate), float(r.ci_lo), float(r.ci_hi), int(float(r.k))

    sl = prow("career_time", "slope_all" + TW)
    dF, dG, dGF = (prow("career_time", s_ + TW) for s_ in ("dbF_all", "dbG_all", "dG_minus_dF_all"))
    for got, want, what in [(sl[0], 0.030, "C1"), (sl[1], 0.020, "C1 lo"), (sl[2], 0.041, "C1 hi"),
                            (dGF[0], 0.035, "C4"), (dGF[1], 0.007, "C4 lo"), (dGF[2], 0.063, "C4 hi")]:
        near(got, want, 3, what)
    v1_assert(sl[3] == 40 and dGF[3] == 40, f"PSEO career-time fields: {sl[3]}, {dGF[3]} vs v1 value 40")
    U = uk_summary()
    uk_sl = U("career slope of rho(G, earnings) per year")
    for got, want, what in [(uk_sl[0], 0.026, "C3"), (uk_sl[1], 0.014, "C3 lo"), (uk_sl[2], 0.037, "C3 hi")]:
        near(got, want, 3, what)
    uk_pts = [U(f"coupling at YAG{y}") for y in (1, 3, 5)]
    near(uk_pts[0][0], 0.379, 3, "C3 YAG1"); near(uk_pts[2][0], 0.484, 3, "C3 YAG5")

    yrs = {"y1": 1, "y5": 5, "y10": 10}
    fig = plt.figure(figsize=(COL2, 64 * MM), layout="constrained")
    gs = fig.add_gridspec(1, 3)
    axa, axb, axc = (fig.add_subplot(gs[0, j]) for j in range(3))
    for ax_ in (axa, axb, axc):
        fs.value_grid(ax_, "y")

    # (A) US coupling levels (no intervals drawn: the release table gives these levels only two-stage and crossed
    # bootstrap intervals, which are not the interval types used in the main text)
    for stat, col, mk, lab in [("coupling_F", fs.ACROSS, "o", "department rank F"),
                               ("coupling_G", fs.GRANK, "s", "university-wide rank G")]:
        pts = [prow("quantile", stat, h, "p50") for h in yrs]
        v1_assert({p[3] for p in pts} == {40}, f"PSEO quantile fields: {sorted({p[3] for p in pts})} vs v1 value 40")
        axa.plot(list(yrs.values()), [p[0] for p in pts], marker=mk, color=col, ms=fs.MS, lw=1.1,
                 ls="-" if mk == "o" else (0, (3, 1.5)), mfc=col if mk == "o" else "white", mec=col, label=lab)
    axa.text(0.04, 0.97, f"slope of the F coupling\n{fmt(sl[0])} per year",
             transform=axa.transAxes, va="top", fontsize=fs.FS_SMALL, color=DGREY, linespacing=1.3)
    axa.set_xticks([1, 5, 10]); axa.set_xlim(0, 11); axa.set_ylim(0, 0.62)
    axa.set_xlabel("Years since graduation")
    axa.set_ylabel("Mean Spearman correlation with median pay")
    axa.legend(loc="lower right")
    panel_title(axa, "A", "US coupling, fixed cohorts")

    # (B) US loadings, two-way CIs
    for coef, col, mk, off, lab in [("bF", fs.ACROSS, "o", -0.18, "b$_F$ (department rank)"),
                                    ("bG", fs.GRANK, "s", 0.18, "b$_G$ (university-wide rank)")]:
        pts = [prow("career_time", f"{coef}_{h}_all" + TW) for h in yrs]
        e = np.array([p[0] for p in pts]); lo = np.array([p[1] for p in pts]); hi = np.array([p[2] for p in pts])
        axb.errorbar(np.array(list(yrs.values())) + off, e, yerr=[e - lo, hi - e], fmt=mk, color=col,
                     ls="-" if mk == "o" else (0, (3, 1.5)), elinewidth=fs.LW_CI,
                     mfc=col if mk == "o" else "white", mec=col, ms=fs.MS, lw=1.1, label=lab)
    axb.text(0.04, 0.97, f"change per year\nb$_G$ {fmt(dG[0])}\n"
             f"b$_F$ {fmt(dF[0])}",
             transform=axb.transAxes, va="top", fontsize=fs.FS_SMALL, color=DGREY, linespacing=1.3)
    axb.axhline(0, color=BLACK, lw=0.6)
    axb.set_xticks([1, 5, 10]); axb.set_xlim(0, 11); axb.set_ylim(-0.2, 0.62)
    axb.set_xlabel("Years since graduation")
    axb.set_ylabel("Standardised rank-regression loading")
    axb.legend(loc="lower right")
    panel_title(axb, "B", "US loadings on F and G")

    # (C) UK coupling of G, two-stage bootstrap CIs (subjects, then providers)
    e = np.array([p[0] for p in uk_pts]); lo = np.array([p[1] for p in uk_pts]); hi = np.array([p[2] for p in uk_pts])
    assert {p[3] for p in uk_pts} == {33}
    axc.errorbar([1, 3, 5], e, yerr=[e - lo, hi - e], fmt="s", ls=(0, (3, 1.5)), color=fs.GRANK, mfc="white",
                 mec=fs.GRANK, ms=fs.MS, lw=1.1, elinewidth=fs.LW_CI, label="university-wide rank G (33 subjects)")
    axc.text(0.04, 0.97, f"slope {fmt(uk_sl[0])} per year",
             transform=axc.transAxes, va="top", fontsize=fs.FS_SMALL, color=DGREY)
    axc.set_xticks([1, 3, 5]); axc.set_xlim(0.3, 5.7); axc.set_ylim(0, 0.62)
    axc.set_xlabel("Years after graduation")
    axc.set_ylabel("Mean Spearman correlation with median pay")
    axc.legend(loc="lower right")
    panel_title(axc, "C", "UK coupling, fixed cohorts")
    save(fig, "nexus_fig3")
    return sl, dF, dG, dGF, uk_sl


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
