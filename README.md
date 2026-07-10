# Tidal recruitment biases the EIT collapse–overdistension PEEP below the true optimum

Simulation code and generated data for the mathematical modelling study:

> **Tidal recruitment biases the electrical-impedance-tomography collapse–overdistension PEEP below the true optimum: a mathematical modelling study.**
> Tatsutoshi Shimatani, Muneyuki Takeuchi. Department of Critical Care Medicine, National Cerebral and Cardiovascular Center, Suita, Osaka, Japan.

This repository reproduces every numerical result and figure in the manuscript. The model is an **airway-free adaptation of the Hickling mathematical ARDS-lung model**: tidal recruitment arises purely from alveolar opening/closing hysteresis (threshold opening pressure TOP, threshold closing pressure TCP), with no airway-closure component. We compare the PEEP selected by the EIT collapse–overdistension method of Costa et al. against the true optimum, and show that the Costa estimate lies systematically **below** the true optimum whenever tidal recruitment is present.

## Repository layout

```
scripts/
  lung_model_core.py            Core lung model (Salazar–Knowles P–V, TOP/TCP hysteresis,
                                unit-state logic, Costa and true ODCL computation)
  metrics.py                    Lung construction, decremental PEEP trial, ODCL metrics
  run_sweeps_tr.py              Data generator: tidal-recruitment sweeps
  sensitivity_tr.py             Data generator: one-at-a-time sensitivity analysis
  make_figures_en.py            Manuscript Figures 1–3 (English)
  make_sensitivity_en.py        Manuscript Figure 4 (English)
  make_figures_tr.py            Presentation figures (Japanese)
  make_sensitivity_tr.py        Sensitivity figures (Japanese)
  build_pdf_tr.py               Japanese presentation PDF
  build_figures_en_pdf.py       English figure-review PDF
  build_sensitivity_interp_pdf.py  Sensitivity-interpretation PDF
  build_manuscript_docx.py      Markdown → .docx manuscript converter
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
python scripts/make_figures_en.py       # Figures 1–3
python scripts/make_sensitivity_en.py   # Figure 4
```

**3. (Optional) Regenerate the Japanese presentation and interpretation PDFs**:

```bash
python scripts/build_pdf_tr.py
python scripts/build_sensitivity_interp_pdf.py
python scripts/build_figures_en_pdf.py
```

## Model summary

- **Geometry**: 30 compartments × 1000 subunits; a superimposed-pressure (SP) gradient sets each subunit's local transmural pressure `Paw − SP`.
- **Unit states**: open, tidally recruiting (reopens/re-collapses within a breath), or persistently collapsed, determined by TOP/TCP relative to inspiratory/expiratory transmural pressure.
- **Tidal-recruitment burden** is varied two ways: (i) by narrowing the hysteresis width `TOP − TCP` (TCP fixed at 2 cmH₂O), and (ii) by increasing the proportion of units assigned a tidally-recruiting hysteresis (TOP = 8, TCP = 2 cmH₂O), the remainder having their opening threshold raised by 12 cmH₂O so they cannot tidally reopen.
- **Two PEEP estimates**: the Costa collapse–overdistension limit (ODCL), inferred from regional compliance change, versus the true optimum (crossing of persistent-collapse and overdistension fractions). Deviation `dev = Costa − true`; negative = Costa selects a lower PEEP.
- Driving pressure DP = 14 cmH₂O; recruitment to 45 cmH₂O; overdistension threshold TMP ≥ 23 cmH₂O.

## Citing

If you use this code, please cite the manuscript above. An archived release of this
repository is available on Zenodo (DOI to be added on release).

## License

MIT — see [LICENSE](LICENSE).
