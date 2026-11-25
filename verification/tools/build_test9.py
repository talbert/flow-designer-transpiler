"""Test 9: Service Catalog trigger at runtime, Get Catalog Variables, Create Catalog Task. Local files only."""
import json, sys, pathlib, copy
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdlib import *
import actgen
OUT = ROOT / "test_import_20261119j"
ITEM, VAR = "439fef5b83e41310d6401665eeaad379", "9f9fef5b83e41310d6401665eeaad3b3"
A["Get Catalog Variables"] = ("330ba3abc31013002841b63b12d3aee8", "22f0b88cc3c632002841b63b12d3aeff")
A["Create Catalog Task"] = ("af51fd0e73141300612c273ffff6a785", "f597c41073081300612c273ffff6a767")
tc = json.load(open(ROOT / "fixtures/dev435256/triggers_timer_catalog.json"))
cat_e = copy.deepcopy(tc["catalog"]["trigger_instance"]["trigger_inputs__decoded"])
def cat_inputs(tsid):
    e = copy.deepcopy(cat_e)
    for x in e: x["triggerInstanceSysId"] = tsid
    return e
R = "Service Catalog_1.request_item"
g1 = act("Get Catalog Variables", 1, {"requested_item": "{{%s}}" % R, "template_catalog_item": (ITEM, "TT9 Test Item"), "catalog_variables": VAR + ":item_option_new"})
c2 = act("Create Catalog Task", 2, {"ah_table_name": ("sc_task", "sc_task"), "ah_requested_item": "{{%s}}" % R, "ah_short_description": "TT9 task, note [{{%s.tt9_note}}]" % g1.ui, "ah_wait": ("0", "false")})
u3 = act("Update Record", 3, {"record": "{{%s}}" % R, "table_name": ("sc_req_item", "Requested Item"),
                              "values": "description=TT9 catalog flow ran, note [{{%s.tt9_note}}], task [{{%s.Catalog Task.number}}]" % (g1.ui, c2.ui)})
f = Flow("TT9 Runtime Catalog", {"name": "Service Catalog", "type": "service_catalog", "definition": "c43a1011c36813002841b63b12d3ae15", "inputs": cat_inputs}, [g1, c2, u3],
         description="Transpiler test 9. Runs when the TT9 Test Item is ordered. Safe to delete.",
         label_cache=[lc(R, "Trigger - Service Catalog➛Requested Item Record", "reference", {g1.ui: ["requested_item"], c2.ui: ["ah_requested_item"], u3.ui: ["record"]}, ref="sc_req_item", ref_disp="Requested Item", attrs=False),
                      {"name": g1.ui + ".tt9_note", "label": "1 - Get Catalog Variables➛tt9_note", "reference": "", "reference_display": "tt9_note", "type": "string", "base_type": "string",
                       "usedInstances": {c2.ui: ["ah_short_description"], u3.ui: ["values"]}, "attributes": {"catalogType": "6", "catalogTypeLabel": "Single Line Text"}},
                      lc(c2.ui + ".Catalog Task.number", "2 - Create Catalog Task➛Catalog Task➛Number", "string", {u3.ui: ["values"]}, parent_table="sc_task", column="number")])
US = "Transpiler Test 20261119j"
xml, usb = actgen.update_set(US, "Transpiler prompt test 9 on dev435256: one catalog flow. Safe to delete.", [], [f])
(OUT / "transpiler_test_20261119j.xml").write_text(xml)
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "catalog_item": ITEM, "variable": VAR,
    "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in f.steps]}]}, indent=1))
print("set", usb, "| flow", f.id)
from fdgen import unblob
import xml.etree.ElementTree as ET
p = ET.fromstring(ET.parse(OUT / "transpiler_test_20261119j.xml").getroot().find("sys_update_xml/payload").text.encode())
for c in p:
    if c.tag == "sys_hub_action_instance_v2" and c.get("action") == "INSERT_OR_UPDATE" and c.findtext("flow") == f.id:
        print([(e["name"], str(e["value"])[:50], e["parameter"]["type"]) for e in unblob(c.findtext("values"))])
