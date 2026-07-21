#!/usr/bin/env python3
"""Gather census signals for the scorecard from the live skill-graph SSOT.
Reads _shared/skill-graph.json (regenerate first with `npm run skill:graph`) for
per-skill incoming blast-radius + outgoing fan-out, and run-counts.seed.json for
standalone ledger run frequency. Emits reference/data/<date>-signals.json.
Usage: gather-signals.py <date> [skills_root]
"""
import json,sys,os
date=sys.argv[1]
ROOT=sys.argv[2] if len(sys.argv)>2 else os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
graph=json.load(open(os.path.join(ROOT,"_shared","skill-graph.json")))["skills"]
SK=os.path.join(ROOT,"skill-scorecard")
rc_path=os.path.join(SK,"reference","data","run-counts.seed.json")
runs=json.load(open(rc_path)) if os.path.exists(rc_path) else {}
sig=[]
for name,info in graph.items():
    if info.get("origin")!="project" or info.get("deprecated"): continue
    sig.append(dict(name=name,
                    **{"in":info["incoming"]["files"],"out":info["outgoing"]["skills"],
                       "runs":runs.get(name)}))
sig.sort(key=lambda r:r["name"])
out=os.path.join(SK,"reference","data",f"{date}-signals.json")
json.dump({"date":date,"source":"_shared/skill-graph.json + run-counts.seed.json","skills":sig},open(out,"w"),indent=0)
print("wrote",out,"|",len(sig),"skills")
