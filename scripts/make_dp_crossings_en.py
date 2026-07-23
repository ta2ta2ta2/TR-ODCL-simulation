"""make_dp_crossings_en.py -- per-DP ODCL crossing panels for the DP-sensitivity
analysis (companion to FigureS1_DP). Shows, at each driving pressure, the true
collapse/overdistension limbs (which define the true optimum) alongside Costa's
compliance-based collapse/overdistension limbs, so the reader can see WHY the
Costa-true gap behaves as it does. True collapse is defined at end-expiration
(permanent collapse + tidal recruitment, collapse_mode="exp"): counting TR units
as injury shifts the true optimum to higher PEEP and Costa deviates downward at
every DP. Airway-free Hickling TR lung (TOP=12, TCP=2, gap=10), n=30 seeds.

  cd scripts && PYTHONPATH=. python make_dp_crossings_en.py
Writes ../out/FigS1b_dp_crossings_en.png (+ .tif).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.lines as mlines
import metrics as M

for p in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"]:
    if os.path.exists(p):
        fm.fontManager.addfont(p); plt.rcParams["font.family"] = fm.FontProperties(fname=p).get_name(); break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.default"] = "regular"

OUT = os.path.join(os.path.dirname(__file__), "..", "out")
PEEP_GRID = np.arange(24, 1, -1)
TOP_TR, TCP_TR, TR_SD = 12.0, 2.0, 1.0
H_REF, MAXSP = 4.9, 14.5
N_SEEDS = 30
DP_LIST = [5, 7, 9, 11, 13, 14, 15]

C_COLL_T = "#c0392b"   # true collapse
C_OD_T   = "#1f5fbf"   # true overdistension
C_COLL_C = "#e8a29a"   # Costa collapse (faded)
C_OD_C   = "#9fbce8"   # Costa overdistension (faded)
C_TRUE   = "#7a3ea8"   # true optimum vline
C_COSTA  = "#666666"   # Costa vline

def mk(seed):
    return M.make_lung(seed=seed, aop_mean=M.DISABLED_OPEN, aop_sd=0.0,
                       acp_mean=M.DISABLED_CLOSE, acp_sd=0.0,
                       top_mean=TOP_TR, top_sd=TR_SD, tcp_mean=TCP_TR, tcp_sd=TR_SD,
                       h_mean=H_REF, max_sp=MAXSP)

def collect(dp):
    agg = {}
    ocs, ots = [], []
    for s in range(N_SEEDS):
        rows, oc, ot = M.decremental_trial(mk(s), dp=dp, peep_grid=PEEP_GRID, collapse_mode="exp")
        ocs.append(oc); ots.append(ot)
        for r in rows:
            agg.setdefault(r["peep"], []).append(
                [r["true_collapse"], r["overdist"], r["coll_costa"], r["hyper_costa"], r["tidal_recruit"]])
    peeps = np.array(sorted(agg, reverse=True), dtype=float)
    A = np.array([np.nanmean(np.array(agg[p], dtype=float), 0) for p in peeps])
    return dict(peep=peeps, tcoll=A[:,0], tod=A[:,1], ccoll=A[:,2], chyp=A[:,3],
                trmax=float(np.nanmax(A[:,4])), costa=float(np.mean(ocs)), true=float(np.mean(ots)))

data = {dp: collect(dp) for dp in DP_LIST}

fig, axes = plt.subplots(2, 4, figsize=(14.5, 7.4))
plt.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.10, hspace=0.42, wspace=0.30)
axf = axes.ravel()

for k, dp in enumerate(DP_LIST):
    ax = axf[k]; d = data[dp]; pe = d["peep"]
    # Costa limbs (faded, behind)
    ax.plot(pe, d["ccoll"], "-", color=C_COLL_C, lw=2.6, zorder=1)
    ax.plot(pe, d["chyp"],  "-", color=C_OD_C,   lw=2.6, zorder=1)
    # true limbs (solid, front)
    ax.plot(pe, d["tcoll"], "-s", color=C_COLL_T, lw=1.7, ms=3.2, zorder=3)
    ax.plot(pe, d["tod"],   "-o", color=C_OD_T,   lw=1.7, ms=3.2, zorder=3)
    ax.axvline(d["true"],  color=C_TRUE,  lw=1.8, ls="--", zorder=4)
    ax.axvline(d["costa"], color=C_COSTA, lw=1.6, zorder=4)
    ax.set_xlim(24.5, 1.5); ax.set_ylim(0, 100)
    dev = d["true"] - d["costa"]
    ax.set_title("DP = %d cmH$_2$O   (\u0394PEEP = %+.1f)" % (dp, dev),
                 fontsize=10, fontweight="bold" if dp == 14 else "normal")
    ax.text(0.035, 0.965, "true %.1f\nCosta %.1f\nTR$_{max}$ %.0f%%" % (d["true"], d["costa"], d["trmax"]),
            transform=ax.transAxes, fontsize=7.6, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.9))
    if k % 4 == 0:
        ax.set_ylabel("Collapse / Overdistension (%)", fontsize=9)
    if k >= 3:
        ax.set_xlabel("PEEP (cmH$_2$O)", fontsize=9)
    ax.tick_params(labelsize=8)

# summary panel (8th): dev and TRmax vs DP
axs = axf[7]
dps = np.array(DP_LIST, dtype=float)
devs = np.array([data[dp]["true"] - data[dp]["costa"] for dp in DP_LIST])
trs = np.array([data[dp]["trmax"] for dp in DP_LIST])
axs.plot(dps, devs, "o-", color=C_TRUE, lw=2.0, ms=6, zorder=3)
axs.axhline(0, color="#999", lw=1.0)
axs.set_xlabel("Driving pressure DP (cmH$_2$O)", fontsize=9)
axs.set_ylabel("\u0394PEEP = true \u2212 Costa (cmH$_2$O)", color=C_TRUE, fontsize=9)
axs.tick_params(axis="y", colors=C_TRUE, labelsize=8); axs.tick_params(axis="x", labelsize=8)
axs.set_title("Summary: \u0394PEEP and tidal recruitment vs DP", fontsize=10)
axr = axs.twinx()
axr.plot(dps, trs, "s--", color="#1f5fbf", lw=1.4, ms=4, alpha=0.9, zorder=2)
axr.set_ylabel("peak tidal-recruiting units (%)", color="#1f5fbf", fontsize=9)
axr.tick_params(axis="y", colors="#1f5fbf", labelsize=8)
axr.set_ylim(-2, 40)

# shared legend
leg = [mlines.Line2D([0],[0], color=C_COLL_T, marker="s", lw=1.7, ms=4, label="true collapse (end-expiratory = permanent + TR)"),
       mlines.Line2D([0],[0], color=C_OD_T,   marker="o", lw=1.7, ms=4, label="true overdistension (TMP\u226523)"),
       mlines.Line2D([0],[0], color=C_COLL_C, lw=2.6, label="Costa collapse (compliance-based)"),
       mlines.Line2D([0],[0], color=C_OD_C,   lw=2.6, label="Costa overdistension (compliance-based)"),
       mlines.Line2D([0],[0], color=C_TRUE, lw=1.8, ls="--", label="true optimum PEEP"),
       mlines.Line2D([0],[0], color=C_COSTA, lw=1.6, label="Costa ODCL PEEP")]
fig.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, 0.985), ncol=6,
           frameon=False, fontsize=8.2, columnspacing=1.3, handletextpad=0.5)
fig.text(0.5, 0.925, "Per-DP collapse\u2013overdistension crossings (end-expiratory collapse definition): counting TR units as true collapse shifts the true optimum to higher PEEP, so Costa deviates downward at every DP",
         ha="center", fontsize=9.2, color="#333")

fig.savefig(os.path.join(OUT, "FigS1b_dp_crossings_en.png"), dpi=300, facecolor="white")
plt.close(fig)
print("wrote FigS1b_dp_crossings_en.png")
for dp in DP_LIST:
    d = data[dp]
    print("DP=%2d true=%.2f costa=%.2f dev=%+.2f TRmax=%.1f" % (dp, d["true"], d["costa"], d["true"]-d["costa"], d["trmax"]))
