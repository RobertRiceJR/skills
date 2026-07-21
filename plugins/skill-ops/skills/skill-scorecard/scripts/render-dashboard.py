#!/usr/bin/env python3
"""Historical dashboard for skill-scorecard. Reads every reference/data/*-run.json
and renders a standalone (no-CDN, inline-SVG) dashboard.html with four views:
disposition trend, axis drift, per-skill trajectory (sparklines + deltas), churn.
Gracefully degrades to a baseline view when only one run exists.
Usage: render-dashboard.py [skills_root]
"""
import json,os,sys,glob
ROOT=sys.argv[1] if len(sys.argv)>1 else os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
SK=os.path.join(ROOT,"skill-scorecard");DATA=os.path.join(SK,"reference","data")
# legitimate runs are those registered in runs.jsonl (guards against stray/test data files)
valid=set()
rj=os.path.join(SK,"runs.jsonl")
if os.path.exists(rj):
    for line in open(rj):
        line=line.strip()
        if line:
            try:valid.add(json.loads(line)["date"])
            except Exception:pass
runs=[]
for f in sorted(glob.glob(os.path.join(DATA,"*-run.json"))):
    r=json.load(open(f))
    if (not valid) or r["meta"]["date"] in valid:
        runs.append(r)
runs.sort(key=lambda r:r["meta"]["date"])
dates=[r["meta"]["date"] for r in runs]
DISPS=["Invest","Maintain","Harden","Simplify","Retire/Review"]
DC={"Invest":"#2c6e9b","Maintain":"#4f9d3a","Harden":"#e08a3e","Simplify":"#c2641f","Retire/Review":"#b5261c"}
AX={"V":"#4f9d3a","S":"#2c6e9b","M":"#e08a3e","MAT":"#5b6472"}
AXL={"V":"Value","S":"Sustainability","M":"Maintainability","MAT":"Maturity"}
latest=runs[-1];prev=runs[-2] if len(runs)>1 else None

def linechart(series,ymin,ymax,ylab,W=860,H=280):
    padL,padR,padT,padB=46,18,18,34;pw=W-padL-padR;ph=H-padT-padB
    n=len(dates)
    def xpos(i):return padL+(pw/2 if n==1 else pw*i/(n-1))
    def ypos(v):return padT+ph*(1-(v-ymin)/(ymax-ymin if ymax>ymin else 1))
    s=[f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" style="max-width:{W}px">']
    # gridlines + y labels
    steps=5
    for k in range(steps+1):
        v=ymin+(ymax-ymin)*k/steps;y=ypos(v)
        s.append(f'<line x1="{padL}" y1="{y:.1f}" x2="{W-padR}" y2="{y:.1f}" stroke="#eef0ee"/>')
        s.append(f'<text x="{padL-6}" y="{y+3:.1f}" font-size="10" fill="#5b6472" text-anchor="end">{v:.0f}</text>')
    # x labels
    for i,dt in enumerate(dates):
        x=xpos(i)
        s.append(f'<text x="{x:.1f}" y="{H-12}" font-size="10" fill="#5b6472" text-anchor="middle">{dt[5:]}</text>')
    # series
    for label,color,vals in series:
        pts=[(xpos(i),ypos(v)) for i,v in enumerate(vals) if v is not None]
        if len(pts)>1:
            s.append('<polyline fill="none" stroke="%s" stroke-width="2.2" points="%s"/>'%(color," ".join(f"{x:.1f},{y:.1f}" for x,y in pts)))
        for x,y in pts:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{color}"/>')
    s.append(f'<text x="{padL}" y="12" font-size="10" fill="#5b6472">{ylab}</text>')
    s.append('</svg>')
    # legend
    leg='<div class="leg">'+''.join(f'<span><i style="background:{c}"></i>{l}</span>' for l,c,_ in series)+'</div>'
    return ''.join(s)+leg

def sparkline(vals,ymin,ymax,w=86,h=22):
    pts=[v for v in vals if v is not None]
    if not pts:return ''
    n=len(vals)
    def xp(i):return (w-4)*(0 if n==1 else i/(n-1))+2
    def yp(v):return h-2-(h-4)*((v-ymin)/(ymax-ymin if ymax>ymin else 1))
    P=[(xp(i),yp(v)) for i,v in enumerate(vals) if v is not None]
    s=[f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    if len(P)>1:s.append('<polyline fill="none" stroke="#2c6e9b" stroke-width="1.6" points="%s"/>'%" ".join(f"{x:.1f},{y:.1f}" for x,y in P))
    lx,ly=P[-1];s.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.4" fill="#1b1f1d"/>')
    s.append('</svg>');return ''.join(s)

# ---- build views ----
# disposition trend
disp_series=[(d,DC[d],[r["meta"]["disp"].get(d,0) for r in runs]) for d in DISPS]
maxc=max([max(s[2]) for s in disp_series]+[1])
disp_svg=linechart(disp_series,0,maxc+1,"skills")
# axis drift
ax_series=[(AXL[a],AX[a],[r["meta"]["avg"][a] for r in runs]) for a in ("V","S","M","MAT")]
ax_svg=linechart(ax_series,1,5,"avg 1-5")
# per-skill trajectory
byname={}
for r in runs:
    for row in r["rows"]:byname.setdefault(row["name"],{})[r["meta"]["date"]]=row
allnames=sorted(byname,key=lambda nm:-(byname[nm].get(dates[-1],{}).get("comp",0)))
traj_rows=[]
for nm in allnames:
    seq=[byname[nm].get(dt,{}).get("comp") for dt in dates]
    cur=byname[nm].get(dates[-1])
    if not cur:continue
    prevc=byname[nm].get(dates[-2],{}).get("comp") if prev else None
    if prevc is None:delta='<span class="dl flat">—</span>'
    else:
        dv=cur["comp"]-prevc
        delta=(f'<span class="dl up">▲ {dv}</span>' if dv>0 else f'<span class="dl dn">▼ {abs(dv)}</span>' if dv<0 else '<span class="dl flat">= 0</span>')
    dcss={"Invest":"d-invest","Maintain":"d-maintain","Harden":"d-harden","Simplify":"d-simplify","Retire/Review":"d-retire"}[cur["disp"]]
    traj_rows.append(f'<tr><td><code>{nm}</code> <span class="tt">{cur["typeName"][:-1] if cur["typeName"].endswith("s") else cur["typeName"]}</span></td>'
        f'<td><span class="badge {dcss}">{cur["disp"]}</span></td>'
        f'<td class="num"><b>{cur["comp"]}</b></td>'
        f'<td class="num">{delta}</td>'
        f'<td>{sparkline(seq,40,90)}</td></tr>')
traj_html="".join(traj_rows)
# churn
if prev:
    a=set(byname[nm].get(dates[-1]) is not None for nm in byname)  # placeholder
    cur_names={row["name"] for row in latest["rows"]};prev_names={row["name"] for row in prev["rows"]}
    new=sorted(cur_names-prev_names);gone=sorted(prev_names-cur_names)
    prowd={row["name"]:row for row in prev["rows"]}
    reclass=[]
    for row in latest["rows"]:
        p=prowd.get(row["name"])
        if p and (p["disp"]!=row["disp"] or p["type"]!=row["type"]):
            ch=[]
            if p["type"]!=row["type"]:ch.append(f'{p["typeName"]}→{row["typeName"]}')
            if p["disp"]!=row["disp"]:ch.append(f'{p["disp"]}→{row["disp"]}')
            reclass.append(f'<li><code>{row["name"]}</code> — {", ".join(ch)}</li>')
    churn=f'<p><b>Since {dates[-2]}:</b></p><ul>'
    churn+=f'<li><b>New ({len(new)}):</b> '+(", ".join(f"<code>{n}</code>" for n in new) or "—")+'</li>'
    churn+=f'<li><b>Removed ({len(gone)}):</b> '+(", ".join(f"<code>{n}</code>" for n in gone) or "—")+'</li>'
    churn+=f'<li><b>Reclassified ({len(reclass)}):</b></li>'+("".join(reclass) if reclass else "<li>—</li>")
    churn+='</ul>'
else:
    churn='<p class="muted">Baseline run — no prior run to diff. Churn (new / removed / reclassified skills) appears after the next run.</p>'

m=latest["meta"]
kpi=f'''<div class="kpi"><div class="n">{m["total"]}</div><div class="l">Skills scored</div></div>
<div class="kpi"><div class="n">{len(runs)}</div><div class="l">Runs on record</div></div>
<div class="kpi"><div class="n">{m["disp"].get("Harden",0)+m["disp"].get("Simplify",0)}</div><div class="l">Need work (Harden+Simplify)</div></div>
<div class="kpi"><div class="n">{m["disp"].get("Retire/Review",0)}</div><div class="l">Retire / Review</div></div>'''

trend_note='' if len(runs)>1 else '<p class="muted">One run on record — lines become trends after the next run. Each future <code>/skill-scorecard</code> run appends a point automatically.</p>'

HTML=r'''<!DOCTYPE html>
<!-- scorecard-dashboard date:__DATE__ runs:__NRUNS__ -->
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill Scorecard — Historical Dashboard</title><style>
:root{--ink:#1b1f1d;--bg:#f7f9f7;--muted:#5b6472;--line:#e4e9e5;--accent:#4f9d3a;--accent-2:#2c6e9b;--accent-3:#e08a3e;--card:#fff;--font:"Inter","Segoe UI",Arial,sans-serif;}
*{box-sizing:border-box;}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--font);}
.wrap{max-width:1080px;margin:0 auto;padding:40px 28px 80px;}
header.report{background:linear-gradient(135deg,var(--ink),var(--accent));color:#fff;border-radius:16px;padding:30px 34px;margin-bottom:22px;box-shadow:0 8px 28px rgba(27,31,29,.18);}
header .eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:11.5px;font-weight:700;opacity:.85;margin:0 0 8px;}
header h1{margin:0 0 6px;font-size:26px;font-weight:750;}header p{margin:0;opacity:.93;font-size:14px;}
h2.section{font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);font-weight:750;margin:30px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--line);}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:4px 0 8px;}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:16px;text-align:center;}
.kpi .n{font-size:30px;font-weight:800;color:var(--accent);line-height:1;}.kpi .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-top:7px;}
.card{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:18px 20px;box-shadow:0 2px 10px rgba(20,25,40,.04);margin-bottom:14px;}
.leg{display:flex;flex-wrap:wrap;gap:14px;margin-top:8px;font-size:12px;color:var(--muted);}
.leg i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;vertical-align:-1px;}
table{width:100%;border-collapse:collapse;font-size:13px;}
thead th{background:#eef1ee;text-align:left;padding:9px 11px;font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:750;border-bottom:1px solid var(--line);}
thead th.num{text-align:center;}tbody td{padding:8px 11px;border-bottom:1px solid #eef0ee;vertical-align:middle;}td.num{text-align:center;}
tbody tr:hover{background:#f6faf4;}code{background:#eef1ee;padding:1px 6px;border-radius:5px;font-size:.9em;}
.tt{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;}
.badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:10.5px;font-weight:750;text-transform:uppercase;}
.d-invest{background:#dbe9f3;color:#1f5781;}.d-maintain{background:#e3f1dc;color:#2f6e1f;}.d-harden{background:#f7ebd9;color:#8a5a14;}.d-simplify{background:#f3e0d0;color:#9a4a12;}.d-retire{background:#f6dcd9;color:#9b2820;}
.dl{font-weight:750;font-size:12px;}.dl.up{color:#2f8f3e;}.dl.dn{color:#b5261c;}.dl.flat{color:#5b6472;}
.muted{color:var(--muted);font-size:13px;}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px;}@media(max-width:820px){.two,.kpis{grid-template-columns:1fr;}}
footer{margin-top:36px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);text-align:center;}
</style></head><body><div class="wrap">
<header class="report"><p class="eyebrow">QE · Skill Scorecard · Historical Dashboard</p>
<h1>Skill Ecosystem — Health Over Time</h1>
<p>Trends across every <code>/skill-scorecard</code> run. Latest: __DATE__ · __NRUNS__ run(s) on record.</p></header>
<div class="kpis">__KPI__</div>
__TRENDNOTE__
<h2 class="section">Disposition trend</h2>
<div class="card">__DISP__</div>
<h2 class="section">Axis drift (ecosystem averages)</h2>
<div class="card">__AXIS__</div>
<h2 class="section">Skill churn</h2>
<div class="card">__CHURN__</div>
<h2 class="section">Per-skill trajectory</h2>
<div class="card"><table><thead><tr><th>Skill</th><th>Disposition</th><th class="num">Standing</th><th class="num">&Delta; vs prev</th><th>History</th></tr></thead><tbody>__TRAJ__</tbody></table></div>
<footer>skill-scorecard historical dashboard · regenerated each run from reference/data/*-run.json · __DATE__</footer>
</div></body></html>'''
HTML=(HTML.replace("__DATE__",dates[-1]).replace("__NRUNS__",str(len(runs)))
  .replace("__KPI__",kpi).replace("__TRENDNOTE__",trend_note)
  .replace("__DISP__",disp_svg).replace("__AXIS__",ax_svg)
  .replace("__CHURN__",churn).replace("__TRAJ__",traj_html))
open(os.path.join(SK,"dashboard.html"),"w").write(HTML)
print("wrote dashboard.html |",len(runs),"run(s) |",len(allnames),"skills tracked")
