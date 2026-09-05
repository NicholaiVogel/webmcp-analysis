#!/usr/bin/env python3
"""Screenshot worker: take shard of Devpost project pages via agent-browser.
Usage: shot_worker.py SHARD TOTAL WORKERS
Each worker owns agent-browser session 'webmcp-<SHARD>'. Logs JSONL to screenshots/log-<SHARD>.jsonl
"""
import json, os, subprocess, sys, time

BASE = "/mnt/work/webmcp-analysis"
SHARD, TOTAL, WORKERS = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
SESSION = f"webmcp-{SHARD}"
LOG = os.path.join(BASE, "screenshots", f"log-{SHARD}.jsonl")
SS_DIR = os.path.join(BASE, "screenshots")
os.makedirs(SS_DIR, exist_ok=True)

def run(*args, timeout=90):
    cmd = ["agent-browser", "--session", SESSION] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"

def log(rec):
    with open(LOG, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# boot session + viewport
run("set", "viewport", "1440", "900", timeout=60)

slugs = [l.strip() for l in open(os.path.join(BASE, "raw", "slugs_all.txt")) if l.strip()]
mine = slugs[SHARD::WORKERS]
t0 = time.time()
done = 0
for slug in mine:
    png = os.path.join(SS_DIR, slug + ".png")
    rec = {"slug": slug, "status": "", "title": "", "bytes": 0}
    if os.path.exists(png) and os.path.getsize(png) > 25000:
        rec["status"] = "cached"
        log(rec); continue
    code, out = run("open", f"https://devpost.com/software/{slug}", timeout=75)
    run("wait", "2200", timeout=30)
    tcode, tout = run("get", "title", timeout=30)
    title = tout.strip().splitlines()[-1] if tout.strip() else ""
    rec["title"] = title[:120]
    scode, sout = run("screenshot", png, timeout=60)
    rec["bytes"] = os.path.getsize(png) if os.path.exists(png) else 0
    if title == "Devpost" or (code != 0 and "403" in out):
        rec["status"] = "DEAD" if title == "Devpost" else f"HTTP_FAIL"
        if rec["bytes"] and rec["bytes"] < 25000 and rec["status"] == "DEAD":
            pass  # keep tiny 404 proof shot
    elif rec["bytes"] < 25000:
        # retry once
        time.sleep(2)
        run("open", f"https://devpost.com/software/{slug}", timeout=75)
        run("wait", "3500", timeout=30)
        run("screenshot", png, timeout=60)
        rec["bytes"] = os.path.getsize(png) if os.path.exists(png) else 0
        rec["status"] = "small_retry"
    else:
        rec["status"] = "ok"
    log(rec)
    done += 1
    if done % 25 == 0:
        rate = done / (time.time() - t0)
        print(f"[{SHARD}] {done}/{len(mine)} rate={rate:.2f}/s eta={int((len(mine)-done)/max(rate,0.01)/60)}min", flush=True)
print(f"[{SHARD}] DONE {done}", flush=True)
