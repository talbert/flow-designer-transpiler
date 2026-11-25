"""Test 3b: subflow with inputs/outputs + a flow using the remaining OOB actions and logic types. Local files only."""
import json, copy, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdgen import *
from catalog import entries, full, params
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "test_import_20261119b"
trig_fx = json.load(open(ROOT / "fixtures/zurich/blobs/Record_Created_trigger_inputs.json"))["decoded"]
NEVER = "short_description=TRANSPILER_TEST_NEVER_MATCH_20261119B"
MAPPER = {"element_mapping_provider": "com.glide.flow_design.action.data.FlowDesignVariableMapper"}
A = {  # action type -> (action_type, action_type_parent)
 "Look Up Record": ("9d09f99587003300663ca1bb36cb0ba3", "b93f42810b30030085c083eb37673a63"),
 "Look Up Records": ("43400a1587003300663ca1bb36cb0b4b", "d1c56ec50b30030085c083eb37673a50"),
 "Create Record": ("2de05916c31332002841b63b12d3aee1", "02f0b88cc3c632002841b63b12d3aeff"),
 "Update Record": ("f9d01dd2c31332002841b63b12d3aea1", "baf174c8c3c232002841b63b12d3aee4"),
 "Send Email": ("c1806bf4a70323008299b39f087901cb", "98c181d20b100300d97d8bf637673ab5"),
 "Fire Event": ("80a30edeff30311077a95dac793bf19b", "15e10e5eff30311077a95dac793bf11e")}
LG = {"If": "af4e1945c3e232002841b63b12d3ae3e", "Else If": None, "Else": "1f781bf3c32232002841b63b12d3aee6", "End": "d176605ea76103004f27b0d2187901c7"}
live = json.load(open(ROOT / "fixtures/dev435256/live_examples_by_definition.json"))
for n in ["Else If", "For Each", "Set Flow Variables", "Do the following until", "Assign Subflow Outputs"]: LG[n] = live[n]["def"]

def act(name, order, values, parent=None):
    return Step("action", order, entries(A[name][0], values), parent=parent, action_type=A[name][0], action_type_parent=A[name][1], label=name)
def lparam(pid, label, name, order, mand, size, attrs, typ="string", tl="String"):
    return {"children": [], "type_label": tl, "id": pid, "label": label, "name": name, "type": typ, "order": order, "extended": False, "mandatory": mand,
            "readOnly": False, "hint": "", "maxsize": size, "reference": "", "reference_display": "", "choiceOption": "", "table": "", "columnName": "",
            "defaultValue": "", "use_dependent": False, "fShowReferenceFinder": False, "local": False, "attributes": attrs, "ref_qual": "", "dependent_on": "", "help": ""}
def lentry(p, value, snapshot, **extra):
    return {**extra, "name": p["name"], "value": value, "displayValue": value, "children": [], "parameter": full(p) if snapshot else p, "scriptActive": False}
def lobj(inputs=(), variables=(), outputs=()):
    return {"outputsToAssign": list(outputs), "inputs": list(inputs), "variables": list(variables), "decisionTableInputs": [], "dynamicInputs": [], "workflowInputs": []}
COND = {"If": ("f0af19c1c32632002841b63b12d3aea3", "9a5f5105c32632002841b63b12d3ae46", 10, 20),
        "Else If": ("f0af19c1c32632002841b63b12d3aea2", "f0af19c1c32632002841b63b12d3aea1", 10, 20),
        "Do the following until": ("bda2cb0473031300612c273ffff6a750", "d7138f0473031300612c273ffff6a78c", 100, 200)}
def cond(kind, order, label, condition, parent=None, connected_to=None):
    n_id, c_id, n_o, c_o = COND[kind]
    def v(snapshot):
        return lobj([lentry(lparam(n_id, "Condition Label", "condition_name", n_o, False, 255, MAPPER | {"use_basic_input": "true"}), label, snapshot),
                     lentry(lparam(c_id, "Condition", "condition", c_o, True, 2000, MAPPER | {"is_scriptable": "false"}), condition, snapshot)])
    return Step("logic", order, v, parent=parent, connected_to=connected_to, logic_def=LG[kind], label=kind)
def var(element, label, order, mandatory=False):
    return {"element": element, "label": label, "type": "string", "type_label": "String", "order": order, "mandatory": mandatory, "id": gid(), "sid": gid(), "uiu": uid()}
def vparam(v, snapshot):
    return lparam(v["sid"] if snapshot else v["id"], v["label"], v["element"], v["order"], bool(v.get("mandatory")), 8000,
                  {"uiType": "string", "uiTypeLabel": "String", **MAPPER, "uiUniqueId": v["uiu"]})
def lc(name, label, typ, used, ref="", ref_disp="", parent_table=None, column=None, attrs=True):
    e = {"name": name, "label": label, "reference": ref, "reference_display": ref_disp, "type": typ, "base_type": typ}
    if parent_table: e |= {"parent_table_name": parent_table, "column_name": column}
    e["usedInstances"] = used
    if attrs and not parent_table: e["attributes"] = MAPPER
    return e
def created_trigger(tsid):
    out = []
    for e in copy.deepcopy(trig_fx):
        val = {"table": ("incident", "Incident"), "condition": (NEVER, NEVER)}.get(e["name"])
        e["triggerInstanceSysId"] = tsid; e["fromTemplate"] = False
        for c in e.get("choiceList") or []: c.setdefault("fSequence", -1)
        if val: e["value"], e["displayValue"] = val
        out.append(e)
    return out

# ---------------- subflow: input user_name, output found
s_in = var("user_name", "User name", 1, True); s_out = var("found", "Found", 1)
sl = act("Look Up Record", 1, {"table": ("sys_user", "User"), "conditions": "user_name={{subflow.user_name}}", "sort_type": ("sort_asc", "a to z"),
                               "if_multiple_records_are_found_action": ("use_first_record", "Return only the first record"), "__snc_dont_fail_on_error": ("1", "true")})
sa = Step("logic", 2, None, logic_def=LG["Assign Subflow Outputs"], label="Assign Subflow Outputs", outputs_assigned="found")
def sa_vals(snapshot):
    p = vparam(s_out, snapshot); val = "{{%s.status}}" % sl.ui
    return lobj(outputs=[{"flowLogicInstanceSysId": sa.sid if snapshot else sa.id, "id": p["id"], "name": "found", "value": val, "displayValue": val,
                          "children": [], "parameter": full(p) if snapshot else p, "scriptActive": False}])
sa.values = sa_vals
subflow = Flow("TT3b Subflow", None, [sl, sa], ftype="subflow", run_as="user", inputs=[s_in], outputs=[s_out],
               description="Transpiler test 3b subflow. One lookup. Safe to delete.",
               label_cache=[lc("subflow.user_name", "Input➛User name", "string", {sl.ui: ["conditions"]}),
                            lc(sl.ui + ".status", "1 - Look Up Record➛Status", "choice", {sa.ui: ["found"]})])

# ---------------- flow using the remaining actions and logic
note = var("note", "Note", 1)
T = "Created_1.current"
a1 = act("Look Up Records", 1, {"table": ("sys_user", "User"), "conditions": "active=true", "sort_type": ("sort_asc", "a to z"), "max_results": "5"})
fe_p = lparam("19df9109c32632002841b63b12d3aed6", "Items", "items", 20, True, 100, dict(MAPPER), "records", "Records")
l2 = Step("logic", 2, lambda snap: lobj([lentry(fe_p, "{{%s.Records}}" % a1.ui, snap)]), logic_def=LG["For Each"], label="For Each")
a3 = act("Create Record", 3, {"table_name": ("incident", "Incident"), "values": "short_description=TT3b created for {{%s.item.user_name}}" % l2.ui}, parent=l2.ui)
l4 = Step("logic", 4, None, logic_def=LG["Set Flow Variables"], label="Set Flow Variables", flow_variables_assigned="note")
def l4_vals(snapshot):
    p = vparam(note, snapshot); val = "set by {{%s.number}}" % T
    e = {"name": "note", "value": val, "displayValue": val, "children": [], "parameter": full(p) if snapshot else p, "scriptActive": False}
    return lobj(inputs=[e], variables=[{"id": p["id"], **e}])
l4.values = l4_vals
l5 = cond("If", 5, "Priority 1", "{{%s.priority}}=1" % T)
a6 = act("Update Record", 6, {"record": "{{%s}}" % T, "table_name": ("incident", "Incident"), "values": "short_description=TT3b updated"}, parent=l5.ui)
l7 = cond("Else If", 7, "Priority 2", "{{%s.priority}}=2" % T, connected_to=l5.ui)
a8 = act("Send Email", 8, {"record": "{{%s}}" % T, "table_name": ("incident", "Incident"), "watermark_email": ("1", "true"), "ah_to": "nobody@example.com",
                           "ah_subject": "TT3b {{%s.number}}" % T, "ah_body": "<p>Note: {{flow_variable.note}}</p>"}, parent=l7.ui)
l9 = Step("logic", 9, None, connected_to=l5.ui, logic_def=LG["Else"], label="Else")
a10 = act("Fire Event", 10, {"event_name": ("4d0b7e44c611227b010619b714a8b983", "incident.assigned.to.group"), "record": "{{%s}}" % T,
                             "table": ("incident", "Incident"), "parm1": "{{flow_variable.note}}"}, parent=l9.ui)
s11 = Step("subflow", 11, None, parent=l9.ui, subflow=subflow.snap, label="TT3b Subflow")
def s11_vals(snapshot):
    p = lparam(s_in["sid"], "User name", "user_name", 1, True, 8000, {"uiType": "string", "uiTypeLabel": "String", **MAPPER, "uiUniqueId": s_in["uiu"]})
    val = "{{%s.caller_id.user_name}}" % T
    return [{"id": s_in["sid"], "name": "user_name", "value": val, "displayValue": val, "children": [], "parameter": full(p) if snapshot else p, "scriptActive": False}]
s11.values = s11_vals
l12 = Step("logic", 12, lobj(), parent=l9.ui, logic_def=LG["End"], label="End")
l13 = cond("Do the following until", 13, "Note is set", "{{flow_variable.note}}ISNOTEMPTY")
a14 = act("Look Up Record", 14, {"table": ("sys_user", "User"), "conditions": "user_name=admin", "sort_type": ("sort_asc", "a to z"),
                                 "if_multiple_records_are_found_action": ("use_first_record", "Return only the first record"), "__snc_dont_fail_on_error": ("1", "true")}, parent=l13.ui)
labels = [
 lc(a1.ui + ".Records", "1 - Look Up Records➛User Records", "records", {l2.ui: ["items"]}, ref="sys_user", ref_disp="User"),
 lc(l2.ui + ".item.user_name", "2 - For Each➛User Record➛User ID", "string", {a3.ui: ["values"]}, parent_table="sys_user", column="user_name"),
 lc(T, "Trigger - Record Created➛Incident Record", "reference", {a6.ui: ["record"], a8.ui: ["record"], a10.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False),
 lc(T + ".number", "Trigger - Record Created➛Incident Record➛Number", "string", {l4.ui: ["note"], a8.ui: ["ah_subject"]}, parent_table="incident", column="number"),
 lc(T + ".priority", "Trigger - Record Created➛Incident Record➛Priority", "integer", {l5.ui: ["condition"], l7.ui: ["condition"]}, parent_table="incident", column="priority"),
 lc(T + ".caller_id.user_name", "Trigger - Record Created➛Incident Record➛Caller➛User ID", "string", {s11.ui: ["user_name"]}, parent_table="sys_user", column="user_name"),
 lc("flow_variable.note", "Flow Variables➛Note", "string", {a8.ui: ["ah_body"], a10.ui: ["parm1"], l13.ui: ["condition"]})]
main = Flow("TT3b Actions", {"name": "Created", "type": "record_create", "definition": "798916a0c31322002841b63b12d3ae7c", "inputs": created_trigger},
            [a1, l2, a3, l4, l5, a6, l7, a8, l9, a10, s11, l12, l13, a14], variables=[note], label_cache=labels,
            description="Transpiler test 3b. Trigger never matches, so no step ever runs. Safe to delete.")
US = "Transpiler Test 20261119b"
xml, usb = update_set(US, "Transpiler prompt test 3b on dev435256. One subflow and one flow. Safe to delete.", [subflow, main])
(OUT / "transpiler_test_20261119b.xml").write_text(xml)
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb,
    "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in f.steps]} for f in (subflow, main)]}, indent=1))
print("written", len(xml), "bytes;", [(f.name, f.id) for f in (subflow, main)], "retrieved set", usb)
