"""Build flow_designer_prompt_v2.2.md from v2.1: results of tests 19, 19b and 19c (the rest of the compact constructs, REST name-value items, mapping-row delete order).
Local files only. Every replacement must match exactly once."""
import pathlib, re
R = pathlib.Path(__file__).parent.parent.parent
s = (R / "archive" / "flow_designer_prompt_v2.1.md").read_text()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
def rex(pat, new):
    global s
    m = re.findall(pat, s, flags=re.S); assert len(m) == 1, (len(m), pat[:80]); s = re.sub(pat, lambda _: new, s, flags=re.S)

rep("**Prompt version 2.1** (2026-11-19).", "**Prompt version 2.2** (2026-11-19).")

# compact mode: what was tested
rex(r"Not tested in compact form: Send Email, Send Notification, Fire Event.*?was not tested in compact form\.",
    "**Also written from these rules and run (test 19):** Send Email, Send Notification, Fire Event, Ask For Approval, Do the following until, End Flow, Exit Loop, Skip Iteration, the Record Updated trigger (`CHANGESTO`, strategy `every`), the Weekly, Monthly and Run Once triggers, and a custom action with Script, REST and Script steps; nine flows and the action were published by one API call. "
    "Not tested in compact form: the Created or Updated trigger (use the Updated entry list below) and the constructs in Section 5 that were never run in any form (Go back to, Make a decision, Append to Flow Variables, Get Flow Outputs, Call a Workflow, Dynamic Flow, the Recurrence trigger). For those, use the entry shape in rule 3 with the names and types from Section 7, and say in `CONFIGURATION_NOTES` that the construct was not tested.")

# rule 5: Else with connected_to
rep("The tested files left `connected_to` empty on Else and Else If and that worked; the platform's own value is the opening If, which is also safe.",
    "`connected_to` on Else and Else If may be empty (the SDK-built files, tested) or the opening If's `ui_id` (the platform's own value; tested in compact form on an Else).")

# exceptions: REST no longer needs the full shape
rex(r"- a custom action needs a \*\*REST step\*\* \(Section 10\.0\.3\), which has no compact reference\.[^\n]*\n", "")

# compact entries proven by test 19, placed before the exceptions list
NEW_ENTRIES = r'''**Compact entries proven by test 19** (written from the rules; each ran):

- **Record Updated / Created or Updated trigger:** the seven Created entries (Appendix E.3) with the `table` and `condition` values, plus one more entry: `{"triggerInstanceSysId":"","label":"Run Trigger","internalType":"choice","dependent":"","choiceList":[{"fValue":"once","fLabel":"Once","fImage":"","fSelected":false,"fUsed":false,"fMissing":false},{"fValue":"unique_changes","fLabel":"For each unique change",…},{"fValue":"always","fLabel":"Only if not currently running",…},{"fValue":"every","fLabel":"For every update",…}],"mandatory":false,"order":100,"name":"trigger_strategy","value":"every","displayValue":"every","displayField":"","scriptActive":false,"children":[],"parameter":{"type":"choice","name":"trigger_strategy","label":"Run Trigger"}}`. Row: `name` `Updated`, `trigger_type` `record_update`, definition from Section 5.1. Pills are `{{Updated_1.current…}}`. Three writes (create, change another field, set urgency to 1) gave one execution.
- **Weekly:** two entries in the Daily entry shape: `day_of_week` (`internalType` and `parameter.type` `day_of_week`, `value` `"4"`, `displayValue` `"Thursday"`, `label` `Day of Week`) and `time` (`glide_time`, `1970-01-01 HH:MM:00`).
- **Monthly:** `day_of_month` (`integer`, `value` the number `19`, `displayValue` `"19"`, `parameter` `{"type":"integer","name":"day_of_month","label":"Day of Month","attributes":{"integer_type":"day_of_month"}}`) and `time`.
- **Run Once:** one entry `run_in` (`glide_date_time`, `label` `Run in`, `value` `YYYY-MM-DD HH:MM:SS`). All three schedules fired at the exact minute set, read in the activating user's time zone.
- **Send Email, Send Notification, Fire Event, Ask For Approval:** short action entries, one per input set, `parameter.type` = the input's internal type from Section 7.3 (`document_id` for `record`, `table_name`, `boolean` for `watermark_email`, `string`, `html` for `ah_body`, `reference` for `event_name` and `notification` with the sys_id as `value` and `displayValue`, `approval_rules` for `approval_conditions`). Send Notification writes an email only when the notification finds a recipient on the record.
- **Do the following until, End, Exit Loop, Skip Iteration:** logic rows. Do the following until has one `condition` entry in the If shape; the body's rows carry its `ui_id` as `parent_ui_id`. End, Exit Loop and Skip Iteration have an empty `inputs` list and sit inside the branch that decides (`parent_ui_id` = that If). Tested: over four users in a For Each, Skip Iteration skipped the second, Exit Loop stopped at the third, and one record was created.

'''
rep("**Use the full published shape (Sections 2 to 10) instead when:**", NEW_ENTRIES + "**Use the full published shape (Sections 2 to 10) instead when:**")

# 5.3 table
rep("| End | `d176605ea76103004f27b0d2187901c7` |", "| End (End Flow) | `d176605ea76103004f27b0d2187901c7` |")
rep("| Exit Loop `[OBSERVED]` | `7444b31c37063110ac85cdd734924bff` |", "| Exit Loop `[RUNTIME_TESTED]` | `7444b31c37063110ac85cdd734924bff` |")
rep("| Skip Iteration `[OBSERVED]` | `48de1b5837063110ac85cdd734924b15` |", "| Skip Iteration `[RUNTIME_TESTED]` | `48de1b5837063110ac85cdd734924b15` |")

# 10.0.3 REST: name-value items, delete order, corrected test claim
rep("Name-value settings with pills use `{\"type\":\"ADV_NV\",\"value\":[{\"name\":\"probe\",\"value\":\"{{step[<cid>].upper}}\"}]}`.",
    "Name-value settings (`query_params`, `headers`) use `{\"type\":\"ADV_NV\",\"value\":[{\"name\":\"probe\",\"value\":\"{{step[<cid>].upper}}\",\"attributes\":{\"omit_if_empty\":false,\"mandatory\":false}}]}`. **Every item needs its `attributes` object** (`{}` is also seen on platform-written steps). Without it the action publishes and then fails when it runs: `Cannot invoke \"java.util.Map.getOrDefault(Object, Object)\" because the return value of \"com.snc.process_flow.operation.utils.NameValueItem.getAttributes()\" is null` (test 19).")
rex(r"Tested: a Script step made a value, a REST step sent it as a query parameter to the instance's own login page, and a second Script step combined the first step's output with the REST step's `status_code`\. The flow wrote `\[INC0010011 / HTTP 200\] status \[200\]`\.",
    "**Tested (test 19c, compact shape):** a Script step made a value; a REST step sent it as a query parameter and inside a header to an echo endpoint on the instance; a second Script step read the REST step's `response_body` and `status_code`. The flow wrote `TT19c summary [probe=INC0010038 header=hdr-INC0010038 / HTTP 200] status [200]`, so both pills reached the wire. The platform's export of that action after activation is `verification/fixtures/dev435256/platform_export_tt19c_rest_action_published.xml`.\n\n"
    "**Correction to the earlier full-shape test (test 8).** That test wrote `[INC0010011 / HTTP 200] status [200]`, which proved the three steps ran and the status code came back. It did **not** prove the query parameter was sent: the step's mapping rows were found missing afterwards. The cause is the record order. Section 10.0 lists `DELETE sys_element_mapping query: table=var__m_sys_flow_step_definition_input_{{STEP_TYPE}}^id={{STEP}}` *after* the step's mapping rows; that is how an older platform export of a Script step reads, and for a Script step it is harmless because those two rows are empty. For a REST or JSON Parser step the same delete removes the rows that carry the pills. **In the full shape, for a REST or JSON Parser step, leave that delete out** (the platform's newer exports have only `DELETE sys_element_mapping query: id={{STEP}}` before the rows). The compact shape has no deletes inside the action and is not affected. A full-shape REST step with pills has therefore not been proven; use compact.")
rep("**Several steps:** one `DELETE sys_hub_step_instance", "**Compact shape (tested, test 19c):** the step instance, one `sys_variable_value` per setting and one `sys_element_mapping` per setting, as described below, with no deletes and no snapshot; Script steps as in Appendix E.5.\n\n**Several steps (full shape):** one `DELETE sys_hub_step_instance")

# 13.1
rep("the last one an action with a JSON Parser step and its flow, also returned `succeeded` = `total`.", "including an action with a JSON Parser step and its flow, and one call for nine flows and an action together, also returned `succeeded` = `total`.")

# critical rules
rep("25. **A JSON Parser step carries its own complex object**", "26. **REST name-value items carry `attributes`**, and in the full shape a REST or JSON Parser step has no scoped mapping delete after its mapping rows (Section 10.0.3).\n25. **A JSON Parser step carries its own complex object**")
i26 = s.index("26. **REST name-value items carry"); e26 = s.index("\n", i26); line26 = s[i26:e26 + 1]; s = s[:i26] + s[e26 + 1:]
i25 = s.index("25. **A JSON Parser step carries its own complex object**"); e25 = s.index("\n", i25); s = s[:e25 + 1] + line26 + s[e25 + 1:]

# Appendix C
anchor = "| Custom action with a JSON Parser step and its flow, both compact and written from this prompt's rules (not by the SDK), one activation call |"
i = s.index(anchor); e = s.index("\n", i)
rows = ("| Compact, written from the rules: Fire Event, Send Email, Do the following until | One incident | Event `incident.inactivity` with `TT19 INC0010030` and `compact`; email `TT19 compact INC0010030`; one task `TT19 loop body for INC0010030`; description `TT19 A done for INC0010030` |\n"
        "| Compact Record Updated trigger, `CHANGESTO`, `every` | Create, change impact, set urgency to 1 | One execution; `TT19 UPDATED fired for INC0010031` |\n"
        "| Compact Ask For Approval, If, End Flow, Else (with `connected_to`) | Two incidents; one approved, one rejected | `TT19 APPROVED branch for INC0010032`, last step not reached; `TT19 NOT APPROVED branch for INC0010033`, last step reached |\n"
        "| Compact Send Notification | One incident with an assignee | Email `INC0010039 priority raised to 4 - Low` (an incident without an assignee gave a `COMPLETE` run and no email) |\n"
        "| Compact For Each with Skip Iteration and Exit Loop | One incident; four users in the loop | One task only, `TT19 loop task abel.tuter`; description `TT19 loop flow finished for INC0010035` |\n"
        "| Compact Weekly, Monthly and Run Once triggers | Schedules set for the same minute | Three executions at 05:32:00 UTC, the minute set (9:32 PM Pacific), each `COMPLETE` |\n"
        "| Compact custom action with Script, REST and Script steps; pills in a query parameter and a header; echo endpoint | One incident | `TT19c summary [probe=INC0010038 header=hdr-INC0010038 / HTTP 200] status [200]`. First attempt without `attributes` on the name-value item: run `ERROR` (Section 10.0.3) |\n")
s = s[:e + 1] + rows + s[e + 1:]

# version history
i = s.index("| **2.1** | 2026-11-19 |"); e = s.index("\n", i)
s = s[:e + 1] + "| **2.2** | 2026-11-19 | `flow_designer_prompt_v2.2.md` | Test 19: every construct that was untested in compact form now ran from rule-written compact payloads (Send Email, Send Notification, Fire Event, Ask For Approval, Do Until, End Flow, Record Updated, Weekly, Monthly, Run Once, REST-step action); Exit Loop and Skip Iteration ran for the first time. REST name-value items need `attributes`. Full-shape mapping-row delete order corrected, and the test 8 claim about the query parameter withdrawn. REST no longer needs the full shape. |\n" + s[e + 1:]
(R / "archive" / "flow_designer_prompt_v2.2.md").write_text(s)
print("written", len(s), "chars,", s.count("\n") + 1, "lines")
