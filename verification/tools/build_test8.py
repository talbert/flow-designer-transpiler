"""Test 8: a three-step custom action (Script, REST, Script) called from a flow; plus a name-clash probe (the TT6 names again with new ids). Local files only."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdlib import *
import actgen, actgen2
OUT = ROOT / "test_import_20261119i"; INC = ("incident", "Incident"); T = "Created_1.current"; TL = "Trigger - Record Created➛Incident Record"
a = actgen2.Action2("TT8 Multi Step Action", "Transpiler test 8. Script, REST and Script steps. Safe to delete.",
    inputs=[dict(element="text", label="Text", type="string", mandatory=True)],
    steps=[dict(type="script", label="Make upper", inputs=[dict(element="text", label="text", type="string", value="{{action.text}}")],
                script="(function execute(inputs, outputs) {\n  outputs.upper = String(inputs.text).toUpperCase();\n})(inputs, outputs);",
                outputs=[dict(element="upper", label="upper", type="string")]),
           dict(type="rest", label="Call login page", config={"base_url": "https://dev435256.service-now.com", "resource_path": "/login.do"}),
           dict(type="script", label="Summarize", inputs=[], script="(function execute(inputs, outputs) {\n  outputs.summary = inputs.upper + ' / HTTP ' + inputs.code;\n})(inputs, outputs);",
                outputs=[dict(element="summary", label="summary", type="string")])],
    outputs=[])
a.steps[1]["pills"] = {"query_params": json.dumps({"type": "ADV_NV", "value": [{"name": "probe", "value": a.pill(0, "upper")}]}, separators=(",", ":"))}
a.steps[2]["inputs"] = [dict(x, id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid()) for x in
                        [dict(element="upper", label="upper", type="string", value=a.pill(0, "upper")), dict(element="code", label="code", type="string", value=a.pill(1, "status_code"))]]
a._user_outputs = [dict(element="summary", label="Summary", type="string", value=a.pill(2, "summary")), dict(element="status_code", label="Status code", type="string", value=a.pill(1, "status_code"))]
a.finish()
c1 = call_action(1, a, {"text": "{{%s.number}}" % T})
u2 = act("Update Record", 2, {"record": "{{%s}}" % T, "table_name": INC, "values": "description=TT8 summary [{{%s.summary}}] status [{{%s.status_code}}]" % (c1.ui, c1.ui)})
f = Flow("TT8 Runtime Multi Step", record_trigger("Created", *INC, "short_descriptionSTARTSWITHTT8RUN"), [c1, u2],
         description="Transpiler test 8. Runs for incidents whose short description starts with TT8RUN. Safe to delete.",
         label_cache=[lc(T + ".number", TL + "➛Number", "string", {c1.ui: ["text"]}, parent_table="incident", column="number"),
                      lc(c1.ui + ".summary", "1 - TT8 Multi Step Action➛Summary", "string", {u2.ui: ["values"]}),
                      lc(c1.ui + ".status_code", "1 - TT8 Multi Step Action➛Status code", "string", {u2.ui: ["values"]}),
                      lc(T, TL, "reference", {u2.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False)])
# ---- clash probe: same names as test 6, new ids everywhere
d = actgen.Action("TT6 Scratch Action", "Transpiler test 8 clash probe: same name as an existing action. Safe to delete.",
    inputs=[dict(element="text", label="Text", type="string", mandatory=True)], step_inputs=[dict(element="text", label="text", type="string", value="{{action.text}}")],
    script="(function execute(inputs, outputs) {\n  outputs.reversed = String(inputs.text);\n})(inputs, outputs);", step_outputs=[dict(element="reversed", label="reversed", type="string")], outputs=[])
d.outputs[0:0] = [dict(element="reversed", label="Reversed", type="string", value=d.pill_step("reversed"), id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid())]
dup_flow = Flow("TT6 Runtime No Click", record_trigger("Created", *INC, "short_description=TT8_CLASH_PROBE_NEVER_MATCH"), [lookup(1, "sys_user", "User", "user_name=admin")],
                description="Transpiler test 8 clash probe: same name and internal name as an existing flow. Never activated. Safe to delete.")
US = "Transpiler Test 20261119i"
xml, usb = actgen.update_set(US, "Transpiler prompt test 8 on dev435256: multi-step action, its flow, and a name-clash probe. Safe to delete.", [a, d], [f, dup_flow])
(OUT / "transpiler_test_20261119i.xml").write_text(xml)
import xml.etree.ElementTree as ET; ET.parse(OUT / "transpiler_test_20261119i.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb,
    "action": {"name": a.name, "id": a.id, "snap": a.snap, "cid": a.steps[0]["cid"], "fd": a.fd}, "dup_action": {"id": d.id, "snap": d.snap, "fd": d.fd},
    "flows": [{"name": x.name, "id": x.id, "snap": x.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in x.steps]} for x in (f, dup_flow)]}, indent=1))
print("set", usb, "| action", a.id, "| flow", f.id, "| dup action", d.id, "| dup flow", dup_flow.id)
