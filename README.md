# Tidal recruitment biases the EIT collapse–overdistention PEEP away from the true optimum

Simulation code, generated data, and the manuscript for the mathematical modeling study:

> **Tidal recruitment biases the electrical-impedance-tomography collapse–overdistention PEEP: a mathematical modeling study.**
> Tatsutoshi Shimatani, Muneyuki Takeuchi. Department of Critical Care Medicine, National Cerebral and Cardiovascular Center, Suita, Osaka, Japan.

This repository reproduces every numerical result and figure in the manuscript. The model is an **airway-free adaptation of the Hickling mathematical ARDS-lung model**: tidal recruitment (TR) arises purely from alveolar opening/closing hysteresis (threshold opening pressure TOP, threshold closing pressure TCP), with no airway-closure component. We compare the PEEP selected by the EIT collapse–overdistention method of Costa et al. against the true optimum. When TR is present, the Costa estimate lies systematically **below** the true optimum: the collapse–overdistention crossing (overdistention–collapse limit, ODCL) is displaced to a lower PEEP than the pressure that truly minimizes the sum of end-expiratory collapse and overdistention.

## Key result

The deviation is reported as **ΔPEEP = true − Costa** (a positive value means the Costa method selects a PEEP *below* the true optimum). At the reference configuration (driving pressure DP = 14 cmH₂O, n = 30 seeds):

| Hysteresis gap (TOP − TCP) | Peak cyclic burden | Costa ODCL | True optimum | ΔPEEP |
|---|---|---|---|---|
| 2 (strongest TR) | 79.3 % | 5.77 | 12.63 | **+6.86** |
| 10 (representative) | 26.9 % | 9.09 | 12.63 | **+3.54** |
| 18 (TR abolished) | 0.0 % | 12.58 | 12.63 | **+0.05** |

Counting tidally recruiting units as end-expiratory collapse anchors the true collapse limb, so the true optimum stays near 12.6 cmH₂O across the sweep while the Costa estimate falls with increasing TR. The downward deviation is positive across the entire one-at-a-time sensitivity analysis (see `out/sensitivity_tr.csv`).

## Repository layout

```
scripts/
  lung_model_core.py            Core lung model (Salazar–Knowles P–V, TOP/TCP hysteresis,
                                unit-state logic, Costa and true ODCL computation)
  metrics.py                    Lung construction, decremental PEEP trial, ODCL metrics
                                (end-expiratory collapse via collapse_mode="exp")
  run_sweeps_tr.py              Data generator: tidal-recruitment sweeps
  sensitivity_tr.py             Data generator: one-at-a-time sensitivity analysis
  make_figures_en.py            Manuscript Figures 1–3
  make_sensitivity_en.py        Manuscript Figure 4
  make_dp_crossings_en.py       Additional file 1 (Figure S1): per-DP collapse–overdistention crossings
  build_manuscript_docx.py      Markdown → .docx manuscript converter
manuscript/
  TR_ODCL_manuscript.md         Manuscript source (Markdown)
  TR_ODCL_manuscript.docx       Manuscript (Word, built from the Markdown)
out/
  sweeps_tr.json, deviation_tr.csv          Pre-computed TR-sweep results
  sensitivity_tr.json, sensitivity_tr.csv   Pre-computed sensitivity results
requirements.txt
LICENSE
```

Figures and PDFs are regenerable and are git-ignored; the exact numerical outputs
(`out/*.json`, `out/*.csv`) are committed so that results can be inspected without
re-running the simulations.

## Requirements

- Python 3.13
- Packages pinned in `requirements.txt` (numpy, scipy, matplotlib, reportlab, pillow, python-docx)

```bash
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
```

## Reproducing the results

All scripts resolve their output directory to `../out` relative to `scripts/`, so run
them from anywhere after cloning.

**1. Regenerate the numerical results** (deterministic; fixed random seeds, n = 30):

```bash
python scripts/run_sweeps_tr.py     # -> out/sweeps_tr.json, out/deviation_tr.csv
python scripts/sensitivity_tr.py    # -> out/sensitivity_tr.json, out/sensitivity_tr.csv
```

These overwrite the committed files with byte-identical content.

**2. Regenerate the manuscript figures**:

```bash
cd scripts
PYTHONPATH=. python make_figures_en.py        # Figures 1–3
PYTHONPATH=. python make_sensitivity_en.py    # Figure 4
PYTHONPATH=. python make_dp_crossings_en.py   # Additional file 1 (Figure S1)
```

**3. (Optional) Rebuild the manuscript .docx from the Markdown source**:

```bash
python scripts/build_manuscript_docx.py       # -> manuscript/TR_ODCL_manuscript.docx
```

## Model summary

- **Geometry**: 30 compartments × 1000 subunits; a superimposed-pressure (SP) gradient sets each subunit's local transmural pressure `Paw − SP`.
- **Unit states**: stable-open, tidally recruiting (reopens at inspiration and re-collapses at expiration within a breath), or persistently collapsed, determined by TOP/TCP relative to the end-inspiratory and end-expiratory transmural pressures.
- **True optimum (end-expiratory collapse)**: a unit not open at end-expiration counts as collapsed, so end-expiratory collapse comprises persistently collapsed *and* tidally recruiting units (`collapse_mode="exp"`). The true optimum is the PEEP at which the end-expiratory-collapse and overdistention fractions cross.
- **Costa ODCL**: the collapse–overdistention limit inferred from regional compliance change, following Costa et al.
- **Deviation**: `dev = true − Costa`; a positive value means the Costa method selects a PEEP below the true optimum.
- **Tidal-recruitment burden** is varied two ways: (i) by narrowing the hysteresis width `TOP − TCP` (TCP fixed at 2 cmH₂O), and (ii) by increasing the proportion of units assigned a tidally-recruiting hysteresis (TOP = 8, TCP = 2 cmH₂O), the remainder having their opening threshold raised by 12 cmH₂O so they cannot tidally reopen.
- Driving pressure DP = 14 cmH₂O; recruitment to 45 cmH₂O; overdistention threshold: end-inspiratory transpulmonary pressure ≥ 23 cmH₂O.

## Citing

If you use this code, please cite the manuscript above. An archived release of this
repository is available on Zenodo (DOI to be added on release).

## License

MIT — see [LICENSE](LICENSE).
