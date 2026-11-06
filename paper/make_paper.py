#!/usr/bin/env python3
"""Render the paper from the result files: numbers.json (value + anchor), DRAFT_4p.src.md -> DRAFT_4p.md, main.src.tex -> main.tex (main.src.tex comes
from md2tex.py) by {{key}} placeholders; a placeholder without a value is an error, and so is a number or citation that has no source.

    python3 paper/md2tex.py && python3 paper/make_paper.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE.parent / "repro"
CE, RL, AT = R / "controlled-edits" / "expected", R / "rewrite-loop" / "expected", R / "attribution" / "expected"
AD = R / "additivity" / "expected"
N, A = {}, {}


def J(p):
    return json.loads(Path(p).read_text())


def put(k, v, anchor):
    N[k], A[k] = v, anchor


def s(x, d=3):
    return f"{x:+.{d}f}".replace("-", "\u2212")


def u(x, d=3):
    return f"{x:.{d}f}"


def collect():
    T, I, S = J(CE / "exp_transforms.json"), J(CE / "exp_insert.json"), J(CE / "subset_effects.json")
    res, ctr = "repro/rewrite-loop/expected/results.json", "repro/controlled-edits/expected/"
    LX, WD, BA = J(AT / "lexicon.json"), J(AT / "word_deletion.json"), J(RL / "before_after_rows.json")
    AS = J(AD / "additivity_summary.json"); ad = "repro/additivity/expected/additivity_summary.json "
    for k, key, d in [("add_paras", "paragraphs", None), ("add_hunks", "hunks", None), ("add_multi", "multi", None), ("add_single", "single", None)]:
        put(k, str(AS[key]), ad + key)
    put("add_D", s(AS["mean_D"]), ad + "mean_D (paragraphs with two or more hunks)"); put("add_S", s(AS["mean_S"]), ad + "mean_S")
    put("add_r", f"{AS['pearson']:.2f}", ad + "pearson"); put("add_rho", f"{AS['spearman']:.2f}", ad + "spearman"); put("add_resid", s(AS["mean_abs_resid"]), ad + "mean_abs_resid")
    put("add_replace", str(AS["by_type"]["replace"]["n"]), ad + "by_type/replace/n")
    put("n_paras", str(len(T["paras"])), ctr + "exp_transforms.json, paragraphs of 40 words or more")
    put("n_sent", str(LX["validity"]["sentences"]), "repro/attribution/expected/lexicon.json validity.sentences")
    for k, a in [("shuffle_a", "shuffle_a"), ("first_half", "first_half_only")]:
        e = T["effects"][a]; an = f"{ctr}exp_transforms.json effects.{a}"
        put(k, s(e["mean_delta"]), an); put(k + "_lo", s(e["ci"][0]), an); put(k + "_hi", s(e["ci"][1]), an)
    for k, a in [("parens", "drop_parentheticals"), ("split_and", "split_at_and_but"), ("mask_num", "numbers_masked"), ("we_to_i", "we_to_I")]:
        e = S[a]; an = f"{ctr}subset_effects.json {a} (paragraphs the edit changes)"
        put(k, s(e["mean"]), an); put(k + "_lo", s(e["ci"][0]), an); put(k + "_hi", s(e["ci"][1]), an); put(k + "_n", str(e["n"]), an)
    for k, a in [("semi", "semicolon_join_pairs"), ("closer", "append_generic_closer"), ("advice", "append_advice"), ("verdict", "append_verdict"),
                 ("contrast", "append_contrast"), ("weran", "append_we_ran"), ("realsent", "append_real_sentence_same_paper")]:
        e = I["effects"][a]; an = f"{ctr}exp_insert.json effects.{a}"
        put(k, s(e["mean"]), an); put(k + "_lo", s(e["ci"][0]), an); put(k + "_hi", s(e["ci"][1]), an); put(k + "_up", f"{round(100 * e['share_up'])}", an + " share_up x 100")
    put("verdict_abs", u(-I["effects"]["append_verdict"]["mean"]), ctr + "exp_insert.json effects.append_verdict (sign dropped)")
    put("null_edit", u(T["effects"]["null_upper_ws"]["mean_delta"]), ctr + "exp_transforms.json effects.null_upper_ws")
    for k, v in [("c_semi", "+0.028"), ("c_contrast", "+0.029"), ("c_advice", "+0.021"), ("c_verdict", "+0.020"), ("c_we", "\u22120.020")]:
        put(k, v, "road-to-robotics journal/papers/ai-map/WRITING_RULES.md section K (311 sentences, ai_phrase_scores.json, 2026-11-05); read, not recomputed here")
    it = J(RL / "results.json")["iteration"]; ia = "repro/rewrite-loop/expected/iterlog.jsonl via results.json iteration"
    put("n_cand", str(it["candidates"]), ia); put("n_lower", str(it["lower"]), ia); put("n_rounds", str(it["paragraph_rounds"]), ia)
    put("share_impr", f"{round(100 * it['share_improved'])}", ia); put("mean_best", u(-it["mean_best_delta"]), ia + " (sign dropped: a drop)")
    put("wd_n", f"{WD['n']:,}", "repro/attribution/expected/word_deletion.json"); put("wd_mean", s(WD["mean"]), "repro/attribution/expected/word_deletion.json")
    put("wd_max", u(WD["max"]), "repro/attribution/expected/word_deletion.json"); put("wd_paras", "20", "repro/attribution/scripts/words.py, paragraphs sorted by score, [:20]")
    v = LX["validity"]; la = "repro/attribution/expected/lexicon.json validity."
    put("lex_held", u(v["heldout_corr"]), la + "heldout_corr"); put("lex_null", u(v["null_p95"]), la + "null_p95")
    put("lex_same", str(v["two_source_same_sign"]), la + "two_source_same_sign"); put("lex_words", str(v["two_source_words"]), la + "two_source_words")
    put("lex_corr", u(v["two_source_corr"], 2), la + "two_source_corr"); put("lex_listed", str(len(LX["lower"]) + len(LX["raise"])), "repro/attribution/expected/lexicon.json lower + raise")
    for p, k in [("register-reproducibility", "reg"), ("jepa-world-model", "jepa"), ("reward-models-stopping-rule", "rew"), ("vla-edge-inference", "vla")]:
        rs = BA[p]; wb_ = sum(r["words_before"] for r in rs); wa = sum(r["words_after"] for r in rs); an = f"repro/rewrite-loop/expected/before_after_rows.json {p}"
        put(k + "_b", u(sum(r["before"] * r["words_before"] for r in rs) / wb_), an); put(k + "_a", u(sum(r["after"] * r["words_after"] for r in rs) / wa), an)
        put(k + "_p", str(len(rs)), an)
    for k, v2 in [("hum1", "0.053"), ("hum2", "0.055"), ("hum3", "0.095")]:
        put(k, v2, "road-to-robotics journal/papers/ai-map/2026-11-04/register-reproducibility/map.md, human reference (3 papers before 2022-11); read, not recomputed here")
    log = [json.loads(l) for l in (RL / "iterlog.jsonl").read_text().splitlines()]

    def lg(paper, para, rnd, cand):
        return next(x["score"] for x in log if x["paper"] == paper and x["para"] == para and x["round"] == rnd and x["cand"] == cand)
    ex = [("jepa_intro", "jepa-world-model", 1, "r1", 0, "r1", 1), ("cold", "register-reproducibility", 11, "r1", 0, "r3", 2), ("classes", "register-reproducibility", 14, "r1", 0, "r1", 1)]
    for k, pa, pr, rb, cb, ra, ca in ex:
        put(k + "_b", u(lg(pa, pr, rb, cb)), f"repro/rewrite-loop/expected/iterlog.jsonl {pa} para {pr} round {rb} cand {cb}")
        put(k + "_a", u(lg(pa, pr, ra, ca)), f"repro/rewrite-loop/expected/iterlog.jsonl {pa} para {pr} round {ra} cand {ca}")
    put("merge_b", u(lg("register-reproducibility", 16, "r2", 0)), "repro/rewrite-loop/expected/iterlog.jsonl register-reproducibility para 16 round r2 cand 0")
    put("merge_a", u(lg("register-reproducibility", 16, "r2", 1)), "repro/rewrite-loop/expected/iterlog.jsonl register-reproducibility para 16 round r2 cand 1")
    words = sum(r["words_before"] for p in BA.values() for r in p)
    put("pass_cost", f"{words / 100 * 0.05:.1f}", f"repro/rewrite-loop/expected/before_after_rows.json, {words} words of the four rendered drafts (paragraphs of 40 words or more) at the listed API rate of $0.05 per 100 words (pangram.com/pricing, read 2026-11-05)")

    HR = J(R / "human-reference" / "expected" / "summary.json"); ha = "repro/human-reference/expected/summary.json"
    put("hr_n", str(HR["human_papers"]), ha); put("hr_dropped", str(len(HR["dropped"])), ha); put("hr_paras", f"{HR['human_paragraphs']:,}", ha)
    put("hr_med", u(HR["paper_mean_median"]), ha); put("hr_min", u(HR["paper_mean_min"]), ha); put("hr_max", u(HR["paper_mean_max"]), ha)
    put("hr_para_med", u(HR["para_median"]), ha); put("hr_gt15", f"{round(100 * HR['share_gt_015'])}", ha + " share_gt_015 x 100"); put("hr_gt25", f"{round(100 * HR['share_gt_025'])}", ha + " share_gt_025 x 100")
    put("hr_ours_above", str(HR["ours_above_human_max"]), ha); put("hr_ours_all", str(len(HR["ours_means"])), ha); put("hr_ours_gt15", f"{round(100 * HR['ours_share_gt_015'])}", ha + " ours_share_gt_015 x 100")
    put("hr_ours_paras", str(HR["ours_paragraphs"]), ha); put("hr_excl", str(HR["excluded_human"]), ha)
    for t, k in [("introduction", "intro"), ("related", "rel"), ("method", "meth"), ("results", "res"), ("conclusion", "conc"), ("other", "oth")]:
        d = HR["types"][t]; put(f"hr_{k}_n", str(d["n"]), ha + f" types.{t}"); put(f"hr_{k}_med", u(d["median"]), ha + f" types.{t}"); put(f"hr_{k}_p90", u(d["p90"]), ha + f" types.{t}")
    for p, k in [("paper-register-reproducibility", "reg"), ("paper-jepa-world-model", "jepa"), ("paper-reward-models-stopping-rule", "rew"), ("paper-vla-edge-inference", "vla")]:
        put(f"hr_ours_{k}", u(HR["ours_means"][p]), ha + f" ours_means.{p}")
    SY = J(R / "human-reference" / "expected" / "style_summary.json"); sa = "repro/human-reference/expected/style_summary.json"
    put("st_maxrho", u(max(abs(v["spearman"]) for v in SY["features"].values()), 2), sa + " features, largest absolute rank correlation")
    for k, key in [("dig", "digit_tok_per100"), ("pas", "passive_per100"), ("con", "contrast_per100"), ("cnx", "connective_per100"), ("com", "comma_per100"), ("wds", "words")]:
        f = SY["features"][key]; d = 0 if key == "words" else 2
        put(f"st_{k}_rho", s(f["spearman"], 2), sa + f" features.{key}.spearman"); put(f"st_{k}_lo", u(f["low"], d), sa + f" features.{key}.low")
        put(f"st_{k}_hi", u(f["high"], d), sa + f" features.{key}.high"); put(f"st_{k}_ours", u(f["ours"], d), sa + f" features.{key}.ours")
    tr = SY["trials"]; put("tr_paras", str(tr["paragraphs"]), sa + " trials"); put("tr_cands", str(tr["candidates"]), sa + " trials"); put("tr_lower", str(tr["lower"]), sa + " trials")
    put("tr_higher", str(tr["higher"]), sa + " trials"); put("tr_mean", s(tr["mean_change"]), sa + " trials.mean_change"); put("tr_not_lower", str(tr["paragraphs"] - tr["paragraphs_best_lower"]), sa + " trials")
    put("st_n_low", str(SY["n_low"]), sa); put("st_n_high", str(SY["n_high"]), sa)
    tl = [json.loads(x) for x in (R / "human-reference" / "expected" / "style_trials.jsonl").read_text().splitlines()]
    rw = {x["cand"]: x["score"] for x in tl if x["paper"] == "register-reproducibility" and x["para"] == 14}
    put("tr_rw_b", u(rw[0]), "repro/human-reference/expected/style_trials.jsonl register-reproducibility para 14 cand 0"); put("tr_rw_a", u(rw[1]), "repro/human-reference/expected/style_trials.jsonl register-reproducibility para 14 cand 1")
    TR = J(R / "triggers" / "expected" / "trigger_summary.json"); SA = J(R / "triggers" / "expected" / "saliency_summary.json"); ta = "repro/triggers/expected/trigger_summary.json"
    ab = {"ai_a": "append_ai_phrase", "ai_p": "prepend_ai_phrase", "mot": "prepend_motivation", "imp": "append_importance", "ptr_a": "append_pointer", "ptr_p": "prepend_pointer",
          "spec_a": "append_specific_paragraph", "spec_p": "prepend_specific_paragraph", "peer": "append_same_register_paragraph", "names": "names_only", "dig": "digits_only",
          "eval": "delete_evaluative_words", "ctl_a": "ctl_append_real_sentence", "ctl_p": "ctl_prepend_real_sentence"}
    for k, key in ab.items():
        for g, gk in (("o", "ours"), ("h", "human_random")):
            e = TR["effects"][gk][key]; put(f"trg_{k}_{g}", s(e["mean"]), ta + f" effects.{gk}.{key}")
            put(f"trg_{k}_{g}_ci", f"{s(e['ci'][0])} to {s(e['ci'][1])}", ta + f" effects.{gk}.{key}.ci")
    put("trg_n_h", str(TR["hosts"]["human_random"]), ta); put("trg_n_o", str(TR["hosts"]["ours"]), ta)
    put("trg_base_h", u(TR["base_mean"]["human_random"]), ta); put("trg_base_o", u(TR["base_mean"]["ours"]), ta)
    sh = [v["top10pct_share_of_positive"] for v in SA.values()]; sa = "repro/triggers/expected/saliency_summary.json"
    put("sal_n", str(len(sh)), sa); put("sal_min", f"{round(100 * min(sh))} %", sa); put("sal_max", f"{round(100 * max(sh))} %", sa)

CITE = {"thai2025editlens": "Thai et al. 2025", "saha2025polish": "Saha and Feizi 2025", "krishna2023paraphrase": "Krishna et al. 2023",
        "cheng2025adversarial": "Cheng et al. 2025", "masrour2025damage": "Masrour et al. 2025"}


def render(src, dst, md=False):
    t = (HERE / src).read_text(); missing = set(re.findall(r"\{\{(\w+)\}\}", t)) - N.keys()
    assert not missing, f"{src}: placeholders without a value: {sorted(missing)}"
    t = re.sub(r"\{\{(\w+)\}\}", lambda m: N[m.group(1)], t)
    if md:
        t = re.sub(r"\[@([^\]]+)\]", lambda m: "(" + "; ".join(CITE[k.strip().lstrip("@")] for k in m.group(1).split(";")) + ")", t)
    (HERE / dst).write_text(t)


def bib():
    """refs.bib is hand-maintained; every \\cite key of main.src.tex has an entry and every entry is cited."""
    keys = set()
    for grp in re.findall(r"\\cite[pt]?\{([^}]*)\}", (HERE / "main.src.tex").read_text()):
        keys |= {k.strip() for k in grp.split(",")}
    have = set(re.findall(r"@\w+\{(\w+),", (HERE / "refs.bib").read_text()))
    assert keys <= have, f"cited but not in refs.bib: {sorted(keys - have)}"
    assert have <= keys, f"in refs.bib but never cited: {sorted(have - keys)}"
    return len(have)


def main():
    collect()
    (HERE / "numbers.json").write_text(json.dumps({k: {"value": N[k], "anchor": A[k]} for k in sorted(N)}, indent=1, ensure_ascii=False))
    render("DRAFT_4p.src.md", "DRAFT_4p.md", md=True)
    if (HERE / "main.src.tex").exists():
        render("main.src.tex", "main.tex")
    print(f"{len(N)} numbers, {bib()} references, rendered")


if __name__ == "__main__":
    main()
