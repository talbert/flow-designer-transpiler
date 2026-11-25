"""Builds flow_designer_prompt20261119d.md from flow_designer_prompt20261119c.md (left untouched).
Changes: a "when to use this prompt" section at the top (update sets, script conversion, auditing; and when to use the Fluent SDK instead, now confirmed by
running it); the compact payload finding (test 12); an appendix on reading and auditing existing flows; the JSON Parser status."""
import pathlib
P = pathlib.Path(__file__).parent.parent.parent
src = (P / "archive" / "flow_designer_prompt20261119c.md").read_text(); t = src; n = 0
def rep(old, new):
    global t, n
    assert t.count(old) == 1, f"expected 1 of {old[:70]!r}, found {t.count(old)}"
    t = t.replace(old, new); n += 1
def cut(start, end, new):
    """Replace everything from the line starting with `start` up to (not including) the line starting with `end`."""
    global t, n
    a = t.index("\n" + start) + 1; b = t.index("\n" + end, a) + 1
    t = t[:a] + new + t[b:]; n += 1

# ---- 1. top of the prompt
cut("**Canonical alternative:**", "**Evidence tags:**",
 "## WHEN TO USE THIS PROMPT, AND WHEN TO USE THE FLUENT SDK\n\n"
 "ServiceNow's own tool for writing flows as code is the Fluent SDK (`@servicenow/sdk`; `now-sdk explain flow-api`, `subflow-api`, `custom-action-api`, `trigger-api`). It is the supported path and the long-term one. This prompt exists for the three jobs the SDK does not do. State which job applies at the start of every answer.\n\n"
 "| Job | Use |\n|---|---|\n"
 "| A new flow inside an application that is built and installed with Fluent | **The SDK.** Do not use this prompt |\n"
 "| The deliverable must be an **update set** (the target team moves changes by update set, or there is no Fluent project) | **This prompt** |\n"
 "| **Converting existing server-side scripts** (business rules, scheduled jobs, script actions) into flows | **This prompt** (Section 12) |\n"
 "| A custom action that needs a **REST step** | **This prompt** (Section 10.0.3); the SDK has no REST step |\n"
 "| **Reading or auditing flows that already exist** on an instance: what a flow does, which flows touch a given table, field, group, user, subflow or value | **This prompt's record knowledge** (Appendix D). The SDK cannot do this across an instance |\n\n"
 "**What was checked about the SDK** (4.14.2, flow package `@servicenow/fluent-flow` 1.1.9-alpha.1, on Brazil Patch 1, 2026-11-19):\n\n"
 "- `[RUNTIME_TESTED]` A flow written in Fluent (record trigger, Look Up Record, If, Else, two Update Record steps with pills) was built with `now-sdk build`, installed with `now-sdk install`, activated by the SDK itself (\"Flow activation complete: 1/1 succeeded\"), and ran correctly on both branches.\n"
 "- `[DOCUMENTED]` and `[SDK_SOURCE]` (its docs and its source; not each one run here): it covers flows, subflows, custom actions, record, schedule, catalog and inbound-email triggers, the logic types (If, Else If, Else, For Each, Do Until, Parallel, Try/Catch, Wait, Set Flow Variables, Exit Loop, Skip Iteration, End Flow) and 33 built-in actions. Custom action steps: Script, Create/Update/Delete Record, Look Up Record(s), Log, Send Email, Send Notification, Fire Event, Ask For Approval, Create Task, Wait For Condition and a few more. **No REST step and no JSON Parser step.**\n"
 "- Its flow package is still labelled alpha.\n"
 "- `[OBSERVED]` `now-sdk query` is a plain table read: it returns `values`, `trigger_inputs` and `subflow_inputs` as the raw base64 text and does not decode them. `now-sdk transform` can turn a flow back into Fluent code, but only for a flow in the project's own application; pointed at a global flow from another project it reported success and wrote nothing.\n"
 "- `[SDK_SOURCE]` Where the SDK and this prompt overlap they agree, rule by rule (Section 0.1).\n\n"
 "**If the user asks for a new flow and has a Fluent project, say so and recommend the SDK before generating anything.**\n\n")

# ---- 2. Section 0.1: confirmed by running it; correct the one difference
rep("These rules are confirmed twice: by ServiceNow's code and by the import and runtime tests here.",
    "These rules are confirmed three ways: by ServiceNow's code, by building and running a flow with the SDK itself (`verification/sdk_probe/`), and by the import and runtime tests here.")
rep("**Where the SDK differs, and why this prompt does not follow it:** it writes flows and actions as `draft` with short blob entries and no snapshot unless told to, then calls the activation endpoint (Section 13.1), which publishes them. This prompt writes the published shape with full entries because that is what was import-tested through an update set.",
    "**Where the SDK differs:** it writes flows and actions as `draft` with short blob entries and no snapshot, then calls the activation endpoint (Section 13.1). The platform then completes the work itself: after that call the stored entries had full parameter objects, `action_type_parent` and `compiled_snapshot` were set, and a snapshot existed. The SDK's own output also leaves `connected_to` empty on Else and sets `action_type_parent` equal to `action_type`; the platform accepted both. This prompt's default is still the full published shape, because it works with or without the endpoint. Section 0.3 describes the SDK's shape as a second, compact mode.")

# ---- 3. Section 0.3 compact mode, before "The platform normalizes"
rep("**The platform normalizes on activation.**",
 "### 0.3 Compact mode: the SDK's payload shape through an update set `[RUNTIME_TESTED]`\n\n"
 "The exact payload the SDK built for one flow, with every id replaced (inside the blobs too), was wrapped in an update set, imported, published with the activation call and run. Both branches gave the right result. The payload was about 10 KB and 13 operations, where the full shape of the same flow is several times larger.\n\n"
 "**What the compact payload contains:**\n\n"
 "- `sys_hub_flow` with `status` `draft`, `active` `false`, `version` `2`, `generation_source` `fluent`, empty `master_snapshot` and `latest_snapshot`, and a generated `label_cache`. **No snapshot section at all.**\n"
 "- `DELETE sys_hub_trigger_instance_v2 flow=…^sys_idNOT IN…`, then the trigger instance; `DELETE sys_hub_action_instance_v2 …`, then each action instance followed by `DELETE sys_hub_alias_mapping source_id=<that action>`; `DELETE sys_hub_flow_logic_instance_v2 …`, then the logic instances.\n"
 "- Short blob entries. Action `values`: `{\"name\":…,\"value\":…,\"displayValue\":…,\"scriptActive\":false,\"parameter\":{\"type\":\"<internal type>\"}}`. Logic `inputs`: `{\"id\":\"\",\"name\":\"condition\",\"value\":…,\"displayValue\":…,\"children\":[],\"parameter\":{},\"scriptActive\":false}`. Trigger: `{\"triggerInstanceSysId\":\"\",\"label\":…,\"internalType\":…,\"dependent\":\"\",\"choiceList\":[…],\"mandatory\":…,\"order\":100,\"name\":…,\"value\":…,\"displayValue\":…,\"displayField\":\"\",\"scriptActive\":false,\"children\":[],\"parameter\":{\"type\":…,\"name\":…,\"label\":…}}`.\n"
 "- The complete tested file is `verification/sdk_probe/sys_hub_flow_f45eb160f0e144a2b8024cee68db89f1.xml`; follow it field for field.\n\n"
 "**Rules for using it:**\n\n"
 "1. **The activation call is not optional in this mode.** Without it the flow stays a draft with no snapshot and nothing completes the short entries. The same short entries inside a *published* payload with a snapshot produced \"Corrupted flow\" (item 2 above). If the target may lack the endpoint, use the full shape.\n"
 "2. **Use it only when the user asks for a compact payload or confirms the target has the endpoint.** The default stays the full published shape (Sections 2 to 7), which works with the endpoint and with the Workflow Studio buttons.\n"
 "3. **Tested once**, on one flow (record trigger, Look Up Record, If, Else, Update Record, in a scoped application). Subflows, custom actions, schedule and catalog triggers, and the other logic types were tested only in the full shape. Say so in `CONFIGURATION_NOTES` when this mode is used for anything else.\n"
 "4. When replacing ids in a payload that already has blobs, replace them inside the decoded blobs as well and re-encode; an id or text changed only in the XML leaves the blob pointing at the old values.\n\n"
 "**The platform normalizes on activation.**")

# ---- 4. 13.1 nuance
rep("It runs the imported snapshot; it does not rewrite it.",
    "When the flow arrives published with a snapshot, it runs that imported snapshot and does not rewrite it (the returned `masterSnapshotId` was the generated one in all six calls). When the flow arrives as a draft without a snapshot (Section 0.3), it builds the snapshot and completes the blob entries.")

# ---- 5. JSON Parser status
rep("**Not tested: the JSON Parser step.** No action on a baseline instance uses it, so there was no platform-written example to follow, and the SDK does not write it either. Use a Script step with `JSON.parse` instead, or Strategy A.",
    "**Not tested: the JSON Parser step.** No action on a baseline instance uses it, the SDK does not write it, and on an instance without IntegrationHub the Action Designer step picker does not offer it (nor the REST step), so no platform-written example could be made. Its step type has four inputs (`target_schema`, `source_data`, `payload_view`, `sample_payload`) and a complex-object output whose format is unknown here. **Use a Script step with `JSON.parse` instead**, and say so in `CONFIGURATION_NOTES`.")

# ---- 6. Appendix C rows + Appendix D
t = t.rstrip("\n") + "\n" + "\n".join([
 "| A flow written in Fluent, built and installed with the SDK 4.14.2 | Two incidents | `SDK IF branch for INC0010013 found System Administrator`; `SDK ELSE branch for INC0010014` |",
 "| Compact mode: the SDK's payload shape through an update set, then the activation call (Section 0.3) | Two incidents | `TT12 IF branch for INC0010017 found System Administrator`; `TT12 ELSE branch for INC0010018` |",
 "", "---", "",
 "## APPENDIX D. Reading and Auditing Existing Flows", "",
 "Use this when the task is to find out what flows on an instance do, not to build one: \"which flows update this table\", \"where is this group, user, field or value used\", \"what would change if this subflow changed\". Everything here is read-only.", "",
 "### D.1 Where a flow's content lives", "",
 "| What | Table and field | Form |", "|---|---|---|",
 "| Flow and subflow header | `sys_hub_flow` (`name`, `active`, `status`, `type`, `run_as`, `master_snapshot`, `label_cache`) | Plain text |",
 "| Trigger settings (table, condition, schedule) | `sys_hub_trigger_instance_v2.trigger_inputs` | **Encoded** |",
 "| Action step inputs (tables, conditions, field values, recipients, scripts in inline values) | `sys_hub_action_instance_v2.values` | **Encoded** |",
 "| Logic inputs (If and loop conditions, variable assignments, waits) | `sys_hub_flow_logic_instance_v2.values` | **Encoded** |",
 "| Inputs passed to a called subflow | `sys_hub_sub_flow_instance_v2.subflow_inputs` | **Encoded** |",
 "| Which pills a flow uses and where | `sys_hub_flow.label_cache` | Plain JSON text |",
 "| The trigger as the engine runs it (active flows only) | `sys_flow_record_trigger` (`table`, `condition`), `sys_flow_timer_trigger`, `sys_flow_catalog_trigger` | Plain text |",
 "| Custom action step settings and scripts | `sys_variable_value` (`document_key` = the step; `value`) | Plain text |",
 "| Custom action wiring | `sys_element_mapping` (`id` = the action or step; `value` = the pill) | Plain text |",
 "| Runs | `sys_flow_context` (`name`, `state`, `source_record`), `sys_flow_log` | Plain text |", "",
 "### D.2 Decoding", "",
 "An encoded field is base64 of gzip of JSON. In Python: `json.loads(gzip.decompress(base64.b64decode(value)))`. Action `values` and `subflow_inputs` decode to a list of entries; logic `values` decodes to an object whose `inputs`, `variables` and `outputsToAssign` are lists of entries; `trigger_inputs` decodes to a list. In every entry, `name` is the input and `value` is what was configured. A `value` may hold literals, an encoded query, a template (`field=value^field=value`), a JSON string (approval due date, REST name-value pairs) and pills.", "",
 "### D.3 Rules for an audit", "",
 "1. **A text search on the encoded fields finds nothing, and that is not a pass.** `valuesLIKEincident` returns zero rows whatever the flow does. Read the rows, decode every one, and search the decoded text. Report how many rows were decoded.",
 "2. **Search both sections.** Rows whose `flow` is the `sys_hub_flow` sys_id are what Workflow Studio shows; rows whose `flow` is the `master_snapshot` sys_id are what runs (Section 3.9). They can differ. For \"what does the instance do today\", read the snapshot rows of active flows.",
 "3. **`label_cache` is a fast first pass** for field and record usage: it lists each pill by name with the steps that use it. It is not rebuilt by activation and may be empty or stale on imported flows, so treat a miss as \"unknown\", not \"unused\".",
 "4. **Callers of a subflow or custom action** point at its master snapshot, not at its definition (Section 0). To find callers, look up the callee's `master_snapshot` and earlier snapshots (`sys_hub_flow_snapshot.parent_flow`, `sys_hub_action_type_snapshot.parent_action`), then search `sys_hub_sub_flow_instance_v2.subflow` or `sys_hub_action_instance_v2.action_type` for any of them.",
 "5. **Fixed records appear as sys_ids**, not names: a group in an approval rule is `{{static.<sys_id>}}`, a reference in a template is the sys_id or `{\"display\":…,\"value\":<sys_id>}`. Search for the sys_id and the display name both.",
 "6. **Scripts hide in two places:** custom action Script steps (`sys_variable_value`), and inline scripts on a step input (the entry has `scriptActive` true and the code under its `script` key). A value search that skips them is incomplete.",
 "7. **Legacy rows:** flows last saved before the `_v2` tables keep their steps in `sys_hub_action_instance`, `sys_hub_flow_logic` and `sys_hub_trigger_instance`, with action inputs in `sys_variable_value` and `sys_element_mapping` (Section 6). Check both generations and say which you found.",
 "8. **State the limits of the read:** which tables were read, how many rows, whether inactive flows and drafts were included, and anything that returned an access error.", ""]) + "\n"
n += 1
out = P / "archive" / "flow_designer_prompt20261119d.md"; out.write_text(t)
print(f"{n} edits applied; {len(src)} -> {len(t)} chars; wrote {out.name}")
