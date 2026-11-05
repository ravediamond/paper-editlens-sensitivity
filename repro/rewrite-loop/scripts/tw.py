"""tw.py: port changed vla paragraphs from md source to main.src.tex. Verifies each original paragraph transforms to exactly the text found in the tex."""
import re, sys, json
from pathlib import Path
R = Path.home()/"scratch/paper-repos/paper-vla-edge-inference/paper"
orig = (Path("work")/"vla-edge-inference.orig.md").read_text().split("\n")
new = (Path("work")/"vla-edge-inference.src.md").read_text().split("\n")
tex = (R/"main.src.tex").read_text()
SUB = [("$", r"\$"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("≥", r"$\geq$"), ("≤", r"$\leq$"), ("×", r"$\times$"), ("°", r"$^\circ$"), ("τ", r"$\tau$"), ("—", "---"), ("–", "--"), ("±", r"$\pm$")]
def esc(x):
    ph = re.findall(r"\{\{[^}]*\}\}", x)
    for k, p in enumerate(ph): x = x.replace(p, f"@@{k}@@", 1)
    for a, b in SUB: x = x.replace(a, b)
    x = x.replace("Fig. 2", "Fig.~\\ref{fig:jump}").replace("Fig. 3", "Fig.~\\ref{fig:cost}").replace("π0", "$\\pi_0$")
    x = re.sub(r"\[arXiv:(\d{4})\.(\d{4,5})\]", lambda m: r"\citep{arxiv" + m.group(1) + m.group(2) + "}", x)
    x = re.sub(r"\[@([^\]]+)\]", lambda m: r"\citep{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}", x)
    x = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", x); x = re.sub(r"(?<!\*)\*([^*\n]+)\*", r"\\emph{\1}", x); x = re.sub(r"`(.+?)`", r"\\texttt{\1}", x)
    for k, p in enumerate(ph): x = x.replace(f"@@{k}@@", p)
    return x
def paras(lines):
    out, cur = [], []
    for l in lines + [""]:
        if l.strip(): cur.append(l)
        elif cur: out.append(" ".join(cur)); cur = []
    return out
po, pn = paras(orig), paras(new)
assert len(po) == len(pn), (len(po), len(pn))
norm = lambda s: re.sub(r"\s+", " ", s).strip()
ntex = norm(tex)
changed = 0
for a, b in zip(po, pn):
    if a == b: continue
    ea, eb = norm(esc(a)), norm(esc(b))
    if ea not in ntex:
        print("NO MATCH for original:", a[:80]); continue
    ntex = ntex.replace(ea, eb); changed += 1
print("changed paragraphs ported:", changed)
if "--write" in sys.argv:
    # keep original line structure: rewrite tex paragraph blocks by replacing the original blocks
    t = tex
    for a, b in zip(po, pn):
        if a == b: continue
        ea = norm(esc(a)); eb = esc(b)
        pat = re.compile(r"\s+".join(re.escape(w) for w in ea.split(" ")))
        if len(pat.findall(t)) != 1: print("pattern count", len(pat.findall(t)), a[:60]); continue
        t = pat.sub(lambda m: eb, t, count=1)
    (R/"main.src.tex").write_text(t); print("written")
