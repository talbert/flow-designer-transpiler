"""Test 3a: how much of each blob does the platform need? Plus daily and catalog triggers. Local files only."""
import json, copy, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdgen import *
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "test_import_20261119a"
trig_fx = json.load(open(ROOT / "fixtures/zurich/blobs/Record_Created_trigger_inputs.json"))["decoded"]
lur_fx = json.load(open(ROOT / "fixtures/zurich/blobs/Look_Up_Record_values.json"))["decoded"]
tc = json.load(open(ROOT / "fixtures/dev435256/triggers_timer_catalog.json"))
LUR, LUR_PARENT = "9d09f99587003300663ca1bb36cb0ba3", "b93f42810b30030085c083eb37673a63"
IF_DEF = "af4e1945c3e232002841b63b12d3ae3e"
NEVER = "short_description=TRANSPILER_TEST_NEVER_MATCH_20261119"
MAPPER = {"element_mapping_provider": "com.glide.flow_design.action.data.FlowDesignVariableMapper"}

# ---- full / compact shapes (control)
FULL_ORDER = ["children","id","label","name","type","typeLabel","order","extended","mandatory","readOnly","hint","maxsize","reference",
              "reference_display","fDataStructure","choices","defaultChoices","choiceOption","table","columnName","defaultValue",
              "use_dependent","fShowReferenceFinder","local","attributes","sysClassName","ref_qual","dependent_on","help"]
def full(p):
    p = dict(p); p.setdefault("help", "")
    if "type_label" in p: p["typeLabel"] = p.pop("type_label")
    for k, dv in {"typeLabel": "", "choices": [], "defaultChoices": [], "fDataStructure": "", "sysClassName": "", "reference_display": "", "children": []}.items(): p.setdefault(k, dv)
    return {k: p[k] for k in FULL_ORDER if k in p} | {k: v for k, v in p.items() if k not in FULL_ORDER}
def compact(p):
    p = dict(p); p.setdefault("help", "")
    if "typeLabel" in p: p["type_label"] = p.pop("typeLabel")
    return p
LUR_VALS = {"table": None, "conditions": None, "sort_column": ("", ""), "sort_type": ("sort_asc", "a to z"),
            "if_multiple_records_are_found_action": ("use_first_record", "Return only the first record"), "__snc_dont_fail_on_error": None}
def lur(table, label, cond, mode):
    def build(snapshot):
        out = []
        for e in copy.deepcopy(lur_fx):
            v = {"table": (table, label), "conditions": (cond, cond)}.get(e["name"]) or LUR_VALS[e["name"]] or (e["value"], e.get("displayValue", e["value"]))
            if mode == "A":
                if e["name"] in ("table", "conditions"): out.append({"name": e["name"], "value": v[0]})
            elif mode == "B":
                out.append({"id": e["id"], "name": e["name"], "value": v[0], "displayValue": v[1],
                            "parameter": {"id": e["parameter"]["id"], "name": e["name"], "type": e["parameter"]["type"], "label": e["parameter"]["label"]}})
            else:
                out.append({"id": e["id"], "name": e["name"], "value": v[0], "displayValue": v[1], "children": [],
                            "parameter": full(e["parameter"]) if snapshot else compact(e["parameter"]), "scriptActive": False})
        return out
    return build
def created_trigger(mode):
    def build(tsid):
        out = []
        for e in copy.deepcopy(trig_fx):
            val = {"table": ("incident", "Incident"), "condition": (NEVER, NEVER)}.get(e["name"])
            if mode == "A":
                if val: out.append({"name": e["name"], "value": val[0]})
                continue
            if mode == "B":
                out.append({"name": e["name"], "value": val[0] if val else e.get("value", ""), "displayValue": val[1] if val else e.get("displayValue", ""),
                            "parameter": {"id": e["parameter"]["id"], "name": e["name"], "type": e["parameter"]["type"]}})
                continue
            e["triggerInstanceSysId"] = tsid; e["fromTemplate"] = False
            for c in e.get("choiceList") or []: c.setdefault("fSequence", -1)
            if val: e["value"], e["displayValue"] = val
            out.append(e)
        return out
    return build
def if_values(pill, mode):
    def P(pid, label, name, order, mand, size, attrs):
        return {"children": [], "type_label": "String", "id": pid, "label": label, "name": name, "type": "string", "order": order, "extended": False,
                "mandatory": mand, "readOnly": False, "hint": "", "maxsize": size, "reference": "", "reference_display": "", "choiceOption": "", "table": "",
                "columnName": "", "defaultValue": "", "use_dependent": False, "fShowReferenceFinder": False, "local": False, "attributes": attrs,
                "ref_qual": "", "dependent_on": "", "help": ""}
    cond = "{{%s}}ISNOTEMPTY" % pill
    if mode == "A": ins = [{"name": "condition_name", "value": "Admin user found"}, {"name": "condition", "value": cond}]
    elif mode == "B": ins = [{"name": "condition_name", "value": "Admin user found", "displayValue": "Admin user found", "parameter": {"id": "f0af19c1c32632002841b63b12d3aea3", "name": "condition_name", "type": "string"}},
                             {"name": "condition", "value": cond, "displayValue": cond, "parameter": {"id": "9a5f5105c32632002841b63b12d3ae46", "name": "condition", "type": "string"}}]
    else: ins = [{"name": "condition_name", "value": "Admin user found", "displayValue": "Admin user found", "children": [],
                  "parameter": P("f0af19c1c32632002841b63b12d3aea3", "Condition Label", "condition_name", 10, False, 255, MAPPER | {"use_basic_input": "true"}), "scriptActive": False},
                 {"name": "condition", "value": cond, "displayValue": cond, "children": [],
                  "parameter": P("9a5f5105c32632002841b63b12d3ae46", "Condition", "condition", 20, True, 2000, MAPPER | {"is_scriptable": "false"}), "scriptActive": False}]
    return {"outputsToAssign": [], "inputs": ins, "variables": [], "decisionTableInputs": [], "dynamicInputs": [], "workflowInputs": []}

def record_flow(name, mode, with_label_cache):
    s1 = Step("action", 1, lur("sys_user", "User", "user_name=admin", mode), action_type=LUR, action_type_parent=LUR_PARENT, label="Look Up Record")
    s2 = Step("logic", 2, None, logic_def=IF_DEF, label="If"); s2.values = if_values(s1.ui + ".Record", mode)
    s3 = Step("action", 3, lur("sys_user_group", "Group", "nameISNOTEMPTY", mode), parent=s2.ui, action_type=LUR, action_type_parent=LUR_PARENT, label="Look Up Record")
    lc = [{"name": s1.ui + ".Record", "label": "1➛User Record", "reference": "sys_user", "reference_display": "User", "type": "reference",
           "base_type": "reference", "usedInstances": {s2.ui: ["condition"]}, "attributes": MAPPER}] if with_label_cache else []
    return Flow(name, {"name": "Created", "type": "record_create", "definition": "798916a0c31322002841b63b12d3ae7c", "inputs": created_trigger(mode)},
                [s1, s2, s3], description=f"Transpiler test 3a ({mode}). Trigger never matches. Safe to delete.", label_cache=lc)

daily_e = copy.deepcopy(tc["daily"]["trigger_instance"]["trigger_inputs__decoded"]); daily_e[0]["value"] = "1970-01-01 03:15:00"
cat_e = copy.deepcopy(tc["catalog"]["trigger_instance"]["trigger_inputs__decoded"])
def cat_inputs(tsid):
    e = copy.deepcopy(cat_e)
    for x in e: x["triggerInstanceSysId"] = tsid
    return e
flows = [
 record_flow("TT3a Min A names only", "A", False),
 record_flow("TT3a Min B ids no boilerplate", "B", True),
 record_flow("TT3a Full with label cache", "F", True),
 Flow("TT3a Daily", {"name": "Daily", "type": "daily", "definition": "89142dc0c32222002841b63b12d3ae8a", "inputs": daily_e},
      [Step("action", 1, lur("sys_user", "User", "user_name=admin", "F"), action_type=LUR, action_type_parent=LUR_PARENT, label="Look Up Record")],
      description="Transpiler test 3a daily trigger. One lookup. Safe to delete."),
 Flow("TT3a Catalog", {"name": "Service Catalog", "type": "service_catalog", "definition": "c43a1011c36813002841b63b12d3ae15", "inputs": cat_inputs},
      [Step("action", 1, lur("sys_user", "User", "user_name=admin", "F"), action_type=LUR, action_type_parent=LUR_PARENT, label="Look Up Record")],
      description="Transpiler test 3a catalog trigger. One lookup. Safe to delete.")]
US = "Transpiler Test 20261119a"
xml, usb = update_set(US, "Transpiler prompt test 3a on dev435256. Five harmless flows. Safe to delete.", flows)
(OUT / "transpiler_test_20261119a.xml").write_text(xml)
man = {"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb,
       "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "trigger": f.trigger["id"], "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid} for s in f.steps]} for f in flows]}
(OUT / "manifest.json").write_text(json.dumps(man, indent=1))
print("written", len(xml), "bytes;", [(f.name, f.id) for f in flows])
