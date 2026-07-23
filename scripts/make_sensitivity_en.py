"""make_sensitivity_en.py -- ENGLISH sensitivity figure for the TR-only study.

English clone of make_sensitivity_tr.py. Reads out/sensitivity_tr.json and
renders Fig4_sensitivity_en.png (300 dpi, Arial, keys in the graphic).

    python scripts/make_sensitivity_en.py
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")

for p in ["/System/Library/Fonts/Supplemental/Arial.ttf",
          "/Library/Fonts/Arial.ttf"]:
    if os.path.exists(p):
        fm.fontManager.addfont(p); plt.rcParams["font.family"] = fm.FontProperties(fname=p).get_name(); break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.default"] = "regular"   # subscripts use the sans font (Arial)
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["savefig.pad_inches"] = 0.03
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

GE = "\u2265"; CMH = r"cmH$_2$O"
C_TR = "#9467bd"; C_DEV = "#8a5a00"; C_REF = "#d62728"; C_NEG = "#9467bd"

PANELS = [
    ("DP",     f"Driving pressure DP ({CMH})"),
    ("max_sp", f"Heterogeneity max_sp ({CMH})"),
    ("h_mean", f"Half-inflation pressure h ({CMH})"),
    ("TCP_TR", f"TR closing pressure TCP ({CMH})\n(TOP co-varied, TOP-TCP held = 10)"),
    ("OD_THR", f"Overdist. threshold TMP{GE} ({CMH})"),
]


def draw(data):
    sw = data["sweeps"]
    fig = plt.figure(figsize=(13.6, 7.4))
    # column 3 is a narrow spacer so the tornado's left-side parameter labels
    # (longest: "TR band position") do not spill into the neighbouring panel
    # column 3 is a narrow spacer so the tornado's left-side parameter labels
    # (longest: "TR band position") do not spill into the neighbouring panel
    gs = gridspec.GridSpec(2, 5, figure=fig, width_ratios=[1, 1, 1, 0.28, 1.15],
                           hspace=0.42, wspace=0.34,
                           left=0.055, right=0.985, top=0.93, bottom=0.09)

    cells = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    for (param, xlab), (r, c) in zip(PANELS, cells):
        ax = fig.add_subplot(gs[r, c])
        rows = sw[param]
        x = np.array([q["value"] for q in rows])
        dev = np.array([q["dev"] for q in rows])
        sd = np.array([q["dev_sd"] for q in rows])
        ax.axhspan(0, 5.5, color=C_NEG, alpha=0.05)
        ax.axhline(0, color="k", lw=0.9, ls=":")
        ax.errorbar(x, dev, yerr=sd, fmt="o-", color=C_DEV, lw=2.0, ms=5, capsize=2.5)
        for q in rows:
            if q["is_ref"]:
                ax.plot(q["value"], q["dev"], "o", ms=11, mfc="none",
                        mec=C_REF, mew=2.0, zorder=5)
        ax.set_xlabel(xlab, fontsize=10)
        if c == 0:
            ax.set_ylabel(f"\u0394PEEP ({CMH})", fontsize=10.5)
        ax.set_ylim(-1.1, 5.5)
        ax.grid(alpha=0.22)
        ax.tick_params(labelsize=9)

    axT = fig.add_subplot(gs[:, 4])
    names_en = {"DP": "Driving pressure DP", "max_sp": "Heterogeneity",
                "h_mean": "Half-infl. pressure", "TCP_TR": "TR band position",
                "OD_THR": "Overdist. threshold"}
    order = ["DP", "OD_THR", "h_mean", "max_sp", "TCP_TR"]
    ref_dev = None
    for q in sw["DP"]:
        if q["is_ref"]:
            ref_dev = q["dev"]
    ys = np.arange(len(order))
    for i, param in enumerate(order):
        devs = [q["dev"] for q in sw[param]]
        lo, hi = min(devs), max(devs)
        axT.barh(i, hi - lo, left=lo, height=0.62, color=C_TR, alpha=0.45,
                 edgecolor=C_TR, lw=1.2)
        axT.plot([lo, hi], [i, i], color=C_TR, lw=0.8)
        axT.text(lo - 0.08, i + 0.34, f"{lo:+.1f}", va="bottom", ha="left", fontsize=8.5)
        axT.text(hi + 0.08, i, f"{hi:+.1f}", va="center", ha="left", fontsize=8.5)
    axT.axvline(0, color="k", lw=0.9, ls=":")
    if ref_dev is not None:
        axT.axvline(ref_dev, color=C_REF, lw=1.6, ls="--")
        axT.text(ref_dev - 0.12, 0.15, f"Reference {ref_dev:+.2f}",
                 color=C_REF, fontsize=8.5, ha="right", va="bottom", rotation=90)
    axT.set_yticks(ys); axT.set_yticklabels([names_en[p] for p in order], fontsize=9.5)
    axT.set_xlabel(f"Range of \u0394PEEP ({CMH})", fontsize=10.5)
    axT.set_xlim(-1.4, 5.5); axT.set_ylim(-0.6, len(order) - 0.4)
    axT.set_title("\u0394PEEP range spanned by each parameter", fontsize=11, pad=10)
    axT.grid(alpha=0.22, axis="x")

    fig.savefig(os.path.join(OUT, "Fig4_sensitivity_en.png"))
    plt.close(fig)
    print("Fig4_sensitivity_en.png")


if __name__ == "__main__":
    data = json.load(open(os.path.join(OUT, "sensitivity_tr.json")))
    draw(data)
