#!/usr/bin/env python3
"""Stage 2 deterministic probe: load a project's demo URL in agent-browser,
screenshot, extract title, detect login walls, record status. Resume-safe."""
import json, os, subprocess, sys

BASE = "/mnt/work/webmcp-analysis"
PROBES = os.path.join(BASE, "probes")
os.makedirs(PROBES, exist_ok=True)
SESSION = "webmcp-probe"

LOGIN_MARKERS = ["sign in", "log in", "login", "sign up", "create account",
                 "get started free", "continue with google", "api key", "password"]

def run(*args, timeout=90):
    try:
        r = subprocess.run(["agent-browser", "--session", SESSION] + list(args),
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"

def probe(slug, url):
    png = os.path.join(PROBES, slug + ".png")
    rec = {"slug": slug, "url": url}
    code, out = run("open", url, timeout=70)
    run("wait", "3500", timeout=30)
    tcode, tout = run("get", "title", timeout=25)
    title = tout.strip().splitlines()[-1] if tout.strip() else ""
    rec["title"] = title[:150]
    _, body = run("eval", "document.body ? document.body.innerText.slice(0,3000) : ''", timeout=25)
    low = body.lower()
    rec["login_markers"] = [m for m in LOGIN_MARKERS if m in low][:5]
    scode, sout = run("screenshot", png, timeout=50)
    rec["shot_bytes"] = os.path.getsize(png) if os.path.exists(png) else 0
    rec["nav_fail"] = bool(code != 0 and ("ERR" in out or "403" in out or "timeout" in out))
    rec["empty"] = rec["shot_bytes"] < 15000 or (title == "" and rec["shot_bytes"] < 30000)
    if rec["nav_fail"]:
        rec["verdict"] = "unreachable"
    elif rec["login_markers"]:
        rec["verdict"] = "login_wall"
    elif rec["empty"]:
        rec["verdict"] = "empty_or_broken"
    else:
        rec["verdict"] = "loaded"
    return rec

if __name__ == "__main__":
    sigs = {}
    for line in open(os.path.join(BASE, "analysis", "signals.jsonl")):
        d = json.loads(line)
        sigs[d["slug"]] = d
    corpus = {}
    for line in open(os.path.join(BASE, "analysis", "corpus.jsonl")):
        d = json.loads(line)
        corpus[d["slug"]] = d
    out = open(os.path.join(BASE, "analysis", "probe_results.jsonl"), "a")
    done = set()
    if os.path.exists(os.path.join(BASE, "analysis", "probe_results.jsonl")):
        for line in open(os.path.join(BASE, "analysis", "probe_results.jsonl")):
            try:
                done.add(json.loads(line)["slug"])
            except Exception:
                pass
    run("set", "viewport", "1440", "900", timeout=60)
    targets = [s for s in sys.argv[1:] if s in sigs and s not in done]
    print(f"probing {len(targets)} of {len(sys.argv)-1} requested", flush=True)
    for i, slug in enumerate(targets, 1):
        url = sigs[slug].get("demo_url") or (corpus.get(slug, {}).get("page", {}).get("demo_links") or [""])[0]
        if not url:
            out.write(json.dumps({"slug": slug, "verdict": "no_demo_url"}, ensure_ascii=False) + "\n")
            continue
        rec = probe(slug, url)
        rec["url"] = url
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out.flush()
        if i % 20 == 0:
            print(f"{i}/{len(targets)}", flush=True)
    print("probe done", flush=True)
