"""Test 21: the 26 general Global building blocks and the ITSM Spoke actions, each written from its catalog line plus the
value-format table (Appendix H.0). Five compact flows. Local files only."""
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
I = lambda n, o, v, p=None: cat_act(n, "sn_itsm_spoke", o, v, p)
OUT = V / "test_import_20261120a"; T = "Created_1.current"; CUR = "{{%s}}" % T
ABEL, HARDWARE, SDESK = "62826bf03710200044e0bfc8bcbe5df1", "8a5055c9c61122780043563ef53438e3", "d625dccec0a8016700a222a0f7900d06"
CI, STD, POLICY = "3a27d4370a0a0bb4006316812bf45439", "563504cc47410200e90d87e8dee490e2", "5b06ce5db701230034d1da23ee11a965"
PROPOSAL, STTRM, ITEM, PRODUCER = "202340cc47410200e90d87e8dee490fb", "05f16fb9b7517210693cfeb0be11a9a3", "439fef5b83e41310d6401665eeaad379", "3f1dd0320a0a0b99000a53f7604a2ef9"
upd = lambda order, text: act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "description=%s^EQ" % text})
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT21%s RUN" % k)

# A: waits and attachments
a1 = G("Add a Pause", 1, {"seconds": "5"})
a2 = G("Wait For Condition", 2, {"record": CUR, "table_name": "incident", "conditions": "state=2", "timeout_flag": "1", "timeout_duration": "1970-01-01 00:10:00"})
a3 = G("Look Up Attachment", 3, {"source_record": CUR, "file_name": "tt21.txt"})
a4 = G("Get Attachments on Record", 4, {"source_record": CUR})
a5 = G("Check Attachment Readiness", 5, {"attachment_sys_id": "{{%s.parameter}}" % a3.ui})
a6 = G("Create Task", 6, {"task_table": "incident_task", "field_values": "short_description=TT21A copy target^incident={{%s.sys_id}}^EQ" % T, "wait": "0"})
a7 = logic("For Each", 7, [("items", "{{%s.parameter}}" % a4.ui)])
a8 = G("Copy Attachment", 8, {"attachment_record": "{{%s.item}}" % a7.ui, "target_record": "{{%s.Record}}" % a6.ui, "table": "incident_task"}, a7)
a9 = G("Create Problem Record from Incident", 9, {"incident_record": CUR})
a10 = act("Look Up Record", 10, {"table": "sys_attachment", "conditions": "sys_id={{%s.parameter}}" % a3.ui})
a11 = G("Move Attachment", 11, {"source_attachment_record": "{{%s.Record}}" % a10.ui, "target_record": "{{%s.problem_record}}" % a9.ui, "table": "problem"})
a12 = G("Delete Attachment", 12, {"record": "{{%s.Record}}" % a6.ui, "table": "incident_task", "attachment_file_name": "tt21.txt", "delete_all_": "0"})
a13 = G("Wait For Condition", 13, {"record": CUR, "table_name": "incident", "conditions": "state=7", "timeout_flag": "1", "timeout_duration": "1970-01-01 00:00:15"})
a14 = G("Wait For Message", 14, {"message": "TT21MSG", "enable_timeout": "1", "timeout": "1970-01-01 00:00:15"})
a15 = upd(15, "TT21A pause [{{%s.duration}}] wait [{{%s.state}}] att [{{%s.parameter}}] count [{{%s.parameter1}}] ready [{{%s.availability}}] problem [{{%s.problem_record.number}}] wait2 [{{%s.state}}] payload [{{%s.payload}}]"
          % (a1.ui, a2.ui, a3.ui, a4.ui, a5.ui, a9.ui, a13.ui, a14.ui))
fa = Flow("TT21A Waits and Attachments", "Transpiler test 21. Wait and attachment actions from catalog lines, for incidents whose short description starts with TT21A RUN. Safe to delete.",
          trig("A"), [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15])

# B: email
b1 = act("Look Up Record", 1, {"table": "sys_email", "conditions": "subjectSTARTSWITHTT21MAIL^type=received"})
E = "{{%s.Record}}" % b1.ui
b2 = G("Get Email Header", 2, {"email_record": E, "target_header": "X-TT21"})
b3 = G("Get Latest Response Text From Email", 3, {"email_record": E})
b4 = G("Look Up Email Attachments", 4, {"email_record": E})
b5 = G("Associate Record to Email", 5, {"email_record": E, "target_record": CUR})
b6 = G("Move Email Attachments to Record", 6, {"email_record": E, "target_record": CUR})
b7 = act("Send Email", 7, {"record": CUR, "table_name": "incident", "watermark_email": "1", "ah_to": "admin@example.com", "ah_subject": "TT21B out {{%s.number}}" % T, "ah_body": "TT21B body for {{%s.number}}" % T})
b8 = G("Send SMS", 8, {"recipients": "+13035550100", "message": "TT21B sms for {{%s.number}}" % T})
b9 = upd(9, "TT21B header [{{%s.header_value}}] text [{{%s.latest_response_text}}] out [{{%s.email.sys_id}}] sms [{{%s.email.sys_id}}]" % (b2.ui, b3.ui, b7.ui, b8.ui))
b10 = G("Wait For Email Reply", 10, {"record": "{{%s.email}}" % b7.ui, "enable_timeout": "1", "timeout_duration": "1970-01-01 00:04:00"})
b11 = upd(11, "TT21B header [{{%s.header_value}}] text [{{%s.latest_response_text}}] out [{{%s.email.sys_id}}] sms [{{%s.email.sys_id}}] reply state [{{%s.state}}] reply [{{%s.email_reply.subject}}]"
          % (b2.ui, b3.ui, b7.ui, b8.ui, b10.ui, b10.ui))
fb = Flow("TT21B Email Actions", "Transpiler test 21. Email actions from catalog lines, for incidents whose short description starts with TT21B RUN. Safe to delete.",
          trig("B"), [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11])

# C: outage, problem and ITSM Spoke record helpers
c1 = G("Create Outage", 1, {"ah_configuration_item": CI, "ah_type": "outage", "ah_begin": "2026-11-20 08:00:00", "ah_source_record": CUR})
c2 = G("Create Task Outage Relationship", 2, {"ah_outage": "{{%s.outagegr}}" % c1.ui, "ah_task": CUR})
c3 = I("Add Comment", 3, {"ah_task": CUR, "ah_comment": "TT21C comment via ITSM Spoke"})
c4 = I("Update Assignment Group", 4, {"ah_task": CUR, "ah_assignment_group": SDESK})
c5 = I("Update Assignee", 5, {"ah_task": CUR, "ah_assignee": ABEL})
c6 = I("Create Problem from Incident", 6, {"ah_incident": CUR})
c7 = I("Create Normal Change Request from Incident", 7, {"ah_incident": CUR})
c8 = I("Create Emergency Change Request from Incident", 8, {"ah_incident": CUR})
c9 = I("Create Emergency Change Request", 9, {"ah_description": "Made by TT21C", "ah_short_description": "Chg made by TT21C"})
c10 = I("Create Change Task on Change Request", 10, {"ah_change": "{{%s.Change Request}}" % c7.ui, "ah_assignment_group": HARDWARE})
c11 = I("Create Request", 11, {"ah_description": "Made by TT21C", "ah_short_description": "Req made by TT21C"})
c12 = I("Create Catalog Task on Request", 12, {"ah_request": "{{%s.Request}}" % c11.ui})
c13 = I("Create Incident", 13, {"ah_task": "{{%s.Change Request}}" % c9.ui})
c14 = I("Create Standard Change Request", 14, {"ah_short_description": "Std chg by TT21C", "ah_standard_change_template": STD})
c15 = I("Create Standard Change Request from Incident", 15, {"ah_incident": CUR, "standard_change_template": STD})
c16 = upd(16, "TT21C outage [{{%s.outagegr.sys_id}}] problem [{{%s.Problem.number}}] chg [{{%s.Change Request.number}}] echg [{{%s.Change Request.number}}] echg2 [{{%s.Change Request.number}}] ctask [{{%s.Change Task.number}}] req [{{%s.Request.number}}] sctask [{{%s.Catalog Task.number}}] inc [{{%s.Incident.number}}] std [{{%s.change_request_sys_id}}] std2 [{{%s.change_request_sys_id}}]"
          % (c1.ui, c6.ui, c7.ui, c8.ui, c9.ui, c10.ui, c11.ui, c12.ui, c13.ui, c14.ui, c15.ui))
c17 = I("Assign Incident to CI Support Group", 17, {"ah_incident": CUR})
fc = Flow("TT21C Record Helpers", "Transpiler test 21. Outage, problem and ITSM Spoke record helpers from catalog lines, for incidents whose short description starts with TT21C RUN. Safe to delete.",
          trig("C"), [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17])

# D: change helpers
d1 = act("Create Record", 1, {"table_name": "change_request", "values": "short_description=Chg made by TT21D^type=normal^EQ"})
CH = "{{%s.record}}" % d1.ui
d2 = I("Evaluate Change Model", 2, {"change_request": CH})
d3 = I("Check Change for Approved User Approval", 3, {"change_request": CH, "user": ABEL})
d4 = I("Disregard Change Request Approvals", 4, {"change_request": CH})
d5 = I("Cancel Change Tasks created from Flow", 5, {"change_request": CH})
d6 = I("Validate Standard Change Proposal", 6, {"proposal": PROPOSAL})
d7 = I("Standard Change Proposal Rejection Comments", 7, {"proposal": PROPOSAL})
d8 = I("Standard Change Proposal Skipped Approval", 8, {"proposal": PROPOSAL})
d9 = I("Disregard Approvals for STTRM Template", 9, {"sttrm_template": STTRM})
d10 = upd(10, "TT21D chg [{{%s.record.number}}] approved [{{%s.user_approved}}] valid [{{%s.answer}}]" % (d1.ui, d3.ui, d6.ui))
d11 = I("Apply Change Approval Policy", 11, {"action_label": "TT21D policy", "policy": POLICY, "change_request": CH,
        "due_date": json.dumps({"action": "none", "date_type": "actual", "date": "{}", "duration": 1, "duration_type": "days", "schedule": "", "schedule_label": ""}, separators=(",", ":"))})
d12 = upd(12, "TT21D chg [{{%s.record.number}}] approved [{{%s.user_approved}}] valid [{{%s.answer}}] policy state [{{%s.state}}]" % (d1.ui, d3.ui, d6.ui, d11.ui))
fd = Flow("TT21D Change Helpers", "Transpiler test 21. ITSM Spoke change helpers from catalog lines, for incidents whose short description starts with TT21D RUN. Safe to delete.",
          trig("D"), [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12])

# E: catalog
e1 = G("Submit Catalog Item Request", 1, {"catalog_item": ITEM, "catalog_item_inputs": "tt9_note=hello from TT21E", "sysparm_quantity": "1", "sysparm_requested_for": ABEL, "wait_for_completion": "0"})
e2 = I("Create Catalog Task on Request Item", 2, {"ah_request_item": "{{%s.requested_item}}" % e1.ui})
e3 = G("Get Catalog Item from Task", 3, {"task": "{{%s.requested_item}}" % e1.ui})
e4 = G("Get Catalog Item Variables", 4, {"catalog_item": ITEM})
e5 = G("Object To String Array", 5, {"array_object": "{{%s.output}}" % e4.ui})
e6 = G("Record Producer", 6, {"catalog_item": PRODUCER, "catalog_item_inputs": "comments=Made by TT21E record producer^urgency=3", "record_table": "incident", "_snc_dont_fail_on_error": "0"})
e7 = upd(7, "TT21E ritm [{{%s.requested_item.number}}] status [{{%s.status}}] sctask [{{%s.Catalog Task.number}}] item [{{%s.item_id}}] vars [{{%s.output}}] arr [{{%s.object_array}}] produced [{{%s.record}}] pstatus [{{%s.status}}]"
         % (e1.ui, e1.ui, e2.ui, e3.ui, e4.ui, e5.ui, e6.ui, e6.ui))
fe = Flow("TT21E Catalog Actions", "Transpiler test 21. Catalog actions from catalog lines, for incidents whose short description starts with TT21E RUN. Safe to delete.",
          trig("E"), [e1, e2, e3, e4, e5, e6, e7])

flows = [fa, fb, fc, fd, fe]
US = "Transpiler Test 20261120a"
xml, usb = actgen.update_set(US, "Transpiler prompt test 21 on dev435256: general building blocks and ITSM Spoke actions from catalog lines. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120a.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120a.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); [print(f.name, f.id) for f in flows]
