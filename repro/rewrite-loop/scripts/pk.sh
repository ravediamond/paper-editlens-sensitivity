#!/bin/bash
# pk.sh paper para cand#  : apply candidate from the last batch
python3 - "$@" <<'PY'
import json,subprocess,sys
p,i,k=sys.argv[1],sys.argv[2],int(sys.argv[3])
open("pick.txt","w").write(json.load(open(f"cand_{p}_{i}.json"))[k-1])
print(p,i,subprocess.run(["python3","wb.py","apply",p,i,"pick.txt"],capture_output=True,text=True).stdout.strip())
PY
