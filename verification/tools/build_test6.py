"""Test 6: action + subflow + record-triggered flow, to be activated only through api/now/wfa_fluent/activate_flows. Local files only."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdlib import *
import actgen
OUT = ROOT / "test_import_20261119g"; INC = ("incident", "Incident"); T = "Created_1.current"; TL = "Trigger - Record Created➛Incident Record"
action = actgen.Action("TT6 Scratch Action", "Transpiler test 6. Reverses a text. Safe to delete.",
    inputs=[dict(element="text", label="Text", type="string", mandatory=True)],
    step_inputs=[dict(element="text", label="text", type="string", value="{{action.text}}")],
    script="(function execute(inputs, outputs) {\n  outputs.reversed = String(inputs.text).split('').reverse().join('');\n})(inputs, outputs);",
    step_outputs=[dict(element="reversed", label="reversed", type="string")], outputs=[])
action.outputs[0:0] = [dict(element="reversed", label="Reversed", type="string", value=action.pill_step("reversed"), id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid())]
s_in = var("user_name", "User name", 1, True); s_out = var("found", "Found", 1)
sl = lookup(1, "sys_user", "User", "user_name={{subflow.user_name}}"); sa = assign_output(2, s_out, "{{%s.Record.name}}" % sl.ui)
subflow = Flow("TT6 Subflow", None, [sl, sa], ftype="subflow", run_as="user", inputs=[s_in], outputs=[s_out], description="Transpiler test 6 subflow. Safe to delete.",
               label_cache=[lc("subflow.user_name", "Input➛User name", "string", {sl.ui: ["conditions"]}),
                            lc(sl.ui + ".Record.name", "1 - Look Up Record➛User Record➛Name", "string", {sa.ui: ["found"]}, parent_table="sys_user", column="name")])
s1 = call_subflow(1, subflow, {"user_name": "{{%s.caller_id.user_name}}" % T})
a2 = call_action(2, action, {"text": "{{%s.found}}" % s1.ui})
a3 = act("Update Record", 3, {"record": "{{%s}}" % T, "table_name": INC, "values": "description=TT6 subflow [{{%s.found}}] action [{{%s.reversed}}]" % (s1.ui, a2.ui)})
flow = Flow("TT6 Runtime No Click", record_trigger("Created", *INC, "short_descriptionSTARTSWITHTT6RUN"), [s1, a2, a3],
            description="Transpiler test 6. Activated through the API only. Runs for incidents whose short description starts with TT6RUN. Safe to delete.",
            label_cache=[lc(T + ".caller_id.user_name", TL + "➛Caller➛User ID", "string", {s1.ui: ["user_name"]}, parent_table="sys_user", column="user_name"),
                         lc(s1.ui + ".found", "1 - TT6 Subflow➛Found", "string", {a2.ui: ["text"], a3.ui: ["values"]}),
                         lc(a2.ui + ".reversed", "2 - TT6 Scratch Action➛Reversed", "string", {a3.ui: ["values"]}),
                         lc(T, TL, "reference", {a3.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False)])
US = "Transpiler Test 20261119g"
xml, usb = actgen.update_set(US, "Transpiler prompt test 6 on dev435256: one action, one subflow, one flow. Safe to delete.", [action], [subflow, flow])
(OUT / "transpiler_test_20261119g.xml").write_text(xml)
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb,
    "action": {"name": action.name, "id": action.id, "snap": action.snap, "cid": action.cid, "fd": action.fd},
    "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in f.steps]} for f in (subflow, flow)]}, indent=1))
print("set", usb, "| action", action.id, "| subflow", subflow.id, "| flow", flow.id)
