"""lung_model_core.py — headless extraction of lung_sim_v83.py core logic.
Verbatim LungModel + Costa/Mojoli ODCL functions, gradio UI stripped.
Source: AOPODCLrevise/lung_sim/lung_sim_v83.py (2026-07-01).
"""
import numpy as np
import matplotlib.pyplot as plt
import traceback

# ==============================================================================
# UI ヘルパー関数 と 定数定義
# ==============================================================================
PRESETS = {
    "Custom": {},
    "NORMAL": {
        "tlc_ml": 6660.0, "h_mean": 7.58, "h_sd": 0,
        "aop_mean": 3.0, "aop_sd": 1.0, "acp_mean": 1.0, "acp_sd": 0.5,
        "top_mean": 2.0, "top_sd": 1.0, "tcp_mean": 1.0, "tcp_sd": 0.5,
        "max_sp": 5.0,
    },
    "ARDS": {
        "tlc_ml": 2500.0, "h_mean": 4.9, "h_sd": 0,
        "aop_mean": 5.0, "aop_sd": 1.0, "acp_mean": 3.0, "acp_sd": 1.0,
        "top_mean": 20.0, "top_sd": 4.0,
        "tcp_mean": 2.0, "tcp_sd": 1.0,
        "max_sp": 14.5,
    },
}

def update_params_from_preset(*a, **k):
    return None  # (UI helper removed for headless core)

# ==============================================================================
# 肺モデルのコアロジック
# V82変更点:
#   ① AOP≥TOP制約の撤廃
#   ② Trap状態 VT: vol(ACP−SP) → vol(AOP)
#   ③ Trap+TCP虚脱 VT: vol(AOP) → 0
#   ④ Recruit-Can VT: vol(TCP) → 0
#   ⑤ ep/dpe補正コンプライアンスを追加計算
# ==============================================================================
class LungModel:
    def __init__(self, n_compartments,
                 max_sp_g1, aop_mean_g1, aop_sd_g1, acp_mean_g1, acp_sd_g1,
                 top_mean_g1, top_sd_g1, tcp_mean_g1, tcp_sd_g1,
                 tlc_L_g1, h_mean_g1, h_sd_g1,
                 max_sp_g2=None, aop_mean_g2=None, aop_sd_g2=None,
                 acp_mean_g2=None, acp_sd_g2=None,
                 top_mean_g2=None, top_sd_g2=None,
                 tcp_mean_g2=None, tcp_sd_g2=None,
                 tlc_L_g2=None, h_mean_g2=None, h_sd_g2=None):

        self.n_compartments = n_compartments
        self.n_alveoli_per_comp = 1000
        self.frc_L = 0.0
        is_bimodal = max_sp_g2 is not None

        if is_bimodal:
            n_comp_g1 = self.n_compartments // 2
            n_comp_g2 = self.n_compartments - n_comp_g1
            total_units_g1 = n_comp_g1 * self.n_alveoli_per_comp
            total_units_g2 = n_comp_g2 * self.n_alveoli_per_comp
        else:
            n_comp_g1 = self.n_compartments
            n_comp_g2 = 0
            total_units_g1 = n_comp_g1 * self.n_alveoli_per_comp

        sp_g1 = np.linspace(0, max_sp_g1, n_comp_g1)
        if is_bimodal:
            sp_g2 = np.linspace(0, max_sp_g2, n_comp_g2)
            sp_flat_comp = np.concatenate((sp_g1, sp_g2))
        else:
            sp_flat_comp = sp_g1

        self.sp = sp_flat_comp[:, np.newaxis]   # (n_comp, 1)

        # ── 変更⑤: ep/dpe補正用にSP・AOP_mean配列を保持 ──────────────────────
        self.sp_per_comp = sp_flat_comp          # (n_comp,)  1D
        aop_mean_arr = np.full(n_comp_g1, aop_mean_g1)
        if is_bimodal:
            aop_mean_arr = np.concatenate([aop_mean_arr,
                                           np.full(n_comp_g2, aop_mean_g2)])
        self.aop_mean_per_comp = aop_mean_arr    # (n_comp,)  1D
        # ────────────────────────────────────────────────────────────────────────

        def _gen(mean1, sd1, mean2, sd2):
            a = np.random.normal(mean1, sd1, (n_comp_g1, self.n_alveoli_per_comp))
            if is_bimodal:
                b = np.random.normal(mean2, sd2, (n_comp_g2, self.n_alveoli_per_comp))
                return np.concatenate((a, b), axis=0)
            return a

        self.aops = _gen(aop_mean_g1, aop_sd_g1, aop_mean_g2, aop_sd_g2)
        self.acps = _gen(acp_mean_g1, acp_sd_g1, acp_mean_g2, acp_sd_g2)
        self.tops = _gen(top_mean_g1, top_sd_g1, top_mean_g2, top_sd_g2)
        self.tcps = _gen(tcp_mean_g1, tcp_sd_g1, tcp_mean_g2, tcp_sd_g2)
        self.h_units = _gen(h_mean_g1, h_sd_g1, h_mean_g2, h_sd_g2)

        for arr in [self.aops, self.tops]: arr[arr < 0] = 0

        # ── 変更①: AOP≥TOP制約の撤廃（AOP≥ACP, TOP≥TCP のみ） ────────────────
        self.aops = np.maximum(self.aops, self.acps)
        self.tops = np.maximum(self.tops, self.tcps)
        # self.aops = np.maximum(self.aops, self.tops)  ← 旧制約（削除）
        # ────────────────────────────────────────────────────────────────────────

        if is_bimodal:
            if tlc_L_g1 <= 0 or tlc_L_g2 <= 0:
                raise ValueError("TLCは0より大きい必要があります。")
            v0_g1 = np.full((n_comp_g1, self.n_alveoli_per_comp),
                            tlc_L_g1 / total_units_g1)
            v0_g2 = np.full((n_comp_g2, self.n_alveoli_per_comp),
                            tlc_L_g2 / total_units_g2)
            self.v0_unit_L_array = np.concatenate((v0_g1, v0_g2), axis=0)
        else:
            if tlc_L_g1 <= 0: raise ValueError("TLCは0より大きい必要があります。")
            self.v0_unit_L_array = np.full(
                (n_comp_g1, self.n_alveoli_per_comp), tlc_L_g1 / total_units_g1)

        self.h_units[self.h_units <= 0.1] = 0.1

    def _vol(self, pressure):
        p = np.maximum(0, pressure)
        return np.maximum(0, self.v0_unit_L_array * (1 - np.exp(-(p * np.log(2)) / self.h_units)))

    def _vol_state(self, peep, airway_open, alv_open_or_trapped):
        """静的EELV（PVループ用）"""
        tp = peep - self.sp
        can = airway_open & alv_open_or_trapped
        trapped = ~airway_open & alv_open_or_trapped
        # Fix2: ACP>TCPのとき気道が先に閉じるため肺胞はvol(ACP)を保持
        trap_open = trapped & ((tp >= self.tcps) | (self.acps > self.tcps))
        return self.frc_L + np.sum(self._vol(tp) * can) + np.sum(self._vol(self.acps) * trap_open)

    def get_trial_metrics(self, peep, dp, start_air, start_alv):
        ti = peep + dp - self.sp
        te = peep - self.sp

        # 吸気後状態
        air_insp = start_air | (ti >= self.aops)
        alv_insp = (start_alv | (ti >= self.tops)) & air_insp

        vol_peak = self._vol(ti)
        total_peak = self.frc_L + np.sum(vol_peak * alv_insp)

        # 呼気後状態
        aw_exp  = (te >= self.acps)
        alv_exp = (te >= self.tcps)
        can     = alv_insp & aw_exp & alv_exp      # 気道・肺胞 ともに開通
        trapped = alv_insp & ~aw_exp               # 気道閉鎖
        # Fix2: ACP>TCPのとき気道が先に閉じるため肺胞はvol(ACP)を保持
        trap_open = trapped & (alv_exp | (self.acps > self.tcps))
        # trap_collapse: both closed AND ACP<=TCP → vol=0

        new_air = alv_insp & aw_exp
        new_alv = can | trap_open   # FIX: trap_collapse (both closed) → vol=0, not phantom-open

        # ── EELV（trap_open→vol(ACP)を使用, trap_collapse→0） ─────────────────
        vol_te  = self._vol(te)
        vol_acp = self._vol(self.acps)             # Fix2: vol(AOP)→vol(ACP)
        eelv = self.frc_L + np.sum(vol_te * can) + np.sum(vol_acp * trap_open)
        # ────────────────────────────────────────────────────────────────────────

        tidal_volume   = total_peak - eelv
        total_comp     = tidal_volume / dp if dp > 0 else 0.0

        # ── VT per comp ──────────────────────────────────────────────────────
        vt_peak_comp = np.sum(vol_peak * alv_insp, axis=1)
        normal_can   = can & start_alv                          # 以前から開通のcan → vol(te)
        # recruit_can = can & ~start_alv                        # 新規開通 → 0
        vt_eelv_comp = (np.sum(vol_te  * normal_can,  axis=1)  # normal_can: vol(te)
                      + np.sum(vol_acp * trap_open,   axis=1)) # trap_open:  vol(ACP)
        vt_per_comp  = vt_peak_comp - vt_eelv_comp
        # ────────────────────────────────────────────────────────────────────────

        return tidal_volume, total_comp, new_air, new_alv, eelv, vt_per_comp

    def generate_pv_loop(self, peep, peak_pressure, start_air, start_alv):
        insp_p = np.linspace(peep, peak_pressure, 100)
        exp_p  = np.linspace(peak_pressure, peep, 100)
        q_bnd  = [0, self.n_compartments//4, self.n_compartments//2,
                  3*self.n_compartments//4, self.n_compartments]

        vol_acp = self._vol(self.acps)             # Fix2: vol(ACP) for trapped units
        end_alv = np.zeros_like(self.aops, dtype=bool)
        insp_v, quad_v = [], [[] for _ in range(4)]

        for i, p in enumerate(insp_p):
            tp = p - self.sp
            air_p = start_air | (tp >= self.aops)
            alv_p = start_alv | (tp >= self.tops)
            can_v = air_p & alv_p
            trap_v = start_alv & ~air_p            # 気道閉鎖・肺胞保持 → vol(ACP)
            v = self._vol(tp)
            rv = np.sum(v * can_v) + np.sum(vol_acp * trap_v)
            insp_v.append((self.frc_L + rv) * 1000)
            for j in range(4):
                s = slice(q_bnd[j], q_bnd[j+1])
                qrv = np.sum(v[s]*can_v[s]) + np.sum(vol_acp[s]*trap_v[s])
                qfrc = self.frc_L / self.n_compartments * (q_bnd[j+1]-q_bnd[j])
                quad_v[j].append((qfrc + qrv) * 1000)
            if i == len(insp_p)-1:
                end_alv = can_v | trap_v

        exp_v = []
        for p in exp_p:
            tp = p - self.sp
            aw  = (tp >= self.acps)
            can_e   = aw & (tp >= self.tcps) & end_alv
            # Fix2: ACP>TCPのとき気道が先に閉じるため肺胞はvol(ACP)を保持
            trap_oe = ~aw & end_alv & ((tp >= self.tcps) | (self.acps > self.tcps))
            v = self._vol(tp)
            rv = np.sum(v * can_e) + np.sum(vol_acp * trap_oe)
            exp_v.append((self.frc_L + rv) * 1000)

        return insp_p, np.array(insp_v), exp_p, np.array(exp_v), np.array(quad_v)

    def stabilize_lung_state(self, peep, dp, start_air=None, start_alv=None, num_breaths=15):
        air = np.zeros_like(self.aops, dtype=bool) if start_air is None else start_air.copy()
        alv = np.zeros_like(self.aops, dtype=bool) if start_alv is None else start_alv.copy()
        for _ in range(num_breaths):
            _, _, air, alv, _, _ = self.get_trial_metrics(peep, dp, air, alv)
        return air, alv

    def run_peep_trial(self, peep_levels, dp_or_vt, mode='pcv', pip_max=60):
        results = []
        last_dp = 15.0

        # 初期最大リクルート
        tp_rec = pip_max - self.sp
        cur_air = (tp_rec >= self.aops)
        cur_alv = cur_air & (tp_rec >= self.tops)

        for peep in peep_levels:
            dp = dp_or_vt if mode == 'pcv' else last_dp

            if mode == 'vcv':
                target_vt = dp_or_vt / 1000.0
                lo, hi = 0.1, 60.0
                tmp_air, tmp_alv = self.stabilize_lung_state(peep, last_dp, cur_air, cur_alv, 5)
                for _ in range(50):
                    mid = (lo + hi) / 2
                    vt_mid, *_ = self.get_trial_metrics(peep, mid, tmp_air, tmp_alv)
                    if abs(vt_mid - target_vt) < 0.0005: break
                    if vt_mid < target_vt: lo = mid
                    else: hi = mid
                dp = mid; last_dp = dp

            # 5回安定化 + 1回計測（V82: 統一）
            fin_air, fin_alv = self.stabilize_lung_state(peep, dp, cur_air, cur_alv, num_breaths=5)
            tv, comp, _, _, eelv, vt_per_comp = self.get_trial_metrics(peep, dp, fin_air, fin_alv)

            # ── 変更⑤: ep/dpe 補正コンプライアンス ────────────────────────────
            ep_comp   = np.maximum(peep, self.aop_mean_per_comp + self.sp_per_comp)
            dpe_comp  = peep + dp - ep_comp                      # (n_comp,)
            with np.errstate(divide='ignore', invalid='ignore'):
                corr_comp = np.where(dpe_comp > 1e-9,
                                      vt_per_comp / dpe_comp * 1000,
                                      0.0)                       # (n_comp,)
            total_corr = float(np.sum(corr_comp))
            # ────────────────────────────────────────────────────────────────────

            insp_p, insp_vr, exp_p, exp_vr, quad_vr = self.generate_pv_loop(
                peep, peep + dp, fin_air, fin_alv)
            if len(insp_vr) > 0:
                ofs = eelv * 1000 - insp_vr[0]
                insp_v, exp_v, quad_v = insp_vr+ofs, exp_vr+ofs, quad_vr+ofs
            else:
                insp_v, exp_v, quad_v = insp_vr, exp_vr, quad_vr

            # 次PEEPへの状態引き継ぎ
            _, _, cur_air, cur_alv, _, _ = self.get_trial_metrics(peep, 0, fin_air, fin_alv)

            results.append({
                "peep":               peep,
                "total_compliance":   comp * 1000,          # 未補正 (mL/cmH₂O)
                "total_corr_comp":    total_corr,           # 補正合計 (mL/cmH₂O)
                "comp_per_comp":      (vt_per_comp/dp)*1000 if dp>0 else np.zeros(self.n_compartments),
                "corr_comp_per_comp": corr_comp,
                "pv_data":            (insp_p, insp_v, exp_p, exp_v, quad_v),
                "driving_pressure":   dp,
                "eelv_liters":        eelv,
                "tidal_volume_liters": tv,
            })
        return results

# ==============================================================================
# ODCL解析（未補正・補正 両対応）
# ==============================================================================
def _calc_odcl(curr, best, best_idx, i):
    diff  = best - curr
    valid = best > 1e-9
    tot   = best[valid].sum()
    if tot < 1e-12: return 0.0, 0.0
    hyper = np.where((i < best_idx) & valid, diff, 0).sum() / tot * 100
    coll  = np.where((i > best_idx) & valid, diff, 0).sum() / tot * 100
    return float(hyper), float(coll)

def analyze_costa(peep_trial_results):
    if not peep_trial_results: return []

    unc  = np.array([r["comp_per_comp"]      for r in peep_trial_results])  # (N_PEEP, N_COMP)
    corr = np.array([r["corr_comp_per_comp"] for r in peep_trial_results])

    n_comp  = unc.shape[1]
    n_g1    = n_comp // 2
    sl1, sl2 = slice(0, n_g1), slice(n_g1, n_comp)

    def _best(arr):
        return np.argmax(arr, axis=0), np.max(arr, axis=0)

    bi_unc,  bc_unc  = _best(unc)
    bi_corr, bc_corr = _best(corr)
    bi_unc1,  bc_unc1  = _best(unc[:, sl1])
    bi_corr1, bc_corr1 = _best(corr[:, sl1])
    bi_unc2,  bc_unc2  = _best(unc[:, sl2])
    bi_corr2, bc_corr2 = _best(corr[:, sl2])

    analysis = []
    for i, r in enumerate(peep_trial_results):
        hu, cu   = _calc_odcl(unc[i],        bc_unc,   bi_unc,   i)
        hc, cc   = _calc_odcl(corr[i],       bc_corr,  bi_corr,  i)
        hu1, cu1 = _calc_odcl(unc[i, sl1],   bc_unc1,  bi_unc1,  i)
        hc1, cc1 = _calc_odcl(corr[i, sl1],  bc_corr1, bi_corr1, i)
        hu2, cu2 = _calc_odcl(unc[i, sl2],   bc_unc2,  bi_unc2,  i)
        hc2, cc2 = _calc_odcl(corr[i, sl2],  bc_corr2, bi_corr2, i)
        analysis.append({
            "peep": r["peep"],
            # 未補正
            "hyper": hu, "coll": cu,
            "hyper_g1": hu1, "coll_g1": cu1,
            "hyper_g2": hu2, "coll_g2": cu2,
            "total_comp_g1": float(np.sum(unc[i, sl1])),
            "total_comp_g2": float(np.sum(unc[i, sl2])),
            # 補正
            "hyper_corr": hc, "coll_corr": cc,
            "hyper_corr_g1": hc1, "coll_corr_g1": cc1,
            "hyper_corr_g2": hc2, "coll_corr_g2": cc2,
            "total_corr_g1": float(np.sum(corr[i, sl1])),
            "total_corr_g2": float(np.sum(corr[i, sl2])),
        })
    return analysis

# ==============================================================================
# ユーティリティ
# ==============================================================================
def _find_odcl(peeps, colls, hypers):
    diff = np.array(colls) - np.array(hypers)
    idxs = np.where(np.diff(np.sign(diff)))[0]
    if len(idxs) == 0: return None
    i = idxs[0]
    x1, d1, x2, d2 = peeps[i], diff[i], peeps[i+1], diff[i+1]
    den = d2 - d1
    if abs(den) < 1e-6: return None
    p = x1 - d1 * (x2 - x1) / den
    if min(x1, x2) <= p <= max(x1, x2): return p
    return None

def calculate_single_ri_ratio(results, aop_mean):
    if not results: return "■ R/I Ratio", "データなし"
    tlo = aop_mean if aop_mean > 5 else 5
    thi = tlo + 10
    peeps = np.array([r['peep'] for r in results])
    lo_i = np.argmin(np.abs(peeps - tlo))
    hi_i = np.argmin(np.abs(peeps - thi))
    plo, phi = peeps[lo_i], peeps[hi_i]
    label = f"■ R/I Ratio ({phi:.0f}→{plo:.0f} cmH₂O)"
    if plo == phi: return label, "試行範囲が狭い"
    rlo = next((r for r in results if r['peep']==plo), None)
    rhi = next((r for r in results if r['peep']==phi), None)
    if not rlo or not rhi: return label, "指定PEEPが範囲外"
    dv   = (rhi['eelv_liters'] - rlo['eelv_liters']) * 1000
    crs  = rlo['total_compliance']
    if crs < 1e-6: return label, "Crs=0"
    dp_eff = phi - max(plo, aop_mean)
    if dp_eff < 1e-6: return label, "有効ΔP=0"
    dv_rec = dv - crs * dp_eff
    return label, f"{dv_rec/dp_eff/crs:.2f} (ΔVrec:{dv_rec:.0f} mL)"

def calc_pv_metrics(ip, iv, ep, ev):
    m = dict(hyst_area=0, hyst_ratio=0, nmd=0, v_max=0)
    if len(iv)<2 or len(ev)<2: return m
    ivn, evn = iv-iv[0], ev-ev[-1]
    m['v_max'] = float(np.max(ivn))
    if m['v_max'] < 1e-6: return m
    ai = np.trapezoid(ivn, ip); ae = np.trapezoid(np.flip(evn), np.flip(ep))
    m['hyst_area'] = float(ae - ai)
    rect = m['v_max'] * (ip.max()-ip.min())
    if rect > 1e-6: m['hyst_ratio'] = m['hyst_area']/rect*100
    fev = np.interp(ip, np.flip(ep), np.flip(evn))
    d = np.maximum(0, fev - ivn)
    if m['v_max'] > 1e-6: m['nmd'] = float(d.max()/m['v_max']*100)
    return m

# ==============================================================================
# Mojoli-style Tidal Hysteresis Analysis
# ==============================================================================
# Tab 6 (Mojoli): 過膨張と判定する経肺圧(TMP)閾値 [cmH₂O]（真の状態ベースODCL用）
MOJOLI_OD_THR = 23.0


def _mojoli_state_dist(lung, peep, dp, fin_air, fin_alv):
    """
    fin_air / fin_alv（呼気末状態）を起点に1呼吸をシミュレートし、
    肺胞ユニットを4状態に分類して各割合(%)を返す。

    States
    ------
    stable_open   : 呼気末も開放（正常換気）
    air_trap      : 吸気時開口・呼気時気道閉鎖、肺胞容量は保持（air trap）
    tidal_recruit : 吸気時開口・呼気時完全虚脱（tidal recruitment）
    always_closed : 最高気道内圧でも開口しない
    overdist      : 換気ユニットのうち吸気末TMP≥MOJOLI_OD_THR（真の過膨張）

    ※ Tab6では気道要素を無効化して呼び出すため、air_trap≈0（実質3状態）。
    """
    sp   = lung.sp                          # (n_comp, 1)
    ti   = peep + dp - sp                   # transmural at PIP
    te   = peep      - sp                   # transmural at PEEP

    # 吸気末状態
    aw2  = fin_air | (ti >= lung.aops)
    alv2 = (fin_alv | (ti >= lung.tops)) & aw2

    # 呼気末状態（Fix2適用）
    aw3       = alv2 & (te >= lung.acps)
    can       = aw3 & alv2 & (te >= lung.tcps)
    trap      = alv2 & ~aw3
    trap_open = trap & ((te >= lung.tcps) | (lung.acps > lung.tcps))

    n_total = float(lung.n_compartments * lung.n_alveoli_per_comp)
    return {
        'stable_open'  : np.sum(can)                     / n_total * 100,
        'air_trap'     : np.sum(trap_open)               / n_total * 100,
        'tidal_recruit': np.sum(alv2 & ~(can|trap_open)) / n_total * 100,
        'always_closed': np.sum(~alv2)                   / n_total * 100,
        'overdist'     : np.sum(can & (ti >= MOJOLI_OD_THR)) / n_total * 100,
    }


def _mojoli_de_trial(lung, dp, n_stab=5, peep_grid=None, pip_rec=45.0):
    """
    固定DPの減圧PEEPトライアル（高圧リクルート手技→減圧）で、各PEEPの
    肺胞3状態割合・真の過膨張%・区画コンプライアンスを返す。
    Panel D/E 用（固定PIPの概念を外し、PEEP依存の虚脱を正しく表現するため）。

    ※ 呼び出し前に lung の気道要素は無効化済み（気道は常に開存）の前提。
    """
    if peep_grid is None:
        peep_grid = np.arange(24, 1, -1)          # 24→2, 全域で交差を確認できる範囲
    sp = lung.sp
    # 初期リクルート手技（高圧 pip_rec で最大リクルート）
    tp_rec  = pip_rec - sp
    cur_air = (tp_rec >= lung.aops)
    cur_alv = cur_air & (tp_rec >= lung.tops)
    rows = []
    for peep in peep_grid:
        fa, fv = lung.stabilize_lung_state(peep, dp, cur_air, cur_alv, n_stab)
        s = _mojoli_state_dist(lung, peep, dp, fa, fv)
        _, _, _, _, _, vt_per_comp = lung.get_trial_metrics(peep, dp, fa, fv)
        comp_pc = (vt_per_comp / dp * 1000) if dp > 1e-9 else np.zeros(lung.n_compartments)
        rows.append(dict(peep=float(peep), comp_per_comp=comp_pc,
                         **{f'st_{k}': v for k, v in s.items()}))
        # 次PEEPへ状態を引き継ぎ（減圧トライアル）
        _, _, cur_air, cur_alv, _, _ = lung.get_trial_metrics(peep, 0, fa, fv)

    # 未補正(Costa)ODCL と 真の状態ベースODCL
    peeps_arr = [r['peep'] for r in rows]
    comp_arr  = np.array([r['comp_per_comp'] for r in rows])
    bi = np.argmax(comp_arr, axis=0); bc = np.max(comp_arr, axis=0)
    for i, r in enumerate(rows):
        hyp_u, coll_u = _calc_odcl(comp_arr[i], bc, bi, i)
        r['hyper_unc'] = hyp_u
        r['coll_unc']  = coll_u
        r['coll_true'] = 100.0 - r['st_stable_open']
    odcl_unc  = _find_odcl(peeps_arr, [r['coll_unc']  for r in rows],
                                      [r['hyper_unc'] for r in rows])
    odcl_true = _find_odcl(peeps_arr, [r['coll_true']  for r in rows],
                                      [r['st_overdist'] for r in rows])
    return rows, odcl_unc, odcl_true


def make_mojoli_figure(lung, fixed_pip, peep_levels, n_stab=5, pbw_kg=70.0,
                       dp_de=15.0, pip_rec=45.0):
    """
    Fixed-PIP tidal PV overlay figure (Mojoli 2026 style).

    Panel A : Each curve origin-shifted to EELV=0 (Mojoli standard).
    Panel B : All curves referenced to PEEP=0 EELV as common zero.
    Panel C : Tidal hysteresis (mL = area/ΔP) vs PEEP with Mojoli thresholds.
    Panel D : 3-state alveolar composition (airway excluded) — 固定DP減圧トライアル.
    Panel E : True-state ODCL vs uncorrected (Costa) ODCL overlay — 固定DP減圧トライアル.

    ※ Tab6限定: 気道の開放/閉鎖(AOP/ACP)概念を除外（気道は常に開存）。
    ※ A/B/C は Mojoli の固定PIP tidal PV。D/E は固定PIPの概念を外し、固定DP
      (=dp_de)・高圧リクルート後の減圧トライアルで算出（PEEP依存の虚脱を表現）。
    """
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors

    peep_levels = sorted([p for p in peep_levels if fixed_pip - p > 0], reverse=True)
    if not peep_levels:
        fig, ax = plt.subplots(); ax.text(0.5, 0.5, 'No valid PEEP levels', ha='center')
        return fig

    # ── Tab6限定: 気道要素を無効化（気道は常に開存）─────────────────────────
    # AOP/ACP を大きな負値にすることで、吸気・呼気とも気道は常に開通扱いになる。
    # → air_trap ≈ 0 となり、状態は「連続開存 / 虚脱再開放 / 完全虚脱」の3状態に帰着。
    lung.aops = np.full_like(lung.aops, -1e9)
    lung.acps = np.full_like(lung.acps, -1e9)

    # ── Reference state: stabilise at PEEP=0 with fixed PIP ─────────────────
    ref_air, ref_alv = lung.stabilize_lung_state(0, fixed_pip, num_breaths=n_stab)
    ref_eelv_mL = lung._vol_state(0, ref_air, ref_alv) * 1000

    cur_air, cur_alv = ref_air.copy(), ref_alv.copy()

    results = []
    for peep in peep_levels:
        dp = fixed_pip - peep
        fin_air, fin_alv = lung.stabilize_lung_state(peep, dp, cur_air, cur_alv, n_stab)
        eelv_mL = lung._vol_state(peep, fin_air, fin_alv) * 1000

        ip, iv, ep, ev, _ = lung.generate_pv_loop(peep, fixed_pip, fin_air, fin_alv)
        m = calc_pv_metrics(ip, iv, ep, ev)

        # ΔV from own EELV (Type A)
        ivn = iv - iv[0]
        evn = ev - ev[-1]

        # Absolute ΔV from PEEP=0 reference (Type B)
        off    = eelv_mL - ref_eelv_mL
        iv_abs = ivn + off
        ev_abs = evn + off

        # Tidal hysteresis in mL (= loop area / ΔP)
        hyst_mL = m['hyst_area'] / dp if dp > 1e-6 else 0.0

        results.append(dict(peep=peep, dp=dp, eelv_mL=eelv_mL,
                            ip=ip, ep=ep, ivn=ivn, evn=evn,
                            iv_abs=iv_abs, ev_abs=ev_abs,
                            hyst_mL=hyst_mL,
                            hyst_nmd_mL=m['nmd'] / 100 * m['v_max']))

        # Carry state forward (decremental trial)
        _, _, cur_air, cur_alv, _, _ = lung.get_trial_metrics(peep, 0, fin_air, fin_alv)

    # ── Panel D/E 用: 固定DP減圧トライアル（固定PIPの概念を外す）──────────────
    de_rows, odcl_unc, odcl_true = _mojoli_de_trial(lung, dp_de, n_stab=n_stab)

    n = len(results)
    # matplotlib>=3.9 で cm.get_cmap が削除されたため plt.get_cmap を使用（新旧両対応）
    cmap   = plt.get_cmap('plasma_r', n)
    colors = [cmap(i) for i in range(n)]

    # Mojoli thresholds (mL)
    thr_abs = 100.0           # ≥100 mL
    thr_pbw = 1.4 * pbw_kg   # ≥1.4 mL/kg PBW

    fig = plt.figure(figsize=(20, 21))
    gs  = fig.add_gridspec(3, 2, hspace=0.42, wspace=0.30,
                           left=0.07, right=0.97, top=0.93, bottom=0.05)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    ax_e = fig.add_subplot(gs[2, :])

    for i, r in enumerate(results):
        lbl = f"PEEP={r['peep']} (DP={r['dp']:.0f})"
        c   = colors[i]
        # Type A
        ax_a.plot(r['ip'], r['ivn'], color=c, lw=2.2, label=lbl)
        ax_a.plot(r['ep'], r['evn'], color=c, lw=1.4, ls='--')
        ax_a.fill_between(r['ip'],
                          r['ivn'],
                          np.interp(r['ip'], np.flip(r['ep']), np.flip(r['evn'])),
                          where=np.interp(r['ip'], np.flip(r['ep']), np.flip(r['evn'])) > r['ivn'],
                          alpha=0.10, color=c)
        # Type B
        ax_b.plot(r['ip'], r['iv_abs'], color=c, lw=2.2, label=lbl)
        ax_b.plot(r['ep'], r['ev_abs'], color=c, lw=1.4, ls='--')

    ax_a.axhline(0, color='gray', lw=0.8, ls=':')
    ax_a.set_xlabel('Airway Pressure (cmH₂O)', fontsize=12)
    ax_a.set_ylabel('ΔVolume from EELV (mL)', fontsize=12)
    ax_a.set_title(f'Type A — EELV = 0 origin (Mojoli style)\n'
                   f'Fixed PIP = {fixed_pip} cmH₂O', fontsize=12, fontweight='bold')
    ax_a.legend(fontsize=8, loc='upper left', framealpha=0.8)
    ax_a.grid(ls='--', alpha=0.45)

    ax_b.axhline(0, color='gray', lw=0.8, ls=':')
    ax_b.set_xlabel('Airway Pressure (cmH₂O)', fontsize=12)
    ax_b.set_ylabel('ΔVolume from PEEP=0 EELV (mL)', fontsize=12)
    ax_b.set_title(f'Type B — Common zero = PEEP=0 lung volume\n'
                   f'Fixed PIP = {fixed_pip} cmH₂O', fontsize=12, fontweight='bold')
    ax_b.legend(fontsize=8, loc='upper left', framealpha=0.8)
    ax_b.grid(ls='--', alpha=0.45)

    # ── Panel C: Hysteresis in mL ────────────────────────────────────────────
    peeps_r  = [r['peep']    for r in results]
    hysts_mL = [r['hyst_mL'] for r in results]
    bar_cols = [mcolors.to_hex(c) for c in colors]
    bars = ax_c.bar(peeps_r, hysts_mL, width=1.4, color=bar_cols, alpha=0.80, zorder=3)
    h_max = max(hysts_mL) if hysts_mL else 1.0
    for bar, h in zip(bars, hysts_mL):
        ax_c.text(bar.get_x() + bar.get_width() / 2, h + h_max * 0.01,
                  f'{h:.0f}', ha='center', va='bottom', fontsize=9)

    ax_c.axhline(thr_abs, color='red',        ls='--', lw=2.2,
                 label=f'≥100 mL (Mojoli 2026)')
    ax_c.axhline(thr_pbw, color='darkorange', ls='-.', lw=2.2,
                 label=f'≥1.4 mL/kg PBW  (PBW={pbw_kg:.0f} kg → {thr_pbw:.0f} mL)')
    ax_c.set_xlabel('PEEP (cmH₂O)', fontsize=12)
    ax_c.set_ylabel('Tidal Hysteresis  (mL = loop area / ΔP)', fontsize=12)
    ax_c.set_title('C.  Tidal Hysteresis (mL) vs PEEP', fontsize=12, fontweight='bold')
    ax_c.set_xticks(peeps_r)
    ax_c.legend(fontsize=10)
    ax_c.grid(axis='y', ls='--', alpha=0.5, zorder=0)

    # ── Panel D: 3-state alveolar composition (airway excluded, FIXED-DP) ─────
    #   green  = stable open (ventilating)
    #   orange = tidal recruitment (collapses at PEEP, reopens at inspiration)
    #   red    = fully collapsed (not reopened at inspiration)
    pe_x   = np.array([r['peep'] for r in de_rows], dtype=float)
    green  = np.array([r['st_stable_open']   for r in de_rows])
    orange = np.array([r['st_tidal_recruit'] for r in de_rows])
    red    = np.array([r['st_always_closed'] for r in de_rows])
    overd  = np.array([r['st_overdist']      for r in de_rows])
    xlo, xhi = pe_x.min() - 0.6, pe_x.max() + 0.6      # 両端に余白（切れ防止）
    ax_d.stackplot(pe_x, green, orange, red,
                   colors=['#27ae60', '#e67e22', '#c0392b'], alpha=0.88,
                   labels=['Stable open (ventilating)',
                           'Tidal recruitment (collapse@PEEP → reopen@insp)',
                           'Fully collapsed'])
    ax_d.plot(pe_x, overd, '--', color='#2471a3', lw=2.4,
              label=f'Overdistension% (TMP ≥ {MOJOLI_OD_THR:.0f})')
    if odcl_unc is not None:
        ax_d.axvline(odcl_unc, color='#111111', lw=2.4, label=f'Uncorrected ODCL = {odcl_unc:.1f}')
    if odcl_true is not None:
        ax_d.axvline(odcl_true, color='#145a32', lw=2.4, ls=(0, (4, 2)),
                     label=f'True-state ODCL = {odcl_true:.1f}')
    ax_d.set_xlim(xhi, xlo); ax_d.set_ylim(0, 100)
    ax_d.set_xlabel('PEEP (cmH₂O) — decremental →', fontsize=12)
    ax_d.set_ylabel('Fraction of alveolar units (%)', fontsize=12)
    ax_d.set_title(f'D.  3-state alveolar composition (airway excluded)\n'
                   f'(fixed DP = {dp_de:.0f}, RM to {pip_rec:.0f} cmH₂O)',
                   fontsize=12, fontweight='bold')
    ax_d.legend(fontsize=8.5, loc='center left', framealpha=0.9)
    ax_d.grid(ls='--', alpha=0.3)

    # ── Panel E: True-state ODCL vs Uncorrected (Costa) ODCL overlay ─────────
    coll_true = np.array([r['coll_true']  for r in de_rows])
    coll_unc  = np.array([r['coll_unc']   for r in de_rows])
    hyp_unc   = np.array([r['hyper_unc']  for r in de_rows])
    ax_e.plot(pe_x, coll_true, 's-',  color='#c0392b', lw=2.6, ms=6, label='Collapse% (true state)')
    ax_e.plot(pe_x, overd,     '^-',  color='#2471a3', lw=2.6, ms=6,
              label=f'Overdistension% (true, TMP ≥ {MOJOLI_OD_THR:.0f})')
    ax_e.plot(pe_x, coll_unc,  's--', color='#e59866', lw=2.0, ms=5, label='Collapse% (uncorrected / compliance)')
    ax_e.plot(pe_x, hyp_unc,   '^--', color='#7fb3d5', lw=2.0, ms=5, label='Hyperdistension% (uncorrected / compliance)')
    if odcl_true is not None:
        ax_e.axvline(odcl_true, color='#145a32', lw=2.8, ls=(0, (4, 2)),
                     label=f'② True-state ODCL = {odcl_true:.1f}')
    if odcl_unc is not None:
        ax_e.axvline(odcl_unc, color='purple', lw=2.8, label=f'① Uncorrected ODCL = {odcl_unc:.1f}')
    if odcl_true is not None and odcl_unc is not None:
        ax_e.axvspan(min(odcl_true, odcl_unc), max(odcl_true, odcl_unc),
                     color='#bbbbbb', alpha=0.25, label=f'distortion = {odcl_unc - odcl_true:+.1f}')
    ax_e.set_xlim(xhi, xlo); ax_e.set_ylim(-2, 102)
    ax_e.set_xlabel('PEEP (cmH₂O) — decremental →', fontsize=12)
    ax_e.set_ylabel('Collapse / Overdistension (%)', fontsize=12)
    ax_e.set_title(f'E.  True-state ODCL (collapse = overdist) vs Uncorrected (Costa) ODCL\n'
                   f'(fixed DP = {dp_de:.0f}, RM to {pip_rec:.0f} cmH₂O)',
                   fontsize=12, fontweight='bold')
    ax_e.legend(fontsize=9, loc='upper center', ncol=2, framealpha=0.9)
    ax_e.grid(ls='--', alpha=0.35)

    fig.suptitle(
        f'Mojoli-style Tidal Hysteresis Analysis  —  AIRWAY EXCLUDED (alveolar TR only)\n'
        f'A/B/C: fixed PIP={fixed_pip} cmH₂O  |  D/E: fixed DP={dp_de:.0f} cmH₂O decremental  '
        f'(stab={n_stab} breaths, PBW={pbw_kg:.0f} kg)',
        fontsize=13, fontweight='bold')
    return fig

