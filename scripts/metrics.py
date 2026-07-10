"""metrics.py -- user-defined state classification and ODCL indices.

Built on lung_model_core.py (verbatim extraction of lung_sim_v83) LungModel.
Shows that, with AOP / tidal recruitment present, Costa ODCL deviates from the
true ODCL that minimizes true-collapse + overdistension.

Definitions (finalized for this study)
--------------------------------------
* TRUE collapse = units that never ventilate at any point of the breath
    = alveolus collapsed throughout, OR air-trapped throughout (airway shut throughout)
    = model's always_closed (~alv2 : not open even at end-inspiratory PIP)
* cyclic reopening (the CAUSE of distortion) = units open at inspiration but shut at expiration
    = air_trap (airway closes at expiration, volume retained)
      + tidal_recruit (alveolus collapses at expiration)
    -> excluded from TRUE collapse because they are not shut "throughout"
* overdistension = ventilating units whose end-inspiratory transpulmonary pressure TMP >= 23
* TRUE ODCL  = PEEP where true-collapse% crosses overdistension%
* Costa ODCL = PEEP where uncorrected-compliance collapse%/hyper% cross
               (no AOP correction is used anywhere)
"""
import numpy as np
import lung_model_core as core

OD_THR = core.MOJOLI_OD_THR   # 23.0

# Thresholds to "always open (disable)" a compartment (closing pressure to a large negative).
DISABLED_CLOSE = -20.0
DISABLED_OPEN = 0.0


def make_lung(seed, aop_mean, aop_sd, acp_mean, acp_sd,
              top_mean, top_sd, tcp_mean, tcp_sd,
              tlc_L=2.5, h_mean=4.9, h_sd=0.1, n_comp=30, max_sp=14.5):
    """Build a LungModel with a fixed seed (v83 RNG is global) for reproducibility."""
    np.random.seed(seed)
    return core.LungModel(
        n_compartments=n_comp, max_sp_g1=max_sp,
        aop_mean_g1=aop_mean, aop_sd_g1=aop_sd, acp_mean_g1=acp_mean, acp_sd_g1=acp_sd,
        top_mean_g1=top_mean, top_sd_g1=top_sd, tcp_mean_g1=tcp_mean, tcp_sd_g1=tcp_sd,
        tlc_L_g1=tlc_L, h_mean_g1=h_mean, h_sd_g1=h_sd,
    )


def decremental_trial(lung, dp=15.0, peep_grid=None, pip_rec=45.0, n_stab=5):
    """Decremental PEEP trial. Returns per-PEEP state distribution + compliance,
    with true_collapse = always_closed and cyclic = air_trap + tidal_recruit."""
    if peep_grid is None:
        peep_grid = np.arange(24, 1, -1)
    sp = lung.sp
    tp_rec = pip_rec - sp
    cur_air = (tp_rec >= lung.aops)
    cur_alv = cur_air & (tp_rec >= lung.tops)

    rows = []
    for peep in peep_grid:
        fa, fv = lung.stabilize_lung_state(peep, dp, cur_air, cur_alv, n_stab)
        s = core._mojoli_state_dist(lung, peep, dp, fa, fv)
        _, _, _, _, _, vt_per_comp = lung.get_trial_metrics(peep, dp, fa, fv)
        comp_pc = (vt_per_comp / dp * 1000) if dp > 1e-9 else np.zeros(lung.n_compartments)
        rows.append(dict(
            peep=float(peep),
            comp_per_comp=comp_pc,
            stable_open=s['stable_open'],
            air_trap=s['air_trap'],
            tidal_recruit=s['tidal_recruit'],
            always_closed=s['always_closed'],
            overdist=s['overdist'],
            true_collapse=s['always_closed'],
            cyclic_reopen=s['air_trap'] + s['tidal_recruit'],
        ))
        _, _, cur_air, cur_alv, _, _ = lung.get_trial_metrics(peep, 0, fa, fv)

    peeps = [r['peep'] for r in rows]
    comp_arr = np.array([r['comp_per_comp'] for r in rows])
    bi = np.argmax(comp_arr, axis=0); bc = np.max(comp_arr, axis=0)
    for i, r in enumerate(rows):
        hyp_u, coll_u = core._calc_odcl(comp_arr[i], bc, bi, i)
        r['hyper_costa'] = hyp_u
        r['coll_costa'] = coll_u
    odcl_costa = core._find_odcl(peeps, [r['coll_costa'] for r in rows],
                                        [r['hyper_costa'] for r in rows])
    odcl_true = core._find_odcl(peeps, [r['true_collapse'] for r in rows],
                                       [r['overdist'] for r in rows])
    return rows, odcl_costa, odcl_true
