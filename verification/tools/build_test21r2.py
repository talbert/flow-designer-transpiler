"""Test 21 round 2: fixes and re-runs after the first results. Local files only."""
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
OUT = V / "test_import_20261120e"; T = "Created_1.current"; CUR = "{{%s}}" % T
ABEL, ITEM, PRODUCER, SMSUSER = "62826bf03710200044e0bfc8bcbe5df1", "439fef5b83e41310d6401665eeaad379", "3f1dd0320a0a0b99000a53f7604a2ef9", sys.argv[1]
POLICY, PROPOSAL, STTRM = "5b06ce5db701230034d1da23ee11a965", "202340cc47410200e90d87e8dee490fb", "05f16fb9b7517210693cfeb0be11a9a3"
upd = lambda order, text, field="description": act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "%s=%s^EQ" % (field, text)})
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT21%s RUN" % k)
D = "Transpiler test 21 round 2. %s, for incidents whose short description starts with TT21%s RUN. Safe to delete."
flows = []
# E5 / E6: catalog variables as a JSON object
e1 = G("Submit Catalog Item Request", 1, {"catalog_item": ITEM, "catalog_item_inputs": json.dumps({"tt9_note": "hello from TT21E5"}), "sysparm_quantity": "1", "sysparm_requested_for": ABEL, "wait_for_completion": "0"})
e2 = I("Create Catalog Task on Request Item", 2, {"ah_request_item": "{{%s.requested_item}}" % e1.ui})
e3 = G("Get Catalog Item from Task", 3, {"task": "{{%s.requested_item}}" % e1.ui})
e4 = upd(4, "TT21E5 ritm [{{%s.requested_item.number}}] status [{{%s.status}}] sctask [{{%s.Catalog Task.number}}] item [{{%s.item_id}}]" % (e1.ui, e1.ui, e2.ui, e3.ui))
flows.append(Flow("TT21E5 Submit Catalog Item JSON", D % ("Submit Catalog Item Request with variables as a JSON object", "E5"), trig("E5"), [e1, e2, e3, e4]))
p1 = G("Record Producer", 1, {"catalog_item": PRODUCER, "catalog_item_inputs": json.dumps({"comments": "Made by TT21E6 record producer", "urgency": "3"}), "record_table": "incident", "_snc_dont_fail_on_error": "0"})
p2 = upd(2, "TT21E6 produced [{{%s.record}}] pstatus [{{%s.status}}] err [{{%s.error_message}}]" % (p1.ui, p1.ui, p1.ui))
flows.append(Flow("TT21E6 Record Producer JSON", D % ("Record Producer with variables as a JSON object", "E6"), trig("E6"), [p1, p2]))
# B2: header and text printed first, Send SMS to a user record, then Wait For Email Reply
b1 = act("Look Up Record", 1, {"table": "sys_email", "conditions": "subjectSTARTSWITHTT21MAIL^type=received"})
E = "{{%s.Record}}" % b1.ui
b2 = G("Get Email Header", 2, {"email_record": E, "target_header": "X-TT21"})
b3 = G("Get Latest Response Text From Email", 3, {"email_record": E})
b4 = G("Look Up Email Attachments", 4, {"email_record": E})
b5 = upd(5, "TT21B2 header [{{%s.header_value}}] text [{{%s.latest_response_text}}]" % (b2.ui, b3.ui))
b6 = act("Send Email", 6, {"record": CUR, "table_name": "incident", "watermark_email": "1", "ah_to": "admin@example.com", "ah_subject": "TT21B2 out {{%s.number}}" % T, "ah_body": "TT21B2 body for {{%s.number}}" % T})
b7 = G("Send SMS", 7, {"recipients": SMSUSER, "message": "TT21B2 sms for {{%s.number}}" % T})
b8 = upd(8, "TT21B2 header [{{%s.header_value}}] text [{{%s.latest_response_text}}] out [{{%s.email.subject}}] sms [{{%s.email.sys_id}}]" % (b2.ui, b3.ui, b6.ui, b7.ui))
b9 = G("Wait For Email Reply", 9, {"record": "{{%s.email}}" % b6.ui, "enable_timeout": "1", "timeout_duration": "1970-01-01 00:04:00"})
b10 = upd(10, "TT21B2 reply state [{{%s.state}}] reply [{{%s.email_reply.subject}}]" % (b9.ui, b9.ui), "close_notes")
flows.append(Flow("TT21B2 Email Actions", D % ("Email actions, Send SMS to a user record, Wait For Email Reply", "B2"), trig("B2"), [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10]))
# C2: Assign Incident to CI Support Group alone (no assignee on the incident)
c1 = I("Assign Incident to CI Support Group", 1, {"ah_incident": CUR})
c2 = upd(2, "TT21C2 assigned")
flows.append(Flow("TT21C2 CI Support Group", D % ("Assign Incident to CI Support Group", "C2"), trig("C2"), [c1, c2]))
# D2: the change helpers after the step that failed
d0 = act("Look Up Record", 1, {"table": "std_change_proposal", "conditions": "sys_id=%s" % PROPOSAL})
P = "{{%s.Record}}" % d0.ui
d1 = act("Create Record", 2, {"table_name": "change_request", "values": "short_description=Chg made by TT21D2^type=normal^EQ"})
CH = "{{%s.record}}" % d1.ui
d7 = I("Standard Change Proposal Rejection Comments", 3, {"proposal": P})
d8 = I("Standard Change Proposal Skipped Approval", 4, {"proposal": P})
d9 = I("Disregard Approvals for STTRM Template", 5, {"sttrm_template": STTRM})
d10 = upd(6, "TT21D2 chg [{{%s.record.number}}] proposal [{{%s.Record.number}}]" % (d1.ui, d0.ui))
d11 = I("Apply Change Approval Policy", 7, {"action_label": "TT21D2 policy", "policy": POLICY, "change_request": CH,
        "due_date": json.dumps({"action": "none", "date_type": "actual", "date": "{}", "duration": 1, "duration_type": "days", "schedule": "", "schedule_label": ""}, separators=(",", ":"))})
d12 = upd(8, "TT21D2 policy state [{{%s.state}}]" % d11.ui, "close_notes")
d13 = I("Validate Standard Change Proposal", 9, {"proposal": P})
d14 = upd(10, "TT21D2 valid [{{%s.answer}}]" % d13.ui, "work_notes")
flows.append(Flow("TT21D2 Change Helpers", D % ("ITSM Spoke change helpers, second part", "D2"), trig("D2"), [d0, d1, d7, d8, d9, d10, d11, d12, d13, d14]))
# A2: Copy Attachment with nothing deleting the copy afterwards
a1 = G("Wait For Condition", 1, {"record": CUR, "table_name": "incident", "conditions": "state=2", "timeout_flag": "0"})
a2 = G("Get Attachments on Record", 2, {"source_record": CUR})
a3 = G("Create Task", 3, {"task_table": "incident_task", "field_values": "short_description=TT21A2 copy target^incident={{%s.sys_id}}^EQ" % T, "wait": "0"})
a4 = logic("For Each", 4, [("items", "{{%s.parameter}}" % a2.ui)])
a5 = G("Copy Attachment", 5, {"attachment_record": "{{%s.item}}" % a4.ui, "target_record": "{{%s.Record}}" % a3.ui, "table": "incident_task"}, a4)
a6 = upd(6, "TT21A2 count [{{%s.parameter1}}] task [{{%s.Record.number}}]" % (a2.ui, a3.ui))
flows.append(Flow("TT21A2 Copy Attachment", D % ("Copy Attachment kept on the target", "A2"), trig("A2"), [a1, a2, a3, a4, a5, a6]))
# 22C2: the SDK-built Append flow, with the appended element written as a one-item list instead of a bare object
class Raw:
    name, id = "TT22C Append To Flow Variables", "341eca5f2ad64e15b5f6037e2bbd91d9"
    def payload(self):
        if getattr(Raw, "_txt", None): return '<?xml version="1.0" encoding="UTF-8"?>' + Raw._txt
        x = (V / "sdk_probe3/update/tt22c_append_sdk_built.xml").read_text()
        x = x.replace('<sys_scope display_value="x_906694_tt11">8f6baeba9ba94590969cbe31fc69e713</sys_scope>', '<sys_scope display_value="Global">global</sys_scope>').replace('<?xml version="1.0"?>', '<?xml version="1.0" encoding="UTF-8"?>')
        root = ET.fromstring(x.split("?>", 1)[1]); n = 0
        for el_ in root.findall("sys_hub_flow_logic_instance_v2"):
            if el_.attrib.get("action") == "delete_multiple" or el_.findtext("logic_definition") != "4784e82683031210d266f953d22bc0fd": continue
            v = json.loads(gzip.decompress(base64.b64decode(el_.findtext("values"))))
            for k in ("inputs", "variables"):
                for e in v[k]:
                    for f in ("value", "displayValue"):
                        j = json.loads(e[f])
                        if isinstance(j["complexObject"]["$COCollectionField"], dict): j["complexObject"]["$COCollectionField"] = [j["complexObject"]["$COCollectionField"]]; n += 1
                        e[f] = json.dumps(j, separators=(",", ":"))
            el_.find("values").text = enc(v)
        assert n == 8, n
        txt = ET.tostring(root, encoding="unicode")
        for old in sorted(set(re.findall(r"<sys_id>([0-9a-f]{32})</sys_id>", txt))):   # fresh ids, so the import does not collide with the first copy
            new = gid(); txt = txt.replace(old, new).replace(hy(old), hy(new))
            if old == "341eca5f2ad64e15b5f6037e2bbd91d9": Raw.id = new
        txt = txt.replace("TT22C Append To Flow Variables", "TT22C2 Append List Form").replace("TT22C RUN", "TT22C2 RUN").replace("TT22C item", "TT22C2 item")
        Raw.name = "TT22C2 Append List Form"; Raw._txt = txt
        return '<?xml version="1.0" encoding="UTF-8"?>' + txt
RAW = Raw()
if len(sys.argv) > 2 and sys.argv[2] == "append": flows = [RAW]
SUF = "f" if flows == [RAW] else "e2"
if flows == [RAW]: RAW.payload()
OUT = V / ("test_import_20261120" + SUF); OUT.mkdir(exist_ok=True)
US = "Transpiler Test 20261120" + SUF
xml, usb = actgen.update_set(US, "Transpiler prompt test 21 round 2 on dev435256. Safe to delete.", [], flows)
(OUT / ("transpiler_test_20261120%s.xml" % SUF)).write_text(xml); ET.parse(OUT / ("transpiler_test_20261120%s.xml" % SUF))
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); print(json.dumps([f.id for f in flows]))
