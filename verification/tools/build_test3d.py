"""Test 3d: a custom action built from the platform's export shape with every id, cid and complex-object name regenerated. Local files only."""
import re, sys, json, time, pathlib, xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdgen import gid, uid, jhash, el, audit_tail, TS, WHO
V = pathlib.Path(__file__).parent.parent
src = (V / "fixtures/dev435256/platform_unload_action_0_current.xml").read_text()
root = ET.fromstring(src.encode())
own = {i for i in (c.findtext("sys_id") for c in root) if i and re.fullmatch(r"[0-9a-f]{32}", i)}
cids = {c.findtext("cid") for c in root if c.tag == "sys_hub_step_instance" and c.findtext("cid")}
fd = set(re.findall(r"FD[0-9a-f]{32}", src))
mp = {**{i: gid() for i in own}, **{c: uid() for c in cids}, **{n: "FD" + gid() for n in fd}}
p = src
for a, b in mp.items(): p = p.replace(a, b)
NAME = "TT3e Generated Action"
p = p.replace("TT3c Copy of Create Outage", NAME).replace("tt3c_copy_of_create_outage", "tt3e_generated_action")
A = mp[root[0].findtext("sys_id")]
US = "Transpiler Test 20261119d"; us_a, us_b, g = gid(), gid(), gid(); ph = jhash(p)
out = ['<?xml version="1.0" encoding="UTF-8"?>', f'<unload unload_date="{TS}">', '<sys_remote_update_set action="INSERT_OR_UPDATE">',
 '<application display_value="Global">global</application>', "<application_name>Global</application_name>", "<application_scope>global</application_scope>",
 "<application_version/>", "<collisions/>", "<commit_date/>", "<deleted/>", el("description", "Transpiler prompt test 3d: one custom action. Safe to delete."),
 "<inserted/>", el("name", US), "<origin_sys_id/>", '<parent display_value=""/>', "<release_date/>", '<remote_base_update_set display_value=""/>', "<remote_parent_id/>",
 el("remote_sys_id", us_a), "<state>loaded</state>", "<summary/>", "<sys_class_name>sys_remote_update_set</sys_class_name>", el("sys_created_by", WHO), el("sys_created_on", TS),
 el("sys_id", us_b), "<sys_mod_count>0</sys_mod_count>", *audit_tail(), '<update_set display_value=""/>', '<update_source display_value=""/>', "<updated/>", "</sys_remote_update_set>",
 '<sys_update_xml action="INSERT_OR_UPDATE">', "<action>INSERT_OR_UPDATE</action>", '<application display_value="Global">global</application>', "<category>retrieved</category>", "<comments/>",
 el("name", f"sys_hub_action_type_definition_{A}"), "<payload><![CDATA[" + p.replace("]]>", "]]]]><![CDATA[>") + "]]></payload>", el("payload_hash", ph),
 el("remote_update_set", us_b, display_value=US), "<replace_on_upgrade>false</replace_on_upgrade>", el("sys_created_by", WHO), el("sys_created_on", TS), el("sys_id", gid()),
 "<sys_mod_count>0</sys_mod_count>", el("sys_recorded_at", format((int(time.time() * 1000) << 28) | 1, "x")), *audit_tail(), "<table>sys_hub_action_type_definition</table>",
 el("target_name", NAME), el("type", "Action"), "<update_domain>global</update_domain>", el("update_guid", g), el("update_guid_history", f"{g}:{ph}"),
 '<update_set display_value=""/>', "<view/>", "</sys_update_xml>", "</unload>"]
f = V / "test_import_20261119d/transpiler_test_20261119d.xml"; f.write_text("\n".join(out) + "\n")
assert ET.parse(f).getroot().find("sys_update_xml/payload").text == p
json.dump({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": us_b, "action": {"name": NAME, "id": A}}, open(V / "test_import_20261119d/manifest.json", "w"), indent=1)
print("remapped ids", len(own), "cids", len(cids), "complex names", len(fd), "| action", A, "| retrieved set", us_b)
