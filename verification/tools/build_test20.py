"""Test 20: a compact flow built from actions never tried before, using ONLY what a catalog line holds
(the action's sys_id, its input names and their internal types). Local files only."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
CAT = json.load(open(V / "fixtures/dev435256/full_catalog.json"))
def cat_act(name, scope, order, values, parent=None):
    a = [x for x in CAT["actions"] if x["name"] == name and x["sys_scope.scope"] == scope and x["state"] == "published"]
    assert len(a) == 1, (name, len(a)); a = a[0]
    types = {r["element"]: r["internal_type"] for r in CAT["action_inputs"] if r["model"] == a["sys_id"]}
    return Step("action", order, [short(k, v, types[k]) for k, v in values.items()], parent, action_type=a["sys_id"], label=name)
OUT = V / "test_import_20261119u"; T = "Created_1.current"
s1 = cat_act("Log", "global", 1, {"log_level": "info", "log_message": "TT20 log for {{%s.number}}" % T})
s2 = cat_act("Create Task", "global", 2, {"task_table": "incident_task", "field_values": "short_description=TT20 task for {{%s.number}}^incident={{%s.sys_id}}^EQ" % (T, T), "wait": "false"})
s3 = cat_act("Create or Update Record", "global", 3, {"table_name": "sys_user", "fields": "user_name=tt20.user^first_name=TT20^last_name={{%s.number}}^EQ" % T})
s4 = cat_act("Update Multiple Records", "global", 4, {"table_name": "incident_task", "conditions": "short_descriptionSTARTSWITHTT20 task for {{%s.number}}" % T, "field_values": "description=TT20 multi^EQ"})
s5 = cat_act("Add Worknote", "sn_itsm_spoke", 5, {"ah_task": "{{%s}}" % T, "ah_work_note": "TT20 worknote via ITSM Spoke"})
s6 = cat_act("Create Incident Task on Incident", "sn_itsm_spoke", 6, {"ah_incident": "{{%s}}" % T})
s7 = act("Update Record", 7, {"table_name": "incident", "record": "{{%s}}" % T,
    "values": "description=TT20 task [{{%s.Record.number}}] upsert [{{%s.status}}] count [{{%s.count}}] itask [{{%s.Incident Task.number}}]^EQ" % (s2.ui, s3.ui, s4.ui, s6.ui)})
s8 = cat_act("Delete Record", "global", 8, {"record": "{{%s.Incident Task}}" % s6.ui})
f = Flow("TT20 Catalog Actions", "Transpiler test 20. Seven actions never tried before, written from catalog lines only, for incidents whose short description starts with TT20RUN. Safe to delete.",
         record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT20RUN"), [s1, s2, s3, s4, s5, s6, s7, s8])
US = "Transpiler Test 20261119u"
xml, usb = actgen.update_set(US, "Transpiler prompt test 20 on dev435256: untried actions from catalog lines. Safe to delete.", [], [f])
(OUT / "transpiler_test_20261119u.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261119u.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []}]}, indent=1))
print("set", usb, "| flow", f.id)
