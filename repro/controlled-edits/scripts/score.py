"""score.py file.json  -> prints scores; file.json = list of texts (or dict label->text)"""
import json, sys, time, uuid
from pathlib import Path
D = Path(__file__).resolve().parent
data = json.load(open(sys.argv[1]))
labels = list(data) if isinstance(data, dict) else list(range(len(data)))
texts = [data[l] for l in labels]
rid = uuid.uuid4().hex[:8] + ".json"
(D / "req" / rid).write_text(json.dumps(texts))
while not (D / "resp" / rid).exists():
    time.sleep(0.3)
time.sleep(0.1)
for l, s, t in zip(labels, json.loads((D / "resp" / rid).read_text()), texts):
    print(f"{s:.3f}  {l}  ({len(t.split())}w)")
