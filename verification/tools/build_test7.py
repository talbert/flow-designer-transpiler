"""Test 7: Parallel, Wait for a duration, Try/Catch at runtime; Daily/Weekly/Monthly set to fire a few minutes after the build. Local files only."""
import json, sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fdlib import *
import actgen
OUT = ROOT / "test_import_20261119h"; INC = ("incident", "Incident"); T = "Created_1.current"; TL = "Trigger - Record Created➛Incident Record"
task = lambda order, text, parent: act("Create Record", order, {"table_name": ("incident_task", "Incident Task"), "values": "incident={{%s.sys_id}}^short_description=%s" % (T, text)}, parent)
l1 = plain("Do the following in Parallel", 1)
l2 = plain("Parallel Branch", 2, parent=l1.ui); a3 = task("2➛3", "TT7 branch A", l2.ui)
l4 = plain("Parallel Branch", 4, parent=l1.ui); a5 = task("4➛5", "TT7 branch B", l4.ui)
l6 = wait_seconds(6, 8)
l7 = plain("Try", 7)
a8 = act("Look Up Record", 8, {"table": ("sys_user", "User"), "conditions": "user_name=tt7_no_such_user", "sort_type": ("sort_asc", "a to z"),
                               "if_multiple_records_are_found_action": ("use_first_record", "Return only the first record"), "__snc_dont_fail_on_error": ("0", "false")}, l7.ui)
a9 = act("Update Record", 9, {"record": "{{%s}}" % T, "table_name": INC, "values": "description=TRY branch finished (not expected)"}, l7.ui)
l10 = catch(10, l7)
a11 = act("Update Record", 11, {"record": "{{%s}}" % T, "table_name": INC, "values": "description=CATCH branch ran for {{%s.number}}" % T}, l10.ui)
a12 = act("Update Record", 12, {"record": "{{%s}}" % T, "table_name": INC, "values": "work_notes=TT7 reached the last step"})
f1 = Flow("TT7 Parallel Wait Try", record_trigger("Created", *INC, "short_descriptionSTARTSWITHTT7RUN"), [l1, l2, a3, l4, a5, l6, l7, a8, a9, l10, a11, a12],
          description="Transpiler test 7. Runs for incidents whose short description starts with TT7RUN. Safe to delete.",
          label_cache=[lc(T + ".sys_id", TL + "➛Sys ID", "GUID", {a3.ui: ["values"], a5.ui: ["values"]}, parent_table="incident", column="sys_id"),
                       lc(T, TL, "reference", {a9.ui: ["record"], a11.ui: ["record"], a12.ui: ["record"]}, ref="incident", ref_disp="Incident", attrs=False),
                       lc(T + ".number", TL + "➛Number", "string", {a11.ui: ["values"]}, parent_table="incident", column="number")])
mins = int(sys.argv[1]) if len(sys.argv) > 1 else 12
pac = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=8) + datetime.timedelta(minutes=mins)
tm = pac.strftime("1970-01-01 %H:%M:00"); dow = str(pac.isoweekday()); dom = str(pac.day)
one = lambda: [lookup(1, "sys_user", "User", "user_name=admin")]
daily_e = timer_entry("3ad4edc0c32222002841b63b12d3aee5", "Time", "time", "glide_time", 100, tm)
wd = timer_entry("c685a104c32222002841b63b12d3aed3", "Day of Week", "day_of_week", "day_of_week", 10, dow); wd["displayValue"] = pac.strftime("%A")
f2 = Flow("TT7 Daily tonight", timer_trigger("Daily", [daily_e]), one(), description="Transpiler test 7 daily trigger. Deactivate after the test. Safe to delete.")
f3 = Flow("TT7 Weekly tonight", timer_trigger("Weekly", [wd, timer_entry("a745a104c32222002841b63b12d3ae18", "Time", "time", "glide_time", 100, tm)]), one(),
          description="Transpiler test 7 weekly trigger. Deactivate after the test. Safe to delete.")
f4 = Flow("TT7 Monthly tonight", timer_trigger("Monthly", [timer_entry("ab36a504c32222002841b63b12d3ae8a", "Day of Month", "day_of_month", "integer", 10, dom, {"integer_type": "day_of_month"}),
                                                           timer_entry("b5d52504c32222002841b63b12d3aeaa", "Time", "time", "glide_time", 100, tm)]), one(),
          description="Transpiler test 7 monthly trigger. Deactivate after the test. Safe to delete.")
flows = [f1, f2, f3, f4]; US = "Transpiler Test 20261119h"
xml, usb = actgen.update_set(US, "Transpiler prompt test 7 on dev435256: four flows. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261119h.xml").write_text(xml)
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "schedule_pacific": pac.strftime("%A %Y-%m-%d %H:%M"),
    "flows": [{"name": f.name, "id": f.id, "snap": f.snap, "steps": [{"kind": s.kind, "order": s.order, "ui": s.ui, "id": s.id, "sid": s.sid, "label": s.kw.get("label")} for s in f.steps]} for f in flows]}, indent=1))
print("set", usb, "| schedules at", pac.strftime("%A %d %H:%M"), "Pacific | dow", dow)
print("ACT", json.dumps({"flows": [{"sys_id": f.id, "active": "", "state": ""} for f in flows], "actions": []}))
