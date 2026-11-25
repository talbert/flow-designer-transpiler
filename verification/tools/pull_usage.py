"""Read-only: every action step in every flow on the test instance (v2 and v1 tables), to see which actions shipped flows really use and with what values.
Writes fixtures/dev435256/action_usage.json."""
import os
import json, subprocess, pathlib, sys
ALIAS = os.environ.get("FDT_SDK_ALIAS", "pdi435256")
def q(t, qs, f, page=500):
    rows, off = [], 0
    while True:
        o = subprocess.run(["now-sdk","query",t,"-a",ALIAS,"-q",qs,"-f",f,"--limit",str(page),"--offset",str(off),"-o","json","--timeout","180000"],capture_output=True,text=True,timeout=900,cwd=os.environ.get("FDT_SDK_DIR", "."))
        l = [x for x in o.stdout.split("\n") if x.startswith("{")]
        if not l: print("ERR", t, o.stdout[-300:], o.stderr[-300:], file=sys.stderr); break
        r = json.loads(l[-1]).get("records", []); rows += r; off += page
        print(t, len(rows), file=sys.stderr)
        if len(r) < page: break
    return rows
def main():
    out = {}
    out["v2"] = q("sys_hub_action_instance_v2", "flow.nameNOT LIKETT^ORDERBYsys_id", "sys_id,flow,flow.name,flow.sys_scope.scope,action_type,action_type_parent,values")
    out["cats"] = q("sys_hub_category", "ORDERBYname", "sys_id,name")
    out["snap"] = q("sys_hub_action_type_snapshot", "ORDERBYsys_id", "sys_id,parent_action,name", 1000)
    if not (out["v2"]): sys.exit("Nothing was read from the instance (check the now-sdk login and FDT_SDK_ALIAS). No file was written.")
    pathlib.Path(__file__).parent.parent.joinpath("fixtures/dev435256/action_usage.json").write_text(json.dumps(out))
    print({k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()
