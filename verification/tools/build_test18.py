"""Test 18: a custom action with a JSON Parser step, generated in the compact shape (draft, no snapshot), called from a compact flow. Local files only.
The parser records follow the hand-built sample read from dev435256 (fixtures/dev435256/jsonparser/)."""
import json, sys, pathlib, gzip, base64, re, xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdgen import gid, uid, TS
import actgen
V = pathlib.Path(__file__).parent.parent; OUT = V / "test_import_20261119q"
MAPPER_CLASS = "com.glide.flow_design.action.data.FlowDesignVariableMapper"; MAPPER = "element_mapping_provider=" + MAPPER_CLASS
JSON_STEP = "502328c387523300f917e55936cb0bf0"; VAR_TARGET = "4674240787523300f917e55936cb0b0e"; VAR_SAMPLE = "d335ac0787523300f917e55936cb0b1d"
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

# ---- JSON Parser: target schema and complex object from a sample payload
def target_schema(sample):
    def node(name, v, path):
        if isinstance(v, dict): return {"name": name, "children": [node(k, x, f"{path}.{k}") for k, x in v.items()], "type": "object", "jpath": path, "previewValue": ""}
        if isinstance(v, list):
            return {"name": name, "children": [{"name": name + "_string", "children": [], "type": "string", "jpath": path + "[*]", "previewValue": str(v[0]) if v else ""}],
                    "type": "array.string", "jpath": path + "[*]", "previewValue": ""}
        pv = "true" if v is True else "false" if v is False else str(v)
        return {"name": name, "children": [], "type": "string", "jpath": path, "previewValue": pv}
    return node("root", sample, "$")
def complex_object(sample, fd, root_uiu):
    def facet(label, order, kind):
        base = {"uiTypeLabel": {"string": "String", "object": "Object"}[kind], "help": "", "read_only": "false", "hint": "", "uiType": kind, "choiceOption": "", "default_value": "",
                "label": label, "mandatory": "false", "order": str(order), "max_length": "0", "uiUniqueId": uid()}
        return {"SimpleMapFacet": cj(base)}
    def body(obj):
        out = {}
        for n, (k, v) in enumerate(obj.items(), 1):
            if isinstance(v, dict): out[k] = body(v); out[k + ".$field_facets"] = facet(k, n, "object")
            elif isinstance(v, list):
                out[k] = ["Any"]
                out[k + ".$field_facets"] = {"SimpleMapFacet": cj({"choiceOption": "", "default_value": "", "child_hint": "", "child_maxsize": "", "label": k, "mandatory": "false",
                    "child_name": k + "_string", "uiUniqueId": uid(), "uiTypeLabel": "Array.String", "help": "", "child_label": k + "_string", "child_type_label": "String",
                    "read_only": "false", "hint": "", "uiType": "array.string", "child_defaultValue": "", "child_type": "string", "order": str(n), "max_length": "0", "child_uiUniqueId": uid()})}
            else: out[k] = "String"; out[k + ".$field_facets"] = facet(k, n, "string")
        return out
    key = "FlowDesigner:" + fd
    return {key: body(sample), key + ".$type_facets": {"SimpleMapFacet": cj({"sourceId": "", "choiceOption": "", "default_value": "", "label": "root", "mandatory": "false",
            "uiUniqueId": root_uiu, "uiTypeLabel": "Object", "help": "", "co_type_name": fd, "element_mapping_provider": MAPPER_CLASS, "read_only": "false", "sourceUiUniqueId": "",
            "sourceType": "", "hint": "", "uiType": "object", "order": "1", "max_length": "65000"})}}

class ParserAction:
    def __init__(self, name, description, step_label, sample, outputs):
        """outputs: list of (element, label, dotted path under root)."""
        self.name, self.id = name, gid()
        A = self.id; ST = gid(); cid = hy(ST); fd = "FD" + gid(); root_uiu = uid()
        self.outputs = outputs
        pill = lambda path: "{{step[%s].root.%s}}" % (cid, path)
        lce = lambda n, l, t, base: {"name": n, "label": l, "type": t, "ref": "", "reference_display": "", "base_type": base, "parent_table_name": "", "column_name": "", "choices": None, "attributes": {}}
        lc = [lce("{{action.text}}", "action➛Text", "action", "string")] + [lce(pill(p), "step➛%s➛root➛%s" % (step_label, p.replace(".", "➛")), "step", "string") for _, _, p in outputs]
        r = ET.Element("record_update", {"table": "sys_hub_action_type_definition"})
        r.append(rec("sys_hub_action_type_definition", A, {"access": "public", "active": "true", "description": description, "label_cache": cj(lc), "name": name, "state": "draft", "system_level": "false"}))
        r.append(rec("sys_hub_step_instance", ST, {"action": A, "active": "true", "cid": cid, "error_handling_type": "1", "label": step_label, "order": "1", "step_type": JSON_STEP}))
        vv = lambda var, order, value: rec("sys_variable_value", gid(), {"document": "sys_hub_step_instance", "document_key": ST, "order": str(order), "value": value, "variable": var})
        r.append(vv(VAR_TARGET, 100, cj(target_schema(sample)))); r.append(vv(VAR_SAMPLE, 300, cj(sample)))
        em = lambda owner, table, field, value: rec("sys_element_mapping", gid(), {"field": field, "id": owner, "table": table, "value": value})
        T = "var__m_sys_flow_step_definition_input_" + JSON_STEP
        r.append(em(ST, T, "sample_payload", "")); r.append(em(ST, T, "source_data", "{{action.text}}")); r.append(em(ST, T, "target_schema", ""))
        for el_, _, p in outputs: r.append(em(A, "var__m_sys_hub_action_output_" + A, el_, pill(p)))
        r.append(rec("sys_complex_object", gid(), {"name": fd, "namespace": "FlowDesigner", "scope_name": "global", "serialized_content": cj(complex_object(sample, fd, root_uiu)), "type": "complex_object_schema"}))
        r.append(rec("sys_hub_step_ext_output", gid(), {"active": "true", "attributes": f"co_type_name={fd},{MAPPER},uiType=object,uiTypeLabel=Object,uiUniqueId={root_uiu}", "element": "root",
                 "internal_type": "string", "label": "root", "max_length": "65000", "model": ST, "model_id": ST, "model_table": "sys_hub_step_instance", "name": "var__m_sys_hub_step_ext_output_" + ST, "order": "1"}))
        var = lambda tag, el_, label, typ, size, order, attrs, extra=None: rec(tag, gid(), {"active": "true", "attributes": attrs, **(extra or {}), "element": el_, "internal_type": typ, "label": label,
                 "mandatory": "false", "max_length": str(size), "model": A, "model_id": A, "model_table": "sys_hub_action_type_definition", "name": f"var__m_{tag}_{A}", "order": str(order)})
        doc = lambda table, el_, label: rec("sys_documentation", gid(), {"element": el_, "label": label, "language": "en", "name": f"var__m_{table}_{A}", "plural": label},
                                             update_name=f"sys_documentation_var__m_{table}_{A}_{el_}_en")
        r.append(var("sys_hub_action_input", "text", "Text", "string", 8000, 1, f"{MAPPER},uiType=string,uiTypeLabel=String,uiUniqueId={A}-text")); r.append(doc("sys_hub_action_input", "text", "Text"))
        for n, (el_, label, _) in enumerate(outputs, 1):
            r.append(doc("sys_hub_action_output", el_, label))
            r.append(var("sys_hub_action_output", el_, label, "string", 8000, n, f"{MAPPER},pwd2droppable=true,uiType=string,uiTypeLabel=String,uiUniqueId={A}-{el_}"))
        r.append(doc("sys_hub_action_output", "__action_status__", "Action Status")); r.append(doc("sys_hub_action_output", "__dont_treat_as_error__", "Don't Treat as Error"))
        r.append(var("sys_hub_action_output", "__action_status__", "Action Status", "string", 65000, len(outputs) + 1,
                     f"{MAPPER},action_error_output=true,uiType=object,uiTypeLabel=Object,uiUniqueId={A}-action-status,co_type_name=FDACTIONSTATUS"))
        r.append(var("sys_hub_action_output", "__dont_treat_as_error__", "Don't Treat as Error", "boolean", 40, len(outputs) + 2,
                     f"{MAPPER},action_error_output=true,uiType=boolean,uiTypeLabel=True/False,uiUniqueId={A}-action-error,visible_in_ui=false", {"default_value": "true"}))
        self.step, self.cid, self.fd, self._root = ST, cid, fd, r
    def payload(self): return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(self._root, encoding="unicode")

class CompactFlow:
    def __init__(self, name, description, prefix, action):
        self.name, self.id = name, gid(); F = self.id
        TPL = ET.fromstring(ET.parse(V / "test_import_20261119o/transpiler_test_20261119o.xml").getroot().find("sys_update_xml").findtext("payload").encode())
        ti = json.loads(gzip.decompress(base64.b64decode(TPL.find("sys_hub_trigger_instance_v2[@action='INSERT_OR_UPDATE']").findtext("trigger_inputs"))))
        for x in ti:
            if x["name"] == "condition": x["value"] = x["displayValue"] = "short_descriptionSTARTSWITH" + prefix
        trig, a1, a2 = gid(), gid(), gid(); u1, u2 = hy(a1), hy(a2)
        short = lambda n, v, t: {"name": n, "value": v, "displayValue": v, "scriptActive": False, "parameter": {"type": t}}
        tmpl = "description=TT18 owner [{{%s.owner}}] city [{{%s.city}}] count [{{%s.count}}] for {{Created_1.current.number}}^EQ" % (u1, u1, u1)
        lce = lambda n, l, used, t="string": {"name": n, "label": l, "type": t, "base_type": t, "usedInstances": used, "attributes": {}}
        lc = [lce("Created_1.current.description", "Trigger - Record Created➛incident Record➛Description", {u1: ["text"]}),
              lce("Created_1.current.sys_id", "Trigger - Record Created➛incident Record➛Sys Id", {u2: ["record"]}),
              lce("Created_1.current.number", "Trigger - Record Created➛incident Record➛Number", {u2: ["values"]})] + \
             [lce(f"{u1}.{el_}", f"{u1}➛{el_}", {u2: ["values"]}) for el_, _, _ in action.outputs]
        r = ET.Element("record_update", dict(TPL.attrib))
        r.append(rec("sys_hub_flow", F, {"access": "public", "active": "false", "allow_high_security_roles": "false", "description": description, "flow_priority": "MEDIUM", "generation_source": "fluent",
                 "label_cache": cj(lc), "name": name, "run_as": "system", "show_draft_actions": "false", "status": "draft", "type": "flow", "version": "2"}))
        r.append(dm("sys_hub_trigger_instance_v2", f"flow={F}^sys_idNOT IN{trig}"))
        r.append(rec("sys_hub_trigger_instance_v2", trig, {"flow": F, "name": "Created", "trigger_definition": "798916a0c31322002841b63b12d3ae7c", "trigger_inputs": enc(ti), "trigger_type": "record_create"}))
        r.append(dm("sys_hub_action_instance_v2", f"flow={F}^sys_idNOT IN{a1},{a2}"))
        ai = lambda sid, typ, order, vals: rec("sys_hub_action_instance_v2", sid, {"action_type": typ, "action_type_parent": typ, "active": "true", "flow": F, "order": str(order),
                 "sys_class_name": "sys_hub_action_instance_v2", "ui_id": hy(sid), "values": enc(vals)})
        r.append(ai(a1, action.id, 1, [short("text", "{{Created_1.current.description}}", "string")]))
        r.append(ai(a2, "f9d01dd2c31332002841b63b12d3aea1", 2, [short("table_name", "incident", "table_name"), short("record", "{{Created_1.current.sys_id}}", "document_id"), short("values", tmpl, "template_value")]))
        r.append(dm("sys_hub_alias_mapping", f"source_id={a1}")); r.append(dm("sys_hub_alias_mapping", f"source_id={a2}"))
        r.append(dm("sys_hub_flow_logic_instance_v2", f"flow={F}"))
        self._root, self.ui = r, (u1, u2)
    def payload(self): return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(self._root, encoding="unicode")

SAMPLE = {"ticket": {"id": "T-18", "site": {"city": "Denver", "zip": "80202"}}, "owner": "Koa", "count": 3, "urgent": True, "flags": ["red", "blue"]}
a = ParserAction("TT18 JSON Parser Action", "Transpiler test 18. One JSON Parser step, generated in the compact shape. Safe to delete.", "Parse payload", SAMPLE,
                 [("owner", "Owner", "owner"), ("city", "City", "ticket.site.city"), ("count", "Count", "count")])
f = CompactFlow("TT18 Compact JSON Parser", "Transpiler test 18. Runs for incidents whose short description starts with TT18RUN; parses the description as JSON. Safe to delete.", "TT18RUN", a)
US = "Transpiler Test 20261119q"
xml, usb = actgen.update_set(US, "Transpiler prompt test 18 on dev435256: JSON Parser step action and its flow, compact shape. Safe to delete.", [a], [f])
(OUT / "transpiler_test_20261119q.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261119q.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "action": {"name": a.name, "id": a.id, "step": a.step, "cid": a.cid, "fd": a.fd},
    "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []}], "sample": SAMPLE}, indent=1))
print("set", usb, "| action", a.id, "| flow", f.id, "| bytes", len(xml))
