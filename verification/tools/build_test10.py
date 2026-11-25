"""Test 10: a scoped application. One custom action and one flow that calls it, both in scope x_906694_tt10. Local files only.
Generated as global, then every scope, package and application reference is rewritten as Section 11.1 of the prompt says."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdlib import *
import actgen
OUT = ROOT / "test_import_20261119k"; INC = ("incident", "Incident"); T = "Created_1.current"; TL = "Trigger - Record Created➛Incident Record"
APP, APP_NAME, SCOPE = "8d3077db83e41310d6401665eeaad336", "TT10 Scoped Test", "x_906694_tt10"
a = actgen.Action("TT10 Scoped Action", "Transpiler test 10. Returns the scope the script ran in. Safe to delete.",
    inputs=[dict(element="text", label="Text", type="string", mandatory=True)], step_inputs=[dict(element="text", label="text", type="string", value="{{action.text}}")],
    script="(function execute(inputs, outputs) {\n  outputs.result = inputs.text + ' in ' + gs.getCurrentScopeName();\n})(inputs, outputs);",
    step_outputs=[dict(element="result", label="result", type="string")], outputs=[])
a.outputs[0:0] = [dict(element="result", label="Result", type="string", value=a.pill_step("result"), id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid())]
c1 = call_action(1, a, {"text": "{{%s.number}}" % T})
u2 = act("Update Record", 2, {"record": "{{%s}}" % T, "table_name": INC, "values": "description=TT10 scoped flow: [{{%s.result}}]" % c1.ui})
f = Flow("TT10 Scoped Flow", record_trigger("Created", *INC, "short_descriptionSTARTSWITHTT10RUN"), [c1, u2],
         description="Transpiler test 10. Scoped flow. Runs for incidents whose short description starts with TT10RUN. Safe to delete.",
         label_cache=[lc(T + ".number", TL + "➛Number", "string", {c1.ui: ["text"]}, parent_table="incident", column="number"),
                      lc(c1.ui + ".result", "1 - TT10 Scoped Action➛Result", "string", {u2.ui: ["values"]}),
                      lc(T, TL, "reference", {u2.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False)])
US = "Transpiler Test 20261119k"
xml, usb = actgen.update_set(US, "Transpiler prompt test 10 on dev435256: a scoped action and flow. Safe to delete.", [a], [f])
n = {}
def sub(old, new):
    global xml
    n[old[:40]] = xml.count(old); xml = xml.replace(old, new)
sub('<sys_scope display_value="Global">global</sys_scope>', f'<sys_scope display_value="{APP_NAME}">{APP}</sys_scope>')
sub('<sys_scope>global</sys_scope>', f'<sys_scope>{APP}</sys_scope>')
sub('<sys_package display_value="Global" source="global">global</sys_package>', f'<sys_package display_value="{APP_NAME}" source="{SCOPE}">{APP}</sys_package>')
sub('<scope_name>global</scope_name>', f'<scope_name>{SCOPE}</scope_name>')
sub('<application display_value="Global">global</application>', f'<application display_value="{APP_NAME}">{APP}</application>')
sub('<application_name>Global</application_name>', f'<application_name>{APP_NAME}</application_name>')
sub('<application_scope>global</application_scope>', f'<application_scope>{SCOPE}</application_scope>')
sub('<application_version/>', '<application_version>1.0.0</application_version>')
print(n)
# payload_hash must match the rewritten payloads
import re
from fdgen import jhash
def fix(m):
    p = m.group(2).replace("]]]]><![CDATA[>", "]]>")
    return m.group(1) + m.group(2) + "]]></payload><payload_hash>%d</payload_hash>" % jhash(p)
xml = re.sub(r"(<payload><!\[CDATA\[)(.*?)\]\]></payload><payload_hash>-?\d+</payload_hash>", fix, xml, flags=re.S)
(OUT / "transpiler_test_20261119k.xml").write_text(xml)
import xml.etree.ElementTree as ET; ET.parse(OUT / "transpiler_test_20261119k.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "app": APP, "scope": SCOPE,
    "action": {"name": a.name, "id": a.id, "snap": a.snap, "cid": a.cid, "fd": a.fd},
    "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in f.steps]}]}, indent=1))
print("set", usb, "| action", a.id, "| flow", f.id, "| leftover 'global' mentions:", xml.count(">global<"))
