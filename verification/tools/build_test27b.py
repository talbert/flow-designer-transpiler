"""Test 27b (yes/no variable spellings), built from the Test 27 helpers: Make a decision with execution run_all and an Otherwise branch (shape read from a designer-saved flow), and Submit Catalog Item Request
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
OUT = V / "test_import_20261120o"; T = "Created_1.current"; CUR = "{{%s}}" % T
upd = lambda order, text, field="description", parent=None: act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "%s=%s^EQ" % (field, text)}, parent)
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT27%s RUN" % k)
def xl(defid, label, order, inputs=(), parent=None, extra=None, **arrays):
    o = lobj([lin(n, v) for n, v in inputs]); o.update(arrays)
    s = Step("logic", order, o, parent, None, logic_definition=defid, label=label); s.extra = extra or {}; return s
ITEM, GEORGE, ABEL = "6d6883e783a09310d6401665eeaad35d", "67484bb0eb32010045e1a5115206fee6", "62826bf03710200044e0bfc8bcbe5df1"
CTL = {"8": "Reference", "7": "CheckBox", "9": "Date", "10": "Date/Time", "1": "Yes / No", "5": "Select Box"}
def cvar(i, n, x, c, label, order):
    return {"id": i, "label": label, "name": n, "type": "string", "type_label": "String", "order": order, "extended": False, "mandatory": False, "readonly": False, "maxsize": 0,
            "children": [], "data_structure": "", "reference": "", "reference_display": "", "ref_qual": "", "choiceOption": "", "table": "item_option_new", "columnName": "",
            "defaultValue": "", "defaultDisplayValue": "", "use_dependent": False, "dependent_on": "", "internal_link": "", "show_ref_finder": False, "local": False,
            "attributes": {"catalogType": c, "catalogTypeLabel": CTL[c], "fd_hide_inline_script_widget": "true"}, "sys_class_name": "", "canDrop": True, "isNew": True,
            "userHasChanged": True, "field_name": n, "value": x}
YN = ("f5688fe783a09310d6401665eeaad3fe", "tt26_yesno", None, "1", "Yes no")
def sub(order, val):
    return G("Submit Catalog Item Request", order, {"catalog_item": ITEM, "catalog_item_inputs": json.dumps({"inputs": [cvar(YN[0], YN[1], val, YN[3], YN[4], 0)]}, separators=(",", ":")),
             "sysparm_quantity": "1", "sysparm_requested_for": ABEL, "wait_for_completion": "0"})
y1, y2, y3 = sub(1, "yes"), sub(2, "true"), sub(3, "1")
y4 = upd(4, "TT27Y yes [{{%s.requested_item.number}}] true [{{%s.requested_item.number}}] one [{{%s.requested_item.number}}]" % (y1.ui, y2.ui, y3.ui))
flows = [Flow("TT27Y Yes No Variable", "Transpiler test 27b. Yes/No catalog variable written as yes, true and 1, for incidents whose short description starts with TT27Y RUN. Safe to delete.", trig("Y"), [y1, y2, y3, y4])]
US = "Transpiler Test 20261120o"
xml, usb = actgen.update_set(US, "Transpiler prompt test 27b on dev435256: yes/no catalog variable. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120o.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120o.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); print(json.dumps([f.id for f in flows]))
