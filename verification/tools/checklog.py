"""Read-only: commit log problems and landed-record counts for a test set. Usage: python3 checklog.py <test dir>"""
import sys, json, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from sn import q
D = pathlib.Path(sys.argv[1]); man = json.load(open(D / "manifest.json"))
logs = q("sys_update_set_log", f"update_set.name={man['update_set']}", "status,log,sys_created_on", 400)
bad = [l for l in logs if l["status"].lower() not in ("info", "") or "unsuccessful" in l["log"] or "skip" in l["log"].lower() or "rror" in l["log"]]
print(f"log lines: {len(logs)} | problem lines: {len(bad)}")
for l in bad[:15]: print("  !", l["status"], l["log"][:260])
for fl in man.get("flows", []):
    F = fl["id"]; r = q("sys_hub_flow", "sys_id=" + F, "name,active,status,type,latest_snapshot,master_snapshot", 1)
    n = lambda t, f="flow": len(q(t, f"{f}={F}", "sys_id", 100))
    print(" ", fl["name"], "|", (r[0]["active"], r[0]["status"]) if r else "MISSING", "| trigger", n("sys_hub_trigger_instance_v2"), "actions", n("sys_hub_action_instance_v2"),
          "logic", n("sys_hub_flow_logic_instance_v2"), "subflow calls", n("sys_hub_sub_flow_instance_v2"), "| sent steps", len(fl["steps"]))
a = man.get("action")
if a:
    for t, f, i in (("sys_hub_action_type_definition", "sys_id", a["id"]), ("sys_hub_action_type_snapshot", "sys_id", a["snap"]), ("sys_hub_step_instance", "action", a["id"]),
                    ("sys_hub_step_instance", "action", a["snap"]), ("sys_hub_action_input", "model", a["id"]), ("sys_hub_action_input", "model", a["snap"]),
                    ("sys_hub_action_output", "model", a["id"]), ("sys_hub_action_output", "model", a["snap"]), ("sys_complex_object", "name", a["fd"]),
                    ("sys_hub_action_plan", "action_id", a["id"])):
        print("  action", t, f, len(q(t, f"{f}={i}", "sys_id", 50)))
