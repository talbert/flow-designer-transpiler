"""Reference generator for the Flow Designer transpiler prompt (update-set XML for flows).
Follows the payload order of a platform-written flow unload (Brazil Patch 1). Writes local files only."""
import json, gzip, base64, uuid, secrets, datetime, time
from xml.sax.saxutils import escape as esc

def gid(): return secrets.token_hex(16)
def uid(): return str(uuid.uuid4())
def blob(obj):
    return base64.b64encode(gzip.compress(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8"), mtime=0)).decode("ascii")
def unblob(s): return json.loads(gzip.decompress(base64.b64decode(s)))

NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
TS = NOW.strftime("%Y-%m-%d %H:%M:%S")
WHO = "admin"

def el(tag, val=None, **attrs):
    a = "".join(f' {k}="{esc(str(v))}"' for k, v in attrs.items())
    if val is None or val == "": return f"<{tag}{a}/>"
    return f"<{tag}{a}>{esc(str(val))}</{tag}>"
def rec(tag, fields, action="INSERT_OR_UPDATE"): return f'<{tag} action="{action}">' + "".join(fields) + f"</{tag}>"
def dm(tag, q): return f'<{tag} action="delete_multiple" query="{esc(q)}"/>'
def audit(sid): return [el("sys_created_by", WHO), el("sys_created_on", TS), el("sys_id", sid), el("sys_mod_count", 0)]
def audit_tail(): return [el("sys_updated_by", WHO), el("sys_updated_on", TS)]

class Step:
    """kind: action | logic | subflow"""
    def __init__(self, kind, order, values=None, parent=None, connected_to=None, **kw):
        self.kind, self.order, self.values, self.parent, self.connected_to = kind, order, values, parent, connected_to
        self.ui = kw.pop("ui", None) or uid()
        self.id, self.sid, self.block = gid(), gid(), gid()   # flow row id, snapshot row id, shared block id
        self.kw = kw   # action: action_type, action_type_parent, label ; logic: logic_def, label, flow_variables_assigned ; subflow: subflow, label

class Flow:
    def __init__(self, name, trigger=None, steps=(), ftype="flow", description="", label_cache=(), run_as="system",
                 inputs=(), outputs=(), variables=()):
        self.name, self.trigger, self.steps, self.type, self.description = name, trigger, list(steps), ftype, description
        self.label_cache, self.run_as = list(label_cache), run_as
        self.inputs, self.outputs, self.variables = list(inputs), list(outputs), list(variables)
        self.id, self.snap = gid(), gid()
        self.internal = "".join(c if c.isalnum() else "_" for c in name.lower())
        if trigger: trigger.setdefault("id", gid()); trigger.setdefault("sid", gid())

    # ---- records
    def _flow_like(self, snapshot):
        sid = self.snap if snapshot else self.id
        tag = "sys_hub_flow_snapshot" if snapshot else "sys_hub_flow"
        lc = json.dumps(self.label_cache, separators=(",", ":"), ensure_ascii=False)
        f = [el("access", "public"), el("acls"), el("active", "true" if snapshot else "false"),
             el("allow_high_security_roles", "false"), el("annotation"), el("attributes"), el("authored_on_release_version"),
             el("callable_by_client_api", "false"), el("category"), el("copied_from"), el("copied_from_name"),
             el("description", self.description)]
        if not snapshot: f += [el("display_name_after_preview")]
        f += [el("flow_priority")]
        if not snapshot: f += [el("generation_source")]
        f += [el("internal_name", self.internal), el("label_cache", lc)]
        if snapshot: f += [el("master", "true")]
        else: f += [el("master_snapshot", self.snap), el("master_snapshot_digest")]
        f += [el("name", self.name), el("natlang"), el("outputs")]
        if snapshot: f += [el("parent_flow", self.id, display_value=self.name)]
        else: f += [el("pre_compiled", "false")]
        f += [el("remote_trigger_id"), el("run_as", self.run_as), el("run_with_roles"), el("sc_callable", "false")]
        if not snapshot: f += [el("show_draft_actions", "false"), el("show_triggered_flows", "false")]
        f += [el("status", "published")]
        if not snapshot: f += [el("substatus")]
        f += [el("sys_class_name", tag), el("sys_created_by", WHO), el("sys_created_on", TS), el("sys_domain", "global"),
              el("sys_domain_path", "/"), el("sys_id", sid), el("sys_mod_count", 0),
              el("sys_name", "" if snapshot else self.name), el("sys_overrides"),
              (el("sys_package") if snapshot else '<sys_package display_value="Global" source="global">global</sys_package>'),
              el("sys_policy"), '<sys_scope display_value="Global">global</sys_scope>',
              el("sys_update_name", "" if snapshot else f"sys_hub_flow_{self.id}"), *audit_tail(), el("type", self.type)]
        if not snapshot: f += [el("updation_source")]
        f += [el("version", 2), el("version_record")]
        return rec(tag, f)

    def _trigger(self, M, snapshot):
        t = self.trigger
        ti = t["inputs"](t["sid" if snapshot else "id"]) if callable(t["inputs"]) else t["inputs"]
        f = [el("comment"), el("display_text"), el("flow", M, display_value=self.name), el("generation_source"),
             el("name", t["name"]), el("published_version"), el("remote_sys_id"), *audit(t["sid" if snapshot else "id"]),
             el("sys_scope"), *audit_tail(), el("trigger_definition", t["definition"], display_value=t["name"]),
             el("trigger_inputs", blob(ti)), el("trigger_outputs"), el("trigger_type", t["type"]), el("updation_source")]
        return rec("sys_hub_trigger_instance_v2", f)

    def _vals(self, s, snapshot):
        v = s.values(snapshot) if callable(s.values) else s.values
        return el("values", blob(v)) if v is not None else el("values")

    def _action(self, s, M, snapshot):
        k = s.kw
        f = [el("action_type", k["action_type"], display_value=k["label"]),
             el("action_type_parent", k.get("action_type_parent", ""), display_value=k["label"]) if k.get("action_type_parent") else el("action_type_parent"),
             el("attributes"), el("comment"), el("compiled_snapshot", k.get("compiled_snapshot", k["action_type"])), el("display_text"),
             el("flow", M, display_value=self.name), el("generation_source"), el("order", s.order), el("parent_ui_id", s.parent or ""),
             el("sys_class_name", "sys_hub_action_instance_v2"), *audit(s.sid if snapshot else s.id),
             '<sys_scope display_value="Global">global</sys_scope>', *audit_tail(), el("ui_id", s.ui), el("updation_source"),
             self._vals(s, snapshot)]
        return rec("sys_hub_action_instance_v2", f)

    def _logic(self, s, M, snapshot):
        k = s.kw
        f = [el("attributes"), el("block", s.block, display_value=""), el("comment"), el("connected_to", s.connected_to or ""),
             el("decision_table"), el("display_text"), el("flow", M, display_value=self.name),
             el("flow_variables_assigned", k.get("flow_variables_assigned", "")), el("generation_source"),
             el("logic_definition", k["logic_def"], display_value=k["label"]), el("order", s.order),
             el("outputs_assigned", k.get("outputs_assigned", "")), el("parent_ui_id", s.parent or ""),
             el("sys_class_name", "sys_hub_flow_logic_instance_v2"), *audit(s.sid if snapshot else s.id),
             '<sys_scope display_value="Global">global</sys_scope>', *audit_tail(), el("ui_id", s.ui), el("updation_source"),
             self._vals(s, snapshot), el("workflow_reference")]
        return rec("sys_hub_flow_logic_instance_v2", f)

    def _subflow(self, s, M, snapshot):
        k = s.kw
        v = s.values(snapshot) if callable(s.values) else s.values
        f = [el("attributes"), el("comment"), el("display_text"), el("flow", M, display_value=self.name), el("generation_source"),
             el("order", s.order), el("parent_ui_id", s.parent or ""), el("show_stages", "false"),
             el("subflow", k["subflow"], display_value=k["label"]), el("subflow_inputs", blob(v)),
             el("sys_class_name", "sys_hub_sub_flow_instance_v2"), *audit(s.sid if snapshot else s.id),
             '<sys_scope display_value="Global">global</sys_scope>', *audit_tail(), el("ui_id", s.ui), el("updation_source"),
             el("wait_for_completion", "true")]
        return rec("sys_hub_sub_flow_instance_v2", f)

    def _var(self, v, M, snapshot, table):
        """v: dict(element,label,type,order,mandatory,max_length,id,sid,uiu,reference). table: sys_hub_flow_input|output|variable"""
        mt = "sys_hub_flow_snapshot" if snapshot else "sys_hub_flow"
        attrs = f"element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,uiType={v['type']},uiTypeLabel={v.get('type_label', v['type'].title())},uiUniqueId={v['uiu']}"
        f = [el("active", "true"), el("array", "false"), el("array_denormalized", "false"), el("attributes", attrs), el("audit", "false"),
             el("calculation", "(function calculatedFieldValue(current) {\n\n\t// Add your code here\n\treturn '';  // return the calculated value\n\n})(current);"),
             el("choice"), el("choice_field"), el("choice_table"), el("column_label", v["label"]), el("comments"), el("create_roles"),
             el("default_value"), el("defaultsort"), el("delete_roles"), el("dependent"), el("dependent_on_field"), el("display", "false"),
             el("dynamic_creation", "false"), el("dynamic_creation_script"), el("dynamic_default_value"), el("dynamic_ref_qual"),
             el("element", v["element"]), el("element_reference", "false"), el("foreign_database"), el("formula"),
             el("function_definition"), el("function_field", "false"), el("help"), el("hint"), el("internal_type", v["type"], display_value=v.get("type_label", v["type"].title())),
             el("label", v["label"]), el("mandatory", "true" if v.get("mandatory") else "false"), el("max_length", v.get("max_length", 8000)),
             el("model", M, display_value=self.name), el("model_id", M, display_value=self.name), el("model_table", mt),
             el("name", f"var__m_{table}_{M}"), el("next_element"), el("order", v["order"]), el("primary", "false"), el("read_only", "false"),
             el("read_only_option"), el("read_roles"), el("reference", v.get("reference", "")), el("reference_cascade_rule"), el("reference_floats", "false"),
             el("reference_key"), el("reference_qual"), el("reference_qual_condition"), el("reference_type"), el("sizeclass"),
             el("spell_check", "false"), el("staged", "false"), el("sys_class_name", table), *audit(v["sid"] if snapshot else v["id"]),
             el("sys_name"), el("sys_package"), el("sys_policy"), '<sys_scope display_value="Global">global</sys_scope>', el("sys_update_name"),
             *audit_tail(), el("table_reference", "false"), el("text_index", "false"), el("unique", "false"), el("use_dependent_field", "false"),
             el("use_dynamic_default", "false"), el("use_reference_qualifier", "simple"), el("virtual", "false"), el("virtual_type", "script"),
             el("widget"), el("write_roles"), el("xml_view", "false")]
        return rec(table, f)

    def _doc(self, v, M, table):
        return rec("sys_documentation", [el("element", v["element"]), el("help"), el("hint"), el("label", v["label"]), el("language", "en"),
            el("name", f"var__m_{table}_{M}"), el("plural"), el("sys_class_name", "sys_documentation"), *audit(gid()), el("sys_name"),
            '<sys_package display_value="Global" source="global">global</sys_package>', el("sys_policy"),
            '<sys_scope display_value="Global">global</sys_scope>', el("sys_update_name"), *audit_tail(), el("url"), el("url_target")])

    def _section(self, M, snapshot):
        k = "sid" if snapshot else "id"
        acts = [s for s in self.steps if s.kind == "action"]; logs = [s for s in self.steps if s.kind == "logic"]
        subs = [s for s in self.steps if s.kind == "subflow"]
        ids = lambda xs: ",".join((s.sid if snapshot else s.id) for s in xs)
        notin = lambda base, xs: base + (f"^sys_idNOT IN{ids(xs)}" if xs else "")
        vnotin = lambda base, xs: base + (f"^sys_idNOT IN{','.join(v[k] for v in xs)}" if xs else "")
        p = [dm("sys_hub_flow_stage", f"flow={M}"), dm("sys_flow_cat_variable_model", f"id={M}"),
             dm("sys_hub_flow_input", vnotin(f"model={M}", self.inputs))]
        for v in self.inputs:
            p += [self._var(v, M, snapshot, "sys_hub_flow_input"), dm("sys_hub_action_input_action_instance", f"action_input={v[k]}")]
        p += [dm("sys_hub_flow_output", vnotin(f"model={M}", self.outputs))]
        for v in self.outputs: p += [self._var(v, M, snapshot, "sys_hub_flow_output")]
        p += [dm("sys_hub_alias_mapping", f"source_id={M}")]
        if self.trigger:
            p += [dm("sys_hub_trigger_instance_v2", f"flow={M}^sys_idNOT IN{self.trigger[k]}"), self._trigger(M, snapshot)]
        else: p += [dm("sys_hub_trigger_instance_v2", f"flow={M}")]
        p += [dm("sys_hub_action_instance_v2", notin(f"flow={M}", acts))]
        for s in acts: p += [self._action(s, M, snapshot), dm("sys_hub_alias_mapping", f"source_id={s.sid if snapshot else s.id}")]
        p += [dm("sys_hub_sub_flow_instance_v2", notin(f"flow={M}", subs))]
        for s in subs: p += [self._subflow(s, M, snapshot)]
        p += [dm("sys_hub_flow_logic_instance_v2", notin(f"flow={M}", logs))]
        for s in logs: p += [self._logic(s, M, snapshot)]
        p += [dm("sys_hub_pill_compound", f"attached_to={M}"), dm("sys_hub_flow_variable", vnotin(f"model={M}", self.variables))]
        for v in self.variables: p += [self._var(v, M, snapshot, "sys_hub_flow_variable")]
        p += [dm("sys_choice", f"name=var__m_sys_hub_flow_variable_{M}")]
        for v in self.variables: p += [self._doc(v, M, "sys_hub_flow_variable")]
        for v in self.inputs: p += [self._doc(v, M, "sys_hub_flow_input")]
        for v in self.outputs: p += [self._doc(v, M, "sys_hub_flow_output")]
        p += [dm("sys_choice", f"name=var__m_sys_hub_flow_input_{M}"), dm("sys_choice", f"name=var__m_sys_hub_flow_output_{M}")]
        return p

    def payload(self):
        F, S = self.id, self.snap
        parts = ['<?xml version="1.0" encoding="UTF-8"?><record_update sys_domain="global" table="sys_hub_flow">',
                 self._flow_like(False), dm("sys_translated_text", f"documentkey={F}"), dm("sys_variable_value", f"document_key={F}"),
                 dm("sys_trigger_runner_mapping", f"identifier={F}"), *self._section(F, False),
                 self._flow_like(True), dm("sys_translated_text", f"documentkey={S}"), dm("sys_variable_value", f"document_key={S}"),
                 *self._section(S, True),
                 rec("sys_hub_flow", [el("sys_id", F), el("latest_snapshot", S), el("compiler_build"), el("version_record")], "UPDATE"),
                 dm("sys_flow_trigger_plan", f"plan_id={F}"), dm("sys_flow_subflow_plan", f"plan_id={F}"), "</record_update>"]
        p = "".join(parts); assert "]]>" not in p
        return p

def jhash(s):
    h = 0
    for ch in s: h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h - 0x100000000 if h >= 0x80000000 else h

def update_set(name, description, flows, notes=""):
    us_a, us_b = gid(), gid()
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    if notes: out.append(f"<!--\n{notes}\n-->")
    out += [f'<unload unload_date="{TS}">', '<sys_remote_update_set action="INSERT_OR_UPDATE">',
            '<application display_value="Global">global</application>', "<application_name>Global</application_name>",
            "<application_scope>global</application_scope>", "<application_version/>", "<collisions/>", "<commit_date/>", "<deleted/>",
            el("description", description), "<inserted/>", el("name", name), "<origin_sys_id/>", '<parent display_value=""/>',
            "<release_date/>", '<remote_base_update_set display_value=""/>', "<remote_parent_id/>", el("remote_sys_id", us_a),
            "<state>loaded</state>", "<summary/>", "<sys_class_name>sys_remote_update_set</sys_class_name>", el("sys_created_by", WHO),
            el("sys_created_on", TS), el("sys_id", us_b), "<sys_mod_count>0</sys_mod_count>", *audit_tail(),
            '<update_set display_value=""/>', '<update_source display_value=""/>', "<updated/>", "</sys_remote_update_set>"]
    for i, fl in enumerate(flows):
        p = fl.payload(); ph = jhash(p); g = gid()
        rec_at = format((int(time.time() * 1000) << 28) | (i + 1), "x")
        out += ['<sys_update_xml action="INSERT_OR_UPDATE">', "<action>INSERT_OR_UPDATE</action>",
                '<application display_value="Global">global</application>', "<category>retrieved</category>", "<comments/>",
                el("name", f"sys_hub_flow_{fl.id}"), f"<payload><![CDATA[{p}]]></payload>", el("payload_hash", ph),
                el("remote_update_set", us_b, display_value=name), "<replace_on_upgrade>false</replace_on_upgrade>",
                el("sys_created_by", WHO), el("sys_created_on", TS), el("sys_id", gid()), "<sys_mod_count>0</sys_mod_count>",
                el("sys_recorded_at", rec_at), *audit_tail(), "<table>sys_hub_flow</table>", el("target_name", fl.name),
                el("type", "Flow"), "<update_domain>global</update_domain>", el("update_guid", g),
                el("update_guid_history", f"{g}:{ph}"), '<update_set display_value=""/>', "<view/>", "</sys_update_xml>"]
    out.append("</unload>")
    return "\n".join(out) + "\n", us_b
