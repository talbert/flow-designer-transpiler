"""Shared step/blob helpers for the test builders (rules as written in the prompt, Sections 7.0-7.10). Local files only."""
import json, copy, pathlib
from fdgen import *
from catalog import entries, full, params
ROOT = pathlib.Path(__file__).parent.parent
trig_fx = json.load(open(ROOT / "fixtures/zurich/blobs/Record_Created_trigger_inputs.json"))["decoded"]
live = json.load(open(ROOT / "fixtures/dev435256/live_examples_by_definition.json"))
MAPPER = {"element_mapping_provider": "com.glide.flow_design.action.data.FlowDesignVariableMapper"}
A = {"Look Up Record": ("9d09f99587003300663ca1bb36cb0ba3", "b93f42810b30030085c083eb37673a63"),
     "Look Up Records": ("43400a1587003300663ca1bb36cb0b4b", "d1c56ec50b30030085c083eb37673a50"),
     "Create Record": ("2de05916c31332002841b63b12d3aee1", "02f0b88cc3c632002841b63b12d3aeff"),
     "Update Record": ("f9d01dd2c31332002841b63b12d3aea1", "baf174c8c3c232002841b63b12d3aee4"),
     "Send Email": ("c1806bf4a70323008299b39f087901cb", "98c181d20b100300d97d8bf637673ab5"),
     "Fire Event": ("80a30edeff30311077a95dac793bf19b", "15e10e5eff30311077a95dac793bf11e"),
     "Send Notification": ("0d8dd9f10f11101051218e8ebc767e27", "7eda5d710f11101051218e8ebc767ec1"),
     "Ask For Approval": ("f8f2e9920b10030085c083eb37673abd", "bae0a1120b10030085c083eb37673a92")}
LG = {"If": "af4e1945c3e232002841b63b12d3ae3e", "Else If": "666e5545c3e232002841b63b12d3ae99", "Else": "1f781bf3c32232002841b63b12d3aee6",
      "End": "d176605ea76103004f27b0d2187901c7", "For Each": "098e1dc5c3e232002841b63b12d3ae33", "Set Flow Variables": "4f787d1e0f9b0010ecf0cc52ff767ea0",
      "Do the following until": "eaeb040687210300e6c2c88fc0e3ec89", "Assign Subflow Outputs": "df4e1945c3e232002841b63b12d3ae3e"}
LUR_DEFAULTS = {"sort_type": ("sort_asc", "a to z"), "if_multiple_records_are_found_action": ("use_first_record", "Return only the first record"),
                "__snc_dont_fail_on_error": ("1", "true")}
def act(name, order, values, parent=None):
    return Step("action", order, entries(A[name][0], values), parent=parent, action_type=A[name][0], action_type_parent=A[name][1], label=name)
def lookup(order, table, label, cond, parent=None):
    return act("Look Up Record", order, {"table": (table, label), "conditions": cond, **LUR_DEFAULTS}, parent)
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
def else_(order, if_step, parent=None): return Step("logic", order, None, parent=parent, connected_to=if_step.ui, logic_def=LG["Else"], label="Else")
def end(order, parent): return Step("logic", order, lobj(), parent=parent, logic_def=LG["End"], label="End")
def foreach(order, items_pill, parent=None):
    p = lparam("19df9109c32632002841b63b12d3aed6", "Items", "items", 20, True, 100, dict(MAPPER), "records", "Records")
    return Step("logic", order, lambda snap: lobj([lentry(p, "{{%s}}" % items_pill, snap)]), parent=parent, logic_def=LG["For Each"], label="For Each")
def var(element, label, order, mandatory=False):
    return {"element": element, "label": label, "type": "string", "type_label": "String", "order": order, "mandatory": mandatory, "id": gid(), "sid": gid(), "uiu": uid()}
def vparam(v, snapshot):
    return lparam(v["sid"] if snapshot else v["id"], v["label"], v["element"], v["order"], bool(v.get("mandatory")), 8000,
                  {"uiType": "string", "uiTypeLabel": "String", **MAPPER, "uiUniqueId": v["uiu"]})
def setvar(order, v, value, parent=None):
    s = Step("logic", order, None, parent=parent, logic_def=LG["Set Flow Variables"], label="Set Flow Variables", flow_variables_assigned=v["element"])
    def vals(snapshot):
        p = vparam(v, snapshot)
        e = {"name": v["element"], "value": value, "displayValue": value, "children": [], "parameter": full(p) if snapshot else p, "scriptActive": False}
        return lobj(inputs=[e], variables=[{"id": p["id"], **e}])
    s.values = vals
    return s
def assign_output(order, v, value):
    s = Step("logic", order, None, logic_def=LG["Assign Subflow Outputs"], label="Assign Subflow Outputs", outputs_assigned=v["element"])
    def vals(snapshot):
        p = vparam(v, snapshot)
        return lobj(outputs=[{"flowLogicInstanceSysId": s.sid if snapshot else s.id, "id": p["id"], "name": v["element"], "value": value, "displayValue": value,
                              "children": [], "parameter": full(p) if snapshot else p, "scriptActive": False}])
    s.values = vals
    return s
def call_subflow(order, sub, inputs, parent=None):
    """inputs: {input element: value}. Points at the subflow's master snapshot; ids are the snapshot's input sys_ids."""
    s = Step("subflow", order, None, parent=parent, subflow=sub.snap, label=sub.name)
    def vals(snapshot):
        out = []
        for i in sub.inputs:
            p = lparam(i["sid"], i["label"], i["element"], i["order"], bool(i.get("mandatory")), 8000, {"uiType": "string", "uiTypeLabel": "String", **MAPPER, "uiUniqueId": i["uiu"]})
            val = inputs.get(i["element"], "")
            out.append({"id": i["sid"], "name": i["element"], "value": val, "displayValue": val, "children": [], "parameter": full(p) if snapshot else p, "scriptActive": False})
        return out
    s.values = vals
    return s
def call_action(order, action, inputs, parent=None):
    """Custom action call: action_type and compiled_snapshot = the action's master snapshot; parameter ids = the snapshot's input sys_ids."""
    def vals(snapshot):
        return [{"id": p["id"], "name": p["name"], "value": inputs.get(p["name"], ""), "displayValue": inputs.get(p["name"], ""), "children": [],
                 "parameter": full(p) if snapshot else p, "scriptActive": False} for p in action.flow_params(snapshot)]
    return Step("action", order, vals, parent=parent, action_type=action.snap, action_type_parent=action.id, compiled_snapshot=action.snap, label=action.name)
def lc(name, label, typ, used, ref="", ref_disp="", parent_table=None, column=None, attrs=True):
    e = {"name": name, "label": label, "reference": ref, "reference_display": ref_disp, "type": typ, "base_type": typ}
    if parent_table: e |= {"parent_table_name": parent_table, "column_name": column}
    e["usedInstances"] = used
    if attrs and not parent_table: e["attributes"] = MAPPER
    return e
# ---- triggers
CREATED = "798916a0c31322002841b63b12d3ae7c"
REC_DEFS = {"Created": (CREATED, "record_create", {}),
            "Updated": ("bb695e60c31322002841b63b12d3aea5", "record_update",
                        {"table": "1dda12e0c31322002841b63b12d3aea8", "condition": "bb9adea0c31322002841b63b12d3ae67", "run_on_extended": "6cd14b76072200103bf10705afd30093",
                         "run_flow_in": "4ecd76460f103300b599bca2ff767e0d", "run_when_user_list": "3f8d5577c7002300f4eba1425a9763e6",
                         "run_when_setting": "48395df3c7002300f4eba1425a976372", "run_when_user_setting": "cf9bd937c7002300f4eba1425a976356",
                         "trigger_strategy": ("c19523d8c31932002841b63b12d3aea1", 101)}),
            "Created or Updated": ("a45d9180c32222002841b63b12d3aea7", "record_create_or_update",
                        {"table": "cf1e1980c32222002841b63b12d3aea0", "condition": "707dd180c32222002841b63b12d3aecb", "run_on_extended": "1c4203b6072200103bf10705afd300b8",
                         "run_flow_in": "231e76460f103300b599bca2ff767e11", "run_when_user_list": "cb9d5577c7002300f4eba1425a9763ef",
                         "run_when_setting": "a22a9137c7002300f4eba1425a976376", "run_when_user_setting": "ed3c9d37c7002300f4eba1425a976347",
                         "trigger_strategy": ("2b9def50c31132002841b63b12d3ae5b", 200)})}
STRATEGY = [("once", "Once"), ("unique_changes", "For each unique change"), ("always", "Only if not currently running"), ("every", "For every update")]
def record_trigger(kind, table, table_label, condition, strategy="once"):
    """Record trigger built as the prompt says: the Record Created entry shape (Appendix B) with this definition's parameter ids, plus trigger_strategy."""
    d, ttype, ids = REC_DEFS[kind]
    def build(tsid):
        out = []
        for e in copy.deepcopy(trig_fx):
            e["triggerInstanceSysId"] = tsid; e["fromTemplate"] = False
            for c in e.get("choiceList") or []:
                c.setdefault("fSequence", -1)
                if "fParameters" in c: c["fParameters"]["name"] = "var__m_sys_hub_trigger_input_" + d
            if e["name"] in ids: e["parameter"]["id"] = ids[e["name"]]
            if kind != "Created" and e["name"] == "condition": e["parameter"]["attributes"] = {"extended_operators": "VALCHANGES;CHANGESFROM;CHANGESTO", **e["parameter"]["attributes"]}
            val = {"table": (table, table_label), "condition": (condition, condition)}.get(e["name"])
            if val: e["value"], e["displayValue"] = val
            out.append(e)
        if "trigger_strategy" in ids:
            pid, order = ids["trigger_strategy"]
            ch = lambda start: [{"label": l, "value": v, "order": start + n} for n, (v, l) in enumerate(STRATEGY)]
            out.append({"triggerInstanceSysId": tsid, "label": "Run Trigger", "internalType": "choice", "dependent": "",
                        "choiceList": [{"fValue": v, "fLabel": l, "fImage": "", "fParameters": {"name": "var__m_sys_hub_trigger_input_" + d}, "fSelected": False, "fUsed": False,
                                        "fMissing": False, "fSequence": -1} for v, l in STRATEGY],
                        "mandatory": False, "order": order, "name": "trigger_strategy", "value": strategy, "displayValue": "",
                        "parameter": {"children": [], "id": pid, "label": "Run Trigger", "name": "trigger_strategy", "type": "choice", "order": order, "extended": False,
                                      "mandatory": False, "readOnly": False, "hint": "Run Trigger every time the condition matches, or only the first time.", "maxsize": 40,
                                      "reference": "", "choices": ch(1), "defaultChoices": ch(1), "choiceOption": "3", "table": "", "columnName": "", "defaultValue": "once",
                                      "defaultDisplayValue": "Once", "use_dependent": False, "fShowReferenceFinder": False, "local": False, "attributes": {}, "ref_qual": "",
                                      "dependent_on": ""},
                        "displayField": "", "scriptActive": False, "fromTemplate": False})
        return out
    return {"name": kind, "type": ttype, "definition": d, "inputs": build}
def timer_entry(pid, label, name, typ, order, value, attrs=None):
    """Scheduled-trigger entry in the Daily entry shape (Appendix B), built from the definition's sys_hub_trigger_input row."""
    return {"label": label, "internalType": typ, "mandatory": True, "fromTemplate": False, "order": order, "valueSysId": "", "name": name, "value": value, "children": [],
            "parameter": {"children": [], "id": pid, "label": label, "name": name, "type": typ, "order": order, "extended": False, "mandatory": True, "readOnly": False,
                          "hint": "", "maxsize": 40 if name.startswith("day_") else 100, "reference": "", "reference_display": "", "choiceOption": "", "table": "", "columnName": "",
                          "defaultValue": "", "use_dependent": False, "fShowReferenceFinder": False, "local": False, "attributes": {**(attrs or {}), **MAPPER}, "ref_qual": "",
                          "dependent_on": ""},
            "displayField": "", "scriptActive": False}
TIMER = {"Weekly": ("cf352104c32222002841b63b12d3ae1f", "weekly"), "Monthly": ("2ca52504c32222002841b63b12d3ae4a", "monthly"),
         "Run Once": ("0a76e504c32222002841b63b12d3aeac", "run_once"), "Daily": ("89142dc0c32222002841b63b12d3ae8a", "daily")}
def timer_trigger(kind, entries_): return {"name": kind, "type": TIMER[kind][1], "definition": TIMER[kind][0], "inputs": entries_}

# ---- added for test 7: Try/Catch, Parallel, Wait for a duration
LG.update({"Try": "07223332de022010ec58424b73829721", "Catch": "35d60003e6022010a5e40cdd1254dd21", "Do the following in Parallel": "5d31e5dedfe50300b61ecae83df26326",
           "Parallel Branch": "a1168de173311300b61e66476bf6a7d0", "Wait for a duration of time": "fdb2541473031300b61e66476bf6a70e"})
def plain(kind, order, parent=None, connected_to=None): return Step("logic", order, lobj(), parent=parent, connected_to=connected_to, logic_def=LG[kind], label=kind)
_catch = json.load(open(ROOT / "fixtures/dev435256/catch_live.json")); _wait = json.load(open(ROOT / "fixtures/dev435256/wait_duration_live.json"))
def _shape(obj, snapshot):
    o = copy.deepcopy(obj)
    for e in o["inputs"]: e["parameter"] = full(e["parameter"]) if snapshot else {("type_label" if k == "typeLabel" else k): v for k, v in e["parameter"].items() if k not in ("fDataStructure", "sysClassName") }
    return o
def catch(order, try_step, parent=None):
    return Step("logic", order, lambda snap: _shape(_catch, snap), parent=parent, connected_to=try_step.ui, logic_def=LG["Catch"], label="Catch")
def wait_seconds(order, seconds, parent=None):
    vals = {"duration_type": ("explicit_duration", "Explicit duration"), "timer_duration": ("1970-01-01 00:00:%02d" % seconds, "%d Seconds" % seconds),
            "timer_relative_duration_operator": ("after", "after")}
    def v(snap):
        o = _shape(_wait, snap)
        for e in o["inputs"]: e["value"], e["displayValue"] = vals.get(e["name"], ("", ""))
        return o
    return Step("logic", order, v, parent=parent, logic_def=LG["Wait for a duration of time"], label="Wait for a duration of time")
