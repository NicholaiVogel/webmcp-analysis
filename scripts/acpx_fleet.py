#!/usr/bin/env python3
"""S1 fleet driver via acpx+codex (ACP): low reasoning, read-approve policy, no MCP.
- prompt from fleet/prompts, stdout = final message, extract JSONL, validate count
- resume-safe, retry pass, bounded concurrency
Usage: acpx_fleet.py [CONCURRENCY] [--retry]"""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/mnt/work/webmcp-analysis"
PROMPTS = os.path.join(BASE, "analysis", "fleet", "prompts")
RESULTS = os.path.join(BASE, "analysis", "results", "raw")
CODEX_HOME = "/mnt/work/hermes-scratch/codex-home"
os.makedirs(RESULTS, exist_ok=True)
CONC = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 24
RETRY = "--retry" in sys.argv
TIMEOUT = 900

index = json.load(open(os.path.join(BASE, "analysis", "fleet", "index.json")))

def out_path(entry):
    return os.path.join(RESULTS, os.path.basename(entry["results_file"]))

def valid(path):
    n = 0
    if not os.path.exists(path) or os.path.getsize(path) < 200:
        return 0
    for line in open(path, encoding="utf-8", errors="ignore"):
        m = re.search(r"\{.*\}", line.strip())
        if m:
            try:
                d = json.loads(m.group(0))
                if "slug" in d and "leverage" in d:
                    n += 1
            except json.JSONDecodeError:
                pass
    return n

def extract(src, dst):
    txt = open(src, encoding="utf-8", errors="ignore").read()
    n = 0
    for line in txt.splitlines():
        for cand in re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", line):
            try:
                d = json.loads(cand)
                if "slug" in d and "leverage" in d:
                    dst.write(json.dumps(d, ensure_ascii=False) + "\n")
                    n += 1
            except json.JSONDecodeError:
                pass
    return n

def run_one(entry):
    name = entry["reviewer"].replace(".txt", "")
    out = out_path(entry)
    expect = len(entry["slugs"])
    if os.path.exists(out) and valid(out) == expect:
        return name, "cached", expect
    prompt_file = os.path.join(PROMPTS, entry["reviewer"])
    tmp_out = out + f".{os.getpid()}.tmp"
    env = dict(os.environ, CODEX_HOME=CODEX_HOME)
    cmd = ["acpx", "--cwd", BASE, "--format", "quiet",
           "--approve-reads", "--non-interactive-permissions", "deny",
           "--suppress-reads", "--timeout", str(TIMEOUT - 60), "--max-turns", "80",
           "codex", "exec", "--file", "-"]
    t0 = time.time()
    try:
        with open(prompt_file) as pf, open(tmp_out, "w") as tf:
            r = subprocess.run(cmd, stdin=pf, stdout=tf, stderr=subprocess.DEVNULL,
                               env=env, timeout=TIMEOUT)
        n = 0
        with open(out, "w") as fo:
            n = extract(tmp_out, fo)
        os.remove(tmp_out)
        dt = int(time.time() - t0)
        if n < expect:
            return name, f"PARTIAL {n}/{expect}", n
        return name, f"ok {dt}s", n
    except subprocess.TimeoutExpired:
        return name, "TIMEOUT", 0
    except Exception as e:
        return name, f"ERR {type(e).__name__}", 0

def _main():
    todo = [e for e in index if not (os.path.exists(out_path(e)) and valid(out_path(e)) == len(e["slugs"]))]
    print(f"total={len(index)} todo={len(todo)} conc={CONC}", flush=True)
    stats = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=CONC) as ex:
        futs = {ex.submit(run_one, e): e for e in todo}
        for i, fu in enumerate(as_completed(futs), 1):
            name, st, n = fu.result()
            key = st.split()[0]
            stats[key] = stats.get(key, 0) + 1
            if i % 25 == 0 or st.split()[0] not in ("ok", "cached"):
                el = int(time.time() - t0)
                print(f"{i}/{len(todo)} {name}: {st} | {stats} elapsed={el}s", flush=True)
    print("DONE", stats, flush=True)

if __name__ == "__main__":
    _main()
