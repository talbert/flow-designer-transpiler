"""Custom action with several steps (Script and REST), generalizing actgen.Action. Local files only."""
import re, json, xml.etree.ElementTree as ET
from actgen import *   # mk, tmpl, dm, TYPES, MAPPER, CALC, gid, uid, sys_update_xml, update_set
REST_STEP = "07a762fb47222200b4fad7527c9a7129"
REST_VARS = {  # step-definition input element -> (sys_id, label, order)
    "connection": ("91e207d03b50030057a4a2e334efc4a0", "Connection", 5), "application": ("f11ebf865f101300a09a2abd7f466652", "MID Application", 12),
    "capabilities": ("c30a451d2f201300a09a839fb18c95b4", "Capabilities", 13), "base_url": ("a67a8ef03b23320057a4a2e334efc472", "Base URL", 15),
    "resource_path": ("3d090af03b23320057a4a2e334efc455", "Resource Path", 20), "query_params": ("4328e2fb47222200b4fad7527c9a7164", "Query Parameters", 25),
    "http_method": ("e85b7ebf47222200b4fad7527c9a71e3", "HTTP Method", 27), "headers": ("371837f1c71003007b237f48cb9763b0", "Headers", 30),
    "honor_duplicate_query_params": ("58715a1c53f22010d3a8ddeeff7b1248", "Honor Duplicate Query Params", 100)}
REST_DEFAULTS = {"connection": "define_connection_inline", "application": "35aa573fd7802200bdbaee5b5e610375", "capabilities": "18409d8007482000dada43c0d1021e8f",
                 "query_params": "{}", "headers": '{"type":"ADV_NV","value":[]}', "honor_duplicate_query_params": "1"}
class Action2(Action):
    def __init__(self, name, description, inputs, steps, outputs):
        """steps: list of dict(type='script'|'rest', label, and for script: inputs=[{element,label,type,value}], script, outputs=[{element,label,type}];
        for rest: config={element: static value}, pills={element: value containing pills}). A step's cid is steps[i]['cid'] after construction."""
        super().__init__(name, description, inputs, [], "", [], [])
        self.steps = []
        for s in steps:
            s = dict(s); s.update(cid=uid(), id={False: gid(), True: gid()})
            for k in ("inputs", "outputs"):
                s[k] = [dict(x, id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid()) for x in s.get(k, [])]
            self.steps.append(s)
        self._user_outputs = outputs
    def finish(self):
        """Call after the output pills are known (they need the step cids)."""
        self.outputs[0:0] = [dict(o, id=gid(), sid=gid(), uiu=uid(), doc=gid(), sdoc=gid()) for o in self._user_outputs]
        return self
    def pill(self, i, element): return "{{step[%s].%s}}" % (self.steps[i]["cid"], element)
    def _label_cache(self):
        e = lambda name, label, typ, base: {"name": name, "label": label, "type": typ, "ref": "", "reference_display": "", "base_type": base,
                                           "parent_table_name": "", "column_name": "", "choices": None, "attributes": {}}
        texts = [x.get("value", "") for s in self.steps for x in s["inputs"]] + [v for s in self.steps for v in s.get("pills", {}).values()] + [o.get("value", "") for o in self.outputs]
        blob = " ".join(texts); lc = []
        for i in self.inputs:
            if "{{action.%s}}" % i["element"] in blob: lc.append(e("{{action.%s}}" % i["element"], "action➛" + i["label"], "action", i["type"]))
        for s in self.steps:
            for el_ in sorted(set(re.findall(r"\{\{step\[%s\]\.(\w+)\}\}" % re.escape(s["cid"]), blob))):
                lc.append(e("{{step[%s].%s}}" % (s["cid"], el_), "step➛%s➛%s" % (s["label"], el_), "step", "string"))
        return json.dumps(lc, separators=(",", ":"), ensure_ascii=False)
    def _step_records(self, snap, M, n, s):
        k = "sid" if snap else "id"; ST = s["id"][snap]; rest = s["type"] == "rest"; stype = REST_STEP if rest else SCRIPT_STEP
        p = [mk(tmpl(snap, "sys_hub_step_instance"), {"action": (M, {"display_value": self.name}), "cid": s["cid"], "label": s["label"], "order": str(n + 1),
                                                     "step_type": (stype, {"display_value": "REST" if rest else "Script"}), "sys_id": ST}),
             dm("sys_variable_value", f"document_key={ST}")]
        maps = []
        if rest:
            cfg = {**REST_DEFAULTS, **s.get("config", {})}
            for el_, val in cfg.items():
                vid, vlabel, order = REST_VARS[el_]
                p.append(self._vv(snap, "sys_hub_step_instance", ST, vid, vlabel, val, order))
            for el_ in sorted(set(cfg) | set(s.get("pills", {}))):
                maps.append((el_, f"var__m_sys_flow_step_definition_input_{stype}", s.get("pills", {}).get(el_, "")))
        else:
            p += [self._vv(snap, "sys_hub_step_instance", ST, VAR_SCRIPT, "Script", s["script"], 600), self._vv(snap, "sys_hub_step_instance", ST, VAR_MID, "MID Application", MID_ALL, 400)]
            maps += [("application", f"var__m_sys_flow_step_definition_input_{stype}", ""), ("script", f"var__m_sys_flow_step_definition_input_{stype}", "")]
            maps += [(x["element"], f"var__m_sys_hub_step_ext_input_{ST}", x["value"]) for x in s["inputs"]]
        p.append(dm("sys_element_mapping", f"id={ST}"))
        for f, t, v in sorted(maps): p.append(self._map(snap, t, ST, f, v))
        p += [dm("sys_element_mapping", f"table=var__m_sys_hub_step_ext_output_{ST}^id={ST}"), dm("sys_element_mapping", f"table=var__m_sys_flow_step_definition_input_{stype}^id={ST}"),
              dm("sys_translated_text", f"documentkey={ST}"),
              dm("sys_hub_step_ext_input", f"model={ST}" + ("^sys_idNOT IN" + ",".join(x[k] for x in s["inputs"]) if s["inputs"] else ""))]
        for m, x in enumerate(s["inputs"]): p.append(self._var(snap, "sys_hub_step_ext_input", x, ST, s["label"], m))
        p.append(dm("sys_hub_step_ext_output", f"model={ST}" + ("^sys_idNOT IN" + ",".join(x[k] for x in s["outputs"]) if s["outputs"] else "")))
        for m, x in enumerate(s["outputs"]): p.append(self._var(snap, "sys_hub_step_ext_output", x, ST, s["label"], m))
        p.append(dm("sys_hub_input_scripts", f"instance={ST}"))
        for x in s["outputs"]: p.append(self._doc(snap, "sys_hub_step_ext_output", ST, x))
        return p
    def section(self, snap):
        M = self.snap if snap else self.id; k = "sid" if snap else "id"
        mt = "sys_hub_action_type_snapshot" if snap else "sys_hub_action_type_definition"
        user_out = [o for o in self.outputs if not o.get("system")]
        dont = next(o for o in self.outputs if o.get("system") == "dont"); status = next(o for o in self.outputs if o.get("system") == "status")
        status_value = json.dumps({"version": "1.0", "complexObject": {"code": {"$cv": {"$c": "java.lang.String", "$v": ""}}, "message": {"$cv": {"$c": "java.lang.String", "$v": ""}}},
                                   "complexObjectSchema": self._status_schema(), "serializationFormat": "JSON"}, separators=(",", ":"))
        p = [dm("sys_translated_text", f"documentkey={M}"), dm("sys_variable_value", f"document_key={M}"),
             self._vv(snap, mt, M, dont[k], dont["label"], "0", 2), self._vv(snap, mt, M, status[k], status["label"], status_value, 1), dm("sys_element_mapping", f"id={M}")]
        for o in user_out + [status, dont]: p.append(self._map(snap, f"var__m_sys_hub_action_output_{M}", M, o["element"], o.get("value", "")))
        p.append(dm("sys_hub_step_instance", f"action={M}^sys_idNOT IN" + ",".join(s["id"][snap] for s in self.steps)))
        for n, s in enumerate(self.steps): p += self._step_records(snap, M, n, s)
        p.append(dm("sys_hub_action_input", f"model={M}^sys_idNOT IN" + ",".join(i[k] for i in self.inputs)))
        for n, i in enumerate(self.inputs): p += [self._var(snap, "sys_hub_action_input", i, M, self.name, n), dm("sys_hub_action_input_action_instance", f"action_input={i[k]}")]
        p.append(dm("sys_hub_action_output", f"model={M}^sys_idNOT IN" + ",".join(o[k] for o in self.outputs)))
        for o, order in [(dont, len(user_out) + 1), (status, len(user_out))] + [(o, n) for n, o in enumerate(user_out)]:
            if o is status and not snap:
                p.append(mk(tmpl(False, "sys_complex_object"), {"name": self.fd, "serialized_content": json.dumps(self._status_schema(), separators=(",", ":")),
                                                               "sys_id": self.cobj_id, "sys_scope": ("global", {"display_value": "Global"})}))
            p += [self._var(snap, "sys_hub_action_output", o, M, self.name, order), dm("sys_hub_action_input_action_instance", f"action_input={o[k]}"), dm("sys_hub_input_scripts", f"instance={o[k]}")]
        p += [dm("sys_hub_pill_compound", f"attached_to={M}"), dm("sys_hub_action_status_metadata", f"action_type_id={M}^sys_idNOT IN{self.meta[snap]}"),
              mk(tmpl(snap, "sys_hub_action_status_metadata"), {"action_type_id": (M, {"display_value": self.name}), "sys_id": self.meta[snap]}),
              dm("sys_hub_status_condition", f"action_status_metadata_id={self.meta[snap]}")]
        for i in self.inputs: p.append(self._doc(snap, "sys_hub_action_input", M, i))
        p.append(dm("sys_choice", f"name=var__m_sys_hub_action_input_{M}"))
        for o in self.outputs: p.append(self._doc(snap, "sys_hub_action_output", M, o))
        p.append(dm("sys_choice", f"name=var__m_sys_hub_action_output_{M}"))
        return p
