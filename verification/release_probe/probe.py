"""Release probe for the Flow Designer transpiler prompt. READ-ONLY (SDK query = GET).
Checks that every table and every 32-hex sys_id the prompt names exists on an instance.
Usage: python3 probe.py <prompt.md> <sdk-alias> <out.json>
Run it before and after an instance upgrade, then diff the two JSON files."""
import os
import json, re, subprocess, sys
prompt, alias, out = sys.argv[1:4]
text = open(prompt).read()

def q(table, query, fields, limit=500):
    r = subprocess.run(["now-sdk", "query", table, "-a", alias, "-q", query,
                        "-f", fields, "--limit", str(limit), "-o", "json"],
                       capture_output=True, text=True, timeout=300, cwd=os.environ.get("FDT_SDK_DIR", "."))
    lines = [l for l in r.stdout.splitlines() if l.startswith("{")]
    if not lines: raise SystemExit(f"query failed on {table}: {r.stdout[-400:]} {r.stderr[-400:]}")
    return json.loads(lines[-1]).get("records", [])

tables = sorted({t for t in re.findall(r"\b(?:sys_hub_[a-z0-9_]*[a-z0-9]|sys_flow_[a-z0-9_]*[a-z0-9]|sys_variable_value|sys_trigger_runner_mapping|sys_choice|sys_element_mapping|sys_remote_update_set|sys_update_xml)\b", text)})
found_t = {r["name"]: r for r in q("sys_db_object", "nameIN" + ",".join(tables), "name,super_class")}

ids = sorted(set(re.findall(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])", text)))
where = {}
# sys_metadata covers action types, logic/trigger/step definitions; the var tables cover parameter ids.
for tbl in ["sys_metadata", "sys_hub_action_input", "sys_hub_trigger_input", "sys_hub_flow_logic_input", "sys_hub_action_output"]:
    left = [i for i in ids if i not in where]
    for k in range(0, len(left), 100):
        for r in q(tbl, "sys_idIN" + ",".join(left[k:k+100]), "sys_id,sys_class_name,sys_name"):
            where[r["sys_id"]] = {"table": r.get("sys_class_name") or tbl, "name": r.get("sys_name", "")}

res = {"alias": alias, "prompt": prompt,
       "tables": {t: (t in found_t) for t in tables},
       "sys_ids": {i: where.get(i) for i in ids}}
json.dump(res, open(out, "w"), indent=1)
mt = [t for t, ok in res["tables"].items() if not ok]
mi = [i for i, v in res["sys_ids"].items() if not v]
print(f"{alias}: tables {len(tables)-len(mt)}/{len(tables)} exist; sys_ids {len(ids)-len(mi)}/{len(ids)} resolve")
print("missing tables:", mt)
print("unresolved sys_ids:", mi)
