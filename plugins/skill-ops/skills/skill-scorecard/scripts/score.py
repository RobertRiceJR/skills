#!/usr/bin/env python3
"""Scorecard engine. Joins deep-read intrinsic axes (<date>-readaxes.json) with
census signals (<date>-signals.json), folds signals into the four final axes,
derives ceiling/headroom, per-type weighted Standing, and a disposition.
Rubric SSOT: reference/rubric.md.  Usage: score.py <date> [skills_root]
"""
import json,sys,os
from collections import Counter
date=sys.argv[1]
ROOT=sys.argv[2] if len(sys.argv)>2 else os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
SK=os.path.join(ROOT,"skill-scorecard");DATA=os.path.join(SK,"reference","data")
rax={r["name"]:r for r in json.load(open(os.path.join(DATA,f"{date}-readaxes.json")))["skills"]}
sig={r["name"]:r for r in json.load(open(os.path.join(DATA,f"{date}-signals.json")))["skills"]}
TYPE_NAME={"O":"Orchestrators","T":"Tools","X":"One-offs"}
WEIGHTS={"O":(0.40,0.25,0.20,0.15),"T":(0.35,0.30,0.20,0.15),"X":(0.35,0.20,0.25,0.20)}
def reach(i):return 5 if i>=20 else 4 if i>=12 else 3 if i>=6 else 2 if i>=3 else 1
def usage(r):
    if r is None:return None
    return 5 if r>=25 else 4 if r>=10 else 3 if r>=3 else 2 if r>=1 else 1
def outf(o):return 1 if o>=10 else 2 if o>=7 else 3 if o>=4 else 4 if o>=1 else 5
def ripple(i):return 1 if i>=20 else 2 if i>=12 else 3 if i>=6 else 4 if i>=3 else 5
def cl(x):return max(1,min(5,int(x+0.5)))
rows=[];missing=[]
for name,ra in rax.items():
    if name not in sig:missing.append(name);continue
    s=sig[name];inf=s["in"];out=s["out"];runs=s["runs"];t=ra["type"]
    vi,si,mi,mat,ci=ra["vi"],ra["si"],ra["mi"],ra["mat"],ra["ci"]
    rs=reach(inf);us=usage(runs);of=outf(out);rp=ripple(inf)
    V=cl(0.625*vi+0.375*rs) if us is None else cl(0.5*vi+0.3*rs+0.2*us)
    S=cl(0.7*si+0.3*of);M=cl(0.7*mi+0.3*rp);MAT=mat;CEIL=ci;head=max(0,CEIL-MAT)
    wv,ws,wm,wmt=WEIGHTS[t];comp=int((wv*V+ws*S+wm*M+wmt*MAT)/5*100+0.5)
    if V<=2:disp="Retire/Review";why=f"Low value (V{V}) — confirm it still earns its place"
    elif S<=2:disp="Harden";why=f"High value (V{V}) but fragile (S{S})"+(f", and tangled (M{M})" if M<=2 else "")
    elif M<=2:disp="Simplify";why=f"Valuable (V{V}) but hard/risky to change (M{M})"
    elif head>=2 or (CEIL>=5 and MAT<=4):disp="Invest";why=f"Solid with real runway — maturity {MAT}, ceiling {CEIL}"
    else:disp="Maintain";why="Healthy across axes — leave it alone"
    rows.append(dict(name=name,type=t,typeName=TYPE_NAME[t],purpose=ra.get("purpose",""),V=V,S=S,M=M,MAT=MAT,CEIL=CEIL,
        head=head,comp=comp,disp=disp,why=why,inf=inf,out=out,runs=runs))
if missing:print("WARN missing signals for:",missing,file=sys.stderr)
for t in ("O","T","X"):
    grp=sorted([r for r in rows if r["type"]==t],key=lambda r:-r["comp"])
    for n,r in enumerate(grp,1):r["rank"]=n;r["typeCount"]=len(grp)
rows.sort(key=lambda r:({"O":0,"T":1,"X":2}[r["type"]],r["rank"]))
meta=dict(date=date,total=len(rows),disp=dict(Counter(r["disp"] for r in rows)),
          O=sum(r["type"]=="O" for r in rows),T=sum(r["type"]=="T" for r in rows),X=sum(r["type"]=="X" for r in rows),
          avg={a:round(sum(r[a] for r in rows)/len(rows),2) for a in ("V","S","M","MAT")})
out=os.path.join(DATA,f"{date}-run.json")
json.dump({"meta":meta,"rows":rows},open(out,"w"),indent=0)
print("wrote",out,"| disp",meta["disp"])
