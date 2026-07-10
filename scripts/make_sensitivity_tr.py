"""make_sensitivity_tr.py -- sensitivity figure for the TR-only Hickling study.

Reads out/sensitivity_tr.json (from sensitivity_tr.py) and renders:
    FigT6_sensitivity.png
      (A) 2x3 small multiples: deviation dev = Costa - true vs each parameter,
          reference value marked, dev=0 reference line, negative region shaded.
      (B) tornado summary: deviation range spanned by each parameter's sweep.

    python scripts/make_sensitivity_tr.py

Depends on out/sensitivity_tr.json.
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

for p in ["/System/Library/Fonts/\u30d2\u30e9\u30ae\u30ce\u89d2\u30b4\u30b7\u30c3\u30af W3.ttc",
          "/System/Library/Fonts/Hiragino Sans GB.ttc",
          "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"]:
    if os.path.exists(p):
        fm.fontManager.addfont(p); plt.rcParams["font.family"] = fm.FontProperties(fname=p).get_name(); break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110
plt.rcParams["savefig.dpi"] = 200

GE = "\u2267"; CMH = "cmH2O"
C_TR = "#9467bd"; C_DEV = "#8a5a00"; C_REF = "#d62728"; C_NEG = "#9467bd"

# panel order + Japanese labels
PANELS = [
    ("DP",     f"\u99c6\u52d5\u5727 DP ({CMH})"),                       # 駆動圧
    ("max_sp", f"\u4e0d\u5747\u4e00\u6027 max_sp ({CMH})"),             # 不均一性
    ("h_mean", f"P-V \u5f62\u72b6\u5b9a\u6570 h ({CMH})"),              # P-V形状
    ("TCP_TR", f"TR \u9589\u9396\u5727 TCP ({CMH})"),                   # 閉鎖圧
    ("OD_THR", f"\u904e\u81a8\u5f35\u95be\u5024 TMP{GE} ({CMH})"),      # 過膨張閾値
]


def draw(data):
    sw = data["sweeps"]
    fig = plt.figure(figsize=(13.6, 7.4))
    gs = gridspec.GridSpec(2, 4, figure=fig, width_ratios=[1, 1, 1, 1.15],
                           hspace=0.42, wspace=0.40,
                           left=0.058, right=0.985, top=0.86, bottom=0.10)

    # ---- (A) small multiples: dev vs each parameter ----
    cells = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    for (param, xlab), (r, c) in zip(PANELS, cells):
        ax = fig.add_subplot(gs[r, c])
        rows = sw[param]
        x = np.array([q["value"] for q in rows])
        dev = np.array([q["dev"] for q in rows])
        sd = np.array([q["dev_sd"] for q in rows])
        ax.axhspan(-5.3, 0, color=C_NEG, alpha=0.05)
        ax.axhline(0, color="k", lw=0.9, ls=":")
        ax.errorbar(x, dev, yerr=sd, fmt="o-", color=C_DEV, lw=2.0, ms=5, capsize=2.5)
        # mark reference
        for q in rows:
            if q["is_ref"]:
                ax.plot(q["value"], q["dev"], "o", ms=11, mfc="none",
                        mec=C_REF, mew=2.0, zorder=5)
        ax.set_xlabel(xlab, fontsize=10)
        if c == 0:
            ax.set_ylabel(f"\u4e56\u96e2 dev ({CMH})", fontsize=10.5)  # 乖離
        ax.set_ylim(-5.3, 1.1)
        ax.grid(alpha=0.22)
        ax.tick_params(labelsize=9)

    # ---- (B) tornado: dev range per parameter ----
    axT = fig.add_subplot(gs[:, 3])
    names_jp = {"DP": "\u99c6\u52d5\u5727 DP", "max_sp": "\u4e0d\u5747\u4e00\u6027",
                "h_mean": "P-V \u5f62\u72b6 h", "TCP_TR": "TR \u9589\u9396\u5727",
                "OD_THR": f"\u904e\u81a8\u5f35\u95be\u5024"}
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
        axT.text(ref_dev - 0.12, 0.15, f"\u57fa\u6e96 {ref_dev:+.2f}",
                 color=C_REF, fontsize=8.5, ha="right", va="bottom", rotation=90)  # 基準
    axT.set_yticks(ys); axT.set_yticklabels([names_jp[p] for p in order], fontsize=9.5)
    axT.set_xlabel(f"\u4e56\u96e2 dev \u306e\u7bc4\u56f2 ({CMH})", fontsize=10.5)  # 乖離の範囲
    axT.set_xlim(-5.5, 1.4); axT.set_ylim(-0.6, len(order) - 0.4)
    axT.set_title("各パラメータが動かす乖離の幅", fontsize=11, pad=10)
    axT.grid(alpha=0.22, axis="x")

    fig.suptitle("肺モデルパラメータ感度解析：TR による ODCL 乖離（dev<0）は広い範囲で頑健",
                 fontsize=13, y=0.965)
    fig.text(0.058, 0.015,
             "各パネル：代表 TR 条件（全肺 recruitable、gap=TOP\u22122=6）固定で当該パラメータのみを変化（赤丸＝基準値）。"
             "dev<0＝Costa ODCL が真値より低圧（TR による歪み）。"
             "DP=5〜15 全域で dev<0（低DPほど乖離大）。過膨張閾値 20 の端でのみ乖離がほぼ消失。",
             fontsize=8.8, color="#444")
    fig.savefig(os.path.join(OUT, "FigT6_sensitivity.png"))
    plt.close(fig)
    print("FigT6_sensitivity.png")


if __name__ == "__main__":
    data = json.load(open(os.path.join(OUT, "sensitivity_tr.json")))
    draw(data)
