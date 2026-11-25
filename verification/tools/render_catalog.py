"""Renders fixtures/dev435256/full_catalog.json (+ full_catalog_choices.json) as the compact text lists of prompt Appendix H. No instance calls."""
import json, collections, pathlib, sys
ROOT = pathlib.Path(__file__).parent.parent
c = json.load(open(ROOT / "fixtures/dev435256/full_catalog.json"))
CH = collections.defaultdict(list)
for r in json.load(open(ROOT / "fixtures/dev435256/full_catalog_choices.json")):
    if r["value"] not in CH[(r["name"], r["element"])]: CH[(r["name"], r["element"])].append(r["value"])
RUN = {"triggers": {"Created", "Updated", "Created or Updated", "Daily", "Weekly", "Monthly", "Repeat", "Run Once", "Service Catalog", "Inbound Email", "SLA Task", "Recurrence", "Knowledge Management"},
       "logic": {"If", "Else If", "Else", "End", "For Each", "Do the following until", "Set Flow Variables", "Assign Subflow Outputs", "Wait for a duration of time",
                 "Do the following in Parallel", "Parallel Branch", "Try", "Catch", "Exit Loop", "Skip Iteration",
                 "Go back to", "Make a decision", "Decision", "Dynamic Flow", "Get Flow Outputs", "Append to Flow Variables", "Top Level Try", "Top Level Catch"},   # added by tests 22 and 23
       "steps": {"Script", "REST", "JSON Parser"},
       "actions": {("global", n) for n in ["Create Record", "Update Record", "Look Up Record", "Look Up Records", "Get Catalog Variables", "Create Catalog Task", "Send Email",
                   "Send Notification", "Ask For Approval", "Fire Event", "Log", "Create Task", "Create or Update Record", "Update Multiple Records", "Delete Record"]}
                  | {("sn_itsm_spoke", "Add Worknote"), ("sn_itsm_spoke", "Create Incident Task on Incident")}
                  # test 21 (2026-11-20)
                  | {("global", n) for n in ["Add a Pause", "Wait For Condition", "Wait For Message", "Wait For Email Reply", "Send SMS", "SLA Percentage Timer", "Look Up Attachment",
                     "Copy Attachment", "Move Attachment", "Delete Attachment", "Get Attachments on Record", "Check Attachment Readiness", "Look Up Email Attachments",
                     "Move Email Attachments to Record", "Associate Record to Email", "Get Email Header", "Get Latest Response Text From Email", "Create Outage",
                     "Create Task Outage Relationship", "Create Problem Record from Incident", "Submit Catalog Item Request", "Record Producer", "Get Catalog Item Variables",
                     "Get Catalog Item from Task", "Object To String Array"]}
                  | {("sn_itsm_spoke", n) for n in ["Add Comment", "Apply Change Approval Policy", "Assign Incident to CI Support Group", "Cancel Change Tasks created from Flow",
                     "Check Change for Approved User Approval", "Create Catalog Task on Request", "Create Catalog Task on Request Item", "Create Change Task on Change Request",
                     "Create Emergency Change Request", "Create Emergency Change Request from Incident", "Create Incident", "Create Normal Change Request from Incident",
                     "Create Problem from Incident", "Create Request", "Create Standard Change Request", "Create Standard Change Request from Incident",
                     "Disregard Approvals for STTRM Template", "Disregard Change Request Approvals", "Evaluate Change Model", "Standard Change Proposal Rejection Comments",
                     "Standard Change Proposal Skipped Approval", "Update Assignee", "Update Assignment Group"]}
                  # test 26 (2026-11-20): Publish Article and the 14 Visual Task Board Spoke actions
                  | {("global", "Publish Article")} | {("sn_vtb_ah", n) for n in ["Add VTB Lane", "Add VTB Member", "Assign VTB Card", "Create Flexible VTB", "Create Freeform VTB", "Create Guided VTB", "Create VTB Card", "Delete VTB Lane", "Get Visual Task Board Lanes", "Move VTB Card", "Remove Assignee from VTB Card", "Remove VTB Member", "Rename VTB Lane", "Reorder VTB Lane"]}}
def group(rows):
    d = collections.defaultdict(list)
    for r in rows:
        if r.get("active", "true") != "false": d[r["model"]].append(r)
    for v in d.values(): v.sort(key=lambda r: (int(r["order"] or 0), r["element"]))
    return d
def io(r, table):
    t = r["internal_type"] or "string"
    if r.get("reference"): t += f"({r['reference']})"
    ch = CH.get((f"var__m_{table}_{r['model']}", r["element"]))
    if ch: t += "[" + "/".join(ch) + "]"
    return f"{r['element']}{'*' if r['mandatory'] == 'true' else ''}:{t}"
def lines(defs, ins, outs, tin, tout, run, extra=lambda d: ""):
    out = []
    for d in defs:
        i = ", ".join(io(r, tin) for r in ins.get(d["sys_id"], [])) or "-"
        o = ", ".join(io(r, tout) for r in outs.get(d["sys_id"], [])) or "-"
        out.append(f"{'T' if run(d) else '-'} {d['sys_id']} | {d['name'].strip()}{extra(d)} | in: {i} | out: {o}")
    return out
ai, ao = group(c["action_inputs"]), group(c["action_outputs"])
acts = [a for a in c["actions"] if a["state"] == "published" and a["active"] == "true" and not a["name"].startswith("TT")]
byscope = collections.defaultdict(list)
for a in acts: byscope[(a["sys_scope.name"], a["sys_scope.scope"])].append(a)
arun = lambda a: (a["sys_scope.scope"], a["name"]) in RUN["actions"]
acc = lambda a: "" if a["access"] == "public" else f" [{a['access']}]"
S = {}
S["triggers"] = lines(c["triggers"], group(c["trigger_inputs"]), group(c["trigger_outputs"]), "sys_hub_trigger_input", "sys_hub_trigger_output",
                      lambda d: d["name"] in RUN["triggers"], lambda d: f" | type {d['type']}" + ("" if d.get("active", "true") == "true" else " [inactive]"))
li = group(c["logic_inputs"]); le = group(c["logic_ext_inputs"])
for k, v in le.items(): li[k] = li.get(k, []) + v
S["logic"] = [x.rsplit(" | out: ", 1)[0] for x in lines(c["logic"], li, {}, "sys_hub_flow_logic_input", "", lambda d: d["name"] in RUN["logic"], lambda d: f" | type {d['type']}")]
S["steps"] = lines(c["steps"], group(c["step_inputs"]), group(c["step_outputs"]), "sys_flow_step_definition_input", "sys_flow_step_definition_output",
                   lambda d: d["name"] in RUN["steps"], lambda d: "" if d["sys_scope.scope"] == "global" else f" [{d['sys_scope.scope']}]")
S["actions_global"] = lines(byscope[("Global", "global")], ai, ao, "sys_hub_action_input", "sys_hub_action_output", arun, acc)
other = []
for (n, s), v in sorted(byscope.items(), key=lambda kv: kv[0][0].lower()):
    if s == "global": continue
    other.append(f"# {n} ({s}), {len(v)}"); other += lines(v, ai, ao, "sys_hub_action_input", "sys_hub_action_output", arun, acc)
S["actions_other"] = other
COUNTS = {"actions": len(acts), "global": len(byscope[("Global", "global")]), "other": len(acts) - len(byscope[("Global", "global")]), "scopes": len(byscope) - 1,
          "triggers": len(c["triggers"]), "logic": len(c["logic"]), "steps": len(c["steps"]), "arun": sum(1 for a in acts if arun(a))}
if __name__ == "__main__":
    for k, v in S.items(): print(k, len(v), "lines", sum(len(x) + 1 for x in v), "chars")
    print(COUNTS)
    if len(sys.argv) > 1:
        for x in S[sys.argv[1]]: print(x)
