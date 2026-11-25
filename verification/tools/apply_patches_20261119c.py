"""Builds flow_designer_prompt20261119c.md from flow_designer_prompt20261119b.md (left untouched).
Changes: the snapshot finding stated everywhere it matters; the activation call given its own section; the Fluent SDK confirmation as its own section;
rules that avoid clashes on the target; and the results of tests 7-10 (Parallel, Wait, Try/Catch, schedules, multi-step and REST actions, catalog, scoped app)."""
import pathlib
P = pathlib.Path(__file__).parent.parent.parent
src = (P / "archive" / "flow_designer_prompt20261119b.md").read_text(); t = src; n = 0
def rep(old, new, count=1):
    global t, n
    assert t.count(old) == count, f"expected {count} of {old[:70]!r}, found {t.count(old)}"
    t = t.replace(old, new); n += 1
def rep_line(prefix, new):
    global t, n
    lines = t.split("\n"); hit = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hit) == 1, f"{len(hit)} lines start with {prefix[:60]!r}"
    lines[hit[0]] = new; t = "\n".join(lines); n += 1
def before(marker, new):
    rep(marker, new + marker)

# ================= 1. the snapshot finding, everywhere
rep_line("**Minimum viable snapshot approach:**",
 "**The snapshot is the program that runs.** `[RUNTIME_TESTED]` The XML must include a snapshot, and after activation the platform executes that imported snapshot: in every runtime test `master_snapshot` and `latest_snapshot` were still the generated snapshot's sys_id, whether the flow was activated in Workflow Studio or through the activation call (Section 13.1). Activation does **not** rebuild the snapshot from the flow section. So the snapshot section is not a shell: every step, blob, condition and pill in it must be complete and must say exactly what the flow section says. The flow section is what Workflow Studio shows and edits; the snapshot section is what executes. A mismatch between them means the designer shows one thing and the instance runs another. Set `compiled_snapshot` equal to `action_type`. Generate `label_cache` (Section 7.10), set the snapshot's `description` equal to the flow's, and use the snapshot-section blob shape (Section 7.0). Workflow Studio writes a new snapshot only when someone edits and saves the flow there.")
rep_line("| Scheduled `trigger_inputs` | Partial |", "| Scheduled `trigger_inputs` | Full | Daily, Weekly, Monthly, Repeat and Run Once entries all ran on schedule (Section 7.4.4, Appendix B) |")
rep("After import and republish, export the flow back out as an Update Set XML from the target instance.", "After import and activation, export the flow back out as an Update Set XML from the target instance.")
rep("The platform's capture/validation pass is bypassed, which is why republishing and testing on the target are mandatory.",
    "The platform's capture/validation pass is bypassed, and activation runs the imported snapshot as it is (Section 3.9), which is why reviewing and testing on the target are mandatory.")
rep_line("1. **Never omit the snapshot section.**",
 "1. **Never omit the snapshot section, and never thin it out.** Every flow needs the flow definition and a complete snapshot mirror (Section 3.9). The imported snapshot is what runs after activation; nothing regenerates it unless someone edits the flow in Workflow Studio.")

# ================= 2. Section 0: what ran, SDK confirmation, clash rules
rep("schedule triggers Run Once and Repeat (Weekly and Monthly were activated and their timer records checked, but their run times had not come yet); every action and logic type in the list above;",
    "schedule triggers Daily, Weekly, Monthly, Repeat and Run Once, each at the exact time set; the Service Catalog trigger (fired by ordering an item); every action and logic type in the list above; Do the following in Parallel with two branches; Wait for a duration; Try and Catch (the error branch ran and the flow carried on); Get Catalog Variables and Create Catalog Task; a custom action with three steps (Script, REST, Script); a flow and a custom action inside a scoped application;")
before("**The platform normalizes on activation.**",
 "### 0.1 Confirmed against ServiceNow's own generator `[SDK_SOURCE]`\n\n"
 "The Fluent SDK (`@servicenow/sdk` 4.14.2, flow plugin `@servicenow/fluent-flow` 1.1.9-alpha.1) writes the same records this prompt writes. Its source (readable in the package's `sdk-api/dist/external-plugins/flow.js.map`) was compared with this prompt on 2026-11-19. These rules are confirmed twice: by ServiceNow's code and by the import and runtime tests here.\n\n"
 "| Rule in this prompt | What the SDK source does |\n|---|---|\n"
 "| `sys_hub_flow.version` is `2` | Constant `FLOW_VERSION = '2'` |\n"
 "| Only the `_v2` instance tables | Writes `sys_hub_trigger_instance_v2`, `sys_hub_action_instance_v2`, `sys_hub_flow_logic_instance_v2`, `sys_hub_sub_flow_instance_v2` |\n"
 "| Blobs are base64 of gzip of JSON | `gzipSync(JSON.stringify(…)).toString('base64')` for `values`, `subflow_inputs`, `trigger_inputs` |\n"
 "| Trigger pills are `{{<Trigger name>_1.…}}` | Sets the pill root to the trigger name plus `_1` |\n"
 "| `{{flow_variable.x}}`, `{{subflow.x}}`, `{{action.x}}`, `{{step[<cid>].x}}`, `{{<ui_id>.output}}`, `{{<for each ui_id>.item.field}}` | Same forms; `flow_var.` does not occur |\n"
 "| `label_cache` entries with `usedInstances` | Same entry keys |\n"
 "| Do not emit record, timer or catalog trigger records, or plans | Not written; listed only as related tables |\n"
 "| `ui_id` is a UUID; nesting by `parent_ui_id`; Catch points at Try through `connected_to` | Same |\n"
 "| First step inside a Parallel Branch has a composite `order` such as `2➛3` | Constant `PARALLEL_ORDER_SEPARATOR = '➛'` |\n"
 "| Weekly `day_of_week` `1` = Monday … `7` = Sunday, with the day name as display value | `DAY_OF_WEEK_DISPLAY_MAP` |\n"
 "| Sys_ids in Section 5 | Of the 44 ids Section 5 held before the `[OBSERVED]` rows were added to 5.3, 31 appear in the SDK source: every trigger definition except Recurrence, every `action_type`, every logic definition, and the Script step. The other 13 are ids the SDK does not use (the `action_type_parent` ids, Recurrence, and the REST and JSON Parser step types); those are confirmed on the instance only |\n\n"
 "**One warning from the source.** Next to the trigger-pill code is the comment \"Temp code to match what UI does now, but raised a defect against FD team to fix it in the app itself\". ServiceNow treats the `_1` form as a quirk of today's Workflow Studio. On a later release, check one platform-written flow (Section 14 step 1) before trusting the trigger pill form.\n\n"
 "**Where the SDK differs, and why this prompt does not follow it:** it writes flows and actions as `draft` with short blob entries and no snapshot unless told to, then calls the activation endpoint (Section 13.1), which publishes them. This prompt writes the published shape with full entries because that is what was import-tested through an update set.\n\n"
 "### 0.2 Avoiding clashes on the target `[IMPORT_TESTED]`\n\n"
 "A clash is the one known way a correct payload still imports partly (item 5 above). What was tested:\n\n"
 "| Thing | Result |\n|---|---|\n"
 "| `sys_complex_object.name` already on the target | **Record rejected, rest of the payload skipped.** This is the only clash seen |\n"
 "| A second action with the same `name` and `internal_name` as an existing one, new sys_ids | Imported cleanly; both exist |\n"
 "| A second flow with the same `name` and `internal_name` as an existing one, new sys_ids | Imported cleanly; both exist |\n"
 "| The same sys_id as an existing record | Not a clash: `INSERT_OR_UPDATE` overwrites that record. Right for a deliberate update, wrong for a new flow |\n\n"
 "Rules:\n\n"
 "1. **Generate every sys_id, every `ui_id`, every step `cid` and every `FD…` complex-object name fresh for each generation run,** with a cryptographic random source. Never copy them from an example in this prompt, from an earlier answer or from an export. Reuse a flow's ids only when the user asks for an update to that same flow.\n"
 "2. **`FD` names:** `FD` followed by 32 random hex characters, one per action, the same string in the three places listed in Section 10.0.\n"
 "3. **Names:** duplicates do not fail the import, but they leave two flows or actions nobody can tell apart, and anything that finds a flow by name (`sn_fd.FlowAPI`, a catalog item picker, a reviewer) may pick the wrong one. Give every generated flow, subflow and action a name that starts with a short prefix the user chooses (default: the source record's name), and derive `internal_name` from the name (lower case, non-alphanumerics to `_`).\n"
 "4. **Inside one action,** keep input elements unique, output elements unique and step labels unique. Inside one flow, keep flow variable, input and output elements unique. (Not tested as a failure; these rows are keyed by owner and element, so a repeat would overwrite or collide.)\n"
 "5. **Pre-flight check to give the user** (read-only list filters on the target): `sys_hub_flow` and `sys_hub_action_type_definition` where `name` is one of the generated names; `sys_complex_object` where `name` is one of the generated `FD` names. Any hit on `sys_complex_object` means regenerate that name before importing.\n"
 "6. **The log check after commit stays** (item 5). It is the only thing that catches a clash nobody predicted.\n\n")

# ================= 3. logic: ids and three new subsections
rep("| Assign Subflow Outputs | `df4e1945c3e232002841b63b12d3ae3e` |",
    "| Assign Subflow Outputs | `df4e1945c3e232002841b63b12d3ae3e` |\n"
    "| Try | `07223332de022010ec58424b73829721` |\n| Catch | `35d60003e6022010a5e40cdd1254dd21` |\n"
    "| Exit Loop `[OBSERVED]` | `7444b31c37063110ac85cdd734924bff` |\n| Skip Iteration `[OBSERVED]` | `48de1b5837063110ac85cdd734924b15` |\n"
    "| Go back to `[OBSERVED]` | `59ea75fd77502110b2b4ddd9cf5a99ef` |\n| Make a decision `[OBSERVED]` | `578e90270b2313009002cab937673a7d` |\n"
    "| Append to Flow Variables `[OBSERVED]` | `4784e82683031210d266f953d22bc0fd` |\n| Get Flow Outputs `[OBSERVED]` | `167796d8731f33008dcbedcc5ef6a7ce` |\n"
    "| Call a Workflow `[OBSERVED]` | `e6edace2733203006715b45a4cf6a7b2` |\n| Dynamic Flow `[OBSERVED]` | `5ede711653223300414eddeeff7b1256` |")
before("### 7.6 Subflow Instance `subflow_inputs` — JSON Array Format",
 "#### 7.5.10 Do the following in Parallel `[RUNTIME_TESTED]`\n\n"
 "Three kinds of row. The parallel block (`5d31e5dedfe50300b61ecae83df26326`) and each Parallel Branch (`a1168de173311300b61e66476bf6a7d0`) carry the empty-structure blob. A branch's `parent_ui_id` is the parallel block's `ui_id`; a step inside a branch has the branch's `ui_id` as `parent_ui_id`. `connected_to` is empty on all of them.\n\n"
 "**`order` is special here:** the first step inside each branch gets `<branch order>➛<its own order>` (the character is U+279B). Later steps in the same branch get plain numbers.\n\n"
 "```\n1      Do the following in Parallel\n2      Parallel Branch          parent = parallel\n2➛3    Create Record            parent = branch 1\n4      Parallel Branch          parent = parallel\n4➛5    Create Record            parent = branch 2\n6      (next top-level step)\n```\n\n"
 "Tested: both branches' records were created in the same second, then the flow went on. Workflow Studio shows the steps as \"2➛3\" and \"4➛5\".\n\n"
 "#### 7.5.11 Wait for a duration of time `[RUNTIME_TESTED]`\n\n"
 "Logic definition `fdb2541473031300b61e66476bf6a70e`. Seven `inputs` entries (no `id` at entry level, like the other logic blobs):\n\n"
 "| Name | Parameter id | Type | Order | Value for a fixed wait |\n|---|---|---|---|---|\n"
 "| `duration_type` | `4973581473031300b61e66476bf6a785` | choice | 100 | `explicit_duration` / \"Explicit duration\" |\n"
 "| `percentage_timer_input_datetime` | `bf1d6161b736230034c6ce69ee11a920` | glide_date_time | 100 | empty |\n"
 "| `timer_percentage` | `8033309c5376230034c6ddeeff7b12e1` | integer | 100 | empty |\n"
 "| `timer_duration` | `ef145c1473031300b61e66476bf6a7be` | glide_duration | 200 | `1970-01-01 00:00:08` / \"8 Seconds\" |\n"
 "| `timer_relative_duration_operator` | `dca4105473031300b61e66476bf6a726` | choice | 300 | `after` / \"after\" |\n"
 "| `timer_relative_duration_datetime` | `1f25d05473031300b61e66476bf6a773` | glide_date_time | 400 | empty |\n"
 "| `timer_schedule` | `fb55145473031300b61e66476bf6a762` | reference | 500 | empty, or a `cmn_schedule` sys_id |\n\n"
 "The duration is a date-time counted from 1970-01-01 00:00:00 (one day is `1970-01-02 00:00:00`). `timer_duration` also takes a pill. Other `duration_type` values seen in live flows: `relative_duration` (uses the operator and `timer_relative_duration_datetime`) and `percentage_duration` (uses `percentage_timer_input_datetime` and `timer_percentage`) `[OBSERVED]`. Build each parameter object from the logic definition's input rows (Section 7.0). Tested: rendered as \"Wait for 08 second(s)\" and the run paused for that long.\n\n"
 "#### 7.5.12 Try and Catch `[RUNTIME_TESTED]`\n\n"
 "Try (`07223332de022010ec58424b73829721`) carries the empty-structure blob; the guarded steps have the Try's `ui_id` as `parent_ui_id`. Catch (`35d60003e6022010a5e40cdd1254dd21`) comes right after the Try's last step, has the **same** `parent_ui_id` as the Try, and sets `connected_to` to the Try's `ui_id`; the handler steps have the Catch's `ui_id` as `parent_ui_id`.\n\n"
 "The Catch blob has one `inputs` entry, `__status__`, whose `value` and `displayValue` are the action-status JSON for the shared complex object `FDACTIONSTATUS` (not a per-action `FD…` name, so it never clashes):\n\n"
 "```json\n{\"version\":\"1.0\",\"complexObjectSchema\":{\"FlowDesigner:FDACTIONSTATUS\":{\"code\":\"Integer\",\"code.$field_facets\":{\"SimpleMapFacet\":\"{…}\"},\"message\":\"String\",\"message.$field_facets\":{\"SimpleMapFacet\":\"{…}\"}},\"FlowDesigner:FDACTIONSTATUS.$type_facets\":{\"SimpleMapFacet\":\"{…}\"}},\"complexObject\":{\"code\":{\"$cv\":{\"$c\":\"java.lang.String\",\"$v\":\"\"}},\"message\":{\"$cv\":{\"$c\":\"java.lang.String\",\"$v\":\"\"}}},\"serializationFormat\":\"JSON\"}\n```\n\n"
 "The complete entry, with the facet strings written out, is kept beside this prompt as `verification/fixtures/dev435256/catch_live.json`; copy it whole. Tested: a Look Up Record with \"don't fail on error\" off (`__snc_dont_fail_on_error` value `0`) found nothing, the rest of the Try was skipped, the Catch steps ran, the flow continued after the Catch and finished `COMPLETE`. Workflow Studio shows the Catch as \"and if error occurs after step N\".\n\n")

# ================= 4. catalog actions
before("### 7.4 Trigger Instance `trigger_inputs` `[OBSERVED]` — JSON Array Format",
 "#### 7.3.9 Get Catalog Variables (`330ba3abc31013002841b63b12d3aee8`) `[RUNTIME_TESTED]`\n\n"
 "Three entries: `requested_item` (reference) = `{{Service Catalog_1.request_item}}`; `template_catalog_item` (reference) value = the `sc_cat_item` sys_id, displayValue = its name; `catalog_variables` (slushbucket) = a comma-separated list of `<variable sys_id>:item_option_new` (value and displayValue the same). The action has no fixed outputs: each chosen variable becomes a pill `{{<ui_id>.<variable name>}}`, with a `label_cache` entry such as `{\"name\":\"<ui_id>.tt9_note\",\"label\":\"1 - Get Catalog Variables➛tt9_note\",\"reference\":\"\",\"reference_display\":\"tt9_note\",\"type\":\"string\",\"base_type\":\"string\",\"usedInstances\":{…},\"attributes\":{\"catalogType\":\"6\",\"catalogTypeLabel\":\"Single Line Text\"}}`. The item and variable sys_ids are target data: list them in `CONFIGURATION_NOTES`. **`sys_flow_cat_variable_model` is not needed** (Section 3.15): the test flow had none, before or after activation, and the variable came through.\n\n"
 "#### 7.3.10 Create Catalog Task (`af51fd0e73141300612c273ffff6a785`) `[RUNTIME_TESTED]`\n\n"
 "Seven entries: `ah_table_name` (`sc_task`), `ah_requested_item` (`{{Service Catalog_1.request_item}}`), `ah_short_description` (text and pills), `ah_fields` (template value for other task fields, may be empty), `ah_wait` (value `1`/displayValue `true` to wait for the task to close, `0`/`false` to go on at once), `template_catalog_item` and `catalog_variables` (empty unless variables should show on the task). The output is named **`Catalog Task`**, with the capital letters and the space: `{{<ui_id>.Catalog Task.number}}`.\n\n"
 "**Running a catalog flow:** activation creates `sys_flow_catalog_trigger`, but the flow runs only for a catalog item whose `sc_cat_item.flow_designer_flow` is this flow. That link is target data set on the item, not part of the flow payload; put it in `CONFIGURATION_NOTES`. Tested: one order of a test item ran the flow, which read the variable, created the task with the variable in its short description and wrote the task number back to the requested item.\n\n")

# ================= 5. custom actions with several steps and a REST step
before("### 10.0.1 Older Skeleton (superseded where it differs from 10.0)",
 "### 10.0.3 More Than One Step, and the REST Step `[RUNTIME_TESTED]`\n\n"
 "**Several steps:** one `DELETE sys_hub_step_instance query: action={{ACTION}}^sys_idNOT IN<all step sys_ids>`, then for each step, in order, its `sys_hub_step_instance` (`order` 1, 2, 3…, its own `cid`) followed by that step's whole block from 10.0 (variable values, mappings, the three deletes, ext inputs, ext outputs, input-scripts delete, labels). A later step reads an earlier step's output with `{{step[<earlier cid>].<output element>}}` in its own mapping row. Action outputs may map from any step.\n\n"
 "**REST step** (`step_type` `07a762fb47222200b4fad7527c9a7129`): it has no ext inputs or outputs of its own. Its settings are `sys_variable_value` rows on the step (`document` `sys_hub_step_instance`), one per setting, where `variable` is the sys_id of the step type's input:\n\n"
 "| Setting | `variable` sys_id | `order` | Tested value |\n|---|---|---|---|\n"
 "| `connection` | `91e207d03b50030057a4a2e334efc4a0` | 5 | `define_connection_inline` (the default `use_connection_alias` needs `connection_alias` `262882f03b23320057a4a2e334efc4f0`) |\n"
 "| `application` | `f11ebf865f101300a09a2abd7f466652` | 12 | `35aa573fd7802200bdbaee5b5e610375` |\n"
 "| `capabilities` | `c30a451d2f201300a09a839fb18c95b4` | 13 | `18409d8007482000dada43c0d1021e8f` |\n"
 "| `base_url` | `a67a8ef03b23320057a4a2e334efc472` | 15 | `https://<host>` |\n"
 "| `resource_path` | `3d090af03b23320057a4a2e334efc455` | 20 | `/login.do` |\n"
 "| `query_params` | `4328e2fb47222200b4fad7527c9a7164` | 25 | `{}` |\n"
 "| `http_method` | `e85b7ebf47222200b4fad7527c9a71e3` | | omitted (default `get`; `post` etc. `[OBSERVED]`) |\n"
 "| `headers` | `371837f1c71003007b237f48cb9763b0` | 30 | `{\"type\":\"ADV_NV\",\"value\":[]}` |\n"
 "| `honor_duplicate_query_params` | `58715a1c53f22010d3a8ddeeff7b1248` | 100 | `1` |\n"
 "| `body` `[OBSERVED]` | `6c6073f1c71003007b237f48cb97633b` | | request body text |\n\n"
 "Every setting also gets a `sys_element_mapping` row with `table` `var__m_sys_flow_step_definition_input_07a762fb47222200b4fad7527c9a7129`, `id` = the step, `field` = the setting. Its `value` is **empty when the setting is fixed text, and holds the pill form when the setting contains pills**; a setting that is only a pill may have a mapping row and no variable row. Name-value settings with pills use `{\"type\":\"ADV_NV\",\"value\":[{\"name\":\"probe\",\"value\":\"{{step[<cid>].upper}}\"}]}`. The step's outputs come from the step type: `{{step[<cid>].status_code}}`, `.response_body`, `.response_headers`, `.error_code`, `.error_message`. Many live REST steps also carry an ext output `sn_auth_token` (type `password2`) for a credential; the tested inline connection had none.\n\n"
 "Tested: a Script step made a value, a REST step sent it as a query parameter to the instance's own login page, and a second Script step combined the first step's output with the REST step's `status_code`. The flow wrote `[INC0010011 / HTTP 200] status [200]`.\n\n"
 "**Not tested: the JSON Parser step.** No action on a baseline instance uses it, so there was no platform-written example to follow, and the SDK does not write it either. Use a Script step with `JSON.parse` instead, or Strategy A.\n\n")

# ================= 6. scoped apps
rep("If the user doesn't specify scope, generate for Global. If the user specifies a scoped app, adjust all scope/package references and warn about cross-scope dependencies in the `CONFIGURATION_NOTES`.",
    "If the user doesn't specify scope, generate for Global. If the user specifies a scoped app, adjust all scope/package references and warn about cross-scope dependencies in the `CONFIGURATION_NOTES`.\n\n"
    "`[RUNTIME_TESTED]` A custom action and a flow that calls it were generated this way for a scoped application and ran. What was changed, and nothing else: every `<sys_scope display_value=\"Global\">global</sys_scope>` became `<sys_scope display_value=\"{{APP_NAME}}\">{{APP_SYS_ID}}</sys_scope>`; every `<sys_package display_value=\"Global\" source=\"global\">global</sys_package>` became `<sys_package display_value=\"{{APP_NAME}}\" source=\"{{APP_SCOPE}}\">{{APP_SYS_ID}}</sys_package>`; `sys_complex_object.scope_name` became the scope name (`x_…`); in the outer wrapper every `<application>` became the app's sys_id with its name as `display_value`, and `application_name`, `application_scope` and `application_version` were set. Empty `<sys_scope/>` and `<sys_package/>` elements, `sys_domain` and `update_domain` stayed as they were. `payload_hash` was recomputed after the change. The application must already exist on the target. The action's script reported `gs.getCurrentScopeName()` as the app's scope, and the flow updated a global-table record through the OOB Update Record action. For the activation call use `sysparm_transaction_scope={{APP_SYS_ID}}` (Section 13.1).")

# ================= 7. Section 13.1: activation by API, as its own section
rep("\n   - **Without the click** `[RUNTIME_TESTED]`:", "\n   - **Without the click:** see Section 13.1. `[RUNTIME_TESTED]` In short:")
before("### Caveats:",
 "### 13.1 Activation by API, Without Workflow Studio `[RUNTIME_TESTED]`\n\n"
 "**Do not drop this section when the prompt is edited.** It removes every manual click after the commit.\n\n"
 "```\nPOST /api/now/wfa_fluent/activate_flows?sysparm_transaction_scope=<global | application sys_id>\nContent-Type: application/json\n\n"
 "{\"flows\":   [{\"sys_id\":\"<subflow sys_id>\",\"active\":\"\",\"state\":\"\"},\n            {\"sys_id\":\"<flow sys_id>\",\"active\":\"\",\"state\":\"\"}],\n \"actions\": [{\"sys_id\":\"<action definition sys_id>\",\"active\":\"\",\"state\":\"\"}]}\n```\n\n"
 "- `flows` takes flows and subflows (`sys_hub_flow` sys_ids); `actions` takes `sys_hub_action_type_definition` sys_ids. Either list may be empty.\n"
 "- Answer 200: `{\"result\":{\"status\":\"success\",\"summary\":{\"total\":3,\"succeeded\":3,\"failed\":0},\"results\":[{\"sys_id\":…,\"status\":\"success\",\"message\":\"Published successfully\",\"flow_name\"|\"action_name\":…,\"isPublished\":true,\"masterSnapshotId\":…}]}}`. A 422 still carries this body with the failures listed. Check that each `masterSnapshotId` is the snapshot sys_id that was generated.\n"
 "- What it does: publishes actions and subflows, activates flows, and builds the same trigger, timer and plan records the Activate button builds. It runs the imported snapshot; it does not rewrite it.\n"
 "- Schedule times are read in the calling user's time zone, as with the button.\n"
 "- It is the call ServiceNow's Fluent SDK makes after an install (`[SDK_SOURCE]`, `post-install.ts`). It is **not documented**. An instance without it answers 400 with \"does not represent any resource\"; then use steps 5 and 6. The SDK's own hint for that case is to install the latest ServiceNow IDE on the instance.\n"
 "- Tested on Brazil Patch 1 in six calls, all `succeeded` = `total`: one scheduled flow; an action, a subflow and a flow together; four flows together; an action and a flow with a REST step; a catalog flow; and a scoped action and flow with the application's sys_id as the scope. Every flow activated this way then ran.\n"
 "- Send it from a session that is signed in as an admin: a REST client with basic or OAuth credentials, or the browser with the session token header `X-UserToken`. Give the user the ready-to-send body with the generated sys_ids in the post-import instructions.\n\n")
rep("8. **Provide post-import instructions** — per Section 13.", "8. **Provide post-import instructions** — per Section 13, including the ready-to-send activation call from Section 13.1 with this output's sys_ids filled in, and the pre-flight clash check from Section 0.2.")

# ================= 8. rules
rep("21. **State the time zone** assumed for any schedule time (Section 7.4.4).",
    "21. **State the time zone** assumed for any schedule time (Section 7.4.4).\n"
    "22. **Fresh identifiers every run:** new sys_ids, `ui_id`s, step `cid`s and `FD…` names for each generation, a name prefix on every flow, subflow and action, and the pre-flight clash check in the instructions (Section 0.2).\n"
    "23. **Always give the activation call** (Section 13.1) beside the manual Publish and Activate steps.")

# ================= 9. schedules: runtime results
rep("- **Times are in the time zone of the user who activates the flow.**",
    "- `[RUNTIME_TESTED]` Daily, Weekly and Monthly flows set to the same minute all ran at exactly that minute. The day is read in the activating user's time zone too: flows set for Thursday the 19th at 17:45 Pacific ran then, although that moment is Friday the 20th in UTC (the timer record stores the time as `1970-01-02 01:45:00`).\n"
    "- **Times are in the time zone of the user who activates the flow.**")
rep("**Weekly** (`cf352104c32222002841b63b12d3ae1f`) `[IMPORT_TESTED]`. Two entries;", "**Weekly** (`cf352104c32222002841b63b12d3ae1f`) `[RUNTIME_TESTED]`. Two entries;")
rep("**Monthly** (`2ca52504c32222002841b63b12d3ae4a`) `[IMPORT_TESTED]`", "**Monthly** (`2ca52504c32222002841b63b12d3ae4a`) `[RUNTIME_TESTED]`")
rep("**Daily** (`89142dc0c32222002841b63b12d3ae8a`) `[IMPORT_TESTED]`", "**Daily** (`89142dc0c32222002841b63b12d3ae8a`) `[RUNTIME_TESTED]`")

# ================= 10. Appendix C rows
t = t.rstrip("\n") + "\n" + "\n".join([
 "| Daily, Weekly and Monthly triggers | Schedules set for the same minute | Three executions at exactly that minute, each `COMPLETE` |",
 "| Do the following in Parallel, Wait for a duration, Try and Catch | One incident | Two branch records created in the same second; run paused about 8 seconds; failed lookup caught, description `CATCH branch ran for INC0010010`, last step reached |",
 "| Custom action with Script, REST and Script steps | One incident | Description `TT8 summary [INC0010011 / HTTP 200] status [200]` |",
 "| Service Catalog trigger, Get Catalog Variables, Create Catalog Task | One order of a test catalog item | Requested item description `TT9 catalog flow ran, note [hello from TT9], task [SCTASK0010001]`; the task's short description carried the variable |",
 "| Scoped application: custom action and flow | One incident | Description `TT10 scoped flow: [INC0010012 in x_906694_tt10]` |",
 "| Same names as existing flow and action, new sys_ids | Import only | Clean commit log; both copies exist (Section 0.2) |", ""]) + "\n"
n += 1
out = P / "archive" / "flow_designer_prompt20261119c.md"; out.write_text(t)
print(f"{n} edits applied; {len(src)} -> {len(t)} chars; wrote {out.name}")
