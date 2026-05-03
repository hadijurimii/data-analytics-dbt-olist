from __future__ import annotations

from pathlib import Path
import math
import textwrap
from typing import Iterable

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "infographics"
SLIDES = OUT / "slides"
OUT.mkdir(exist_ok=True)
SLIDES.mkdir(exist_ok=True)

W, H = 1600, 1000
BG = "#f6f2e8"
PAPER = "#fffaf0"
INK = "#18212f"
MUTED = "#5e6a78"
LINE = "#c9c0b2"
BLUE = "#1d4ed8"
TEAL = "#0f766e"
PURPLE = "#6d28d9"
ORANGE = "#b45309"
GREEN = "#047857"
RED = "#b91c1c"
SLATE = "#334155"
YELLOW = "#ca8a04"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(size: int, bold: bool = False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    except Exception:
        return ImageFont.load_default()

F_TITLE = font(48, True)
F_SUB = font(24)
F_H = font(31, True)
F_BOX = font(25, True)
F_TXT = font(21)
F_SMALL = font(17)
F_TINY = font(14)
F_NUM = font(34, True)


def canvas(title: str, subtitle: str = "", size=(W, H)):
    img = Image.new("RGB", size, BG)
    d = ImageDraw.Draw(img)
    d.text((64, 44), title, fill=INK, font=F_TITLE)
    if subtitle:
        d.text((66, 104), subtitle, fill=MUTED, font=F_SUB)
    return img, d


def footer(d: ImageDraw.ImageDraw, text: str, size=(W, H)):
    d.text((64, size[1] - 44), text, fill=MUTED, font=F_SMALL)


def wrap_lines(text: str, width: int) -> list[str]:
    out: list[str] = []
    for para in str(text).split("\n"):
        out.extend(textwrap.wrap(para, width=width) or [""])
    return out


def card(d, xy, title, bullets: Iterable[str], color=BLUE, w=440, h=220, number=None):
    x, y = xy
    d.rounded_rectangle((x+7, y+9, x+w+7, y+h+9), 22, fill="#ded6ca")
    d.rounded_rectangle((x, y, x+w, y+h), 22, fill="white", outline=LINE, width=2)
    if number is not None:
        d.ellipse((x+22, y+22, x+74, y+74), fill=color)
        d.text((x+38, y+30), str(number), fill="white", font=font(27, True))
        tx = x + 90
    else:
        tx = x + 24
    d.text((tx, y+24), title, fill=color, font=F_BOX)
    yy = y + 85
    for b in bullets:
        lines = wrap_lines(b, 41)
        d.text((x+28, yy), "•", fill=color, font=F_TXT)
        for i, line in enumerate(lines[:3]):
            d.text((x+56, yy), line, fill=INK if i == 0 else MUTED, font=F_TXT)
            yy += 27
        yy += 5
    return (x, y, x+w, y+h)


def arrow(d, start, end, color="#87909c", width=5):
    x1, y1 = start; x2, y2 = end
    d.line((x1, y1, x2, y2), fill=color, width=width)
    ang = math.atan2(y2-y1, x2-x1)
    s = 18
    pts = [(x2, y2), (x2-s*math.cos(ang-0.48), y2-s*math.sin(ang-0.48)), (x2-s*math.cos(ang+0.48), y2-s*math.sin(ang+0.48))]
    d.polygon(pts, fill=color)


def save(img, name):
    p = OUT / name
    img.save(p, quality=95)
    return p


def save_slide(img, name):
    p = SLIDES / name
    img.save(p, quality=95)
    return p


def money(v):
    return f"R${v/1000:.1f}k"

# Load outputs
q1 = pd.read_csv(ROOT / "output/q1_top_monthly_category_gmv.csv")
q1a = pd.read_csv(ROOT / "output/q1_anomaly_months.csv")
q2 = pd.read_csv(ROOT / "output/q2_best_repeat_states.csv")
q3 = pd.read_csv(ROOT / "output/q3_delivery_review_segments.csv")
q4 = pd.read_csv(ROOT / "output/q4_payment_mix.csv")
q5 = pd.read_csv(ROOT / "output/q5_customer_ltv_state.csv")

created = []

# 01 detailed phase map
img, d = canvas("01. Whole Project Phase Map", "The end-to-end answer: reproducible data pipeline + interview-ready analytics outputs")
cols = [(80, 220, BLUE, "Acquire", ["Olist CSVs in data/raw", "BR public holidays", "Raw files gitignored"]),
        (380, 220, TEAL, "Ingest", ["Python loader", "10 raw DuckDB tables", "Idempotent local run"]),
        (680, 220, PURPLE, "Model", ["dbt staging", "intermediate facts", "marts for questions"]),
        (980, 220, ORANGE, "Analyze", ["Revenue seasonality", "Cohorts + retention", "Delivery/review risk"]),
        (1280, 220, GREEN, "Package", ["CSV outputs", "report.md", "Docker + Prefect"])]
prev = None
for i,(x,y,c,t,b) in enumerate(cols, 1):
    card(d, (x,y), t, b, c, 240, 260, i)
    if prev: arrow(d, (prev+240, y+130), (x-18, y+130))
    prev = x
card(d, (110, 610), "What this proves", ["Not just queries: this is a hand-offable analytics system.", "Clear raw/staging/intermediate/mart layers make the logic defensible.", "Tests and Docker make it repeatable for another reviewer."], BLUE, 620, 250)
card(d, (870, 610), "What the data says", ["GMV spikes need campaign/category investigation, not lazy holiday assumptions.", "Retention is low overall, with better pockets in ES, MT, SP and RJ.", "Late cross-state delivery is the clearest review-score pain point."], GREEN, 620, 250)
footer(d, "Use this as the first visual when explaining the project to a non-technical interviewer.")
created.append(save(img, "01_whole_project_phase_map.png"))

# 02 architecture/data lineage
img, d = canvas("02. Architecture + Data Lineage", "From source systems to marts, outputs, and demo material")
lanes = [
    (120, 220, "Sources", BLUE, ["Olist CSVs", "Nager.Date holidays", "Static fallback"]),
    (430, 220, "Storage", TEAL, ["DuckDB file", "raw schema", "local warehouse"]),
    (740, 220, "dbt Transform", PURPLE, ["staging", "intermediate", "marts"]),
    (1050, 220, "Outputs", ORANGE, ["7 answer CSVs", "report.md", "summary.md"]),
    (1360, 220, "Run Layer", GREEN, ["Prefect flow", "Docker Compose", "pytest + dbt tests"]),
]
for i,(x,y,t,c,b) in enumerate(lanes):
    card(d, (x,y), t, b, c, 230, 250)
    if i: arrow(d, (x-70, y+125), (x-18, y+125))
# data contracts
card(d, (180, 610), "Design decision", ["Small stack, production-shaped: raw -> staging -> intermediate -> marts.", "Business questions are exported as files so reviewers can inspect answers without opening DuckDB."], SLATE, 520, 230)
card(d, (900, 610), "Why DuckDB + dbt", ["DuckDB keeps the technical test local and fast.", "dbt makes assumptions visible, testable, and easy to defend during the interview."], SLATE, 520, 230)
footer(d, "Best for technical reviewers who ask: how does the system actually work?")
created.append(save(img, "02_architecture_data_lineage.png"))

# 03 dbt layer explanation
img, d = canvas("03. dbt Model Layers Explained", "A newbie-friendly view of why the warehouse is split into layers")
ys = [230, 430, 630]
labels = [("Staging", BLUE, "Clean and normalize raw tables", ["Rename fields", "Cast dates/numbers", "Keep one model per source"]),
          ("Intermediate", PURPLE, "Create reusable business facts", ["Delivered orders", "Order items + products", "Customer order sequence"]),
          ("Marts", GREEN, "Answer stakeholder questions", ["Revenue seasonality", "Cohorts/repeat", "Delivery/review, payment, LTV"])]
for i,(t,c,sub,b) in enumerate(labels):
    x,y = 130,ys[i]
    d.rounded_rectangle((x,y,x+1340,y+135), 26, fill="white", outline=LINE, width=2)
    d.rounded_rectangle((x,y,x+270,y+135), 26, fill=c)
    d.text((x+42,y+45), t, fill="white", font=F_H)
    d.text((x+320,y+28), sub, fill=c, font=F_BOX)
    bx = x+320
    for j,item in enumerate(b):
        d.text((bx+j*310,y+80), f"• {item}", fill=INK, font=F_TXT)
    if i < 2: arrow(d, (800, y+145), (800, ys[i+1]-18), width=6)
footer(d, "Explain this as: staging is spelling/typing, intermediate is reusable logic, marts are answers.")
created.append(save(img, "03_dbt_layers_newbie_explainer.png"))

# 04 business question map
img, d = canvas("04. Business Questions -> Data Products", "Each requirement becomes a mart and a generated answer file")
items = [
    ("Q1", "Revenue + seasonality", "monthly category GMV, YoY, anomalies, holiday share", "q1_top_monthly_category_gmv.csv", BLUE),
    ("Q2", "Customer cohorts", "first purchase state/month + 90-day repeat", "q2_best_repeat_states.csv", PURPLE),
    ("Q3", "Delivery vs review", "late/on-time + same/cross-state + category", "q3_delivery_review_segments.csv", RED),
    ("Extra", "Payment mix", "payment type value, orders, installments", "q4_payment_mix.csv", ORANGE),
    ("Extra", "Customer value", "avg/median/total GMV by state + repeat share", "q5_customer_ltv_state.csv", GREEN),
]
y=205
for i,(q,t,logic,file,c) in enumerate(items):
    d.rounded_rectangle((115,y,1485,y+120), 22, fill="white", outline=LINE, width=2)
    d.rounded_rectangle((115,y,245,y+120), 22, fill=c)
    d.text((143,y+40), q, fill="white", font=F_BOX)
    d.text((280,y+24), t, fill=c, font=F_H)
    d.text((280,y+70), logic, fill=INK, font=F_TXT)
    d.rounded_rectangle((1020,y+32,1450,y+88), 14, fill="#f1f5f9", outline="#cbd5e1")
    d.text((1045,y+49), file, fill=SLATE, font=F_SMALL)
    y += 142
footer(d, "Useful for interviewers: it shows every business question has a concrete output artifact.")
created.append(save(img, "04_business_questions_to_outputs.png"))

# 05 revenue top categories horizontal bar
img, d = canvas("05. Revenue Seasonality: Top Monthly Category GMV", "Top 12 category-months from the generated Q1 output")
top = q1.head(12).copy()
maxv = top.gmv.max()
x0,y0 = 430,210
barw = 880
for i,row in top.iterrows():
    yy = y0 + i*54
    label = f"{row['order_month'][:7]}  {row['product_category']}"
    d.text((80, yy+8), label, fill=INK, font=F_SMALL)
    w = int(barw * row.gmv/maxv)
    col = GREEN if row.product_category == 'health_beauty' else BLUE if row.product_category == 'watches_gifts' else ORANGE if row.is_anomaly_month else SLATE
    d.rounded_rectangle((x0, yy, x0+w, yy+34), 9, fill=col)
    d.text((x0+w+14, yy+6), money(row.gmv), fill=INK, font=F_SMALL)
card(d, (1080, 650), "Reading", ["watches_gifts and health_beauty dominate the top months.", "computers_accessories Feb 2018 is flagged as an anomaly, not just a large month."], GREEN, 420, 210)
footer(d, "GMV = product item price total, not including freight unless stated in source logic.")
created.append(save(img, "05_top_monthly_category_gmv.png"))

# 06 anomalies vs holiday share
img, d = canvas("06. Anomaly Months vs Holiday Share", "Spikes are real, but holidays usually are not enough to explain them")
plot = (120, 190, 1120, 820)
xmin,xmax = 0, max(q1a.holiday_gmv_share_pct.max(), 10)
ymin,ymax = 2.8, max(q1a.anomaly_z_score.max(),4)
d.rectangle(plot, fill="white", outline=LINE, width=2)
# axes
for t in range(0, int(xmax)+1, 2):
    x = plot[0] + (t-xmin)/(xmax-xmin)*(plot[2]-plot[0])
    d.line((x,plot[3],x,plot[3]+8), fill=MUTED)
    d.text((x-10,plot[3]+14), str(t), fill=MUTED, font=F_TINY)
for t in [3.0,3.2,3.4,3.6,3.8]:
    y = plot[3] - (t-ymin)/(ymax-ymin)*(plot[3]-plot[1])
    d.line((plot[0]-8,y,plot[0],y), fill=MUTED)
    d.text((plot[0]-48,y-8), f"{t:.1f}", fill=MUTED, font=F_TINY)
for _,r in q1a.head(25).iterrows():
    x = plot[0] + (r.holiday_gmv_share_pct-xmin)/(xmax-xmin)*(plot[2]-plot[0])
    y = plot[3] - (r.anomaly_z_score-ymin)/(ymax-ymin)*(plot[3]-plot[1])
    size = max(8, min(26, math.sqrt(r.gmv)/5))
    d.ellipse((x-size,y-size,x+size,y+size), fill=ORANGE if r.holiday_gmv_share_pct>5 else BLUE, outline="white", width=2)
# labels top 3
for _,r in q1a.head(3).iterrows():
    x = plot[0] + (r.holiday_gmv_share_pct-xmin)/(xmax-xmin)*(plot[2]-plot[0])
    y = plot[3] - (r.anomaly_z_score-ymin)/(ymax-ymin)*(plot[3]-plot[1])
    d.text((x+16,y-8), str(r.product_category)[:20], fill=INK, font=F_TINY)
d.text((470, 875), "Holiday GMV share %", fill=MUTED, font=F_SMALL)
d.text((22, 470), "Anomaly z-score", fill=MUTED, font=F_SMALL)
card(d, (1190, 270), "Main insight", ["Several anomalies have near-zero holiday-day GMV share.", "Do not overclaim causality. Holidays are context, not proof.", "Next investigation: promotions, supply, seller campaigns, category events."], ORANGE, 330, 310)
footer(d, "Bubble size roughly follows GMV. This is an interviewer-friendly caution against false causal claims.")
created.append(save(img, "06_anomalies_vs_holiday_share.png"))

# 07 retention by state
img, d = canvas("07. Customer Retention by State", "90-day repeat purchase rate is low overall, so the insight is about pockets of relative strength")
top = q2.head(15)
maxr = top.repeat_rate_90d_pct.max()
for i,r in top.iterrows():
    y = 200 + i*45
    d.text((90,y+7), r.customer_state, fill=INK, font=F_BOX)
    d.text((160,y+9), f"{int(r.customers):,} customers", fill=MUTED, font=F_SMALL)
    w = int(860*r.repeat_rate_90d_pct/maxr)
    col = GREEN if i<5 else BLUE
    d.rounded_rectangle((390,y,390+w,y+30), 9, fill=col)
    d.text((1270,y+5), f"{r.repeat_rate_90d_pct:.2f}%", fill=INK, font=F_SMALL)
card(d, (900, 730), "Story", ["Even best states are below 2% repeat within 90 days.", "Pitch this as retention opportunity, not retention success.", "Compare strong states to weak states to find category or delivery differences."], BLUE, 560, 210)
footer(d, "Best high-volume states in this slice: ES, MT, SP, GO, RJ.")
created.append(save(img, "07_repeat_rate_by_state.png"))

# 08 delivery review risk matrix
img, d = canvas("08. Delivery/Review Risk Matrix", "Where operational pain is most visible: late + cross-state + low review")
plot=(110,190,1120,820)
d.rectangle(plot, fill="white", outline=LINE, width=2)
# axes labels
for score in [2.0,2.5,3.0,3.5,4.0]:
    x = plot[0] + (score-2.0)/(4.2-2.0)*(plot[2]-plot[0])
    d.line((x,plot[3],x,plot[3]+8), fill=MUTED)
    d.text((x-12,plot[3]+14), str(score), fill=MUTED, font=F_TINY)
for late in [0,5,10,15]:
    y = plot[3] - (late-0)/(16-0)*(plot[3]-plot[1])
    d.line((plot[0]-8,y,plot[0],y), fill=MUTED)
    d.text((plot[0]-42,y-8), str(late), fill=MUTED, font=F_TINY)
for _,r in q3.iterrows():
    x = plot[0] + (r.avg_review_score-2.0)/(4.2-2.0)*(plot[2]-plot[0])
    y = plot[3] - (max(0,r.avg_days_late)-0)/(16-0)*(plot[3]-plot[1])
    size = max(10, min(36, math.sqrt(r.orders)*1.1))
    col = RED if r.delivery_status == 'late_or_unknown' and r.shipment_scope == 'cross_state' else GREEN if r.delivery_status == 'on_time' else ORANGE
    d.ellipse((x-size,y-size,x+size,y+size), fill=col, outline="white", width=2)
for _,r in q3.head(8).iterrows():
    x = plot[0] + (r.avg_review_score-2.0)/(4.2-2.0)*(plot[2]-plot[0])
    y = plot[3] - (max(0,r.avg_days_late)-0)/(16-0)*(plot[3]-plot[1])
    d.text((x+14,y-9), str(r.product_category)[:16], fill=INK, font=F_TINY)
d.text((470, 875), "Average review score", fill=MUTED, font=F_SMALL)
d.text((18, 470), "Average days late", fill=MUTED, font=F_SMALL)
card(d, (1190, 255), "Priority queue", ["Fix the upper-left cluster first: late, many days late, low score.", "Top risk categories include stationery, toys, baby, sports/leisure, bed/bath/table, health/beauty."], RED, 330, 270)
footer(d, "Bubble size follows order count. Lower score + higher lateness = higher operational risk.")
created.append(save(img, "08_delivery_review_risk_matrix.png"))

# 09 payment mix
img, d = canvas("09. Payment Mix", "Most value and orders run through credit card, with boleto as the clear second lane")
total = q4.payment_value.sum()
cx,cy,r=470,520,235
start=-90
colors=[BLUE,ORANGE,GREEN,PURPLE]
for i,row in q4.iterrows():
    extent=360*row.payment_value/total
    d.pieslice((cx-r,cy-r,cx+r,cy+r), start, start+extent, fill=colors[i], outline=BG, width=3)
    start+=extent
d.ellipse((cx-105,cy-105,cx+105,cy+105), fill=BG)
d.text((cx-82,cy-25), "Payment", fill=INK, font=F_H)
d.text((cx-55,cy+18), "value", fill=MUTED, font=F_TXT)
y=245
for i,row in q4.iterrows():
    pct=row.payment_value/total*100
    d.rounded_rectangle((880,y,1430,y+90), 18, fill="white", outline=LINE, width=2)
    d.rectangle((905,y+30,935,y+60), fill=colors[i])
    d.text((955,y+22), row.payment_type, fill=INK, font=F_BOX)
    d.text((1190,y+20), f"{pct:.1f}% value", fill=colors[i], font=F_BOX)
    d.text((955,y+55), f"{int(row.orders):,} orders • avg installments {row.avg_installments:.2f}", fill=MUTED, font=F_SMALL)
    y += 115
footer(d, "Business angle: payment type is a product/finance dimension, not just a technical aggregation.")
created.append(save(img, "09_payment_mix_donut.png"))

# 10 customer value state scatter/bubbles
img, d = canvas("10. Customer Value by State", "Average GMV and repeat share highlight where customers look more valuable")
plot=(110,190,1120,820)
d.rectangle(plot, fill="white", outline=LINE, width=2)
xmin,xmax = 80, max(q5.avg_customer_gmv)+20
ymin,ymax = 1.4, max(q5.repeat_customer_share_pct)+0.3
for xval in [100,140,180,220]:
    x=plot[0]+(xval-xmin)/(xmax-xmin)*(plot[2]-plot[0])
    d.line((x,plot[3],x,plot[3]+8),fill=MUTED)
    d.text((x-20,plot[3]+14),str(xval),fill=MUTED,font=F_TINY)
for yval in [1.5,2.0,2.5,3.0,3.5]:
    y=plot[3]-(yval-ymin)/(ymax-ymin)*(plot[3]-plot[1])
    d.line((plot[0]-8,y,plot[0],y),fill=MUTED)
    d.text((plot[0]-45,y-8),str(yval),fill=MUTED,font=F_TINY)
for _,r in q5.iterrows():
    x=plot[0]+(r.avg_customer_gmv-xmin)/(xmax-xmin)*(plot[2]-plot[0])
    y=plot[3]-(r.repeat_customer_share_pct-ymin)/(ymax-ymin)*(plot[3]-plot[1])
    size=max(12,min(45,math.sqrt(r.customers)/4))
    col=GREEN if r.avg_customer_gmv>160 else BLUE
    d.ellipse((x-size,y-size,x+size,y+size),fill=col,outline="white",width=2)
    d.text((x+size+4,y-8),r.customer_state,fill=INK,font=F_TINY)
d.text((450,875),"Average customer GMV (R$)",fill=MUTED,font=F_SMALL)
d.text((14,470),"Repeat customer share %",fill=MUTED,font=F_SMALL)
card(d, (1190, 280), "Read this", ["PB has the highest average GMV but lower total scale.", "MT combines decent average value with stronger repeat share.", "SP/RJ/MG matter for scale even if average GMV is not top."], GREEN, 330, 300)
footer(d, "Bubble size follows customer count. This helps avoid confusing high average value with market scale.")
created.append(save(img, "10_customer_value_state_bubbles.png"))

# 11 interviewer narrative
img, d = canvas("11. Interview Storyboard", "A clean 90-second explanation of the project")
steps=[("Problem", "Turn messy marketplace CSVs into business answers."),
       ("Approach", "Build a local mini-warehouse with DuckDB and dbt."),
       ("Enrichment", "Add Brazilian holidays, but avoid weak causality claims."),
       ("Outputs", "Export answer CSVs and a report, not only hidden SQL."),
       ("Quality", "Run dbt tests, pytest, Prefect, and Docker Compose."),
       ("Insight", "Focus on GMV drivers, retention pockets, and delivery pain.")]
for i,(t,b) in enumerate(steps):
    x=110+(i%3)*490; y=220+(i//3)*300
    card(d,(x,y),t,[b], [BLUE,TEAL,PURPLE,ORANGE,SLATE,GREEN][i], 400, 210, i+1)
    if i in [0,1,3,4]: arrow(d,(x+400,y+105),(x+468,y+105))
    if i==2: arrow(d,(x+200,y+220),(x+200, y+280))
footer(d, "This is the high-level talk track when an interviewer says: walk me through your project.")
created.append(save(img, "11_interviewer_storyboard.png"))

# 12 quality and reproducibility checklist
img, d = canvas("12. Quality + Reproducibility Proof", "Evidence that this is more than an exploratory notebook")
checks=[("10", "raw tables loaded", BLUE), ("18", "dbt models built", PURPLE), ("19", "dbt tests passed", GREEN), ("2", "pytest tests passed", GREEN), ("1", "Prefect entrypoint", ORANGE), ("1", "Docker Compose runner", SLATE)]
for i,(num,lab,c) in enumerate(checks):
    x=120+(i%3)*480; y=220+(i//2 if False else i//3)*260
    d.rounded_rectangle((x+8,y+9,x+390,y+210),28,fill="#ded6ca")
    d.rounded_rectangle((x,y,x+390,y+200),28,fill="white",outline=LINE,width=2)
    d.text((x+38,y+35),num,fill=c,font=font(66,True))
    for j,l in enumerate(wrap_lines(lab,22)):
        d.text((x+38,y+120+j*27),l,fill=INK,font=F_BOX if j==0 else F_TXT)
card(d,(280,760),"Defence line",["I optimized for a stack that a reviewer can run, inspect, and challenge live.","The point is not maximum complexity. The point is reproducible, layered, business-facing analytics."],GREEN,1040,160)
footer(d,"Use when defending technical choices and hand-off readiness.")
created.append(save(img,"12_quality_reproducibility_scorecard.png"))

# 13 newbie glossary
img,d=canvas("13. Newbie Glossary", "Plain-English meanings for the stack pieces")
gloss=[("DuckDB","A local analytics database in one file."),("dbt","SQL transformation framework with tests and docs."),("Staging","Clean copy of raw data with proper types and names."),("Intermediate","Reusable business facts before final reports."),("Mart","A ready-to-use table answering a business question."),("Prefect","Orchestrates the run order like a pipeline conductor."),("Docker Compose","Runs the project in a repeatable container setup."),("GMV","Gross merchandise value, here product item sales value.")]
for i,(t,b) in enumerate(gloss):
    x=100+(i%2)*730; y=200+(i//2)*165
    d.rounded_rectangle((x,y,x+630,y+115),18,fill="white",outline=LINE,width=2)
    d.text((x+26,y+20),t,fill=[BLUE,TEAL,PURPLE,ORANGE,GREEN,RED,SLATE,YELLOW][i],font=F_BOX)
    d.text((x+26,y+60),b,fill=INK,font=F_TXT)
footer(d,"Good for someone new to modern analytics engineering.")
created.append(save(img,"13_newbie_glossary.png"))

# 14 recommendations roadmap
img,d=canvas("14. What To Do With The Insights", "Turn the analysis into practical next actions")
actions=[("GMV spikes", "Investigate promotions, category campaigns, seller availability, and stock events.", BLUE),
         ("Retention", "Study ES/MT/SP/RJ baskets and delivery experience, then design state/category-specific retention plays.", PURPLE),
         ("Delivery pain", "Attack late cross-state categories first, because review-score damage is clearest there.", RED),
         ("Payment", "Use credit-card dominance and boleto share in checkout/payment product planning.", ORANGE),
         ("Market value", "Separate average-value states from scale states before allocating marketing spend.", GREEN)]
y=205
for i,(t,b,c) in enumerate(actions,1):
    d.rounded_rectangle((130,y,1470,y+118),22,fill="white",outline=LINE,width=2)
    d.ellipse((160,y+29,220,y+89),fill=c)
    d.text((181,y+43),str(i),fill="white",font=F_BOX)
    d.text((250,y+23),t,fill=c,font=F_H)
    d.text((250,y+70),b,fill=INK,font=F_TXT)
    y+=138
footer(d,"This turns the data work into business recommendations, which is what interviewers usually care about.")
created.append(save(img,"14_insight_to_action_roadmap.png"))

# Slides, 16:9
SW,SH=1600,900
def slide(title, subtitle, body, name, color=BLUE):
    im=Image.new("RGB",(SW,SH),BG); dr=ImageDraw.Draw(im)
    dr.rounded_rectangle((70,70,1530,830),36,fill="white",outline=LINE,width=2)
    dr.rectangle((70,70,1530,190),fill=color)
    dr.text((115,105),title,fill="white",font=font(50,True))
    dr.text((115,215),subtitle,fill=color,font=F_H)
    yy=295
    for b in body:
        dr.text((135,yy),"•",fill=color,font=F_H)
        for l in wrap_lines(b,78):
            dr.text((175,yy+3),l,fill=INK,font=F_TXT)
            yy+=33
        yy+=20
    dr.text((115,795),"Lance Data Olist Analytics",fill=MUTED,font=F_SMALL)
    save_slide(im,name)

slide("01 / Executive Summary","What was built",[
    "A local analytics stack for Olist marketplace data using Python, DuckDB, dbt, Prefect, and Docker Compose.",
    "It answers revenue, retention, delivery/review, payment, and customer value questions with exported CSVs and a report.",
    "The project is deliberately small but production-shaped: layered, tested, reproducible, and explainable."
],"slide_01_executive_summary.png",BLUE)
slide("02 / Architecture","How the system runs",[
    "Raw Olist CSVs and Brazilian holidays flow into a DuckDB warehouse.",
    "dbt creates staging, intermediate, and mart layers.",
    "Prefect runs ingestion, dbt, tests, and export in one command. Docker Compose provides repeatable execution."
],"slide_02_architecture.png",TEAL)
slide("03 / Revenue Insight","What drove top GMV months",[
    "watches_gifts and health_beauty dominate the strongest monthly category GMV rows.",
    "computers_accessories in Feb 2018 is a notable anomaly with strong YoY growth.",
    "Holiday share is useful context, but not enough evidence to claim holiday causality for most spikes."
],"slide_03_revenue_insight.png",GREEN)
slide("04 / Retention Insight","What cohorts show",[
    "90-day repeat purchase rates are low overall, so the opportunity is retention improvement.",
    "ES, MT, SP, GO, and RJ are relatively stronger states in the generated output.",
    "Next analysis should compare category mix, delivery experience, and campaign exposure by state."
],"slide_04_retention_insight.png",PURPLE)
slide("05 / Delivery Insight","Where reviews suffer",[
    "Late or unknown cross-state delivery segments have the weakest review scores.",
    "Priority categories include stationery, toys, baby, sports/leisure, bed/bath/table, and health/beauty.",
    "This is the strongest operational recommendation because lateness and review damage line up clearly."
],"slide_05_delivery_insight.png",RED)
slide("06 / Payment + Value","Extra stakeholder answers",[
    "Credit card dominates order count and payment value, with boleto as the second lane.",
    "State value analysis separates high average GMV states from high scale states.",
    "This gives finance, product, and marketing useful follow-up paths beyond the core questions."
],"slide_06_payment_value.png",ORANGE)
slide("07 / Quality Proof","Why the project is defensible",[
    "10 raw tables loaded, 18 dbt models built, 19 dbt tests passed, and 2 pytest tests passed.",
    "The pipeline completed through Prefect and Docker Compose.",
    "Assumptions and business interpretation are documented in report.md and supporting docs."
],"slide_07_quality_proof.png",SLATE)
slide("08 / Closing Recommendation","How to explain the value",[
    "Do not sell it as a huge stack. Sell it as a reproducible client-handoff analytics system.",
    "The best commercial story: investigate GMV spikes properly, improve retention pockets, and fix late cross-state delivery pain.",
    "The best technical story: clean layering, tests, orchestration, and repeatable local execution."
],"slide_08_closing_recommendation.png",GREEN)

# Contact sheet
imgs = [Path(p) for p in created]
thumb_w, thumb_h = 360, 225
sheet = Image.new("RGB", (1600, 1320), BG)
sd = ImageDraw.Draw(sheet)
sd.text((55,35), "Infographics Contact Sheet", fill=INK, font=F_TITLE)
sd.text((57,92), "Generated PNGs for newbie explanation, interviewer defence, and business insight discussion", fill=MUTED, font=F_SUB)
for idx,p in enumerate(imgs):
    im=Image.open(p).resize((thumb_w,thumb_h))
    x=55+(idx%4)*385; y=160+(idx//4)*285
    sheet.paste(im,(x,y))
    sd.text((x,y+thumb_h+10),p.name.replace('_',' ')[:42],fill=INK,font=F_TINY)
sheet.save(OUT/"00_contact_sheet.png",quality=95)

print("Generated:")
for p in [OUT/"00_contact_sheet.png", *created, *sorted(SLIDES.glob('*.png'))]:
    print(p.relative_to(ROOT))
