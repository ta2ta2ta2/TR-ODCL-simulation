"""make_figures_tr.py -- TR-only (airway-free) presentation figures.

Regenerates all figures for the Hickling TR-ODCL presentation from the sweep
data (out/sweeps_tr.json) plus fresh representative decremental trials.

    python scripts/make_figures_tr.py

Produces into out/:
    FigT1_concept.png     -- what is tidal recruitment (TR) + how the hysteresis gap is set
    FigT2_core.png        -- PRIMARY result: ODCL vs hysteresis gap, and dev vs TR burden
    FigT3_curves.png      -- representative decremental trial, no-TR vs with-TR
    FigT4_states.png      -- state composition vs PEEP (no-TR vs with-TR)
    FigT5_mechanism.png   -- why Costa under-detects collapse (compliance peak)

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

# --- Japanese font (Hiragino for on-figure text) ---
for p in ["/System/Library/Fonts/\u30d2\u30e9\u30ae\u30ce\u89d2\u30b4\u30b7\u30c3\u30af W3.ttc",
          "/System/Library/Fonts/Hiragino Sans GB.ttc",
          "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"]:
    if os.path.exists(p):
        fm.fontManager.addfont(p); plt.rcParams["font.family"] = fm.FontProperties(fname=p).get_name(); break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110
plt.rcParams["savefig.dpi"] = 200

DP = 14.0
PEEP_GRID = np.arange(24, 1, -1)
OD_THR = core.MOJOLI_OD_THR
GE = "\u2267"; CMH = "cmH2O"
# TR-unit params (must match run_sweeps_tr.py)
TOP_TR = 8.0; TCP_TR = 2.0; TR_SD = 1.0
TCP_FIX = 2.0
# representative gap conditions for the illustrative (single-condition) panels
TOP_REP = 8.0     # gap = 6: TR present (matches the concept hysteresis loop)
TOP_NOTR = 20.0   # gap = 18: no TR (persistent closure) -- internal control
F_REP = 0.4       # kept for the auxiliary f_TR-based panels

# colors
C_TRUE_COLL="#1f77b4"; C_TRUE_OD="#d62728"; C_COSTA_COLL="#7fb0d6"; C_COSTA_HYP="#e8908f"
C_ODCL_TRUE="#0b3d66"; C_ODCL_COSTA="#8a5a00"
C_STABLE="#2ca02c"; C_TR="#9467bd"; C_DEAD="#8c564b"


def make_frac_tr(seed, f_tr):
    """Identical construction to run_sweeps_tr.make_frac_tr."""
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
    return _pack(*M.decremental_trial(lung, dp=DP, peep_grid=PEEP_GRID))


def rep_gap(top, seed=0):
    """Representative decremental trial for a whole-lung TR condition set by the
    alveolar hysteresis gap = top - TCP_FIX (airway disabled)."""
    lung = M.make_lung(seed=seed, aop_mean=M.DISABLED_OPEN, aop_sd=0.0,
                       acp_mean=M.DISABLED_CLOSE, acp_sd=0.0,
                       top_mean=top, top_sd=1.0, tcp_mean=TCP_FIX, tcp_sd=1.0)
    return _pack(*M.decremental_trial(lung, dp=DP, peep_grid=PEEP_GRID))


# ============================================================ FigT1: concept
def fig_concept():
    fig = plt.figure(figsize=(12.5, 5.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.24,
                          left=0.075, right=0.98, top=0.86, bottom=0.13)
    # -- left: single-unit pressure-volume with TR hysteresis loop
    ax = fig.add_subplot(gs[0, 0])
    p = np.linspace(0, 30, 400)
    v = lambda pr: 1.0 * (1 - np.exp(-np.maximum(pr, 0) * np.log(2) / 4.9))
    # Salazar P-V (inflation) curve
    ax.plot(p, v(p), color="#444", lw=2.0, label="Salazar P-V 曲線")
    top, tcp = 8.0, 2.0
    v_tcp, v_top = float(v(tcp)), float(v(top))
    # vertical guides at TCP / TOP
    ax.axvline(top, color=C_TR, ls="--", lw=1.2, alpha=0.7)
    ax.axvline(tcp, color=C_DEAD, ls="--", lw=1.2, alpha=0.7)
    ax.text(top+0.3, 0.04, "TOP\n（吸気で開通）", color=C_TR, fontsize=9.0, va="bottom")
    ax.text(tcp+0.3, 0.95, "TCP\n（呼気で虚脱）", color=C_DEAD, fontsize=9.0, va="top")
    # points on the curve at TCP and TOP
    ax.plot([tcp, top], [v_tcp, v_top], "o", color="#444", ms=6, zorder=6)
    # (1) chord along the curve: the open-unit slope (true compliance TCP->TOP)
    ax.plot([tcp, top], [v_tcp, v_top], color="#1a7f37", lw=2.4, ls="--",
            label="開存ユニットの傾き\n（曲線上 TCP→TOP を結ぶ直線）")
    # (2) TR apparent path: collapse (V=0) -> TOP, a steeper line
    ax.plot([tcp, top], [0.0, v_top], color=C_TR, lw=3.0,
            label="TR ユニットの見かけの傾き\n（虚脱 V=0 →TOP）")
    ax.plot([tcp], [0.0], "v", color=C_TR, ms=8, zorder=6)
    # shade the wedge between the two slopes = excess apparent compliance
    ax.fill_between([tcp, top], [0.0, v_top], [v_tcp, v_top],
                    color=C_TR, alpha=0.16, zorder=1)
    ax.annotate("虚脱から立ち上がるぶん\n傾き（見かけコンプライアンス）が\n直線より急に見える",
                xy=(4.6, 0.30), xytext=(9.6, 0.56), fontsize=9.0, color=C_TR,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color=C_TR, lw=1.4))
    ax.set_xlabel(f"経肺圧 TMP ({CMH})", fontsize=11)
    ax.set_ylabel("ユニット容量（相対）", fontsize=11)
    ax.set_title("TR ユニットの見かけコンプライアンスは開存直線より大きい", fontsize=11.5, pad=8)
    ax.set_xlim(0, 30); ax.set_ylim(0, 1.05)
    ax.text(0.03, 0.985,
            "毎呼吸、吸気で開通し呼気で虚脱を繰り返すユニット。\n"
            "気道機序は無効化し肺胞ヒステリシス（TOP/TCP）のみ。",
            transform=ax.transAxes, fontsize=8.8, va="top", color="#333")
    ax.legend(fontsize=8.2, loc="lower right", framealpha=0.92)
    # -- right: how the hysteresis gap is controlled
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis("off")
    ax2.set_title("本研究の操作：ヒステリシス gap ＝ TOP − TCP", fontsize=12.5, pad=8)
    ax2.text(0.0, 0.96,
             "肺の力学（DP、PEEP範囲、P-V曲線、\n過膨張閾値）は全条件で固定。\n"
             "変えるのは肺胞ヒステリシス幅 gap ただ一つ：",
             transform=ax2.transAxes, fontsize=10.5, va="top", color="#222",
             linespacing=1.5)
    ax2.text(0.04, 0.68,
             "• gap 小（例 gap=2〜6、TOP 低）\n"
             "   呼気で虚脱→吸気で毎回再開通\n"
             "   ＝ TR 強い（cyclic ユニット多い）\n\n"
             "• gap 大（例 gap≧14、TOP 高）\n"
             "   一度虚脱すると再開通せず恒久虚脱\n"
             "   ＝ TR 消失（Costa 中立、乖離≒0）",
             transform=ax2.transAxes, fontsize=10.0, va="top", color="#222",
             linespacing=1.5)
    ax2.text(0.04, 0.12,
             "→ gap≧DP 付近で TR 消失＝Costa≒真（対照）\n→ gap を縮めると TR の影響だけが現れる\n"
             "  （TCP=2 固定、最小 gap=2）",
             transform=ax2.transAxes, fontsize=10.0, va="bottom",
             color=C_TR, fontweight="bold", linespacing=1.5)
    fig.savefig(os.path.join(OUT, "FigT1_concept.png"))
    plt.close(fig); print("FigT1_concept.png")


# ============================================================ FigT2: core result
def fig_core(gap):
    G = np.array([r["gap"] for r in gap])
    OC = np.array([r["costa"] for r in gap]); OCs = np.array([r["costa_sd"] for r in gap])
    OT = np.array([r["true"] for r in gap]);  OTs = np.array([r["true_sd"] for r in gap])
    DEV = np.array([r["dev"] for r in gap]);  DEVs = np.array([r["dev_sd"] for r in gap])
    PK = np.array([r["peak_cyclic"] for r in gap])

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.4))
    fig.subplots_adjust(left=0.07, right=0.985, top=0.88, bottom=0.14, wspace=0.24)
    # -- left: ODCL vs hysteresis gap (small gap = strong TR on the LEFT) --
    ax = axes[0]
    ax.plot(G, OT, "o-", color=C_ODCL_TRUE, lw=2.4, label="真の ODCL")
    ax.fill_between(G, OT-OTs, OT+OTs, color=C_ODCL_TRUE, alpha=0.10)
    ax.plot(G, OC, "s-", color=C_ODCL_COSTA, lw=2.4, label="Costa ODCL")
    ax.fill_between(G, OC-OCs, OC+OCs, color=C_ODCL_COSTA, alpha=0.10)
    ax.fill_between(G, OC, OT, alpha=0.13, color=C_ODCL_COSTA)
    ax.set_xlim(G.max()+0.6, G.min()-0.6)   # small gap (strong TR) on the right
    ax.set_xlabel(f"ヒステリシス gap ＝ TOP − TCP ({CMH})   ←gap 縮小＝TR 増大", fontsize=11)
    ax.set_ylabel(f"ODCL PEEP ({CMH})", fontsize=11.5)
    ax.set_title("gap が小さい（TR が強い）ほど Costa ODCL が真値から下方に乖離", fontsize=11.5, pad=8)
    ax.legend(fontsize=10.5, loc="lower left", framealpha=0.92); ax.grid(alpha=0.25)

    # -- right: dev vs peak cyclic burden (monotonic) --
    ax2 = axes[1]
    ax2.errorbar(PK, DEV, yerr=DEVs, fmt="D-", color=C_TR, lw=2.4, capsize=3, ms=6)
    for x, y, gg in zip(PK, DEV, G):
        if gg in (2, 6, 10, 14, 18):
            ax2.annotate(f"gap={gg:.0f}", (x, y), fontsize=8.5, ha="left",
                         xytext=(4, 5), textcoords="offset points")
    ax2.margins(x=0.08)
    ax2.axhline(0, color="k", lw=0.9, ls=":")
    ax2.set_xlabel("実際の TR 負荷 ＝ ピーク cyclic ユニット% ", fontsize=11.5)
    ax2.set_ylabel(f"乖離 dev ＝ Costa − 真 ({CMH})", fontsize=11.5)
    ax2.set_title("TR 負荷と乖離量は単調に対応", fontsize=12, pad=8); ax2.grid(alpha=0.25)
    fig.text(0.985, 0.012,
             "主軸はヒステリシス gap（TOP−TCP、最小 gap=2）。参考: "
             "Retamal/Bugedo, Intensive Care Med 2011 (PMID 21483386); "
             "Mojoli et al, Crit Care 2023 (PMC10261834)",
             fontsize=6.4, color="#666", ha="right", va="bottom")
    fig.savefig(os.path.join(OUT, "FigT2_core.png"))
    plt.close(fig); print("FigT2_core.png")


# ============================================================ FigT3: repr curves
def fig_curves():
    d0 = rep_gap(TOP_NOTR); dR = rep_gap(TOP_REP)
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.4), sharey=True)
    fig.subplots_adjust(left=0.06, right=0.985, top=0.86, bottom=0.14, wspace=0.10)
    for ax, d, ttl in [(axes[0], d0, f"TR なし（gap=18）"),
                       (axes[1], dR, f"TR あり（gap=6）")]:
        P = d["P"]
        ax.plot(P, d["cc"], color=C_COSTA_COLL, lw=2.4, label="Costa 虚脱%")
        ax.plot(P, d["ch"], color=C_COSTA_HYP, lw=2.4, label="Costa 過膨張%")
        ax.plot(P, d["tc"], color=C_TRUE_COLL, lw=2.2, ls="--", label="真の虚脱%")
        ax.plot(P, d["od"], color=C_TRUE_OD, lw=2.2, ls="--", label=f"真の過膨張%(TMP{GE}23)")
        if d["ot"]: ax.axvline(d["ot"], color=C_ODCL_TRUE, lw=1.8, ls=":")
        if d["oc"]: ax.axvline(d["oc"], color=C_ODCL_COSTA, lw=1.8, ls=":")
        ax.set_xlim(20, 3); ax.set_ylim(-2, 70)
        ax.set_xlabel(f"PEEP ({CMH})  ←減圧", fontsize=11)
        ax.set_title(ttl, fontsize=12.5, pad=6)
        ax.grid(alpha=0.2)
        txt = f"真 ODCL={d['ot']:.1f}\nCosta ODCL={d['oc']:.1f}\ndev={d['oc']-d['ot']:+.1f}"
        ax.text(0.03, 0.97, txt, transform=ax.transAxes, fontsize=10.5, va="top",
                bbox=dict(boxstyle="round", fc="white", ec="#bbb", alpha=0.9))
    axes[0].set_ylabel("割合 (%)", fontsize=11.5)
    axes[1].legend(fontsize=9.5, loc="lower left", framealpha=0.92)
    fig.suptitle("代表的な減圧トライアル：TR が Costa の虚脱・過膨張検出を歪め ODCL 交差点を低圧へ",
                 fontsize=12.5, y=0.955)
    fig.savefig(os.path.join(OUT, "FigT3_curves.png"))
    plt.close(fig); print("FigT3_curves.png")


# ============================================================ FigT4: states
def fig_states():
    d0 = rep_gap(TOP_NOTR); dR = rep_gap(TOP_REP)
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.4), sharey=True)
    fig.subplots_adjust(left=0.06, right=0.85, top=0.86, bottom=0.14, wspace=0.10)
    for ax, d, ttl in [(axes[0], d0, f"TR なし（gap=18）"),
                       (axes[1], dR, f"TR あり（gap=6）")]:
        P = d["P"]
        # so + cyc + ac sum to 100%; overdistension is a SUBSET of ventilating
        # units, so overlay it as a line (do not stack) to keep the axis at 100%.
        ax.stackplot(P, d["so"], d["cyc"], d["ac"],
                     colors=[C_STABLE, C_TR, C_DEAD], alpha=0.85,
                     labels=["安定開通", "cyclic（TR）", "恒久虚脱"])
        ax.plot(P, d["od"], color=C_TRUE_OD, lw=2.4, label=f"過膨張(TMP{GE}23)")
        ax.set_xlim(20, 3); ax.set_ylim(0, 105)
        ax.set_xlabel(f"PEEP ({CMH})  ←減圧", fontsize=11)
        ax.set_title(ttl, fontsize=12.5, pad=6)
    axes[0].set_ylabel("ユニット割合 (%)", fontsize=11.5)
    # 100% stacked area has no interior blank space -> legend outside, right margin
    axes[1].legend(fontsize=9.5, loc="center left", bbox_to_anchor=(1.02, 0.5),
                   framealpha=0.95)
    fig.suptitle("状態組成：TR あり条件でのみ cyclic ユニット（紫）が出現", fontsize=12.5, y=0.955)
    fig.savefig(os.path.join(OUT, "FigT4_states.png"))
    plt.close(fig); print("FigT4_states.png")


# ============================================================ FigT5: mechanism
def fig_mechanism():
    dR = rep_gap(TOP_REP)
    P = dR["P"]
    fig, ax2 = plt.subplots(1, 1, figsize=(8.4, 5.4))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.14)
    # costa vs true collapse% — detection lag
    ax2.plot(P, dR["cc"], color=C_COSTA_COLL, lw=2.6, label="Costa 虚脱%（見かけ）")
    ax2.plot(P, dR["tc"], color=C_TRUE_COLL, lw=2.4, ls="--", label="真の虚脱%（恒久虚脱）")
    if dR["ot"]: ax2.axvline(dR["ot"], color=C_ODCL_TRUE, lw=1.8, ls=":",
                             label=f"真の ODCL {dR['ot']:.1f}")
    if dR["oc"]: ax2.axvline(dR["oc"], color=C_ODCL_COSTA, lw=1.8, ls=":",
                             label=f"Costa ODCL {dR['oc']:.1f}")
    ax2.set_xlim(20, 3); ax2.set_xlabel(f"PEEP ({CMH})  ←減圧", fontsize=11.5)
    ax2.set_ylabel("虚脱 (%)", fontsize=11.5)
    ax2.set_title("Costa は虚脱検出が低圧まで遅れる→交差点が低圧へ", fontsize=12, pad=8)
    ax2.legend(fontsize=10.0, loc="upper left", framealpha=0.92); ax2.grid(alpha=0.22)
    fig.suptitle("機序：TR による見かけコンプライアンス上昇が Costa の虚脱過小評価を生む",
                 fontsize=12.5, y=0.965)
    fig.savefig(os.path.join(OUT, "FigT5_mechanism.png"))
    plt.close(fig); print("FigT5_mechanism.png")


if __name__ == "__main__":
    data = json.load(open(os.path.join(OUT, "sweeps_tr.json")))
    gap = data["gap"]
    fig_concept()
    fig_core(gap)
    fig_curves()
    fig_states()
    fig_mechanism()
    print("all TR figures done")
