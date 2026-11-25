"""Test 27: Make a decision with execution run_all and an Otherwise branch (shape read from a designer-saved flow), and Submit Catalog Item Request
with six more catalog variable types. Local files only."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
CAT = json.load(open(V / "fixtures/dev435256/full_catalog.json"))
def cat_act(name, scope, order, values, parent=None):
    a = [x for x in CAT["actions"] if x["name"] == name and x["sys_scope.scope"] == scope and x["state"] == "published" and x.get("active", "true") != "false"]
    assert len(a) == 1, (name, len(a)); a = a[0]
    types = {r["element"]: r["internal_type"] for r in CAT["action_inputs"] if r["model"] == a["sys_id"]}
    return Step("action", order, [short(k, v, types[k]) for k, v in values.items()], parent, action_type=a["sys_id"], label=name)
G = lambda n, o, v, p=None: cat_act(n, "global", o, v, p)
OUT = V / "test_import_20261120n"; T = "Created_1.current"; CUR = "{{%s}}" % T
upd = lambda order, text, field="description", parent=None: act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "%s=%s^EQ" % (field, text)}, parent)
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT27%s RUN" % k)
def xl(defid, label, order, inputs=(), parent=None, extra=None, **arrays):
    o = lobj([lin(n, v) for n, v in inputs]); o.update(arrays)
    s = Step("logic", order, o, parent, None, logic_definition=defid, label=label); s.extra = extra or {}; return s
DT, DT_INPUT = "51b35a90c3723010a9f5e548fa40ddb2", "26e3da90c3723010a9f5e548fa40dde7"
ANS_TEST, ANS_DEFAULT = "d3332eb353323010b846ddeeff7b12bd", "f988ce5b9b6630100290af417ef04beb"
MD, DEC = "578e90270b2313009002cab937673a7d", "b1f542d673331300612c273ffff6a7c7"
d1 = xl(MD, "Make a decision", 1, [("decision_label", "TT27 pick"), ("decision_table", DT), ("execution", "run_all"), ("answer_table", "sys_hub_flow"), ("has_branches", "1"), ("include_otherwise", "1")],
        extra={"decision_table": DT},
        decisionTableInputs=[{"id": DT_INPUT, "name": "instance_type", "value": "{{%s.description}}" % T, "displayValue": "{{%s.description}}" % T, "children": [], "parameter": {"type": "choice"}, "scriptActive": False}])
d2 = xl(DEC, "Decision", 2, [("label", "Test"), ("answer", ANS_TEST)], d1)
d3 = upd(3, "TT27D branch TEST", parent=d2)
d4 = xl(DEC, "Decision", 4, [("label", "Default"), ("answer", ANS_DEFAULT)], d1)
d5 = upd(5, "TT27D branch DEFAULT", parent=d4)
d6 = xl(DEC, "Decision", 6, [("label", ""), ("answer", "")], d1)                 # the Otherwise branch: empty answer
d7 = upd(7, "TT27D branch OTHERWISE", parent=d6)
d8 = upd(8, "TT27D after the branches", "close_notes")
fd = Flow("TT27D Decision Run All Otherwise", "Transpiler test 27. Make a decision with run_all and an Otherwise branch, for incidents whose short description starts with TT27D RUN. Safe to delete.",
          trig("D"), [d1, d2, d3, d4, d5, d6, d7, d8])

ITEM, GEORGE, ABEL = "6d6883e783a09310d6401665eeaad35d", "67484bb0eb32010045e1a5115206fee6", "62826bf03710200044e0bfc8bcbe5df1"
CTL = {"8": "Reference", "7": "CheckBox", "9": "Date", "10": "Date/Time", "1": "Yes / No", "5": "Select Box"}
def cvar(i, n, x, c, label, order):
    return {"id": i, "label": label, "name": n, "type": "string", "type_label": "String", "order": order, "extended": False, "mandatory": False, "readonly": False, "maxsize": 0,
            "children": [], "data_structure": "", "reference": "", "reference_display": "", "ref_qual": "", "choiceOption": "", "table": "item_option_new", "columnName": "",
            "defaultValue": "", "defaultDisplayValue": "", "use_dependent": False, "dependent_on": "", "internal_link": "", "show_ref_finder": False, "local": False,
            "attributes": {"catalogType": c, "catalogTypeLabel": CTL[c], "fd_hide_inline_script_widget": "true"}, "sys_class_name": "", "canDrop": True, "isNew": True,
            "userHasChanged": True, "field_name": n, "value": x}
VARS = [("29688fe783a09310d6401665eeaad38e", "tt26_user", GEORGE, "8", "User"), ("7d688fe783a09310d6401665eeaad3b1", "tt26_check", "true", "7", "Check"),
        ("bd688fe783a09310d6401665eeaad3cc", "tt26_date", "2026-12-24", "9", "Date"), ("71684be783a09310d6401665eeaad3bd", "tt26_datetime", "2026-12-24 10:30:00", "10", "Date time"),
        ("f5688fe783a09310d6401665eeaad3fe", "tt26_yesno", "Yes", "1", "Yes no"), ("3568cfe783a09310d6401665eeaad319", "tt26_choice", "beta", "5", "Choice")]
e1 = G("Submit Catalog Item Request", 1, {"catalog_item": ITEM, "catalog_item_inputs": json.dumps({"inputs": [cvar(*a, order=k) for k, a in enumerate(VARS)]}, separators=(",", ":")),
       "sysparm_quantity": "1", "sysparm_requested_for": ABEL, "wait_for_completion": "0"})
e2 = upd(2, "TT27E ritm [{{%s.requested_item.number}}] status [{{%s.status}}] err [{{%s.error_message}}]" % (e1.ui, e1.ui, e1.ui))
fe = Flow("TT27E Catalog Variable Types", "Transpiler test 27. Submit Catalog Item Request with reference, check box, date, date/time, yes/no and select box variables, for incidents whose short description starts with TT27E RUN. Safe to delete.",
          trig("E"), [e1, e2])
# V: Get Visual Task Board Lanes reads its input as JSON text {"value": "<board sys_id>"} (its own script); a bare sys_id returned no lanes in test 26
g1 = cat_act("Get Visual Task Board Lanes", "sn_vtb_ah", 1, {"board": json.dumps({"value": "3e770b6783a09310d6401665eeaad3df"})})
g2 = upd(2, "TT27V lanes [{{%s.output}}]" % g1.ui)
fv = Flow("TT27V Board Lanes", "Transpiler test 27. Get Visual Task Board Lanes with the board as JSON text, for incidents whose short description starts with TT27V RUN. Safe to delete.", trig("V"), [g1, g2])
flows = [fd, fe, fv]
US = "Transpiler Test 20261120n"
xml, usb = actgen.update_set(US, "Transpiler prompt test 27 on dev435256: decision options and catalog variable types. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120n.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120n.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); print(json.dumps([f.id for f in flows]))
