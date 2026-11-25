"""Read-only: flow executions and their side effects for the TT4 runtime test."""
import sys, json, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from sn import q
def main():
    ctx = q("sys_flow_context", "nameSTARTSWITHTT4^ORDERBYsys_created_on", "sys_id,name,state,source_table,source_record,sys_created_on,run_time,error_message", 60)
    print("== executions")
    for c in ctx:
        src = q("incident", "sys_id=" + c["source_record"], "number", 1) if c["source_record"] else []
        print(f"  {c['name']:26} {c['state']:12} {src[0]['number'] if src else '-':11} {c['sys_created_on']} {(c.get('error_message') or '')[:200]}")
    print("== incidents")
    for i in q("incident", "short_descriptionSTARTSWITHTT4RUN^ORDERBYnumber", "sys_id,number,short_description,urgency,description,approval,state", 30):
        print(f"  {i['number']} | {i['short_description']} | urgency {i['urgency']} | description: {i['description']!r} | approval: {i['approval']}")
        for j in q("sys_journal_field", f"element_id={i['sys_id']}^element=work_notes", "value,sys_created_by", 5): print("      work note:", repr(j["value"]), "by", j["sys_created_by"])
        for t in q("incident_task", f"incident={i['sys_id']}", "number,short_description", 5): print("      task:", t["number"], t["short_description"])
        for a in q("sysapproval_approver", f"sysapproval={i['sys_id']}^ORdocument_id={i['sys_id']}", "sys_id,approver.user_name,state", 5): print("      approval:", a)
        for e in q("sysevent", f"instance={i['sys_id']}^name=incident.inactivity", "name,parm1,parm2,state", 3): print("      event:", e)
        for m in q("sys_email", f"instance={i['sys_id']}", "subject,recipients,type,state", 5): print("      email:", m)
    print("== flow log (errors)")
    for l in q("sys_flow_log", "context.nameSTARTSWITHTT4^levelIN2,3^ORDERBYDESCsys_created_on", "context.name,level,message,sys_created_on", 15): print("  ", l["context.name"], l["level"], l["message"][:300])


if __name__ == "__main__":
    main()
