"""Compact-mode generator written from the prompt's compact rules (draft, short blob entries, no snapshot, definition ids). Local files only.
Not derived from SDK output files, except the seven record-trigger entries, which are the literal list in Appendix E.3."""
import json, re, gzip, base64, pathlib, xml.etree.ElementTree as ET
from fdgen import gid, uid, TS
import fdlib
from catalog import params
V = pathlib.Path(__file__).parent.parent
MAPPER = "element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper"
hy = lambda g: f"{g[:8]}-{g[8:12]}-{g[12:16]}-{g[16:20]}-{g[20:]}"
enc = lambda o: base64.b64encode(gzip.compress(json.dumps(o, ensure_ascii=False).encode(), mtime=0)).decode()
cj = lambda o: json.dumps(o, separators=(",", ":"), ensure_ascii=False)
def rec(tag, sid, fields, update_name=None):
    e = ET.Element(tag, {"action": "INSERT_OR_UPDATE", "apply_defaults": "true"})
    ET.SubElement(e, "sys_id").text = sid
    s = ET.SubElement(e, "sys_scope", {"display_value": "Global"}); s.text = "global"
    ET.SubElement(e, "sys_update_name").text = update_name or f"{tag}_{sid}"
    for k, v in fields.items(): ET.SubElement(e, k).text = v
    return e
def dm(tag, q): return ET.Element(tag, {"action": "delete_multiple", "query": q})
LG = dict(fdlib.LG, **{"Exit Loop": "7444b31c37063110ac85cdd734924bff", "Skip Iteration": "48de1b5837063110ac85cdd734924b15"})

# ---------------- steps
class Step:
    def __init__(self, kind, order, values, parent=None, connected_to=None, **fields):
        self.kind, self.order, self.values, self.parent, self.connected_to, self.fields = kind, order, values, parent, connected_to, fields
        self.id = gid(); self.ui = hy(self.id)
def short(name, value, typ): return {"name": name, "value": value, "displayValue": value, "scriptActive": False, "parameter": {"type": typ}}
def act(name, order, values, parent=None):
    """Built-in action: one short entry per input that is set; the type is the input's internal type on the action definition."""
    t = fdlib.A[name][0]; types = {p["name"]: p["type"] for p in params(t)}
    return Step("action", order, [short(k, v, types[k]) for k, v in values.items()], parent, action_type=t, label=name)
def call(action, order, values, parent=None):
    return Step("action", order, [short(k, v, action.input_types[k]) for k, v in values.items()], parent, action_type=action.id, label=action.name)
def lobj(inputs=()): return {"outputsToAssign": [], "variables": [], "decisionTableInputs": [], "dynamicInputs": [], "workflowInputs": [], "inputs": list(inputs)}
def lin(name, value): return {"id": "", "name": name, "value": value, "displayValue": value, "children": [], "parameter": {}, "scriptActive": False}
def logic(kind, order, inputs=(), parent=None, connected_to=None):
    return Step("logic", order, lobj([lin(n, v) for n, v in inputs]), parent, connected_to, logic_definition=LG[kind], label=kind)

# ---------------- triggers
_TPL = ET.fromstring(ET.parse(V / "test_import_20261119o/transpiler_test_20261119o.xml").getroot().find("sys_update_xml").findtext("payload").encode())
_REC = json.loads(gzip.decompress(base64.b64decode(_TPL.find("sys_hub_trigger_instance_v2[@action='INSERT_OR_UPDATE']").findtext("trigger_inputs"))))
REC = {"Created": ("798916a0c31322002841b63b12d3ae7c", "record_create"), "Updated": ("bb695e60c31322002841b63b12d3aea5", "record_update"),
       "Created or Updated": ("a45d9180c32222002841b63b12d3aea7", "record_create_or_update")}
STRATEGY = [("once", "Once"), ("unique_changes", "For each unique change"), ("always", "Only if not currently running"), ("every", "For every update")]
def tentry(label, typ, name, value, display=None, mandatory=True, attrs=None, choices=()):
    p = {"type": typ, "name": name, "label": label}
    if attrs: p["attributes"] = attrs
    return {"triggerInstanceSysId": "", "label": label, "internalType": typ, "dependent": "",
            "choiceList": [{"fValue": v, "fLabel": l, "fImage": "", "fSelected": False, "fUsed": False, "fMissing": False} for v, l in choices],
            "mandatory": mandatory, "order": 100, "name": name, "value": value, "displayValue": str(value) if display is None else display, "displayField": "",
            "scriptActive": False, "children": [], "parameter": p}
def record_trigger(kind, table, condition, strategy=None):
    e = json.loads(json.dumps(_REC))
    for x in e:
        if x["name"] == "table": x["value"] = x["displayValue"] = table
        if x["name"] == "condition": x["value"] = x["displayValue"] = condition
    if kind != "Created": e.append(tentry("Run Trigger", "choice", "trigger_strategy", strategy or "once", mandatory=False, choices=STRATEGY))
    return {"name": kind, "definition": REC[kind][0], "type": REC[kind][1], "entries": e}
TIMER = {"Weekly": ("cf352104c32222002841b63b12d3ae1f", "weekly"), "Monthly": ("2ca52504c32222002841b63b12d3ae4a", "monthly"), "Run Once": ("0a76e504c32222002841b63b12d3aeac", "run_once")}
DAYS = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
def weekly(day, hhmm): return {"name": "Weekly", "definition": TIMER["Weekly"][0], "type": "weekly",
    "entries": [tentry("Day of Week", "day_of_week", "day_of_week", str(day), DAYS[day]), tentry("Time", "glide_time", "time", f"1970-01-01 {hhmm}:00")]}
def monthly(day, hhmm): return {"name": "Monthly", "definition": TIMER["Monthly"][0], "type": "monthly",
    "entries": [tentry("Day of Month", "integer", "day_of_month", day, attrs={"integer_type": "day_of_month"}), tentry("Time", "glide_time", "time", f"1970-01-01 {hhmm}:00")]}
def run_once(when): return {"name": "Run Once", "definition": TIMER["Run Once"][0], "type": "run_once", "entries": [tentry("Run in", "glide_date_time", "run_in", when)]}

def inbound_email(conditions, target_table="", order=100, stop=True):
    return {"name": "Inbound Email", "definition": "6f0180400b320300f4eb8bf637673ad4", "type": "email", "entries": [
        tentry("Email Conditions", "conditions", "email_conditions", conditions, mandatory=False),
        tentry("Order", "integer", "order", order, mandatory=False),
        tentry("Stop processing", "boolean", "stop_condition_evaluation", stop, "true" if stop else "false", mandatory=False),
        tentry("Reply Record Type", "table_name", "target_table", target_table, mandatory=False)]}
def sla_task(): return {"name": "SLA Task", "definition": "f5ce00a873723300d70877186bf6a759", "type": "sla_task", "entries": []}
def raw_trigger(name, definition, typ, entries): return {"name": name, "definition": definition, "type": typ, "entries": entries}
# ---------------- flow
class Flow:
    def __init__(self, name, description, trigger, steps, run_as="system", fid=None, extra=()):
        """fid: a sys_id chosen beforehand (needed when a step value must contain the flow's id); extra: records placed right after sys_hub_flow (flow variables)."""
        self.name, self.id, self.steps, self.trigger = name, fid or gid(), steps, trigger; F = self.id
        tname = trigger["name"]
        # label_cache: one entry per pill, with the steps and inputs that use it (prompt Section 7.10, compact form in Appendix E.4)
        used = {}
        for s in steps:
            ents = s.values if isinstance(s.values, list) else s.values["inputs"]
            for e in ents:
                for pill in re.findall(r"\{\{([^}]+)\}\}", str(e["value"])):
                    if pill.startswith("static."): continue
                    used.setdefault(pill, {}).setdefault(s.ui, [])
                    if e["name"] not in used[pill][s.ui]: used[pill][s.ui].append(e["name"])
        def label(p):
            if p.startswith(tname + "_1.current"):
                rest = p[len(tname) + 11:]; return f"Trigger - Record {tname}➛incident Record" + ("➛" + rest.replace(".", "➛") if rest else "")
            return p.replace(".", "➛")
        lc = [{"name": p, "label": label(p), "type": "reference" if p.endswith(".current") else "string", "base_type": "reference" if p.endswith(".current") else "string",
               "usedInstances": u, "attributes": {}} for p, u in used.items()]
        r = ET.Element("record_update", dict(_TPL.attrib))
        r.append(rec("sys_hub_flow", F, {"access": "public", "active": "false", "allow_high_security_roles": "false", "description": description, "flow_priority": "MEDIUM",
                 "generation_source": "fluent", "label_cache": cj(lc), "name": name, "run_as": run_as, "show_draft_actions": "false", "status": "draft", "type": "flow", "version": "2"}))
        for e in extra: r.append(e)
        trig = gid()
        r.append(dm("sys_hub_trigger_instance_v2", f"flow={F}^sys_idNOT IN{trig}"))
        r.append(rec("sys_hub_trigger_instance_v2", trig, {"flow": F, "name": tname, "trigger_definition": trigger["definition"], "trigger_inputs": enc(trigger["entries"]), "trigger_type": trigger["type"]}))
        acts = [s for s in steps if s.kind == "action"]; logs = [s for s in steps if s.kind == "logic"]
        r.append(dm("sys_hub_action_instance_v2", f"flow={F}" + ("^sys_idNOT IN" + ",".join(s.id for s in acts) if acts else "")))
        for s in acts:
            f = {"action_type": s.fields["action_type"], "action_type_parent": s.fields["action_type"], "active": "true", "flow": F, "order": str(s.order)}
            if s.parent: f["parent_ui_id"] = s.parent.ui
            f.update({"sys_class_name": "sys_hub_action_instance_v2", "ui_id": s.ui, "values": enc(s.values)})
            r.append(rec("sys_hub_action_instance_v2", s.id, f))
        for s in acts: r.append(dm("sys_hub_alias_mapping", f"source_id={s.id}"))
        r.append(dm("sys_hub_flow_logic_instance_v2", f"flow={F}" + ("^sys_idNOT IN" + ",".join(s.id for s in logs) if logs else "")))
        for s in logs:
            f = {"flow": F, "logic_definition": s.fields["logic_definition"], "order": str(s.order)}
            if s.connected_to: f["connected_to"] = s.connected_to.ui
            if s.parent: f["parent_ui_id"] = s.parent.ui
            f.update(getattr(s, "extra", {}))   # row-level fields some logic types need, e.g. decision_table
            f.update({"ui_id": s.ui, "values": enc(s.values)})
            r.append(rec("sys_hub_flow_logic_instance_v2", s.id, f))
        self._root = r
    def payload(self): return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(self._root, encoding="unicode")

# ---------------- custom action with Script and REST steps
SCRIPT_STEP, REST_STEP = "106afb6647032200b4fad7527c9a71e7", "07a762fb47222200b4fad7527c9a7129"
VAR_SCRIPT, VAR_RUNTIME = "71aa7f6647032200b4fad7527c9a719b", "74315b04b3201300176b051a16a8dc2b"
from actgen2 import REST_VARS, REST_DEFAULTS
class Action:
    def __init__(self, name, description, inputs, steps, outputs):
        """inputs: [(element, label)]; steps: dicts with type 'script' (label, inputs [(element, value)], script, outputs [element]) or 'rest' (label, config {setting: text}, pills {setting: text with pills});
        a value may be a callable taking the list of step cids; outputs: [(element, label, value or callable)]. All strings."""
        self.name, self.id = name, gid(); A = self.id
        self.input_types = {e: "string" for e, _ in inputs}
        sids = [gid() for _ in steps]; cids = [hy(x) for x in sids]
        val = lambda v: v(cids) if callable(v) else v
        r = ET.Element("record_update", {"table": "sys_hub_action_type_definition"}); rows = []; pills = []
        em = lambda owner, table, field, value: rec("sys_element_mapping", gid(), {"field": field, "id": owner, "table": table, "value": value})
        vv = lambda step, var, order, value: rec("sys_variable_value", gid(), {"document": "sys_hub_step_instance", "document_key": step, "order": str(order), "value": value, "variable": var})
        ext = lambda tag, step, el_: rec(tag, gid(), {"active": "true", "attributes": f"{MAPPER},uiType=string,uiTypeLabel=String", "element": el_, "internal_type": "string", "label": el_,
                                                    "model": step, "model_id": step, "model_table": "sys_hub_step_instance", "name": f"var__m_{tag}_{step}"})
        for n, (s, ST, cid) in enumerate(zip(steps, sids, cids), 1):
            rest = s["type"] == "rest"
            rows.append(rec("sys_hub_step_instance", ST, {"action": A, "active": "true", "cid": cid, "error_handling_type": "1", "label": s["label"], "order": str(n), "step_type": REST_STEP if rest else SCRIPT_STEP}))
            if rest:
                cfg = {**REST_DEFAULTS, **s.get("config", {})}; sp = {k: val(v) for k, v in s.get("pills", {}).items()}
                for el_, text in cfg.items(): rows.append(vv(ST, REST_VARS[el_][0], REST_VARS[el_][2], text))
                for el_ in sorted(set(cfg) | set(sp)): rows.append(em(ST, "var__m_sys_flow_step_definition_input_" + REST_STEP, el_, sp.get(el_, ""))); pills.append(sp.get(el_, ""))
            else:
                rows += [vv(ST, VAR_RUNTIME, 100, "instance"), vv(ST, VAR_SCRIPT, 100, s["script"])]
                for el_, v in s["inputs"]: rows.append(em(ST, "var__m_sys_hub_step_ext_input_" + ST, el_, val(v))); pills.append(val(v))
                for el_, _ in s["inputs"]: rows.append(ext("sys_hub_step_ext_input", ST, el_))
                for el_ in s["outputs"]: rows.append(ext("sys_hub_step_ext_output", ST, el_))
        for el_, _, v in outputs: rows.append(em(A, "var__m_sys_hub_action_output_" + A, el_, val(v))); pills.append(val(v))
        lce = lambda n, l, t: {"name": n, "label": l, "type": t, "ref": "", "reference_display": "", "base_type": "string", "parent_table_name": "", "column_name": "", "choices": None, "attributes": {}}
        blob = " ".join(pills); lc = [lce("{{action.%s}}" % e, "action➛" + l, "action") for e, l in inputs if "{{action.%s}}" % e in blob]
        for s, cid in zip(steps, cids):
            for el_ in sorted(set(re.findall(r"\{\{step\[%s\]\.(\w+)\}\}" % re.escape(cid), blob))): lc.append(lce("{{step[%s].%s}}" % (cid, el_), "step➛%s➛%s" % (s["label"], el_), "step"))
        r.append(rec("sys_hub_action_type_definition", A, {"access": "public", "active": "true", "description": description, "label_cache": cj(lc), "name": name, "state": "draft", "system_level": "false"}))
        r.extend(rows)
        var = lambda tag, el_, label, typ, size, order, attrs, extra=None: rec(tag, gid(), {"active": "true", "attributes": attrs, **(extra or {}), "element": el_, "internal_type": typ, "label": label,
                 "mandatory": "false", "max_length": str(size), "model": A, "model_id": A, "model_table": "sys_hub_action_type_definition", "name": f"var__m_{tag}_{A}", "order": str(order)})
        doc = lambda table, el_, label: rec("sys_documentation", gid(), {"element": el_, "label": label, "language": "en", "name": f"var__m_{table}_{A}", "plural": label},
                                             update_name=f"sys_documentation_var__m_{table}_{A}_{el_}_en")
        for n, (el_, label) in enumerate(inputs, 1):
            r.append(var("sys_hub_action_input", el_, label, "string", 8000, n, f"{MAPPER},uiType=string,uiTypeLabel=String,uiUniqueId={A}-{el_}")); r.append(doc("sys_hub_action_input", el_, label))
        for n, (el_, label, _) in enumerate(outputs, 1):
            r.append(doc("sys_hub_action_output", el_, label))
            r.append(var("sys_hub_action_output", el_, label, "string", 8000, n, f"{MAPPER},pwd2droppable=true,uiType=string,uiTypeLabel=String,uiUniqueId={A}-{el_}"))
        r.append(doc("sys_hub_action_output", "__action_status__", "Action Status")); r.append(doc("sys_hub_action_output", "__dont_treat_as_error__", "Don't Treat as Error"))
        r.append(var("sys_hub_action_output", "__action_status__", "Action Status", "string", 65000, len(outputs) + 1,
                     f"{MAPPER},action_error_output=true,uiType=object,uiTypeLabel=Object,uiUniqueId={A}-action-status,co_type_name=FDACTIONSTATUS"))
        r.append(var("sys_hub_action_output", "__dont_treat_as_error__", "Don't Treat as Error", "boolean", 40, len(outputs) + 2,
                     f"{MAPPER},action_error_output=true,uiType=boolean,uiTypeLabel=True/False,uiUniqueId={A}-action-error,visible_in_ui=false", {"default_value": "true"}))
        self._root, self.cids = r, cids
    def payload(self): return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(self._root, encoding="unicode")
