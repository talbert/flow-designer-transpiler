"""Build flow_designer_prompt20261119.md from 20261015 + the import tests run on dev435256 (Brazil Patch 1). Local file edit only."""
import pathlib, json, copy
D = pathlib.Path(__file__).resolve().parent.parent.parent
V = D / "verification"
t = (D / "archive" / "flow_designer_prompt20261015.md").read_text()
n = 0
def rep(old, new, count=1):
    global t, n
    c = t.count(old)
    assert c == count, f"expected {count}, got {c}: {old[:90]!r}"
    t = t.replace(old, new); n += 1
def cut(start, end, new):
    """Replace from the line starting with `start` up to (not including) the line starting with `end`."""
    global t, n
    i0 = t.index(start); i1 = t.index(end, i0 + len(start))
    t = t[:i0] + new + t[i1:]; n += 1
J = lambda o: json.dumps(o, separators=(",", ":"), ensure_ascii=False)

# ---------------- header
rep("The sys_ids and parameter IDs in Sections 5 and 7 are verified on Zurich (Patch 10), Australia (Patch 2) and Brazil (Patch 1).",
    "The sys_ids and parameter IDs in Sections 5 and 7 are verified on Zurich (Patch 10), Australia (Patch 2) and Brazil (Patch 1). Section 0 lists the rules proven by importing generated XML into a Brazil Patch 1 instance.")
rep("- `[TARGET_VERIFY]` -- Must be checked on the target instance before trusting.",
    "- `[IMPORT_TESTED]` -- XML generated from this rule was imported, opened in Workflow Studio and activated on Brazil Patch 1 (2026-11-19), and the platform's re-export was compared with what was sent.\n- `[TARGET_VERIFY]` -- Must be checked on the target instance before trusting.")

SECTION0 = r'''## 0. IMPORT-TESTED RULES `[IMPORT_TESTED]`

These rules come from seven generated flows and one generated subflow that were imported, opened and activated on Brazil Patch 1. **Where any later section disagrees with this section, this section wins.**

**What was tested and passed:** record-created trigger, daily trigger, Service Catalog trigger; Look Up Record, Look Up Records, Create Record, Update Record, Send Email, Fire Event; If, Else If, Else, End Flow, For Each, Do the following until, Set Flow Variables, Assign Subflow Outputs; a flow variable; a subflow with one input and one output; a flow calling that subflow; data pills from the trigger, from steps, from a For Each item, from a flow variable and from a subflow input.

**What failed, and what it proves:**

1. **`version` must be `2`.** With `1` the flow commits but opens empty.
2. **Blobs need their full structure.** Two flows with reduced blob entries (only `name` + `value`; or `id`, `name`, `value`, `displayValue` and a 4-key `parameter`) committed cleanly but Workflow Studio showed **"Corrupted flow. This flow can't be opened."** Every blob entry must carry the complete entry shape and a complete `parameter` object (Section 7.0).
3. **A `delete_multiple` for a table that does not exist** logs an error at commit. Use only the tables in Section 2.1.
4. **`label_cache` is not rebuilt by activation.** With `[]`, a pill in a condition renders blank. With entries (Section 7.10), it renders with its label.

**What to emit and what to leave to the platform:**

| Emit | Do not emit (activation or Workflow Studio builds it) |
|---|---|
| `sys_hub_flow` (inactive, `version` 2) and its snapshot | `sys_flow_record_trigger`, `sys_flow_timer_trigger`, `sys_flow_catalog_trigger` |
| `sys_hub_trigger_instance_v2` with a full `trigger_inputs` blob | `sys_trigger_runner_mapping`, `sys_flow_trigger_auto_script` |
| Action, subflow and logic instances with full blobs | `sys_flow_trigger_plan`, `sys_flow_subflow_plan` |
| Flow inputs, outputs, variables and their `sys_documentation` | `sys_hub_flow_version` |
| `label_cache` entries for every pill used | The two automatic flow inputs of a record or catalog trigger (`current`, `table_name`) |

Activation built every item in the right column from the trigger blob: the record trigger (table, condition, run options), the timer trigger (`timer_type` 11 and the time, converted from the activating user's time zone to UTC), and the catalog trigger.

**Rules for ids inside blobs:**

- Flow-section rows and snapshot-section rows have different `sys_id`s and the same `ui_id`s.
- **Blobs in the snapshot section still point at flow-section ids**: `triggerInstanceSysId`, `flowLogicInstanceSysId`, flow variable ids and subflow output ids are the flow-section values in both sections.
- A logic row and its snapshot mirror carry the **same** `block` value.
- `sys_hub_sub_flow_instance_v2.subflow` is the sys_id of the called subflow's **master snapshot** (`sys_hub_flow_snapshot`), not of its `sys_hub_flow` record. Each `subflow_inputs` entry `id` and `parameter.id` is the sys_id of that snapshot's `sys_hub_flow_input` row.

**The platform normalizes on activation.** It renumbers `order` to 1, 2, 3…, rewrites `block` ids, fills `hint`/`help`/`defaultDisplayValue` and choice lists in parameters, and reorders `label_cache`. None of these need to be exact in generated XML.

---

'''
rep("---\n\n## 1. OUTER XML WRAPPER", "---\n\n" + SECTION0 + "## 1. OUTER XML WRAPPER")

# ---------------- 2.1 skeleton: platform order
rep("""  <!-- 2. CLEAN EXISTING VARIABLE VALUES -->
  <sys_variable_value action="delete_multiple" query="document_key={{FLOW_SYS_ID}}"/>""",
    """  <!-- 2. CLEAN TRANSLATIONS AND VARIABLE VALUES -->
  <sys_translated_text action="delete_multiple" query="documentkey={{FLOW_SYS_ID}}"/>
  <sys_variable_value action="delete_multiple" query="document_key={{FLOW_SYS_ID}}"/>""")
rep("""  <!-- 3. TRIGGER (catalog, record, scheduled) -->
  <!-- catalog example: -->
  <sys_flow_catalog_trigger action="INSERT_OR_UPDATE">...</sys_flow_catalog_trigger>
  <!-- record-triggered: emit NO trigger record; Activate creates sys_flow_record_trigger (Section 3.1) -->
  <!-- scheduled/timer example (see Section 3.13; [TARGET_VERIFY], not yet seen in a platform unload): -->
  <!-- <sys_flow_timer_trigger action="INSERT_OR_UPDATE">...</sys_flow_timer_trigger> -->
""",
    """  <!-- 3. TRIGGER RECORD: emit none. Activation creates sys_flow_record_trigger / sys_flow_timer_trigger /
       sys_flow_catalog_trigger from the trigger_inputs blob (Section 0). -->
""")
rep("""  <sys_hub_action_instance_v2 action="INSERT_OR_UPDATE">...</sys_hub_action_instance_v2>
  <!-- Repeat for each action step -->""",
    """  <sys_hub_action_instance_v2 action="INSERT_OR_UPDATE">...</sys_hub_action_instance_v2>
  <sys_hub_alias_mapping action="delete_multiple" query="source_id={{STEP_SYS_ID}}"/>
  <!-- Repeat the insert + alias delete pair for each action step -->""")
rep("""  <!-- Always emit this delete_multiple to clean up any pre-existing logic on the target, even if the new flow has no logic blocks -->
  <sys_hub_flow_logic_instance_v2 action="delete_multiple" query="flow={{FLOW_SYS_ID}}"/>""",
    """  <!-- Always emit this delete_multiple, even if the new flow has no logic blocks -->
  <sys_hub_flow_logic_instance_v2 action="delete_multiple" query="flow={{FLOW_SYS_ID}}^sys_idNOT IN{{LOGIC_IDS_CSV}}"/>
  <sys_hub_flow_logic_instance_v2 action="INSERT_OR_UPDATE">...</sys_hub_flow_logic_instance_v2>""")
rep("""  <!-- 20. PLAN CLEANUP — delete only; activation builds the plans (Section 3.10) -->
  <sys_flow_trigger_plan action="delete_multiple" query="plan_id={{FLOW_SYS_ID}}"/>""",
    """  <!-- 20. PLAN CLEANUP — delete only; activation builds the plans (Section 3.10) -->
  <!-- For a subflow (type=subflow) omit the sys_trigger_runner_mapping delete in item 4. -->
  <sys_flow_trigger_plan action="delete_multiple" query="plan_id={{FLOW_SYS_ID}}"/>""")

# ---------------- 3.1 / 3.9 flow + snapshot templates
rep("  <sys_customer_update>true</sys_customer_update>\n  <sys_domain>global</sys_domain>\n  <sys_domain_path/>\n  <sys_id>{{FLOW_SYS_ID}}</sys_id>",
    "  <sys_domain>global</sys_domain>\n  <sys_domain_path>/</sys_domain_path>\n  <sys_id>{{FLOW_SYS_ID}}</sys_id>")
rep("  <sys_customer_update>true</sys_customer_update>\n  <sys_domain>global</sys_domain>\n  <sys_domain_path/>\n  <sys_id>{{SNAPSHOT_SYS_ID}}</sys_id>",
    "  <sys_domain>global</sys_domain>\n  <sys_domain_path>/</sys_domain_path>\n  <sys_id>{{SNAPSHOT_SYS_ID}}</sys_id>")
rep("""  <sys_policy/>
  <sys_replace_on_upgrade>false</sys_replace_on_upgrade>
  <sys_scope display_value="Global">global</sys_scope>
  <sys_update_name>sys_hub_flow_{{FLOW_SYS_ID}}</sys_update_name>""",
    """  <sys_policy/>
  <sys_scope display_value="Global">global</sys_scope>
  <sys_update_name>sys_hub_flow_{{FLOW_SYS_ID}}</sys_update_name>""")
rep("""  <sys_policy/>
  <sys_replace_on_upgrade>false</sys_replace_on_upgrade>
  <sys_scope display_value="Global">global</sys_scope>
  <sys_update_name/>
  <sys_updated_by>{{CREATOR}}</sys_updated_by>
  <sys_updated_on>{{TIMESTAMP}}</sys_updated_on>
  <type>flow</type>
  <version>2</version>""",
    """  <sys_policy/>
  <sys_scope display_value="Global">global</sys_scope>
  <sys_update_name/>
  <sys_updated_by>{{CREATOR}}</sys_updated_by>
  <sys_updated_on>{{TIMESTAMP}}</sys_updated_on>
  <type>flow</type>
  <version>2</version>""")
rep("  <label_cache>[]</label_cache>", "  <label_cache>{{LABEL_CACHE_JSON}}</label_cache>", 2)
rep("**Note on `sys_customer_update`:** Set to `true` for all records generated by this prompt. This marks them as customer customizations, which protects them from being overwritten during ServiceNow family upgrades. Setting `false` marks a record as out-of-box platform content -- the platform may overwrite it during upgrades. Only use `false` if you are intentionally creating records that should be treated as platform-managed (rare for customer-generated flows).",
    "**Note on `sys_customer_update` and `sys_replace_on_upgrade`:** `[PLATFORM_EXPORT]` Do not emit them. The platform's own export of a flow has neither element on `sys_hub_flow`, `sys_hub_flow_snapshot` or any child record.\n\n**Note on `type`:** `flow` or `subflow`. A subflow has no trigger instance, uses `run_as` `user` in live data, and is called through its master snapshot (Section 3.4).")
i0 = t.index("**Note on `label_cache`:**"); i1 = t.index("\n", i0)
t = t[:i0] + "**Note on `label_cache`:** `[IMPORT_TESTED]` A JSON array with one entry for each data pill the flow uses. Flow Designer reads it to draw pill labels. **Generate it** (Section 7.10); activation does not rebuild it, and with `[]` pills in conditions render blank. Put the same array on the flow and on the snapshot." + t[i1:]; n += 1
rep("Given this, use `[]` for `label_cache` and set `compiled_snapshot` equal to `action_type` -- both are regenerated on republish.",
    "Set `compiled_snapshot` equal to `action_type`. Generate `label_cache` (Section 7.10), set the snapshot's `description` equal to the flow's, and use the snapshot-section blob shape (Section 7.0).")
rep("| Service Catalog | sys_id of the `sys_flow_catalog_trigger` record (Section 3.11) |",
    "| Service Catalog | sys_id of the `sys_flow_catalog_trigger` record (Section 3.11), set by activation |")
rep("For service catalog and other trigger types, use Strategy A (Section 7.8).",
    "For the Service Catalog trigger see Section 7.4.5. For other trigger types, use Strategy A (Section 7.8).")
rep("For OOB action types (Create Record, Update Record, Look Up Record, Look Up Records), generate this blob using the templates in Section 7.3. For custom actions or spokes, use Strategy A (Section 7.8).",
    "For the OOB action types in Appendix A, generate this blob from the parameter objects there. For any other action (custom or spoke), build the parameter objects from the action's input definitions with the rule in Section 7.0; if the definitions are not available, use Strategy A (Section 7.8).")

# ---------------- 3.4 subflow instance
rep("""  <parent_ui_id/>
  <subflow display_value="{{SUBFLOW_NAME}}">{{SUBFLOW_SYS_ID}}</subflow>""",
    """  <parent_ui_id/>
  <show_stages>false</show_stages>
  <subflow display_value="{{SUBFLOW_NAME}}">{{SUBFLOW_MASTER_SNAPSHOT_SYS_ID}}</subflow>""")
rep("### 3.5 `sys_hub_flow_logic_instance_v2`",
    "`[IMPORT_TESTED]` **`subflow` holds the called subflow's master snapshot sys_id** (`sys_hub_flow.master_snapshot` of the subflow), not the subflow's own sys_id; 52 of 53 live rows do this. When the subflow is generated in the same update set, use the snapshot sys_id you generated for it. When it already exists on the target, the user must supply its `master_snapshot` and the sys_ids of that snapshot's `sys_hub_flow_input` rows (Section 7.6).\n\n### 3.5 `sys_hub_flow_logic_instance_v2`")
rep("- **`connected_to`** `[OBSERVED]` — Set on **Else** and **Else If** blocks to the `ui_id` of the If they belong to (190 of 190 Else blocks on Brazil Patch 1). Empty on If, For Each and End. An Else's `parent_ui_id` is the block that encloses the whole If group (empty at top level), not the If itself.",
    "- **`connected_to`** `[IMPORT_TESTED]` — Set on **Else** and **Else If** blocks to the `ui_id` of the **If** that opens the group (80 of 80 Else and 67 of 67 Else If rows in live flows point at the If, never at a preceding Else If). Empty on every other logic type. An Else or Else If has the same `parent_ui_id` as its If.")
rep("Emit a fresh unique 32-char GUID per logic instance; because republishing",
    "Emit a fresh unique 32-char GUID per logic instance, and reuse the same value on that instance's snapshot mirror; because republishing")

# ---------------- 3.11 catalog trigger
cut("### 3.11 `sys_flow_catalog_trigger`", "### 3.12 `sys_hub_flow_version`", """### 3.11 `sys_flow_catalog_trigger` (Catalog/Service Catalog Trigger)

`[IMPORT_TESTED]` **Do not emit this record.** Emit the `sys_hub_trigger_instance_v2` with the Service Catalog trigger definition and the `trigger_inputs` blob in Section 7.4.5. Activation creates the `sys_flow_catalog_trigger` record and sets `remote_trigger_id`.

`[OBSERVED]` The table's fields are `active`, `catalog_item`, `name`, `published_version`, `run_flow_in` and `trigger_definition`, plus system fields. It has no `cat_item`, `condition`, `flow` or `order` field. The link from a catalog item to the flow is set on the catalog item (its Flow field), not on this record; tell the user in `CONFIGURATION_NOTES` to set it.

""")

# ---------------- 3.13 timer trigger
rep("For flows triggered on a schedule (daily, weekly, monthly, repeat interval, or one-time):",
    "`[IMPORT_TESTED]` **Do not emit this record.** Emit the `sys_hub_trigger_instance_v2` with the schedule's trigger definition and the `trigger_inputs` blob in Section 7.4.4. Activation creates the `sys_flow_timer_trigger` record and a `sys_flow_trigger_auto_script` record, and sets `remote_trigger_id`. The template below documents what activation writes; it is reference only.\n\nFor flows triggered on a schedule (daily, weekly, monthly, repeat interval, or one-time):")
rep("**Important:** The `time` field in `sys_flow_timer_trigger` is stored in **UTC**.",
    "`[IMPORT_TESTED]` The `time` value in the **trigger blob** is in the time zone of the user who activates the flow: a blob value of `03:15:00` activated by a US/Pacific user produced `sys_flow_timer_trigger.time` = `11:15:00`. State the intended local time in `CONFIGURATION_NOTES`.\n\n**Important:** The `time` field in `sys_flow_timer_trigger` is stored in **UTC**.")

# ---------------- 7.2.1 pills
rep("| `{{trigger.current.<field>}}` | Field from the trigger record (record-triggered flows) | `{{trigger.current.sys_id}}` |\n", "")
rep("| `{{trigger.current.<dotwalked>}}` | Dot-walked reference from trigger record | `{{trigger.current.assignment_group.manager.email}}` |\n", "")
rep("| `{{<trigger_display>_<N>.current.<field>}}` | Alternative trigger pill format using trigger display name and sequence number | `{{Created_1.current.short_description}}` |",
    "| `{{<trigger name>_1.current}}` | The trigger record (record-triggered flows) | `{{Created_1.current}}` |\n| `{{<trigger name>_1.current.<field>}}` | Field or dot-walked field of the trigger record | `{{Updated_1.current.assignment_group.manager.email}}` |")
rep("| `{{flow_var.<variable_name>}}` | Flow scratchpad variable | `{{flow_var.counter}}` |",
    "| `{{flow_variable.<variable_name>}}` | Flow variable | `{{flow_variable.counter}}` |")
rep("{{flow_var.counter}}>10", "{{flow_variable.counter}}>10")
rep("**Pill usage in encoded query conditions:**",
    "`[IMPORT_TESTED]` **Trigger pills start with the trigger instance's `name` plus `_1`**: `Created_1`, `Updated_1`, `Created or Updated_1`, `Service Catalog_1`. In live flows this form appears 245 times and `{{trigger.…}}` 5 times; use the name form. **Flow variables are `{{flow_variable.<name>}}`** (109 live uses); `{{flow_var.…}}` does not occur. A For Each item is `{{<for each ui_id>.item}}` or `{{<for each ui_id>.item.<field>}}`. In every example below, read `{{trigger.current…}}` as `{{<trigger name>_1.current…}}`.\n\n**Pill usage in encoded query conditions:**")

# ---------------- 7.0 new + 7.3 pointers
SEC70 = r'''### 7.0 Blob Shape Rules `[IMPORT_TESTED]`

**Every entry must be complete.** A blob entry with a reduced `parameter` object, or with none, makes Workflow Studio report the flow as corrupted (Section 0). Emit one entry for **every** input the action, trigger or logic definition has, including inputs you leave empty (`"value": ""`).

**Entry shape for action `values` and `subflow_inputs`:**

```json
{"id": "<input sys_id>", "name": "<input element>", "value": "<value or pill>", "displayValue": "<label of the value, or the value>",
 "children": [], "parameter": { ...parameter object... }, "scriptActive": false}
```

**Two parameter shapes, one per section:**

| Section | Shape | Keys |
|---|---|---|
| Flow section (rows whose `flow` is the `sys_hub_flow` sys_id) | compact | `type_label`; `choices` and `defaultChoices` only on choice inputs |
| Snapshot section (rows whose `flow` is the snapshot sys_id) | full | `typeLabel` instead of `type_label`; always `choices`, `defaultChoices`, `fDataStructure` (`""`), `sysClassName` (`""`) |

Both shapes carry `help` and `reference_display`. To make the full shape from the compact one: rename `type_label` to `typeLabel` and add `"choices": []`, `"defaultChoices": []`, `"fDataStructure": ""`, `"sysClassName": ""` where they are missing. The platform accepted the same compact objects in both sections for logic blobs, then rewrote the snapshot side to the full shape.

**Building a parameter object for any action** `[OBSERVED]`. The object is a projection of the input's definition row (`sys_hub_action_input` for actions, `sys_hub_flow_input` for subflow inputs, `sys_hub_flow_variable` for flow variables). Checked against 522 entries in live flows: no value disagreed.

| Parameter key | Definition field |
|---|---|
| `id` | `sys_id` |
| `name` | `element` |
| `label` | `label` |
| `type` | `internal_type` |
| `type_label` | label of the internal type (for example `String`, `Table Name`, `Choice`, `True/False`) |
| `order` | `order` (integer) |
| `mandatory`, `readOnly` | `mandatory`, `read_only` (booleans) |
| `maxsize` | `max_length` (integer) |
| `reference`, `reference_display` | `reference`, label of that table |
| `hint`, `help` | `hint`, `help` |
| `choiceOption`, `table`, `columnName` | `choice`, `choice_table`, `choice_field` |
| `defaultValue` | `default_value` |
| `ref_qual`, `dependent_on`, `use_dependent` | `reference_qual`, `dependent_on_field`, `use_dependent_field` |
| `attributes` | the `attributes` string (`k=v,k=v`) as a JSON object |
| `children`, `extended`, `fShowReferenceFinder`, `local` | `[]`, `false`, `false`, `false` |
| `choices`, `defaultChoices` | for choice inputs: `[{"label","value","order"}]` from the input's choice list |

Appendix A has ready-made compact objects for the tested OOB actions. For a custom or spoke action, ask the user for the action's input definitions (a list export of `sys_hub_action_input` filtered by `model=<action type sys_id>`) and apply the table.

'''
rep("### 7.1 Blob Encoding", SEC70 + "### 7.1 Blob Encoding")
rep("**Template:** Same array structure as Create/Update Record. The `parameter` blocks use the same schema",
    "**Template:** `[IMPORT_TESTED]` Use the six parameter objects in Appendix A. `displayValue` for `if_multiple_records_are_found_action` = `use_first_record` is `Return only the first record`. Older note: the `parameter` blocks use the same schema")
rep("**Template:** Same array structure. The `parameter` blocks mirror Look Up Record with the IDs above substituted.",
    "**Template:** `[IMPORT_TESTED]` Use the five parameter objects in Appendix A.")
rep("**Template:** Same array structure as other action types. The `ah_to`, `ah_cc`, and `ah_bcc` fields",
    "**Template:** `[IMPORT_TESTED]` Use the eight parameter objects in Appendix A. The `ah_to`, `ah_cc`, and `ah_bcc` fields")
rep("**Template:** Same array structure. Maps directly from `gs.eventQueue(event_name, record, parm1, parm2)`.",
    "**Template:** `[IMPORT_TESTED]` Use the five parameter objects in Appendix A. `event_name` takes the sys_id of the `sysevent_register` row as `value` and the event name as `displayValue`. Maps directly from `gs.eventQueue(event_name, record, parm1, parm2)`.")

# ---------------- 7.4 trigger entries
rep("#### 7.4.4 Scheduled/Timer Triggers",
    "`[IMPORT_TESTED]` **Record trigger entries:** each entry also carries `\"fromTemplate\": false`, `\"triggerInstanceSysId\": \"<flow-section trigger instance sys_id>\"` (the same value in the snapshot copy), and each `choiceList` item carries `\"fSequence\": -1`. Appendix B has the complete seven-entry Record Created blob that passed the import test; Record Updated and Record Created or Updated use the same entry shape with the parameter ids in 7.4.2 and 7.4.3 plus the `trigger_strategy` entry.\n\n#### 7.4.4 Scheduled/Timer Triggers")
cut("Scheduled triggers keep their schedule in the `sys_flow_timer_trigger` record", "### 7.5 Flow Logic `values`", """`[IMPORT_TESTED]` Emit only the trigger instance and its one-entry `trigger_inputs` blob. Activation builds `sys_flow_timer_trigger` from it (Section 3.13).

- **Daily** (definition `89142dc0c32222002841b63b12d3ae8a`, `trigger_type` `daily`, name `Daily`): one entry `time`. Tested: a blob with `"value": "1970-01-01 03:15:00"` rendered as "Daily at 03:15:00" and activated. Full entry in Appendix B.
- **Repeat** (definition `f63f0d94c32222002841b63b12d3aeed`, `trigger_type` `repeat`, name `Repeat`): one entry `repeat`, value like `1970-01-01 00:15:00` for 15 minutes. `[OBSERVED]` Full entry in Appendix B; not import-tested.
- **Weekly, Monthly, Run Once:** no live example exists on a baseline instance. `[TARGET_VERIFY]` Build the entries from the trigger definition's `sys_hub_trigger_input` rows in the Daily entry shape, and say so in `CONFIGURATION_NOTES`.

#### 7.4.5 Service Catalog Trigger (`c43a1011c36813002841b63b12d3ae15`)

`[IMPORT_TESTED]` `trigger_type` `service_catalog`, name `Service Catalog`. One entry, `run_flow_in` (parameter id `6090c72977203300f5bfcfcc78106159`, value `background`). Full entry in Appendix B. Trigger pills are `{{Service Catalog_1.request_item}}` and `{{Service Catalog_1.table_name}}`. Activation creates the `sys_flow_catalog_trigger` record.

""")

# ---------------- 7.5 logic fixes
rep("- `condition`: `9a5f5105c32632002841b63b12d3ae46` (same as If)\n\nThe `parameter` boilerplate blocks are identical to If except for the `id` field in `condition_name`.",
    "- `condition`: `f0af19c1c32632002841b63b12d3aea1` `[IMPORT_TESTED]` (not the If id; last character is `1`)\n\nThe `parameter` boilerplate blocks are identical to If except for the two `id` fields. Set `connected_to` to the opening If's `ui_id`.")
rep("No blob needed. The `values` field is either empty or absent. Else blocks have no condition to configure. Set `connected_to` to the If's `ui_id` (Section 3.5).",
    "`[IMPORT_TESTED]` Use the empty-structure blob shown under End (all six arrays empty); the platform writes that blob for an Else. Set `connected_to` to the If's `ui_id` (Section 3.5).")
rep("- `condition`: uses a different ID from If/Else If (verify from instance if needed)",
    "- `condition`: `d7138f0473031300612c273ffff6a78c` `[IMPORT_TESTED]` (order: 200)\n\nThe steps inside the loop have `parent_ui_id` = the Do Until block's `ui_id`. The `condition_name` parameter has no `use_basic_input` attribute here.")
rep("- The `id` field at entry level is an **empty string** (not a stable OOB ID)",
    "- `[IMPORT_TESTED]` In the flow section, `inputs` entries have **no** `id` key and `variables` entries have `id` = the flow variable's sys_id. In the snapshot section both have `id`. The id is always the **flow-section** `sys_hub_flow_variable` sys_id")
rep("### 7.6 Subflow Instance `subflow_inputs`",
    """#### 7.5.9 Assign Subflow Outputs `[IMPORT_TESTED]`

Used inside a subflow to set its outputs. The `outputsToAssign` array is populated; `inputs` and `variables` are empty. The logic row's `outputs_assigned` field holds a CSV of the output element names.

```json
{"outputsToAssign": [{"flowLogicInstanceSysId": "<flow-section sys_id of this logic row>", "id": "<flow-section sys_hub_flow_output sys_id>",
   "name": "<output element>", "value": "<value or pill>", "displayValue": "<same>", "children": [],
   "parameter": { ...parameter object built from the sys_hub_flow_output row, id = same output sys_id... }, "scriptActive": false}],
 "inputs": [], "variables": [], "decisionTableInputs": [], "dynamicInputs": [], "workflowInputs": []}
```

### 7.6 Subflow Instance `subflow_inputs`""")
rep("**However, parameter IDs are NOT stable.** Unlike OOB action types, subflow input IDs come from the subflow's own `sys_hub_flow_input` records, which are instance-specific. This means the blob cannot be generated from a static template -- the parameter IDs must be looked up from the target subflow's definition on the target instance.\n\n**For subflow instances, use Strategy A** (Section 7.8) and note the intended input mappings in `CONFIGURATION_NOTES`.",
    "`[IMPORT_TESTED]` **The ids are those of the subflow's master snapshot.** Each entry's `id` and `parameter.id` is the sys_id of the `sys_hub_flow_input` row whose `model` is the subflow's master snapshot. The `parameter` object is built from that row (Section 7.0); its `attributes` include `uiType`, `uiTypeLabel`, `element_mapping_provider` and the input's `uiUniqueId`.\n\n- **Subflow generated in the same update set:** you chose those snapshot-section input sys_ids yourself, so generate the blob. This was tested: the caller rendered the subflow step and the subflow's publish dialog listed the caller.\n- **Subflow that already exists on the target:** ask the user for the subflow's `master_snapshot` sys_id and its snapshot inputs (`sys_hub_flow_input` where `model` = that snapshot). Without them, use Strategy A (Section 7.8).")

# ---------------- 7.10 label cache (insert before 7.7)
rep("### 7.7 Blob Generation Capability",
    r'''### 7.10 `label_cache` Entries `[IMPORT_TESTED]`

One entry per distinct pill used anywhere in the flow. The same array goes on `sys_hub_flow` and `sys_hub_flow_snapshot`.

```json
{"name": "<pill text without the braces>", "label": "<label>", "reference": "<table, for a record>", "reference_display": "<table label or field label>",
 "type": "<type>", "base_type": "<type>", "usedInstances": {"<ui_id of a step that uses the pill>": ["<input name>", "..."]},
 "attributes": {"element_mapping_provider": "com.glide.flow_design.action.data.FlowDesignVariableMapper"}}
```

- A pill for a **field** (dot-walked) drops `attributes` and adds `"parent_table_name": "<table that owns the field>", "column_name": "<field>"`.
- A **choice** output adds `"choices": [{"label","value","order"}]`.
- `label` conventions seen in live flows: step output `"<order> - <Action name>➛<Output label>"` (for example `1 - Look Up Record➛User Record`); trigger `"Trigger - Record Created➛Incident Record➛Priority"`; subflow input `"Input➛<Input label>"`; flow variable `"Flow Variables➛<label>"`. The separator is `➛` (U+279B).
- `type` examples: `reference` for a record, `records` for a record list, `string`, `integer`, `choice`.
- The platform rewrites labels and order on activation, so the label text need not be exact; the entry must exist and `name` must match the pill.

### 7.7 Blob Generation Capability''')

# ---------------- 13 / 15
rep("3. **Open the flow in Flow Designer** (`Process Automation > Flow Designer`). If it opens with no trigger and no actions, check `sys_hub_flow.version`; it must be `2` (Section 3.1).",
    "3. **Open the flow in Flow Designer** (`Process Automation > Flow Designer`). If it opens with no trigger and no actions, check `sys_hub_flow.version`; it must be `2` (Section 3.1). If it says **\"Corrupted flow. This flow can't be opened\"**, a blob entry is incomplete (Section 7.0).")
rep("2. **Generate real base64-gzip blobs for OOB action types** using Section 7 templates. For unsupported action types, use Strategy A placeholders (Section 7.8). Never fabricate blob content outside of the documented JSON structures.",
    "2. **Generate real base64-gzip blobs with complete entries** (Section 7.0). An incomplete entry corrupts the flow. Where the input definitions are not known, use Strategy A placeholders (Section 7.8). Never fabricate blob content outside of the documented JSON structures.")
rep("11. **Set `sys_customer_update` to `true`** on `sys_hub_flow` and `sys_hub_flow_snapshot`. Do not emit it on instance records (Section 3.3).",
    "11. **Do not emit `sys_customer_update` or `sys_replace_on_upgrade`** on any record (Section 3.1).")
rep("12. **Do not emit `sys_hub_flow_version`, `sys_flow_record_trigger` or `sys_flow_trigger_plan` records**",
    "12. **Do not emit `sys_hub_flow_version`, `sys_flow_record_trigger`, `sys_flow_timer_trigger`, `sys_flow_catalog_trigger` or plan records**")
rep("16. **Follow the platform.**",
    "16. **Generate `label_cache`** with one entry per pill (Section 7.10).\n17. **Use the live pill forms:** `{{<trigger name>_1.current…}}` and `{{flow_variable.<name>}}` (Section 7.2.1).\n18. **Follow the platform.**")

# ---------------- appendices
cat = json.load(open(V / "fixtures/dev435256/parameter_catalog.json"))
names = {"9d09f99587003300663ca1bb36cb0ba3": "Look Up Record", "43400a1587003300663ca1bb36cb0b4b": "Look Up Records", "2de05916c31332002841b63b12d3aee1": "Create Record",
         "f9d01dd2c31332002841b63b12d3aea1": "Update Record", "c1806bf4a70323008299b39f087901cb": "Send Email", "80a30edeff30311077a95dac793bf19b": "Fire Event"}
A = ["\n---\n\n## APPENDIX A. Compact Parameter Objects for Tested OOB Actions `[IMPORT_TESTED]`\n",
     "Read from the action input definitions on Brazil Patch 1 and used in the import tests. One line per input, in input order. These are the **compact** (flow-section) objects; make the snapshot-section shape with the rule in Section 7.0. The platform fills `hint`, `help` and `defaultDisplayValue` itself on activation.\n"]
for key, ps in cat.items():
    sid = key.split(":")[1]
    A.append(f"\n**{names[sid]}** (`{sid}`)\n\n```json\n" + "\n".join(J(p) for p in ps) + "\n```\n")
trig = json.load(open(V / "fixtures/zurich/blobs/Record_Created_trigger_inputs.json"))["decoded"]
for e in trig:
    e["triggerInstanceSysId"] = "{{FLOW_SECTION_TRIGGER_INSTANCE_SYS_ID}}"; e["fromTemplate"] = False
    for c in e.get("choiceList") or []: c.setdefault("fSequence", -1)
    if e["name"] == "table": e["value"], e["displayValue"] = "{{TABLE_NAME}}", "{{TABLE_LABEL}}"
    if e["name"] == "condition": e["value"] = "{{ENCODED_QUERY}}"; e["displayValue"] = "{{ENCODED_QUERY}}"
tc = json.load(open(V / "fixtures/dev435256/triggers_timer_catalog.json"))
def trig_entries(label):
    es = copy.deepcopy(tc[label]["trigger_instance"]["trigger_inputs__decoded"])
    for e in es:
        if "triggerInstanceSysId" in e: e["triggerInstanceSysId"] = "{{FLOW_SECTION_TRIGGER_INSTANCE_SYS_ID}}"
    return es
B = ["\n## APPENDIX B. Complete Trigger Blobs\n",
     "\n**Record Created** (`798916a0c31322002841b63b12d3ae7c`) `[IMPORT_TESTED]`. One line per entry, in this order.\n\n```json\n" + "\n".join(J(e) for e in trig) + "\n```\n",
     "\n**Daily** (`89142dc0c32222002841b63b12d3ae8a`) `[IMPORT_TESTED]`\n\n```json\n" + "\n".join(J(e) for e in trig_entries("daily")) + "\n```\n",
     "\n**Repeat** (`f63f0d94c32222002841b63b12d3aeed`) `[OBSERVED]`\n\n```json\n" + "\n".join(J(e) for e in trig_entries("repeat")) + "\n```\n",
     "\n**Service Catalog** (`c43a1011c36813002841b63b12d3ae15`) `[IMPORT_TESTED]`\n\n```json\n" + "\n".join(J(e) for e in trig_entries("catalog")) + "\n```\n"]
t = t.rstrip("\n") + "\n" + "".join(A) + "".join(B)
n += 2

(D / "archive" / "flow_designer_prompt20261119.md").write_text(t)
left = [x for x in ["flow_var.", "sys_customer_update>true", "<label_cache>[]", "cat_item"] if x in t]
print(f"{n} edits; {len(t.splitlines())} lines, {len(t)} chars; appendix A {sum(map(len, A))} chars, B {sum(map(len, B))} chars; leftovers: {left}")
