"""Read-only: show flow runs and the test incidents for a name prefix. Usage: runs.py TT21 [minutes]"""
import sys
sys.path.insert(0, __import__("pathlib").Path(__file__).parent.as_posix())
from sn import q
pre = sys.argv[1]; mins = sys.argv[2] if len(sys.argv) > 2 else "240"
for x in q("sys_flow_context", "nameSTARTSWITH%s^sys_created_onRELATIVEGT@minute@ago@%s^ORDERBYsys_created_on" % (pre, mins), "sys_id,name,state,sys_created_on,source_record,error_message", 60):
    print(x["name"], "|", x["state"], "|", x["sys_created_on"], "|", x["sys_id"], "|", (x.get("error_message") or "")[:300])
for x in q("incident", "short_descriptionSTARTSWITH%s^sys_created_onRELATIVEGT@minute@ago@%s^ORDERBYnumber" % (pre, mins), "number,short_description,state,urgency,description,close_notes,assignment_group.name,assigned_to.name", 60):
    print(x["number"], "|", x["short_description"], "| state", x["state"], "urg", x["urgency"], "|", x["assignment_group.name"], "|", x["assigned_to.name"], "|", x["description"], "|", x["close_notes"])
