"""run_sweeps_tr.py -- TR-only (airway-free) sweeps for the Hickling ODCL study.

Hickling-type alveolar recruitment/derecruitment only. The airway mechanism
(AOP/ACP) is fully disabled; the ONLY cyclic mechanism is tidal recruitment
(TR): an alveolus opens at inspiration when TMP >= TOP and collapses at
expiration when TMP < TCP.

PRIMARY analysis -- alveolar hysteresis gap sweep (TOP - TCP)
------------------------------------------------------------
We vary the alveolar hysteresis width gap = TOP - TCP of the (recruitable)
lung units, holding TCP fixed at 2 cmH2O and all lung mechanics (DP, PEEP
range, P-V curve, OD threshold) fixed. The gap is the physical amount of
tidal recruitment: a wide gap (TOP high) means a unit that has collapsed at
expiration needs a much higher inspiratory pressure to re-open, so once the
PEEP drops it stays permanently closed (no cycling); a narrow gap means the
unit re-opens every inspiration (fully cyclic -> maximal TR).

    gap large (>= DP)  -> closed units stay closed  -> no TR      -> Costa ~ true
    gap small          -> units re-open every breath -> maximal TR -> Costa ODCL
                                                        pulled below true ODCL

The minimum gap analysed is 2 (gap = 0 is a degenerate point: TOP = TCP means
the unit opens and closes at the SAME pressure, i.e. hysteresis area = 0, which
is not tidal recruitment in the hysteresis sense -- excluded).

AUXILIARY analysis -- direct TR-fraction sweep
----------------------------------------------
For completeness we also vary the FRACTION f_TR of units that are cyclic
(TR units at fixed gap = 6; remaining units made persistent/Costa-neutral),
retained as supporting material. Capped at f_TR <= 0.6 (physiological upper
bound of cyclic burden; see refs).

    python scripts/run_sweeps_tr.py

Depends on scripts/lung_model_core.py (verbatim lung_sim v83) and scripts/metrics.py.
"""
import os, sys, json, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as M

DP = 14.0
PEEP_GRID = np.arange(24, 1, -1)
N_SEEDS = 30

# --- PRIMARY: alveolar hysteresis gap sweep (TOP - TCP) --------------------
TCP_FIX = 2.0
GAP_VALS = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22]  # TOP; gap = TOP - TCP_FIX = 2..20
# --- AUXILIARY: TR-fraction sweep ------------------------------------------
TOP_TR = 8.0                      # alveolar opening pressure of TR units
TCP_TR = 2.0                      # alveolar closing pressure (gap = 6, cyclic)
TR_SD = 1.0
FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]  # capped at 0.6: physiological upper bound of TR burden (see refs)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)


def make_frac_tr(seed, f_tr):
    """Lung where a fraction f_tr of subunits are tidally recruiting (cyclic),
    the rest are the SAME units made persistent (non-cyclic, Costa-neutral).

    TR units:  TOP=8+-1, TCP=2+-1 (gap=6) -> cycle across the titration.
    non-TR:    TOP raised by +12 (-> ~20) so they never tidally reopen; they
               stay open at high PEEP or collapse permanently at low PEEP.
    Airway mechanism disabled throughout (alveolar Hickling only).
    """
    lung = M.make_lung(seed=seed, aop_mean=M.DISABLED_OPEN, aop_sd=0.0,
                       acp_mean=M.DISABLED_CLOSE, acp_sd=0.0,
                       top_mean=TOP_TR, top_sd=TR_SD, tcp_mean=TCP_TR, tcp_sd=TR_SD)
    rng = np.random.default_rng(seed + 999)
    persistent = rng.random(lung.tops.shape) >= f_tr
    lung.tops = np.where(persistent, lung.tops + 12.0, lung.tops)
    return lung


def cfg_tr(top):
    """Auxiliary gap sweep config: airway disabled, alveolar TOP/TCP."""
    return dict(aop_mean=M.DISABLED_OPEN, aop_sd=0.0, acp_mean=M.DISABLED_CLOSE, acp_sd=0.0,
                top_mean=top, top_sd=1.0, tcp_mean=TCP_FIX, tcp_sd=1.0)


def sweep_frac(fracs):
    out = []
    for f in fracs:
        cst, tru, pk = [], [], []
        for seed in range(N_SEEDS):
            lung = make_frac_tr(seed, f)
            rows, oc, ot = M.decremental_trial(lung, dp=DP, peep_grid=PEEP_GRID, collapse_mode="exp")
            if oc and ot:
                cst.append(oc); tru.append(ot)
                pk.append(max(r["cyclic_reopen"] for r in rows))
        cst = np.array(cst); tru = np.array(tru); dev = tru - cst; pk = np.array(pk)
        out.append(dict(f_tr=float(f), n=int(len(cst)),
                        costa=float(cst.mean()), costa_sd=float(cst.std()),
                        true=float(tru.mean()), true_sd=float(tru.std()),
                        dev=float(dev.mean()), dev_sd=float(dev.std()),
                        peak_cyclic=float(pk.mean())))
        print(f"  f_TR={f:>3.1f} peakCyc={pk.mean():>4.1f}% Costa={cst.mean():.2f} "
              f"TRUE={tru.mean():.2f} dev={dev.mean():+.3f}")
    return out


def sweep_gap(vals, close_fix):
    out = []
    for v in vals:
        cst, tru, pk = [], [], []
        for seed in range(N_SEEDS):
            lung = M.make_lung(seed=seed, **cfg_tr(v))
            rows, oc, ot = M.decremental_trial(lung, dp=DP, peep_grid=PEEP_GRID, collapse_mode="exp")
            if oc and ot:
                cst.append(oc); tru.append(ot)
                pk.append(max(r["cyclic_reopen"] for r in rows))
        cst = np.array(cst); tru = np.array(tru); dev = tru - cst; pk = np.array(pk)
        out.append(dict(val=float(v), gap=float(v - close_fix), n=int(len(cst)),
                        costa=float(cst.mean()), costa_sd=float(cst.std()),
                        true=float(tru.mean()), true_sd=float(tru.std()),
                        dev=float(dev.mean()), dev_sd=float(dev.std()),
                        peak_cyclic=float(pk.mean())))
        print(f"  TOP={v:>2} gap={v-close_fix:>2} peakCyc={pk.mean():>4.1f}% "
              f"Costa={cst.mean():.2f} TRUE={tru.mean():.2f} dev={dev.mean():+.3f}")
    return out


if __name__ == "__main__":
    print(f"[PRIMARY] hysteresis gap sweep (airway disabled), DP={DP}, gap=2..20, n={N_SEEDS}")
    res_gap = sweep_gap(GAP_VALS, TCP_FIX)
    print(f"\n[AUX] TR-fraction sweep, DP={DP}, f_TR=0..0.6, n={N_SEEDS}")
    res_frac = sweep_frac(FRACS)

    json.dump({"gap": res_gap, "frac": res_frac, "dp": DP,
               "tcp_fix": TCP_FIX, "top_tr": TOP_TR, "tcp_tr": TCP_TR, "n_seed": N_SEEDS},
              open(os.path.join(OUT, "sweeps_tr.json"), "w"), indent=1)

    with open(os.path.join(OUT, "deviation_tr.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["analysis", "sweep_param", "value", "gap", "peak_cyclic_pct",
                    "n_seed", "costa_odcl_mean", "costa_odcl_sd",
                    "true_odcl_mean", "true_odcl_sd", "deviation_mean", "deviation_sd"])
        for r in res_gap:
            w.writerow(["primary_hysteresis_gap", "TOP", f'{r["val"]:.0f}', f'{r["gap"]:.0f}',
                        f'{r["peak_cyclic"]:.1f}',
                        r["n"], f'{r["costa"]:.3f}', f'{r["costa_sd"]:.3f}',
                        f'{r["true"]:.3f}', f'{r["true_sd"]:.3f}',
                        f'{r["dev"]:.3f}', f'{r["dev_sd"]:.3f}'])
        for r in res_frac:
            w.writerow(["aux_fraction_TR", "f_TR", f'{r["f_tr"]:.2f}', "", f'{r["peak_cyclic"]:.1f}',
                        r["n"], f'{r["costa"]:.3f}', f'{r["costa_sd"]:.3f}',
                        f'{r["true"]:.3f}', f'{r["true_sd"]:.3f}',
                        f'{r["dev"]:.3f}', f'{r["dev_sd"]:.3f}'])
    print("wrote out/sweeps_tr.json and out/deviation_tr.csv")
