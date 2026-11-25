"""Test 24: the three weak spots left by tests 21 to 23. Append to Flow Variables written from the rules (array of objects, elements in a list,
element fields read inside For Each), Wait For Message resumed by a message, Wait For Email Reply resumed by a reply. Local files only."""
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
OUT = V / "test_import_20261120k"; T = "Created_1.current"; CUR = "{{%s}}" % T
upd = lambda order, text, field="description": act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "%s=%s^EQ" % (field, text)})
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT24%s RUN" % k)

# ---- A: array-of-objects flow variable, Append to Flow Variables, For Each reading the element fields
def array_object_variable(flow_id, element, label, child_label, fields):
    """fields: [(name, 'String'|'Integer', uiType, label)]. Returns (variable sys_id, schema object, records)."""
    vid = gid(); FD = "FD" + vid; item = {}
    for n, (fn, typ, ui, fl) in enumerate(fields, 1):
        item[fn] = typ
        item[fn + ".$field_facets"] = {"SimpleMapFacet": cj({"uiTypeLabel": typ, "read_only": "false", "uiType": ui, "choiceOption": "", "default_value": "", "hint": "", "label": fl,
                                                              "mandatory": "false", "order": str(n), "max_length": "0"})}
    tf = {"SimpleMapFacet": cj({"sourceId": "", "max_rows": "", "choiceOption": "", "default_value": "", "label": label, "child_hint": "", "child_maxsize": "0", "mandatory": "false",
          "child_name": "item", "uiUniqueId": f"{flow_id}-{element}", "uiTypeLabel": "Array.Object", "co_type_name": FD, "child_label": child_label, "child_type_label": "Object",
          "read_only": "false", "sourceUiUniqueId": "", "sourceType": "", "hint": "", "uiType": "array.object", "child_defaultValue": "", "child_type": "object", "order": "0",
          "max_length": "65000", "child_uiUniqueId": f"{flow_id}-{element}-child"})}
    schema = {f"FlowDesigner:{FD}": {"$COCollectionField": [{"item": item}], "$COCollectionField.$field_facets": {"SimpleMapFacet": cj({"up-shift-collection-level": "true"})},
                                     "$COCollectionField.$type_facets": tf}, f"FlowDesigner:{FD}.$type_facets": tf}
    name = f"var__m_sys_hub_flow_variable_{flow_id}"
    recs = [dm("sys_hub_flow_variable", f"model={flow_id}^sys_idNOT IN{vid}"),
            rec("sys_hub_flow_variable", vid, {"active": "true", "attributes": f"co_type_name={FD},element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,uiType=array.object,uiTypeLabel=Array.Object,uiUniqueId={flow_id}-{element},child_maxsize=0,child_hint=,child_label={child_label},child_name=item,child_type=object,child_type_label=Object,child_uiUniqueId={flow_id}-{element}-child,max_rows=,child_defaultValue=",
                 "element": element, "internal_type": "string", "label": label, "mandatory": "false", "max_length": "65000", "model": flow_id, "model_id": flow_id, "model_table": "sys_hub_flow", "name": name, "order": "1"}),
            rec("sys_documentation", gid(), {"element": element, "label": label, "language": "en", "name": name, "plural": label}, update_name=f"sys_documentation_{name}_{element}_en"),
            rec("sys_complex_object", gid(), {"name": FD, "namespace": "FlowDesigner", "serialized_content": cj(schema), "type": "complex_object_collection"})]
    return vid, schema, recs
def append(order, vid, element, schema, elements, parent=None):
    ser = cj({"version": "1.0", "complexObjectSchema": schema, "complexObject": {"name$": "FD" + vid, "$COCollectionField": elements}, "serializationFormat": "JSON"})
    e = {"id": vid, "name": element, "value": ser, "displayValue": ser, "children": [], "parameter": {}, "scriptActive": False}
    o = lobj([e]); o["variables"] = [dict(e)]
    s = Step("logic", order, o, parent, None, logic_definition="4784e82683031210d266f953d22bc0fd", label="Append to Flow Variables"); s.extra = {"flow_variables_assigned": element}; return s
FA = gid()
vid, schema, vrecs = array_object_variable(FA, "items", "Items", "Item", [("name", "String", "string", "Name"), ("id", "Integer", "integer", "ID")])
a1 = append(1, vid, "items", schema, [{"name": "Alice", "id": 1}, {"name": "Bob", "id": 2}])
a2 = append(2, vid, "items", schema, [{"name": "{{%s.number}}" % T, "id": 3}])
a3 = logic("For Each", 3, [("items", "{{flow_variable.items}}")])
a4 = G("Create Task", 4, {"task_table": "incident_task", "field_values": "short_description=TT24A item [{{%s.item.name}}] id [{{%s.item.id}}]^incident={{%s.sys_id}}^EQ" % (a3.ui, a3.ui, T), "wait": "0"}, a3)
a5 = upd(5, "TT24A loop finished")
fa = Flow("TT24A Append From Rules", "Transpiler test 24. Array-of-objects flow variable, Append to Flow Variables and For Each over it, written from the rules, for incidents whose short description starts with TT24A RUN. Safe to delete.",
          trig("A"), [a1, a2, a3, a4, a5], fid=FA, extra=vrecs)

# ---- B and C: Wait For Message resumed by sn_fd.FlowAPI.sendMessage from a custom action in a second flow
sm = Action("TT24 Send Flow Message", "Transpiler test 24. Sends a message to a waiting flow with sn_fd.FlowAPI.sendMessage. Safe to delete.",
    [("context_id", "Context id"), ("message", "Message"), ("payload", "Payload")],
    [dict(type="script", label="Send message", inputs=[("context_id", "{{action.context_id}}"), ("message", "{{action.message}}"), ("payload", "{{action.payload}}")], outputs=["result"],
          script="(function execute(inputs, outputs) {\n  sn_fd.FlowAPI.sendMessage(String(inputs.context_id), String(inputs.message), String(inputs.payload));\n  outputs.result = 'sent ' + inputs.message + ' to ' + inputs.context_id;\n})(inputs, outputs);")],
    [("result", "Result", lambda c: "{{step[%s].result}}" % c[0])])
b1 = G("Wait For Message", 1, {"message": "TT24MSG", "enable_timeout": "1", "timeout": "1970-01-01 00:10:00"})
b2 = upd(2, "TT24B resumed, payload [{{%s.payload}}]" % b1.ui)
fb = Flow("TT24B Wait For Message", "Transpiler test 24. Waits for the message TT24MSG, for incidents whose short description starts with TT24B RUN. Safe to delete.", trig("B"), [b1, b2])
c1 = act("Look Up Record", 1, {"table": "sys_flow_context", "conditions": "name=TT24B Wait For Message^state=WAITING"})
c2 = call(sm, 2, {"context_id": "{{%s.Record.sys_id}}" % c1.ui, "message": "TT24MSG", "payload": "hello from {{%s.number}}" % T})
c3 = upd(3, "TT24C [{{%s.result}}]" % c2.ui)
fc = Flow("TT24C Send Message", "Transpiler test 24. Sends TT24MSG to the waiting TT24B flow, for incidents whose short description starts with TT24C RUN. Safe to delete.", trig("C"), [c1, c2, c3])

# ---- D: Wait For Email Reply resumed by a reply
d1 = act("Send Email", 1, {"record": CUR, "table_name": "incident", "watermark_email": "1", "ah_to": "admin@example.com", "ah_subject": "TT24D out {{%s.number}}" % T, "ah_body": "TT24D body for {{%s.number}}" % T})
d2 = upd(2, "TT24D sent [{{%s.email.sys_id}}]" % d1.ui)
d3 = G("Wait For Email Reply", 3, {"record": "{{%s.email}}" % d1.ui, "enable_timeout": "1", "timeout_duration": "1970-01-01 00:10:00"})
d4 = upd(4, "TT24D reply state [{{%s.state}}] reply [{{%s.email_reply.subject}}]" % (d3.ui, d3.ui), "close_notes")
fd = Flow("TT24D Wait For Email Reply", "Transpiler test 24. Sends an email and waits for its reply, for incidents whose short description starts with TT24D RUN. Safe to delete.", trig("D"), [d1, d2, d3, d4])

flows = [fa, fb, fc, fd]
US = "Transpiler Test 20261120k"
xml, usb = actgen.update_set(US, "Transpiler prompt test 24 on dev435256: Append to Flow Variables from the rules, Wait For Message and Wait For Email Reply resumed. Safe to delete.", [sm], flows)
(OUT / "transpiler_test_20261120k.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120k.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "action": {"name": sm.name, "id": sm.id}, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb, "| action", sm.id); print(json.dumps([f.id for f in flows]))
