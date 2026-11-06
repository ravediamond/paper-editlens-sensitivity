"""Shared pieces of the human-dose experiment: paths, paragraph extraction from a rendered DRAFT_4p.md, git helpers.

Runs on the Orin with the `editlens` venv (`~/venvs/editlens/bin/python`). The paper repositories are the clones under
~/scratch/paper-repos/; road-to-robotics is at ~/workspace/road-to-robotics (paper_map.strip_cites, paper_polish.score)."""
import hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent / "expected"
RTR = Path.home() / "workspace/road-to-robotics/scripts"
sys.path.insert(0, str(RTR))
PAPERS = ["paper-register-reproducibility", "paper-jepa-world-model", "paper-reward-models-stopping-rule", "paper-vla-edge-inference"]
REPOS = Path.home() / "scratch/paper-repos"
DRAFT = "paper/DRAFT_4p.md"
MIN_WORDS = 40
BINS = [(0.00, 0.03), (0.03, 0.06), (0.06, 0.10), (0.10, 0.15), (0.15, 1.01)]


def strip_cites(t):
    try:
        import paper_map as M
        return M.strip_cites(t)
    except Exception:
        t = re.sub(r"\[@[^\]]+\]", "", t)
        t = re.sub(r"\[arXiv:[^\]]+\]", "", t)
        return re.sub(r"[ \t]+", " ", re.sub(r"\s+([,.;:])", r"\1", t)).strip()


def nwords(t):
    return len(re.findall(r"\b\w+\b", t))


def paragraphs(md):
    """Prose paragraphs of a rendered markdown draft: blank-line blocks that are not headings, tables, quotes, code,
    figures, list items or the author line; citations stripped; at least MIN_WORDS words."""
    out, fence = [], False
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if not b:
            continue
        if b.startswith("```"):
            fence = not fence if b.count("```") % 2 else fence
            continue
        if fence:
            continue
        first = b.lstrip()
        if first[0] in "#|>!-*" or first.startswith("Table ") or first.startswith("Figure ") or first.startswith("*") or re.match(r"^\d+\.\s", first):
            continue
        t = strip_cites(re.sub(r"\s+", " ", b))
        if nwords(t) >= MIN_WORDS:
            out.append(t)
    return out


def sha(t):
    return hashlib.sha1(t.encode()).hexdigest()[:12]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def show(repo, rev, path=DRAFT):
    return git(repo, "show", f"{rev}:{path}")


def load(name):
    p = EXP / name
    return json.loads(p.read_text()) if p.exists() else None


def dump(name, obj):
    EXP.mkdir(parents=True, exist_ok=True)
    (EXP / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def bin_of(m):
    for i, (lo, hi) in enumerate(BINS):
        if lo <= m < hi:
            return i
    return len(BINS) - 1
