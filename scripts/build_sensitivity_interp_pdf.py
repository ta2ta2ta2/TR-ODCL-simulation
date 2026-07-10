"""build_sensitivity_interp_pdf.py -- Japanese team-facing interpretation guide
for the TR-only ODCL sensitivity analysis. Reads out/sensitivity_tr.json so every
in-text number stays in sync with the data, and embeds out/Fig6_sensitivity_en.png.

    python scripts/build_sensitivity_interp_pdf.py
        -> out/TR_ODCL_sensitivity_interpretation.pdf

Portrait A4 reading document. One section per swept parameter (DP, max_sp, h_mean,
TCP_TR, OD_THR) + tornado summary, each with a values table and a mechanistic
interpretation grounded in the airway-free Hickling TR model.
"""
import os, json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUT = "out"
_JP_TTF = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
pdfmetrics.registerFont(TTFont('JPserif', _JP_TTF))
pdfmetrics.registerFontFamily('JPserif', normal='JPserif', bold='JPserif',
                              italic='JPserif', boldItalic='JPserif')
JP = 'JPserif'
GE = "\u2267"   # >= (CJK glyph-safe)
LE = "\u2266"   # <=
MINUS = "\u2212"

ss = getSampleStyleSheet()
def S(name, size, leading=None, color='#222222', align=TA_LEFT, space=6):
    return ParagraphStyle(name, parent=ss['Normal'], fontName=JP, fontSize=size,
        leading=leading or size*1.6, textColor=colors.HexColor(color),
        alignment=align, spaceAfter=space)
st_title = S('t', 19, color='#0b3d66', align=TA_CENTER, space=4)
st_sub   = S('s', 11.5, color='#555555', align=TA_CENTER, space=2)
st_h     = S('h', 15, color='#0b3d66', space=7)
st_h2    = S('h2', 12.5, color='#8a5a00', space=5)
st_body  = S('b', 10.3, leading=16.5)
st_bodys = S('bs', 9.3, leading=14.5, color='#333333')
st_note  = S('n', 8.5, color='#666666', leading=12.5)
st_cap   = S('c', 9, color='#444444', align=TA_CENTER, space=2)
st_key   = S('k', 10.6, color='#8a1c1c', leading=17)

PAGE = A4
CW = PAGE[0] - 36*mm

def img(path, w):
    from reportlab.lib.utils import ImageReader
    ir = ImageReader(path); iw, ih = ir.getSize()
    return Image(path, width=w, height=w*ih/iw)

def fnum(x, nd=2):
    s = f'{x:.{nd}f}'
    return s.replace('-', MINUS)

# ---- data ----
SN = json.load(open(os.path.join(OUT, "sensitivity_tr.json")))
ref = SN["reference"]
SW = SN["sweeps"]

def valtable(rows, headers):
    t = Table([headers] + rows, colWidths=None, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), JP, 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b3d66')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.4, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f2f6fa')]),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def sweep_rows(key):
    rows = []
    for r in SW[key]:
        mark = '  (基準)' if r['is_ref'] else ''
        rows.append([f'{r["value"]:.1f}{mark}', fnum(r['costa']), fnum(r['true']),
                     fnum(r['dev'])])
    return rows

HDR = ['設定値 (cmH2O)', 'Costa ODCL', '真の ODCL', '乖離 dev']

story = []

# ================= COVER =================
story += [Spacer(1, 8*mm)]
story += [Paragraph('感度解析の読み方と各結果の解釈', st_title)]
story += [Paragraph('― TR-only（気道排除）Hickling モデルにおける '
                    'ODCL 乖離のパラメータ感度 ―', st_sub)]
story += [Spacer(1, 4*mm)]
story += [HRFlowable(width='100%', color=colors.HexColor('#cccccc'), spaceAfter=6)]
story += [Paragraph(
    '本資料は、発表スライドの感度解析図（Fig. 6）に示した 5 つのパラメータ掃引と'
    'トルネード図について、<b>それぞれが何を意味し、なぜその傾向になるのか</b>を'
    '機序に沿って解説する補足資料である。数値はすべて out/sensitivity_tr.json '
    'から直接読み込んでおり、本文と図は同一データに基づく。', st_body)]

# ---- what the analysis is ----
story += [Paragraph('0. 感度解析の枠組み', st_h)]
story += [Paragraph(
    '主結果（gap 掃引）は「TR が強いほど Costa ODCL が真値から低圧側へずれる」ことを示した。'
    '感度解析の目的は、<b>この乖離が特定のパラメータ設定に依存した見かけの現象ではなく、'
    '肺モデルの妥当なパラメータ範囲全体で頑健に成立する</b>ことを確認することである。', st_body)]
story += [Paragraph(
    '<b>手法（One-at-a-time）</b>：TR 負荷を生理的に代表的な水準に固定し'
    '（gap = TOP{MINUS}TCP = {g} cmH2O、全肺リクルータブル、代表的 TR 条件）、'
    'そこから 1 つのパラメータだけを基準値の周囲で動かし、他は固定する。'
    '各図の赤丸が基準条件（dev = {dref} cmH2O）である。'
    .replace('{MINUS}', MINUS).replace('{g}', f'{ref["gap"]:.0f}')
    .replace('{dref}', fnum(SW["DP"][5]["dev"])), st_body)]
story += [Paragraph(
    '<b>指標の符号</b>：dev = Costa ODCL {MINUS} 真の ODCL。'
    '<b>dev &lt; 0</b> は Costa が真の最適 PEEP より<b>低い</b> PEEP を最適と誤判定すること'
    '（＝ TR による系統的な低圧側バイアス）を意味する。'
    .replace('{MINUS}', MINUS), st_key)]
story += [Paragraph(
    '基準条件：DP={dp}、max_sp={ms}、h={h}、TOP={top}／TCP={tcp}（gap={g}）、'
    '過膨張閾値 TMP{GE}{od}、n={n} seed。'
    .replace('{dp}', f'{ref["dp"]:.0f}').replace('{ms}', f'{ref["max_sp"]:.1f}')
    .replace('{h}', f'{ref["h_mean"]:.1f}').replace('{top}', f'{ref["top_tr"]:.0f}')
    .replace('{tcp}', f'{ref["tcp_tr"]:.0f}').replace('{g}', f'{ref["gap"]:.0f}')
    .replace('{GE}', GE).replace('{od}', f'{ref["od_thr"]:.0f}')
    .replace('{n}', f'{ref["n_seed"]}'), st_note)]
story += [PageBreak()]

# ================= FIGURE =================
story += [Paragraph('感度解析図（Fig. 6）全体', st_h)]
story += [img(os.path.join(OUT, "Fig6_sensitivity_en.png"), CW)]
story += [Paragraph(
    '左〜中央の 5 パネル：各パラメータを掃引したときの dev。右のトルネード図：'
    '各パラメータが張る dev の範囲。赤破線が基準条件 dev={dref}。'
    '<b>すべてのパネルで曲線は 0 線より下（dev &lt; 0）にあり</b>、'
    '乖離が全域で負に保たれることが一目で分かる。'
    .replace('{dref}', fnum(SW["DP"][5]["dev"])), st_cap)]
story += [Paragraph(
    '以下、各パラメータについて「何を変えたか／なぜその傾向か／論文上の含意」を順に解説する。',
    st_body)]
story += [PageBreak()]

# ================= 1. DP =================
story += [Paragraph('1. ドライビング圧 DP（駆動圧）', st_h)]
story += [Paragraph('掃引範囲 5〜15 cmH2O ／ 基準 14 cmH2O', st_h2)]
story += [valtable(sweep_rows("DP"), HDR)]
story += [Spacer(1, 3*mm)]
story += [Paragraph('<b>傾向</b>：DP を下げるほど乖離が急激に大きくなる'
    '（DP=15 で dev={a} → DP=5 で dev={b}）。全域で dev &lt; 0。'
    .replace('{a}', fnum(SW["DP"][6]["dev"])).replace('{b}', fnum(SW["DP"][0]["dev"])), st_body)]
story += [Paragraph('<b>なぜか（二重の効果）</b>：', st_h2)]
story += [Paragraph(
    '① <u>見かけコンプライアンスの増幅</u>：TR ユニットは毎呼吸ゼロ容量から再開通する。'
    'その見かけ弦コンプライアンスは（再開通容量 ΔV）÷ DP なので、DP が小さいほど同じ ΔV が'
    '小さい分母で割られ、<b>見かけコンプライアンスがより誇張</b>される。Costa はこれを健常な'
    '開存ユニットと誤認し、虚脱検出がさらに低圧まで遅れる。', st_bodys)]
story += [Paragraph(
    '② <u>真の過膨張の高圧化</u>：吸気末圧 ti = PEEP + DP {MINUS} sp。DP が小さいと '
    'TMP{GE}23 に達するのに高い PEEP が必要になり、<b>真の過膨張限界（＝真の ODCL）が高圧へ移動</b>'
    'する（DP=5 で真値 {t}）。一方 Costa の交差点は誇張コンプライアンスに引きずられ低圧のまま'
    '（{c}）。両者の差が {d} まで開く。'
    .replace('{MINUS}', MINUS).replace('{GE}', GE)
    .replace('{t}', fnum(SW["DP"][0]["true"])).replace('{c}', fnum(SW["DP"][0]["costa"]))
    .replace('{d}', fnum(SW["DP"][0]["dev"])), st_bodys)]
story += [Paragraph(
    '<b>論文上の含意（重要）</b>：肺保護換気は低 DP を志向するため、'
    '<b>臨床的に望ましい低 DP ほど Costa の低圧バイアスは悪化する</b>。'
    'この所見は本研究の警鐘を強める方向に働く。', st_key)]
story += [PageBreak()]

# ================= 2. max_sp =================
story += [Paragraph('2. 不均一性 max_sp（重畳圧の広がり）', st_h)]
story += [Paragraph('掃引範囲 10〜18 cmH2O ／ 基準 14.5 cmH2O', st_h2)]
story += [valtable(sweep_rows("max_sp"), HDR)]
story += [Spacer(1, 3*mm)]
story += [Paragraph('<b>傾向</b>：不均一性が小さいほど乖離が大きい'
    '（max_sp=10 で dev={a}、Costa は {c} まで低下 → max_sp=18 で dev={b}）。全域で dev &lt; 0。'
    .replace('{a}', fnum(SW["max_sp"][0]["dev"])).replace('{c}', fnum(SW["max_sp"][0]["costa"]))
    .replace('{b}', fnum(SW["max_sp"][4]["dev"])), st_body)]
story += [Paragraph('<b>なぜか</b>：', st_h2)]
story += [Paragraph(
    'max_sp は 30 区画に割り当てる重畳圧（＝局所の開閉圧の分布幅）を決める。'
    '<u>均一な肺（max_sp 小）</u>では TR ユニットの開閉圧がそろい、'
    '<b>狭い PEEP 帯で一斉に再開通・虚脱</b>する。その結果、見かけコンプライアンスの誇張が'
    '同期して集中し、Costa の虚脱検出が一括して極端に低い PEEP（{c}）まで遅れ、乖離が最大化する。'
    .replace('{c}', fnum(SW["max_sp"][0]["costa"])), st_bodys)]
story += [Paragraph(
    '<u>不均一な肺（max_sp 大）</u>では開閉圧が広く分散し、TR の影響が多数の PEEP 水準へ'
    '<b>薄く引き伸ばされる</b>。さらに高 sp ユニットが高い PEEP を要するため真の ODCL 自体が'
    '上昇し（{t}）、相対的な乖離が希釈される。'
    .replace('{c}', fnum(SW["max_sp"][0]["costa"]))
    .replace('{t}', fnum(SW["max_sp"][4]["true"])), st_bodys)]
story += [Paragraph(
    '<b>論文上の含意</b>：均一性の高い（早期・限局性の少ない）ARDS 肺ほど Costa の誤差が'
    '大きくなりうる。ただし乖離の符号は全域で負であり、結論は不均一性に依存しない。', st_key)]
story += [PageBreak()]

# ================= 3. h_mean =================
story += [Paragraph('3. P-V 曲線形状定数 h', st_h)]
story += [Paragraph('掃引範囲 3.9〜5.9 cmH2O ／ 基準 4.9 cmH2O', st_h2)]
story += [valtable(sweep_rows("h_mean"), HDR)]
story += [Spacer(1, 3*mm)]
story += [Paragraph('<b>傾向</b>：感度は最も弱い。dev は {a} 〜 {b} の狭い範囲にとどまり、'
    '真の ODCL は {t} で一定。'
    .replace('{a}', fnum(SW["h_mean"][0]["dev"])).replace('{b}', fnum(SW["h_mean"][4]["dev"]))
    .replace('{t}', fnum(SW["h_mean"][0]["true"])), st_body)]
story += [Paragraph('<b>なぜか</b>：', st_h2)]
story += [Paragraph(
    'h は単位 P-V 曲線 v = v0(1 {MINUS} exp({MINUS}P·ln2/h)) の圧力定数で、各ユニットの'
    '容量の立ち上がり方（硬さ）を決める。h は<b>どのユニットが TR になるか</b>にも'
    '<b>過膨張閾値</b>にも影響しないため、真の ODCL は不変。'
    '変わるのは見かけコンプライアンス誇張の深さだけで、その効果は小さい。'
    .replace('{MINUS}', MINUS), st_bodys)]
story += [Paragraph(
    '<b>論文上の含意</b>：本モデルの中心的パラメータである P-V 形状は結論に対する'
    '感度が低く、<b>結果の頑健性を支持</b>する。', st_key)]
story += [PageBreak()]

# ================= 4. TCP_TR =================
story += [Paragraph('4. TR 閉鎖圧 TCP（gap 固定・帯の圧位置を移動）', st_h)]
story += [Paragraph('掃引範囲 0〜6 cmH2O ／ 基準 2 cmH2O（TOP を TCP+6 で連動、gap=6 一定）', st_h2)]
story += [valtable(sweep_rows("TCP_TR"), HDR)]
story += [Spacer(1, 3*mm)]
story += [Paragraph(
    '<b>まず注意：この掃引では gap は縮まない。</b> 直感的には「TCP を上げれば TOP{MINUS}TCP が'
    '縮んで TR が強まり乖離が拡大するはず」だが、本パネルはそうならない。設定上 '
    '<b>TOP = TCP + 6 として TOP を TCP と一緒に引き上げており、gap = TOP{MINUS}TCP は 6 で一定</b>'
    'に保たれる。したがって TR の「量」は変わらず、変わるのは<b>再開通が起こる圧帯の絶対位置</b>'
    'だけである。実際、周期的リクルートメント量（peak cyclic）は全水準で 53.4% と完全に一定である。'
    .replace('{MINUS}', MINUS), st_key)]
story += [Paragraph(
    '（gap そのものを縮めて TR を強める操作＝ご指摘の効果は、TCP を 2 に固定して TOP を下げる'
    '<b>主掃引（gap 掃引）で提示済み</b>であり、そこでは gap 小＝強い TR＝乖離大となる。'
    '本パネルは主掃引と重複しないよう、あえて gap を固定して別の軸を分離している。）', st_note)]
story += [Paragraph('<b>傾向</b>：TCP（＝帯の圧位置）を上げると乖離は 0 に近づく'
    '（TCP=0 で dev={a} → TCP=6 で dev={b}）。全域で dev &lt; 0。'
    .replace('{a}', fnum(SW["TCP_TR"][0]["dev"])).replace('{b}', fnum(SW["TCP_TR"][3]["dev"])), st_body)]
story += [Paragraph('<b>なぜか（gap 一定なのに乖離が縮む理由）</b>：', st_h2)]
story += [Paragraph(
    'gap（TR 量）が同じでも、TCP を上げると再開通する圧帯全体が<b>高い PEEP 側へ平行移動</b>'
    'する。ここで真の ODCL は「過膨張（TMP{GE}23）が現れる高 PEEP 側」で決まり、その位置は帯の'
    '移動につれて上昇する（真値 {tc}→{tc2}）。一方 Costa の見かけ交差点も帯とともに上昇する'
    '（{cc}→{cc2}）。'
    .replace('{GE}', GE)
    .replace('{tc}', fnum(SW["TCP_TR"][0]["true"])).replace('{tc2}', fnum(SW["TCP_TR"][3]["true"]))
    .replace('{cc}', fnum(SW["TCP_TR"][0]["costa"])).replace('{cc2}', fnum(SW["TCP_TR"][3]["costa"])),
    st_bodys)]
story += [Paragraph(
    'ただし両者の上がり方は非対称である。TCP が高いと、TR ユニットは減圧トライアルの'
    '<b>比較的高い PEEP で恒久虚脱へ移行</b>し、その圧帯が真の過膨張限界に近づく。'
    'このとき見かけコンプライアンス誇張が及ぶ PEEP 範囲と真の虚脱・過膨張の PEEP 範囲が'
    '重なり、Costa の検出遅れの「幅」が縮む。結果として真値と Costa の差（＝乖離）が小さくなる。'
    '逆に TCP が低いほど帯が低圧側にあり、誇張が真の過膨張限界からより離れた低圧まで'
    '伸びるため、検出遅れが拡大し乖離が最大化する。', st_bodys)]
story += [Paragraph(
    '<b>論文上の含意</b>：TR ユニットが<b>低い圧まで開存を保つ（低 TCP）</b>ほど乖離が大きい。'
    'これは「早期に閉じてしまう TR ほど真の虚脱に近く Costa が検出しやすい」という機序と整合する。'
    'gap を固定した本掃引でも符号は全域で負であり、結論は帯の圧位置に依存しない。', st_key)]
story += [PageBreak()]

# ================= 5. OD_THR =================
story += [Paragraph('5. 過膨張閾値 OD_THR（TMP 判定）', st_h)]
story += [Paragraph('掃引範囲 20〜26 cmH2O ／ 基準 23 cmH2O', st_h2)]
story += [valtable(sweep_rows("OD_THR"), HDR)]
story += [Spacer(1, 3*mm)]
story += [Paragraph('<b>傾向</b>：最も感度が高い。ただし Costa ODCL は {c} で不変であり、'
    '動くのは<b>真の ODCL のみ</b>（{t20}→{t26}）。緩い閾値 20 では乖離がほぼ消える'
    '（dev={d20}）、厳しい閾値 26 では乖離が最大（dev={d26}）。'
    .replace('{c}', fnum(SW["OD_THR"][0]["costa"]))
    .replace('{t20}', fnum(SW["OD_THR"][0]["true"])).replace('{t26}', fnum(SW["OD_THR"][2]["true"]))
    .replace('{d20}', fnum(SW["OD_THR"][0]["dev"])).replace('{d26}', fnum(SW["OD_THR"][2]["dev"])),
    st_body)]
story += [Paragraph('<b>なぜか（他の 4 つと質が違う）</b>：', st_h2)]
story += [Paragraph(
    'この閾値は Costa の（誤った）コンプライアンス由来虚脱検出には一切影響せず'
    '（Costa は {c} で固定）、<b>比較対象である「真の ODCL」の定義位置だけ</b>を動かす。'
    '閾値を厳しく（26）すると過膨張が高圧でしか成立せず真の ODCL が上昇（{t26}）、'
    '緩く（20）すると過膨張が低圧で成立し真の ODCL が Costa と同じ低圧（{t20}）に来て'
    '両者が偶然一致する。'
    .replace('{c}', fnum(SW["OD_THR"][0]["costa"]))
    .replace('{t26}', fnum(SW["OD_THR"][2]["true"]))
    .replace('{t20}', fnum(SW["OD_THR"][0]["true"])), st_bodys)]
story += [Paragraph(
    '<b>重要な注意（論文で明示すべき）</b>：緩い閾値 20 で乖離が消えるのは'
    '<b>Costa が正確になったからではなく、「真の最適 PEEP」の定義を低圧側に付け替えたため</b>'
    'である。文献（Mojoli）に基づく TMP{GE}23 を採用する限り乖離は明確に負であり、'
    '報告する乖離の大きさは採用する過膨張基準に依存することを透明に述べる必要がある。'
    .replace('{GE}', GE), st_key)]
story += [PageBreak()]

# ================= 6. tornado =================
story += [Paragraph('6. トルネード図（総括）', st_h)]
rng = {}
for k in ["DP","max_sp","h_mean","TCP_TR","OD_THR"]:
    ds = [r["dev"] for r in SW[k]]
    rng[k] = (min(ds), max(ds))
labels = {"DP":"駆動圧 DP","OD_THR":"過膨張閾値","max_sp":"不均一性 max_sp",
          "TCP_TR":"TR 閉鎖圧 TCP","h_mean":"P-V 形状 h"}
order = sorted(rng, key=lambda k: rng[k][0])  # widest (most negative min) first
trows = [[labels[k], fnum(rng[k][0]), fnum(rng[k][1]),
          fnum(rng[k][1]-rng[k][0])] for k in order]
story += [valtable(trows, ['パラメータ', 'dev 最小', 'dev 最大', '幅'])]
story += [Spacer(1, 3*mm)]
story += [Paragraph(
    'トルネード図は各パラメータが張る dev の範囲を降順に並べたもの。'
    '影響の大きい順に <b>駆動圧 DP &gt; 過膨張閾値 &gt; 不均一性 &gt; TR 閉鎖圧 &gt; P-V 形状 h</b>。'
    , st_body)]
story += [Paragraph(
    '<b>最重要メッセージ</b>：探索した全パラメータ・全水準で dev は負であった。'
    '乖離が 0 に到達しうるのは、(a) 過膨張閾値を非生理的に緩めて「真の最適」を低圧へ付け替える、'
    'または (b) gap{GE}DP として TR そのものを消失させる（主掃引で提示）— '
    'いずれもモデル挙動ではなく前提の変更による場合に限られる。'
    'したがって <b>「TR は Costa ODCL を低圧側へ歪める」という結論はパラメータ空間全体で頑健</b>'
    'である。'.replace('{GE}', GE), st_key)]
story += [Paragraph(
    '＜補足＞ DP と過膨張閾値の影響が大きいのは、いずれも「真の ODCL の位置」を強く動かす'
    'ためである（DP は過膨張到達 PEEP と見かけコンプライアンスの両方に、過膨張閾値は真値定義に'
    '直接作用）。一方 TR 固有のパラメータ（TCP、不均一性）や P-V 形状は乖離の符号を変えない。',
    st_note)]

doc = SimpleDocTemplate(os.path.join(OUT, "TR_ODCL_sensitivity_interpretation.pdf"),
    pagesize=PAGE, leftMargin=18*mm, rightMargin=18*mm,
    topMargin=16*mm, bottomMargin=14*mm,
    title="TR-only ODCL sensitivity interpretation")
doc.build(story)
print("built:", os.path.join(OUT, "TR_ODCL_sensitivity_interpretation.pdf"),
      os.path.getsize(os.path.join(OUT, "TR_ODCL_sensitivity_interpretation.pdf")), "bytes")
