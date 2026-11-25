"""Read-only query helper (GET only) for the test instance."""
import os
import json, subprocess, gzip, base64
def q(t, qs, f, lim=50, alias=os.environ.get("FDT_SDK_ALIAS", "pdi435256")):
    o = subprocess.run(["now-sdk","query",t,"-a",alias,"-q",qs,"-f",f,"--limit",str(lim),"-o","json"],capture_output=True,text=True,timeout=300,cwd=os.environ.get("FDT_SDK_DIR", "."))
    l = [x for x in o.stdout.splitlines() if x.startswith("{")]
    if not l: raise RuntimeError(o.stdout[-400:] + o.stderr[-400:])
    return json.loads(l[-1]).get("records", [])
def dec(v):
    try: return json.loads(gzip.decompress(base64.b64decode(v)))
    except Exception: return None
