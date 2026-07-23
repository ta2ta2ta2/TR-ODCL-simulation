# TR biases the electrical-impedance-tomography collapse–overdistention PEEP: a mathematical modeling study

## Title page

**Title:** Tidal recruitment biases the electrical-impedance-tomography collapse–overdistention PEEP: a mathematical modeling study

**Short title:** Tidal recruitment lowers the EIT collapse–overdistention PEEP

**Authors:** Tatsutoshi Shimatani, Muneyuki Takeuchi*

**Affiliations:**
Department of Critical Care Medicine, National Cerebral and Cardiovascular Center, Suita, Osaka, Japan

**Corresponding author:** *Muneyuki Takeuchi, Department of Critical Care Medicine, National Cerebral and Cardiovascular Center, Suita, Osaka, Japan; e-mail: mutake1017@gmail.com

---

## Abstract

**Background.** Electrical impedance tomography (EIT) is increasingly used to individualize positive end-expiratory pressure (PEEP). In the Costa method, the optimal PEEP is the crossing of the estimated collapse and overdistention curves (the overdistention–collapse intercept, ODCL), derived from regional compliance change. Tidal recruitment (TR) — the cyclic reopening and re-collapse of unstable units within a breath — inflates apparent compliance and may distort this estimate, but the resulting error has not been characterized.

**Methods.** We adapted the Hickling mathematical ARDS-lung model (Salazar–Knowles pressure–volume relationship; 30 compartments × 1000 subunits). TR arose solely from alveolar opening/closing hysteresis, defined by the threshold opening (TOP) and closing (TCP) pressures. We compared the Costa ODCL with the true optimum (crossing of the end-expiratory-collapse and overdistention fractions, where a unit not open at end-expiration counts as collapsed), defining ΔPEEP = true − Costa (a positive value indicates the Costa PEEP lies below the true optimum). The extent of TR was varied by narrowing the hysteresis width TOP − TCP (TCP fixed at 2 cmH₂O). A one-at-a-time sensitivity analysis of the lung model and configuration parameters was anchored to a representative condition (TOP − TCP = 10, TCP = 2).

**Results.** The Costa ODCL lay below the true optimum wherever TR was present. At the representative condition it was 9.1 versus 12.6 cmH₂O (ΔPEEP = +3.5 cmH₂O; peak cyclic fraction 26.9%). When TR was abolished, the bias disappeared (ΔPEEP = +0.05 cmH₂O at TOP − TCP = 18), and it tended to be larger with more pronounced TR (up to +6.9 cmH₂O). The downward bias persisted across the entire parameter space explored.

**Conclusions.** TR systematically shifts the EIT collapse–overdistention PEEP below the true optimum because it inflates apparent compliance rather than reflecting true stabilization. This directional bias was robust to plausible variation in lung mechanics. The collapse–overdistention crossing should therefore be interpreted with caution when TR is present.

---

## Keywords

Acute respiratory distress syndrome; Positive end-expiratory pressure; Electrical impedance tomography; Tidal recruitment; Alveolar collapse; Overdistention; Lung protective ventilation; Mathematical model; Decremental PEEP trial

---

## Background

Setting positive end-expiratory pressure (PEEP) in the acute respiratory distress syndrome (ARDS) requires balancing the reopening of collapsed lung against the overdistention of aerated lung [1, 2]. Electrical impedance tomography (EIT) provides a bedside, radiation-free view of regional ventilation and has been proposed to individualize PEEP during a decremental PEEP trial [3, 4]. The most widely used approach, introduced by Costa and colleagues, estimates the collapsed and overdistended fractions at each PEEP step from the change in pixel-level compliance and defines the "optimal" PEEP as the pressure at which the estimated collapse and overdistention curves cross [3]. We refer to this crossing point as the overdistention–collapse intercept (ODCL). The method is now widely adopted in routine clinical practice [4, 5].

The compliance-based approach assumes that a loss of regional compliance as PEEP is lowered indicates alveolar collapse, so that the pressure minimizing the sum of collapse and overdistention is the safe compromise. This assumption is challenged by tidal recruitment (TR): the cyclic reopening at inspiration and re-collapse at expiration of unstable lung units within a single breath [6]. A unit that reopens from full collapse at every inspiration undergoes a large volume excursion, so its apparent (breath-by-breath) compliance is high — even though it is not stably open and is arguably being injured by repetitive opening. As illustrated in Fig. 1, because such a unit reopens from near-zero to its inspiratory volume at every breath, its apparent chord compliance is steeper than the true chord of a stably open unit over the same pressure interval. Recent work using tidal lung hysteresis confirms that such cyclic recruitment/derecruitment is common in ARDS and detectable at the bedside [6]. Because the Costa method infers collapse from a fall in compliance, TR — which keeps apparent compliance high as PEEP falls — could systematically bias the collapse estimate and hence the ODCL. Whether this bias exists, and its direction and size, has not been established.

Hickling's mathematical ARDS-lung model provides a well-characterized framework in which the true mechanical state of every lung unit is known exactly [7]. It reproduces the clinical observation that the best compliance during a decremental PEEP trial coincides with open-lung PEEP, whereas during an incremental trial it does not, owing to superimposed pressure and alveolar opening/closing behavior. The model is therefore suited to test a hypothesis that cannot be examined at the bedside, where the true collapse state is unobservable: that TR distorts the EIT collapse–overdistention crossing, displacing the ODCL from the true optimal PEEP.

We addressed this question in an adaptation of the Hickling model in which TR arises solely from alveolar opening/closing hysteresis. Isolating this single mechanism let us attribute any deviation of the Costa ODCL from the true optimum unambiguously to TR. We hypothesized that TR would shift the Costa ODCL below the true optimal PEEP, with a tendency for the shift to be greater when TR was more pronounced.

---

## Methods

### Lung model

We used the Hickling mathematical model of the ARDS lung [7], implemented in Python (v3.13; NumPy, SciPy). The lung comprised 30 vertically stacked compartments, each divided into 1000 subunits, spanning a gradient of superimposed pressure (maximum 14.5 cmH₂O in the reference configuration). The static pressure–volume behavior of each open unit followed the Salazar–Knowles exponential relationship, V(P) = V₀·(1 − e^(−P·ln2/h)), with an elastance shape constant h (reference mean 4.9 cmH₂O) and total lung capacity scaled to 2.5 L [8].

The only source of intratidal instability was alveolar opening/closing hysteresis. Each unit was assigned a threshold opening pressure (TOP) and a threshold closing pressure (TCP), with TOP ≥ TCP. Within a breath, a unit's local end-expiratory transpulmonary pressure was PEEP − superimposed pressure and its end-inspiratory transpulmonary pressure was PEEP + driving pressure (DP) − superimposed pressure. A unit was classified as stable-open if it stayed open throughout the breath, persistently collapsed if it stayed closed throughout, and tidally recruiting if it reopened at inspiration but re-collapsed at expiration.

### Ventilation protocol

A decremental PEEP trial was simulated after a recruitment maneuver to a peak inspiratory pressure of 45 cmH₂O, using the constant-DP design of a Hickling-type decremental trial. DP was fixed at 14 cmH₂O in the reference configuration (the tidal pressure swing on the model P–V curve corresponds to a representative tidal volume of ~400–500 mL at high PEEP, matching the range reported by Hickling). PEEP was lowered stepwise over the range needed to locate both crossing points. At each step, five stabilizing breaths were applied before metrics were recorded. Each trial used one random seed of the unit-level parameter distributions; 30 trials were run throughout.

### Definitions of collapse, overdistention and the two PEEP estimates

The true optimal PEEP was the PEEP at which the fraction of end-expiratory–collapsed units (true collapse — units that are not open at end-expiration) equalled the fraction of overdistended units. This applies the same crossing rule as the Costa method, but to the ground-truth fractions known exactly in the model rather than to their compliance-based estimates; the difference between the two therefore isolates the error of the estimation step alone. A ventilating unit was classified as overdistended when its end-inspiratory transpulmonary pressure reached or exceeded 23 cmH₂O, consistent with the lung stress (transpulmonary pressure) at which strain approaches the level associated with ventilator-induced lung injury [9]; this threshold was varied from 20 to 26 cmH₂O in the sensitivity analysis.

The Costa ODCL was computed by reproducing the compliance-based EIT algorithm on the same lung: for each unit, breath-by-breath compliance was tracked across the decremental trial; the collapse fraction at each PEEP was derived from the compliance loss relative to each unit's own maximum, and the overdistention fraction from the compliance loss above the compliance peak; the ODCL was the PEEP at which the resulting collapse and overdistention curves crossed [3]. Crucially, this algorithm sees only apparent compliance and cannot distinguish a stably open unit from a tidally recruiting one.

The deviation was defined as ΔPEEP = true optimal PEEP − Costa ODCL, so that a positive value indicates that the Costa method selects a PEEP below the true optimum.

### Varying the extent of TR

We varied the alveolar hysteresis width TOP − TCP by sweeping TOP while holding TCP at 2 cmH₂O. A narrow TOP − TCP produces strong TR (many units reopen and re-collapse within a breath), whereas TOP − TCP ≥ DP abolishes it, because a closed unit cannot be reopened by the available inspiratory pressure. A width of zero was excluded, as it corresponds to no TR by definition.

### Sensitivity analysis

To test robustness, we performed a one-at-a-time sensitivity analysis anchored to a representative TR condition (TOP − TCP = 10; reference ΔPEEP = +3.54 cmH₂O). Each of five parameters was varied while the others were held at their reference values: DP (DP, 5–15 cmH₂O), maximum superimposed pressure as an index of vertical heterogeneity (max_sp, 10–18 cmH₂O), the elastance shape constant (h, 3.9–5.9 cmH₂O), the closing pressure of the recruiting units (TCP, 0–6 cmH₂O, with TOP co-varied to preserve TOP − TCP), and the overdistention threshold (20–26 cmH₂O). Results were summarized as a tornado plot of ΔPEEP.

### Reporting and reproducibility

Values are reported as mean ± standard deviation across the 30 trials. No inferential statistics were applied: in a deterministic model the between-trial variability reflects only the random draw of unit parameters, not sampling of a population, so the standard deviations are reported to document the stability of each estimate. The complete simulation and figure-generation code, together with the exact numerical outputs, are provided (see Availability of data and materials). A large language model (Claude, Anthropic) was used for language editing and code drafting; all output was verified by the authors.

---

## Results

### TR displaces the collapse–overdistention crossing to a lower PEEP

At the representative TR condition (TOP − TCP = 10), the Costa ODCL was 9.1 ± 0.01 cmH₂O and the true optimal PEEP was 12.6 ± 0.01 cmH₂O, a deviation of +3.5 cmH₂O (Figs. 2, 3). Here the peak fraction of tidally recruiting units during the trial was 26.9%. When TR was abolished (TOP − TCP = 18), the Costa and true curves were superimposed and the estimates coincided (Costa 12.6, true 12.6 cmH₂O; ΔPEEP = +0.05 cmH₂O), showing that without TR the compliance-based algorithm recovers the true optimum (Fig. 3, top row).

This inflated apparent compliance persists to low PEEP, delaying the compliance-loss signal on which the Costa collapse estimate depends beyond the pressure at which the units actually fail to stay open. The Costa collapse curve is therefore shifted leftward relative to the true curve, and the crossing that defines the ODCL is pulled down.

### The downward deviation is present with TR and tends to be larger with greater TR

Across the hysteresis-width sweep, ΔPEEP was negative wherever TR was present and returned to essentially zero only when TR was abolished (−0.05 cmH₂O at TOP − TCP = 18, control); it tended to be larger with more pronounced TR, reaching +6.9 cmH₂O at the narrowest hysteresis width (TOP − TCP = 2) (Fig. 2). The corresponding peak cyclic-unit fraction rose from 0% to 79.3%. The Costa estimate fell as TOP decreased, whereas the overdistention limb was unchanged. The true optimum remained essentially constant (≈12.6 cmH₂O) across the sweep — because counting tidally recruiting units as end-expiratory collapse anchors the collapse limb — whereas the Costa estimate fell from 12.6 to 5.8 cmH₂O, so the gap between them widened as TR increased.

### The downward deviation is robust across the model-parameter space

The one-at-a-time sensitivity analysis, anchored to TOP − TCP = 10 (reference ΔPEEP = +3.54 cmH₂O), showed that ΔPEEP remained positive — the Costa PEEP stayed below the true optimum — for every parameter value tested (Fig. 4). Its magnitude was most sensitive to DP and the overdistention threshold:

- DP: ΔPEEP was non-monotonic in DP, ranging from +2.95 cmH₂O (DP = 9) to +4.81 cmH₂O (DP = 5) and remaining downward across the whole 5–15 cmH₂O range.
- Overdistention threshold: ΔPEEP ranged from +2.04 cmH₂O (at 20 cmH₂O) to +5.04 cmH₂O (at 26 cmH₂O).
- Vertical heterogeneity (max_sp): ΔPEEP ranged from +3.37 cmH₂O (max_sp = 18) to +4.19 cmH₂O (max_sp = 10).
- Elastance shape constant (h): ΔPEEP ranged from +3.28 (h = 5.9) to +3.85 cmH₂O (h = 3.9).
- Closing pressure (TCP): with hysteresis width preserved, ΔPEEP ranged from +2.46 (TCP = 6) to +3.67 cmH₂O (TCP = 0).

In every case the Costa method identified a PEEP below the true optimum; no combination of parameters within the explored ranges reversed the direction of the error.

---

## Discussion

In the Hickling model, where the true mechanical state of every lung unit is known, TR systematically displaced the EIT collapse–overdistention PEEP (the Costa ODCL) below the true optimal PEEP. The bias was present whenever TR occurred, tended to be larger when TR was more pronounced, and persisted across the full range of DP, lung heterogeneity, elastance and overdistention threshold examined.

The mechanism is straightforward. The Costa method infers collapse from a fall in regional compliance as PEEP is lowered [3]. A tidally recruiting unit reopens from collapse at every inspiration, so it keeps a high apparent compliance even at low PEEP, when it is no longer stably open. This masks the compliance-loss signal and delays the detection of collapse, pulling the crossing downward. When TR is abolished (hysteresis width ≥ DP), the Costa estimate recovers the true optimum — an internal control that favours this interpretation over an implementation artifact.

DP alters the deviation through two channels. First, it scales the apparent-compliance error that drives the collapse estimate: DP sets the pressure window over which a tidally recruiting unit swings, so it governs how much that unit's apparent compliance is inflated relative to a stably open one, and hence how far the collapse limb is displaced. Second, it moves the overdistention estimate: because a unit is judged overdistended from its end-inspiratory transpulmonary pressure (PEEP + DP − superimposed pressure), changing DP shifts the overdistention limb along the PEEP axis and therefore the pressure at which the crossing is read. Under the end-expiratory-collapse definition the true optimum is essentially independent of DP — counting tidally recruiting units as collapse anchors the collapse limb — so ΔPEEP tracks the Costa error directly and remained downward at every DP examined (Additional file 1: Figure S1). Its magnitude was non-monotonic in DP, reflecting the balance of these two channels: it was largest at the lowest DP (ΔPEEP = +4.8 cmH₂O at DP = 5 cmH₂O) and fell to a minimum near DP = 9 cmH₂O (+3.0 cmH₂O). The residual deviation at DP = 5, where TR is absent, reflects the overdistention-limb channel alone — a small method-intrinsic offset — rather than TR.

TR is common in ARDS and is not directly visible on the compliance-based EIT display, and cyclic recruitment/derecruitment can be demonstrated with tidal lung hysteresis and other techniques [6]. Our central finding is directional: in a lung with substantial TR the compliance-based crossing is displaced toward a lower PEEP than the true collapse–overdistention balance. We interpret this as a caution about how the crossing is read when TR is present, not as a basis for a specific bedside adjustment; the magnitude of the shift is model-dependent and is not intended as a correction factor.

Our study has several limitations. First, it is a modeling study; the absolute magnitude of ΔPEEP depends on model parameters and should not be read as a bedside correction factor. The value of the model is that it isolates a mechanism and establishes the direction and robustness of the bias, which cannot be determined directly in patients, where the ground-truth collapse state is not available for comparison. Second, the model does not represent perfusion, gas exchange, chest-wall mechanics or the temporal dynamics of recruitment beyond the stabilizing breaths applied at each step, so it addresses the geometry of the compliance-based estimate rather than the full physiology of PEEP selection.

The study's strengths are the use of a validated modeling framework with full knowledge of the ground truth, the isolation of a single mechanism, a tendency for the bias to be larger when TR was more pronounced, and the robustness of the effect's direction across a wide sensitivity analysis.

---

## Conclusions

In the Hickling model, TR systematically biases the EIT collapse–overdistention PEEP (the Costa ODCL) below the true optimal PEEP, with a tendency for the bias to be larger when TR is more pronounced. It arises because TR inflates apparent compliance and thereby delays the compliance-based detection of collapse. Its direction is robust to plausible variation in DP, lung heterogeneity, elastance and overdistention threshold. These results indicate that the collapse–overdistention crossing should be interpreted with caution when TR is present. Whether and how this directional bias should modify bedside PEEP selection cannot be determined from a modeling study and will require clinical investigation.

---

## List of abbreviations

ARDS, acute respiratory distress syndrome; DP, driving pressure; EIT, electrical impedance tomography; ODCL, overdistention–collapse intercept (the collapse–overdistention crossing PEEP of the Costa method); PEEP, positive end-expiratory pressure; TCP, threshold closing pressure; TOP, threshold opening pressure; TR, tidal recruitment.

---

## Declarations

### Ethics approval and consent to participate

Not applicable. This study is based entirely on mathematical simulation and did not involve human participants, human data, human tissue or animals.

### Consent for publication

Not applicable.

### Availability of data and materials

The datasets and code supporting the conclusions of this article are available in the GitHub repository (https://github.com/ta2ta2ta2/TR-ODCL-simulation). An archived version with a persistent identifier is available at Zenodo (DOI: 10.5281/zenodo.21298097).

### Additional files

Additional file 1: Figure S1 — per–DP collapse–overdistension crossings.

### Competing interests

The authors declare that they have no competing interests.

### Funding

This work was supported by JSPS KAKENHI Grant Numbers 24K12210, 26K19783 and 22K16641.

### Authors' contributions

T.S. designed the model and performed the simulations. T.S. and M.T. analyzed the data and contributed to writing the manuscript. All authors read and approved the final manuscript.

### Acknowledgements

The authors acknowledge the use of a large language model (Claude, Anthropic) for language editing and code drafting during the preparation of this manuscript. The authors take full responsibility for the content of the publication.

---

## References

1. Amato MBP, Meade MO, Slutsky AS, Brochard L, Costa ELV, Schoenfeld DA, et al. Driving pressure and survival in the acute respiratory distress syndrome. N Engl J Med. 2015;372(8):747–755.
2. Gattinoni L, Caironi P, Cressoni M, Chiumello D, Ranieri VM, Quintel M, et al. Lung recruitment in patients with the acute respiratory distress syndrome. N Engl J Med. 2006;354(17):1775–1786.
3. Costa ELV, Borges JB, Melo A, Suarez-Sipmann F, Toufen C Jr, Bohm SH, Amato MBP. Bedside estimation of recruitable alveolar collapse and hyperdistension by electrical impedance tomography. Intensive Care Med. 2009;35(6):1132–1137. doi:10.1007/s00134-009-1447-y.
4. Jonkman AH, Alcala GC, Pavlovsky B, Roca O, Spadaro S, Scaramuzzo G, et al.; Pleural Pressure Working Group. Lung recruitment assessed by electrical impedance tomography (RECRUIT): a multicenter study of COVID-19 acute respiratory distress syndrome. Am J Respir Crit Care Med. 2023;208(1):25–38.
5. Sousa MLA, Katira BH, Bouch S, Hsing V, Engelberts D, Amato MBP, Post M, Brochard LJ. Limiting overdistention or collapse when mechanically ventilating injured lungs: a randomized study in a porcine model. Am J Respir Crit Care Med. 2024. doi:10.1164/rccm.202310-1895OC.
6. Mojoli F, Adrião D, Pozzi M, Giacosa M, Couto R, Orlando A, et al. Validation of thresholds for tidal lung hysteresis to detect tidal recruitment/derecruitment in patients with acute respiratory distress syndrome. Am J Respir Crit Care Med. 2026;212(4):827–829. doi:10.1093/ajrccm/aamaf120.
7. Hickling KG. Best compliance during a decremental, but not incremental, positive end-expiratory pressure trial is related to open-lung positive end-expiratory pressure: a mathematical model of acute respiratory distress syndrome lungs. Am J Respir Crit Care Med. 2001;163(1):69–78.
8. Salazar E, Knowles JH. An analysis of pressure-volume characteristics of the lungs. J Appl Physiol. 1964;19(1):97–104.
9. Chiumello D, Carlesso E, Cadringher P, Caironi P, Valenza F, Polli F, Tallarini F, Cozzi P, Cressoni M, Colombo A, Marini JJ, Gattinoni L. Lung stress and strain during mechanical ventilation for acute respiratory distress syndrome. Am J Respir Crit Care Med. 2008;178(4):346–355. doi:10.1164/rccm.200710-1589OC.
10. Sousa MLA, Katira BH, Bouch S, et al. Individualized PEEP can improve both pulmonary hemodynamics and lung mechanics. Crit Care. 2025;29:107. doi:10.1186/s13054-025-05325-7.
11. Beitler JR, Sarge T, Banner-Goodspeed VM, Gong MN, Cook D, Novack V, et al. Effect of titrating positive end-expiratory pressure (PEEP) with an esophageal pressure–guided strategy vs an empirical high PEEP-Fio₂ strategy on death and days free from mechanical ventilation among patients with acute respiratory distress syndrome: a randomized clinical trial. JAMA. 2019;321(9):846–857.

---

## Figure legends

**Figure 1. Mechanism by which TR inflates apparent compliance.**
Salazar–Knowles pressure–volume relationship for a representative lung unit. A stably open unit oscillates over a small volume chord between its end-expiratory and end-inspiratory pressures (true chord). A tidally recruiting unit instead reopens from near-zero volume at every inspiration, so its apparent breath-by-breath chord is much steeper. This inflated apparent compliance persists to low PEEP, delaying the compliance-loss signal on which the Costa collapse estimate depends. TCP, threshold closing pressure; TOP, threshold opening pressure.

**Figure 2. The downward Costa deviation is present across the range of TR examined and tends to be larger with greater TR.**
Principal result of the hysteresis-width sweep. (a) The Costa collapse–overdistention PEEP (ODCL) lies below the true optimum across the entire sweep, and the gap between them widens as the hysteresis width TOP − TCP narrows. The Costa estimate falls as TOP decreases while the true optimum stays essentially constant (counting tidally recruiting units as end-expiratory collapse anchors the collapse limb); because the overdistention limb is independent of TOP, the Costa crossing moves only as its collapse-estimate limb shifts. (b) ΔPEEP (= true − Costa), plotted against the realized extent of TR (peak cyclic-unit fraction), varies from ~+0.05 cmH₂O when TR is abolished (TOP − TCP = 18) to ~+6.9 cmH₂O at the strongest TR (TOP − TCP = 2); the representative condition (TOP − TCP = 10) yields ΔPEEP ~+3.5 cmH₂O.

**Figure 3. TR adds a cyclic band and displaces the ODCL crossing to a lower PEEP.**
Representative decremental PEEP trial without TR (top row, TOP − TCP = 18) and with TR (bottom row, TOP − TCP = 10). Left column, unit-state composition (100% stacked areas: stable-open, tidally recruiting, persistently collapsed) with the overdistention fraction overlaid. Right column, the Costa and true collapse and overdistention curves and their crossing points. Without TR the two ODCL estimates coincide (~12.6 cmH₂O); with TR the Costa ODCL (9.1 cmH₂O) falls below the true optimum (12.6 cmH₂O).

**Figure 4. The downward deviation is robust across the model-parameter space.**
One-at-a-time sensitivity analysis anchored to the representative TR condition (TOP − TCP = 10, DP = 14 cmH₂O; reference ΔPEEP = +3.54 cmH₂O, red circle in each panel). Panels (a)–(e): DP, maximum superimposed pressure (vertical heterogeneity), elastance shape constant, closing pressure (with hysteresis width preserved), and overdistention threshold. Panel (f): tornado summary. ΔPEEP remains positive — the Costa PEEP stays below the true optimum — for every parameter value tested; its magnitude is most sensitive to DP and the overdistention threshold. DP, DP; max_sp, maximum superimposed pressure; TCP, threshold closing pressure; TMP, end-inspiratory transpulmonary pressure; TOP, threshold opening pressure.

---

## Supplementary figure legends

**Additional file 1: Figure S1. Per–DP collapse–overdistension crossings under the end-expiratory-collapse definition.**
Collapse and overdistention curves at each DP (DP = 5–15 cmH₂O) for the representative TR condition (TOP − TCP = 10; n = 30 seeds). Because tidally recruiting units are counted as end-expiratory (true) collapse, the collapse limb is anchored and the true optimum is essentially independent of DP (≈12.6 cmH₂O at DP = 14), whereas the Costa estimate falls as DP rises; the Costa ODCL therefore lies below the true optimum at every DP. The summary panel shows that ΔPEEP (= true − Costa) is downward throughout and non-monotonic in DP — largest at DP = 5 cmH₂O (+4.8 cmH₂O, where TR is absent and the offset reflects the overdistention-limb definition), with a minimum near DP = 9 cmH₂O (+3.0 cmH₂O) — while the peak tidally-recruiting fraction rises with DP (from ~0% at DP = 5 to ~33% at DP = 15).

