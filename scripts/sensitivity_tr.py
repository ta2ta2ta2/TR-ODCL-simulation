"""sensitivity_tr.py -- one-at-a-time (OAT) parameter sensitivity for the
TR-only Hickling ODCL study.

We fix the lung at the representative TR condition of the primary analysis
(whole-lung recruitable, hysteresis width TOP - TCP = 10, i.e. TOP=12/TCP=2,
matching the "TR present" panel) and vary each key lung-model parameter one
at a time around its reference value, holding everything else fixed. For each value we recompute
the Costa ODCL, the true ODCL, and the deviation dev = Costa - true across
N_SEEDS seeds. The claim under test is that TR drives Costa ODCL BELOW the
true ODCL (dev < 0) robustly, across plausible variation in:

  DP        driving pressure (cmH2O)
  max_sp    superimposed-pressure / regional heterogeneity span (cmH2O)
  h_mean    alveolar P-V curve shape constant (cmH2O)
  TCP_TR    closing pressure of the TR units (cmH2O)
  TOP-TCP   alveolar hysteresis width of the TR units (cmH2O)
  OD_THR    overdistension transmural-pressure threshold (cmH2O)

    python scripts/sensitivity_tr.py

Depends on scripts/lung_model_core.py and scripts/metrics.py.
Writes out/sensitivity_tr.json and out/sensitivity_tr.csv.
"""
import os, sys, json, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as M
import lung_model_core as core

# ---- reference operating point --------------------------------------------
DP_REF     = 14.0
TOP_TR_REF = 12.0
TCP_TR_REF = 2.0        # reference hysteresis width TOP-TCP = 10
TR_SD      = 1.0
H_REF      = 4.9
MAXSP_REF  = 14.5
OD_REF     = 23.0
N_SEEDS    = 30
PEEP_GRID  = np.arange(24, 1, -1)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)


def make_lung(seed, dp=DP_REF, top_tr=TOP_TR_REF, tcp_tr=TCP_TR_REF,
              h_mean=H_REF, max_sp=MAXSP_REF):
    """Airway disabled; whole-lung recruitable alveolar units with hysteresis
    hysteresis width TOP-TCP = top_tr - tcp_tr (matches the primary sweep's cfg_tr)."""
    return M.make_lung(seed=seed, aop_mean=M.DISABLED_OPEN, aop_sd=0.0,
                       acp_mean=M.DISABLED_CLOSE, acp_sd=0.0,
                       top_mean=top_tr, top_sd=TR_SD, tcp_mean=tcp_tr, tcp_sd=TR_SD,
                       h_mean=h_mean, max_sp=max_sp)


def measure(**kw):
    """Mean Costa/true ODCL and deviation over seeds for a given parameter set.
    kw may include dp, top_tr, tcp_tr, h_mean, max_sp."""
    dp = kw.pop("dp", DP_REF)
    cst, tru = [], []
    for seed in range(N_SEEDS):
        lung = make_lung(seed, dp=dp, **kw)
        _, oc, ot = M.decremental_trial(lung, dp=dp, peep_grid=PEEP_GRID)
        if oc and ot:
            cst.append(oc); tru.append(ot)
    cst = np.array(cst); tru = np.array(tru); dev = cst - tru
    return dict(n=int(len(cst)), costa=float(cst.mean()), costa_sd=float(cst.std()),
                true=float(tru.mean()), true_sd=float(tru.std()),
                dev=float(dev.mean()), dev_sd=float(dev.std()))


def sweep(param, values, ref, unit, fixed_kw_fn):
    """Run measure() over values of one parameter. fixed_kw_fn(v)->kw dict."""
    rows = []
    for v in values:
        kw = fixed_kw_fn(v)
        r = measure(**kw)
        r.update(param=param, value=float(v), is_ref=bool(abs(v - ref) < 1e-9), unit=unit)
        rows.append(r)
        print(f"  {param:>7}={v:>6}{'*' if r['is_ref'] else ' '} "
              f"Costa={r['costa']:.2f} TRUE={r['true']:.2f} dev={r['dev']:+.3f}")
    return rows


if __name__ == "__main__":
    print(f"Sensitivity (OAT) around TOP-TCP={TOP_TR_REF-TCP_TR_REF:.0f} (TOP={TOP_TR_REF}/"
          f"TCP={TCP_TR_REF}), DP={DP_REF}, h={H_REF}, max_sp={MAXSP_REF}, OD={OD_REF}, n={N_SEEDS}")
    all_rows = {}

    print("[1] driving pressure DP")
    all_rows["DP"] = sweep("DP", [5, 7, 9, 11, 13, 14, 15], DP_REF, "cmH2O",
                           lambda v: dict(dp=float(v)))

    print("[2] superimposed-pressure span max_sp")
    all_rows["max_sp"] = sweep("max_sp", [10.0, 12.5, 14.5, 16.5, 18.0], MAXSP_REF, "cmH2O",
                               lambda v: dict(max_sp=float(v)))

    print("[3] P-V shape constant h_mean")
    all_rows["h_mean"] = sweep("h_mean", [3.9, 4.4, 4.9, 5.4, 5.9], H_REF, "cmH2O",
                               lambda v: dict(h_mean=float(v)))

    print("[4] TR closing pressure TCP_TR")
    all_rows["TCP_TR"] = sweep("TCP_TR", [0.0, 2.0, 4.0, 6.0], TCP_TR_REF, "cmH2O",
                               lambda v: dict(tcp_tr=float(v), top_tr=float(v) + 10.0))

    print("[5] overdistension threshold OD_THR")
    od_rows = []
    for v in [20.0, 23.0, 26.0]:
        core.MOJOLI_OD_THR = v
        r = measure()
        r.update(param="OD_THR", value=float(v), is_ref=bool(abs(v - OD_REF) < 1e-9), unit="cmH2O")
        od_rows.append(r)
        print(f"   OD_THR={v:>6}{'*' if r['is_ref'] else ' '} "
              f"Costa={r['costa']:.2f} TRUE={r['true']:.2f} dev={r['dev']:+.3f}")
    core.MOJOLI_OD_THR = OD_REF
    all_rows["OD_THR"] = od_rows

    ref = dict(gap=TOP_TR_REF - TCP_TR_REF, dp=DP_REF, top_tr=TOP_TR_REF, tcp_tr=TCP_TR_REF,
               h_mean=H_REF, max_sp=MAXSP_REF, od_thr=OD_REF, n_seed=N_SEEDS)
    json.dump({"reference": ref, "sweeps": all_rows},
              open(os.path.join(OUT, "sensitivity_tr.json"), "w"), indent=1)

    with open(os.path.join(OUT, "sensitivity_tr.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parameter", "value", "unit", "is_reference", "n_seed",
                    "costa_odcl_mean", "costa_odcl_sd", "true_odcl_mean", "true_odcl_sd",
                    "deviation_mean", "deviation_sd"])
        for param, rows in all_rows.items():
            for r in rows:
                w.writerow([r["param"], f'{r["value"]:.1f}', r["unit"], int(r["is_ref"]), r["n"],
                            f'{r["costa"]:.3f}', f'{r["costa_sd"]:.3f}',
                            f'{r["true"]:.3f}', f'{r["true_sd"]:.3f}',
                            f'{r["dev"]:.3f}', f'{r["dev_sd"]:.3f}'])
    print("wrote out/sensitivity_tr.json and out/sensitivity_tr.csv")
