"""Generator for a custom action written from a spec (Section 10.0 of the prompt). Local files only.
Field lists and constant defaults come from the platform export fixture; every content field is set from the spec.
Emits the published shape (definition + snapshot + final UPDATE) WITHOUT sys_hub_action_plan: the plan is compiled data."""
import copy, json, re, time, pathlib, xml.etree.ElementTree as ET
from fdgen import gid, uid, jhash, el, audit_tail, TS, WHO
V = pathlib.Path(__file__).parent.parent
FX = ET.parse(V / "fixtures/dev435256/platform_unload_action_0_current.xml").getroot()
_i = [k for k, c in enumerate(FX) if c.tag == "sys_hub_action_type_snapshot"][0]
SEC = {False: list(FX[:_i]), True: list(FX[_i:])}
SCRIPT_STEP = "106afb6647032200b4fad7527c9a71e7"
VAR_SCRIPT, VAR_MID, MID_ALL = "71aa7f6647032200b4fad7527c9a719b", "f5e56d79b3101300176b051a16a8dce4", "35aa573fd7802200bdbaee5b5e610375"
CALC = "(function calculatedFieldValue(current) {\n\n\t// Add your code here\n\treturn '';  // return the calculated value\n\n})(current);"
TYPES = {"string": ("String", 8000), "integer": ("Integer", 40), "boolean": ("True/False", 40), "reference": ("Reference", 32)}
MAPPER = "element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper"

def tmpl(snap, tag, pred=lambda c: True):
    return next(c for c in SEC[snap] if c.tag == tag and c.get("action") == "INSERT_OR_UPDATE" and pred(c))
def mk(t, over):
    """Copy the template's field list; blank every content field; then apply overrides. over value: str or (str, attrs)."""
    e = ET.Element(t.tag, {"action": "INSERT_OR_UPDATE"})
    keep = {"sys_class_name", "sys_domain", "sys_domain_path", "active", "array", "array_denormalized", "audit", "display", "dynamic_creation",
            "element_reference", "function_field", "primary", "reference_floats", "spell_check", "staged", "table_reference", "text_index", "unique",
            "use_dependent_field", "use_dynamic_default", "use_reference_qualifier", "virtual", "virtual_type", "xml_view", "language", "namespace",
            "scope_name", "type", "error_handling_type", "access", "callable_by_client_api", "ih_action", "pre_compiled", "system_level",
            "authored_on_release_version", "sys_scope", "sys_package", "model_table", "document"}
    seen = set()
    for f in t:
        if f.tag in seen: continue          # the export repeats a few tags; write each once
        seen.add(f.tag)
        n = ET.SubElement(e, f.tag)
        if f.tag in keep: n.text = f.text; n.attrib.update(f.attrib)
        if f.tag in over:
            v = over[f.tag]
            if isinstance(v, tuple): n.text, attrs = v; n.attrib.clear(); n.attrib.update(attrs)
            else: n.text = v; n.attrib.clear() if f.tag not in keep else None
    for k in over:
        assert k in seen, f"{t.tag} has no field {k}"
    for tag, val in (("sys_created_by", WHO), ("sys_created_on", TS), ("sys_updated_by", WHO), ("sys_updated_on", TS), ("sys_mod_count", "0")):
        n = e.find(tag)
        if n is not None: n.text = val
    return e
def dm(tag, q): return ET.Element(tag, {"action": "delete_multiple", "query": q})

class Action:
    def __init__(self, name, description, inputs, step_inputs, script, step_outputs, outputs, step_label="Script step"):
        """inputs/outputs/step_*: lists of dict(element,label,type[,mandatory]). step_inputs add 'value' (pill or literal); outputs add 'value'."""
        self.name, self.description, self.script, self.step_label = name, description, script, step_label
        self.internal = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        self.id, self.snap, self.cid, self.fd = gid(), gid(), uid(), "FD" + gid()
        self.cobj_id = gid()
        def ids(xs):
            xs = [dict(x) for x in xs]
            for x in xs: x.update(id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid(), map=gid(), smap=gid())
            return xs
        self.inputs, self.step_inputs, self.step_outputs = ids(inputs), ids(step_inputs), ids(step_outputs)
        sysout = [dict(element="__dont_treat_as_error__", label="Don't Treat as Error", type="boolean", system="dont"),
                  dict(element="__action_status__", label="Action Status", type="string", system="status")]
        self.outputs = ids(outputs) + ids(sysout)
        self.step = {False: gid(), True: gid()}
        self.meta = {False: gid(), True: gid()}
    def pill_step(self, element): return "{{step[%s].%s}}" % (self.cid, element)
    def _status_schema(self):
        t = json.loads(tmpl(False, "sys_complex_object").findtext("serialized_content").replace("FD1fc4cf17a3a01310910e8076a914a6ee", self.fd))
        return t
    def _label_cache(self):
        e = lambda name, label, typ, base: {"name": name, "label": label, "type": typ, "ref": "", "reference_display": "", "base_type": base,
                                           "parent_table_name": "", "column_name": "", "choices": None, "attributes": {}}
        used_in = {m.group(1) for s in self.step_inputs for m in re.finditer(r"\{\{action\.(\w+)\}\}", s.get("value", ""))}
        lc = [e("{{action.%s}}" % i["element"], "action➛" + i["label"], "action", i["type"]) for i in self.inputs if i["element"] in used_in]
        lc += [e(o["value"], "step➛%s➛%s" % (self.step_label, m.group(1)), "step", o["type"]) for o in self.outputs if not o.get("system")
               for m in [re.search(r"\]\.(\w+)\}\}", o["value"])] if m]
        return json.dumps(lc, separators=(",", ":"), ensure_ascii=False)
    def _var(self, snap, tag, v, model, model_name, order):
        tl, size = TYPES[v["type"]]
        k = "sid" if snap else "id"
        attrs = f"{MAPPER},uiType={v['type']},uiTypeLabel={tl},uiUniqueId={v['uiu']}"
        ro = "false"; dv = ""
        if v.get("system") == "dont": attrs, ro, dv = f"action_error_output=true,{MAPPER},uiType=boolean,visible_in_ui=false", "true", "true"
        if v.get("system") == "status": attrs, ro, size = f"action_error_output=true,co_type_name={self.fd},{MAPPER},uiType=object", "true", 65000
        t = tmpl(snap, tag)
        o = {"attributes": attrs, "calculation": CALC, "element": v["element"], "internal_type": (v["type"], {"display_value": tl}), "label": v["label"],
             "mandatory": "true" if v.get("mandatory") else "false", "max_length": str(size), "model": (model, {"display_value": model_name}),
             "model_id": model, "name": f"var__m_{tag}_{model}", "order": str(order), "read_only": ro, "sys_id": v[k]}
        if dv: o["default_value"] = dv
        return mk(t, o)
    def _doc(self, snap, table, model, v):
        return mk(tmpl(snap, "sys_documentation"), {"element": v["element"], "label": v["label"], "name": f"var__m_{table}_{model}", "sys_id": v["sdoc" if snap else "doc"]})
    def _map(self, snap, table, owner, field, value):
        return mk(tmpl(snap, "sys_element_mapping"), {"field": field, "id": owner, "sys_id": gid(), "table": table, "value": value})
    def _vv(self, snap, doc, key, variable, vlabel, value, order):
        return mk(tmpl(snap, "sys_variable_value"), {"document": doc, "document_key": key, "order": str(order), "sys_id": gid(), "value": value,
                                                     "variable": (variable, {"display_value": vlabel})})
    def section(self, snap):
        M = self.snap if snap else self.id; k = "sid" if snap else "id"; ST = self.step[snap]
        mt = "sys_hub_action_type_snapshot" if snap else "sys_hub_action_type_definition"
        user_out = [o for o in self.outputs if not o.get("system")]
        dont = next(o for o in self.outputs if o.get("system") == "dont"); status = next(o for o in self.outputs if o.get("system") == "status")
        status_value = json.dumps({"version": "1.0", "complexObject": {"code": {"$cv": {"$c": "java.lang.String", "$v": ""}}, "message": {"$cv": {"$c": "java.lang.String", "$v": ""}}},
                                   "complexObjectSchema": self._status_schema(), "serializationFormat": "JSON"}, separators=(",", ":"))
        p = [dm("sys_translated_text", f"documentkey={M}"), dm("sys_variable_value", f"document_key={M}"),
             self._vv(snap, mt, M, dont[k], dont["label"], "0", 2), self._vv(snap, mt, M, status[k], status["label"], status_value, 1),
             dm("sys_element_mapping", f"id={M}")]
        for o in user_out + [status, dont]:
            p.append(self._map(snap, f"var__m_sys_hub_action_output_{M}", M, o["element"], o.get("value", "")))
        p += [dm("sys_hub_step_instance", f"action={M}^sys_idNOT IN{ST}"),
              mk(tmpl(snap, "sys_hub_step_instance"), {"action": (M, {"display_value": self.name}), "cid": self.cid, "label": self.step_label, "order": "1",
                                                      "step_type": (SCRIPT_STEP, {"display_value": "Script"}), "sys_id": ST}),
              dm("sys_variable_value", f"document_key={ST}"),
              self._vv(snap, "sys_hub_step_instance", ST, VAR_SCRIPT, "Script", self.script, 600),
              self._vv(snap, "sys_hub_step_instance", ST, VAR_MID, "MID Application", MID_ALL, 400),
              dm("sys_element_mapping", f"id={ST}")]
        maps = [("application", f"var__m_sys_flow_step_definition_input_{SCRIPT_STEP}", ""), ("script", f"var__m_sys_flow_step_definition_input_{SCRIPT_STEP}", "")]
        maps += [(s["element"], f"var__m_sys_hub_step_ext_input_{ST}", s["value"]) for s in self.step_inputs]
        for f, t, v in sorted(maps): p.append(self._map(snap, t, ST, f, v))
        p += [dm("sys_element_mapping", f"table=var__m_sys_hub_step_ext_output_{ST}^id={ST}"),
              dm("sys_element_mapping", f"table=var__m_sys_flow_step_definition_input_{SCRIPT_STEP}^id={ST}"),
              dm("sys_translated_text", f"documentkey={ST}"),
              dm("sys_hub_step_ext_input", f"model={ST}^sys_idNOT IN" + ",".join(s[k] for s in self.step_inputs))]
        for n, s in enumerate(self.step_inputs): p.append(self._var(snap, "sys_hub_step_ext_input", s, ST, self.step_label, n))
        p.append(dm("sys_hub_step_ext_output", f"model={ST}^sys_idNOT IN" + ",".join(s[k] for s in self.step_outputs)))
        for n, s in enumerate(self.step_outputs): p.append(self._var(snap, "sys_hub_step_ext_output", s, ST, self.step_label, n))
        p.append(dm("sys_hub_input_scripts", f"instance={ST}"))
        for s in self.step_outputs: p.append(self._doc(snap, "sys_hub_step_ext_output", ST, s))
        p.append(dm("sys_hub_action_input", f"model={M}^sys_idNOT IN" + ",".join(i[k] for i in self.inputs)))
        for n, i in enumerate(self.inputs):
            p += [self._var(snap, "sys_hub_action_input", i, M, self.name, n), dm("sys_hub_action_input_action_instance", f"action_input={i[k]}")]
        p.append(dm("sys_hub_action_output", f"model={M}^sys_idNOT IN" + ",".join(o[k] for o in self.outputs)))
        for o, order in [(dont, len(user_out) + 1), (status, len(user_out))] + [(o, n) for n, o in enumerate(user_out)]:
            if o is status and not snap:
                p.append(mk(tmpl(False, "sys_complex_object"), {"name": self.fd, "serialized_content": json.dumps(self._status_schema(), separators=(",", ":")),
                                                               "sys_id": self.cobj_id, "sys_scope": ("global", {"display_value": "Global"})}))
            p += [self._var(snap, "sys_hub_action_output", o, M, self.name, order), dm("sys_hub_action_input_action_instance", f"action_input={o[k]}"),
                  dm("sys_hub_input_scripts", f"instance={o[k]}")]
        p += [dm("sys_hub_pill_compound", f"attached_to={M}"), dm("sys_hub_action_status_metadata", f"action_type_id={M}^sys_idNOT IN{self.meta[snap]}"),
              mk(tmpl(snap, "sys_hub_action_status_metadata"), {"action_type_id": (M, {"display_value": self.name}), "sys_id": self.meta[snap]}),
              dm("sys_hub_status_condition", f"action_status_metadata_id={self.meta[snap]}")]
        for i in self.inputs: p.append(self._doc(snap, "sys_hub_action_input", M, i))
        p.append(dm("sys_choice", f"name=var__m_sys_hub_action_input_{M}"))
        for o in self.outputs: p.append(self._doc(snap, "sys_hub_action_output", M, o))
        p.append(dm("sys_choice", f"name=var__m_sys_hub_action_output_{M}"))
        return p
    def payload(self):
        root = ET.Element("record_update", {"sys_domain": "global", "table": "sys_hub_action_type_definition"})
        common = {"attributes": "{}", "description": self.description, "internal_name": self.internal, "label_cache": self._label_cache(), "name": self.name}
        d = mk(tmpl(False, "sys_hub_action_type_definition"), {**common, "active": "true", "master_snapshot": self.snap, "state": "published", "sys_id": self.id,
               "sys_name": self.name, "sys_update_name": f"sys_hub_action_type_definition_{self.id}"})
        s = mk(tmpl(True, "sys_hub_action_type_snapshot"), {**common, "master": "true", "parent_action": (self.id, {"display_value": self.name}), "sys_id": self.snap,
               "sys_scope": "global"})
        root.extend([d, *self.section(False), dm("sys_hub_action_plan", f"action_id={self.id}"), s, *self.section(True)])
        u = ET.SubElement(root, "sys_hub_action_type_definition", {"action": "UPDATE"})
        ET.SubElement(u, "sys_id").text = self.id; ET.SubElement(u, "latest_snapshot").text = self.snap; ET.SubElement(u, "compiler_build")
        return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root, encoding="unicode")
    # --- what a flow needs to call this action
    def flow_params(self, snapshot_section):
        """Parameter objects for a flow's action-instance blob: derived from the SNAPSHOT's sys_hub_action_input rows."""
        out = []
        for n, i in enumerate(self.inputs):
            tl, size = TYPES[i["type"]]
            p = {"children": [], "type_label": tl, "id": i["sid"], "label": i["label"], "name": i["element"], "type": i["type"], "order": n, "extended": False,
                 "mandatory": bool(i.get("mandatory")), "readOnly": False, "hint": "", "maxsize": size, "reference": "", "reference_display": "", "choiceOption": "",
                 "table": "", "columnName": "", "defaultValue": "", "use_dependent": False, "fShowReferenceFinder": False, "local": False,
                 "attributes": {"uiType": i["type"], "uiTypeLabel": tl, "element_mapping_provider": "com.glide.flow_design.action.data.FlowDesignVariableMapper", "uiUniqueId": i["uiu"]},
                 "ref_qual": "", "dependent_on": "", "help": ""}
            out.append(p)
        return out

def sys_update_xml(us_b, us_name, n, name, table, target, typ, payload):
    g = gid(); ph = jhash(payload)
    return ['<sys_update_xml action="INSERT_OR_UPDATE">', "<action>INSERT_OR_UPDATE</action>", '<application display_value="Global">global</application>',
            "<category>retrieved</category>", "<comments/>", el("name", name), "<payload><![CDATA[" + payload.replace("]]>", "]]]]><![CDATA[>") + "]]></payload>",
            el("payload_hash", ph), el("remote_update_set", us_b, display_value=us_name), "<replace_on_upgrade>false</replace_on_upgrade>", el("sys_created_by", WHO),
            el("sys_created_on", TS), el("sys_id", gid()), "<sys_mod_count>0</sys_mod_count>", el("sys_recorded_at", format((int(time.time() * 1000) << 28) | n, "x")),
            *audit_tail(), el("table", table), el("target_name", target), el("type", typ), "<update_domain>global</update_domain>", el("update_guid", g),
            el("update_guid_history", f"{g}:{ph}"), '<update_set display_value=""/>', "<view/>", "</sys_update_xml>"]
def update_set(name, description, actions=(), flows=()):
    """Actions first, then subflows/flows in the order given."""
    us_a, us_b = gid(), gid()
    out = ['<?xml version="1.0" encoding="UTF-8"?>', f'<unload unload_date="{TS}">', '<sys_remote_update_set action="INSERT_OR_UPDATE">',
           '<application display_value="Global">global</application>', "<application_name>Global</application_name>", "<application_scope>global</application_scope>",
           "<application_version/>", "<collisions/>", "<commit_date/>", "<deleted/>", el("description", description), "<inserted/>", el("name", name), "<origin_sys_id/>",
           '<parent display_value=""/>', "<release_date/>", '<remote_base_update_set display_value=""/>', "<remote_parent_id/>", el("remote_sys_id", us_a),
           "<state>loaded</state>", "<summary/>", "<sys_class_name>sys_remote_update_set</sys_class_name>", el("sys_created_by", WHO), el("sys_created_on", TS),
           el("sys_id", us_b), "<sys_mod_count>0</sys_mod_count>", *audit_tail(), '<update_set display_value=""/>', '<update_source display_value=""/>', "<updated/>",
           "</sys_remote_update_set>"]
    n = 0
    for a in actions:
        n += 1; out += sys_update_xml(us_b, name, n, f"sys_hub_action_type_definition_{a.id}", "sys_hub_action_type_definition", a.name, "Action", a.payload())
    for f in flows:
        n += 1; out += sys_update_xml(us_b, name, n, f"sys_hub_flow_{f.id}", "sys_hub_flow", f.name, "Flow", f.payload())
    out.append("</unload>")
    return "\n".join(out) + "\n", us_b
