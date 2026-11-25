"""Test 20b: Create or Update Record with the unique-field marker that live flows carry (`^coalesce_fields=<fields>` at the end of `fields`). Local files only."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compactgen import *
import actgen
CAT = json.load(open(V / "fixtures/dev435256/full_catalog.json"))
def cat_act(name, scope, order, values, parent=None):
    a = [x for x in CAT["actions"] if x["name"] == name and x["sys_scope.scope"] == scope and x["state"] == "published"]
    assert len(a) == 1, (name, len(a)); a = a[0]
    types = {r["element"]: r["internal_type"] for r in CAT["action_inputs"] if r["model"] == a["sys_id"]}
    return Step("action", order, [short(k, v, types[k]) for k, v in values.items()], parent, action_type=a["sys_id"], label=name)
OUT = V / "test_import_20261119v"; T = "Created_1.current"
s1 = cat_act("Create or Update Record", "global", 1, {"table_name": "sys_user", "fields": "user_name=tt20b.user^first_name=TT20B^last_name={{%s.number}}^coalesce_fields=user_name" % T})
s2 = act("Update Record", 2, {"table_name": "incident", "record": "{{%s}}" % T, "values": "description=TT20b upsert [{{%s.status}}] user [{{%s.record.last_name}}]^EQ" % (s1.ui, s1.ui)})
f = Flow("TT20b Create or Update", "Transpiler test 20b. Create or Update Record with coalesce_fields, for incidents whose short description starts with TT20BRUN. Safe to delete.",
         record_trigger("Created", "incident", "short_descriptionSTARTSWITHTT20BRUN"), [s1, s2])
US = "Transpiler Test 20261119v"
xml, usb = actgen.update_set(US, "Transpiler prompt test 20b on dev435256: Create or Update Record with coalesce_fields. Safe to delete.", [], [f])
(OUT / "transpiler_test_20261119v.xml").write_text(xml); ET.parse(OUT / "transpiler_test_20261119v.xml")
(OUT / "manifest.json").write_text(json.dumps({"generated_utc": TS, "update_set": US, "retrieved_set_sys_id": usb, "flows": [{"name": f.name, "id": f.id, "snap": "", "steps": []}]}, indent=1))
print("set", usb, "| flow", f.id)
