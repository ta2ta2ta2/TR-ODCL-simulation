#!/usr/bin/env python3
"""Build a review PDF: each English figure with its English legend (BMC style) below.
BMC rule reminder: in the real manuscript the title (<=15 words) + legend (<=300 words)
go in the manuscript TEXT, not in the graphic; here we place them below each figure so
the user can review figure + legend together. On-graphic color keys stay embedded.
Run from tr_only/ with env=lungsim:  python scripts/build_figures_en_pdf.py
Output: out/TR_ODCL_figures_EN_review.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                PageBreak, HRFlowable, KeepTogether)
from PIL import Image as PILImage

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")

# Arial for body text (matches figure font)
ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIALB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
pdfmetrics.registerFont(TTFont("Arial", ARIAL))
pdfmetrics.registerFont(TTFont("Arial-Bold", ARIALB if os.path.exists(ARIALB) else ARIAL))

PAGE = A4
LM = RM = 20 * mm
TM = BM = 18 * mm
CW = PAGE[0] - LM - RM

st_h = ParagraphStyle("h", fontName="Arial-Bold", fontSize=13, leading=17,
                      textColor="#0b3d66", spaceBefore=2, spaceAfter=8)
st_ttl = ParagraphStyle("ttl", fontName="Arial-Bold", fontSize=10, leading=14,
                        textColor="#111111", spaceBefore=6, spaceAfter=3)
st_leg = ParagraphStyle("leg", fontName="Arial", fontSize=9, leading=13.2,
                        textColor="#222222", alignment=TA_LEFT, spaceAfter=2)
st_note = ParagraphStyle("note", fontName="Arial", fontSize=8, leading=11,
                         textColor="#666666", spaceBefore=8)

def img(fn, max_w_mm=170, max_h_mm=150):
    """Place a figure scaled to fit within max_w/max_h (mm), preserving aspect."""
    path = os.path.join(OUT, fn)
    iw, ih = PILImage.open(path).size
    max_w = min(max_w_mm * mm, CW)
    max_h = max_h_mm * mm
    scale = min(max_w / iw, max_h / ih)
    return Image(path, width=iw * scale, height=ih * scale)

GE = "\u2265"; MI = "\u2212"; AP = "\u2248"; EN = "\u2013"; EM = "\u2014"

# ----- English legends (BMC: title <=15 words; legend <=300 words) -----
FIGS = [
 ('Fig1_concept_en.png',
  'Figure 1. A tidally recruiting alveolar unit overestimates its own compliance.',
  "Single-unit schematic on the Salazar pressure" + EN + "volume (P" + EN + "V) relationship (black), "
  "plotted with the airway mechanism disabled so that the only source of hysteresis is alveolar "
  "(threshold opening pressure, TOP, exceeding threshold closing pressure, TCP). A unit that "
  "collapses completely at end-expiration and reopens at each inspiration traverses the curve "
  "from zero volume to the volume at TOP on every breath; the chord it spans (purple) is "
  "therefore steeper than the chord of a unit that remains open and merely oscillates along the "
  "local curve between TCP and TOP (green dashed). Because tidal compliance is estimated as the "
  "tidal-volume-to-driving-pressure ratio, the tidally recruiting unit reports a higher "
  "apparent compliance than an otherwise identical open unit, despite unchanged underlying "
  "tissue mechanics. This single-unit distortion is the mechanistic basis of the whole-lung "
  "deviation characterised in the subsequent figures. TOP and TCP are indicated by the vertical "
  "dashed lines; the shaded region denotes the compliance overestimation."),
 ('Fig2_core_en.png',
  'Figure 2. The downward Costa deviation increases with tidal-recruitment burden.',
  "Principal result. All lung mechanics were held constant (driving pressure DP = 14 cmH2O, "
  "overdistension threshold end-inspiratory transpulmonary pressure TMP " + GE + " 23 cmH2O, n = 30 "
  "simulated patients), and only the alveolar hysteresis width TOP " + MI + " TCP was varied "
  "(TCP fixed at 2 cmH2O). A narrow TOP " + MI + " TCP causes units to "
  "collapse at expiration and reopen at inspiration (strong tidal recruitment, TR), whereas "
  "TOP " + MI + " TCP " + GE + " DP keeps units closed once collapsed, abolishing TR. "
  "(a) The Costa-method open-circuit collapse limit (ODCL), derived from uncorrected per-unit "
  "compliance, lies below the true ODCL across the entire sweep, and the shaded interval "
  "between the two widens as TOP " + MI + " TCP narrows. Both ODCL estimates themselves fall "
  "as TOP decreases: the overdistension limb depends only on end-inspiratory pressure "
  "(TMP = PEEP + DP), not on TOP, so the crossing that defines the ODCL moves only when the "
  "collapse limb moves. A lower TOP keeps units recruited to a lower PEEP, shifting the "
  "collapse fraction " + EM + " and thus the collapse" + EN + "overdistension crossing " + EM + " "
  "toward a lower PEEP; this genuinely lowers the true ODCL. The Costa ODCL follows the same "
  "shift but falls further, because the recruiting units also inflate apparent compliance and "
  "delay Costa collapse detection (Figure 1) " + EM + " the source of the negative deviation. "
  "(b) The corresponding deviation "
  "(dev = Costa " + MI + " true), plotted against the realised TR burden (peak cyclic-unit "
  "fraction), varies monotonically" + EM + "from dev " + AP + " " + MI + "0.05 cmH2O at TOP " + MI + " TCP = 18 "
  "(TR abolished; control) to dev " + AP + " " + MI + "2.2 cmH2O at TOP " + MI + " TCP = 2 (strongest TR); "
  "the representative condition used throughout (TOP " + MI + " TCP = 10) yields dev " + AP + " "
  + MI + "1.5 cmH2O. The deviation is negative at every point: whenever TR is present the "
  "Costa method identifies a PEEP below the true optimum, and the magnitude scales with TR burden."),
 ('Fig3_states_odcl_en.png',
  'Figure 3. Tidal recruitment adds a cyclic band and displaces the ODCL crossing to a lower PEEP.',
  "Representative decremental PEEP trial, without TR (top row) and with TR (bottom row). "
  "Left column: unit-state composition (100% stacked areas) " + EM + " green, stable-open units; "
  "purple, cyclic (tidally recruiting) units that collapse at expiration and reopen at "
  "inspiration; brown, persistently collapsed units; the red line is the overdistension "
  "fraction (units with end-inspiratory TMP " + GE + " 23 cmH2O). Right column: the Costa-method "
  "collapse and overdistension fractions (solid) with the true collapse and true "
  "overdistension fractions (dashed); the ODCL is the PEEP at which the collapse and "
  "overdistension curves intersect (vertical dotted lines). "
  "(a, b) No TR (TOP " + MI + " TCP = 18): no cyclic band is present and, once closed at low PEEP, "
  "units are persistently collapsed; the Costa and true curves are superimposed and the two "
  "ODCL estimates coincide (both " + AP + " 12.6 cmH2O; dev " + AP + " 0). "
  "(c, d) With TR (TOP " + MI + " TCP = 10): a broad cyclic band occupies the mid-to-low PEEP range, "
  "in the volume that would otherwise be persistently collapsed. These cyclic units sustain a "
  "high apparent per-unit compliance to low PEEP (Figure 1), so the Costa collapse curve is not "
  "yet elevated where the true collapse curve already rises, and the Costa overdistension "
  "fraction also stays higher and persists to lower PEEP. The Costa crossing is consequently "
  "displaced to " + AP + " 9.1 cmH2O whereas the true ODCL is " + AP + " 10.6 cmH2O "
  "(dev " + AP + " " + MI + "1.5 cmH2O). The overdistension profile at high PEEP is identical between "
  "conditions; they differ only in low-PEEP behaviour, so the deviation arises from delayed "
  "collapse detection rather than from any change in the true optimum."),
 ('Fig4_sensitivity_en.png',
  'Figure 4. The downward deviation is robust across the model parameter space.',
  "One-at-a-time sensitivity analysis anchored to the representative TR condition "
  "(TOP " + MI + " TCP = 10, DP = 14 cmH2O; reference dev = " + MI + "1.54 cmH2O, marked by the red "
  "circle in each panel). Each parameter was varied with all others held fixed. "
  "(a) Driving pressure DP (5" + EN + "15 cmH2O): the deviation is largest at low DP "
  "(dev " + AP + " " + MI + "4.8 cmH2O at DP = 5) because a smaller tidal volume makes the fixed "
  "apparent-compliance distortion proportionally greater. "
  "(b) Inter-unit heterogeneity (max_sp): a wider distribution of unit thresholds deepens the "
  "deviation modestly (dev " + AP + " " + MI + "2.3 cmH2O at the widest), as more units fall into the "
  "cyclic band. "
  "(c) P" + EN + "V shape constant h: the deviation is nearly flat, indicating that the effect does "
  "not depend on the precise curvature of the pressure" + EN + "volume relationship. "
  "(d) TR closing pressure TCP (with TOP co-varied so TOP " + MI + " TCP is held at 10): the "
  "deviation shrinks as TCP rises toward mid-lung pressures (dev " + AP + " " + MI + "0.5 cmH2O at "
  "TCP = 6), because higher-lying units traverse a flatter part of the P" + EN + "V curve and their "
  "apparent-compliance overestimation is smaller. "
  "(e) Overdistension threshold TMP: the deviation scales strongly with the threshold, "
  "approaching zero at the low extreme (dev " + AP + " " + MI + "0.04 cmH2O at TMP " + GE + " 20 cmH2O) "
  + EM + " a mechanistic boundary at which overdistension is registered early enough to meet the "
  "collapse limb before the TR-induced lag becomes influential " + EM + " and reaching "
  "dev " + AP + " " + MI + "3.2 cmH2O at TMP " + GE + " 26 cmH2O. "
  "(f) Tornado plot: the deviation range spanned by each parameter, ranked; driving pressure "
  "and the overdistension threshold dominate. Across every setting the deviation remains "
  "negative: whenever tidal recruitment is present, the Costa ODCL lies below the true optimum."),
]

def build():
    doc = SimpleDocTemplate(os.path.join(OUT, "TR_ODCL_figures_EN_review.pdf"),
                            pagesize=PAGE, leftMargin=LM, rightMargin=RM,
                            topMargin=TM, bottomMargin=BM,
                            title="TR-ODCL English figures (review)")
    story = []
    story.append(Paragraph("Costa-method ODCL deviation under tidal recruitment "
                           "\u2014 English figures with legends (review draft)", st_h))
    story.append(Paragraph("BMC Pulmonary Medicine figure style: fonts embedded, "
                           "color keys embedded in each graphic. In the manuscript each "
                           "title (\u226415 words) and legend (\u2264300 words) belongs in the "
                           "text, not in the graphic; they are placed below each figure "
                           "here for review only.", st_note))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.6, color="#cccccc"))
    for fn, ttl, leg in FIGS:
        block = [Spacer(1, 3 * mm), img(fn, max_w_mm=170, max_h_mm=120),
                 Paragraph(ttl, st_ttl), Paragraph(leg, st_leg)]
        story.append(KeepTogether(block))
        story.append(Spacer(1, 2 * mm))
        story.append(HRFlowable(width="100%", thickness=0.4, color="#dddddd"))
    doc.build(story)
    print("built", os.path.join(OUT, "TR_ODCL_figures_EN_review.pdf"))

if __name__ == "__main__":
    build()
