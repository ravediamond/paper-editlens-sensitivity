#!/usr/bin/env python3
"""AI-direction reference rows: human source paragraphs edited by an LLM, from the authors' dataset `pangram/editlens_iclr`
(test split), scored with the same 3B model and the same magnitude metric (PROTOCOL §2, §3).

    ai_curve.py --columns      print the split's columns and 2 rows; write expected/ai_route.json with the route chosen (§6 check 5)
    ai_curve.py                600 AI-edited rows drawn with seed 0 (120 per cosine bin when the source text is available,
                               else uniform); write expected/ai_rows.json

Row: {"idx", "cosine", "sng", "label" (the authors' score column if any), "s_src", "s_edit", "delta", "words_src", "words_edit"}
Texts are not stored (the dataset is CC BY-NC-SA, re-downloadable). The fallback route of §2 (300 human-reference paragraphs
edited once with the 31 test-split prompts) is `ai_curve.py --fallback` and writes ai_rows_fallback.json; it needs an Anthropic key
in the environment and is not run unless the dataset route fails or the owner asks for the same-domain check."""
import random, sys
from common import *  # noqa: F401,F403

DATASET, SPLIT = "pangram/editlens_iclr", "test"
N, PER_BIN, SEED = 600, 120, 0
SRC_COLS = ["source_text", "source", "original_text", "human_text", "original"]
TXT_COLS = ["text", "edited_text", "output"]
LAB_COLS = ["label", "class", "category", "type"]
SCORE_COLS = ["score", "cosine", "cosine_distance", "edit_score", "target"]


def pick(cols, names):
    return next((c for c in names if c in cols), None)


def load_split():
    from datasets import load_dataset
    return load_dataset(DATASET, split=SPLIT)


def columns():
    ds = load_split()
    print(ds.column_names); print(ds[0]); print(ds[1])
    cols = ds.column_names
    route = {"text": pick(cols, TXT_COLS), "source": pick(cols, SRC_COLS), "label": pick(cols, LAB_COLS), "score": pick(cols, SCORE_COLS),
             "route": "dataset+recomputed" if pick(cols, SRC_COLS) else "dataset+label" if pick(cols, SCORE_COLS) else "fallback",
             "decided": "before any AI-direction score was computed"}
    dump("ai_route.json", route); print(route)


def main():
    R = load("ai_route.json") or sys.exit("run --columns first")
    if R["route"] == "fallback":
        sys.exit("dataset route unusable: run --fallback (needs owner go)")
    import paper_polish as PP  # noqa: E402
    ds = load_split()
    lab = R["label"]
    rows = [i for i in range(len(ds)) if lab is None or "edit" in str(ds[i][lab]).lower() or str(ds[i][lab]) in ("1", "mixed")]
    rng = random.Random(SEED); rng.shuffle(rows)
    out, per_bin = [], {}
    if R["source"]:
        from magnitude import cosine_distance, soft_ngrams
        for i in rows:
            x, y = ds[i][R["source"]], ds[i][R["text"]]
            if nwords(x) < MIN_WORDS or nwords(y) < MIN_WORDS:
                continue
            c = cosine_distance(x, y); b = bin_of(c)
            if per_bin.get(b, 0) >= PER_BIN:
                continue
            per_bin[b] = per_bin.get(b, 0) + 1
            out.append({"idx": i, "cosine": round(c, 5), "sng": round(soft_ngrams(x, y), 5), "label": ds[i][R["score"]] if R["score"] else None,
                        "words_src": nwords(x), "words_edit": nwords(y), "_x": x, "_y": y})
            if len(out) >= N:
                break
    else:
        for i in rows[:N]:
            y = ds[i][R["text"]]
            out.append({"idx": i, "cosine": float(ds[i][R["score"]]), "sng": None, "label": ds[i][R["score"]], "words_src": None, "words_edit": nwords(y), "_x": None, "_y": y})
    for k in range(0, len(out), 16):
        chunk = out[k:k + 16]
        ys = PP.score([r["_y"] for r in chunk])
        xs = PP.score([r["_x"] for r in chunk]) if chunk[0]["_x"] is not None else [None] * len(chunk)
        for r, sx, sy in zip(chunk, xs, ys):
            r["s_src"], r["s_edit"], r["delta"] = sx, sy, (None if sx is None else round(sy - sx, 4))
            r.pop("_x"); r.pop("_y")
        print(f"{min(k + 16, len(out))}/{len(out)}")
    dump("ai_rows.json", out)
    print({b: sum(bin_of(r["cosine"]) == b for r in out) for b in range(len(BINS))})


PROMPTS_TEST = ["Lighten the tone and add a touch of humor", "Adjust the tone to be more friendly", "Increase the emotional stakes",
    "Make this sound more formal and school-like", "Make this nicer but keep the main point", "Change this so people from other countries can get it too",
    "Make this longer with more evidence", "Expand this text with more specific examples and details", "Show rather than tell by adding scene-setting details",
    "Include sounds, smells, textures, and other sensory elements", "Add a short story to make this more interesting", "Show how this works in real life",
    "Simplify this text", "Make this more specific", "Reduce wordiness while amplifying impact", "Say this in fewer words without losing meaning",
    "Edit this to be punchier and more direct", "Make this text flow more naturally", "Improve how the sentences sound together",
    "Refine the pacing and cadence of this paragraph", "Write a better and more interesting beginning", "Write this in a way that my teacher would get it",
    "Can you make my paper more persuasive?", "Make the main idea clearer", "Improve this to make it stronger and clearer", "Paraphrase this",
    "Rewrite this in different words while keeping the same meaning", "Reword this to improve clarity while keeping the meaning",
    "Make sure there's a beginning, middle, and end", "Group related ideas and use transitions to improve structure",
    "Can you fix any spelling, grammar, or punctuation issues?"]  # EditLens Table 8, TEST split, 31 prompts


def fallback(n=300, model="claude-sonnet-4-5"):
    """Same-domain AI-direction rows: human-reference paragraphs (the PDFs of ../human-reference, extracted with its score_pdfs.sections)
    edited once by an LLM with one of the 31 test-split prompts (seed 0). Writes ai_rows_fallback.json. Needs ANTHROPIC_API_KEY and the
    human PDF folder as argv[2]."""
    import os, anthropic
    sys.path.insert(0, str(HERE.parent.parent / "human-reference/scripts"))
    from score_pdfs import sections  # noqa: E402
    import paper_polish as PP  # noqa: E402
    from magnitude import cosine_distance, soft_ngrams
    pdfs = sorted(Path(sys.argv[2]).glob("*.pdf"))
    paras = [(pdf.stem, q["text"]) for pdf in pdfs for s in sections(pdf) for q in s["paras"] if nwords(q["text"]) >= MIN_WORDS]
    rng = random.Random(SEED); rng.shuffle(paras); paras = paras[:n]
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    out = []
    for k, (pid, x) in enumerate(paras):
        prompt = rng.choice(PROMPTS_TEST)
        msg = client.messages.create(model=model, max_tokens=1024, messages=[{"role": "user", "content": f"{prompt}\n\n{x}\n\nReturn only the edited text."}])
        y = msg.content[0].text.strip()
        sx, sy = PP.score([x, y])
        out.append({"idx": f"{pid}:{k}", "prompt": prompt, "cosine": round(cosine_distance(x, y), 5), "sng": round(soft_ngrams(x, y), 5), "label": None,
                    "words_src": nwords(x), "words_edit": nwords(y), "s_src": sx, "s_edit": sy, "delta": round(sy - sx, 4)})
        print(k + 1, pid, prompt[:30], out[-1]["cosine"], out[-1]["delta"])
    dump("ai_rows_fallback.json", out)


if __name__ == "__main__":
    columns() if "--columns" in sys.argv else fallback() if "--fallback" in sys.argv else main()
