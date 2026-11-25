"""Test 23: triggers without rules until now. Inbound Email and SLA Task (entry shapes confirmed by a local Fluent SDK build and a shipped flow),
Recurrence written from its Appendix H line alone, and SLA Percentage Timer from its catalog line. Local files only."""
import json, sys, pathlib, datetime
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
OUT = V / "test_import_20261120c"
# A: Inbound Email
E = "{{Inbound Email_1.inbound_email}}"
a1 = G("Get Email Header", 1, {"email_record": E, "target_header": "X-TT23"})
a2 = G("Get Latest Response Text From Email", 2, {"email_record": E})
a3 = act("Create Record", 3, {"table_name": "incident", "values": "short_description=Made by TT23A from email^description=TT23A subject [{{Inbound Email_1.subject}}] from [{{Inbound Email_1.from_address}}] header [{{%s.header_value}}] text [{{%s.latest_response_text}}]^EQ" % (a1.ui, a2.ui)})
a4 = G("Associate Record to Email", 4, {"email_record": E, "target_record": "{{%s.record}}" % a3.ui})
a5 = G("Move Email Attachments to Record", 5, {"email_record": E, "target_record": "{{%s.record}}" % a3.ui})
fa = Flow("TT23A Inbound Email", "Transpiler test 23. Inbound Email trigger for emails whose subject contains TT23MAIL. Safe to delete.",
          inbound_email("subjectLIKETT23MAIL", "incident", 50, True), [a1, a2, a3, a4, a5])
# B: SLA Task
S = "SLA Task_1.task_sla_record"
b1 = act("Update Record", 1, {"table_name": "incident", "record": "{{%s.task}}" % S, "values": "description=TT23B SLA flow started for [{{%s.sla.name}}]^EQ" % S})
b2 = G("SLA Percentage Timer", 2, {"percentage": "50"})
b3 = act("Update Record", 3, {"table_name": "incident", "record": "{{%s.task}}" % S, "values": "description=TT23B SLA flow started for [{{%s.sla.name}}] timer status [{{%s.status}}] total [{{%s.total_duration}}]^EQ" % (S, b2.ui, b2.ui)})
fb = Flow("TT23B SLA Task", "Transpiler test 23. SLA Task trigger with SLA Percentage Timer. Attached to the SLA definition TT23B SLA. Safe to delete.", sla_task(), [b1, b2, b3])
# C: Recurrence, from its catalog line: every 2 minutes from the start of today, no end
start = datetime.date.today().strftime("%Y-%m-%d 00:00:00")
rec_entries = [tentry("Repeat", "choice", "recurrence", "periodically", "Custom", mandatory=False),
               tentry("Every", "glide_duration", "repeat", "1970-01-01 00:02:00", mandatory=False),
               tentry("Start date and time", "glide_date_time", "start_date_and_time", start, mandatory=False),
               tentry("End", "choice", "end", "no_end_date", "No end date", mandatory=False),
               tentry("Time zone", "string", "time_zone", "floating", "Use System Time Zone", mandatory=False)]
c1 = act("Create Record", 1, {"table_name": "incident", "values": "short_description=Made by TT23C recurrence^description=TT23C ran at [{{Recurrence_1.run_start_date_time}}]^EQ"})
fc = Flow("TT23C Recurrence", "Transpiler test 23. Recurrence trigger from its catalog line, every 2 minutes. Deactivate after one run. Safe to delete.",
          raw_trigger("Recurrence", "7b3308f67fd21210a652b9277c8665f0", "recurrence", rec_entries), [c1])
flows = [fa, fb, fc]
US = "Transpiler Test 20261120c"
xml, usb = actgen.update_set(US, "Transpiler prompt test 23 on dev435256: Inbound Email, SLA Task and Recurrence triggers. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120c.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120c.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); [print(f.name, f.id) for f in flows]
