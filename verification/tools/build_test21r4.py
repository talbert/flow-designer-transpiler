"""Test 21 round 4: catalog variables in the shape Workflow Studio saves, {"inputs":[{id,name,value}]}, reduced to id, name, type, value and attributes.catalogType per variable. Local files only."""
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
G = lambda n, o, v, p=None: cat_act(n, "global", o, v, p)
I = lambda n, o, v, p=None: cat_act(n, "sn_itsm_spoke", o, v, p)
OUT = V / "test_import_20261120i"; T = "Created_1.current"; CUR = "{{%s}}" % T
ABEL, ITEM, PRODUCER = "62826bf03710200044e0bfc8bcbe5df1", "439fef5b83e41310d6401665eeaad379", "3f1dd0320a0a0b99000a53f7604a2ef9"
cvars = lambda *v: json.dumps({"inputs": [{"id": i, "name": n, "type": "string", "value": x, "attributes": {"catalogType": c}} for i, n, x, c in v]}, separators=(",", ":"))
upd = lambda order, text: act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "description=%s^EQ" % text})
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT21%s RUN" % k)
e1 = G("Submit Catalog Item Request", 1, {"catalog_item": ITEM, "catalog_item_inputs": cvars(("9f9fef5b83e41310d6401665eeaad3b3", "tt9_note", "hello from TT21E10 {{%s.number}}" % T, "6")),
       "sysparm_quantity": "1", "sysparm_requested_for": ABEL, "wait_for_completion": "0"})
e2 = I("Create Catalog Task on Request Item", 2, {"ah_request_item": "{{%s.requested_item}}" % e1.ui})
e3 = G("Get Catalog Item from Task", 3, {"task": "{{%s.requested_item}}" % e1.ui})
e4 = upd(4, "TT21E10 ritm [{{%s.requested_item.number}}] status [{{%s.status}}] sctask [{{%s.Catalog Task.number}}] item [{{%s.item_id}}]" % (e1.ui, e1.ui, e2.ui, e3.ui))
f1 = Flow("TT21E10 Submit Catalog Item Inputs", "Transpiler test 21 round 4. Submit Catalog Item Request with variables in the designer's shape, for incidents whose short description starts with TT21E10 RUN. Safe to delete.", trig("E10"), [e1, e2, e3, e4])
p1 = G("Record Producer", 1, {"catalog_item": PRODUCER, "catalog_item_inputs": cvars(("3f272c500a0a0b990059c24380a2bc02", "comments", "Made by TT21E11 record producer", "2"), ("5a33d0ef0a0a0b9b007b906f6c589c57", "urgency", "3", "5")),
       "record_table": "incident", "_snc_dont_fail_on_error": "0"})
p2 = upd(2, "TT21E11 produced [{{%s.record}}] pstatus [{{%s.status}}] err [{{%s.error_message}}]" % (p1.ui, p1.ui, p1.ui))
f2 = Flow("TT21E11 Record Producer Inputs", "Transpiler test 21 round 4. Record Producer with variables in the designer's shape, for incidents whose short description starts with TT21E11 RUN. Safe to delete.", trig("E11"), [p1, p2])
flows = [f1, f2]
US = "Transpiler Test 20261120i"
xml, usb = actgen.update_set(US, "Transpiler prompt test 21 round 4 on dev435256: catalog variables. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120i.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120i.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); print(json.dumps([f.id for f in flows]))
