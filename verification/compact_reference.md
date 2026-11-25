## APPENDIX E. Compact Payload Reference `[RUNTIME_TESTED]`

Everything in this appendix is copied by script (`verification/tools/compact_reference.py`) from the files ServiceNow's Fluent SDK 4.14.2 generated for the compact-mode test (`verification/sdk_probe2/update/`). Those exact files were imported through an update set, published and run (Appendix C). `<… id>` and `<ui_id>` stand for the test's own generated ids; every other id is a platform id and is literal.

### E.1 Operation order per payload

**TT13 Action** (action, 12696 bytes): sys_hub_action_type_definition → sys_hub_step_instance → sys_variable_value ×2 → sys_element_mapping ×2 → sys_hub_step_ext_input → sys_hub_step_ext_output → sys_hub_action_input → sys_documentation ×4 → sys_hub_action_output ×3

**TT13 Compact Catalog** (flow, 6919 bytes): sys_hub_flow → DELETE sys_hub_trigger_instance_v2 → sys_hub_trigger_instance_v2 → DELETE sys_hub_action_instance_v2 → sys_hub_action_instance_v2 ×3 → DELETE sys_hub_alias_mapping ×3

**TT13 Compact Repeat** (flow, 3456 bytes): sys_hub_flow → DELETE sys_hub_trigger_instance_v2 → sys_hub_trigger_instance_v2 → DELETE sys_hub_action_instance_v2 → sys_hub_action_instance_v2 → DELETE sys_hub_alias_mapping

**TT13 Compact Daily** (flow, 3439 bytes): sys_hub_flow → DELETE sys_hub_trigger_instance_v2 → sys_hub_trigger_instance_v2 → DELETE sys_hub_action_instance_v2 → sys_hub_action_instance_v2 → DELETE sys_hub_alias_mapping

**TT13 Compact Main** (flow, 33524 bytes): sys_hub_flow → DELETE sys_hub_flow_variable → sys_hub_flow_variable → sys_documentation → DELETE sys_hub_trigger_instance_v2 → sys_hub_trigger_instance_v2 → DELETE sys_hub_action_instance_v2 → sys_hub_action_instance_v2 ×11 → DELETE sys_hub_alias_mapping ×11 → DELETE sys_hub_flow_logic_instance_v2 → sys_hub_flow_logic_instance_v2 ×12 → DELETE sys_hub_sub_flow_instance_v2 → sys_hub_sub_flow_instance_v2 → DELETE sys_hub_alias_mapping

**TT13 Subflow** (subflow, 7007 bytes): sys_hub_flow → DELETE sys_hub_flow_input → sys_hub_flow_input → sys_documentation ×2 → DELETE sys_hub_flow_output → sys_hub_flow_output → DELETE sys_hub_action_instance_v2 → sys_hub_action_instance_v2 → DELETE sys_hub_alias_mapping → DELETE sys_hub_flow_logic_instance_v2 → sys_hub_flow_logic_instance_v2

### E.2 Fields written per table (first record of each kind; empty fields listed by name only)


**`sys_hub_action_type_definition`**: `sys_id` = `<action_type_definition id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_action_type_definition_6808a80282a048d0899a7819b3f38e4b`; `access` = `public`; `active` = `true`; `description` = `Transpiler comparison test. Reverses the input text with one Script step. Safe to delete.`; `label_cache` = `(JSON text, see E.4)`; `name` = `TT13 Action`; `state` = `draft`; `system_level` = `false`. Empty: `annotation`, `category`, `sys_policy`.

**`sys_hub_step_instance`**: `sys_id` = `<step_instance id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_step_instance_5e58e21c02d341ae97f3976afbd88d7e`; `action` = `<action_type_definition id>`; `active` = `true`; `cid` = `<ui_id>`; `error_handling_type` = `1`; `label` = `Reverse text`; `order` = `1`; `step_type` = `106afb6647032200b4fad7527c9a71e7`.

**`sys_variable_value`**: `sys_id` = `<variable_value id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_variable_value_96aa4e948dd7429b8a0b0d0710e878c5`; `document` = `sys_hub_step_instance`; `document_key` = `<step_instance id>`; `order` = `100`; `value` = `instance`; `variable` = `74315b04b3201300176b051a16a8dc2b`.

**`sys_element_mapping`**: `sys_id` = `<element_mapping id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_element_mapping_e1ea8017c89c49d4ab8f9e97851fef42`; `field` = `text`; `id` = `<step_instance id>`; `table` = `var__m_sys_hub_step_ext_input_5e58e21c02d341ae97f3976afbd88d7e`; `value` = `{{action.text}}`.

**`sys_hub_step_ext_input`**: `sys_id` = `<step_ext_input id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_step_ext_input_c289f710a414403db8ced590063bdd01`; `active` = `true`; `attributes` = `element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,uiType=string,uiTypeLabel=`; `element` = `text`; `internal_type` = `string`; `label` = `Text`; `model` = `<step_instance id>`; `model_id` = `<step_instance id>`; `model_table` = `sys_hub_step_instance`; `name` = `var__m_sys_hub_step_ext_input_5e58e21c02d341ae97f3976afbd88d7e`. Empty: `default_value`.

**`sys_hub_step_ext_output`**: `sys_id` = `<step_ext_output id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_step_ext_output_e620bfd3fecb4106958e826d52804ad3`; `active` = `true`; `attributes` = `element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,uiType=string,uiTypeLabel=`; `element` = `reversed`; `internal_type` = `string`; `label` = `Reversed`; `model` = `<step_instance id>`; `model_id` = `<step_instance id>`; `model_table` = `sys_hub_step_instance`; `name` = `var__m_sys_hub_step_ext_output_5e58e21c02d341ae97f3976afbd88d7e`. Empty: `mandatory`.

**`sys_hub_action_input`**: `sys_id` = `<action_input id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_action_input_c9a42adb64e34b1c98752eaa6213ac04`; `active` = `true`; `element` = `text`; `internal_type` = `string`; `label` = `Text`; `mandatory` = `false`; `max_length` = `40`; `model` = `<action_type_definition id>`; `model_id` = `<action_type_definition id>`; `model_table` = `sys_hub_action_type_definition`; `name` = `var__m_sys_hub_action_input_6808a80282a048d0899a7819b3f38e4b`; `order` = `1`. Empty: `attributes`, `default_value`, `hint`.

**`sys_documentation`**: `sys_id` = `<documentation id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_documentation_var__m_sys_hub_action_input_6808a80282a048d0899a7819b3f38e4b_text_en`; `element` = `text`; `label` = `Text`; `language` = `en`; `name` = `var__m_sys_hub_action_input_6808a80282a048d0899a7819b3f38e4b`; `plural` = `Texts`. Empty: `hint`.

**`sys_hub_action_output`**: `sys_id` = `<action_output id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_action_output_bfce6f8d0510410d97188a1adbb5ddfd`; `active` = `true`; `attributes` = `element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,pwd2droppable=true,uiType=`; `element` = `reversed`; `internal_type` = `string`; `label` = `Reversed`; `mandatory` = `false`; `max_length` = `40`; `model` = `<action_type_definition id>`; `model_id` = `<action_type_definition id>`; `model_table` = `sys_hub_action_type_definition`; `name` = `var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `order` = `1`. Empty: `default_value`, `hint`.

**`sys_hub_flow`** (type `flow`): `sys_id` = `<flow id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_flow_421af7af6e3f498fa1404e41e137fad6`; `access` = `public`; `active` = `false`; `allow_high_security_roles` = `false`; `description` = `Transpiler comparison test. Service Catalog trigger with a catalog variable. Safe to delete.`; `flow_priority` = `MEDIUM`; `generation_source` = `fluent`; `label_cache` = `(JSON text, see E.4)`; `name` = `TT13 Compact Catalog`; `run_as` = `user`; `show_draft_actions` = `false`; `status` = `draft`; `type` = `flow`; `version` = `2`. Empty: `annotation`, `category`, `run_with_roles`, `sys_policy`.
- `DELETE sys_hub_trigger_instance_v2` query form: `flow=<flow id>^sys_idNOT INdaa1661f03b9417499bbd81cf74b7783`

**`sys_hub_trigger_instance_v2`**: `sys_id` = `<trigger id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_trigger_instance_v2_daa1661f03b9417499bbd81cf74b7783`; `flow` = `<flow id>`; `name` = `Service Catalog`; `trigger_definition` = `c43a1011c36813002841b63b12d3ae15`; `trigger_inputs` = `(encoded, see E.3)`; `trigger_type` = `service_catalog`. Empty: `category`, `comment`, `trigger_outputs`.
- `DELETE sys_hub_action_instance_v2` query form: `flow=<flow id>^sys_idNOT IN24ec0b2ab65e483ca8fb20ccf9b422f0,<action id>,<action id>`

**`sys_hub_action_instance_v2`**: `sys_id` = `<action id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_action_instance_v2_24ec0b2ab65e483ca8fb20ccf9b422f0`; `action_type` = `330ba3abc31013002841b63b12d3aee8`; `action_type_parent` = `330ba3abc31013002841b63b12d3aee8`; `active` = `true`; `flow` = `<flow id>`; `order` = `1`; `sys_class_name` = `sys_hub_action_instance_v2`; `ui_id` = `<ui_id>`; `values` = `(encoded, see E.3)`. Empty: `comment`, `display_text`, `generation_source`, `parent_ui_id`, `updation_source`.
- `DELETE sys_hub_alias_mapping` query form: `source_id=<action id>`
- `DELETE sys_hub_flow_variable` query form: `model=<flow id>^sys_idNOT IN64b6d789f19c46e789769480c1791ff3`

**`sys_hub_flow_variable`**: `sys_id` = `<flow_variable id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_flow_variable_64b6d789f19c46e789769480c1791ff3`; `active` = `true`; `element` = `note`; `internal_type` = `string`; `label` = `Note`; `mandatory` = `false`; `max_length` = `40`; `model` = `<flow id>`; `model_id` = `<flow id>`; `model_table` = `sys_hub_flow`; `name` = `var__m_sys_hub_flow_variable_dd0fabad027a44938069bc23381dd1b1`; `order` = `1`. Empty: `attributes`, `default_value`, `hint`.
- `DELETE sys_hub_flow_logic_instance_v2` query form: `flow=<flow id>^sys_idNOT IN9e1a3ff91da941a18a841e1a4c580454,<flow_logic id>,<flow_logic id>,<flow_logic id>,<flow_logic id>,<flow_logic id>,<flow_logi`

**`sys_hub_flow_logic_instance_v2`**: `sys_id` = `<flow_logic id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_flow_logic_instance_v2_9e1a3ff91da941a18a841e1a4c580454`; `flow` = `<flow id>`; `flow_variables_assigned` = `note`; `logic_definition` = `4f787d1e0f9b0010ecf0cc52ff767ea0`; `order` = `2`; `ui_id` = `<ui_id>`; `values` = `(encoded, see E.3)`. Empty: `comment`.
- `DELETE sys_hub_sub_flow_instance_v2` query form: `flow=<flow id>^sys_idNOT IN88d0874d30e24da5bbcb6f27cb75d179`

**`sys_hub_sub_flow_instance_v2`**: `sys_id` = `<sub_flow id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_sub_flow_instance_v2_88d0874d30e24da5bbcb6f27cb75d179`; `flow` = `<flow id>`; `order` = `11`; `show_stages` = `false`; `subflow` = `<flow id>`; `subflow_inputs` = `(encoded, see E.3)`; `sys_class_name` = `sys_hub_sub_flow_instance_v2`; `ui_id` = `<ui_id>`; `wait_for_completion` = `true`. Empty: `attributes`, `comment`, `display_text`, `generation_source`, `parent_ui_id`.

**`sys_hub_flow`** (type `subflow`): `sys_id` = `<flow id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_flow_f0124e5ade0346d099c6b01d2bed9524`; `access` = `public`; `active` = `false`; `allow_high_security_roles` = `false`; `description` = `Transpiler comparison test. Looks up a sys_user by user name and returns the name. Safe to delete.`; `flow_priority` = `MEDIUM`; `generation_source` = `fluent`; `label_cache` = `(JSON text, see E.4)`; `name` = `TT13 Subflow`; `run_as` = `user`; `show_draft_actions` = `false`; `status` = `draft`; `type` = `subflow`; `version` = `2`. Empty: `annotation`, `category`, `run_with_roles`, `sys_policy`.
- `DELETE sys_hub_flow_input` query form: `model=<flow id>^sys_idNOT IN064b0fea9d4947c5821c7307e529dbf2`

**`sys_hub_flow_input`**: `sys_id` = `<flow_input id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_flow_input_064b0fea9d4947c5821c7307e529dbf2`; `active` = `true`; `element` = `user_name`; `internal_type` = `string`; `label` = `User name`; `mandatory` = `true`; `max_length` = `40`; `model` = `<flow id>`; `model_id` = `<flow id>`; `model_table` = `sys_hub_flow`; `name` = `var__m_sys_hub_flow_input_f0124e5ade0346d099c6b01d2bed9524`; `order` = `1`. Empty: `attributes`, `default_value`, `hint`.
- `DELETE sys_hub_flow_output` query form: `model=<flow id>^sys_idNOT INd54414dd1b0e477393d1fd9a8a6a27a3`

**`sys_hub_flow_output`**: `sys_id` = `<flow_output id>`; `sys_scope`[display_value="x_906694_tt11"] = `8f6baeba9ba94590969cbe31fc69e713`; `sys_update_name` = `sys_hub_flow_output_d54414dd1b0e477393d1fd9a8a6a27a3`; `active` = `true`; `element` = `found`; `internal_type` = `string`; `label` = `Found`; `mandatory` = `false`; `max_length` = `40`; `model` = `<flow id>`; `model_id` = `<flow id>`; `model_table` = `sys_hub_flow`; `name` = `var__m_sys_hub_flow_output_f0124e5ade0346d099c6b01d2bed9524`; `order` = `1`. Empty: `attributes`, `default_value`, `hint`.

### E.3 Decoded blob entries, one example per construct

Each line is the decoded JSON of one record's blob. Encode it as in Section 7.1.

**Trigger: Service Catalog** — `sys_hub_trigger_instance_v2`, `trigger_definition` = `c43a1011c36813002841b63b12d3ae15`

```json
[{"triggerInstanceSysId":"","label":"Run flow In","internalType":"choice","dependent":"","choiceList":[{"fValue":"any","fLabel":"Run flow in any context","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"background","fLabel":"Run flow in background (default)","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"foreground","fLabel":"Run flow in foreground","fImage":"","fSelected":false,"fUsed":false,"fMissing":false}],"mandatory":false,"order":100,"name":"run_flow_in","value":"any","displayValue":"any","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"choice","name":"run_flow_in","label":"Run flow In","attributes":{"advanced":"true"}}}]
```

**Get Catalog Variables** — `sys_hub_action_instance_v2`, `action_type` = `330ba3abc31013002841b63b12d3aee8`; row fields: {"order": "1", "action_type_parent": "330ba3abc31013002841b63b12d3aee8"}

```json
[{"name":"catalog_variables","value":"9f9fef5b83e41310d6401665eeaad3b3:item_option_new","displayValue":"9f9fef5b83e41310d6401665eeaad3b3:item_option_new","scriptActive":false,"parameter":{"type":"slushbucket"}},{"name":"requested_item","value":"{{Service Catalog_1.request_item}}","displayValue":"{{Service Catalog_1.request_item}}","scriptActive":false,"parameter":{"type":"reference"}},{"name":"template_catalog_item","value":"439fef5b83e41310d6401665eeaad379","displayValue":"439fef5b83e41310d6401665eeaad379","scriptActive":false,"parameter":{"type":"reference"}}]
```

**Create Catalog Task** — `sys_hub_action_instance_v2`, `action_type` = `af51fd0e73141300612c273ffff6a785`; row fields: {"order": "2", "action_type_parent": "af51fd0e73141300612c273ffff6a785"}

```json
[{"name":"ah_wait","value":false,"displayValue":false,"scriptActive":false,"parameter":{"type":"boolean"}},{"name":"ah_short_description","value":"TT13 task, note [{{<ui_id>.tt9_note}}]","displayValue":"TT13 task, note [{{<ui_id>.tt9_note}}]","scriptActive":false,"parameter":{"type":"string"}},{"name":"ah_table_name","value":"sc_task","displayValue":"sc_task","scriptActive":false,"parameter":{"type":"table_name"}},{"name":"ah_requested_item","value":"{{Service Catalog_1.request_item}}","displayValue":"{{Service Catalog_1.request_item}}","scriptActive":false,"parameter":{"type":"reference"}}]
```

**Update Record** — `sys_hub_action_instance_v2`, `action_type` = `f9d01dd2c31332002841b63b12d3aea1`; row fields: {"order": "3", "action_type_parent": "f9d01dd2c31332002841b63b12d3aea1"}

```json
[{"name":"table_name","value":"sc_req_item","displayValue":"sc_req_item","scriptActive":false,"parameter":{"type":"table_name"}},{"name":"record","value":"{{Service Catalog_1.request_item}}","displayValue":"{{Service Catalog_1.request_item}}","scriptActive":false,"parameter":{"type":"document_id"}},{"name":"values","value":"description=TT13 catalog flow ran, note [{{<ui_id>.tt9_note}}]^EQ","displayValue":"description=TT13 catalog flow ran, note [{{<ui_id>.tt9_note}}]^EQ","scriptActive":false,"parameter":{"type":"template_value"}}]
```

**Trigger: Repeat** — `sys_hub_trigger_instance_v2`, `trigger_definition` = `f63f0d94c32222002841b63b12d3aeed`

```json
[{"triggerInstanceSysId":"","label":"Repeat","internalType":"glide_duration","dependent":"","choiceList":[],"mandatory":true,"order":100,"name":"repeat","value":"1970-01-01 00:02:00","displayValue":"1970-01-01 00:02:00","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"glide_duration","name":"repeat","label":"Repeat"}}]
```

**Look Up Record** — `sys_hub_action_instance_v2`, `action_type` = `9d09f99587003300663ca1bb36cb0ba3`; row fields: {"order": "1", "action_type_parent": "9d09f99587003300663ca1bb36cb0ba3"}

```json
[{"name":"sort_type","value":"sort_asc","displayValue":"sort_asc","scriptActive":false,"parameter":{"type":"choice"}},{"name":"conditions","value":"user_name=admin","displayValue":"user_name=admin","scriptActive":false,"parameter":{"type":"conditions"}},{"name":"table","value":"sys_user","displayValue":"sys_user","scriptActive":false,"parameter":{"type":"table_name"}},{"name":"if_multiple_records_are_found_action","value":"use_first_record","displayValue":"use_first_record","scriptActive":false,"parameter":{"type":"choice"}}]
```

**Trigger: Daily** — `sys_hub_trigger_instance_v2`, `trigger_definition` = `89142dc0c32222002841b63b12d3ae8a`

```json
[{"triggerInstanceSysId":"","label":"Time","internalType":"glide_time","dependent":"","choiceList":[],"mandatory":true,"order":100,"name":"time","value":"1970-01-01 03:40:00","displayValue":"1970-01-01 03:40:00","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"glide_time","name":"time","label":"Time"}}]
```

**Trigger: Created** — `sys_hub_trigger_instance_v2`, `trigger_definition` = `798916a0c31322002841b63b12d3ae7c`

```json
[{"triggerInstanceSysId":"","label":"Table","internalType":"table_name","dependent":"","choiceList":[],"mandatory":true,"order":100,"name":"table","value":"incident","displayValue":"incident","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"table_name","name":"table","label":"Table"}},{"triggerInstanceSysId":"","label":"Run On Extended Tables","internalType":"choice","dependent":"","choiceList":[{"fValue":"true","fLabel":"Run on current and extended tables","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"false","fLabel":"Run only on current table","fImage":"","fSelected":false,"fUsed":false,"fMissing":false}],"mandatory":false,"order":100,"name":"run_on_extended","value":"false","displayValue":"false","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"choice","name":"run_on_extended","label":"Run On Extended Tables","attributes":{"advanced":"true"}}},{"triggerInstanceSysId":"","label":"Run When Session Setting","internalType":"choice","dependent":"","choiceList":[{"fValue":"both","fLabel":"Run for Both Interactive and Non-Interactive Sessions","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"non_interactive","fLabel":"Only Run for Non-Interactive Session","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"interactive","fLabel":"Only Run for User Interactive Session","fImage":"","fSelected":false,"fUsed":false,"fMissing":false}],"mandatory":false,"order":100,"name":"run_when_setting","value":"both","displayValue":"both","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"choice","name":"run_when_setting","label":"Run When Session Setting","attributes":{"advanced":"true"}}},{"triggerInstanceSysId":"","label":"Run flow In","internalType":"choice","dependent":"","choiceList":[{"fValue":"any","fLabel":"Run flow in any context","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"background","fLabel":"Run flow in background (default)","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"foreground","fLabel":"Run flow in foreground","fImage":"","fSelected":false,"fUsed":false,"fMissing":false}],"mandatory":false,"order":100,"name":"run_flow_in","value":"background","displayValue":"background","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"choice","name":"run_flow_in","label":"Run flow In","attributes":{"advanced":"true"}}},{"triggerInstanceSysId":"","label":"Condition","internalType":"conditions","dependent":"","choiceList":[],"mandatory":false,"order":100,"name":"condition","value":"short_descriptionSTARTSWITHTT13RUN","displayValue":"short_descriptionSTARTSWITHTT13RUN","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"conditions","name":"condition","label":"Condition","attributes":{"wants_to_add_conditions":"true","modelDependent":"trigger_inputs"},"dependent_on":"table","use_dependent":true}},{"triggerInstanceSysId":"","label":"Run When User Setting","internalType":"choice","dependent":"","choiceList":[{"fValue":"any","fLabel":"Run for any user","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"one_of","fLabel":"Only Run if triggered by the following users","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"not_one_of","fLabel":"Do not run if triggered by the following users","fImage":"","fSelected":false,"fUsed":false,"fMissing":false}],"mandatory":false,"order":100,"name":"run_when_user_setting","value":"any","displayValue":"any","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"choice","name":"run_when_user_setting","label":"Run When User Setting","attributes":{"advanced":"true"}}},{"triggerInstanceSysId":"","label":"Run When User List","internalType":"glide_list","dependent":"","choiceList":[],"mandatory":false,"order":100,"name":"run_when_user_list","value":"","displayValue":"","displayField":"","scriptActive":false,"valueSysId":"","children":[],"parameter":{"type":"glide_list","name":"run_when_user_list","label":"Run When User List","attributes":{"advanced":"true"}}}]
```

**Look Up Records** — `sys_hub_action_instance_v2`, `action_type` = `43400a1587003300663ca1bb36cb0b4b`; row fields: {"order": "1", "action_type_parent": "43400a1587003300663ca1bb36cb0b4b"}

```json
[{"name":"conditions","value":"user_nameINabel.tuter,itil","displayValue":"user_nameINabel.tuter,itil","scriptActive":false,"parameter":{"type":"conditions"}},{"name":"table","value":"sys_user","displayValue":"sys_user","scriptActive":false,"parameter":{"type":"table_name"}},{"name":"sort_type","value":"sort_asc","displayValue":"sort_asc","scriptActive":false,"parameter":{"type":"choice"}},{"name":"max_results","value":1000,"displayValue":1000,"scriptActive":false,"parameter":{"type":"integer"}}]
```

**Custom action call** — `sys_hub_action_instance_v2`, `action_type` = `<action_type_definition id>`; row fields: {"order": "12", "action_type_parent": "<action_type_definition id>"}

```json
[{"name":"text","value":"{{<ui_id>.found}}","displayValue":"{{<ui_id>.found}}","scriptActive":false,"parameter":{"type":"string"}}]
```

**Create Record** — `sys_hub_action_instance_v2`, `action_type` = `2de05916c31332002841b63b12d3aee1`; row fields: {"order": "17", "parent_ui_id": "<ui_id>", "action_type_parent": "2de05916c31332002841b63b12d3aee1"}

```json
[{"name":"table_name","value":"incident_task","displayValue":"incident_task","scriptActive":false,"parameter":{"type":"table_name"}},{"name":"values","value":"incident={{Created_1.current.sys_id}}^short_description=TT13 caught^EQ","displayValue":"incident={{Created_1.current.sys_id}}^short_description=TT13 caught^EQ","scriptActive":false,"parameter":{"type":"template_value"}}]
```

**Set Flow Variables** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `4f787d1e0f9b0010ecf0cc52ff767ea0`; row fields: {"order": "2", "flow_variables_assigned": "note"}

```json
{"outputsToAssign":[],"variables":[{"id":"<flow_variable id>","name":"note","value":"start","displayValue":"start","children":[],"parameter":{},"scriptActive":false}],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[{"id":"<flow_variable id>","name":"note","value":"start","displayValue":"","children":[],"parameter":{},"scriptActive":false}]}
```

**For Each** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `098e1dc5c3e232002841b63b12d3ae33`; row fields: {"order": "3"}

```json
{"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[{"id":"","name":"items","value":"{{<ui_id>.Records}}","displayValue":"{{<ui_id>.Records}}"}]}
```

**If** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `af4e1945c3e232002841b63b12d3ae3e`; row fields: {"order": "5"}

```json
{"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[{"id":"","name":"condition","value":"{{Created_1.current.urgency}}=1","displayValue":"{{Created_1.current.urgency}}=1","children":[],"parameter":{},"scriptActive":false}]}
```

**Else If** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `666e5545c3e232002841b63b12d3ae99`; row fields: {"order": "7"}

```json
{"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[{"id":"","name":"condition","value":"{{Created_1.current.urgency}}=2","displayValue":"{{Created_1.current.urgency}}=2","children":[],"parameter":{},"scriptActive":false}]}
```

**Else** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `1f781bf3c32232002841b63b12d3aee6`; row fields: {"order": "9"}

```json
{"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[]}
```

**Try** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `07223332de022010ec58424b73829721`; row fields: {"order": "13"}

```json
{"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[]}
```

**Catch** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `35d60003e6022010a5e40cdd1254dd21`; row fields: {"order": "16", "connected_to": "<ui_id>"}

```json
{"inputs":[],"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[]}
```

**Do the following in Parallel** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `5d31e5dedfe50300b61ecae83df26326`; row fields: {"order": "18"}

```json
{"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[]}
```

**Parallel Branch** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `a1168de173311300b61e66476bf6a7d0`; row fields: {"order": "19", "parent_ui_id": "<ui_id>"}

```json
{"inputs":[],"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[]}
```

**Wait for a duration of time** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `fdb2541473031300b61e66476bf6a70e`; row fields: {"order": "23"}

```json
{"outputsToAssign":[],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[{"id":"4973581473031300b61e66476bf6a785","name":"duration_type","value":"explicit_duration","displayValue":"Explicit duration","children":[],"scriptActive":false},{"id":"bf1d6161b736230034c6ce69ee11a920","name":"percentage_timer_input_datetime","value":"","displayValue":"","children":[],"scriptActive":false},{"id":"8033309c5376230034c6ddeeff7b12e1","name":"timer_percentage","value":"","displayValue":"","children":[],"scriptActive":false},{"id":"ef145c1473031300b61e66476bf6a7be","name":"timer_duration","value":"1970-01-01 00:00:05","displayValue":"1970-01-01 00:00:05","children":[],"scriptActive":false,"parameter":{"type":"glide_duration"}},{"id":"dca4105473031300b61e66476bf6a726","name":"timer_relative_duration_operator","value":"","displayValue":"","children":[],"scriptActive":false},{"id":"1f25d05473031300b61e66476bf6a773","name":"timer_relative_duration_datetime","value":"","displayValue":"","children":[],"scriptActive":false},{"id":"fb55145473031300b61e66476bf6a762","name":"timer_schedule","value":"","displayValue":"","children":[],"scriptActive":false}]}
```

**Subflow call** — `sys_hub_sub_flow_instance_v2`, `subflow` = `<flow id>`; row fields: {"order": "11", "wait_for_completion": "true"}

```json
[{"name":"user_name","value":"{{Created_1.current.caller_id.user_name}}","displayValue":"{{Created_1.current.caller_id.user_name}}","parameter":{"type":"string"}}]
```

**Assign Subflow Outputs** — `sys_hub_flow_logic_instance_v2`, `logic_definition` = `df4e1945c3e232002841b63b12d3ae3e`; row fields: {"order": "2", "outputs_assigned": "found"}

```json
{"outputsToAssign":[{"id":"","name":"found","value":"{{<ui_id>.Record.name}}","displayValue":"{{<ui_id>.Record.name}}","children":[],"parameter":{},"scriptActive":false}],"variables":[],"decisionTableInputs":[],"dynamicInputs":[],"workflowInputs":[],"inputs":[]}
```

### E.4 Row linkage of the tested main flow, and its `label_cache`

| order | table | definition | ui_id | parent_ui_id | connected_to |
|---|---|---|---|---|---|
| `1` | `action_instance_v2` | Look Up Records | u1 |  |  |
| `2` | `flow_logic_instance_v2` | Set Flow Variables | u2 |  |  |
| `3` | `flow_logic_instance_v2` | For Each | u3 |  |  |
| `4` | `flow_logic_instance_v2` | Set Flow Variables | u4 | u3 |  |
| `5` | `flow_logic_instance_v2` | If | u5 |  |  |
| `6` | `action_instance_v2` | Update Record | u6 | u5 |  |
| `7` | `flow_logic_instance_v2` | Else If | u7 |  |  |
| `8` | `action_instance_v2` | Update Record | u8 | u7 |  |
| `9` | `flow_logic_instance_v2` | Else | u9 |  |  |
| `10` | `action_instance_v2` | Update Record | u10 | u9 |  |
| `11` | `sub_flow_instance_v2` | subflow | u11 |  |  |
| `12` | `action_instance_v2` | custom action | u12 |  |  |
| `13` | `flow_logic_instance_v2` | Try | u13 |  |  |
| `14` | `action_instance_v2` | Look Up Record | u14 | u13 |  |
| `15` | `action_instance_v2` | Update Record | u15 | u13 |  |
| `16` | `flow_logic_instance_v2` | Catch | u16 |  | u13 |
| `17` | `action_instance_v2` | Create Record | u17 | u16 |  |
| `18` | `flow_logic_instance_v2` | Do the following in Parallel | u18 |  |  |
| `19` | `flow_logic_instance_v2` | Parallel Branch | u19 | u18 |  |
| `19➛20` | `action_instance_v2` | Create Record | u20 | u19 |  |
| `21` | `flow_logic_instance_v2` | Parallel Branch | u21 | u18 |  |
| `21➛22` | `action_instance_v2` | Create Record | u22 | u21 |  |
| `23` | `flow_logic_instance_v2` | Wait for a duration of time | u23 |  |  |
| `24` | `action_instance_v2` | Update Record | u24 |  |  |

`label_cache` of that flow has 10 entries. First three:

```json
{"name":"<ui_id>.Records","label":"<ui_id>➛Records","type":"array.object","base_type":"array.object","usedInstances":{"<ui_id>":["items"]},"attributes":{},"column_name":"Records"}
{"name":"flow_variable.note","label":"Flow Variables➛Note","type":"string","base_type":"string","usedInstances":{"<ui_id>":["note"],"<ui_id>":["values"]},"attributes":{},"reference_table":null,"reference_display":null}
{"name":"<ui_id>.item.user_name","label":"3 - For Each - ➛item➛User Name","type":"string","base_type":"string","usedInstances":{"<ui_id>":["note"]},"attributes":{}}
```

### E.5 The compact custom action

No snapshot, no `sys_hub_action_plan`, `state` `draft`. Rows other than the definition:

- `sys_hub_step_instance`: `sys_id`=`<step_instance id>`; `action`=`<action_type_definition id>`; `active`=`true`; `cid`=`<ui_id>`; `error_handling_type`=`1`; `label`=`Reverse text`; `order`=`1`; `step_type`=`106afb6647032200b4fad7527c9a71e7`
- `sys_variable_value`: `sys_id`=`<variable_value id>`; `document`=`sys_hub_step_instance`; `document_key`=`<step_instance id>`; `order`=`100`; `value`=`instance`; `variable`=`74315b04b3201300176b051a16a8dc2b`
- `sys_variable_value`: `sys_id`=`<variable_value id>`; `document`=`sys_hub_step_instance`; `document_key`=`<step_instance id>`; `order`=`100`; `value`=`(function execute(inputs, outputs) {\n    outputs.reversed = String(inputs.text || '').split('').reverse().join('');\n})(inputs, outputs);`; `variable`=`71aa7f6647032200b4fad7527c9a719b`
- `sys_element_mapping`: `sys_id`=`<element_mapping id>`; `field`=`text`; `id`=`<step_instance id>`; `table`=`var__m_sys_hub_step_ext_input_5e58e21c02d341ae97f3976afbd88d7e`; `value`=`{{action.text}}`
- `sys_element_mapping`: `sys_id`=`<element_mapping id>`; `field`=`reversed`; `id`=`<action_type_definition id>`; `table`=`var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `value`=`{{step[<ui_id>].reversed}}`
- `sys_hub_step_ext_input`: `sys_id`=`<step_ext_input id>`; `active`=`true`; `attributes`=`element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,uiType=string,uiTypeLabel=String`; `element`=`text`; `internal_type`=`string`; `label`=`Text`; `model`=`<step_instance id>`; `model_id`=`<step_instance id>`; `model_table`=`sys_hub_step_instance`; `name`=`var__m_sys_hub_step_ext_input_5e58e21c02d341ae97f3976afbd88d7e`
- `sys_hub_step_ext_output`: `sys_id`=`<step_ext_output id>`; `active`=`true`; `attributes`=`element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,uiType=string,uiTypeLabel=String`; `element`=`reversed`; `internal_type`=`string`; `label`=`Reversed`; `model`=`<step_instance id>`; `model_id`=`<step_instance id>`; `model_table`=`sys_hub_step_instance`; `name`=`var__m_sys_hub_step_ext_output_5e58e21c02d341ae97f3976afbd88d7e`
- `sys_hub_action_input`: `sys_id`=`<action_input id>`; `active`=`true`; `element`=`text`; `internal_type`=`string`; `label`=`Text`; `mandatory`=`false`; `max_length`=`40`; `model`=`<action_type_definition id>`; `model_id`=`<action_type_definition id>`; `model_table`=`sys_hub_action_type_definition`; `name`=`var__m_sys_hub_action_input_6808a80282a048d0899a7819b3f38e4b`; `order`=`1`
- `sys_documentation`: `sys_id`=`<documentation id>`; `element`=`text`; `label`=`Text`; `language`=`en`; `name`=`var__m_sys_hub_action_input_6808a80282a048d0899a7819b3f38e4b`; `plural`=`Texts`
- `sys_documentation`: `sys_id`=`<documentation id>`; `element`=`reversed`; `label`=`Reversed`; `language`=`en`; `name`=`var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `plural`=`Reversed`
- `sys_documentation`: `sys_id`=`<documentation id>`; `element`=`__action_status__`; `label`=`Action Status`; `language`=`en`; `name`=`var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `plural`=`Action Status`
- `sys_documentation`: `sys_id`=`<documentation id>`; `element`=`__dont_treat_as_error__`; `label`=`Don't Treat as Error`; `language`=`en`; `name`=`var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `plural`=`Don't Treat as Errors`
- `sys_hub_action_output`: `sys_id`=`<action_output id>`; `active`=`true`; `attributes`=`element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,pwd2droppable=true,uiType=string,uiTypeLabel=String,uiUn`; `element`=`reversed`; `internal_type`=`string`; `label`=`Reversed`; `mandatory`=`false`; `max_length`=`40`; `model`=`<action_type_definition id>`; `model_id`=`<action_type_definition id>`; `model_table`=`sys_hub_action_type_definition`; `name`=`var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `order`=`1`
- `sys_hub_action_output`: `sys_id`=`<action_output id>`; `active`=`true`; `attributes`=`element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,action_error_output=true,uiType=object,uiTypeLabel=Objec`; `element`=`__action_status__`; `internal_type`=`string`; `label`=`Action Status`; `mandatory`=`false`; `max_length`=`65000`; `model`=`<action_type_definition id>`; `model_id`=`<action_type_definition id>`; `model_table`=`sys_hub_action_type_definition`; `name`=`var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `order`=`1`
- `sys_hub_action_output`: `sys_id`=`<action_output id>`; `active`=`true`; `attributes`=`element_mapping_provider=com.glide.flow_design.action.data.FlowDesignVariableMapper,action_error_output=true,uiType=boolean,uiTypeLabel=True`; `default_value`=`true`; `element`=`__dont_treat_as_error__`; `internal_type`=`boolean`; `label`=`Don't Treat as Error`; `mandatory`=`false`; `max_length`=`40`; `model`=`<action_type_definition id>`; `model_id`=`<action_type_definition id>`; `model_table`=`sys_hub_action_type_definition`; `name`=`var__m_sys_hub_action_output_6808a80282a048d0899a7819b3f38e4b`; `order`=`2`
