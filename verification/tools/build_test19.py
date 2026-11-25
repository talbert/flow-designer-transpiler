"""Test 19: the constructs not yet tested in compact form, all written from the compact rules. Local files only.
Usage: python3 build_test19.py [minutes until the schedules fire, default 10]"""
import json, sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
OUT = V / "test_import_20261119r"; ADMIN = "6816f79cc0a8016401c5a33be04be441"
T = "Created_1.current"; U = "Updated_1.current"
upd = lambda order, text, parent=None, rec_=T: act("Update Record", order, {"table_name": "incident", "record": "{{%s}}" % rec_, "values": text + "^EQ"}, parent)
one = lambda: [act("Look Up Record", 1, {"table": "sys_user", "conditions": "user_name=admin"})]
flows = []
# A: Fire Event, Send Email, Do Until
a1 = act("Fire Event", 1, {"event_name": "a2384bb60a0a140600ee61d2bd0c17c7", "record": "{{%s}}" % T, "table": "incident", "parm1": "TT19 {{%s.number}}" % T, "parm2": "compact"})
a2 = act("Send Email", 2, {"record": "{{%s}}" % T, "table_name": "incident", "watermark_email": "true", "ah_to": "admin@example.com", "ah_subject": "TT19 compact {{%s.number}}" % T, "ah_body": "<p>TT19 body for {{%s.number}}</p>" % T})
l3 = logic("Do the following until", 3, [("condition", "{{%s.number}}ISNOTEMPTY" % T)])
a4 = act("Create Record", 4, {"table_name": "incident_task", "values": "incident={{%s.sys_id}}^short_description=TT19 loop body for {{%s.number}}^EQ" % (T, T)}, l3)
a5 = upd(5, "description=TT19 A done for {{%s.number}}" % T)
flows.append(Flow("TT19 Compact Event Email Until", "Transpiler test 19. Runs for incidents whose short description starts with TT19RUN-A. Safe to delete.",
                  record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT19RUN-A"), [a1, a2, l3, a4, a5]))
# B: Record Updated trigger, CHANGESTO, every update
flows.append(Flow("TT19 Compact Updated", "Transpiler test 19. Runs when urgency changes to 1 on incidents whose short description starts with TT19RUN-UPD. Safe to delete.",
                  record_trigger("Updated", "incident", "short_descriptionSTARTSWITHTT19RUN-UPD^urgencyCHANGESTO1", "every"), [upd(1, "description=TT19 UPDATED fired for {{%s.number}}" % U, rec_=U)]))
# C: Ask For Approval, If, End Flow, Else (Else carries connected_to = the If)
rule = "ApprovesAnyU[{{static.%s}}]OrRejectsAnyU[{{static.%s}}]" % (ADMIN, ADMIN)
p1 = act("Ask For Approval", 1, {"record": "{{%s}}" % T, "table": "incident", "approval_conditions": rule})
p2 = logic("If", 2, [("condition", "{{%s.approval_state}}=approved" % p1.ui)])
p3 = upd(3, "description=TT19 APPROVED branch for {{%s.number}}" % T, p2)
p4 = logic("End", 4, parent=p2)
p5 = logic("Else", 5, connected_to=p2)
p6 = upd(6, "description=TT19 NOT APPROVED branch for {{%s.number}}" % T, p5)
p7 = upd(7, "close_notes=TT19 reached the last step")
flows.append(Flow("TT19 Compact Approval", "Transpiler test 19. Asks the admin user to approve incidents whose short description starts with TT19RUN-APPR. Safe to delete.",
                  record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT19RUN-APPR"), [p1, p2, p3, p4, p5, p6, p7]))
# D: Send Notification
flows.append(Flow("TT19 Compact Notification", "Transpiler test 19. Sends one notification for incidents whose short description starts with TT19RUN-NOTIF. Safe to delete.",
                  record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT19RUN-NOTIF"),
                  [act("Send Notification", 1, {"record": "{{%s}}" % T, "table_name": "incident", "notification": "2a811dee7f0232005f58108c3ffa9111"})]))
# E: Exit Loop and Skip Iteration inside For Each
e1 = act("Look Up Records", 1, {"table": "sys_user", "conditions": "user_nameINabel.tuter,admin,beth.anglin,itil", "sort_column": "user_name", "sort_type": "sort_asc", "max_results": "10"})
e2 = logic("For Each", 2, [("items", "{{%s.Records}}" % e1.ui)])
e3 = logic("If", 3, [("condition", "{{%s.item.user_name}}=admin" % e2.ui)], parent=e2)
e4 = logic("Skip Iteration", 4, parent=e3)
e5 = logic("If", 5, [("condition", "{{%s.item.user_name}}=beth.anglin" % e2.ui)], parent=e2)
e6 = logic("Exit Loop", 6, parent=e5)
e7 = act("Create Record", 7, {"table_name": "incident_task", "values": "incident={{%s.sys_id}}^short_description=TT19 loop task {{%s.item.user_name}}^EQ" % (T, e2.ui)}, e2)
e8 = upd(8, "description=TT19 loop flow finished for {{%s.number}}" % T)
flows.append(Flow("TT19 Compact Loop Control", "Transpiler test 19. Skip Iteration and Exit Loop. Runs for incidents whose short description starts with TT19RUN-LOOP. Safe to delete.",
                  record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT19RUN-LOOP"), [e1, e2, e3, e4, e5, e6, e7, e8]))
# F: custom action with Script, REST and Script steps, compact
ra = Action("TT19 REST Action", "Transpiler test 19. Script, REST and Script steps in the compact shape. Safe to delete.", [("text", "Text")],
    [dict(type="script", label="Make upper", inputs=[("text", "{{action.text}}")], outputs=["upper"],
          script="(function execute(inputs, outputs) {\n  outputs.upper = String(inputs.text).toUpperCase();\n})(inputs, outputs);"),
     dict(type="rest", label="Call login page", config={"base_url": "https://dev435256.service-now.com", "resource_path": "/login.do"},
          pills={"query_params": lambda c: cj({"type": "ADV_NV", "value": [{"name": "probe", "value": "{{step[%s].upper}}" % c[0]}]})}),
     dict(type="script", label="Summarize", inputs=[("upper", lambda c: "{{step[%s].upper}}" % c[0]), ("code", lambda c: "{{step[%s].status_code}}" % c[1])], outputs=["summary"],
          script="(function execute(inputs, outputs) {\n  outputs.summary = inputs.upper + ' / HTTP ' + inputs.code;\n})(inputs, outputs);")],
    [("summary", "Summary", lambda c: "{{step[%s].summary}}" % c[2]), ("status_code", "Status code", lambda c: "{{step[%s].status_code}}" % c[1])])
r1 = call(ra, 1, {"text": "{{%s.number}}" % T})
r2 = upd(2, "description=TT19 summary [{{%s.summary}}] status [{{%s.status_code}}]" % (r1.ui, r1.ui))
flows.append(Flow("TT19 Compact REST", "Transpiler test 19. Calls the compact REST action for incidents whose short description starts with TT19RUN-REST. Safe to delete.",
                  record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT19RUN-REST"), [r1, r2]))
# G-I: Weekly, Monthly, Run Once, set to fire soon (values are in the activating user's time zone, Pacific)
mins = int(sys.argv[1]) if len(sys.argv) > 1 else 10
at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=8) + datetime.timedelta(minutes=mins)
flows.append(Flow("TT19 Compact Weekly", "Transpiler test 19 weekly trigger. One lookup. Safe to delete.", weekly(at.isoweekday(), at.strftime("%H:%M")), one()))
flows.append(Flow("TT19 Compact Monthly", "Transpiler test 19 monthly trigger. One lookup. Safe to delete.", monthly(at.day, at.strftime("%H:%M")), one()))
flows.append(Flow("TT19 Compact Run Once", "Transpiler test 19 run-once trigger. One lookup. Safe to delete.", run_once(at.strftime("%Y-%m-%d %H:%M:00")), one()))
US = "Transpiler Test 20261119r"
xml, usb = actgen.update_set(US, "Transpiler prompt test 19 on dev435256: constructs not yet tested in compact form. Safe to delete.", [ra], flows)
(OUT / "transpiler_test_20261119r.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261119r.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "schedules_fire_pacific": at.strftime("%Y-%m-%d %H:%M"),
    "action": {"name": ra.name, "id": ra.id}, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb, "| bytes", len(xml), "| schedules fire (Pacific)", at.strftime("%Y-%m-%d %H:%M"), "day", at.isoweekday())
print(json.dumps({"flows": [{"sys_id": f.id, "active": "", "state": ""} for f in flows], "actions": [{"sys_id": ra.id, "active": "", "state": ""}]}))
for f in flows: print(" ", f.name, f.id)
