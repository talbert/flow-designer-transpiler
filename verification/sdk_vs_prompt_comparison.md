# Fluent SDK flow plugin 4.14.0 source vs. transpiler prompt 20261119d

Written 2026-11-19. Read-only comparison; nothing was run against an instance.

**Compared**

- Prompt: `flow_designer_prompt20261119d.md` (2,989 lines). Cited as "prompt L<line>".
- SDK source: `flow-src-4.14.0/src/` (extracted from the source map). Cited as `<path under src/>:<line>`.
- SDK docs: `/opt/homebrew/lib/node_modules/@servicenow/sdk/docs/` (`api/flow/*.md`, `guides/wfa-*.md`). Cited as `docs/<file>:<line>`.
- Two helper classes live outside the flow plugin, in the installed `@servicenow/sdk-build-core` source (`src/plugins/data-shape.ts`, `src/plugins/time.ts`); cited as `sdk-build-core/<file>:<line>`.
- One cross-check used a file that already existed in the project: the SDK-built payload `verification/sdk_probe/sys_hub_flow_f45eb160f0e144a2b8024cee68db89f1.xml` (decoded locally). Cited as "probe".

**Not repeated here** (already verified before this pass): `version` 2, the `_v2` tables, gzip plus base64 blobs, `{{<Trigger name>_1.…}}` pills, the `flow_variable.` / `subflow.` / `action.` / `step[cid].` pill forms, `label_cache` entries with `usedInstances`, no trigger or plan records, the `➛` order separator, the day-of-week map. Where a nuance contradicts one of them it is listed.

**How to read the evidence.** The SDK writes *draft* records with short blob entries and then calls the activation endpoint; the prompt's default is the *published* shape. A difference between the two is therefore not automatically an error in the prompt. Each item says which side has runtime evidence. Anything marked **[inferred]** was reasoned from the code, not read as a literal.

**Counts.** Disagreements: 24. In the SDK and missing from the prompt: 59 numbered items (ids 6; logic 3 blocks covering 15 logic types, 4 of them new detail; triggers 9; facts about the ten documented actions 9; record and field facts 15; custom actions 10; approval grammar 1; inline scripts and pills 6). In the prompt and not in the SDK: 14. Checked and consistent: 30.

---

## Disagreements

Most important first. "Published shape" means the prompt's default (Sections 2 to 7); "compact mode" means prompt Section 0.3.

### 1. Schedule trigger times: activating user's time zone (prompt) or UTC (SDK)

- **Prompt:** the `time` value in the `sys_hub_trigger_instance_v2.trigger_inputs` blob is read in the time zone of the user who activates the flow. L877 (`03:15:00` activated by a US/Pacific user gave `sys_flow_timer_trigger.time` = `11:15:00`), L1717, L1718, L2732, L2739. Tagged `[RUNTIME_TESTED]`.
- **SDK:** treats the blob value as UTC.
  - Write side: `Time({hours, minutes, seconds}, timezone)` is converted from the named zone **to UTC** before it is written (`sdk-build-core/src/plugins/time.ts:210-235`; `sdk-build-core/src/plugins/data-shape.ts:153-157`). With no zone argument it uses the build machine's local zone (`time.ts:237-246`).
  - Read side: `TimeShape.from(source, value, UTC_TIMEZONE_VALUE)` (`plugin/plugins/flow-instance-plugin.ts:272-275`; `UTC_TIMEZONE_VALUE = 'UTC'` at `plugin/utils/flow-constants.ts:118`).
  - Docs: every schedule example passes `"UTC"` (`docs/guides/wfa-trigger-guide.md:48, 209, 240, 272`) and line 230 says the week is computed in UTC, so `day_of_week: 1` is UTC Monday.
- **Why it matters:** the two cannot both be right for an admin whose time zone is not UTC. The prompt has a runtime result; the SDK's assumption was not run here. Worth one targeted test: build a Daily flow with the SDK using `Time({hours: 2}, "UTC")`, let the SDK activate it, and read `sys_flow_timer_trigger.time`. If it is not `02:00:00`, the SDK docs are wrong and the prompt's rule stands; if it is, the activation endpoint behaves differently from the Activate button for the SDK's service user (for example because that user's zone is UTC).

### 2. `sys_hub_flow_logic_instance_v2.connected_to` on Else and Else If

- **Prompt:** L587: Else and Else If point at the `ui_id` of the **If that opens the group**, "never at a preceding Else If" (80 of 80 and 67 of 67 live rows). L102 says the SDK's own output "leaves `connected_to` empty on Else".
- **SDK source:** `plugin/flow-logic/flow-logic-plugin-helpers.ts:2092-2124` (`handleSiblingConnection`). For `wfa.flowLogic.else` and `wfa.flowLogic.elseIf` it takes the **immediately preceding sibling statement** and sets `connected_to` to that record's `ui_id` (line 2119), merged into the record at lines 2081-2085. For If → Else If → Else that makes Else point at the **Else If**, not the If.
- **Probe:** the built XML has no `connected_to` element on the Else at all (matches prompt L102). **[inferred]** the assignment only happens when `transform.toRecord(sibling)` succeeds (line 2118), and it did not in that build.
- **Net:** three different behaviours (prompt rule, SDK source intent, SDK build output). The prompt's rule has the live-data evidence. L102 should say the source *intends* previous-sibling linking and the build left it empty.

### 3. Called subflow: master snapshot id (prompt) or `sys_hub_flow` id (SDK)

- **Prompt:** L78 and L549: `sys_hub_sub_flow_instance_v2.subflow` = the called subflow's **master snapshot** sys_id; each `subflow_inputs` entry `id` and `parameter.id` = that snapshot's `sys_hub_flow_input` sys_id (L2064).
- **SDK:** `plugin/plugins/flow-instance-plugin.ts:979`: `subflow` = `subflowDefRecord.getId()`, the subflow's own `sys_hub_flow` sys_id. Entry shape (lines 1697-1704) is `{"name":…, "value":…, "displayValue":…, "parameter":{"type":<internal type>}}`: **no `id`**, no `scriptActive`, and `children` only for complex objects (1707-1709). The key `waitForCompletion` is stripped from the inputs (1678) and written to `sys_hub_sub_flow_instance_v2.wait_for_completion` (981).
- **Why it matters:** prompt Section 0.3 says compact mode was tested only without subflows. If compact mode is used with a subflow call, the SDK's convention is the definition id, not the snapshot id. **[inferred]** activation rewrites it.

### 4. Step that calls a custom action: snapshot id (prompt) or definition id (SDK)

- **Prompt:** L79: `action_type` and `compiled_snapshot` = the action's master snapshot (`sys_hub_action_type_snapshot`), `action_type_parent` = its `sys_hub_action_type_definition`.
- **SDK:** `plugin/plugins/flow-instance-plugin.ts:918-919`: `action_type` **and** `action_type_parent` are both the `Action(...)` record's own id (the `sys_hub_action_type_definition` sys_id for a custom action; the built-in action id for an OOB action). `compiled_snapshot` is never written. Entries carry no `id`.
- Same compact-mode caveat as item 3. Prompt L102 already notes the OOB half of this ("sets `action_type_parent` equal to `action_type`").

### 5. Catch blob

- **Prompt:** L2052-2058: the Catch row's `values` has one `inputs` entry, `__status__`, holding the `FDACTIONSTATUS` JSON.
- **SDK:** `plugin/flow-logic/flow-logic-plugin.ts:510-518` writes the Catch with `values: createEmptyFlowLogicValues()`, i.e. `{"inputs":[],"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[]}` (`flow-logic-plugin-helpers.ts:105-114`). No `__status__` entry.
- Everything else about Try/Catch agrees (see "Checked and consistent").

### 6. Set Flow Variables: which entries carry `id`, and whether `inputs` equals `variables`

- **Prompt:** L1987: in the flow section `inputs` entries have **no** `id` key and `variables` entries have `id` = the flow variable sys_id. L1926 and L1989: the two arrays hold "identical entries".
- **SDK:** `plugin/plugins/flow-definition-plugin.ts:1566-1578`: **both** `variables` and `inputs` entries get `id` = the `sys_hub_flow_variable` sys_id. They are not identical: `inputs` entries are created with `displayValue: ""` (`createVariableInput`, `flow-logic-plugin-helpers.ts:211-213`) and `variables` entries with `displayValue` = the value (`createVariable`, 198-200). Both have `"parameter": {}`.

### 7. Assign Subflow Outputs entries

- **Prompt:** L2009-2012: each `outputsToAssign` entry has `flowLogicInstanceSysId` and `id` = the flow-section `sys_hub_flow_output` sys_id, plus a full `parameter`.
- **SDK:** `flow-logic-plugin-helpers.ts:155-170, 185-187, 684-686`: `{"id":"","name":…,"value":…,"displayValue":…,"children":[],"parameter":{},"scriptActive":false}`. No `flowLogicInstanceSysId`; `id` stays empty (the post-processing at `flow-definition-plugin.ts:1592-1710` never fills it, unlike flow variables).
- `sys_hub_flow_logic_instance_v2.outputs_assigned` = comma-joined output names on both sides.

### 8. Wait for a duration entries

- **Prompt:** L2034: "no `id` at entry level". L2042: `timer_relative_duration_operator` = `after` for a fixed wait. L2041: `timer_duration` displayValue "8 Seconds".
- **SDK:** `plugin/flow-logic/flow-logic-constants.ts:37-94`: all seven entries are `{"id":"<parameter id>","name":…,"value":"","displayValue":"","children":[],"scriptActive":false}`, so `id` **is** at entry level and there is no `parameter` object, except that `timer_duration` gets `"parameter":{"type":"glide_duration"}` (`flow-logic-plugin-helpers.ts:370-384`). For `explicit_duration` only entries 0, 3 and 6 are filled; `timer_relative_duration_operator` stays `""` (387-390). `timer_duration` displayValue is the same date-time string as the value (382-384).
- Names, parameter ids and entry order are identical on both sides. `duration_type` display values in the SDK: `explicit_duration` → `Explicit duration`, `relative_duration` → `Relative duration`, `percentage_duration` → `Percentage duration` (364-368).

### 9. `__action_status__` output: per-action complex object (prompt) or shared `FDACTIONSTATUS` (SDK)

- **Prompt:** L2230 and L2339: each action gets a `sys_complex_object` named `FD` + 32 hex, and the `__action_status__` output has `co_type_name=<FD name>`. That per-action name is the one clash seen (L58, L110).
- **SDK:** `plugin/utils/flow-constants.ts:573-597`: `__action_status__` attributes are `action_error_output=true,co_type_name=FDACTIONSTATUS,element_mapping_provider=…,uiType=object,uiTypeLabel=Object,uiUniqueId=<action sys_id>-action-status`. No per-action `sys_complex_object` is written for the status output; `FDACTIONSTATUS` is a platform built-in (`plugin/utils/built-in-complex-objects.ts:48-60`, sys_id `b91cc65087022010226ca1bb36cb0be4`, `sys_policy` `read`).
- The prompt's own older skeleton (L2425) also says `co_type_name=FDACTIONSTATUS`. If the shared name works in the published shape it removes the clash risk in Section 0.2; that is untested here.

### 10. `template_value` strings: terminator and caret escaping

- **Prompt:** L1231-1243: `field1=value1^field2=value2^field3={{pill}}`; no terminator and no escaping rule.
- **SDK:** `sdk-build-core/src/plugins/data-shape.ts:233-243`: joins `field=value` with `^`, **appends `^EQ`**, and **escapes a literal `^` inside a value as `^^`**. Probe blob: `"value":"description=SDK ELSE branch for {{Created_1.current.number}}^EQ"`.
- Inside a custom action step the same rules apply (`plugin/plugins/step-instance-plugin.ts:1131-1136, 1176`), except that a template containing pills goes to `sys_element_mapping.value` **without** `^EQ` (1140-1156).
- Both forms are reported as working: the prompt's test generators in `verification/tools/` contain no `^EQ`, and the SDK-built probe has it. The escaping rule is the part the prompt lacks: a field value containing `^` splits the template unless doubled.

### 11. `sys_hub_flow_stage.component_indexes`, `always_show`, `stage_id`, `order`

- **Prompt:** L703 `always_show` `true`; L708 `component_indexes` = "{{STEP_ORDER_AT_STAGE_BOUNDARY}}"; L713 `stage_id` = a UUID v4.
- **SDK:** `component_indexes` is the **zero-based index** of the first step of the stage, i.e. that step's `order` minus 1 (`flow-definition-plugin.ts:2334`; `plugin/utils/flow-stage-processor.ts:480`); when the same stage is started in several branches the indexes are comma-joined (534); a declared stage that is never started gets `""` (547). `order` is zero-based in first-use order (534, 544-548). `always_show` defaults to `false` (131). `stage_id` is the record's own sys_id re-hyphenated as a UUID (145, 218). `duration` default `1970-01-01 00:00:00` (`flow-constants.ts:35`).

### 12. Approval rule suffix `M`

- **Prompt:** L1587: `ApprovesRejectsAnyG[<group>]|AnyM` described as "Group members, plus manager option".
- **SDK:** `M` is the `manual` flag: `plugin/utils/approval-rules-processor.ts:98-102` emits `<ruleType>M` and returns without any `U[…]`/`G[…]`; parsed back at 241-245 as `manual: true`. `api/flow-data-helpers.ts:291-292` documents it as manual approval required (no auto-approval). Nothing in the SDK relates `M` to a manager.

### 13. `run_flow_in` choices and default

- **Prompt:** L2881 (Record Created): `choices` = `background`, `foreground` only, while `defaultValue` and the entry `value` are both `any`. L2902 (Service Catalog): `defaultValue` `""`, choiceList `""`/`background`/`foreground`, value `background`.
- **SDK:** `api/built-ins/triggers/created-trigger.now.ts:55-75` (same in Updated, Created or Updated and `service-catalog-trigger.now.ts:9-29`): three choices, `any` "Run flow in any context" (sequence 0), `background` "Run flow in background (default)" (1), `foreground` "Run flow in foreground" (2); default `any` for all four triggers.
- The prompt writes a value (`any`) that its own choice list does not contain. Harmless so far (it ran), but the SDK list is the complete one.

### 14. Record trigger input labels

- **Prompt:** L1631-1635 and L2879-2884: labels equal the element names (`run_on_extended`, `run_when_setting`, `run_flow_in`, `run_when_user_setting`, `run_when_user_list`); Service Catalog "Run Flow In".
- **SDK:** "Run On Extended Tables", "Run When Session Setting", "Run flow In", "Run When User Setting", "Run When User List" (`created-trigger.now.ts:20-109`). Cosmetic; the prompt's labels were read from an instance.

### 15. `valueSysId` on trigger entries

- **Prompt:** L1603: present on scheduled-trigger entries, absent on record-trigger entries.
- **SDK:** `plugin/plugins/flow-trigger-instance-plugin.ts:390`: `valueSysId: ""` is added only when the input type is `glide_list` (that is `run_when_user_list` on the three record triggers). Never on schedule entries.

### 16. `sys_hub_flow` defaults

- **Prompt:** L406 `run_as` `system`; L395 `flow_priority` empty; L396 `generation_source` empty.
- **SDK:** `plugin/constants/flow-plugin-constants.ts:13, 18, 28`: `flow_priority` default `MEDIUM` (allowed `LOW`/`MEDIUM`/`HIGH`, `docs/api/flow/flow-api.md:49`), `run_as` default `user`, `generation_source` `fluent`. `allowHighSecurityRoles` is only valid when `run_as` is `user` (`flow-definition-plugin.ts:2179-2184`).

### 17. Custom action inputs and outputs: `order` and `attributes`

- **Prompt:** L2338: `order` from 0; every input and output has `attributes` = `element_mapping_provider=…,uiType=<type>,uiTypeLabel=<label>,uiUniqueId=<new uuid>`. L2339: `__dont_treat_as_error__` and `__action_status__` are `read_only` true.
- **SDK:** `plugin/utils/flow-io-to-record.ts:87`: `order` = index + 1 (from 1). Inputs get **only** attributes the author supplied (188). Outputs get `element_mapping_provider=…,pwd2droppable=true,uiType=<type>,uiTypeLabel=<label>,uiUniqueId=<action sys_id>-<output name>` (176-186). System outputs (`flow-constants.ts:601-680`): `__action_status__` `order` 1, `max_length` 65000, `internal_type` `string`; `__dont_treat_as_error__` `order` 2, `max_length` 40, `internal_type` `boolean`, `default_value` `true`, attributes `action_error_output=true,element_mapping_provider=…,uiType=boolean,uiTypeLabel=True/False,uiUniqueId=<action sys_id>-action-error,visible_in_ui=false`. `read_only` is not set on either.

### 18. `sys_variable_value.order` for step settings

- **Prompt:** L2340: Script `order` 600, MID Application `order` 400 with value `35aa573fd7802200bdbaee5b5e610375`.
- **SDK:** every step `sys_variable_value` row has `order` 100 (`plugin/plugins/step-instance-plugin.ts:1088, 1211, 1276`; ext inputs 653, 703, 721). No MID Application row is written unless the author sets `application`.

### 19. `sys_complex_object.serialized_content` format and name

- **Prompt:** L2489-2506 offers a "simplified format" (`{"name","label","type","children"}`) "which the platform will accept". L118 and L2230: name = `FD` + 32 random hex.
- **SDK:** always writes the native format: root key `FlowDesigner:<name>`, one `<field>.$field_facets` per field and a `FlowDesigner:<name>.$type_facets` (`plugin/utils/complex-objects.ts:449-537`). `type` is `complex_object_schema` for an object and `complex_object_collection` for an array (`flow-io-to-record.ts:129`). Default name is deterministic: `FD<sys_id of the variable row>` (`flow-io-to-record.ts:106`), or for a step output `FD<step sys_id>_<output name>` (`step-instance-plugin.ts:748-749`).

### 20. Flow snapshot in the SDK's output

- **Prompt:** L102 and L130: the SDK writes "no snapshot".
- **SDK:** when the `Flow`/`Subflow`/`Action` config carries `masterSnapshot`, it writes a `sys_hub_flow_snapshot` (id = that value; `active` false, `status` `draft`, `master` true, `parent_flow`, same `label_cache`) plus snapshot copies of inputs, outputs and flow variables with `model_table` `sys_hub_flow_snapshot`, and sets both `latest_snapshot` and `master_snapshot` on the flow (`flow-definition-plugin.ts:2487-2573`). Same for actions with `sys_hub_action_type_snapshot` (`state` `draft`, `master` true, `parent_action`) at `plugin/plugins/flow-action-definition-plugin.ts:2708-2780`. No instance rows are mirrored. `masterSnapshot` is not in the docs; **[inferred]** it exists so a flow pulled from an instance keeps its snapshot id.

### 21. `sys_hub_alias_mapping` delete after subflow instances

- **Prompt:** L294-296 (skeleton item 11): no alias-mapping delete after a `sys_hub_sub_flow_instance_v2`.
- **SDK:** `plugin/utils/flow-to-xml.ts:30-33`: one `delete_multiple sys_hub_alias_mapping query="source_id=<instance sys_id>"` after every action instance **and** every subflow instance.

### 22. Get Catalog Variables `template_catalog_item` reference table

- **Prompt:** L1593: value = the `sc_cat_item` sys_id.
- **SDK:** the input references `st_sys_catalog_items_and_variable_sets` and is mandatory (`api/built-ins/actions/core/getCatalogVariables.now.ts:25`); `requested_item` is labelled "Submitted Request" and mandatory. The value the SDK writes is still the catalog item sys_id with the item name as `displayValue` (`flow-instance-plugin.ts:1439-1447`), so only the parameter's `reference` differs.

### 23. `condition_name` on If, Else If and Do Until

- **Prompt:** L1736-1769, L1917-1922: both `condition_name` and `condition` entries always present.
- **SDK:** `condition_name` is written only when a label was given; with no label the blob has the single `condition` entry (`flow-logic-plugin-helpers.ts:296-314, 408-425`; probe confirms). With an empty condition `inputs` is `[]`.

### 24. Prompt's summary of what the SDK covers

- **Prompt L24:** triggers "record, schedule, catalog and inbound-email"; logic list without Append to Flow Variables or Assign Subflow Outputs.
- **SDK:** also SLA Task, Knowledge Management and Remote Table Query triggers (`api/built-ins/triggers/index.ts:47-58`), and `appendToFlowVariables`, `assignSubflowOutputs` (`api/flow-logic/index.ts:49-59`). `goBackTo` exists in the plugin but is commented out of the public API (`api/flow-logic/index.ts:5, 32`) and of the id map (`plugin/flow-logic/flow-logic-constants.ts:100`).

---

## In the SDK, missing from the prompt

### A. Ids

**A1. Trigger definitions not in prompt Section 5.1**

| Trigger | `sys_hub_trigger_definition` sys_id | `trigger_type` | File |
|---|---|---|---|
| Inbound Email | `6f0180400b320300f4eb8bf637673ad4` | `email` | `api/built-ins/triggers/inbound-email-trigger.now.ts` |
| SLA Task | `f5ce00a873723300d70877186bf6a759` | `sla_task` | `api/built-ins/triggers/sla-task-trigger.now.ts` |
| Knowledge Management | `9bdb2c0483331210730e5b43c22bc071` | `knowledge_management` | `api/built-ins/triggers/knowledge-management-trigger.now.ts` |
| Remote Table Query | `778cf3bf37232110aba6473174924b7c` | `remote_table_query` | `api/built-ins/triggers/remote-table-query-trigger.now.ts` |

The pill-prefix table also knows a trigger named `REST API - Asynchronous` (`'REST API - Asynchronous_1'`, `plugin/utils/pill-string-parser.ts:142`) but the SDK has no definition or id for it.

**A2. Built-in actions not in prompt Section 5.2** (23 of the SDK's 33; ids also listed in `plugin/utils/flow-constants.ts:134-168`). The SDK holds only the `action_type` id; it has no `action_type_parent` ids. Input and output names are the `element` values; types are the SDK column helpers.

| Action | `action_type` sys_id | File | Inputs | Outputs |
|---|---|---|---|---|
| Add Worknote Link to Context | `fd4a0fb70f003300ecf0cc52ff767e2a` | `addWorknoteLinkToContext.now.ts` | `journal_field` FieldName (mandatory); `record` DocumentId (mandatory); `table` TableName (mandatory); `additional_comments` String | none |
| Associate Record to Email | `7b95a4c0a73133008299b39f087901b4` (category `0f722c44a73133008299b39f08790130`) | `associateRecordToEmail.now.ts` | `target_record` DocumentId (mandatory); `email_record` DocumentId (mandatory) | none |
| Copy Attachment | `30fe6cdb0f973300dfd3694e68767e5a` (category `a20738df9363130079b5925cf67ffb74`) | `copyAttachment.now.ts` | `target_record` DocumentId (mandatory, default 'ef43c6d40a0a0b5700c77f9bf387afe3'); `attachment_record` Reference (mandatory, ref sys_attachment); `table` TableName (mandatory) | none |
| Create or Update Record | `ab575ae253b3230034c6ddeeff7b12f1` | `createOrUpdateRecord.now.ts` | `fields` TemplateValue (mandatory); `table_name` TableName (mandatory) | `status` Choice (choices created/updated/error); `record` DocumentId; `error_message` String; `table_name` TableName |
| Create Task | `2b3a6335531003003bf1d9109ec58759` | `createTask.now.ts` | `task_table` TableName (mandatory); `wait` Boolean; `field_values` TemplateValue | `Table` TableName; `Record` DocumentId |
| Delete Attachment | `bdc2a0170f973300dfd3694e68767e47` (category `a20738df9363130079b5925cf67ffb74`) | `deleteAttachment.now.ts` | `delete_all_` Boolean (default true); `attachment_file_name` String; `record` DocumentId (mandatory, default 'ef43c6d40a0a0b5700c77f9bf387afe3'); `table` TableName (mandatory) | none |
| Delete Record | `c3e09916c31332002841b63b12d3aedf` | `deleteRecord.now.ts` | `record` DocumentId (mandatory) | none |
| Get Attachments on Record | `082e70db0f4273003788001ea8767e02` (category `a20738df9363130079b5925cf67ffb74`) | `getAttachmentsOnRecord.now.ts` | `file_name` String; `source_record` DocumentId (mandatory) | `parameter` Records (ref sys_attachment); `parameter1` Integer |
| Get Email Header | `a8cfa3efa70223008299b39f0879018b` (category `3a116084a71223008299b39f087901c1`) | `getEmailHeader.now.ts` | `target_header` String (mandatory); `email_record` Reference (mandatory, ref sys_email) | `header_value` String |
| Get Latest Response Text From Email | `a159d7820f13101051218e8ebc767eea` | `getLatestResponseTextFromEmail.now.ts` | `email_record` Reference (mandatory, ref sys_email) | `latest_response_text` String (mandatory) |
| Log | `5bc1bcc6531003003bf1d9109ec587d4` | `log.now.ts` | `log_level` Choice (default 'info', choices warn/info/error); `log_message` String | none |
| Look Up Email Attachments | `2dbeaf29c7322300f4eba1425a976340` (category `3a116084a71223008299b39f087901c1`) | `lookUpEmailAttachments.now.ts` | `email_record` Reference (mandatory, ref sys_email) | `email_attachments` Records (ref sys_email_attachment) |
| Look Up Attachment | `6ecdee36935023005e69925cf67ffb47` (category `a20738df9363130079b5925cf67ffb74`) | `lookupAttachment.now.ts` | `file_name` String; `source_record` DocumentId (mandatory) | `parameter1` String; `parameter` String |
| Move Attachment | `7159823353cc10103a33ddeeff7b1216` (category `a20738df9363130079b5925cf67ffb74`) | `moveAttachment.now.ts` | `source_attachment_record` Reference (mandatory, ref sys_attachment); `target_record` DocumentId (mandatory); `table` TableName (mandatory) | none |
| Move Email Attachments to Record | `bd8fcd48a73133008299b39f087901fc` (category `0f722c44a73133008299b39f08790130`) | `moveEmailAttachmentsToRecord.now.ts` | `target_record` DocumentId (mandatory); `email_record` DocumentId (mandatory) | none |
| Record Producer | `87a397837333001098e194596bf6a7bc` (category `bf2f2fec73f70300b61e66476bf6a774`) | `recordProducer.now.ts` | `record_table` TableName; `catalog_item` Reference (mandatory, ref sc_cat_item); `catalog_item_inputs` String; `_snc_dont_fail_on_error` Boolean | `error_message` String; `record` DocumentId; `table` TableName; `status` Choice (default '0', choices 0/1) |
| Send SMS | `027499be7333001099792f163cf6a7a7` | `sendSms.now.ts` | `recipients` String (mandatory); `message` String (mandatory) | `email` Reference (ref sys_email) |
| SLA Percentage Timer | `a1a50c4573873300d70877186bf6a762` | `slaPercentageTimer.now.ts` | `sla_flow_inputs` FlowObject; `percentage` Integer (mandatory); `task_sla_record` Reference (default '', ref task_sla) | `scheduled_end_date_time` DateTime; `status` Choice (default 'completed', choices skipped/repair/completed/paused/cancelled); `total_duration` Duration |
| Submit Catalog Item Request | `c7a04c607312001098e194596bf6a72a` (category `bf2f2fec73f70300b61e66476bf6a774`) | `submitCatalogItemRequest.now.ts` | `catalog_item_inputs` String; `delivery_address` String; `sysparm_requested_for` Reference (ref sys_user); `schedule` Reference (ref cmn_schedule); `duration` Duration (default '1970-01-01 00:00:00'); `_snc_dont_fail_on_error` Boolean; `catalog_item` Reference (mandatory, ref sc_cat_item); `timeout_flag` Boolean; `sysparm_quantity` Integer (default 1); `special_instructions` String; `wait_for_completion` Boolean | `error_message` String; `requested_item` DocumentId; `status` Choice (default '0', choices 0/1/2) |
| Update Multiple Records | `9daf2a72c75100105312134c95c26073` | `updateMultipleRecords.now.ts` | `table_name` TableName (mandatory); `conditions` Conditions (mandatory); `sort_type` Choice (default 'sort_asc', choices sort_desc/sort_asc); `field_values` TemplateValue (mandatory); `sort_column` FieldName; `dont_fail_flow_on_error` Boolean | `count` Integer; `message` String; `status` Choice (default '1', choices 0/1) |
| Wait For Condition | `89ce8a4187120010663ca1bb36cb0be3` | `waitForCondition.now.ts` | `timeout_duration` Duration; `table_name` TableName; `timeout_schedule` Reference (ref cmn_schedule); `timeout_flag` Boolean; `record` DocumentId (mandatory); `conditions` Conditions (mandatory) | `state` Choice (default '0', choices 0/1) |
| Wait For Email Reply | `8e38de067f0312108e688c90ac866501` | `waitForEmailReply.now.ts` | `timeout_schedule` Reference (ref cmn_schedule); `record` Reference (mandatory, ref sys_email); `enable_timeout` Boolean; `timeout_duration` Duration | `state` Choice (default '0', choices 0/1); `email_reply` Reference (ref sys_email) |
| Wait For Message | `605d0ab8931012105cd18166448918db` | `waitForMessage.now.ts` | `message` String (mandatory); `enable_timeout` Boolean; `timeout` Duration | `payload` String |

Action category ids seen: `bf2f2fec73f70300b61e66476bf6a774` (the Service Catalog actions), `a20738df9363130079b5925cf67ffb74` (attachment actions), `0f722c44a73133008299b39f08790130` and `3a116084a71223008299b39f087901c1` (email actions).

**A3. Step types not in prompt Section 5.4** (22 beyond Script; `plugin/utils/flow-constants.ts:181-522`, full schemas in `api/built-ins/action-steps/action-step-definitions.now.ts`). The variable sys_ids are what goes in `sys_variable_value.variable` for a step setting.

| Step type | `sys_flow_step_definition` sys_id | `actionStep.` name | Input variables (element, variable sys_id, uiType where the SDK records one) | Output variables |
|---|---|---|---|---|
| Ask for Approval | `a4eb47900b22320085c083eb37673acc` | `askForApproval` | `approval_reason` `30a496c67f3012108e688c90ac8665a0`; `approval_conditions` `745c0f900b22320085c083eb37673a79` (approval_rules); `record` `982c8b900b22320085c083eb37673a7c`; `table` `a44ccb900b22320085c083eb37673ab4`; `due_date` `d3dac4860b333200c438ee6537673a5a` (schedule_date_time); `approval_field` `db521c5567323200c4098c7942415a67`; `journal_field` `f7b3d09567323200c4098c7942415a65` | `state` `aa7568070b23320085c083eb37673a73` |
| Collect Activity Context | `05a6e480a301311029c4d1f3e31e61f1` | `collectActivityContext` | none | `activity_context` `89e202b9a3013110fc7ad1f3e31e616d` |
| Create App From Payload | `65a40b525b12101083f30f216581c787` | `createAppFromPayload` | `template_instance_id` `03c116415b03101083f30f216581c74d`; `scan_id` `c74f30905b33101083f30f216581c7f0` | `sys_app_id` `f343f3925b12101083f30f216581c739` |
| Create Record | `9cbaa0f267003200553fafb49585ef69` | `createRecord` | `skip_insert` `9e5f9d85536333003bf1d9109ec587c6` (boolean); `create_record_field_values` `e78d203667003200553fafb49585ef63` (template_value); `create_record_table_name` `f0fb68f267003200553fafb49585efa0` | `table_name` `795c557267003200553fafb49585efb0`; `record` `966cd57267003200553fafb49585efa0` |
| Create Record For Remote Table | `e0b9272d53112110aba6ddeeff7b1224` | `createRecordForRemoteTable` | `query_id` `8d068211a3913110aba698e6d31e61b6`; `create_record_table_name` `c442d88a53912110aba6ddeeff7b1277`; `create_record_field_values` `e5d96b2d53112110aba6ddeeff7b1236` (template_value) | `table_name` `2b3a236d53112110aba6ddeeff7b129d` |
| Create Task | `07973e960b233200cbd9e240e0ea604e` | `createTask` | `skip_insert` `1aeb688553af33003bf1d9109ec58710` (boolean); `create_record_field_values` `2a7872d60b233200cbd9e240e0ea601e` (template_value); `create_record_table_name` `9b6832d60b233200cbd9e240e0ea601c`; `wait` `a498b2d60b233200cbd9e240e0ea6004` (boolean) | `table` `19efa6b653333200f5bf435723dc340e`; `task` `9f0b036353233200f5bf435723dc3475` |
| Create or Update Record | `8f5c107a53a3230034c6ddeeff7b129d` | `createOrUpdateRecord` | `fields` `5eac547a53a3230034c6ddeeff7b12c7` (template_value); `table` `728c907a53a3230034c6ddeeff7b12e9` | `record` `5d0ade9c537b230034c6ddeeff7b12ac`; `table_name` `9c9ad6dc537b230034c6ddeeff7b127e`; `error_message` `9dbbda1053bb230034c6ddeeff7b12c8`; `status` `b32b521053bb230034c6ddeeff7b12d2` |
| Delete Multiple Records | `8c6b7466c71100105312134c95c2602a` | `deleteMultipleRecords` | `set_workflow` `156c34a6c71100105312134c95c26068` (boolean); `table_name` `693c70a6c71100105312134c95c26011`; `dont_fail_flow_on_error` `76207652c72a40105312134c95c26083` (boolean); `sort_column` `79fb8029c7ee00105312134c95c26042`; `conditions` `a34cb0a6c71100105312134c95c260a3` (conditions); `sort_type` `a85c8429c7ee00105312134c95c26033` | `error_message` `60fbbc66c71100105312134c95c26033`; `status` `ce41be52c72a40105312134c95c2606b`; `count` `e7db3c66c71100105312134c95c26031` (integer) |
| Delete Record | `b67821c1c723220061f553c6f09763c2` | `deleteRecord` | `record` `995a2105c723220061f553c6f0976301`; `table_name` `ab19a9c1c723220061f553c6f0976383` | none |
| Email | `4c5f36a37f0b32005f58108c3ffa9126` | `email` | `watermark_email` `0fba76757303230082999cfd7bf6a7f2` (boolean); `cc` `33c003277f0b32005f58108c3ffa91e8`; `to` `40cf3ae37f0b32005f58108c3ffa91f3`; `subject` `4d0183277f0b32005f58108c3ffa9197`; `body` `8ef44f277f0b32005f58108c3ffa91f7`; `record` `9971a338a70323008299b39f08790195`; `table_name` `e1312338a70323008299b39f087901f5`; `bcc` `e8f043277f0b32005f58108c3ffa91d1` | `email` `f4a503677f0b32005f58108c3ffa91cf` |
| Fire Event | `092bb996ff30311077a95dac793bf166` | `fireEvent` | `table` `020ebd5aff30311077a95dac793bf1ea`; `parm1` `077ef59aff30311077a95dac793bf1ba`; `parm2` `17be7d9aff30311077a95dac793bf18f`; `event_name` `599cf11aff30311077a95dac793bf1d2`; `record` `a3ad395aff30311077a95dac793bf12e` | none |
| Get Latest Response Text From Email | `0e07df020f13101051218e8ebc767e57` | `getLatestResponseTextFromEmail` | `email_record` `44d757420f13101051218e8ebc767eee` | `latest_response_text` `6f88df420f13101051218e8ebc767e67` |
| Log | `a03fea9bc712220061f553c6f09763b1` | `log` | `log_message` `4fc2fadbc712220061f553c6f0976388`; `log_level` `ab123adbc712220061f553c6f0976387` | none |
| Look Up Record | `dc9c26043b23220057a4a2e334efc447` | `lookUpRecord` | `conditions` `0cfca6043b23220057a4a2e334efc43b` (conditions); `multiple_records_found` `3b9387923b23220057a4a2e334efc4e4`; `sort_column` `a6da115587003300663ca1bb36cb0bc0`; `dont_fail_flow_on_error` `b019356673110010d70877186bf6a780` (boolean); `sort_type` `c62b915587003300663ca1bb36cb0bd2`; `lookup_table_name` `f9cc66043b23220057a4a2e334efc42f` | `error_message` `145a3da673110010d70877186bf6a7a5`; `status` `14bd89c673310010d70877186bf6a7be`; `table_name` `a64d6a043b23220057a4a2e334efc4e8`; `record` `d3e627913b23220057a4a2e334efc45e` |
| Look Up Records | `48526b2dc32a32002841b63b12d3ae72` | `lookUpRecords` | `limit` `0677f8e053200300f5bf435723dc34e3` (integer); `sort_column` `2df79dd187003300663ca1bb36cb0b33`; `table_name` `4d19bb21c36a32002841b63b12d3aeef`; `sort_type` `6a88151587003300663ca1bb36cb0b14`; `conditions` `95f8bb21c36a32002841b63b12d3ae0c` (conditions) | `records` `5db8f721c36a32002841b63b12d3aeb7`; `table_name` `c576f2a2c32232002841b63b12d3ae66`; `count` `f6700274c32b32002841b63b12d3ae37` (integer) |
| Notification | `5d31f8f37f1322004d145212bdfa9145` | `notification` | `record` `4d1cbc717f0332004d145212bdfa91b8`; `table_name` `b8a793697f2a32005f58108c3ffa910b`; `notification` `cc7fb8b17f0332004d145212bdfa91da` | none |
| SMS | `f760b5c2737c001086592f163cf6a758` | `sms` | `message` `c951b106737c001086592f163cf6a75a`; `recipients` `dd317dc2737c001086592f163cf6a7fe` | `email` `29817506737c001086592f163cf6a72d` |
| Script | `106afb6647032200b4fad7527c9a71e7` | `script` | `mid_cluster` `0d2db9e653310110d3a8ddeeff7b1208`; `host` `28e4e579b3101300176b051a16a8dc0f`; `connection_alias` `2b2ba571b3101300176b051a16a8dc8f`; `mid_selection_type` `2c226939b3101300176b051a16a8dc83`; `script` `71aa7f6647032200b4fad7527c9a719b`; `required_run_time` `74315b04b3201300176b051a16a8dc2b`; `capabilities` `7d36ed79b3101300176b051a16a8dceb`; `mid_selection` `cbd1070373531010791f94596bf6a776`; `mid_server` `f0d58b8373531010791f94596bf6a7be`; `application` `f5e56d79b3101300176b051a16a8dce4` | none |
| Update Multiple Records | `a3dfc066c7dd00105312134c95c26014` | `updateMultipleRecords` | `set_autosysfields` `0f7194a6c7dd00105312134c95c26028` (boolean); `sort_column` `168d8069c7ee00105312134c95c260a7`; `conditions` `66401866c7dd00105312134c95c2607e` (conditions); `sort_type` `71ad0469c7ee00105312134c95c26027`; `set_workflow` `8a6154a6c7dd00105312134c95c26019` (boolean); `field_values` `a5505866c7dd00105312134c95c26065` (template_value); `table_name` `c530d466c7dd00105312134c95c26066`; `dont_fail_flow_on_error` `e2214bd6c72a40105312134c95c2600c` (boolean) | `error_message` `10209466c7dd00105312134c95c26031`; `status` `4f814fd6c72a40105312134c95c26001`; `count` `a4101466c7dd00105312134c95c260a8` (integer) |
| Update Record | `b51f683667003200553fafb49585ef3f` | `updateRecord` | `table_name` `3930d57267003200553fafb49585efc5`; `record` `aab0ddb267003200553fafb49585ef30`; `update_record_field_values` `fcbf6c3667003200553fafb49585ef2e` (template_value) | `table_name` `2fb3d57267003200553fafb49585ef43`; `record` `ffd3197267003200553fafb49585ef5a` |
| Wait For Condition | `4c9234ca0b18030085c083eb37673aaa` | `waitForCondition` | `timeout_duration` `1fac6063876100102fa5a1bb36cb0bac` (glide_duration); `table_name` `72b2bcca0b18030085c083eb37673a0b`; `conditions` `7de2fcca0b18030085c083eb37673aed` (conditions); `timeout_schedule` `ae1d6463876100102fa5a1bb36cb0b56`; `timeout_flag` `bc93428187120010663ca1bb36cb0b83` (boolean); `record` `c5d2fcca0b18030085c083eb37673a1c` | `state` `1fbdac63876100102fa5a1bb36cb0ba2` |
| Wait For Email Reply | `81e15fbd7fcb12108e688c90ac866541` | `waitForEmailReply` | `record` `391597b17f0f12108e688c90ac866571`; `timeout_duration` `3e78d3b57f0f12108e688c90ac86653b` (glide_duration); `enable_timeout` `b3285f757f0f12108e688c90ac866575` (boolean); `timeout_schedule` `b7a8d7b57f0f12108e688c90ac86659f` | `email_reply` `10991bf57f0f12108e688c90ac866577`; `state` `752ad3397f0f12108e688c90ac866579` |
| Wait For Message | `0d9746f0931012105cd181664489188c` | `waitForMessage` | `timeout_duration` `15a942b4931012105cd18166448918bc` (glide_duration); `message` `83e74ef0931012105cd181664489182b`; `enable_timeout` `d728c634931012105cd18166448918b0` (boolean) | `payload` `640b4ef4931012105cd181664489180b` |

Neither REST (`07a762fb47222200b4fad7527c9a7129`) nor JSON Parser (`502328c387523300f917e55936cb0bf0`) appears anywhere in the SDK source, which agrees with the prompt.

**A4. Script step inputs the prompt does not list.** The prompt names two (`script` `71aa7f6647032200b4fad7527c9a719b`, `application` `f5e56d79b3101300176b051a16a8dce4`). The SDK lists ten (`api/built-ins/action-steps/action-step-definitions.now.ts:104-203`): `required_run_time` `74315b04b3201300176b051a16a8dc2b` (mandatory choice: `vanilla` "Vanilla (Core JavaScript)", `mid`, `instance`), `mid_selection_type` `2c226939b3101300176b051a16a8dc83` (`any`, `use_connection_alias`, `define_connection_inline`), `mid_selection` `cbd1070373531010791f94596bf6a776` (`auto_select`, `specific_mid_server`, `specific_mid_cluster`), `mid_cluster` `0d2db9e653310110d3a8ddeeff7b1208`, `mid_server` `f0d58b8373531010791f94596bf6a7be`, `host` `28e4e579b3101300176b051a16a8dc0f`, `connection_alias` `2b2ba571b3101300176b051a16a8dc8f` (ref `sys_alias`), `capabilities` `7d36ed79b3101300176b051a16a8dceb` (ref `ecc_agent_capability`); `application` references `ecc_agent_application`.

**A5. Built-in complex objects** (`plugin/utils/built-in-complex-objects.ts:20-81`): `FDChangeDetails` `239e04950f023300ecf0cc52ff767e0c` (`complex_object_schema`), `FDSTEPSTATUS` `73720df26f312010bf408271145b3600` (`complex_object_schema`; fields `code` Integer, `message` String), `FDACTIONSTATUS` `b91cc65087022010226ca1bb36cb0be4` (`complex_object_schema`, `sys_policy` `read`), `FDCollection` `f4f014150f023300ecf0cc52ff767eed` (`complex_object_collection` of `FDChangeDetails`). All `namespace` `FlowDesigner`.

**A6. Approval due date handling ids** (`plugin/utils/flow-constants.ts:128-132`): the SDK parses a `schedule_date_time` value as an approval due date only for `f8f2e9920b10030085c083eb37673abd` (Ask For Approval action), `a4eb47900b22320085c083eb37673acc` (Ask for Approval step) and `cd04ac7573011010791f94596bf6a716` (the SDK's own comment says its identity is unknown).

### B. Logic types: how the plugin writes each row

Every logic row is a `sys_hub_flow_logic_instance_v2` with these fields and no others (`flow-logic-plugin-helpers.ts:47-69, 2034-2090`; `flow-definition-plugin.ts:2446-2450`): `comment` (the annotation), `logic_definition`, `values`, `ui_id`, `parent_ui_id` (only when nested), `flow`, `order`, plus `connected_to`, `outputs_assigned` or `flow_variables_assigned` where noted. `values` is always the six-key object `{"inputs":[],"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[]}`; `decisionTableInputs`, `dynamicInputs` and `workflowInputs` are always `[]`. A generic entry is `{"id":"","name":…,"value":…,"displayValue":…,"children":[],"parameter":{},"scriptActive":false}` (155-170).

| Logic | `logic_definition` | `values` content | Other fields and rules |
|---|---|---|---|
| If | `af4e1945c3e232002841b63b12d3ae3e` | `inputs`: optional `condition_name`, then `condition` | children get `parent_ui_id` = its `ui_id` |
| Else If | `666e5545c3e232002841b63b12d3ae99` | same as If | `connected_to`: see Disagreement 2; must directly follow an If or Else If |
| Else | `1f781bf3c32232002841b63b12d3aee6` | all empty | as Else If |
| For Each | `098e1dc5c3e232002841b63b12d3ae33` | `inputs`: one entry `{"id":"","name":"items","value":<pill>,"displayValue":<pill>}` (no `children`, `parameter` or `scriptActive`; 321-338) | item pills inside the body are `{{<for each ui_id>.item…}}` whatever the author called the loop variable (`flow-logic-plugin.ts:749-784`); the items pill must be an array type (`records`, `array.object`, `array.string`, …) |
| Do the following until | `eaeb040687210300e6c2c88fc0e3ec89` | `inputs`: optional `condition_name`, then `condition` (408-425) | do-while: the condition is evaluated after the body |
| Do the following in Parallel | `5d31e5dedfe50300b61ecae83df26326` | all empty | one Parallel Branch row (`a1168de173311300b61e66476bf6a7d0`, empty values, `parent_ui_id` = the parallel row) per non-empty branch; an empty branch writes no row; nesting a parallel inside a parallel is refused (`flow-logic-diagnostics.ts:399-412`) |
| Try / Catch | `07223332de022010ec58424b73829721` / `35d60003e6022010a5e40cdd1254dd21` | both all empty | Catch: `connected_to` = Try `ui_id`, same `parent_ui_id` as the Try (`flow-logic-plugin.ts:505-559, 710-719`); row order is Try, try body, Catch, catch body |
| Wait for a duration | `fdb2541473031300b61e66476bf6a70e` | seven fixed entries (Disagreement 8) | outputs usable as pills: `total_duration`, `scheduled_end_date_time` (`docs/api/flow/wfa-flow-logic-api.md:509-514`) |
| Set Flow Variables | `4f787d1e0f9b0010ecf0cc52ff767ea0` | `inputs` and `variables` (Disagreement 6) | `flow_variables_assigned` = comma-joined variable names |
| **Append to Flow Variables** | `4784e82683031210d266f953d22bc0fd` | **same wire format as Set Flow Variables** (`flow-logic-plugin-helpers.ts:236-238, 285-288, 742-748`); only the platform's handling differs (append instead of overwrite) | `flow_variables_assigned` = comma-joined names (2066-2070); target must be an array-of-objects flow variable (`docs/api/flow/wfa-flow-logic-api.md:451-455`) |
| Assign Subflow Outputs | `df4e1945c3e232002841b63b12d3ae3e` | `outputsToAssign` (Disagreement 7) | `outputs_assigned` = comma-joined names |
| **Exit Loop** | `7444b31c37063110ac85cdd734924bff` | all empty (227) | no other fields; must be inside a For Each or Do the following until (`flow-logic-diagnostics.ts:786-798`) |
| **Skip Iteration** | `48de1b5837063110ac85cdd734924b15` | all empty (229) | same placement rule |
| End Flow | `d176605ea76103004f27b0d2187901c7` | all empty (228) | must be inside If, Else If, Else, For Each, Do until, Parallel or Try/Catch (`flow-logic-diagnostics.ts:800-820`) |
| **Go back to** | `59ea75fd77502110b2b4ddd9cf5a99ef` (commented out at `flow-logic-constants.ts:100`, so the SDK cannot build it today) | `inputs`: one entry `name` `go_back_to_step`, `value` = the **`ui_id`** of the target step (`flow-logic-plugin-helpers.ts:316-319, 797-800`) | placement rule coded: only inside an If/Else If/Else branch, a Catch branch or a decision branch, and not inside the flow's error handler (`flow-logic-diagnostics.ts:156-184`) |

Not in the SDK at all: **Make a decision** (only the string `'MakeADecision'` in the Go back to placement check, `flow-logic-diagnostics.ts:202`; no id, no `decisionTableInputs` writer, `decision_table` never written), **Get Flow Outputs**, **Call a Workflow**, **Dynamic Flow** (no ids, no code; `workflow_reference` never written; `dynamic_inputs` and `dynamic_choice` are listed as unsupported data types at `flow-constants.ts:120`).

**Flow-level error handler (Top Level Try/Catch):** not implemented. The only trace is a stub, `isWithinErrorHandler`, that always returns false with a to-do note for when an error handler is added (`flow-logic-diagnostics.ts:240-243`). Nothing in the SDK shows how that handler is stored.

**Flow stages (`sys_hub_flow_stage`):** see Disagreement 11 (the stage fields) and section E items 5, 11, 12 and 13 (subflow stages, states JSON, identity, placement rules).

### C. Triggers

1. **Outputs the prompt does not list.** Record triggers: `current` (document_id, depends on `table_name`), `table_name`, `run_start_time`, `run_start_date_time` (`created-trigger.now.ts:111-130`). Updated and Created or Updated add `changed_fields`, an array of `FDChangeDetails` objects with `previous_display_value`, `previous_value`, `current_display_value`, `current_value`, `field_name` (`updated-trigger.now.ts:143-166`). Daily, Weekly, Monthly, Repeat, Run Once: `run_start_time`, `run_start_date_time`. Service Catalog: `request_item` (ref `sc_req_item`), `table_name` (default `sc_req_item`), `run_start_time`, `run_start_date_time`.
2. **Inbound Email** (`email`): inputs `email_conditions` (conditions on `sys_email`, attribute `condition_builder=v2`), `order` (integer, `visible=false`), `stop_condition_evaluation` (boolean, default `true`, `visible=false`), `target_table` (table_name, "Reply Record Type"). Outputs `inbound_email` (ref `sys_email`), `target_table_name`, `target_record`, `subject`, `body_text`, `from_address`, `user` (ref `sys_user`). Pills start `{{Inbound Email_1.…}}`.
3. **SLA Task** (`sla_task`): no inputs. Outputs `task_sla_record` (ref `task_sla`) and `sla_flow_inputs` (object: `duration`, `relative_duration_works_on`, `is_repair`, `duration_type`, `name`).
4. **Knowledge Management** (`knowledge_management`): no inputs. Outputs `knowledge` (ref `kb_knowledge`), `table_name` (default `kb_knowledge`), `run_start_time`, `run_start_date_time`.
5. **Remote Table Query** (`remote_table_query`): input `u_table` (table_name, reference `sys_script_vtable`). Outputs `table_name`, `query_parameters` (name-value pairs), `query_id`.
6. **Hidden inputs.** An input whose attributes include `visible=false` or `visible_in_fd=false` is treated as hidden (`flow-trigger-instance-plugin.ts:46-52`; `flow-instance-plugin.ts:83-90`).
7. **Custom triggers.** A trigger blob that contains an input named `trigger_type` marks a custom trigger, which the SDK refuses to convert (`flow-trigger-instance-plugin.ts:84-88`).
8. **Service Catalog `run_flow_in` fallback.** When that blob value is empty the SDK reads `sys_flow_catalog_trigger.run_flow_in` through `sys_hub_flow.remote_trigger_id`, else assumes `background` (57-71).
9. **Trigger label text for `label_cache`** (`plugin/utils/label-cache-processor.ts:34-48`): `Trigger - Record Created`, `Trigger - Record Updated`, `Trigger - Record Created or Updated`, `Trigger - Run Daily`, `Trigger - Run Weekly`, `Trigger - Run Monthly`, `Trigger - Run Repeat`, `Trigger - Run Once`, `Trigger - Inbound Email`, `Trigger - Service Catalog`, `Trigger - Knowledge Management`, `Trigger - Remote Table Query`, `Trigger - SLA Task`.

### D. Actions the prompt documents: facts it lacks

1. **Ask For Approval output choices.** `approval_state` values: `not requested`, `requested`, `approved`, `rejected`, `cancelled`, `not_required`, `skipped` (`askForApproval.now.ts:48-80`). Prompt L1575 names two.
2. **Ask For Approval lengths:** `approval_field`, `journal_field`, `approval_conditions` max 8000; `approval_reason` max 160.
3. **Approval due date fields** (`plugin/utils/flow-shapes.ts:260-288`; `api/flow-data-helpers.ts:423-436`): `action` one of `none`, `approve`, `reject`, `cancel`; `date_type` `actual` or `relative`; `date` a pill or `{}`; `duration` a number; `duration_type` one of `years`, `quarters`, `months`, `weeks`, `days`, `hours`, `minutes`, `seconds`; `schedule` a `cmn_schedule` sys_id; `schedule_label` always written `""`.
4. **Send Email output:** `email` (reference to `sys_email`), usable as `{{<ui_id>.email}}` (`sendEmail.now.ts:54`). The SDK refuses data pills in `ah_body` at build time (`plugin/plugins/flow-diagnostics-plugin.ts:160-173`); the source gives no reason.
5. **Look Up Record output `status`:** choice `0` "Success", `1` "Error", default `0`; `error_message` max 8000.
6. **Fluent name alias:** the SDK calls the Look Up Record flag `dont_fail_flow_on_error` and writes it as `__snc_dont_fail_on_error` (`flow-constants.ts:547-557`; applied at `flow-instance-plugin.ts:1121, 1149`). Record Producer and Submit Catalog Item Request use `_snc_dont_fail_on_error` (one leading underscore).
7. **Create Catalog Task:** `ah_wait` default `true`; `ah_table_name` default `sc_task`, read-only; `ah_fields` depends on `ah_table_name`, max 65000; `catalog_variables` and `ah_short_description` max 12000. The SDK writes booleans as JSON `true`/`false` (prompt L1597 uses `1`/`true`); **[inferred]** from the pass-through at `flow-instance-plugin.ts:1148-1156`.
8. **Catalog variable pills:** for Get Catalog Variables and Create Catalog Task the SDK builds `catalog_variables` as `<variable sys_id>:item_option_new` joined by commas, taking variables from the item and from its variable sets (`io_set_item` → `variable_set`) (`flow-instance-plugin.ts:1359-1412`).
9. **Which entries the SDK emits (compact mode).** Only inputs the author supplied, plus inputs that have a default or are hidden (`flow-instance-plugin.ts:1574-1618, 1175-1259`). The probe's Look Up Record blob has four entries (`sort_type`, `conditions`, `table`, `if_multiple_records_are_found_action`), not six. `displayValue` is the raw value (`"sys_user"`, not `"User"`). A defaulted or hidden entry's `parameter` also carries the input's `attributes` object and `reference`.

### E. Record and field facts

1. **`ui_id` is derived, not random.** `ui_id` = the row's own sys_id re-hyphenated 8-4-4-4-12 (`plugin/utils/utils.ts:32-36`; `flow-instance-plugin.ts:940, 998`; `flow-logic-plugin-helpers.ts:66-68`). Same for a step's `cid` (`step-instance-plugin.ts:596`) and a stage's `stage_id`.
2. **`order`** is 1, 2, 3… with no gaps, one number per row in depth-first order, nested rows included (`flow-definition-plugin.ts:2305, 2420-2453`). The composite `<n-1>➛<n>` is given to whichever row directly follows a Parallel Branch row (2422-2434).
3. **`sys_hub_action_instance_v2.active`** = `true` is written (`flow-instance-plugin.ts:916`; present in the probe). The prompt's template (L486-508) has no `active`.
4. **`sys_hub_trigger_instance_v2.category`** = `""` is written (`flow-trigger-instance-plugin.ts:219`); `comment` holds the annotation.
5. **`sys_hub_sub_flow_instance_v2.show_stages`** comes from `showSubflowStage` (default false). When true, a `sys_hub_flow_stage` row of `type` `subflow` is added: `value` = the subflow instance's `ui_id`, `label` = the subflow's name, `states` `{}`, `component_indexes` `""`, `always_show` false, `order` continuing after the declared stages (`flow-stage-processor.ts:171-223`).
6. **`sys_hub_flow.run_with_roles`** = comma-joined role sys_ids; **`sys_policy`** = `read` for a read-protected flow; **`internal_name`** is written only when supplied (otherwise the platform derives it) (`flow-definition-plugin.ts:2189-2212`).
7. **Deletes are generated only for child tables that have rows in this payload**, in the form `<parent field>=<parent id>^sys_idNOT IN<ids>` (`flow-to-xml.ts:72-94, 235-294`). Never generated for `sys_flow_record_trigger`, `sys_flow_timer_trigger`, `sys_hub_flow_snapshot`, `sys_choice`, `sys_documentation`, `sys_complex_object`, `sys_element_mapping` (16-24). Record fields are written in alphabetical order (49).
8. **`sys_choice` rows** are wrapped as `<sys_choice field="<element>" table="<var__m_ name>">…</sys_choice>` groups (`flow-to-xml.ts:107-146`).
9. **Relationship keys the SDK relies on** (useful for Appendix D audits; `flow-definition-plugin.ts:1011-1137, 1724-1780`): `sys_flow_record_trigger` and `sys_flow_timer_trigger` are reached from `sys_hub_flow.remote_trigger_id`; `sys_flow_trigger_auto_script.trigger` → the timer trigger; `sys_trigger_runner_mapping.identifier`; `sys_flow_trigger_plan.plan_id`, `sys_flow_subflow_plan.plan_id`; `sys_hub_flow_snapshot.parent_flow`; `sys_hub_pill_compound.attached_to`; `sys_hub_alias_mapping.source_id`; `sys_flow_cat_variable_model.id` → `sys_flow_cat_variable.flow_catalog_model`; legacy `sys_hub_sub_flow_instance_inputs.model`, `sys_hub_flow_logic_ext_input.model`, `sys_hub_input_scripts.instance`. A complex object is matched to its input or output by the regex `co_type_name=([^,]+)` on `attributes` (`flow-io-to-record.ts:581-584`).
10. **What makes the SDK give up on a flow** (so it is a list of things it cannot represent; `flow-constants.ts:17-23`, `utils.ts:362-377`): any `sys_hub_pill_compound` row (data pill transforms) or any V1 row (`sys_hub_trigger_instance`, `sys_hub_action_instance`, `sys_hub_sub_flow_instance`, `sys_hub_flow_logic`).
11. **Stage states JSON** default: `{"in_progress":"In progress","complete":"Completed","error":"Error","pending":"Pending - has not started","skipped":"Skipped"}`; custom labels use the keys `pending`, `in_progress`, `complete`, `error`, `skipped` (`flow-stage-processor.ts:54-68`).
12. **Stage identity:** `sys_hub_flow_stage` coalesces on `flow` + `value`; `type` is `standard` or `subflow`; `ancestor_array_position` 0 and `ancestor_component_id`, `ancestor_stage_id`, `ancestral_if_else_logic` empty (`flow-stage-processor.ts:123-146`).
13. **Stage placement rules** (`flow-diagnostics-plugin.ts:319-354`): a stage cannot start inside a For Each or a Parallel block, and cannot be the last statement of the flow or of an If/Else If/Else/Try/Catch branch.
14. **Flow variable types the SDK allows:** string, integer, decimal, reference, date-time, boolean, float, JSON, object, array (`utils.ts:124-136`). Inside an object: string, integer, decimal, date-time, boolean, object, array only (138-146). Reference fields are not allowed inside an object or array used as a subflow or action input or output (`complex-objects.ts:304-316`).
15. **`label_cache` details** (`label-cache-processor.ts`): a new entry is `{"name":…,"label":"","type":<type>,"base_type":<type>,"usedInstances":{<ui_id>:[<input name>]},"attributes":{}}` (491-500) with `parent_table_name`, `column_name`, `reference` added when known; for a flow variable or subflow input the SDK adds `reference_table` and `reference_display` (838-841; note `reference_table`, where the prompt's shape at L2179 uses `reference`). Labels: trigger `Trigger - Record Created➛<table> Record➛<Field Words>` (696-716); For Each item `<n> - For Each - ➛<table> Record➛<Field Words>` or `…➛item` (670-693); flow variable `Flow Variables➛<label>`; subflow input `Input➛<label>`; a step output gets its raw path joined by `➛` (787-791; probe: `30fcf185-…➛Record➛name`). `usedInstances` lists the input **name** for each use; for a child of an object input it lists the child field name.

### F. Custom actions (prompt Section 10.0 to 10.0.3)

1. **Definition as the SDK writes it** (`flow-action-definition-plugin.ts:2366-2381`): `sys_hub_action_type_definition` with `name`, optional `internal_name`, `annotation`, `description`, `access` `public`, `category`, `sys_policy`, `active` **true**, `state` **`draft`**, `system_level` false, `label_cache`. The activation call is then sent for it (`plugin/post-install.ts:31-52`). Coalesce keys the SDK declares: `sys_hub_action_input` and `sys_hub_action_output` on `model` + `element`; `sys_hub_action_status_metadata` on `action_type_id`; `sys_hub_status_condition` on `action_status_metadata_id` + `order`; `sys_element_mapping` on `id` + `table` + `field` (2335-2349).
2. **Step instance** (`step-instance-plugin.ts:582-597`): `step_type`, `order`, `active` true, `label`, `cid`, `action`, and `error_handling_type`: **`1` = stop the action, `2` = do not stop the action** (47-50); default 1. The prompt has only the value 1 with no meaning.
3. **Where a step setting is stored** (`step-instance-plugin.ts:999-1301`):
   - fixed value → `sys_variable_value` (`document` `sys_hub_step_instance`, `document_key` = step, `variable` = the step-definition input sys_id, `order` 100). No `sys_element_mapping` row.
   - value containing a pill → `sys_element_mapping` only (`table` `var__m_sys_flow_step_definition_input_<step type>`, `id` = step, `field` = input name, `value` = text with pills). No `sys_variable_value` row.
   - approval rules with pills, and every approval due date → the JSON or rule string goes in `sys_element_mapping.value` **and** an empty `sys_variable_value` row is written (1039-1098, 1183-1219).
   - template value without pills → `sys_variable_value` = `field=value^…^EQ`; with pills → `sys_element_mapping`, no `^EQ`.
4. **Extended inputs** (`sys_hub_step_ext_input`, 612-730): always `internal_type` `string`, `attributes` `element_mapping_provider=…,uiType=string,uiTypeLabel=String` (no `uiUniqueId`), `model` and `model_id` = step, `model_table` `sys_hub_step_instance`, `name` `var__m_sys_hub_step_ext_input_<step>`. A fixed value is a `sys_variable_value` whose `variable` is the **ext input row's sys_id**; a pill value is a `sys_element_mapping` with `table` `var__m_sys_hub_step_ext_input_<step>`. With no value an empty `sys_variable_value` is still written.
5. **Extended outputs** (`sys_hub_step_ext_output`, 732-830): `attributes` `element_mapping_provider=…,uiType=<type>,uiTypeLabel=<label>`; an object or array output is `internal_type` `string`, `max_length` 65000 with the complex-object attributes (`co_type_name`, `uiType` `object` or `array.<type>`, and for arrays `child_name`, `child_label`, `child_type`, `child_type_label`, `child_maxsize`, `child_hint`, `child_uiUniqueId`, `max_rows`, `child_defaultValue`; `complex-objects.ts:595-628`).
6. **Action outputs of object or array type** also get a `sys_variable_value` on the action: `document` = the action table, `document_key` = the action, `variable` = the output row's sys_id, `name` = the output name, `order` = index + 1, `value` = `{"version":"1.0","complexObject":{…},"complexObjectSchema":{…},"serializationFormat":"JSON"}` (`flow-io-to-record.ts:146-160, 464-488`; `complex-objects.ts:546-586`). For an array `complexObject` is `{"name$":"<co name>","$COCollectionField":[]}`; for an object each field is `{"$cv":{"$c":"java.lang.<Type>","$v":""}}`.
7. **Error evaluation** (`flow-action-definition-plugin.ts:2602-2691`): one `sys_hub_action_status_metadata` (`action_type_id`), then one `sys_hub_status_condition` per rule with `action_status_metadata_id`, `label`, `condition` (an encoded condition with pills, typically on `{{step[<cid>].__step_status__.code}}`), `dont_treat_as_error` (boolean), `order` (from 1) and `status`. `status` is the `FDACTIONSTATUS` JSON `{"version":"1.0","complexObject":{"code":{"$cv":{"$c":"java.lang.String","$v":"<code>"}},"message":{"$cv":{"$c":"java.lang.String","$v":"<message>"}}},"complexObjectSchema":{…},"serializationFormat":"JSON"}`; when code or message is a pill, `$v` is `""` and the pill goes into that field's facet as `"mapped":"{\"code\":\"{{…}}\"}"` (otherwise `"mapped":"{}"`) (1504-1543). With error evaluation present the `__action_status__` row in `sys_element_mapping` has `value` = that JSON with empty code and message (2680-2689); the prompt (L2311) shows it empty and has only the delete for `sys_hub_status_condition` (L2283).
8. **Step status pill.** Every step exposes `{{step[<cid>].__step_status__}}` (object with `code`, `message`; built-in `FDSTEPSTATUS`). The SDK adds a `label_cache` entry for it for every step: `{"name":"{{step[<cid>].__step_status__}}","label":"step➛<step label>➛Step Status","type":"step","ref":"","reference_display":"","base_type":"object","parent_table_name":"","column_name":"","choices":null,"attributes":{}}` (`flow-action-definition-plugin.ts:737-753`). It also writes one `{{action.<input>}}` entry for **every** input, used or not (688-713), and a dot-walked action pill gets `parent_table_name` = the input and `column_name` = the last segment (715-735).
9. **Action output mapping.** One `sys_element_mapping` per assigned output: `table` `var__m_sys_hub_action_output_<action>`, `id` = action, `field` = output name, `value` = pill or text (2587-2596). The SDK requires every declared output to be assigned and non-empty (2527-2548).
10. **Pill type detection inside an action:** inside `Action(...)` an input pill is `{{action.<name>}}`; anywhere else it is `{{subflow.<name>}}` (`plugin/plugins/flow-data-pill-plugin.ts:94-100`).

### G. Approval rules (`plugin/utils/approval-rules-processor.ts` vs prompt L1577-1589)

`plugin/plugins/approval-rules-plugin.ts` only wraps `wfa.approvalRules(...)` and `wfa.approvalDueDate(...)`; the string is built in `approval-rules-processor.ts:18-135`. Grammar as generated:

```
rules      := ruleSet ( "Or" ruleSet )*            (an empty rule list is the string "Approves")
ruleSet    := action rule ( "&" rule )*
action     := "Approves" | "Rejects" | "ApprovesRejects"
rule       := condition ( "|" condition )*
condition  := type "M"                              (manual; no user or group lists)
            | type [ "U[" pill ("," pill)* "]" ] [ "G[" pill ("," pill)* "]" ]
type       := "Any" | "All" | "Res" | <n> "#" | <n> "%"
pill       := "{{static.<sys_id>}}" | any other "{{…}}" pill, kept as written
```

What the prompt's table lacks: `&` (all rules in a set must pass), `<n>#` (a fixed count of approvals, for example `Approves2#U[…]`), `Res` (everyone has responded and anyone approved or rejected), the bare `Approves` for an empty rule list, and the real meaning of `M` (Disagreement 12). The parser splits on the literal text `Or` (154), so `Or` cannot appear inside a rule. Every form in the prompt's table is valid under this grammar.

### H. Inline scripts and pill transforms

1. **Inline script on an input** (`plugin/utils/flow-shapes.ts:182-197`): the entry is `{"id":"","name":"<input>","value":"","displayValue":"","children":[],"scriptActive":true,"script":{"<input>":{"scriptActive":true,"script":"<code>"}}}`. There is no `parameter` key. The same shape is used in action `values`, `subflow_inputs` and logic `inputs`/`variables`/`outputsToAssign` (`flow-instance-plugin.ts:1023-1052`; `flow-logic-plugin-helpers.ts:1878-1903`). Prompt L2986 has the two key names but not the nesting by input name or the empty `value`.
2. **Script on one field of a template value** (`flow-instance-plugin.ts:1792-1793, 1842-1863, 1628-1639`): the field is written as `<field>=fd-scripted` inside the template string, the entry gets `"scriptActive":true`, and `"script"` is keyed by the **field** name: `{"<field>":{"scriptActive":true,"script":"<code>"}}`. (The SDK's own reader comment at 711-713 expects `scriptActive` false at the top level in this case; it accepts either.)
3. **Inside a custom action step** the same `fd-scripted` placeholder is used and the code goes to a `sys_hub_input_scripts` row: `instance` = step sys_id, `input_name` = the input, `script` = the JSON map `{"<field>":{"scriptActive":true,"script":"<code>"}}` (`step-instance-plugin.ts:1118-1121, 1159-1170, 1285-1296`). Prompt L2213-2218 covers only the escaping.
4. **Where inline scripts are not allowed** (`flow-constants.ts:739-759`): inputs of type `template_value` (as a whole), `dynamic_inputs`, `glide_variables`; and `template_catalog_item`, `catalog_variables`, `ah_table_name`, `catalog_item` on the catalog actions. The script reads flow data through `fd_data` (`docs/api/flow/wfa-flow-logic-api.md:574`).
5. **Data pill transforms are not serialized by the SDK at all.** `sys_hub_pill_compound` is in its unsupported list (`flow-constants.ts:12-23`); a flow that has one is not converted. The SDK source has nothing on the compound's format.
6. **Type and metadata suffixes are build-time only.** Internally the SDK writes pills as `{{name|type|meta:<parent table>:<column>:<reference>}}` (`plugin/utils/data-pill-shapes.ts:64-75`) and strips everything from the first `|` before the blob is written (`label-cache-processor.ts:32, 603-607`), copying the parts into `label_cache` (`type`/`base_type`, `parent_table_name`, `column_name`, `reference`). The probe's stored blobs contain no `|`. The SDK's reader does strip a `|…` suffix if it meets one (`pill-string-parser.ts:67-72`).

---

## In the prompt, not in the SDK

Listed without judgement. These are things the prompt tells the model to write, or knows, that the plugin never writes or holds.

1. All `action_type_parent` ids (Section 5.2) and `sys_hub_action_instance_v2.compiled_snapshot` (L491).
2. `sys_hub_flow_logic_instance_v2.block` (L556, L589), and the empty `attributes`, `decision_table`, `display_text`, `workflow_reference` elements on logic rows.
3. Every input parameter id for triggers and for If, Else If, For Each and Do until (Sections 7.4, 7.5.1 to 7.5.6): the SDK writes `"id":""` and `"parameter":{}` for those. It holds parameter ids only for Wait for a duration.
4. Full `parameter` objects, `fParameters`, `fSequence`, `fromTemplate`, `triggerInstanceSysId` values (the SDK writes `""`), and the snapshot-section shapes (Section 7.0, Appendices A and B).
5. Real `order` values on trigger entries (1, 10, 101, 200): the SDK writes 100 for every entry.
6. `extended_operators` on the Updated trigger's condition (L1683).
7. Recurrence trigger (`7b3308f67fd21210a652b9277c8665f0`) and `timer_type` values.
8. Logic definitions Make a decision, Get Flow Outputs, Call a Workflow, Dynamic Flow (L1045-1049).
9. REST and JSON Parser step types and all REST step setting ids (Section 10.0.3).
10. The snapshot section with mirrored instance rows, the final `UPDATE` of `latest_snapshot`, and the fixed deletes for tables with no rows (`sys_translated_text`, `sys_variable_value`, `sys_trigger_runner_mapping`, `sys_hub_flow_stage`, `sys_hub_pill_compound`, plans, `sys_choice`).
11. In custom actions: `sys_variable_value` rows on the action for `__action_status__` and `__dont_treat_as_error__`, the empty `sys_element_mapping` rows for fixed settings and for `application`/`script`, `sys_hub_action_plan` delete, `ih_action`, `pre_compiled`, `action_status`, `action_template`.
12. Step-output `label_cache` labels of the form `<n> - <Action name>➛<Output label>` (the SDK writes the raw path).
13. `sys_flow_cat_variable_model` handling (Section 3.15); the SDK only lists it as a related table.
14. All import, clash and update-set-log rules (Sections 0, 0.2, 1, 13), which are outside what a build tool does.

---

## Checked and consistent

One line each. "Same" means the literals match.

1. Logic definition ids: all 14 ids in the SDK map, plus Parallel Branch and Catch, equal prompt Section 5.3; the prompt's Go back to id equals the SDK's commented-out one.
2. Wait for a duration: seven input names, parameter ids and order are the same on both sides.
3. All ten action ids in prompt Section 5.2 and all nine trigger ids the SDK has from Section 5.1 match, with the same `trigger_type` keys and names.
4. Script step type id and its `script` and `application` variable ids match.
5. Create Record: inputs `table_name` (mandatory), `values` (mandatory, template value, max 16000000, depends on `table_name`); outputs `record`, `table_name`. Same.
6. Update Record: inputs `record`, `table_name`, `values`, all mandatory; `record` max 40; outputs `record`, `table_name`. Same.
7. Look Up Record: six inputs with the same names once the SDK's `dont_fail_flow_on_error` is mapped to `__snc_dont_fail_on_error` (section D item 6), none mandatory, `sort_type` default `sort_asc`, `if_multiple_records_are_found_action` default `use_first_record` with labels "Return only the first record" and "Fail the step"; outputs `Record`, `Table`, `status`, `error_message` with the same capitals. Same.
8. Look Up Records: five inputs, `max_results` default 1000; outputs `Records`, `Count`, `Table`. Same.
9. Send Email: eight inputs, `ah_to` and `ah_subject` mandatory, `watermark_email` default true, `ah_body` html max 65536, the three address fields and subject max 8000. Same.
10. Send Notification: `record`, `table_name`, `notification` (mandatory, reference `sysevent_email_action`); no outputs. Same.
11. Fire Event: `event_name` (mandatory, reference `sysevent_register`), `record` (mandatory), `table`, `parm1`, `parm2`; no outputs. Same.
12. Ask For Approval: seven inputs with the same names and types (`approval_rules`, `schedule_date_time`, `field_name`), `record` and `approval_conditions` mandatory; output `approval_state`. Same.
13. Approval due date default JSON `{"action":"none","date_type":"actual","date":"{}","duration":1,"duration_type":"days","schedule":"","schedule_label":""}`: identical to prompt L1589.
14. Approval users and groups as `{{static.<sys_id>}}`, other pills kept as written, comma separated: same.
15. Get Catalog Variables and Create Catalog Task input names, the `<sys_id>:item_option_new` list, and the output name `Catalog Task`: same.
16. Record trigger inputs: the seven names, types, defaults `false` / `both` / `any` / `any`, choice values and labels, and `condition` depending on `table` with attributes `wants_to_add_conditions` and `modelDependent=trigger_inputs`: same. `trigger_strategy` on Updated and Created or Updated only, default `once`, four choices with the same labels and hint: same.
17. Daily (`time`), Weekly (`day_of_week`, `time`), Monthly (`day_of_month` with `integer_type=day_of_month`, `time`), Repeat (`repeat`), Run Once (`run_in`): names, types and mandatory flags the same.
18. Service Catalog trigger: single input `run_flow_in`; pills `request_item` and `table_name`. Same apart from Disagreement 13.
19. Compact trigger entry shape in prompt L132 equals `flow-trigger-instance-plugin.ts:377-412` key for key.
20. Compact action entry `{"name","value","displayValue","scriptActive":false,"parameter":{"type"}}` and compact logic entry in prompt L132 equal the source and the probe.
21. Else, End Flow, Parallel, Parallel Branch and Try carry the all-empty six-key object: same.
22. Nesting through `parent_ui_id`; Catch has the Try's `parent_ui_id` and `connected_to` = the Try; Catch comes after the try body: same.
23. Composite order `<n-1>➛<n>` on the first row inside a parallel branch: same rule.
24. `flow_variables_assigned` and `outputs_assigned` as comma-joined element names: same.
25. For Each item pill `{{<for each ui_id>.item…}}`, action pills `{{action.x}}`, step pills `{{step[<cid>].x}}`, subflow input `{{subflow.x}}`, flow variable `{{flow_variable.x}}`: same.
26. Action `label_cache` entry shape (`name` with braces, `label` `action➛…` / `step➛<label>➛…`, `type`, `ref`, `reference_display`, `base_type`, `parent_table_name`, `column_name`, `choices` null, `attributes` {}): equal to prompt L2343.
27. `sys_element_mapping` table names `var__m_sys_flow_step_definition_input_<step type>`, `var__m_sys_hub_step_ext_input_<step>`, `var__m_sys_hub_step_ext_output_<step>`, `var__m_sys_hub_action_output_<action>` and `id` = the owner: same.
28. Input, output and variable rows: `model`, `model_id`, `model_table`, `name` = `var__m_<table>_<owner sys_id>`; complex-object variables `internal_type` `string`, `max_length` 65000: same.
29. Stage states default labels: same five values.
30. Activation call: `POST api/now/wfa_fluent/activate_flows`, body `{"flows":[…],"actions":[…]}` with `{sys_id, active:"", state:""}` entries, query `sysparm_transaction_scope`, 422 still carries the result body, 400 "does not represent any resource" when the endpoint is missing (`plugin/post-install.ts:41-72, 105-116`): same as prompt L2721-2733.
