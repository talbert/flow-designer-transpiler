"""Test 26: flow error handler (Top Level Try / Top Level Catch), Visual Task Board Spoke actions, the Knowledge Management trigger,
and the Recurrence forms not yet run (yearly, every 2 days, two weekdays, relative weekday, end date). Local files only."""
import json, sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
CAT = json.load(open(V / "fixtures/dev435256/full_catalog.json"))
def cat_act(name, scope, order, values, parent=None):
    a = [x for x in CAT["actions"] if x["name"] == name and x["sys_scope.scope"] == scope and x["state"] == "published" and x.get("active", "true") != "false"]
    if name == "Create VTB Card": a = [x for x in a if x["sys_id"] == "c6c9d5860fa63300adbf483f68767ef4"]     # the line printed in Appendix H
    assert len(a) == 1, (name, len(a)); a = a[0]
    types = {r["element"]: r["internal_type"] for r in CAT["action_inputs"] if r["model"] == a["sys_id"]}
    return Step("action", order, [short(k, v, types[k]) for k, v in values.items()], parent, action_type=a["sys_id"], label=name)
G = lambda n, o, v, p=None: cat_act(n, "global", o, v, p)
B = lambda n, o, v, p=None: cat_act(n, "sn_vtb_ah", o, v, p)
OUT = V / "test_import_20261120m"; T = "Created_1.current"; CUR = "{{%s}}" % T
ABEL, GEORGE = "62826bf03710200044e0bfc8bcbe5df1", "67484bb0eb32010045e1a5115206fee6"
upd = lambda order, text, field="description", parent=None: act("Update Record", order, {"table_name": "incident", "record": CUR, "values": "%s=%s^EQ" % (field, text)}, parent)
trig = lambda k: record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT26%s RUN" % k)
def xl(defid, label, order, inputs=(), parent=None):
    return Step("logic", order, lobj([lin(n, v) for n, v in inputs]), parent, None, logic_definition=defid, label=label)
flows = []

# ---- A: error handler. Top Level Try holds every main step; Top Level Catch (enabled) holds the handler steps.
t0 = xl("e9060aa2c3013010ace8b740ad40dd51", "Top Level Try", 0)
a1 = upd(1, "TT26A step 1 ran", parent=t0)
a2 = act("Look Up Record", 2, {"table": "sys_user", "conditions": "user_name=tt26_no_such_user", "__snc_dont_fail_on_error": "0"}, t0)
a3 = upd(3, "TT26A step 3 ran, which is wrong", "close_notes", t0)
c4 = xl("35d60003e6022010a5e40cdd1254dd23", "Top Level Catch", 4, [("enabled", "1")])
a5 = upd(5, "TT26A handler ran, code [{{%s.__status__.code}}] message [{{%s.__status__.message}}]" % (c4.ui, c4.ui), "close_notes", c4)
flows.append(Flow("TT26A Error Handler", "Transpiler test 26. Flow error handler: the second step fails and the handler runs, for incidents whose short description starts with TT26A RUN. Safe to delete.",
                  trig("A"), [t0, a1, a2, a3, c4, a5]))

# ---- V: Visual Task Board Spoke, all 14 actions
v1 = B("Create Freeform VTB", 1, {"Name": "TT26 board {{%s.number}}" % T, "Owner": ABEL})
BD = "{{%s.Board}}" % v1.ui
v2 = B("Add VTB Lane", 2, {"Board": BD, "Lane_Name": "TT26 lane A"})
v3 = B("Add VTB Lane", 3, {"Board": BD, "Lane_Name": "TT26 lane B"})
v4 = B("Rename VTB Lane", 4, {"Lane": "{{%s.Lane}}" % v3.ui, "New_Lane_Name": "TT26 lane B2"})
v5 = B("Reorder VTB Lane", 5, {"Lane": "{{%s.Lane}}" % v3.ui, "New_Order": "0"})
v6 = B("Add VTB Member", 6, {"Board": BD, "User": GEORGE})
v7 = B("Create VTB Card", 7, {"Board": BD, "Lane": "{{%s.Lane.sys_id}}" % v2.ui, "Task": CUR})
CD = "{{%s.Card}}" % v7.ui
v8 = B("Assign VTB Card", 8, {"Card": CD, "User": GEORGE})
v9 = B("Move VTB Card", 9, {"Card": CD, "Lane": "{{%s.Lane}}" % v3.ui})
v10 = B("Remove Assignee from VTB Card", 10, {"Card": CD})
v11 = B("Get Visual Task Board Lanes", 11, {"board": "{{%s.Board.sys_id}}" % v1.ui})
v12 = B("Add VTB Lane", 12, {"Board": BD, "Lane_Name": "TT26 lane C"})
v13 = B("Delete VTB Lane", 13, {"Lane": "{{%s.Lane}}" % v12.ui})
v14 = B("Remove VTB Member", 14, {"Board": BD, "User": GEORGE})
v15 = upd(15, "TT26V board [{{%s.Board.name}}] card [{{%s.Card.sys_id}}] lanes [{{%s.output}}]" % (v1.ui, v7.ui, v11.ui))
v16 = B("Create Flexible VTB", 16, {"Name": "TT26 flex {{%s.number}}" % T, "Task_Table": "incident", "Filter": "short_descriptionSTARTSWITHTT26V", "Owner": ABEL})
v17 = B("Create Guided VTB", 17, {"Name": "TT26 guided {{%s.number}}" % T, "Task_Table": "incident", "Lane_Field": "state", "Filter": "short_descriptionSTARTSWITHTT26V", "Owner": ABEL})
v18 = upd(18, "TT26V flex [{{%s.Board.name}}] guided [{{%s.Board.name}}]" % (v16.ui, v17.ui), "close_notes")
flows.append(Flow("TT26V Visual Task Board", "Transpiler test 26. Visual Task Board Spoke actions from catalog lines, for incidents whose short description starts with TT26V RUN. Safe to delete.",
                  trig("V"), [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, v13, v14, v15, v16, v17, v18]))

# ---- K: Knowledge Management trigger (empty trigger_inputs); a knowledge base names the flow in kb_publish_flow
K = "Knowledge Management_1.knowledge"
k1 = G("Publish Article", 1, {"knowledge_record": "{{%s}}" % K})
k2 = act("Update Record", 2, {"table_name": "kb_knowledge", "record": "{{%s}}" % K, "values": "meta=TT26K publish flow ran for {{%s.number}}^EQ" % K})
flows.append(Flow("TT26K Knowledge Publish", "Transpiler test 26. Knowledge Management trigger; set as the publish flow of the knowledge base TT26 KB. Safe to delete.",
                  raw_trigger("Knowledge Management", "9bdb2c0483331210730e5b43c22bc071", "knowledge_management", []), [k1, k2]))

# ---- R: Recurrence forms not yet run. Start in the past, so the next run the platform schedules shows how it read the entries.
now = datetime.datetime.utcnow() - datetime.timedelta(hours=8)
S = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d 23:30:00")          # yesterday 11:30 PM Pacific
REP = [("once", "Does not repeat"), ("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("yearly", "Yearly"), ("periodically", "Custom")]
END = [("no_end_date", "No end date"), ("after", "After"), ("end_date", "On this day")]
SEL = [("fixed_day", "Fixed day"), ("relative_weekday", "Relative weekday")]
def base(kind, label, end="no_end_date", endlabel="No end date"):
    return [tentry("Repeat", "choice", "recurrence", kind, label, mandatory=False, choices=REP), tentry("Start date and time", "glide_date_time", "start_date_and_time", S, mandatory=False),
            tentry("End", "choice", "end", end, endlabel, mandatory=False, choices=END), tentry("Time zone", "string", "time_zone", "floating", "Use System Time Zone", mandatory=False)]
every = lambda n: tentry("Every", "integer", "frequency", n, mandatory=False)
enddt = (now + datetime.timedelta(days=3)).strftime("%Y-%m-%d 00:00:00")
forms = {"Yearly": base("yearly", "Yearly") + [every(1), tentry("Every", "month_of_year", "repeat_month", "3", "March", mandatory=False), tentry("On", "choice", "day_selection", "fixed_day", "Fixed day", mandatory=False, choices=SEL), tentry("Fixed day", "integer", "day_of_month", 15, mandatory=False)],
         "Every2Days": base("daily", "Daily") + [every(2)],
         "TwoWeekdays": base("weekly", "Weekly") + [every(1), tentry("Days of the week", "day_of_week", "days_of_the_week", "2,4", "Tuesday, Thursday", mandatory=False)],
         "SecondTuesday": base("monthly", "Monthly") + [every(1), tentry("On", "choice", "day_selection", "relative_weekday", "Relative weekday", mandatory=False, choices=SEL),
                           tentry("Relative week", "choice", "relative_week", "2", "Second", mandatory=False, choices=[("1", "First"), ("2", "Second"), ("3", "Third"), ("4", "Fourth"), ("5", "Last")]),
                           tentry("Weekday", "day_of_week", "relative_weekday", "2", "Tuesday", mandatory=False)],
         "EndDate": base("daily", "Daily", "end_date", "On this day") + [every(1), tentry("Date and Time", "glide_date_time", "end_date_time", enddt, mandatory=False)]}
rflows = []
for k, entries in forms.items():
    c1 = act("Create Record", 1, {"table_name": "incident", "values": "short_description=Made by TT26R %s^description=TT26R %s ran at [{{Recurrence_1.run_start_date_time}}]^EQ" % (k, k)})
    f = Flow("TT26R Recurrence %s" % k, "Transpiler test 26. Recurrence trigger, form %s, start %s Pacific. Deactivate after reading the next run. Safe to delete." % (k, S),
             raw_trigger("Recurrence", "7b3308f67fd21210a652b9277c8665f0", "recurrence", entries), [c1]); rflows.append(f)
flows += rflows
US = "Transpiler Test 20261120m"
xml, usb = actgen.update_set(US, "Transpiler prompt test 26 on dev435256: error handler, Visual Task Board, Knowledge Management trigger, more Recurrence forms. Safe to delete.", [], flows)
(OUT / "transpiler_test_20261120m.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261120m.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "recurrence_start_pacific": S, "end_date_time": enddt, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []} for f in flows]}, indent=1))
print("set", usb, "| recurrence start", S, "| end", enddt); print(json.dumps({f.name: f.id for f in flows}, indent=0))
