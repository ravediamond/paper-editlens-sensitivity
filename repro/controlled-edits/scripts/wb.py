"""wb.py list <paper> | score <paper> <para#> cands.json [round] | apply <paper> <para#> text.txt
paper = register-reproducibility | jepa-world-model | reward-models-stopping-rule | vla-edge-inference
Paragraph = lines l0..l1 of the working source copy (same numbering as the rendered text, from inventory.json)."""
import json, re, subprocess, sys, time
from pathlib import Path
D = Path(__file__).resolve().parent
inv = json.load(open(D/"baseline.json"))
def numbers(p):
    return {k: v["value"] for k, v in json.load(open(Path.home()/f"scratch/paper-repos/paper-{p}/paper/numbers.json")).items()}
import sys as _s
_s.path.insert(0, "/home/jetson/workspace/road-to-robotics/scripts")
import prose_check as P, paper_map as M
def render(p, t):
    n = numbers(p)
    t = re.sub(r"\{\{(\w+)\}\}", lambda m: n[m.group(1)], t)
    if t.lstrip().startswith("!["):
        return M.strip_cites(re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t))
    return M.strip_cites(" ".join(x for _, x in P.extract(t, "md") if x.strip()))
def src_lines(p): return (D/"work"/f"{p}.src.md").read_text().split("\n")
def para_src(p, i):
    e = inv["paper-"+p]["paras"][i]; return "\n".join(src_lines(p)[e["l0"]-1:e["l1"]])
def score_texts(texts):
    (D/"tmp.json").write_text(json.dumps(texts))
    o = subprocess.run(["python3", str(D/"score.py"), str(D/"tmp.json")], capture_output=True, text=True).stdout.strip().split("\n")
    return [float(l.split()[0]) for l in o]
if __name__ == "__main__":
    cmd, p = sys.argv[1], sys.argv[2]
    if cmd == "list":
        for i, e in enumerate(inv["paper-"+p]["paras"]):
            print(f"{i:2d} L{e['l0']}-{e['l1']} {e['base']:.3f} {len(e['text'].split()):4d}w  [{e['sec'][:28]}] {e['text'][:70]}")
    elif cmd == "score":
        i = int(sys.argv[3]); cands = json.load(open(sys.argv[4])); rnd = sys.argv[5] if len(sys.argv) > 5 else "?"
        cur = para_src(p, i)
        allc = [cur] + cands
        sc = score_texts([render(p, c) for c in allc])
        log = open(D/"iterlog.jsonl", "a")
        for k, (c, s) in enumerate(zip(allc, sc)):
            ph_ok = sorted(re.findall(r"\{\{\w+\}\}", c)) == sorted(re.findall(r"\{\{\w+\}\}", cur))
            print(f"{'cur' if k == 0 else 'c'+str(k)}  {s:.3f}  placeholders_kept={ph_ok}  {len(render(p,c).split())}w")
            log.write(json.dumps({"paper": p, "para": i, "round": rnd, "cand": k, "score": s, "ph_ok": ph_ok, "text": c, "t": time.time()}) + "\n")
    elif cmd == "apply":
        i = int(sys.argv[3]); new = Path(sys.argv[4]).read_text().rstrip("\n")
        e = inv["paper-"+p]["paras"][i]; L = src_lines(p)
        cur = "\n".join(L[e["l0"]-1:e["l1"]])
        assert sorted(re.findall(r"\{\{\w+\}\}", new)) == sorted(re.findall(r"\{\{\w+\}\}", cur)), "placeholders differ"
        nl = new.split("\n"); L[e["l0"]-1:e["l1"]] = nl
        delta = len(nl) - (e["l1"] - e["l0"] + 1)
        (D/"work"/f"{p}.src.md").write_text("\n".join(L))
        if delta:
            for o in inv["paper-"+p]["paras"]:
                if o is e: continue
                if o["l0"] > e["l1"]: o["l0"] += delta; o["l1"] += delta
            e["l1"] += delta
            json.dump(inv, open(D/"baseline.json", "w"), indent=1)
        print("applied")
