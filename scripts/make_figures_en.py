"""make_figures_en.py -- ENGLISH manuscript figures for the TR-only Hickling study.

English-language clone of make_figures_tr.py. All on-figure text is in English;
keys/legends are embedded in the graphic (BMC Pulmonary Medicine rule).
Figures are rendered at 300 dpi with Arial, cropped tight for submission.

    python scripts/make_figures_en.py

Produces into out/ (English versions):
    Fig1_concept_en.png       -- what tidal recruitment (TR) is (single-unit schematic)
    Fig2_core_en.png          -- PRIMARY result: ODCL vs TOP; dev vs TR burden
    Fig3_states_odcl_en.png   -- merged 2x2: unit states (L) + ODCL crossing (R), no-TR/with-TR
    Fig4_mechanism_en.png     -- why Costa under-detects collapse (gap emphasised + detection lag)
    (Fig5_sensitivity_en.png is produced by make_sensitivity_en.py)

Depends on scripts/lung_model_core.py (verbatim lung_sim v83) and metrics.py.
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as M
import lung_model_core as core

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

# --- Arial for a clean journal sans-serif; embed as raster at 300 dpi ---
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
plt.rcParams["pdf.fonttype"] = 42   # embed TrueType (vector PDF safety)
plt.rcParams["ps.fonttype"] = 42

DP = 14.0
PEEP_GRID = np.arange(24, 1, -1)
OD_THR = core.MOJOLI_OD_THR
GE = "\u2265"; CMH = r"cmH$_2$O"   # subscript-2 via mathtext (Arial has no U+2082)
# TR-unit params (must match run_sweeps_tr.py)
TOP_TR = 8.0; TCP_TR = 2.0; TR_SD = 1.0
TCP_FIX = 2.0
TOP_REP = 12.0    # TOP-TCP = 10: representative TR-present condition
TOP_NOTR = 20.0   # TOP-TCP = 18: no TR (persistent closure) -- internal control
F_REP = 0.4

# colors (identical to the Japanese figures)
C_TRUE_COLL="#1f77b4"; C_TRUE_OD="#d62728"; C_COSTA_COLL="#7fb0d6"; C_COSTA_HYP="#e8908f"
C_ODCL_TRUE="#0b3d66"; C_ODCL_COSTA="#8a5a00"
C_STABLE="#2ca02c"; C_TR="#9467bd"; C_DEAD="#8c564b"


def make_frac_tr(seed, f_tr):
    lung = M.make_lung(seed=seed, aop_mean=M.DISABLED_OPEN, aop_sd=0.0,
                       acp_mean=M.DISABLED_CLOSE, acp_sd=0.0,
                       top_mean=TOP_TR, top_sd=TR_SD, tcp_mean=TCP_TR, tcp_sd=TR_SD)
    rng = np.random.default_rng(seed + 999)
    persistent = rng.random(lung.tops.shape) >= f_tr
    lung.tops = np.where(persistent, lung.tops + 12.0, lung.tops)
    return lung


def _pack(rows, oc, ot):
    P = np.array([r["peep"] for r in rows]); g = lambda k: np.array([r[k] for r in rows])
    comp = np.array([r["comp_per_comp"] for r in rows])
    return dict(P=P, oc=oc, ot=ot, tc=g("true_collapse"), od=g("overdist"),
                cc=g("coll_costa"), ch=g("hyper_costa"), so=g("stable_open"),
                tr=g("tidal_recruit"), ac=g("always_closed"),
                cyc=g("cyclic_reopen"), comp=comp)


def rep(f_tr, seed=0):
    lung = make_frac_tr(seed, f_tr)
    return _pack(*M.decremental_trial(lung, dp=DP, peep_grid=PEEP_GRID, collapse_mode="exp"))


def rep_gap(top, seed=0):
    lung = M.make_lung(seed=seed, aop_mean=M.DISABLED_OPEN, aop_sd=0.0,
                       acp_mean=M.DISABLED_CLOSE, acp_sd=0.0,
                       top_mean=top, top_sd=1.0, tcp_mean=TCP_FIX, tcp_sd=1.0)
    return _pack(*M.decremental_trial(lung, dp=DP, peep_grid=PEEP_GRID, collapse_mode="exp"))


# ============================================================ Fig1: concept
def fig_concept():
    fig = plt.figure(figsize=(7.4, 5.6))
    ax = fig.add_subplot(1, 1, 1)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.90, bottom=0.13)
    p = np.linspace(0, 30, 400)
    v = lambda pr: 1.0 * (1 - np.exp(-np.maximum(pr, 0) * np.log(2) / 4.9))
    ax.plot(p, v(p), color="#444", lw=2.0, label="Salazar P-V curve")
    top, tcp = 8.0, 2.0
    v_tcp, v_top = float(v(tcp)), float(v(top))
    ax.axvline(top, color=C_TR, ls="--", lw=1.2, alpha=0.7)
    ax.axvline(tcp, color=C_DEAD, ls="--", lw=1.2, alpha=0.7)
    ax.text(top+0.3, 0.04, "TOP", color=C_TR, fontsize=9.5, va="bottom")
    ax.text(tcp+0.3, 0.97, "TCP", color=C_DEAD, fontsize=9.5, va="top")
    ax.plot([tcp, top], [v_tcp, v_top], "o", color="#444", ms=6, zorder=6)
    ax.plot([tcp, top], [v_tcp, v_top], color="#1a7f37", lw=2.4, ls="--",
            label="Open unit")
    ax.plot([tcp, top], [0.0, v_top], color=C_TR, lw=3.0,
            label="TR unit")
    ax.plot([tcp], [0.0], "v", color=C_TR, ms=8, zorder=6)
    ax.fill_between([tcp, top], [0.0, v_top], [v_tcp, v_top],
                    color=C_TR, alpha=0.16, zorder=1)
    ax.set_xlabel(f"Transpulmonary pressure, TMP ({CMH})", fontsize=11)
    ax.set_ylabel("Unit volume (relative)", fontsize=11)
    ax.set_xlim(0, 30); ax.set_ylim(0, 1.05)
    ax.legend(fontsize=9.0, loc="lower right", framealpha=0.92)
    fig.savefig(os.path.join(OUT, "Fig1_concept_en.png"))
    plt.close(fig); print("Fig1_concept_en.png")


# ============================================================ Fig2: core result
def fig_core(gap):
    G = np.array([r["gap"] for r in gap])
    OC = np.array([r["costa"] for r in gap]); OCs = np.array([r["costa_sd"] for r in gap])
    OT = np.array([r["true"] for r in gap]);  OTs = np.array([r["true_sd"] for r in gap])
    DEV = np.array([r["dev"] for r in gap]);  DEVs = np.array([r["dev_sd"] for r in gap])
    PK = np.array([r["peak_cyclic"] for r in gap])

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.4))
    fig.subplots_adjust(left=0.07, right=0.985, top=0.88, bottom=0.14, wspace=0.24)
    ax = axes[0]
    TOPx = G + TCP_FIX
    ax.plot(TOPx, OT, "o-", color=C_ODCL_TRUE, lw=2.4, label="True ODCL")
    ax.fill_between(TOPx, OT-OTs, OT+OTs, color=C_ODCL_TRUE, alpha=0.10)
    ax.plot(TOPx, OC, "s-", color=C_ODCL_COSTA, lw=2.4, label="Costa ODCL")
    ax.fill_between(TOPx, OC-OCs, OC+OCs, color=C_ODCL_COSTA, alpha=0.10)
    ax.fill_between(TOPx, OC, OT, alpha=0.13, color=C_ODCL_COSTA)
    ax.set_xlim(TOPx.max()+0.6, TOPx.min()-0.6)
    ax.set_xlabel(f"Threshold opening pressure, TOP ({CMH})", fontsize=11.5)
    ax.set_ylabel(f"ODCL PEEP ({CMH})", fontsize=11.5)
    ax.set_title("(a)", loc="left", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10.5, loc="lower left", framealpha=0.92); ax.grid(alpha=0.25)

    ax2 = axes[1]
    ax2.errorbar(PK, DEV, yerr=DEVs, fmt="D-", color=C_TR, lw=2.4, capsize=3, ms=6)
    ax2.margins(x=0.08)
    ax2.axhline(0, color="k", lw=0.9, ls=":")
    ax2.set_xlabel("Peak cyclic-unit fraction (%)", fontsize=11.5)
    ax2.set_ylabel(f"\u0394PEEP = true \u2212 Costa ({CMH})", fontsize=11.5)
    ax2.set_title("(b)", loc="left", fontsize=12, fontweight="bold"); ax2.grid(alpha=0.25)
    fig.savefig(os.path.join(OUT, "Fig2_core_en.png"))
    plt.close(fig); print("Fig2_core_en.png")


# ================================================ Fig3: states (L) + ODCL (R)
def fig_states_odcl():
    """Merged 2x2: rows = No TR / With TR; left column = unit-state composition,
    right column = ODCL crossing (Costa vs true collapse/overdistension)."""
    d0 = rep_gap(TOP_NOTR); dR = rep_gap(TOP_REP)
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 9.2))
    fig.subplots_adjust(left=0.075, right=0.80, top=0.94, bottom=0.085,
                        wspace=0.16, hspace=0.26)
    rows = [(0, d0, "No TR"), (1, dR, "With TR")]
    tag = {(0, 0): "(a)", (0, 1): "(b)", (1, 0): "(c)", (1, 1): "(d)"}
    for r, d, cond in rows:
        P = d["P"]
        # --- left: state composition ---
        axS = axes[r, 0]
        axS.stackplot(P, d["so"], d["cyc"], d["ac"],
                      colors=[C_STABLE, C_TR, C_DEAD], alpha=0.85,
                      labels=["Stable open", "Cyclic (TR)", "Persistent collapse"])
        axS.plot(P, d["od"], color=C_TRUE_OD, lw=2.2, label=f"Overdistension (TMP{GE}23)")
        axS.set_xlim(20, 3); axS.set_ylim(0, 105)
        axS.set_ylabel("Unit fraction (%)", fontsize=11)
        axS.set_title(f"{tag[(r,0)]} {cond} \u2014 unit states", fontsize=12, pad=5)
        # --- right: ODCL crossing ---
        axO = axes[r, 1]
        axO.plot(P, d["cc"], color=C_COSTA_COLL, lw=2.4, label="Costa collapse %")
        axO.plot(P, d["ch"], color=C_COSTA_HYP, lw=2.4, label="Costa overdist. %")
        axO.plot(P, d["tc"], color=C_TRUE_COLL, lw=2.2, ls="--", label="True collapse % (end-expiratory)")
        axO.plot(P, d["od"], color=C_TRUE_OD, lw=2.2, ls="--", label=f"True overdist. % (TMP{GE}23)")
        lab_t = "True ODCL" if r == 0 else None
        lab_c = "Costa ODCL" if r == 0 else None
        if d["ot"]: axO.axvline(d["ot"], color=C_ODCL_TRUE, lw=1.8, ls=":", label=lab_t)
        if d["oc"]: axO.axvline(d["oc"], color=C_ODCL_COSTA, lw=1.8, ls=":", label=lab_c)
        axO.set_xlim(20, 3); axO.set_ylim(-2, 70)
        axO.set_ylabel("Fraction (%)", fontsize=11)
        axO.set_title(f"{tag[(r,1)]} {cond} \u2014 ODCL crossing", fontsize=12, pad=5)
        axO.grid(alpha=0.2)
    for ax in (axes[1, 0], axes[1, 1]):
        ax.set_xlabel(f"PEEP ({CMH})", fontsize=11)
    # two figure-level legends stacked in the far-right margin (no panel overlap)
    hS, lS = axes[0, 0].get_legend_handles_labels()
    hO, lO = axes[0, 1].get_legend_handles_labels()
    fig.legend(hS, lS, fontsize=9.2, loc="upper left", bbox_to_anchor=(0.815, 0.945),
               framealpha=0.95, title="Left column: unit states",
               title_fontsize=9.4, borderaxespad=0.0)
    fig.legend(hO, lO, fontsize=9.2, loc="upper left", bbox_to_anchor=(0.815, 0.63),
               framealpha=0.95, title="Right column: ODCL crossing",
               title_fontsize=9.4, borderaxespad=0.0)
    fig.savefig(os.path.join(OUT, "Fig3_states_odcl_en.png"))
    plt.close(fig); print("Fig3_states_odcl_en.png")


if __name__ == "__main__":
    data = json.load(open(os.path.join(OUT, "sweeps_tr.json")))
    gap = data["gap"]
    fig_concept()
    fig_core(gap)
    fig_states_odcl()
    print("all EN figures done")
