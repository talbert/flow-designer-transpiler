"""Test 5: Created-or-Updated trigger (runs), Repeat trigger (runs), Weekly with a day display value. Local files only."""
import json, sys, pathlib, copy
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdlib import *
import actgen
OUT = ROOT / "test_import_20261119f"; INC = ("incident", "Incident")
tc = json.load(open(ROOT / "fixtures/dev435256/triggers_timer_catalog.json"))
C = "Created or Updated_1.current"
c1 = act("Update Record", 1, {"record": "{{%s}}" % C, "table_name": INC, "values": "description=CREATED-OR-UPDATED trigger fired for {{%s.number}}" % C})
f1 = Flow("TT5 Runtime Created or Updated", record_trigger("Created or Updated", *INC, "short_descriptionSTARTSWITHTT5RUN-CU", "once"), [c1],
          description="Transpiler test 5. Runs once per incident whose short description starts with TT5RUN-CU. Safe to delete.",
          label_cache=[lc(C, "Trigger - Record Created or Updated➛Incident Record", "reference", {c1.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False),
                       lc(C + ".number", "Trigger - Record Created or Updated➛Incident Record➛Number", "string", {c1.ui: ["values"]}, parent_table="incident", column="number")])
rep = copy.deepcopy(tc["repeat"]["trigger_instance"]["trigger_inputs__decoded"]); rep[0]["value"] = "1970-01-01 00:02:00"
f2 = Flow("TT5 Repeat", {"name": "Repeat", "type": "repeat", "definition": "f63f0d94c32222002841b63b12d3aeed", "inputs": rep}, [lookup(1, "sys_user", "User", "user_name=admin")],
          description="Transpiler test 5 repeat trigger, every 2 minutes. Deactivate after the test. Safe to delete.")
wd = timer_entry("c685a104c32222002841b63b12d3aed3", "Day of Week", "day_of_week", "day_of_week", 10, "2"); wd["displayValue"] = "Tuesday"
f3 = Flow("TT5 Weekly with day name", timer_trigger("Weekly", [wd, timer_entry("a745a104c32222002841b63b12d3ae18", "Time", "time", "glide_time", 100, "1970-01-01 03:30:00")]),
          [lookup(1, "sys_user", "User", "user_name=admin")], description="Transpiler test 5 weekly trigger with a day display value. Not activated. Safe to delete.")
flows = [f1, f2, f3]; US = "Transpiler Test 20261119f"
xml, usb = actgen.update_set(US, "Transpiler prompt test 5 on dev435256: three flows. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261119f.xml").write_text(xml)
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb,
    "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in f.steps]} for f in flows]}, indent=1))
print("written", len(xml), "| set", usb); [print(" ", f.name, f.id) for f in flows]
print(json.dumps(rep)[:300])
