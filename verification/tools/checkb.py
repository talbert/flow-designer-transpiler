"""Read-only check B: compare the platform's re-export of each flow in a manifest with the sent XML.
Usage: python3 checkb.py <test dir> [alias]"""
import os
import json, subprocess, sys, re, gzip, base64, pathlib, xml.etree.ElementTree as ET
D = pathlib.Path(sys.argv[1]); A = sys.argv[2] if len(sys.argv) > 2 else "pdi435256"
FX = D / "readback"; FX.mkdir(exist_ok=True)
def q(t, qs, f, lim=50):
    o = subprocess.run(["now-sdk","query",t,"-a",A,"-q",qs,"-f",f,"--limit",str(lim),"-o","json"],capture_output=True,text=True,timeout=300,cwd=os.environ.get("FDT_SDK_DIR", "."))
    l = [x for x in o.stdout.splitlines() if x.startswith("{")]
    return json.loads(l[-1]).get("records", []) if l else []
def dec(v):
    try: return json.loads(gzip.decompress(base64.b64decode(v)))
    except Exception: return None
def walk(a, b, path=""):
    out = []
    if type(a) != type(b): return [(path, a, b)]
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append((path + "." + k, "<ABSENT>", b[k]))
            elif k not in b: out.append((path + "." + k, a[k], "<ABSENT>"))
            else: out += walk(a[k], b[k], path + "." + k)
    elif isinstance(a, list):
        if len(a) != len(b): out.append((path + "[len]", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)): out += walk(x, y, f"{path}[{x.get('name', i) if isinstance(x, dict) else i}]")
    elif a != b: out.append((path, a, b))
    return out
man = json.load(open(D / "manifest.json"))
xmlfile = next(D.glob("*.xml"))
sent = {ux.findtext("name"): ET.fromstring(ux.find("payload").text.encode()) for ux in ET.parse(xmlfile).getroot().findall("sys_update_xml")}
IGN = {"sys_updated_on", "sys_updated_by", "sys_mod_count", "sys_created_on", "sys_created_by"}
for fl in man["flows"]:
    F = fl["id"]; print(f"\n=== {fl['name']} ({F[:8]})")
    r = q("sys_hub_flow", f"sys_id={F}", "status,active,version,remote_trigger_id,version_record,label_cache")
    if not r: print("  NOT FOUND"); continue
    r = r[0]; lc = r.pop("label_cache", ""); print("  flow:", r, "| label_cache chars:", len(lc))
    uv = q("sys_update_version", f"name=sys_hub_flow_{F}^state=current", "sys_id,sys_created_on,source_table,payload", 1)
    if not uv: print("  no platform export"); continue
    p = uv[0]["payload"]; (FX / f"{fl['name'].replace(' ', '_')}_platform.xml").write_text(p)
    plat = ET.fromstring(p.encode()); s = sent[f"sys_hub_flow_{F}"]
    if p.strip() == ET.tostring(s, encoding="unicode").strip() or len(plat) == len(s) and uv[0]["source_table"] != "sys_update_set": pass
    ops = lambda root: [(c.tag, c.get("action")) for c in root]
    extra = [o for o in ops(plat) if o not in ops(s)]; missing = [o for o in ops(s) if o not in ops(plat)]
    print("  export source:", uv[0]["source_table"], uv[0]["sys_created_on"], "| op kinds only in platform:", sorted(set(extra)), "| only in sent:", sorted(set(missing)))
    recs = lambda root: {(c.tag, c.findtext("sys_id")): c for c in root if c.get("action") == "INSERT_OR_UPDATE"}
    sr, pr = recs(s), recs(plat)
    print("  records added by platform:", sorted({k[0] for k in pr if k not in sr}), "| dropped:", [k for k in sr if k not in pr])
    for k in [k for k in pr if k not in sr]:
        if k[0] in ("sys_flow_record_trigger", "sys_flow_timer_trigger", "sys_flow_catalog_trigger", "sys_flow_trigger_plan", "sys_trigger_runner_mapping", "sys_flow_subflow_plan"):
            print("   +", k[0], {e.tag: (e.text or "")[:120] for e in pr[k] if (e.text or "") and e.tag not in IGN and not e.tag.startswith("sys_")})
    for k in sr:
        if k not in pr: continue
        fa = {e.tag: (e.text or "") for e in sr[k]}; fb = {e.tag: (e.text or "") for e in pr[k]}
        diffs = []
        for f in sorted(set(fa) | set(fb)):
            va, vb = fa.get(f, "<ABSENT>"), fb.get(f, "<ABSENT>")
            if va == vb or f in IGN: continue
            da, db = dec(va), dec(vb)
            if da is not None and db is not None:
                w = walk(da, db)
                if w: diffs.append(f"{f}: {len(w)} blob diffs, e.g. {[(x[0], str(x[1])[:40], str(x[2])[:40]) for x in w[:3]]}")
            else: diffs.append(f"{f}: {va[:50]!r} -> {vb[:90]!r}")
        if diffs: print("  ~", k[0].replace("sys_hub_", ""), k[1][:6], "|", " ; ".join(diffs)[:700])
