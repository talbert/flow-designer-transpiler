"""Read-only pull of every Flow Designer definition on the test instance (GET only): triggers, flow logic, actions, step types,
with their inputs and outputs. Writes fixtures/dev435256/full_catalog.json."""
import os
import json, subprocess, pathlib, sys
OUT = pathlib.Path(__file__).parent.parent / "fixtures/dev435256/full_catalog.json"
ALIAS = os.environ.get("FDT_SDK_ALIAS", "pdi435256")
def q(t, qs, f, page=1000, alias=ALIAS):
    rows, off = [], 0
    while True:
        o = subprocess.run(["now-sdk","query",t,"-a",alias,"-q",qs,"-f",f,"--limit",str(page),"--offset",str(off),"-o","json","--timeout","120000"],
                           capture_output=True,text=True,timeout=600,cwd=os.environ.get("FDT_SDK_DIR", "."))
        l = [x for x in o.stdout.split("\n") if x.startswith("{")]
        if not l:
            print("ERR", t, (o.stdout[-300:] + o.stderr[-300:]), file=sys.stderr); break
        r = json.loads(l[-1]).get("records", [])
        rows += r; off += page
        if len(r) < page: break
    print(t, len(rows), file=sys.stderr)
    return rows
def main():
    IO = "sys_id,model,element,label,internal_type,mandatory,order,reference,default_value,choice,max_length,attributes,active"
    cat = {}
    cat["actions"] = q("sys_hub_action_type_definition", "ORDERBYname", "sys_id,name,internal_name,sys_scope,sys_scope.name,sys_scope.scope,state,active,access,category,description,sys_class_name,sys_package.name")
    cat["action_inputs"] = q("sys_hub_action_input", "ORDERBYmodel", IO)
    cat["action_outputs"] = q("sys_hub_action_output", "ORDERBYmodel", IO)
    cat["triggers"] = q("sys_hub_trigger_definition", "ORDERBYname", "sys_id,name,type,sys_scope.name,sys_scope.scope,active,description,sys_class_name")
    cat["trigger_inputs"] = q("sys_hub_trigger_input", "ORDERBYmodel", IO)
    cat["trigger_outputs"] = q("sys_hub_trigger_output", "ORDERBYmodel", IO)
    cat["logic"] = q("sys_hub_flow_logic_definition", "ORDERBYname", "sys_id,name,type,sys_scope.name,sys_scope.scope,active,description,sys_class_name,visible,category")
    cat["logic_inputs"] = q("sys_hub_flow_logic_input", "ORDERBYmodel", IO)
    cat["logic_ext_inputs"] = q("sys_hub_flow_logic_ext_input", "ORDERBYmodel", IO)
    cat["logic_outputs"] = q("sys_hub_flow_logic_output", "ORDERBYmodel", IO)
    cat["steps"] = q("sys_flow_step_definition", "ORDERBYname", "sys_id,name,sys_scope.name,sys_scope.scope,active,description,sys_class_name,category,access")
    cat["step_inputs"] = q("sys_flow_step_definition_input", "ORDERBYmodel", IO)
    cat["step_outputs"] = q("sys_flow_step_definition_output", "ORDERBYmodel", IO)
    if not (cat["actions"] and cat["action_inputs"]): sys.exit("Nothing was read from the instance (check the now-sdk login and FDT_SDK_ALIAS). No file was written.")
    OUT.write_text(json.dumps(cat, indent=1))
    print({k: len(v) for k, v in cat.items()})


if __name__ == "__main__":
    main()
