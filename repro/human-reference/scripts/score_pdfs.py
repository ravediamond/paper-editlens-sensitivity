#!/usr/bin/env python3
"""Score the paragraphs of a set of PDFs with the open EditLens 3B model, section by section, through the same PDF extractor for every paper
(road-to-robotics scripts/paper_map.py pdf_sections, pdftotext in reading order, references dropped). Needs `ws paper-polish serve`.

    python3 score_pdfs.py HUMAN_PDF_DIR OUT.json [--ours PDF ...]

Per paragraph of at least 40 words: paper id, group (human or ours), section title, section type, words, score, sha1 of the text. The text is not
stored. The fence of paper_map allows the human folder (~/scratch/WS-162/...) and the four papers' repositories."""
import hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/road-to-robotics/scripts"))
import paper_map as M  # noqa: E402
import paper_polish as PP  # noqa: E402

TYPES = [("abstract", r"abstract"), ("introduction", r"introduc"), ("related", r"related|background|prior work|literature"),
         ("method", r"method|approach|model|problem|setup|formulation|framework|system|architecture|algorithm|preliminar|task|design|data"),
         ("results", r"experiment|result|evaluat|analysis|ablation|simulation|study|comparison|performance|benchmark"),
         ("conclusion", r"conclu|discussion|limitation|future|summary")]


def stype(t):
    t = t.lower()
    for name, rx in TYPES:
        if re.search(rx, t):
            return name
    return "other"


TOP = [re.compile(p) for p in (r"^(?:[IVX]+\.?\s+)([A-Z][A-Z0-9 ,:'/&-]{3,60})$", r"^\d+\.?\s+([A-Z][A-Za-z0-9 ,:'/&-]{2,60})$", r"^([A-Z][A-Z ]{3,40})$",
                              r"^(Abstract|Introduction|Related Works?|Conclusions?|Discussion|Experiments|Results|Methods?|Approach|Background|Evaluation)$")]
SUB = re.compile(r"^(?:[A-Z]\.|\d+\.\d+\.?)\s+[A-Z][A-Za-z0-9 ,:'/&-]{2,70}$")


def sections(pdf):
    """pdftotext in reading order; top-level headings (Roman, numbered, upper-case or plain Introduction / Conclusion ...) start a section, sub-headings only end a paragraph."""
    import subprocess
    txt = subprocess.run(["pdftotext", "-nopgbrk", str(pdf), "-"], capture_output=True, text=True).stdout
    txt = re.sub(r"-\n(?=[a-z])", "", txt).replace("\ufb01", "fi").replace("\ufb02", "fl")
    secs, buf, skip = [{"title": "Abstract", "paras": []}], [], False

    def prose_like(lines):
        toks = " ".join(lines).split(); alpha = sum(bool(re.fullmatch(r"[A-Za-z][A-Za-z'-]*[.,;:]?", t)) for t in toks)
        return len(toks) >= 12 and alpha / len(toks) >= 0.6 and sum(len(l.split()) for l in lines) / len(lines) >= 5

    def flush():
        nonlocal buf
        if buf and not skip and prose_like(buf):
            secs[-1]["paras"].append({"text": M.strip_cites(" ".join(buf))})
        buf = []
    for l in txt.split("\n"):
        t = l.strip()
        if t and len(t.split()) <= 9 and any(rx.match(t) for rx in TOP):
            flush(); skip = bool(re.search(r"REFERENCES|BIBLIOGRAPHY|ACKNOWLEDG|APPENDIX|References|Bibliography|Acknowledg|Appendix", t))
            if not skip:
                secs.append({"title": t, "paras": []})
        elif t and SUB.match(t) and len(t.split()) <= 10:
            flush()
        elif not t:
            flush()
        else:
            buf.append(t)
    flush()
    return [s for s in secs if s["paras"]]


def rows_for(pdf, group, pid):
    out = []
    for s in sections(pdf):
        for p in s["paras"]:
            if M.words(p["text"]) >= 40 and PP_tok(p["text"]) <= M.MAX_TOKENS:
                out.append({"paper": pid, "group": group, "section": s["title"], "type": stype(s["title"]), "words": M.words(p["text"]),
                            "sha1": hashlib.sha1(p["text"].encode()).hexdigest()[:12], "_t": M.clean_text(p["text"])})
    return out


def PP_tok(t):
    return len(t.split()) * 1.4  # a cheap upper bound on tokens; the server truncates at 1024 either way


def main():
    a = sys.argv[1:]; hdir, out = Path(a[0]), a[1]; ours = a[a.index("--ours") + 1:] if "--ours" in a else []
    rows = []
    for f in sorted(hdir.glob("pdfs/*.pdf")):
        rows += rows_for(f, "human", re.sub(r"v\d+$", "", f.stem))
    for f in ours:
        rows += rows_for(Path(f), "ours", Path(f).parents[1].name)
    old = {}
    prev = Path(out).with_name("rows_v1_extractor.json")
    if prev.exists():
        for r in json.loads(prev.read_text()):
            old[(r["paper"], r["sha1"])] = r["score"]
    todo = [r for r in rows if (r["paper"], r["sha1"]) not in old]
    sc = PP.score([r["_t"] for r in todo], wait=1800) if todo else []
    new = {id(r): s for r, s in zip(todo, sc)}
    for r in rows:
        r["score"] = old.get((r["paper"], r["sha1"]), new.get(id(r)))
    for r in rows:
        r.pop("_t", None)
    print(len(rows) - len(todo), "scores reused,", len(todo), "scored")
    Path(out).write_text(json.dumps(rows))
    print(len(rows), "paragraphs;", len({r["paper"] for r in rows if r["group"] == "human"}), "human papers")


if __name__ == "__main__":
    main()
