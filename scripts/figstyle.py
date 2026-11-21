"""One figure style for every figure of the paper (paper/nhb/main.tex and si.tex).

Imported by scripts/83_nexus_figures.py and scripts/86_nexus_figures_extra.py. Style only: no data, no numbers.

Decisions
---------
* Font. STIXGeneral, a Times-compatible serif that ships with matplotlib, so the figures match the Times text of
  main.tex and si.tex and render the same on any machine; mathtext uses the STIX set. It is TrueType, so PDFs embed
  it as Type 42 (pdf.fonttype 42). TeX Gyre Termes is installed locally but is CFF-flavoured OpenType, which
  matplotlib writes into the PDF as a malformed FontFile2, so it is not used.
* Sizes, at the final print size. Figures are drawn at the journal widths (87 mm single column, 178 mm double) and
  included at that width or slightly larger (the draft layout scales them by 1.02-1.03). No text is below 7 pt:
  tick labels, row labels, legends and annotations 7 pt; axis labels 7.5 pt; panel titles 8 pt bold.
* Exact sizes. Figures use constrained layout at a fixed figsize and are saved without bbox_inches="tight", so
  every figure keeps its stated width.
* Colour = concept, one colour per concept in every figure (Okabe-Ito, colour-blind safe):
      ACROSS    blue            #0072B2  agreement across universities within a field or subject, for the
                                         department-level academic measure (US hiring rank F, UK REF rating);
                                         also the university part of F (mean F of the university's other
                                         programmes) in the prediction decomposition
      WITHIN    vermilion       #D55E00  statistics within universities (departments of one university compared)
      GRANK     pink            #CC79A7  the university-wide hiring rank G (Okabe-Ito "reddish purple"; text
                                         in the darker #A0457F)
      RESEARCH  bluish green    #009E73  NRC research measures (positive control)
      NATIONAL  orange          #E69F00  UK subjects paid on national scales (text in the darker #8A5D00)
      TOTAL     dark grey       #4D4D4D  a combined quantity (F as a whole in the prediction decomposition)
      NULL      light grey band #C8C8C8  simulated values under equal agreement (a range, not an interval)
  Series that share a colour are told apart by marker shape or fill, so every figure survives grey-scale printing;
  each legend names its markers.
* Intervals. A point estimate is a marker; its 95% interval is a line in the series colour without caps
  (1.2 pt; dashed when the interval is cluster-robust rather than bootstrap). Values without an interval in the
  source are drawn as markers only (open markers where a filled one would suggest an interval). Means over fields or
  subjects are larger diamonds with a black edge.
* Panels. Bold capital letters A, B, C at the top left, followed by a short title.
* Grid. A faint solid grid on the value axis only; long lists (more than 20 rows) also get alternating row bands.
* Export. Vector PDF plus 300-dpi PNG, metadata dates suppressed, so a re-run is byte-identical.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

MM = 1 / 25.4
COL1 = 87 * MM          # single-column width
COL2 = 178 * MM         # double-column width

# font sizes (pt)
FS_SMALL = 7.0          # tick labels, row labels, legends, annotations: the minimum
FS_LABEL = 7.5          # axis labels
FS_TITLE = 8.0          # panel titles

# colour = concept (Okabe-Ito)
ACROSS = "#0072B2"
WITHIN = "#D55E00"
GRANK = "#CC79A7"
GRANK_TXT = "#A0457F"
RESEARCH = "#009E73"
NATIONAL = "#E69F00"
NATIONAL_TXT = "#8A5D00"
TOTAL = "#4D4D4D"
NULL_FILL, NULL_EDGE = "#C8C8C8", "#8C8C8C"
BLACK, DGREY, MGREY, LGREY = "#000000", "#4D4D4D", "#8C8C8C", "#C8C8C8"
BAND = "#F4F4F4"        # alternating row band
GRID = "#E1E1E1"

# marks
LW_CI = 1.2             # interval line width
LW_THIN = 0.8
MS = 4.2                # marker size (points) for Line2D markers
S_PT = 20               # scatter size (points^2) of a point estimate
S_MEAN = 32             # scatter size of a mean (diamond, black edge)

RC = {
    "font.family": "serif", "font.serif": ["STIXGeneral"], "mathtext.fontset": "stix",
    "font.size": FS_SMALL, "axes.labelsize": FS_LABEL, "axes.titlesize": FS_TITLE, "axes.titleweight": "bold",
    "xtick.labelsize": FS_SMALL, "ytick.labelsize": FS_SMALL, "legend.fontsize": FS_SMALL,
    "legend.title_fontsize": FS_SMALL, "legend.frameon": False, "legend.handletextpad": 0.4,
    "legend.borderaxespad": 0.2, "legend.handlelength": 1.6,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.major.pad": 2, "ytick.major.pad": 2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titlepad": 4, "axes.labelpad": 2.5,
    "axes.grid": False, "grid.color": GRID, "grid.linewidth": 0.5, "grid.linestyle": "-",
    "lines.linewidth": 1.1, "lines.markersize": MS, "errorbar.capsize": 0,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "savefig.dpi": 300, "figure.dpi": 100, "axes.unicode_minus": True,
}


def apply():
    """set the shared rcParams (call once, before any figure is created)"""
    plt.rcParams.update(RC)


def panel_title(ax, letter, text):
    """bold capital panel letter at the top left, then a short title"""
    ax.set_title(f"{letter}  {text}", loc="left", fontweight="bold", fontsize=FS_TITLE)


def value_grid(ax, axis="x"):
    """faint grid on the value axis only, drawn under the data"""
    ax.set_axisbelow(True)
    ax.grid(True, axis=axis)


def hinterval(ax, y, est, lo=None, hi=None, color=ACROSS, marker="o", filled=True, dashed=False, s=S_PT,
              alpha=1.0, z=3, edge=None):
    """horizontal 95% interval (line, no caps) with the point estimate on top; lo/hi None -> marker only"""
    if lo is not None and hi is not None:
        ax.plot([lo, hi], [y, y], color=color, lw=LW_CI, solid_capstyle="butt", dash_capstyle="butt",
                ls=(0, (2.2, 1.2)) if dashed else "-", zorder=z, alpha=alpha)
    if filled:
        ax.scatter(est, y, s=s, marker=marker, color=color, edgecolor=edge or "white", lw=0.4, zorder=z + 1,
                   alpha=alpha)
    else:
        ax.scatter(est, y, s=s, marker=marker, facecolor="white", edgecolor=color, lw=0.9, zorder=z + 1,
                   alpha=alpha)


def fmt(x, nd=3):
    """signed number with a true minus sign"""
    return f"{x:+.{nd}f}".replace("-", "−")


def save(fig, figdir: Path, name: str, root: Path | None = None):
    """vector PDF + 300-dpi PNG with metadata dates suppressed (byte-identical re-runs)"""
    figdir = Path(figdir)
    figdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figdir / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None, "Producer": None,
                                                  "Creator": None})
    fig.savefig(figdir / f"{name}.png", dpi=300, metadata={"Software": None})
    plt.close(fig)
    shown = figdir.relative_to(root) if root is not None else figdir
    print(f"wrote {shown}/{name}.pdf and .png")
