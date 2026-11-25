"""Test 25: the Recurrence trigger's other forms (once, daily, weekly, monthly), written from the catalog line, scheduled a few minutes ahead in the
activating user's time zone (US/Pacific for admin on the test instance). Local files only."""
import json, sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
OUT = V / "test_import_20261120l"
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 6
now = datetime.datetime.utcnow() - datetime.timedelta(hours=8)            # Pacific standard time
start = (now + datetime.timedelta(minutes=MIN)).replace(second=0, microsecond=0)
S = start.strftime("%Y-%m-%d %H:%M:%S"); DOW = str(start.isoweekday()); DOM = start.day
REP = [("once", "Does not repeat"), ("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("yearly", "Yearly"), ("periodically", "Custom")]
END = [("no_end_date", "No end date"), ("after", "After"), ("end_date", "On this day")]
def base(kind, label):
    return [tentry("Repeat", "choice", "recurrence", kind, label, mandatory=False, choices=REP),
            tentry("Start date and time", "glide_date_time", "start_date_and_time", S, mandatory=False),
            tentry("End", "choice", "end", "no_end_date", "No end date", mandatory=False, choices=END),
            tentry("Time zone", "string", "time_zone", "floating", "Use System Time Zone", mandatory=False)]
every = lambda n: tentry("Every", "integer", "frequency", n, mandatory=False)
forms = {"Once": base("once", "Does not repeat"),
         "Daily": base("daily", "Daily") + [every(1)],
         "Weekly": base("weekly", "Weekly") + [every(1), tentry("Days of the week", "day_of_week", "days_of_the_week", DOW, DAYS[int(DOW)], mandatory=False)],
         "Monthly": base("monthly", "Monthly") + [every(1), tentry("On", "choice", "day_selection", "fixed_day", "Fixed day", mandatory=False, choices=[("fixed_day", "Fixed day"), ("relative_weekday", "Relative weekday")]),
                                                 tentry("Fixed day", "integer", "day_of_month", DOM, mandatory=False)]}
flows = []
for k, entries in forms.items():
    c1 = act("Create Record", 1, {"table_name": "incident", "values": "short_description=Made by TT25 recurrence %s^description=TT25 %s ran at [{{Recurrence_1.run_start_date_time}}], planned %s^EQ" % (k, k, S)})
    flows.append(Flow("TT25 Recurrence %s" % k, "Transpiler test 25. Recurrence trigger, form %s, first run planned %s Pacific. Deactivate after the run. Safe to delete." % (k, S),
                      raw_trigger("Recurrence", "7b3308f67fd21210a652b9277c8665f0", "recurrence", entries), [c1]))
US = "Transpiler Test 20261120l"
xml, usb = actgen.update_set(US, "Transpiler prompt test 25 on dev435256: Recurrence trigger forms. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120l.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120l.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "planned_start_pacific": S, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb, "| planned", S, "Pacific | dow", DOW, "dom", DOM); print(json.dumps([f.id for f in flows]))
