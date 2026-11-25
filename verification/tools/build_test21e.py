"""Test 21E bisect: which catalog input makes publish fail with 'Expected a JsonObject but was JsonPrimitive'. One small flow per suspect. Local files only."""
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
OUT = V / "test_import_20261120d"; T = "Created_1.current"; CUR = "{{%s}}" % T
ABEL, ITEM, PRODUCER = "62826bf03710200044e0bfc8bcbe5df1", "439fef5b83e41310d6401665eeaad379", "3f1dd0320a0a0b99000a53f7604a2ef9"
upd = lambda order, text: act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "description=%s^EQ" % text})
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT21%s RUN" % k)
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "1"
flows = []
# E1: Submit Catalog Item Request + tasks
e1 = G("Submit Catalog Item Request", 1, {"catalog_item": ITEM, "catalog_item_inputs": "tt9_note=hello from TT21E", "sysparm_quantity": "1", "sysparm_requested_for": ABEL, "wait_for_completion": "0"})
e2 = I("Create Catalog Task on Request Item", 2, {"ah_request_item": "{{%s.requested_item}}" % e1.ui})
e3 = G("Get Catalog Item from Task", 3, {"task": "{{%s.requested_item}}" % e1.ui})
e4 = upd(4, "TT21E1 ritm [{{%s.requested_item.number}}] status [{{%s.status}}] sctask [{{%s.Catalog Task.number}}] item [{{%s.item_id}}]" % (e1.ui, e1.ui, e2.ui, e3.ui))
flows.append(Flow("TT21E1 Submit Catalog Item", "Transpiler test 21. Submit Catalog Item Request, for incidents whose short description starts with TT21E1 RUN. Safe to delete.", trig("E1"), [e1, e2, e3, e4]))
# E2: Record Producer
p1 = G("Record Producer", 1, {"catalog_item": PRODUCER, "catalog_item_inputs": "comments=Made by TT21E record producer^urgency=3", "record_table": "incident", "_snc_dont_fail_on_error": "0"})
p2 = upd(2, "TT21E2 produced [{{%s.record}}] pstatus [{{%s.status}}] err [{{%s.error_message}}]" % (p1.ui, p1.ui, p1.ui))
flows.append(Flow("TT21E2 Record Producer", "Transpiler test 21. Record Producer, for incidents whose short description starts with TT21E2 RUN. Safe to delete.", trig("E2"), [p1, p2]))
# E3: Get Catalog Item Variables + Object To String Array
v1 = G("Get Catalog Item Variables", 1, {"catalog_item": ITEM})
v2 = upd(2, "TT21E3 vars [{{%s.output}}]" % v1.ui)
flows.append(Flow("TT21E3 Catalog Item Variables", "Transpiler test 21. Get Catalog Item Variables, for incidents whose short description starts with TT21E3 RUN. Safe to delete.", trig("E3"), [v1, v2]))
o1 = G("Get Catalog Item Variables", 1, {"catalog_item": ITEM})
o2 = G("Object To String Array", 2, {"array_object": "{{%s.output}}" % o1.ui})
o3 = upd(3, "TT21E4 arr [{{%s.object_array}}]" % o2.ui)
flows.append(Flow("TT21E4 Object To String Array", "Transpiler test 21. Object To String Array, for incidents whose short description starts with TT21E4 RUN. Safe to delete.", trig("E4"), [o1, o2, o3]))
US = "Transpiler Test 20261120d"
xml, usb = actgen.update_set(US, "Transpiler prompt test 21E on dev435256: catalog actions, one flow each. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120d.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120d.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); print(json.dumps([f.id for f in flows]))
