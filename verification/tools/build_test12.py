"""Test 12: the Fluent SDK's own flow payload (draft, short blobs, no snapshot), re-identified, sent through an update set. Local files only."""
import sys, re, json, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import actgen
from fdgen import gid, uid, TS, el, audit_tail, WHO
V = pathlib.Path(__file__).parent.parent
src = next((V / "sdk_probe").glob("sys_hub_flow_*.xml")).read_text()
APP, APPN, SC = "8f6baeba9ba94590969cbe31fc69e713", "TT11 SDK Probe", "x_906694_tt11"
KEEP = {APP, "798916a0c31322002841b63b12d3ae7c", "9d09f99587003300663ca1bb36cb0ba3", "f9d01dd2c31332002841b63b12d3aea1", "af4e1945c3e232002841b63b12d3ae3e", "1f781bf3c32232002841b63b12d3aee6"}
ids = sorted(set(re.findall(r"\b[0-9a-f]{32}\b", src))); uu = sorted(set(re.findall(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", src)))
own = [i for i in ids if i not in KEEP]; print("kept:", [i for i in ids if i in KEEP], "| replaced:", len(own), "| uuids:", len(uu))
p = src
for i in own: p = p.replace(i, gid())
for u in uu: p = p.replace(u, uid())
p = p.replace("TT11 SDK Probe Flow", "TT12 SDK Shape Via Update Set").replace("TT11RUN", "TT12RUN").replace("SDK IF branch", "TT12 IF branch").replace("SDK ELSE branch", "TT12 ELSE branch")
newF = re.search(r"<sys_id>([0-9a-f]{32})</sys_id>", p[p.index("<sys_hub_flow "):]).group(1)
US = "Transpiler Test 20261119l2"; us_a, us_b = gid(), gid()
out = ['<?xml version="1.0" encoding="UTF-8"?>', f'<unload unload_date="{TS}">', '<sys_remote_update_set action="INSERT_OR_UPDATE">', f'<application display_value="{APPN}">{APP}</application>',
       f"<application_name>{APPN}</application_name>", f"<application_scope>{SC}</application_scope>", "<application_version>0.0.1</application_version>", "<collisions/>", "<commit_date/>", "<deleted/>",
       el("description", "Transpiler prompt test 12: the Fluent SDK's own payload shape (draft, short blobs, no snapshot) sent through an update set. Safe to delete."), "<inserted/>", el("name", US), "<origin_sys_id/>",
       '<parent display_value=""/>', "<release_date/>", '<remote_base_update_set display_value=""/>', "<remote_parent_id/>", el("remote_sys_id", us_a), "<state>loaded</state>", "<summary/>",
       "<sys_class_name>sys_remote_update_set</sys_class_name>", el("sys_created_by", WHO), el("sys_created_on", TS), el("sys_id", us_b), "<sys_mod_count>0</sys_mod_count>", *audit_tail(),
       '<update_set display_value=""/>', '<update_source display_value=""/>', "<updated/>", "</sys_remote_update_set>"]
x = [l.replace('<application display_value="Global">global</application>', f'<application display_value="{APPN}">{APP}</application>')
     for l in actgen.sys_update_xml(us_b, US, 1, f"sys_hub_flow_{newF}", "sys_hub_flow", "TT12 SDK Shape Via Update Set", "Flow", p)]
f = V / "test_import_20261119l/transpiler_test_20261119l2.xml"; f.write_text("\n".join(out + x + ["</unload>"]) + "\n")
import xml.etree.ElementTree as ET; ET.parse(f)
json.dump({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": us_b, "flows": [{"name": "TT12 SDK Shape Via Update Set", "id": newF, "snap": "", "steps": [1, 2, 3, 4, 5]}]}, open(V / "test_import_20261119l/manifest.json", "w"), indent=1)
print("set", us_b, "| flow", newF)
