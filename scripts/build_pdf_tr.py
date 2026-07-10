"""build_pdf_tr.py -- Japanese team-presentation PDF for the TR-only Hickling
ODCL study (airway-free). Reads out/sweeps_tr.json + out/sensitivity_tr.json so
all in-text numbers stay in sync with the data.

    python scripts/build_pdf_tr.py    ->  out/TR_ODCL_Hickling_presentation.pdf

Reuses the Arial-Unicode TrueType embedding approach (Hiragino ttc CFF outlines
cannot be embedded by reportlab).
"""
import os, json
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUT = "out"
_JP_TTF = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
pdfmetrics.registerFont(TTFont('JPserif', _JP_TTF))
pdfmetrics.registerFontFamily('JPserif', normal='JPserif', bold='JPserif',
                              italic='JPserif', boldItalic='JPserif')
JP = 'JPserif'
GE = "\u2267"   # ≧ (CJK, glyph-safe)
LE = "\u2266"   # ≦ (CJK, glyph-safe)

ss = getSampleStyleSheet()
def S(name, size, leading=None, color='#222222', align=TA_LEFT, space=6):
    return ParagraphStyle(name, parent=ss['Normal'], fontName=JP, fontSize=size,
        leading=leading or size*1.5, textColor=colors.HexColor(color),
        alignment=align, spaceAfter=space)
st_title = S('t', 20, color='#0b3d66', align=TA_CENTER, space=4)
st_sub   = S('s', 12, color='#555555', align=TA_CENTER, space=2)
st_h     = S('h', 15, color='#0b3d66', space=8)
st_body  = S('b', 10.5, leading=17)
st_bodys = S('bs', 9.5, leading=15)
st_note  = S('n', 8.5, color='#666666', leading=13)
st_cap   = S('c', 9, color='#444444', align=TA_CENTER, space=2)
st_key   = S('k', 11, color='#8a1c1c', leading=18)

PAGE = landscape(A4)
CW = PAGE[0] - 40*mm

def img(path, w):
    from reportlab.lib.utils import ImageReader
    ir = ImageReader(path); iw, ih = ir.getSize()
    return Image(path, width=w, height=w*ih/iw)

# ---- data ----
D = json.load(open(os.path.join(OUT, "sweeps_tr.json")))
gaps = D["gap"]
def g(v):  # fetch a gap row by gap width
    return min(gaps, key=lambda r: abs(r["gap"] - v))
g2, g6, g10, g18 = g(2.0), g(6.0), g(10.0), g(18.0)   # min / representative TR / mid / control
SN = json.load(open(os.path.join(OUT, "sensitivity_tr.json")))
ref = SN["reference"]

story = []

# ================= P1 cover =================
story += [Spacer(1, 38*mm)]
story += [Paragraph('tidal recruitment は Costa 法 ODCL を'
                    '「真の最適 PEEP」から低圧側へ歪める', st_title)]
story += [Paragraph('― 気道要素を排した Hickling 型肺胞モデルによる in silico 検証 ―', st_sub)]
story += [Spacer(1, 10*mm)]
story += [Paragraph('肺シミュレーションモデル (lung_sim v83, airway-free) による検証',
                    S('x', 12, color='#333333', align=TA_CENTER, space=2))]
story += [Spacer(1, 28*mm)]
story += [Paragraph('チーム内共有資料', st_sub)]
story += [PageBreak()]

# ================= P2 background =================
story += [Paragraph('1. 背景と目的', st_h)]
story += [HRFlowable(width='100%', color=colors.HexColor('#cccccc'), spaceAfter=8)]
story += [Paragraph(
    'Costa らの電気インピーダンス・トモグラフィ(EIT)由来の ODCL（overdistension–collapse '
    'decrement limit）は、減圧 PEEP トライアル中の局所コンプライアンス変化から「虚脱%」と'
    '「過膨張%」を推定し、両者が交差する PEEP を最適 PEEP とする方法である。', st_body)]
story += [Paragraph(
    '本検討では気道の開閉（AOP/ACP）要素を<b>すべて排除</b>し、オリジナルの Hickling 型'
    '肺胞リクルートメント／デリクルートメントのみを持つモデルを用いる。'
    '唯一の周期的機序は <b>tidal recruitment（TR）</b>：肺胞が吸気で開き（TMP{GE}TOP）'
    '呼気で虚脱する（TMP&lt;TCP）現象である。'.replace('{GE}', GE), st_body)]
story += [Spacer(1, 3*mm)]
story += [Paragraph(
    '【目的】 肺胞ヒステリシス幅 gap（＝TOP−TCP）を変化させて TR の強さを直接操作し、'
    'Costa ODCL が<b>真の ODCL</b>（真の虚脱と過膨張を最小化する PEEP）から、'
    'どの方向・どの程度ずれるかを同一モデル上で定量する。', st_key)]
story += [Paragraph(
    '※ 気道補正法は扱わない。純粋に「TR が ODCL 推定に与える系統誤差」を提示する。', st_note)]
story += [PageBreak()]

# ================= P3 definitions =================
story += [Paragraph('2. 定義（本検討で確定）', st_h)]
story += [HRFlowable(width='100%', color=colors.HexColor('#cccccc'), spaceAfter=8)]
defs = [
    ['用語', '定義'],
    ['真の虚脱', '呼吸周期を通じて開通しない肺胞（always-closed）。TR（周期的再開通）は含めない。'],
    ['過膨張', '換気しているユニットのうち吸気末 経肺胞圧 TMP{GE}23 cmH2O のもの。'.replace('{GE}', GE)],
    ['真の ODCL', '真の虚脱% と 過膨張% が交差する PEEP（真に最小化すべき最適 PEEP）。'],
    ['Costa ODCL', '局所コンプライアンス低下から推定した虚脱%／過膨張% の交差 PEEP（補正なし）。'],
    ['tidal recruitment', '吸気で開き呼気で虚脱する肺胞（TMP が TOP/TCP を跨ぐ）。'
                          'Costa はこれを見かけのコンプライアンス変化として拾う。'],
]
t = Table(defs, colWidths=[CW*0.20, CW*0.80])
t.setStyle(TableStyle([
    ('FONT', (0,0), (-1,-1), JP, 10),
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b3d66')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('LINEBELOW', (0,0), (-1,-1), 0.4, colors.HexColor('#bbbbbb')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f2f6fa')]),
    ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story += [t]
story += [PageBreak()]

# ================= P4 model & method =================
story += [Paragraph('3. モデルと解析方法', st_h)]
story += [HRFlowable(width='100%', color=colors.HexColor('#cccccc'), spaceAfter=8)]
story += [Paragraph(
    '<b>肺モデル</b>：30 区画 × 1000 サブユニット（計 30,000）。各区画は重力方向の'
    '重畳圧（superimposed pressure, 0〜{ms} cmH2O）で階層化。P-V 曲線は '
    'v = v0(1 − exp(−P·ln2/h)), h={h}。気道機序（AOP/ACP）は無効化。'
    .replace('{ms}', f'{ref["max_sp"]:.1f}').replace('{h}', f'{ref["h_mean"]:.1f}'), st_body)]
story += [Paragraph(
    '<b>PEEP トライアル</b>：ドライビング圧 DP={dp} cmH2O 固定、PEEP を 24→2 cmH2O へ減圧、'
    'リクルートメント PIP=45、n_stab=5、過膨張 TMP{GE}23、n={n} seed で平均。'
    .replace('{dp}', f'{ref["dp"]:.0f}').replace('{GE}', GE).replace('{n}', f'{ref["n_seed"]}'),
    st_body)]
story += [PageBreak()]

# ---------------- P4b: TR (gap) manipulation (detailed) ----------------
story += [Paragraph('3-2. TR の操作：ヒステリシス gap（詳細）', st_h)]
story += [HRFlowable(width='100%', color=colors.HexColor('#cccccc'), spaceAfter=8)]
story += [Paragraph(
    'TR の強さを「単一変数」として動かすため、肺全体を recruitable な肺胞ユニットとし、'
    'その<b>肺胞ヒステリシス幅 gap＝TOP−TCP</b>のみを操作変数とする。閉鎖閾値 TCP は '
    '{c} cmH2O に固定し、開放閾値 TOP を上げ下げして gap を変える（最小 gap=2、TOP={c2}）。'
    .replace('{c}', f'{ref["tcp_tr"]:.0f}').replace('{c2}', f'{ref["tcp_tr"]+2:.0f}'), st_body)]
st_cell = ParagraphStyle('cell', fontName=JP, fontSize=9, leading=12.5, textColor=colors.HexColor('#222222'))
grp = [
    ['条件', 'gap = TOP − TCP', '滴定中の挙動', 'TR 負荷'],
    [Paragraph('gap 小（強 TR）', st_cell),
     Paragraph('例 gap=2〜6（TOP={a}〜{b}、TCP={c}）'
     .replace('{a}', f'{ref["tcp_tr"]+2:.0f}').replace('{b}', f'{ref["tcp_tr"]+6:.0f}')
     .replace('{c}', f'{ref["tcp_tr"]:.0f}'), st_cell),
     Paragraph('呼気で TMP＜TCP→完全虚脱、吸気で TMP{GE}TOP→再開通。'
     '毎呼吸「全開閉スイング」を繰り返す（＝tidal recruitment）。'.replace('{GE}', GE), st_cell),
     Paragraph('大（cyclic 多い）', st_cell)],
    [Paragraph('gap 大（TR 消失）', st_cell),
     Paragraph('例 gap{GE}14（TOP{GE}16）'.replace('{GE}', GE), st_cell),
     Paragraph('開放閾値が高すぎて一度虚脱すると毎呼吸の再開通が起きない。'
     '高 PEEP では開存、低 PEEP では恒久虚脱に落ちる＝周期性なし。Costa 中立（乖離≒0）。', st_cell),
     Paragraph('ほぼ 0（対照）', st_cell)],
]
tg = Table(grp, colWidths=[CW*0.16, CW*0.24, CW*0.46, CW*0.14])
tg.setStyle(TableStyle([
    ('FONT', (0,0), (-1,-1), JP, 9),
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b3d66')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('LINEBELOW', (0,0), (-1,-1), 0.4, colors.HexColor('#bbbbbb')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f2f6fa')]),
    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story += [tg]
story += [Spacer(1, 3*mm)]
story += [Paragraph(
    '<b>この設計の要点</b>：全条件が<b>同一の肺（同一シード）</b>で TOP のみ異なり、'
    '肺の力学（DP、PEEP 範囲、P-V 曲線 h、重畳圧分布、過膨張閾値）は gap に依らず完全に固定'
    'される。したがって Costa ODCL の変化は「ヒステリシス gap＝TR の強さ」のみに起因し、'
    '他の交絡を排除できる。', st_body)]
story += [Paragraph(
    '<b>なぜ gap がTRを制御するか</b>：gap が DP を下回ると、呼気末に閉じたユニットは'
    '次の吸気で必ず再開通する（cyclic）。gap が DP に近づくほど再開通に必要な圧が高くなり、'
    'PEEP を下げると再開通できず恒久虚脱へ移行する（TR 消失）。gap は「虚脱ユニットが '
    'cyclic に留まるか恒久閉鎖するか」を決める物理量である。', st_body)]
story += [Paragraph(
    '<b>gap 大（≧14）は内部対照</b>：cyclic ユニットが消えるので Costa≒真（乖離 dev≒{d} '
    'cmH2O）。gap を縮めるほど TR の影響だけが現れる。報告する「TR 負荷」は、滴定全体での'
    '最大 cyclic ユニット%（ピーク cyclic%）で表す。'
    .replace('{d}', f'{g18["dev"]:+.2f}'), st_key)]
story += [PageBreak()]

# ================= P5 concept figure =================
story += [Paragraph('4. tidal recruitment とは／ヒステリシス gap の設定', st_h)]
story += [img(os.path.join(OUT, 'FigT1_concept.png'), CW*0.92)]
story += [Paragraph('図1（左）：Salazar P-V 曲線上で TCP と TOP を結ぶ直線（緑破線＝開存ユニットの傾き）'
                    'に対し、虚脱（V=0）から TOP へ立ち上がる TR ユニットの傾き（紫）は急で、'
                    '見かけコンプライアンスが直線より大きく見える（網掛け＝過大分）。'
                    '右：唯一の操作変数 gap＝TOP−TCP。', st_cap)]
story += [PageBreak()]

# ================= P6 MAIN result =================
story += [Paragraph('5. 主結果：TR が増えるほど Costa ODCL が真値から下方へ乖離', st_h)]
story += [img(os.path.join(OUT, 'FigT2_core.png'), CW*0.96)]
story += [Paragraph(
    '図2：（左）ヒステリシス gap を縮める（TR を強める）ほど Costa ODCL が真の ODCL より'
    '低圧へ乖離。（右）実際の TR 負荷（ピーク cyclic ユニット%）と乖離量は単調に対応。', st_cap)]
story += [Paragraph(
    'gap=2〜18 の全域で dev&lt;0（単調）：gap=18（TR 消失）で dev={d18}、gap=10 で {d10}、'
    'gap=6 で {d6}、gap=2（最強 TR）で {d2} cmH2O。gap が DP={dp} に近づくと乖離は消失する。'
    .replace('{d18}', f'{g18["dev"]:+.2f}').replace('{d10}', f'{g10["dev"]:+.2f}')
    .replace('{d6}', f'{g6["dev"]:+.2f}').replace('{d2}', f'{g2["dev"]:+.2f}')
    .replace('{dp}', f'{ref["dp"]:.0f}'), st_key)]
story += [PageBreak()]

# ================= P7 representative curves =================
story += [Paragraph('6. 代表的な減圧トライアル（TR なし vs TR あり）', st_h)]
story += [img(os.path.join(OUT, 'FigT3_curves.png'), CW*0.96)]
story += [Paragraph(
    '図3：TR ありでは低 PEEP まで見かけコンプライアンスが保たれ、Costa の虚脱検出が'
    '低圧へ遅れる → 交差点（Costa ODCL）が真値より低圧に落ちる。', st_cap)]
story += [PageBreak()]

# ================= P8 state composition =================
story += [Paragraph('7. 状態組成の推移', st_h)]
story += [img(os.path.join(OUT, 'FigT4_states.png'), CW*0.96)]
story += [Paragraph(
    '図4：TR あり条件でのみ cyclic（紫）ユニットが出現。過膨張（赤線）は換気ユニットの'
    '部分集合なのでオーバーレイ表示（積み上げない）。', st_cap)]
story += [PageBreak()]

# ================= P9 mechanism prose =================
story += [Paragraph('8. なぜ Costa ODCL が下がるのか（機序）', st_h)]
story += [HRFlowable(width='100%', color=colors.HexColor('#cccccc'), spaceAfter=8)]
for i, txt in enumerate([
    'TR ユニットは呼気で完全虚脱→吸気で再開通する。この「全開閉スイング」は、'
    '恒久虚脱（換気量ゼロ）を基準にすると見かけ上きわめて大きなコンプライアンスに映る。',
    'このスイングは低 PEEP でも維持されるため、見かけコンプライアンスのピークが'
    '低圧側へ移動する（各ユニットの基準 PEEP が低圧に集中）。',
    'Costa は各ユニットの最大コンプライアンス PEEP を基準に虚脱を判定するので、'
    '低圧まで「虚脱していない」と誤認し、虚脱%の立ち上がりが低圧へ遅れる。',
    '結果として虚脱%と過膨張%の交差点（Costa ODCL）が真値より低圧に引きずられる'
    '（代表条件 gap=6 のとき Costa={c} &lt; 真 {t} cmH2O）。'
    .replace('{c}', f'{g6["costa"]:.1f}').replace('{t}', f'{g6["true"]:.1f}')],
    ):
    story += [Paragraph(f'<b>{["①","②","③","④"][i]}</b> {txt}', st_body)]
story += [PageBreak()]

# ================= P10 mechanism figure =================
story += [Paragraph('8-2. 機序図：虚脱検出の遅れ', st_h)]
story += [img(os.path.join(OUT, 'FigT5_mechanism.png'), CW*0.66)]
story += [Paragraph('図5：代表 TR 条件（gap=6）で、Costa の見かけ虚脱%（水色）は真の恒久虚脱%'
                    '（紺破線）より低圧まで立ち上がらない。この検出の遅れにより、虚脱%と'
                    '過膨張%の交差点＝Costa ODCL が真値より低圧に落ちる。', st_cap)]
story += [PageBreak()]

# ================= P11 sensitivity =================
story += [Paragraph('9. 肺モデルパラメータの感度解析', st_h)]
story += [img(os.path.join(OUT, 'FigT6_sensitivity.png'), CW*0.98)]
story += [Paragraph(
    '図6：代表 TR 条件（全肺 recruitable、gap=6）固定で 5 パラメータを個別に変化（赤丸＝基準）。'
    'DP=5〜15 の全域で dev<0（低 DP ほど乖離大）。過膨張閾値を 20 cmH2O まで下げた端でのみ'
    '乖離がほぼ消失＝機序的境界。生理的範囲では TR による下方乖離は頑健。'
    'なお TR の閉鎖圧 TCP を変えても（ヒステリシス幅 gap=6 は保ったままループ全体を'
    '圧軸上で上下させても）乖離は残存する。ヒステリシス幅 gap そのものの掃引は本解析'
    '（図2）と同一の操作のため、感度解析からは重複として除外した。', st_cap)]
story += [PageBreak()]

# ================= P12 conclusion =================
story += [Paragraph('10. 結論と限界', st_h)]
story += [HRFlowable(width='100%', color=colors.HexColor('#cccccc'), spaceAfter=8)]
story += [Paragraph(
    '<b>結論</b>：気道要素を排した純 Hickling 型モデルでも、tidal recruitment が存在すると'
    'Costa 法 ODCL は真の最適 PEEP より系統的に<b>低圧側へ</b>ずれる。乖離量は TR 負荷と'
    '単調に増大し、生理的パラメータ範囲で頑健である。', st_key)]
story += [Paragraph(
    '<b>限界</b>：(1) in silico モデルであり実データ検証は今後。'
    '(2) 過膨張は TMP{GE}23 の二値判定、Costa 過膨張は連続コンプライアンス重みで、'
    '両者の定義差が小さな固定オフセットを生む。'
    '(3) 機序を明確にするため gap=2〜18 の全域を提示したが、最小 gap（gap=2〜4）では'
    'ピーク cyclic ユニットが 67〜79% に達し、実肺では非現実的に高い。先行研究では'
    '不安定膨張組織が肺の 28% を超えると死亡と関連し（Thorax 2017）、臨床的に妥当な TR 負荷は'
    'これ以下に留まる。ただし乖離は gap 全域で単調に負であり、生理的範囲でも一貫して下方バイアスを示す。'
    .replace('{GE}', GE).replace('{LE}', LE), st_body)]
story += [Spacer(1, 4*mm)]
story += [Paragraph(
    '<b>参考文献</b>：'
    '(1) Bellani/Terragni et al. Tidal changes on CT and progression of ARDS. Thorax 2017 (PMID 28634220). '
    '(2) Retamal/Bugedo et al. Tidal volume is a major determinant of cyclic recruitment-derecruitment. '
    'Intensive Care Med 2011 (PMID 21483386). '
    '(3) Mojoli et al. Tidal lung hysteresis to interpret PEEP-induced changes in compliance. '
    'Crit Care 2023 (PMC10261834).', st_cap)]

doc = SimpleDocTemplate(os.path.join(OUT, 'TR_ODCL_Hickling_presentation.pdf'),
    pagesize=PAGE, leftMargin=20*mm, rightMargin=20*mm,
    topMargin=14*mm, bottomMargin=12*mm)
doc.build(story)
print('built out/TR_ODCL_Hickling_presentation.pdf')
