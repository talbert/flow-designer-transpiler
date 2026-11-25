"""Build flow_designer_prompt_v2.1.md from the trimmed draft: resolve the two TRIM-REVIEW marks, add the JSON Parser step (test 18)
and the script form of activation (test 17). Local files only. Every replacement must match exactly once."""
import pathlib, re
R = pathlib.Path(__file__).parent.parent.parent
s = (R / "archive" / "flow_designer_prompt_v2.1_draft.md").read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
def rex(pat, new):
    global s
    m = re.findall(pat, s, flags=re.S); assert len(m) == 1, (len(m), pat[:80])
    s = re.sub(pat, lambda _: new, s, flags=re.S)

# 1. version line
rep("**Prompt version 2.1 (draft)** (2026-11-19).", "**Prompt version 2.1** (2026-11-19).")

# 2. when-to-use
rep("| A custom action that needs a **REST step** | **This prompt** (Section 10.0.3); the SDK has no REST step |",
    "| A custom action that needs a **REST step** or a **JSON Parser step** | **This prompt** (Sections 10.0.3 and 10.0.4); the SDK has neither step |")

# 3. compact mode: what was tested, rule 8, rule 11
rep("and with the ordinary Workflow Studio Activate button (one flow). Not tested in compact form:",
    "and with the ordinary Workflow Studio Activate button (one flow), and from a server script (one flow, Section 13.1). **Written from these rules alone, not by the SDK:** a compact custom action with a JSON Parser step and the compact flow that calls it (Section 10.0.4); both published with one API call and ran. Not tested in compact form:")
rep("**No snapshot, no `sys_hub_action_plan`, and no `sys_complex_object`:** the `__action_status__` output uses the shared `co_type_name=FDACTIONSTATUS`, so the name clash in Section 0.2 cannot happen.",
    "**No snapshot, no `sys_hub_action_plan`, and no `sys_complex_object` for the action status:** the `__action_status__` output uses the shared `co_type_name=FDACTIONSTATUS`, so the name clash in Section 0.2 cannot happen. **One exception:** a step whose output is an object (the JSON Parser step, Section 10.0.4) needs its own `sys_complex_object` with a fresh `FD…` name.")
rep("and the manual way (open in Workflow Studio, Edit, Publish for a subflow or action, Activate for a flow).",
    "and the manual way (open in Workflow Studio, Edit, Publish for a subflow or action, Activate for a flow). Where neither fits (a fix script, a deployment script), a flow can be published from a server script with `sn_fd.FlowAPI.publishFlowFromFluent('<flow sys_id>')` (Section 13.1).")

# 4. step type table
rex(r"\| JSON Parser \| `502328c387523300f917e55936cb0bf0` `\[OBSERVED\]` — [^\n]*\|",
    "| JSON Parser | `502328c387523300f917e55936cb0bf0` `[RUNTIME_TESTED]` (Section 10.0.4) — the step type record exists only after plugin `com.glide.hub.action_step.jsonparser` is installed (inactive on a baseline instance); Action Designer listed the step, and the REST step, only after \"ServiceNow IntegrationHub Installer\" was activated (Brazil Patch 1, 2026-11-19) |")

# 5. TRIM-REVIEW 1 (Create Record / Update Record templates)
rex(r"<!-- TRIM-REVIEW: v2\.0 printed full-shape templates here.*?-->",
    "`[OBSERVED]` Entries in flows saved by Workflow Studio show `use_dependent` `true` on Create Record `values`, Update Record `record` and Update Record `values`. The parameter objects in Appendix A, read from the action definitions, have `false` there, and those are the objects that were imported and ran. **Use Appendix A.** In compact mode the question does not arise: the platform writes the parameter object itself.")

# 6. JSON Parser: replace the 'not tested' paragraph and add Section 10.0.4
rex(r"\*\*Not tested: the JSON Parser step\.\*\*[^\n]*\n",
    "For a step that parses JSON, see Section 10.0.4. (Until 2026-11-19 this prompt said to use a Script step with `JSON.parse` instead; that still works and needs no IntegrationHub.)\n")
NEW_1004 = r'''### 10.0.4 The JSON Parser Step `[RUNTIME_TESTED]`

Tested on Brazil Patch 1, 2026-11-19 (test 18, `verification/test_import_20261119q/`). A custom action with one JSON Parser step was generated **in the compact shape from the rules below**, imported, published by one activation call together with the compact flow that calls it, and ran. An incident whose description held `{"ticket":{"id":"T-99","site":{"city":"Boulder","zip":"80301"}},"owner":"Craig","count":42,"urgent":false,"flags":["green"]}` came back as `TT18 owner [Craig] city [Boulder] count [42] for INC0010028`. A second payload with `city` and `count` missing and one extra member gave empty text for the missing outputs and no error. The rules were read from a step built by hand in Action Designer; before the test, the generator's output for that step's sample was compared with what the platform had stored (target schema identical; complex object identical apart from the random `uiUniqueId` values).

**Prerequisite `[OBSERVED]`:** see Section 5.4. The run was made with IntegrationHub installed; running the step on an instance without it is untested. Say so in `CONFIGURATION_NOTES`, and offer the Script-step alternative (`JSON.parse` in a Script step) when the target has no IntegrationHub.

**Rows for the step**, in addition to the action's own rows (Section 10.0, or Appendix E.5 in compact mode):

1. `sys_hub_step_instance`: `step_type` `502328c387523300f917e55936cb0bf0`, `label`, `order`, `cid`, `error_handling_type` `1`, `action` = the action.
2. Two `sys_variable_value` rows with `document` `sys_hub_step_instance` and `document_key` = the step:

| Step input | `variable` | `order` | `value` |
|---|---|---|---|
| `target_schema` | `4674240787523300f917e55936cb0b0e` | `100` | the target schema, as JSON text (below) |
| `sample_payload` | `d335ac0787523300f917e55936cb0b1d` | `300` | the sample payload, as JSON text |

   The step type's other two inputs had no variable row: `source_data` (`aaa4a40787523300f917e55936cb0b69`; it is set through the mapping row below) and `payload_view` (`95d4280787523300f917e55936cb0bfe`, a choice behind the "Structured Payload View" switch, left off).
3. Three `sys_element_mapping` rows with `id` = the step and `table` `var__m_sys_flow_step_definition_input_502328c387523300f917e55936cb0bf0`: `field` `source_data` with `value` = the pill for the text to parse (`{{action.<input>}}` or `{{step[<cid>].<output>}}`); `field` `sample_payload` and `field` `target_schema`, both with an empty `value`.
4. One `sys_hub_step_ext_output`: `element` `root`, `label` `root`, `internal_type` `string`, `max_length` `65000`, `order` `1`, `model` and `model_id` = the step, `model_table` `sys_hub_step_instance`, `name` `var__m_sys_hub_step_ext_output_<step sys_id>`, `attributes` `co_type_name=FD<32 hex>,element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,uiType=object,uiTypeLabel=Object,uiUniqueId=<uuid>`.
5. One `sys_complex_object`: `name` = that `FD…` name, `namespace` `FlowDesigner`, `scope_name` = the action's scope, `type` `complex_object_schema`, `serialized_content` (below). The `FD…` name is not derived from any sys_id; make it from fresh hex every run (Section 0.2).

**Target schema.** One node per JSON member, in the sample's order: `{"name":…,"children":[…],"type":…,"jpath":…,"previewValue":…}`.

| Member in the sample | `type` | `jpath` | `previewValue` | `children` |
|---|---|---|---|---|
| the whole payload | `object` | `$` | `""` | its members; `name` is `root` |
| an object | `object` | `$.owner` | `""` | its members |
| text, number or boolean | `string` | `$.owner.city` | the sample's value as text (`Denver`, `3`, `true`) | `[]` |
| an array of text or numbers | `array.string` | `$.tags[*]` | `""` | one node: `name` `<member>_string`, `type` `string`, `jpath` `$.tags[*]`, `previewValue` the first element |

Action Designer's Generate Target button typed every scalar as String, numbers and booleans included. For the sample `{"name":"Koa","count":3,"tags":["a","b"],"owner":{"id":"x1"}}` the platform stored:

```json
{"name":"root","children":[{"name":"name","children":[],"type":"string","jpath":"$.name","previewValue":"Koa"},{"name":"count","children":[],"type":"string","jpath":"$.count","previewValue":"3"},{"name":"tags","children":[{"name":"tags_string","children":[],"type":"string","jpath":"$.tags[*]","previewValue":"a"}],"type":"array.string","jpath":"$.tags[*]","previewValue":""},{"name":"owner","children":[{"name":"id","children":[],"type":"string","jpath":"$.owner.id","previewValue":"x1"}],"type":"object","jpath":"$.owner","previewValue":""}],"type":"object","jpath":"$","previewValue":""}
```

**Complex object `serialized_content`.** Two top-level keys. Each facet value is JSON written as a string.

```
{"FlowDesigner:<FD name>": {
    "<scalar member>": "String",
    "<scalar member>.$field_facets": {"SimpleMapFacet": "<scalar facet>"},
    "<object member>": { …the same pattern for its members… },
    "<object member>.$field_facets": {"SimpleMapFacet": "<object facet>"},
    "<array member>": ["Any"],
    "<array member>.$field_facets": {"SimpleMapFacet": "<array facet>"}},
 "FlowDesigner:<FD name>.$type_facets": {"SimpleMapFacet": "<type facet>"}}
```

- Scalar facet: `{"uiTypeLabel":"String","help":"","read_only":"false","hint":"","uiType":"string","choiceOption":"","default_value":"","label":"<member>","mandatory":"false","order":"<position among its siblings, from 1>","max_length":"0","uiUniqueId":"<fresh uuid>"}`
- Object facet: the same with `uiTypeLabel` `Object` and `uiType` `object`.
- Array facet: `{"choiceOption":"","default_value":"","child_hint":"","child_maxsize":"","label":"<member>","mandatory":"false","child_name":"<member>_string","uiUniqueId":"<fresh uuid>","uiTypeLabel":"Array.String","help":"","child_label":"<member>_string","child_type_label":"String","read_only":"false","hint":"","uiType":"array.string","child_defaultValue":"","child_type":"string","order":"<position>","max_length":"0","child_uiUniqueId":"<fresh uuid>"}`
- Type facet: `{"sourceId":"","choiceOption":"","default_value":"","label":"root","mandatory":"false","uiUniqueId":"<the same uuid as on the step output's attributes>","uiTypeLabel":"Object","help":"","co_type_name":"<FD name>","element_mapping_provider":"com.glide.flow_design.action.data.FlowDesignVariableMapper","read_only":"false","sourceUiUniqueId":"","sourceType":"","hint":"","uiType":"object","order":"1","max_length":"65000"}`

**Pills.** A parsed member is `{{step[<cid>].root.<member>}}`, nested `{{step[<cid>].root.ticket.site.city}}`. Use it in an action output's mapping row or in a later step's input. The action's `label_cache` entry for it: `{"name":"{{step[<cid>].root.owner.city}}","label":"step➛<step label>➛root➛owner➛city","type":"step","ref":"","reference_display":"","base_type":"string","parent_table_name":"","column_name":"","choices":null,"attributes":{}}`.

**Compact shape (tested):** emit the five kinds of row above with the action as a draft (compact rule 8), then activate. The platform built the snapshot, a second step instance and a second complex object for it.

**Full published shape `[PLATFORM_EXPORT]`** (`verification/fixtures/dev435256/jsonparser/platform_export_tt18_action_published.xml`, the platform's export of the tested action after activation): the snapshot section repeats the step rows with its own step sys_id and the same `cid`, and it has **its own `sys_complex_object` with a different `FD…` name**, which the snapshot's `sys_hub_step_ext_output` names in `co_type_name`. Both step outputs carry the same `uiUniqueId`. So a full-shape action with a JSON Parser step needs two complex objects, one per section, with two fresh names. Generating that shape directly was not tested; prefer compact.

**Not tested:** arrays of objects, members typed as anything but String, the Structured Payload View switch, passing the whole `root` object out as an action output, and the XML Parser and JSON Builder steps (their plugins were inactive on the test instance).

'''
rep("### 10.0.1 Older Skeleton\n", NEW_1004 + "### 10.0.1 Older Skeleton\n")

# 7. TRIM-REVIEW 2 (Section 10.1)
rex(r"<!-- TRIM-REVIEW: Section 10\.1 carries no evidence tag.*?-->",
    "**Status of this section.** The format the platform itself writes (`$field_facets`, `SimpleMapFacet`, `type` `complex_object_schema`) is the tested one: Section 10.0 for the `__action_status__` object `[PLATFORM_EXPORT]` and Section 10.0.4 for a JSON Parser output `[RUNTIME_TESTED]`. **Generate that format.** The simplified format and the record template below are older, carry no evidence tag and were never import-tested; they are kept for reference only.")

# 8. Section 13.1: script form and later calls
rep("Unverified, from the SDK's GitHub discussions: the IDE needs Zurich Patch 8 or later; a scriptable form `sn_fd.FlowAPI.publishFlowFromFluent()` / `publishActionFromFluent()` exists; publishing fails for flows in a non-global domain; a third-party client treats HTTP 207 as partial success.",
    "Unverified, from the SDK's GitHub discussions: the IDE needs Zurich Patch 8 or later; publishing fails for flows in a non-global domain; a third-party client treats HTTP 207 as partial success. The same discussions name a scriptable form, which was then tested (next item).\n- **Script form** `[RUNTIME_TESTED]`: `sn_fd.FlowAPI.publishFlowFromFluent('<flow sys_id>')`, run once from a background script on Brazil Patch 1, published and activated a compact draft flow. It returned a JSON string (`id`, `masterSnapshotId`, `name`, `updatedBy`, `triggerInstances`, …), left the flow `status` `published` and `active` `true` with a new master snapshot, and the flow then ran on both of its branches. `sn_fd.FlowAPI.publishActionFromFluent` exists (`typeof` gives `function`) but was not called. Neither is in the official API documentation. Use the script form where a REST call cannot be made, for example in a fix script that runs after the update set commits.")
rep("Every flow activated this way then ran.", "Every flow activated this way then ran. Later calls on compact drafts (Appendix C), the last one an action with a JSON Parser step and its flow, also returned `succeeded` = `total`.")

# 9. critical rules
rep("24. **Compact mode is the default.**", "25. **A JSON Parser step carries its own complex object** in the platform's facet format, with a fresh `FD…` name, in compact mode too (Section 10.0.4).\n24. **Compact mode is the default.**")
# keep numeric order: move 25 after 24
i24 = s.index("24. **Compact mode is the default.**"); end24 = s.index("\n", i24)
i25 = s.index("25. **A JSON Parser step carries"); end25 = s.index("\n", i25)
line25 = s[i25:end25 + 1]; s = s[:i25] + s[end25 + 1:]
i24 = s.index("24. **Compact mode is the default.**"); end24 = s.index("\n", i24)
s = s[:end24 + 1] + line25 + s[end24 + 1:]

# 10. Appendix C rows
rep("| Compact flow in the global scope, activation call with scope `global` | Two incidents | `TT16 IF branch for INC0010024 found System Administrator`; `TT16 ELSE branch for INC0010025` |\n",
    "| Compact flow in the global scope, activation call with scope `global` | Two incidents | `TT16 IF branch for INC0010024 found System Administrator`; `TT16 ELSE branch for INC0010025` |\n"
    "| Compact draft flow published from a server script, `sn_fd.FlowAPI.publishFlowFromFluent` | Two incidents | `TT17 IF branch for INC0010026 found System Administrator`; `TT17 ELSE branch for INC0010027` |\n"
    "| Custom action with a JSON Parser step and its flow, both compact and written from this prompt's rules (not by the SDK), one activation call | Two incidents with JSON text in the description | `TT18 owner [Craig] city [Boulder] count [42] for INC0010028`; with two members missing: `TT18 owner [Root] city [] count [] for INC0010029` |\n")

# 11. Appendix D: one more audit rule
rep("8. **State the limits of the read:** which tables were read, how many rows, whether inactive flows and drafts were included, and anything that returned an access error.\n",
    "8. **State the limits of the read:** which tables were read, how many rows, whether inactive flows and drafts were included, and anything that returned an access error.\n"
    "9. **The newest export can be older than the live rows.** `[OBSERVED]` A custom action was changed and republished by hand in Action Designer (a JSON Parser step added). The live step rows and the master snapshot changed (the master snapshot kept its sys_id and was rewritten in place), but no new `sys_update_version` or `sys_update_xml` row appeared for the action in the following half hour; the newest export still showed the action without the step. The cause was not found. For \"what does it do today\", read the live rows, not the last export.\n"
    "10. **Parsed JSON has its own shape record.** A JSON Parser step's output members are not columns anywhere: they are in the step's `target_schema` variable value and in a `sys_complex_object` named by `co_type_name` on the step's output (Section 10.0.4). A pill such as `{{step[<cid>].root.owner.city}}` can be traced only through those.\n")

# 12. Appendix E.5 note
rep("No snapshot, no `sys_hub_action_plan`, `state` `draft`. Rows other than the definition:",
    "No snapshot, no `sys_hub_action_plan`, `state` `draft`. A JSON Parser step adds two variable values, three mapping rows, an object output and a `sys_complex_object` (Section 10.0.4). Rows other than the definition, for the tested Script-step action:")

# 13. version history
rex(r"\| 2\.1 \(draft\) \|[^\n]*\|",
    "| **2.1** | 2026-11-19 | `flow_designer_prompt_v2.1.md` | Trimmed: repetition and superseded wording removed, no technical content removed (checked with `verification/tools/knowledge_check.py`). **JSON Parser step** written from a hand-built sample and runtime-tested in compact form (new Section 10.0.4). **Script form of activation** tested (`sn_fd.FlowAPI.publishFlowFromFluent`, Section 13.1). Complex-object format settled on the platform's facet format (Section 10.1). With no release named, the default is now Brazil Patch 1, the tested release. Two audit rules added (Appendix D). |")
assert "TRIM-REVIEW" not in s and "(draft)" not in s.split("## VERSION HISTORY")[0][:400]
(R / "archive" / "flow_designer_prompt_v2.1.md").write_text(s)
print("written", len(s), "chars,", s.count("\n") + 1, "lines")
