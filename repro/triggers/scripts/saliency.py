#!/usr/bin/env python3
"""Token attribution for the open EditLens score: gradient of the score (probability-weighted bucket mean) with respect to the input embeddings,
times the embedding, summed over the embedding dimension and over the sub-word tokens of each word. Positive = the word pushes the score up.
Loads its own copy of the model, so stop `ws paper-polish` first (one copy is about 7 GB).

    python3 saliency.py TEXTS.json OUT.json     TEXTS.json: [{"id": ..., "text": ...}, ...]; OUT: per id the score, the words and their attributions."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/road-to-robotics/scripts"))
import paper_map as M  # noqa: E402


def main():
    import torch
    items = json.loads(Path(sys.argv[1]).read_text()); sc = M.EditLensScorer(); tok, model = sc.tokenizer, sc.model; out = {}
    for it in items:
        text = M.clean_text(it["text"])
        x = tok(text, truncation=True, max_length=900, return_tensors="pt", return_offsets_mapping=True)
        off = x.pop("offset_mapping")[0].tolist(); x = x.to("cuda")
        emb = model.get_input_embeddings()(x["input_ids"]).detach().clone().float().requires_grad_(True)
        logits = model(inputs_embeds=emb.half(), attention_mask=x["attention_mask"]).logits.float()
        p = torch.softmax(logits, -1)[0]; n = p.shape[0]; score = (p * torch.arange(n, device=p.device)).sum() / (n - 1)
        score.backward(); a = (emb.grad * emb).sum(-1)[0].detach().cpu().tolist()
        import re
        spans = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]; where = {}
        for wi, (ws_, we_) in enumerate(spans):
            for c in range(ws_, we_):
                where[c] = wi
        acc = [0.0] * len(spans)
        for (s0, e0), v in zip(off, a):
            if e0 == s0:
                continue
            c = s0
            while c < e0 and text[c].isspace():
                c += 1
            if c in where:
                acc[where[c]] += v
        words = [{"s": ws_, "e": we_, "a": acc[wi]} for wi, (ws_, we_) in enumerate(spans)]
        out[it["id"]] = {"score": float(score), "direct": sc.score(text)[0], "words": [{"w": text[w["s"]:w["e"]], "a": w["a"]} for w in words]}
        print(it["id"], round(float(score), 3), round(out[it["id"]]["direct"], 3), flush=True)
    Path(sys.argv[2]).write_text(json.dumps(out))


if __name__ == "__main__":
    main()
