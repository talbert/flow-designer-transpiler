"""Test 19b: the compact REST-step action again, with the name-value item carrying its `attributes` object as platform-written steps do. Local files only."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
OUT = V / "test_import_20261119t"; T = "Created_1.current"
NV = lambda c: cj({"type": "ADV_NV", "value": [{"name": "probe", "value": "{{step[%s].upper}}" % c[0], "attributes": {"omit_if_empty": False, "mandatory": False}}]})
HD = lambda c: cj({"type": "ADV_NV", "value": [{"name": "Accept", "value": "application/json", "attributes": {"omit_if_empty": False, "mandatory": False}},
    {"name": "X-TT19", "value": "hdr-{{action.text}}", "attributes": {"omit_if_empty": False, "mandatory": False}}]})
ra = Action("TT19c REST Action", "Transpiler test 19c. Script, REST and Script steps in the compact shape. Safe to delete.", [("text", "Text")],
    [dict(type="script", label="Make upper", inputs=[("text", "{{action.text}}")], outputs=["upper"],
          script="(function execute(inputs, outputs) {\n  outputs.upper = String(inputs.text).toUpperCase();\n})(inputs, outputs);"),
     dict(type="rest", label="Call echo", config={"base_url": "https://dev435256.service-now.com", "resource_path": "/api/906694/tt19_echo"}, pills={"query_params": NV, "headers": HD}),
     dict(type="script", label="Summarize", inputs=[("body", lambda c: "{{step[%s].response_body}}" % c[1]), ("code", lambda c: "{{step[%s].status_code}}" % c[1])], outputs=["summary"],
          script="(function execute(inputs, outputs) {\n  var r = JSON.parse(inputs.body).result;\n  outputs.summary = 'probe=' + r.probe + ' header=' + r.header + ' / HTTP ' + inputs.code;\n})(inputs, outputs);")],
    [("summary", "Summary", lambda c: "{{step[%s].summary}}" % c[2]), ("status_code", "Status code", lambda c: "{{step[%s].status_code}}" % c[1])])
r1 = call(ra, 1, {"text": "{{%s.number}}" % T})
r2 = act("Update Record", 2, {"table_name": "incident", "record": "{{%s}}" % T, "values": "description=TT19c summary [{{%s.summary}}] status [{{%s.status_code}}]^EQ" % (r1.ui, r1.ui)})
f = Flow("TT19c Compact REST", "Transpiler test 19c. Calls the compact REST action for incidents whose short description starts with TT19CRUN-REST. Safe to delete.",
         record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT19CRUN-REST"), [r1, r2])
US = "Transpiler Test 20261119t"
xml, usb = actgen.update_set(US, "Transpiler prompt test 19c on dev435256: compact REST-step action. Safe to delete.", [ra], [f])
(OUT / "transpiler_test_20261119t.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261119t.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "action": {"name": ra.name, "id": ra.id}, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []}]}, indent=1))
print("set", usb, "| action", ra.id, "| flow", f.id)
