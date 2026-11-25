"""Test 23 round 2: Inbound Email trigger with no reply record type (new emails), and one guess at the catalog variables shape. Local files only."""
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
OUT = V / "test_import_20261120g"
E = "{{Inbound Email_1.inbound_email}}"
a1 = G("Get Email Header", 1, {"email_record": E, "target_header": "X-TT23"})
a2 = G("Get Latest Response Text From Email", 2, {"email_record": E})
a3 = act("Create Record", 3, {"table_name": "incident", "values": "short_description=Made by TT23A2 from email^description=TT23A2 subject [{{Inbound Email_1.subject}}] from [{{Inbound Email_1.from_address}}] header [{{%s.header_value}}] text [{{%s.latest_response_text}}]^EQ" % (a1.ui, a2.ui)})
a4 = G("Associate Record to Email", 4, {"email_record": E, "target_record": "{{%s.record}}" % a3.ui})
a5 = G("Move Email Attachments to Record", 5, {"email_record": E, "target_record": "{{%s.record}}" % a3.ui})
fa = Flow("TT23A2 Inbound Email New", "Transpiler test 23 round 2. Inbound Email trigger with no reply record type, for emails whose subject contains TT23NEW. Safe to delete.",
          inbound_email("subjectLIKETT23NEW", "", 40, True), [a1, a2, a3, a4, a5])
T = "Created_1.current"; CUR = "{{%s}}" % T
ABEL, ITEM = "62826bf03710200044e0bfc8bcbe5df1", "439fef5b83e41310d6401665eeaad379"
e1 = G("Submit Catalog Item Request", 1, {"catalog_item": ITEM, "catalog_item_inputs": json.dumps({"variables": [{"name": "tt9_note", "value": "hello from TT21E7"}]}), "sysparm_quantity": "1", "sysparm_requested_for": ABEL, "wait_for_completion": "0"})
e2 = act("Update Record", 2, {"table_name": "incident", "record": CUR, "values": "description=TT21E7 ritm [{{%s.requested_item.number}}] status [{{%s.status}}]^EQ" % (e1.ui, e1.ui)})
fe = Flow("TT21E7 Submit Catalog Item Guess", "Transpiler test 21 round 3. Submit Catalog Item Request with a guessed variables shape, for incidents whose short description starts with TT21E7 RUN. Safe to delete.",
          record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT21E7 RUN"), [e1, e2])
flows = [fa, fe]
US = "Transpiler Test 20261120g"
xml, usb = actgen.update_set(US, "Transpiler prompt test 23 round 2 on dev435256. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120g.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120g.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); print(json.dumps([f.id for f in flows]))
