# -*- coding: utf-8 -*-
import json,sys,os
date=sys.argv[1] if len(sys.argv)>1 else "2026-06-24"
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
SK=os.path.join(ROOT,"skill-scorecard")
run=json.load(open(os.path.join(SK,"reference","data",date+"-run.json")))
pay=json.dumps(run); meta=run["meta"]; d=meta["disp"]
# greppable header for registry regeneration
HDR="<!-- scorecard-meta\ndate: %s\ntotal: %d\ndisp: %s\nstatus: complete\n-->\n"%(date,meta["total"],json.dumps(d))
TPL=r'''<!DOCTYPE html>
__HDR__
<!-- skills-ecosystem ranking — Value / Sustainability / Maintainability / Maturity+Ceiling, per-type weighted composite + disposition. Companion to TDD-011 reference census. -->
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skills Ecosystem — Sustainability &amp; Value Rankings</title>
<style>
:root{--ink:#1b1f1d;--bg:#f7f9f7;--muted:#5b6472;--line:#e4e9e5;--accent:#4f9d3a;--accent-2:#2c6e9b;--accent-3:#e08a3e;--accent-soft:#eef5ea;--card:#fff;
--p1:#b5261c;--p2:#dd6b3f;--p3:#d4a017;--p4:#5fa345;--p5:#1d7a33;
--font-head:"Inter","Segoe UI",Arial,sans-serif;--font-body:"Inter","Segoe UI",Arial,sans-serif;}
*{box-sizing:border-box;}html{-webkit-print-color-adjust:exact;print-color-adjust:exact;}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--font-body);}
.wrap{max-width:1180px;margin:0 auto;padding:40px 28px 80px;}
header.report{background:linear-gradient(135deg,var(--ink) 0%,var(--accent) 100%);color:#fff;border-radius:16px;padding:34px 36px;margin-bottom:24px;box-shadow:0 8px 28px rgba(27,31,29,.18);}
header.report .eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:11.5px;font-weight:700;opacity:.85;margin:0 0 10px;}
header.report h1{margin:0 0 8px;font-size:29px;line-height:1.15;font-weight:750;font-family:var(--font-head);}
header.report p.sub{margin:0;font-size:15px;opacity:.93;max-width:820px;}
header.report .meta{margin-top:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,.25);display:flex;flex-wrap:wrap;gap:22px;font-size:12.5px;opacity:.93;}
h2.section{font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);font-weight:750;margin:34px 0 14px;padding-bottom:8px;border-bottom:2px solid var(--line);font-family:var(--font-head);}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:4px 0 18px;}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:16px;text-align:center;}
.kpi .n{font-size:30px;font-weight:800;color:var(--accent);font-family:var(--font-head);line-height:1;}
.kpi .l{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-top:7px;}
.callout{background:var(--accent-soft);border:1px solid var(--line);border-left:5px solid var(--accent);border-radius:12px;padding:18px 22px;margin:6px 0 22px;}
.callout .lbl{font-size:11px;text-transform:uppercase;letter-spacing:.12em;font-weight:750;color:var(--accent);margin-bottom:6px;}
.callout p{margin:0;font-size:14.5px;line-height:1.55;}.callout p+p{margin-top:9px;}
.tablecard{background:var(--card);border:1px solid var(--line);border-radius:13px;overflow:hidden;box-shadow:0 2px 10px rgba(20,25,40,.04);margin-bottom:10px;}
table{width:100%;border-collapse:collapse;font-size:13.5px;}
thead th{background:#eef1ee;text-align:left;padding:11px 12px;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:750;border-bottom:1px solid var(--line);white-space:nowrap;cursor:pointer;user-select:none;}
thead th.num{text-align:center;}thead th:hover{color:var(--ink);}
thead th .ar{opacity:.45;font-size:9px;}
tbody td{padding:10px 12px;border-bottom:1px solid #eef0ee;vertical-align:middle;}
tbody tr:last-child td{border-bottom:none;}tbody tr:hover{background:#f6faf4;}
td.num{text-align:center;}
.sk{font-weight:700;font-family:var(--font-head);font-size:13.5px;}
.sk code{background:#eef1ee;padding:1px 6px;border-radius:5px;font-size:.92em;}
.pp{font-size:11.5px;color:var(--muted);margin-top:2px;max-width:430px;line-height:1.35;}
.sig{font-size:10.5px;color:var(--muted);margin-top:3px;}
.sig b{color:var(--ink);font-weight:700;}
.score{display:inline-block;min-width:26px;padding:3px 0;border-radius:6px;font-weight:750;font-size:12.5px;color:#fff;text-align:center;}
.p1{background:var(--p1);}.p2{background:var(--p2);}.p3{background:var(--p3);color:#3a2e00;}.p4{background:var(--p4);}.p5{background:var(--p5);}
.comp{font-weight:800;font-family:var(--font-head);font-size:15px;}
.gapbar{display:inline-flex;gap:2px;}
.seg{width:15px;height:11px;border-radius:2px;display:inline-block;}
.seg.fill{background:var(--accent);}
.seg.head{background:repeating-linear-gradient(45deg,var(--accent-3),var(--accent-3) 2px,#f6e3cf 2px,#f6e3cf 4px);}
.seg.empty{background:var(--line);}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:750;text-transform:uppercase;letter-spacing:.03em;white-space:nowrap;}
.d-invest{background:#dbe9f3;color:#1f5781;}.d-maintain{background:#e3f1dc;color:#2f6e1f;}
.d-harden{background:#f7ebd9;color:#8a5a14;}.d-simplify{background:#f3e0d0;color:#9a4a12;}
.d-retire{background:#f6dcd9;color:#9b2820;}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 14px;}
.controls input{flex:1;min-width:200px;padding:9px 12px;border:1px solid var(--line);border-radius:9px;font:14px var(--font-body);background:var(--card);}
.chip{cursor:pointer;padding:5px 12px;border-radius:20px;font-size:11.5px;font-weight:700;border:1px solid var(--line);background:var(--card);color:var(--muted);user-select:none;}
.chip.on{color:#fff;border-color:transparent;}
.chip.on.c-invest{background:var(--accent-2);}.chip.on.c-maintain{background:var(--accent);}
.chip.on.c-harden{background:var(--accent-3);}.chip.on.c-simplify{background:#c2641f;}.chip.on.c-retire{background:var(--p1);}
.tier{border-left:5px solid var(--accent);border-radius:10px;padding:14px 18px;margin-bottom:12px;background:var(--card);border-top:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line);}
.tier h3{margin:0 0 6px;font-size:14px;font-family:var(--font-head);}
.tier p,.tier li{font-size:13px;color:var(--ink);}.tier ul{margin:6px 0 0;padding-left:18px;}
.legend{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:8px;}
.legend .item{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 15px;}
.legend .item .k{font-weight:750;font-size:12.5px;margin-bottom:3px;}
.legend .item .d{font-size:12px;color:var(--muted);line-height:1.45;}
.wt{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:6px;}
.wt th,.wt td{border:1px solid var(--line);padding:7px 10px;text-align:center;}
.wt th{background:#eef1ee;color:var(--muted);text-transform:uppercase;font-size:10.5px;letter-spacing:.05em;}
.wt td:first-child,.wt th:first-child{text-align:left;}
.secthead{display:flex;align-items:baseline;gap:12px;margin:26px 0 10px;}
.secthead h2{margin:0;font-size:20px;font-family:var(--font-head);}
.secthead .cnt{font-size:12px;color:var(--muted);}
code{background:#eef1ee;padding:1px 6px;border-radius:5px;font-size:.88em;font-family:"SF Mono",Consolas,monospace;}
.note{font-size:12px;color:var(--muted);margin-top:10px;line-height:1.5;}
footer.rep{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);text-align:center;}
@media(max-width:760px){.kpis,.legend{grid-template-columns:1fr;}.pp{max-width:none;}}
</style></head><body><div class="wrap">
<header class="report">
<p class="eyebrow">Technical Due Diligence · QE · Skill Ecosystem Overhaul</p>
<h1>Skills Ecosystem — Sustainability &amp; Value Rankings</h1>
<p class="sub">Every live skill scored on four axes — Value, Sustainability, Maintainability, Maturity — with a ceiling read for headroom, a per-type weighted standing score, and a recommended disposition. Companion to the TDD-011 reference-count census.</p>
<div class="meta"><span><b>Prepared for:</b> Robert Rice</span><span><b>Date:</b> __DATE__</span><span><b>Scope:</b> 56 live project skills</span><span><b>Evidence:</b> deep-read of every SKILL.md + census signals</span></div>
</header>

<div class="kpis">
<div class="kpi"><div class="n">__TOTAL__</div><div class="l">Live skills scored</div></div>
<div class="kpi"><div class="n">__HARDEN__</div><div class="l">Harden (fragile)</div></div>
<div class="kpi"><div class="n">__SIMPLIFY__</div><div class="l">Simplify (tangled)</div></div>
<div class="kpi"><div class="n">__RETIRE__</div><div class="l">Retire / Review</div></div>
</div>

<div class="callout"><div class="lbl">How to read this</div>
<p><b>Standing</b> (the composite, 0–100) is a blended <em>health</em> score, not an importance ranking — a load-bearing skill that is fragile and tangled scores <em>lower</em> than a humble, clean one. That is the point: it surfaces where the value-at-risk is. <b>Value</b> is its own column — sort by it to rank pure importance.</p>
<p>The actionable shortlist for the overhaul is the <b>__ACTION__ skills</b> not marked <span class="badge d-maintain">Maintain</span>: __HARDEN__ to harden, __SIMPLIFY__ to simplify, __RETIRE__ to review/retire, and __INVEST__ with real runway to invest in. The other __MAINTAINN__ are healthy — leave them alone.</p></div>

<h2 class="section">The scoring model</h2>
<div class="legend">
<div class="item"><div class="k">Value — what it's worth when it runs</div><div class="d">Intrinsic criticality blended with census reach (incoming blast radius) and actual ledger run-count. Higher = more painful to lose.</div></div>
<div class="item"><div class="k">Sustainability — will it keep working untouched?</div><div class="d">Resistance to external rot. Lower when it leans on volatile surfaces (live DOM, third-party APIs, drifting schemas) or fans out to many sub-skills (any one breaking breaks it).</div></div>
<div class="item"><div class="k">Maintainability — cost/safety to change on purpose</div><div class="d">Internal health: size, single-responsibility, safety nets (evals). Penalized by high incoming blast radius — editing a load-bearing skill ripples across many files.</div></div>
<div class="item"><div class="k">Maturity → Ceiling — are we there?</div><div class="d">The bar shows current maturity (solid green) and the remaining headroom to its realistic ceiling (hatched amber). A long hatched tail = unrealized upside.</div></div>
</div>
<div class="tier info" style="border-left-color:var(--accent-2);">
<h3>Per-type weighting &amp; disposition logic</h3>
<p>Same four axes, weighted differently by type because "value" means different things for a conductor, a worker, and a niche helper. Standing = weighted average of the four axes, scaled to 100.</p>
<table class="wt"><thead><tr><th>Type</th><th>Value</th><th>Sustainability</th><th>Maintainability</th><th>Maturity</th></tr></thead><tbody>
<tr><td>Orchestrators</td><td>40%</td><td>25%</td><td>20%</td><td>15%</td></tr>
<tr><td>Tools</td><td>35%</td><td>30%</td><td>20%</td><td>15%</td></tr>
<tr><td>One-offs</td><td>35%</td><td>20%</td><td>25%</td><td>20%</td></tr>
</tbody></table>
<ul>
<li><span class="badge d-retire">Retire/Review</span> Value ≤ 2 — question whether it still earns its place.</li>
<li><span class="badge d-harden">Harden</span> Valuable but fragile (Sustainability ≤ 2) — stabilize before it breaks under you.</li>
<li><span class="badge d-simplify">Simplify</span> Valuable but hard/risky to change (Maintainability ≤ 2) — de-tangle.</li>
<li><span class="badge d-invest">Invest</span> Solid, with real headroom (ceiling ≥ 5 or gap ≥ 2) — grow it.</li>
<li><span class="badge d-maintain">Maintain</span> Healthy on every axis — leave it alone.</li>
</ul>
<p class="note">Disposition is a priority cascade (protect value first, then grow): a Harden-flagged skill that also has a high ceiling is an Invest candidate <em>after</em> it is stabilized. Portability is excluded by request (Claude-specific is fine).</p>
</div>

<div class="controls">
<input id="q" placeholder="Filter by skill name or purpose…" oninput="setQ(this.value)">
<span class="chip c-invest" onclick="tog('Invest',this)">Invest</span>
<span class="chip c-harden" onclick="tog('Harden',this)">Harden</span>
<span class="chip c-simplify" onclick="tog('Simplify',this)">Simplify</span>
<span class="chip c-retire" onclick="tog('Retire/Review',this)">Retire/Review</span>
<span class="chip c-maintain" onclick="tog('Maintain',this)">Maintain</span>
</div>
<div id="tables"></div>

<footer class="rep">QE skill-ecosystem rankings · 56 live skills · deep-read + census-fold · generated __DATE__ · companion to TDD-011<br>
Census note: the TDD-011 census enumerated 62; 6 are no longer live (<code>pr-qa</code>, <code>review-pr</code>, <code>qe-dashboard</code> archived; <code>sync-vault</code>, <code>staged-run</code>, <code>sync-repos</code>, <code>run-and-fix</code> removed/redirect) — excluded here.</footer>
</div>
<script>
const PAY=__DATA__;const ROWS=PAY.rows;
const ORDER={O:0,T:1,X:2},TNAME={O:"Orchestrators",T:"Tools",X:"One-offs"};
const DC={"Invest":"d-invest","Maintain":"d-maintain","Harden":"d-harden","Simplify":"d-simplify","Retire/Review":"d-retire"};
let q="",filt=new Set(),sortKey="comp",sortDir=-1;
function pill(n){return '<span class="score p'+n+'">'+n+'</span>';}
function gap(mat,ceil){let s='';for(let i=1;i<=5;i++){let c=i<=mat?'fill':(i<=ceil?'head':'empty');s+='<span class="seg '+c+'"></span>';}return '<span class="gapbar" title="maturity '+mat+' → ceiling '+ceil+' (headroom '+Math.max(0,ceil-mat)+')">'+s+'</span>';}
function setQ(v){q=v.toLowerCase();render();}
function tog(d,el){if(filt.has(d)){filt.delete(d);el.classList.remove('on');}else{filt.add(d);el.classList.add('on');}render();}
function sortBy(k){if(sortKey===k){sortDir*=-1;}else{sortKey=k;sortDir=(k==='name')?1:-1;}render();}
const COLS=[["rank","#",1],["name","Skill",0],["disp","Disposition",0],["V","Value",1],["S","Sustain",1],["M","Maintain",1],["gap","Maturity→Ceiling",1],["comp","Standing",1]];
function render(){
 const host=document.getElementById('tables');host.innerHTML='';
 ["O","T","X"].forEach(t=>{
  let rs=ROWS.filter(r=>r.type===t)
    .filter(r=>!filt.size||filt.has(r.disp))
    .filter(r=>!q||r.name.toLowerCase().includes(q)||r.purpose.toLowerCase().includes(q));
  const total=ROWS.filter(r=>r.type===t).length;
  const head=document.createElement('div');head.className='secthead';
  head.innerHTML='<h2>'+TNAME[t]+'</h2><span class="cnt">'+rs.length+' of '+total+' shown</span>';
  host.appendChild(head);
  if(!rs.length){const e=document.createElement('p');e.className='note';e.textContent='— none match the current filter —';host.appendChild(e);return;}
  rs.sort((a,b)=>{let k=sortKey==='gap'?'head':sortKey;let av=a[k],bv=b[k];if(k==='name'){return sortDir*av.localeCompare(bv);}return sortDir*(av-bv)|| (a.rank-b.rank);});
  let th=COLS.map(c=>{let ar=sortKey===c[0]||(sortKey==='head'&&c[0]==='gap')?(sortDir<0?' ▾':' ▴'):'';return '<th class="'+(c[2]?'num':'')+'" onclick="sortBy(\''+c[0]+'\')">'+c[1]+'<span class="ar">'+ar+'</span></th>';}).join('');
  let body=rs.map(r=>{
   let sig='<span class="sig">in <b>'+r.inf+'</b> · out <b>'+r.out+'</b> · runs <b>'+(r.runs==null?'—':r.runs)+'</b></span>';
   return '<tr>'+
    '<td class="num"><b>'+r.rank+'</b></td>'+
    '<td><div class="sk"><code>'+r.name+'</code></div><div class="pp">'+r.purpose+'</div>'+sig+'</td>'+
    '<td><span class="badge '+DC[r.disp]+'" title="'+r.why+'">'+r.disp+'</span></td>'+
    '<td class="num">'+pill(r.V)+'</td><td class="num">'+pill(r.S)+'</td><td class="num">'+pill(r.M)+'</td>'+
    '<td class="num">'+gap(r.MAT,r.CEIL)+'</td>'+
    '<td class="num"><span class="comp">'+r.comp+'</span></td></tr>';
  }).join('');
  const card=document.createElement('div');card.className='tablecard';
  card.innerHTML='<table><thead><tr>'+th+'</tr></thead><tbody>'+body+'</tbody></table>';
  host.appendChild(card);
 });
}
render();
</script></body></html>'''
TPL=TPL.replace("__HDR__",HDR)
TPL=TPL.replace("__DATE__",date)
TPL=TPL.replace("__DATA__",pay)
TPL=TPL.replace("__TOTAL__",str(meta["total"]))
TPL=TPL.replace("__HARDEN__",str(d.get("Harden",0)))
TPL=TPL.replace("__SIMPLIFY__",str(d.get("Simplify",0)))
TPL=TPL.replace("__RETIRE__",str(d.get("Retire/Review",0)))
TPL=TPL.replace("__INVEST__",str(d.get("Invest",0)))
TPL=TPL.replace("__MAINTAINN__",str(d.get("Maintain",0)))
TPL=TPL.replace("__ACTION__",str(meta["total"]-d.get("Maintain",0)))
outp=os.path.join(SK,"reference","runs",date+"-skill-scorecard.html")
open(outp,"w").write(TPL)
print("WROTE",outp)
print("bytes",len(TPL))
