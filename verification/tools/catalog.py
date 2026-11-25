"""Builds blob `parameter` objects from the instance's own input definitions (read-only GETs), and caches them."""
import os
import json, subprocess, pathlib
CACHE = pathlib.Path(__file__).parent.parent / "fixtures/dev435256/parameter_catalog.json"
_cat = json.load(open(CACHE)) if CACHE.exists() else {}
INF = "sys_id,element,label,internal_type,internal_type.label,order,mandatory,max_length,reference,reference.label,hint,attributes,choice,choice_table,choice_field,default_value,reference_qual,dependent_on_field,use_dependent_field,read_only,help"
def q(t, qs, f, lim=200, alias=os.environ.get("FDT_SDK_ALIAS", "pdi435256")):
    o = subprocess.run(["now-sdk","query",t,"-a",alias,"-q",qs,"-f",f,"--limit",str(lim),"-o","json"],capture_output=True,text=True,timeout=300,cwd=os.environ.get("FDT_SDK_DIR", "."))
    l = [x for x in o.stdout.splitlines() if x.startswith("{")]
    return json.loads(l[-1]).get("records", []) if l else []
def _b(v): return str(v).lower() == "true"
def _attrs(s):
    d = {}
    for part in (s or "").split(","):
        if "=" in part: k, v = part.split("=", 1); d[k.strip()] = v
    return d
def derive(r, choices):
    p = {"children": [], "type_label": r.get("internal_type.label", ""), "id": r["sys_id"], "label": r["label"], "name": r["element"],
         "type": r["internal_type"], "order": int(r["order"] or 0), "extended": False, "mandatory": _b(r["mandatory"]), "readOnly": _b(r["read_only"]),
         "hint": r["hint"], "maxsize": int(r["max_length"] or 0), "reference": r["reference"], "reference_display": r.get("reference.label", ""),
         "choiceOption": r["choice"], "table": r["choice_table"], "columnName": r["choice_field"], "defaultValue": r["default_value"],
         "use_dependent": _b(r["use_dependent_field"]), "fShowReferenceFinder": False, "local": False, "attributes": _attrs(r["attributes"]),
         "ref_qual": r["reference_qual"], "dependent_on": r["dependent_on_field"], "help": r.get("help", "")}
    if choices:
        p["choices"] = [{"label": c["label"], "value": c["value"], "order": i} for i, c in enumerate(choices)]
        p["defaultChoices"] = [{"label": c["label"], "value": c["value"], "order": i + 1} for i, c in enumerate(choices)]
    return p
def params(model, table="sys_hub_action_input"):
    """Ordered list of compact parameter objects for a definition (action type, trigger definition or logic definition)."""
    key = f"{table}:{model}"
    if key not in _cat:
        rows = sorted(q(table, f"model={model}", INF), key=lambda r: int(r["order"] or 0))
        ch = {}
        for c in q("sys_choice", f"name=var__m_{table}_{model}^inactive=false^language=en^ORDERBYsequence", "element,label,value,sequence", 300):
            ch.setdefault(c["element"], []).append(c)
        _cat[key] = [derive(r, ch.get(r["element"])) for r in rows]
        CACHE.write_text(json.dumps(_cat, indent=1))
    return json.loads(json.dumps(_cat[key]))
FULL_ORDER = ["children","id","label","name","type","typeLabel","order","extended","mandatory","readOnly","hint","maxsize","reference","reference_display",
              "fDataStructure","choices","defaultChoices","choiceOption","table","columnName","defaultValue","use_dependent","fShowReferenceFinder",
              "local","attributes","sysClassName","ref_qual","dependent_on","help"]
def full(p):
    """Snapshot-section shape."""
    p = dict(p)
    if "type_label" in p: p["typeLabel"] = p.pop("type_label")
    for k, dv in {"choices": [], "defaultChoices": [], "fDataStructure": "", "sysClassName": ""}.items(): p.setdefault(k, dv)
    return {k: p[k] for k in FULL_ORDER if k in p} | {k: v for k, v in p.items() if k not in FULL_ORDER}
def entries(model, values, table="sys_hub_action_input"):
    """values: {input name: value or (value, displayValue)}. Returns a callable(snapshot) -> blob entry list covering every input."""
    ps = params(model, table)
    def build(snapshot):
        out = []
        for p in ps:
            v = values.get(p["name"], "")
            val, disp = v if isinstance(v, tuple) else (v, v)
            out.append({"id": p["id"], "name": p["name"], "value": val, "displayValue": disp, "children": [],
                        "parameter": full(p) if snapshot else p, "scriptActive": False})
        return out
    return build
