"""Builds the compact-mode reference (Markdown) from the SDK-generated, runtime-tested files in sdk_probe2/update. Local files only.
Every literal in the output is copied from those files; sys_ids of the test's own records are shortened to placeholders."""
import re, json, gzip, base64, pathlib, collections, xml.etree.ElementTree as ET
V = pathlib.Path(__file__).parent.parent; U = V / "sdk_probe2/update"
dec = lambda v: json.loads(gzip.decompress(base64.b64decode(v)))
files = sorted(U.glob("sys_hub_action_type_definition_*.xml")) + sorted(U.glob("sys_hub_flow_*.xml"))
roots = {f.name: ET.fromstring(f.read_text().encode()) for f in files}
own = {}
for r in roots.values():
    for c in r:
        s = c.findtext("sys_id")
        if s and c.get("action") != "delete_multiple": own[s] = "<" + c.tag.replace("sys_hub_", "").replace("_instance_v2", "").replace("sys_", "") + " id>"
def ph(s):
    s = re.sub(r"\b[0-9a-f]{32}\b", lambda m: own.get(m.group(0), m.group(0)), s)
    return re.sub(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "<ui_id>", s)
names = {}
def nm(table, sid):
    return sid
out = ["## APPENDIX E. Compact Payload Reference `[RUNTIME_TESTED]`", "",
       "Everything in this appendix is copied by script (`verification/tools/compact_reference.py`) from the files ServiceNow's Fluent SDK 4.14.2 generated for the compact-mode test (`verification/sdk_probe2/update/`). Those exact files were imported through an update set, published and run (Appendix C). `<… id>` and `<ui_id>` stand for the test's own generated ids; every other id is a platform id and is literal.", ""]
# ---- per-file operation order
out += ["### E.1 Operation order per payload", ""]
for fn, r in roots.items():
    first = r[0]; kind = first.findtext("type") or ("action" if "action" in fn else "")
    seq = []
    for c in r:
        t = ("DELETE " if c.get("action") == "delete_multiple" else "") + c.tag
        if seq and seq[-1][0] == t: seq[-1][1] += 1
        else: seq.append([t, 1])
    out += [f"**{first.findtext('name')}** ({kind or 'flow'}, {len(fn) and (U / fn).stat().st_size} bytes): " + " → ".join(f"{t}" + (f" ×{n}" if n > 1 else "") for t, n in seq), ""]
# ---- field lists with sample values, one per table
out += ["### E.2 Fields written per table (first record of each kind; empty fields listed by name only)", ""]
seen = set()
for r in roots.values():
    for c in r:
        if c.get("action") == "delete_multiple":
            k = ("DEL", c.tag)
            if k not in seen: seen.add(k); out.append(f"- `DELETE {c.tag}` query form: `{ph(c.get('query'))[:150]}`")
            continue
        key = (c.tag, c.findtext("type") if c.tag == "sys_hub_flow" else "")
        if key in seen: continue
        seen.add(key)
        vals, empty = [], []
        for e in c:
            v = (e.text or "")
            if not v.strip(): empty.append(e.tag); continue
            if e.tag in ("values", "trigger_inputs", "subflow_inputs"): v = "(encoded, see E.3)"
            elif e.tag == "label_cache": v = "(JSON text, see E.4)"
            v = ph(v).replace("\n", "\\n")
            a = "".join(f' {k}="{ph(x)}"' for k, x in e.attrib.items())
            vals.append(f"`{e.tag}`{('[' + a.strip() + ']') if a else ''} = `{v[:110]}`")
        out += ["", f"**`{c.tag}`**" + (f" (type `{key[1]}`)" if key[1] else "") + ": " + "; ".join(vals) + ((". Empty: " + ", ".join(f"`{x}`" for x in empty)) if empty else "") + "."]
out += [""]
# ---- decoded blobs: one example per definition
out += ["### E.3 Decoded blob entries, one example per construct", "", "Each line is the decoded JSON of one record's blob. Encode it as in Section 7.1.", ""]
def defname(c):
    for f in ("logic_definition", "action_type", "trigger_definition", "subflow"):
        e = c.find(f)
        if e is not None and (e.text or "").strip(): return f, e.text, e.get("display_value") or ""
    return "", "", ""
LOGIC = {"af4e1945c3e232002841b63b12d3ae3e": "If", "666e5545c3e232002841b63b12d3ae99": "Else If", "1f781bf3c32232002841b63b12d3aee6": "Else", "098e1dc5c3e232002841b63b12d3ae33": "For Each",
         "4f787d1e0f9b0010ecf0cc52ff767ea0": "Set Flow Variables", "07223332de022010ec58424b73829721": "Try", "35d60003e6022010a5e40cdd1254dd21": "Catch", "5d31e5dedfe50300b61ecae83df26326": "Do the following in Parallel",
         "a1168de173311300b61e66476bf6a7d0": "Parallel Branch", "fdb2541473031300b61e66476bf6a70e": "Wait for a duration of time", "df4e1945c3e232002841b63b12d3ae3e": "Assign Subflow Outputs",
         "798916a0c31322002841b63b12d3ae7c": "Trigger: Created", "f63f0d94c32222002841b63b12d3aeed": "Trigger: Repeat", "89142dc0c32222002841b63b12d3ae8a": "Trigger: Daily", "c43a1011c36813002841b63b12d3ae15": "Trigger: Service Catalog",
         "9d09f99587003300663ca1bb36cb0ba3": "Look Up Record", "43400a1587003300663ca1bb36cb0b4b": "Look Up Records", "2de05916c31332002841b63b12d3aee1": "Create Record", "f9d01dd2c31332002841b63b12d3aea1": "Update Record",
         "330ba3abc31013002841b63b12d3aee8": "Get Catalog Variables", "af51fd0e73141300612c273ffff6a785": "Create Catalog Task"}
done = set()
for r in roots.values():
    for c in r:
        if c.get("action") == "delete_multiple": continue
        for fld in ("values", "trigger_inputs", "subflow_inputs"):
            v = c.findtext(fld)
            if not v: continue
            f, did, disp = defname(c)
            label = LOGIC.get(did) or ("Custom action call" if f == "action_type" else "Subflow call" if f == "subflow" else did)
            if label in done: continue
            done.add(label)
            extra = {k: ph(c.findtext(k) or "") for k in ("order", "parent_ui_id", "connected_to", "flow_variables_assigned", "outputs_assigned", "action_type_parent", "wait_for_completion") if (c.findtext(k) or "").strip()}
            out += [f"**{label}** — `{c.tag}`, `{f}` = `{ph(did)}`" + (f"; row fields: {json.dumps(extra, ensure_ascii=False)}" if extra else ""), "", "```json", ph(json.dumps(dec(v), ensure_ascii=False, separators=(",", ":"))), "```", ""]
# logic rows with no blob content differences: list row-level linkage for the whole main flow
main = next(r for r in roots.values() if r[0].findtext("name") == "TT13 Compact Main")
out += ["### E.4 Row linkage of the tested main flow, and its `label_cache`", "", "| order | table | definition | ui_id | parent_ui_id | connected_to |", "|---|---|---|---|---|---|"]
uim = {}
def short(u):
    if not u: return ""
    uim.setdefault(u, f"u{len(uim) + 1}"); return uim[u]
rows = [c for c in main if c.get("action") != "delete_multiple" and c.findtext("ui_id")]
for c in sorted(rows, key=lambda c: [int(x) for x in re.findall(r"\d+", c.findtext("order") or "0")]):
    f, did, disp = defname(c)
    out.append(f"| `{c.findtext('order')}` | `{c.tag.replace('sys_hub_', '')}` | {LOGIC.get(did) or ('custom action' if f == 'action_type' else 'subflow' if f == 'subflow' else did)} | {short(c.findtext('ui_id'))} | {short(c.findtext('parent_ui_id'))} | {short(c.findtext('connected_to'))} |")
lc = json.loads(main[0].findtext("label_cache"))
out += ["", f"`label_cache` of that flow has {len(lc)} entries. First three:", "", "```json"] + [ph(json.dumps(e, ensure_ascii=False, separators=(",", ":"))) for e in lc[:3]] + ["```", ""]
# ---- custom action: variable values and mappings
act = next(r for r in roots.values() if r.get("table") == "sys_hub_action_type_definition")
out += ["### E.5 The compact custom action", "", "No snapshot, no `sys_hub_action_plan`, `state` `draft`. Rows other than the definition:", ""]
for c in act:
    if c.get("action") == "delete_multiple" or c.tag == "sys_hub_action_type_definition": continue
    ne = {e.tag: ph((e.text or ""))[:140].replace("\n", "\\n") for e in c if (e.text or "").strip() and e.tag not in ("sys_scope", "sys_update_name", "calculation")}
    out.append(f"- `{c.tag}`: " + "; ".join(f"`{k}`=`{v}`" for k, v in ne.items()))
text = "\n".join(out) + "\n"
(V / "compact_reference.md").write_text(text)
print(len(text), "chars;", text.count("\n"), "lines; constructs:", sorted(done))
