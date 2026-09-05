#!/usr/bin/env python3
"""S1 fleet driver: run all reviewer prompts via codex exec (no MCP, low reasoning).
- bounded concurrency (default 16 processes)
- per-call timeout, resume-safe (skips already-validated results)
- lenient JSONL extraction from output; failures queued for retry pass
Usage: codex_fleet.py [CONCURRENCY] [--retry]"""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/mnt/work/webmcp-analysis"
PROMPTS = os.path.join(BASE, "analysis", "fleet", "prompts")
RESULTS = os.path.join(BASE, "analysis", "results", "raw")
os.makedirs(RESULTS, exist_ok=True)
CONC = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 16
RETRY = "--retry" in sys.argv
TIMEOUT = 900

index = json.load(open(os.path.join(BASE, "analysis", "fleet", "index.json")))

def out_path(entry):
    return os.path.join(RESULTS, os.path.basename(entry["results_file"]))

def valid(path):
    if not os.path.exists(path) or os.path.getsize(path) < 200:
        return 0
    n = 0
    for line in open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        m = re.search(r"\{.*\}", line)
        if m:
            try:
                d = json.loads(m.group(0))
                if "slug" in d and "leverage" in d:
                    n += 1
            except json.JSONDecodeError:
                pass
    return n

def extract(raw_path, out):
    """Pull JSON objects from codex final message; write clean JSONL."""
    txt = open(raw_path, encoding="utf-8", errors="ignore").read()
    n = 0
    for line in txt.splitlines():
        for candidate in re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", line):
            try:
                d = json.loads(candidate)
                if "slug" in d and "leverage" in d:
                    out.write(json.dumps(d, ensure_ascii=False) + "\n")
                    n += 1
            except json.JSONDecodeError:
                pass
    return n

def run_one(entry):
    name = entry["reviewer"].replace(".txt", "")
    out = out_path(entry)
    if os.path.exists(out) and valid(out) == len(entry["slugs"]):
        return name, "cached", len(entry["slugs"])
    prompt_file = os.path.join(PROMPTS, entry["reviewer"])
    with open(prompt_file) as f:
        prompt = f.read()
    tmp_out = out + ".raw"
    cmd = ["codex", "exec", "--ignore-user-config",
           "-c", 'model_reasoning_effort="low"',
           "-s", "read-only", "--skip-git-repo-check",
           "-C", BASE, "-o", tmp_out, "-"]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=TIMEOUT)
        if r.returncode != 0 or not os.path.exists(tmp_out):
            return name, f"FAIL rc={r.returncode}", 0
        n = 0
        with open(out, "w") as fo:
            n = extract(tmp_out, fo)
        os.remove(tmp_out)
        expect = len(entry["slugs"])
        if n < expect:
            return name, f"PARTIAL {n}/{expect}", n
        return name, "ok", n
    except subprocess.TimeoutExpired:
        return name, "TIMEOUT", 0

def _main():
    todo = [e for e in index if not (os.path.exists(out_path(e)) and valid(out_path(e)) == len(e["slugs"]))]
    if RETRY:
        todo = [e for e in index if not (os.path.exists(out_path(e)) and valid(out_path(e)) == len(e["slugs"]))]
    print(f"total={len(index)} todo={len(todo)} conc={CONC}", flush=True)
    stats = {}
    with ThreadPoolExecutor(max_workers=CONC) as ex:
        futs = {ex.submit(run_one, e): e for e in todo}
        for i, fu in enumerate(as_completed(futs), 1):
            name, st, n = fu.result()
            key = st.split()[0]
            stats[key] = stats.get(key, 0) + 1
            if i % 20 == 0 or st != "ok":
                print(f"{i}/{len(todo)} {name}: {st} ({n}) {stats}", flush=True)
    print("DONE", stats, flush=True)

if __name__ == "__main__":
    _main()
