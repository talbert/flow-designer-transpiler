"""Test 22: logic types never run before. Go back to, Make a decision (with and without branches), Decision, Dynamic Flow, Get Flow Outputs,
and the Created or Updated trigger in compact form. Shapes follow shipped flows on the test instance, written as compact entries. Local files only."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
LGX = {"Go back to": "59ea75fd77502110b2b4ddd9cf5a99ef", "Make a decision": "578e90270b2313009002cab937673a7d", "Decision": "b1f542d673331300612c273ffff6a7c7",
       "Dynamic Flow": "5ede711653223300414eddeeff7b1256", "Get Flow Outputs": "167796d8731f33008dcbedcc5ef6a7ce"}
def xlogic(kind, order, inputs=(), parent=None, extra=None, **arrays):
    o = lobj([lin(n, v) for n, v in inputs]); o.update(arrays)
    s = Step("logic", order, o, parent, None, logic_definition=LGX[kind], label=kind); s.extra = extra or {}; return s
OUT = V / "test_import_20261120b"
DT, DT_INPUT = "51b35a90c3723010a9f5e548fa40ddb2", "26e3da90c3723010a9f5e548fa40dde7"       # decision table "Deployment Environment Type Flow", its one input instance_type
ANS_TEST, ANS_DEFAULT = "d3332eb353323010b846ddeeff7b12bd", "f988ce5b9b6630100290af417ef04beb"  # its answers (subflows)
SUB, SUB_IN = "f0124e5ade0346d099c6b01d2bed9524", "064b0fea9d4947c5821c7307e529dbf2"         # "TT13 Subflow": input user_name, output found
def decide(order, value, branches, input_id):
    return xlogic("Make a decision", order, [("decision_label", "TT22 pick a flow"), ("decision_table", DT), ("execution", "first_match"), ("answer_table", "sys_hub_flow"),
                  ("has_branches", "1" if branches else "0"), ("include_otherwise", "0")], extra={"decision_table": DT},
                  decisionTableInputs=[{"id": input_id, "name": "instance_type", "value": value, "displayValue": value, "children": [], "parameter": {"type": "choice"}, "scriptActive": False}])

# A: Created or Updated trigger (compact), Make a decision without branches, Go back to
T = "Created or Updated_1.current"; CUR = "{{%s}}" % T
a1 = decide(1, "test", False, "instance_type")
a2 = act("Look Up Record", 2, {"table": "incident", "conditions": "sys_id={{%s.sys_id}}" % T})
a3 = logic("If", 3, [("condition", "{{%s.Record.urgency}}=3" % a2.ui)])
a4 = act("Update Record", 4, {"table_name": "incident", "record": CUR, "values": "urgency=2^EQ"}, a3)
a5 = xlogic("Go back to", 5, [("go_back_to_step", a2.ui)], a3)
a6 = act("Update Record", 6, {"table_name": "incident", "record": CUR, "values": "description=TT22A answer [{{%s.answer.name}}] urgency after loop [{{%s.Record.urgency}}]^EQ" % (a1.ui, a2.ui)})
fa = Flow("TT22A Decision and Go Back", "Transpiler test 22. Created or Updated trigger, Make a decision, Go back to, for incidents whose short description starts with TT22A RUN. Safe to delete.",
          record_trigger("Created or Updated", "incident", "short_descriptionSTARTSWITHTT22A RUN", "once"), [a1, a2, a3, a4, a5, a6])

# B: Make a decision with branches, Dynamic Flow, Get Flow Outputs
T = "Created_1.current"; CUR = "{{%s}}" % T
b1 = decide(1, "{{%s.description}}" % T, True, DT_INPUT)
b2 = xlogic("Decision", 2, [("label", "Test"), ("answer", ANS_TEST)], b1)
b3 = act("Update Record", 3, {"table_name": "incident", "record": CUR, "values": "description=TT22B branch TEST^EQ"}, b2)
b4 = xlogic("Decision", 4, [("label", "Default"), ("answer", ANS_DEFAULT)], b1)
b5 = act("Update Record", 5, {"table_name": "incident", "record": CUR, "values": "description=TT22B branch DEFAULT^EQ"}, b4)
b6 = xlogic("Dynamic Flow", 6, [("flow_template", SUB), ("wait_for_completion", "1"), ("flow", SUB)],
            dynamicInputs=[{"id": SUB_IN, "name": "user_name", "label": "User name", "type": "string", "value": "abel.tuter", "scriptActive": False}])
b7 = xlogic("Get Flow Outputs", 7, [("flow_template", SUB), ("context", "{{%s.context}}" % b6.ui)])
b8 = act("Update Record", 8, {"table_name": "incident", "record": CUR, "values": "close_notes=TT22B dynamic [{{%s.found}}] outputs [{{%s.found}}]^EQ" % (b6.ui, b7.ui)})
fb = Flow("TT22B Decision Branches and Dynamic Flow", "Transpiler test 22. Make a decision with branches, Dynamic Flow, Get Flow Outputs, for incidents whose short description starts with TT22B RUN. Safe to delete.",
          record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT22B RUN"), [b1, b2, b3, b4, b5, b6, b7, b8])
# C: Append to Flow Variables on an array of objects. The file the Fluent SDK built (sdk_probe3), with only the scope changed to Global.
class Raw:
    name, id = "TT22C Append To Flow Variables", "341eca5f2ad64e15b5f6037e2bbd91d9"
    def payload(self):
        x = (V / "sdk_probe3/update/tt22c_append_sdk_built.xml").read_text()
        assert x.count('<sys_scope display_value="x_906694_tt11">8f6baeba9ba94590969cbe31fc69e713</sys_scope>') == 9
        return x.replace('<sys_scope display_value="x_906694_tt11">8f6baeba9ba94590969cbe31fc69e713</sys_scope>', '<sys_scope display_value="Global">global</sys_scope>').replace('<?xml version="1.0"?>', '<?xml version="1.0" encoding="UTF-8"?>')
flows = [fa, fb, Raw()]
US = "Transpiler Test 20261120b"
xml, usb = actgen.update_set(US, "Transpiler prompt test 22 on dev435256: logic types never run before. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120b.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120b.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb); [print(f.name, f.id) for f in flows]
