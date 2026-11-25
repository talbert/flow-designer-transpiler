"""Test 4: flows that really run, a custom action written from a spec, and the trigger/action types not yet import-tested. Local files only."""
import json, sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdlib import *
import actgen
OUT = ROOT / "test_import_20261119e"
ADMIN = "6816f79cc0a8016401c5a33be04be441"
INC = ("incident", "Incident")

# ---------------- custom action written from a spec (not a copy)
action = actgen.Action(
    "TT4 Scratch Action", "Transpiler test 4. Repeats a text in upper case. Safe to delete.",
    inputs=[dict(element="text", label="Text", type="string", mandatory=True), dict(element="times", label="Times", type="integer")],
    step_inputs=[dict(element="text", label="text", type="string", value="{{action.text}}"), dict(element="times", label="times", type="integer", value="{{action.times}}")],
    script="(function execute(inputs, outputs) {\n  var n = parseInt(inputs.times, 10) || 1;\n  var parts = [];\n  for (var i = 0; i < n; i++) {\n    parts.push(String(inputs.text).toUpperCase());\n  }\n"
           "  outputs.result = parts.join(' & ');\n  outputs.length = outputs.result.length;\n})(inputs, outputs);",
    step_outputs=[dict(element="result", label="result", type="string"), dict(element="length", label="length", type="integer")],
    outputs=[])
action.outputs[0:0] = [dict(o, id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid()) for o in
                       [dict(element="result", label="Result", type="string", value=action.pill_step("result")),
                        dict(element="length", label="Length", type="integer", value=action.pill_step("length"))]]

# ---------------- subflow: user_name in, the user's display name out
s_in = var("user_name", "User name", 1, True); s_out = var("found", "Found", 1)
sl = lookup(1, "sys_user", "User", "user_name={{subflow.user_name}}")
sa = assign_output(2, s_out, "{{%s.Record.name}}" % sl.ui)
subflow = Flow("TT4 Subflow", None, [sl, sa], ftype="subflow", run_as="user", inputs=[s_in], outputs=[s_out],
               description="Transpiler test 4 subflow. One lookup. Safe to delete.",
               label_cache=[lc("subflow.user_name", "Input➛User name", "string", {sl.ui: ["conditions"]}),
                            lc(sl.ui + ".Record.name", "1 - Look Up Record➛User Record➛Name", "string", {sa.ui: ["found"]}, parent_table="sys_user", column="name")])

# ---------------- flow 1: runs on a new incident; every logic type, a subflow call and the custom action
T = "Created_1.current"; note = var("note", "Note", 1)
upd = lambda order, text, parent=None, rec=T: act("Update Record", order, {"record": "{{%s}}" % rec, "table_name": INC, "values": text}, parent)
a1 = lookup(1, "sys_user", "User", "user_name=admin")
l2 = setvar(2, note, "start {{%s.Record.user_name}}" % a1.ui)
l3 = cond("If", 3, "Urgency high", "{{%s.urgency}}=1" % T)
a4 = upd(4, "description=IF branch for {{%s.number}}" % T, l3.ui)
l5 = cond("Else If", 5, "Urgency medium", "{{%s.urgency}}=2" % T, connected_to=l3.ui)
a6 = upd(6, "description=ELSE IF branch for {{%s.number}}" % T, l5.ui)
l7 = else_(7, l3)
a8 = upd(8, "description=ELSE branch for {{%s.number}}" % T, l7.ui)
a9 = act("Look Up Records", 9, {"table": ("sys_user", "User"), "conditions": "user_nameINabel.tuter,itil", "sort_column": ("user_name", "User ID"), "sort_type": ("sort_asc", "a to z"), "max_results": "5"})
l10 = foreach(10, a9.ui + ".Records")
a11 = act("Create Record", 11, {"table_name": ("incident_task", "Incident Task"),
                                "values": "incident={{%s.sys_id}}^short_description=TT4 task for {{%s.item.user_name}}" % (T, l10.ui)}, l10.ui)
l12 = setvar(12, note, "{{flow_variable.note}} +{{%s.item.user_name}}" % l10.ui, l10.ui)
s13 = call_subflow(13, subflow, {"user_name": "{{%s.caller_id.user_name}}" % T})
a14 = call_action(14, action, {"text": "{{flow_variable.note}}", "times": "2"})
a15 = upd(15, "work_notes=TT4 var [{{flow_variable.note}}] subflow [{{%s.found}}] action [{{%s.result}}] length [{{%s.length}}]" % (s13.ui, a14.ui, a14.ui))
a16 = act("Fire Event", 16, {"event_name": ("a2384bb60a0a140600ee61d2bd0c17c7", "incident.inactivity"), "record": "{{%s}}" % T, "table": INC,
                             "parm1": "TT4 {{%s.number}}" % T, "parm2": "{{flow_variable.note}}"})
a17 = act("Send Email", 17, {"record": "{{%s}}" % T, "table_name": INC, "watermark_email": ("1", "true"), "ah_to": "admin@example.com",
                             "ah_subject": "TT4 runtime {{%s.number}}" % T, "ah_body": "<p>Note: {{flow_variable.note}}</p>"})
l18 = cond("Do the following until", 18, "Note is set", "{{flow_variable.note}}ISNOTEMPTY")
a19 = lookup(19, "sys_user", "User", "user_name=admin", l18.ui)
TL = "Trigger - Record Created➛Incident Record"
f1 = Flow("TT4 Runtime Created", record_trigger("Created", *INC, "short_descriptionSTARTSWITHTT4RUN-CREATED"),
          [a1, l2, l3, a4, l5, a6, l7, a8, a9, l10, a11, l12, s13, a14, a15, a16, a17, l18, a19], variables=[note],
          description="Transpiler test 4. Runs only for incidents whose short description starts with TT4RUN-CREATED. Safe to delete.",
          label_cache=[
            lc(a1.ui + ".Record.user_name", "1 - Look Up Record➛User Record➛User ID", "string", {l2.ui: ["note"]}, parent_table="sys_user", column="user_name"),
            lc(T + ".urgency", TL + "➛Urgency", "integer", {l3.ui: ["condition"], l5.ui: ["condition"]}, parent_table="incident", column="urgency"),
            lc(T, TL, "reference", {a4.ui: ["record"], a6.ui: ["record"], a8.ui: ["record"], a15.ui: ["record"], a16.ui: ["record"], a17.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False),
            lc(T + ".number", TL + "➛Number", "string", {a4.ui: ["values"], a6.ui: ["values"], a8.ui: ["values"], a16.ui: ["parm1"], a17.ui: ["ah_subject"]}, parent_table="incident", column="number"),
            lc(a9.ui + ".Records", "9 - Look Up Records➛User Records", "records", {l10.ui: ["items"]}, ref="sys_user", ref_disp="User"),
            lc(l10.ui + ".item.user_name", "10 - For Each➛User Record➛User ID", "string", {a11.ui: ["values"], l12.ui: ["note"]}, parent_table="sys_user", column="user_name"),
            lc(T + ".sys_id", TL + "➛Sys ID", "GUID", {a11.ui: ["values"]}, parent_table="incident", column="sys_id"),
            lc("flow_variable.note", "Flow Variables➛Note", "string", {l12.ui: ["note"], a14.ui: ["text"], a15.ui: ["values"], a16.ui: ["parm2"], a17.ui: ["ah_body"], l18.ui: ["condition"]}),
            lc(T + ".caller_id.user_name", TL + "➛Caller➛User ID", "string", {s13.ui: ["user_name"]}, parent_table="sys_user", column="user_name"),
            lc(s13.ui + ".found", "13 - TT4 Subflow➛Found", "string", {a15.ui: ["values"]}),
            lc(a14.ui + ".result", "14 - TT4 Scratch Action➛Result", "string", {a15.ui: ["values"]}),
            lc(a14.ui + ".length", "14 - TT4 Scratch Action➛Length", "integer", {a15.ui: ["values"]})])

# ---------------- flow 2: Record Updated trigger with a CHANGESTO condition
U = "Updated_1.current"
u1 = upd(1, "description=UPDATED trigger fired for {{%s.number}}" % U, rec=U)
f2 = Flow("TT4 Runtime Updated", record_trigger("Updated", *INC, "short_descriptionSTARTSWITHTT4RUN-UPD^urgencyCHANGESTO1", "every"), [u1],
          description="Transpiler test 4. Runs when urgency changes to 1 on incidents whose short description starts with TT4RUN-UPD. Safe to delete.",
          label_cache=[lc(U, "Trigger - Record Updated➛Incident Record", "reference", {u1.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False),
                       lc(U + ".number", "Trigger - Record Updated➛Incident Record➛Number", "string", {u1.ui: ["values"]}, parent_table="incident", column="number")])

# ---------------- flow 3: Ask For Approval, then a branch on the result, with End Flow in the approved branch
rule = "ApprovesAnyU[{{static.%s}}]OrRejectsAnyU[{{static.%s}}]" % (ADMIN, ADMIN)
p1 = act("Ask For Approval", 1, {"record": "{{%s}}" % T, "table": INC, "approval_conditions": rule})
p2 = cond("If", 2, "Approved", "{{%s.approval_state}}=approved" % p1.ui)
p3 = upd(3, "description=APPROVED branch for {{%s.number}}" % T, p2.ui)
p4 = end(4, p2.ui)
p5 = else_(5, p2)
p6 = upd(6, "description=NOT APPROVED branch for {{%s.number}}" % T, p5.ui)
p7 = upd(7, "work_notes=TT4 reached the last step")
f3 = Flow("TT4 Runtime Approval", record_trigger("Created", *INC, "short_descriptionSTARTSWITHTT4RUN-APPR"), [p1, p2, p3, p4, p5, p6, p7],
          description="Transpiler test 4. Asks the admin user to approve incidents whose short description starts with TT4RUN-APPR. Safe to delete.",
          label_cache=[lc(T, TL, "reference", {p1.ui: ["record"], p3.ui: ["record"], p6.ui: ["record"], p7.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False),
                       lc(p1.ui + ".approval_state", "1 - Ask For Approval➛Approval State", "choice", {p2.ui: ["condition"]}),
                       lc(T + ".number", TL + "➛Number", "string", {p3.ui: ["values"], p6.ui: ["values"]}, parent_table="incident", column="number")])

# ---------------- flow 4: Send Notification
n1 = act("Send Notification", 1, {"record": "{{%s}}" % T, "table_name": INC, "notification": ("2a811dee7f0232005f58108c3ffa9111", "Incident Priority Raised")})
f4 = Flow("TT4 Runtime Notification", record_trigger("Created", *INC, "short_descriptionSTARTSWITHTT4RUN-NOTIF"), [n1],
          description="Transpiler test 4. Sends one notification for incidents whose short description starts with TT4RUN-NOTIF. Safe to delete.",
          label_cache=[lc(T, TL, "reference", {n1.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False)])

# ---------------- flows 5-7: Weekly, Monthly, Run Once (entries built from the definition rows in the Daily shape)
one = lambda: [lookup(1, "sys_user", "User", "user_name=admin")]
run_at = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=8) + datetime.timedelta(minutes=int(sys.argv[1]) if len(sys.argv) > 1 else 35)).strftime("%Y-%m-%d %H:%M:00")
f5 = Flow("TT4 Weekly", timer_trigger("Weekly", [timer_entry("c685a104c32222002841b63b12d3aed3", "Day of Week", "day_of_week", "day_of_week", 10, "2"),
                                                 timer_entry("a745a104c32222002841b63b12d3ae18", "Time", "time", "glide_time", 100, "1970-01-01 03:20:00")]), one(),
          description="Transpiler test 4 weekly trigger. One lookup. Safe to delete.")
f6 = Flow("TT4 Monthly", timer_trigger("Monthly", [timer_entry("ab36a504c32222002841b63b12d3ae8a", "Day of Month", "day_of_month", "integer", 10, "15", {"integer_type": "day_of_month"}),
                                                   timer_entry("b5d52504c32222002841b63b12d3aeaa", "Time", "time", "glide_time", 100, "1970-01-01 03:25:00")]), one(),
          description="Transpiler test 4 monthly trigger. One lookup. Safe to delete.")
f7 = Flow("TT4 Run Once", timer_trigger("Run Once", [timer_entry("92afcd94c32222002841b63b12d3aee8", "Run in", "run_in", "glide_date_time", 100, run_at)]), one(),
          description="Transpiler test 4 run-once trigger. One lookup. Safe to delete.")

flows = [subflow, f1, f2, f3, f4, f5, f6, f7]
US = "Transpiler Test 20261119e"
xml, usb = actgen.update_set(US, "Transpiler prompt test 4 on dev435256: one custom action, one subflow, seven flows. Safe to delete.", [action], flows)
(OUT / "transpiler_test_20261119e.xml").write_text(xml)
import xml.etree.ElementTree as ET; ET.parse(OUT / "transpiler_test_20261119e.xml")
man = {"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "run_once_value": run_at,
       "action": {"name": action.name, "id": action.id, "snap": action.snap, "cid": action.cid, "fd": action.fd},
       "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in f.steps]} for f in flows]}
(OUT / "manifest.json").write_text(json.dumps(man, indent=1))
print("written", len(xml), "bytes | retrieved set", usb, "| run once at", run_at, "Pacific")
for f in flows: print(" ", f.name, f.id)
print("  action", action.id, "snapshot", action.snap)
