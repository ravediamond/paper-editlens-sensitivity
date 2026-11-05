"""loo.py paper para... : leave-one-sentence-out contributions in the working copy"""
import sys, re
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
sys.path.insert(0, "/home/jetson/workspace/road-to-robotics/scripts")
import paper_sentences as S
p = a[0]
for i in map(int, a[1:]):
    t = wb.render(p, wb.para_src(p, i)); ss = S.split_sentences(t)
    texts = [t] + [" ".join(x for j, x in enumerate(ss) if j != k) for k in range(len(ss))]
    sc = wb.score_texts(texts)
    print(f"--- para {i}: {sc[0]:.3f}")
    for k, s in enumerate(ss):
        print(f"  {sc[0]-sc[k+1]:+.3f}  {s[:110]}")
