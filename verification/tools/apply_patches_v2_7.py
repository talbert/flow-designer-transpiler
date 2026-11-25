"""Build flow_designer_prompt_v2.7.md from v2.6: results of tests 26 and 27 (2026-11-20): flow error handler, Knowledge Management trigger,
Visual Task Board actions, decision options, more catalog variable types, more Recurrence forms. Local files only. Every replacement must match exactly once."""
import json, pathlib
R = pathlib.Path(__file__).parent.parent.parent
s = (R / "archive" / "flow_designer_prompt_v2.6.md").read_text()
CAT = json.load(open(R / "verification/fixtures/dev435256/full_catalog.json"))
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
def repline(start, new):
    global s
    assert s.count("\n" + start) == 1, (s.count("\n" + start), start[:80]); i = s.index("\n" + start) + 1; j = s.index("\n", i); s = s[:i] + new + s[j:]
def addafter(start, extra):
    """Append text to the end of the one line that begins with `start`."""
    global s
    assert s.count("\n" + start) == 1, (s.count("\n" + start), start[:80]); i = s.index("\n" + start) + 1; j = s.index("\n", i); s = s[:j] + extra + s[j:]
rep("**Prompt version 2.6** (2026-11-20).", "**Prompt version 2.7** (2026-11-20).")

# ---- markers
ids = [a["sys_id"] for a in CAT["actions"] if a["sys_scope.scope"] == "sn_vtb_ah" and a["state"] == "published" and a.get("active", "true") != "false"]
assert len(ids) == 14, len(ids)
ids += ["7321c78a14b75210f8779da9137d354d",                                         # Publish Article
        "35d60003e6022010a5e40cdd1254dd23", "e9060aa2c3013010ace8b740ad40dd51",     # Top Level Catch, Top Level Try
        "9bdb2c0483331210730e5b43c22bc071"]                                         # Knowledge Management trigger
for i in ids: rep("\n- %s | " % i, "\nT %s | " % i)

# ---- summary near the top and the id tables
rep("and the other Recurrence forms ran (tests 24 and 25). Their rules are in Appendix H.0.",
    "and the other Recurrence forms ran (tests 24 and 25). Tests 26 and 27 added the **flow error handler**, the Knowledge Management trigger, the 14 Visual Task Board actions, the `run_all` and Otherwise options of Make a decision, and six more catalog variable types. Their rules are in Appendix H.0.")
rep("| Decision (a branch of Make a decision) `[RUNTIME_TESTED]` (Appendix H.0) | `b1f542d673331300612c273ffff6a7c7` |",
    "| Decision (a branch of Make a decision) `[RUNTIME_TESTED]` (Appendix H.0) | `b1f542d673331300612c273ffff6a7c7` |\n| Top Level Try (flow error handler, the main steps) `[RUNTIME_TESTED]` (Appendix H.0) | `e9060aa2c3013010ace8b740ad40dd51` |\n| Top Level Catch (flow error handler, the handler steps) `[RUNTIME_TESTED]` (Appendix H.0) | `35d60003e6022010a5e40cdd1254dd23` |")
rep("| SLA Task `[RUNTIME_TESTED]` (Appendix H.0) | `f5ce00a873723300d70877186bf6a759` | `sla_task` |",
    "| SLA Task `[RUNTIME_TESTED]` (Appendix H.0) | `f5ce00a873723300d70877186bf6a759` | `sla_task` |\n| Knowledge Management `[RUNTIME_TESTED]` (Appendix H.0) | `9bdb2c0483331210730e5b43c22bc071` | `knowledge_management` |")
addafter("**Flow-level error handler (Top Level Try/Catch):** not implemented.", " **This prompt has tested rules for it (Appendix H.0, test 26).**")

# ---- catalog variable types
repline("    `order` counts from 0. Tested with catalog types", '''    `order` counts from 0. `"type"` is `"string"` for every variable type tested; the variable's own type goes in `attributes.catalogType` (the number in `item_option_new.type`, as text). A pill inside `value` resolved. Tested types and how the value is written:

    | `catalogType` | `catalogTypeLabel` | `value` |
    |---|---|---|
    | `6` | `Single Line Text` | text |
    | `2` | `Multi Line Text` | text |
    | `5` | `Select Box` | the choice's stored value |
    | `8` | `Reference` | the record's sys_id |
    | `7` | `CheckBox` | `true` or `false` |
    | `1` | `Yes / No` | `true` or `false`. **Not `Yes`:** `Yes` and `yes` were stored as No; `true` and `1` were stored as Yes |
    | `9` | `Date` | `YYYY-MM-DD` |
    | `10` | `Date/Time` | `YYYY-MM-DD HH:MM:SS`, read in the time zone of the user the flow runs as (`2026-12-24 10:30:00` was stored as 18:30 UTC) |

    The variable sys_ids come from the target instance (`item_option_new` for the item): ask for them or name them in `CONFIGURATION_NOTES`.''')

# ---- which actions to reach for
repline("1. The actions with a `T`:", "1. The actions with a `T`: they have run (80 actions after test 26).")
repline("4. **Messaging and boards**", '''4. **Messaging and boards** (58: Slack WebHooks, Connect Spoke, Visual Task Board Spoke, Omni-Experience). The 14 **Visual Task Board Spoke** actions carry a `T` (test 26): they created a freeform, a flexible and a guided board, added, renamed, reordered and deleted lanes, added and removed a member, and created, assigned, moved and unassigned a card. Their input names start with a capital (`Board`, `Lane_Name`, `Task_Table`). Create VTB Card takes the lane as the lane's sys_id, `{{<Add VTB Lane ui_id>.Lane.sys_id}}`. **Get Visual Task Board Lanes** reads its `board` input as JSON text, `{"value":"<board sys_id>"}`; a bare sys_id returns no lanes. The Slack, Connect and Omni-Experience actions were not run: they need a connection, credential or channel set up on the target. Name that need in `CONFIGURATION_NOTES`.''')

# ---- triggers
repline("- **Knowledge Management** `[OBSERVED]`", '''- **Knowledge Management** `[RUNTIME_TESTED]` (`trigger_type` `knowledge_management`, instance `name` `Knowledge Management`; its definition is in state `draft` on the test instance, and the shipped knowledge flows use it): `trigger_inputs` is the encoded empty list `[]`. The flow does not start by itself: a knowledge base names it in `kb_knowledge_base.kb_publish_flow` (run when someone publishes an article) or `kb_knowledge_base.kb_retire_flow` (run on retire). Say so in `CONFIGURATION_NOTES`. **The flow replaces the knowledge base's normal publishing, so it must publish the article itself**: the action Publish Article (`7321c78a14b75210f8779da9137d354d`, input `knowledge_record`) does it. Pill `{{Knowledge Management_1.knowledge}}` (the `kb_knowledge` record) and dot-walks from it. In test 26 the Publish button on an article of a test knowledge base ran the flow; the article became `published` and the flow's Update Record on it ran.''')
repline("  - Not run: `yearly`", '''  - **Scheduled as intended, but not waited for** (test 26; the start was set in the past and the platform's next run was read from `sys_trigger`): `yearly` with `repeat_month` (`month_of_year`, label `Every`, `3` for March), `day_selection` = `fixed_day` and `day_of_month` `15` gave March 15 of the next year; `monthly` with `day_selection` = `relative_weekday`, `relative_week` (`choice`, label `Relative week`, `1` to `4`, `5` for last) = `2` and `relative_weekday` (`day_of_week`, label `Weekday`) = `2` gave the second Tuesday of the next month; `weekly` with `days_of_the_week` = `2,4` gave the next Tuesday; `end` = `end_date` with `end_date_time` (`glide_date_time`, label `Date and Time`) was stored on the trigger row. A start time in the past did not make the flow run at activation.
  - Not settled: `frequency` above 1 (with `daily` and `2` the value was stored, but the first next run was the next day), `end` = `after`, business calendars. For those, follow Section 7.8.''')

# ---- flow logic
rep("A logic type with `-` (Call a Workflow, Placeholder, Top Level Try, Top Level Catch, Update Flow Template) has no tested rules: do not guess its shape; follow Section 7.8.",
    "A logic type with `-` (Call a Workflow, Placeholder, Update Flow Template) has no tested rules: do not guess its shape; follow Section 7.8.")
repline("- **Go back to** `[RUNTIME_TESTED]`:", '''- **Flow error handler (Top Level Try and Top Level Catch)** `[RUNTIME_TESTED]` (test 26). This is the "Error handler" section at the bottom of a flow in Workflow Studio. When a step of the flow fails, the remaining steps are skipped, the handler's steps run, and the execution ends as `COMPLETE`.
  - **Top Level Try** (`e9060aa2c3013010ace8b740ad40dd51`): one row with `order` `0`, no `parent_ui_id`, and the empty six-key `values`. **Every top-level step of the flow gets this row's `ui_id` as its `parent_ui_id`** (steps nested deeper keep their own parent).
  - **Top Level Catch** (`35d60003e6022010a5e40cdd1254dd23`): one row ordered after the last main step, no `parent_ui_id`, no `connected_to`, and one input, `enabled` = `1`. The handler's steps get this row's `ui_id` as their `parent_ui_id`.
  - Inside the handler, the error is `{{<Top Level Catch ui_id>.__status__.code}}` and `{{<Top Level Catch ui_id>.__status__.message}}`. In the test a Look Up Record that found nothing gave code `1` and the message "No record found in Look Up Record action. Context id: …".
  - Use it when the source script has a `try`/`catch` around its whole body, or when the request asks what should happen if the flow fails. For a `try`/`catch` around part of the logic, use the ordinary Try and Catch.
'''
+ "- **Go back to** `[RUNTIME_TESTED]`:" + s[s.index("\n- **Go back to** `[RUNTIME_TESTED]`:") + len("\n- **Go back to** `[RUNTIME_TESTED]`:"):s.index("\n", s.index("\n- **Go back to** `[RUNTIME_TESTED]`:") + 1)])
rep("`execution` (`first_match`; `run_all` was not run)", "`execution` (`first_match`, or `run_all` to run the branch of every decision that matches; both ran)")
rep("`has_branches` (`1` or `0`), `include_otherwise` (`0`).", "`has_branches` (`1` or `0`), `include_otherwise` (`1` adds an Otherwise branch, `0` none; both ran).")
addafter("- **Decision** `[RUNTIME_TESTED]`", " **The Otherwise branch** is one more Decision row, placed after the answer branches, with `label` and `answer` both empty; it needs `include_otherwise` `1` on the Make a decision step and runs when no decision matches (test 27: three incidents took the Test, Default and Otherwise branches).")

# ---- Appendix C
ROW = "| Recurrence trigger, forms `once`, `daily`, `weekly`, `monthly` (test 25) | Start time set five minutes ahead | Four executions at 17:14:01 UTC, the minute set (9:14 AM Pacific). Next runs scheduled for the next day, seven days later and one month later; none for `once` |"
rep(ROW, ROW + '''
| Flow error handler: Top Level Try with three steps, the second failing; Top Level Catch with one step (test 26, flow A) | One incident | `TT26A step 1 ran`; step 3 did not run; `TT26A handler ran, code [1] message [No record found in Look Up Record action. …]`; execution `COMPLETE` |
| Visual Task Board Spoke, all 14 actions from catalog lines (test 26, flow V; test 27, flow V) | Two incidents | Boards `TT26 board INC0010086`, `TT26 flex …`, `TT26 guided …`; lanes `TT26 lane A` and `TT26 lane B2`; card for the incident in lane B2, unassigned; no members left; lane list returned once the board was passed as `{"value":"<sys_id>"}` |
| Knowledge Management trigger with Publish Article (test 26, flow K) | A test knowledge base naming the flow, one draft article, Publish clicked | Article `KB0010001` `published`; `meta` = `TT26K publish flow ran for KB0010001` |
| Recurrence trigger, forms yearly, every 2 days, two weekdays, second Tuesday, end date (test 26) | Start set to the day before; next run read from `sys_trigger`; not waited for | Next runs: 2027-03-15, the next evening, the next Tuesday, 2026-12-08, the next evening; `end_date_time` stored |
| Make a decision with `run_all`, two answer branches and an Otherwise branch (test 27, flow D) | Three incidents, description `test`, `prod`, `zzz` | `TT27D branch TEST`, `TT27D branch DEFAULT`, `TT27D branch OTHERWISE`; each then `TT27D after the branches` |
| Submit Catalog Item Request with reference, check box, date, date/time, yes/no and select box variables (test 27, flows E and Y) | Two incidents | `RITM0010005`: user sys_id, `true`, `2026-12-24`, `2026-12-24 18:30:00` (UTC), `beta`; yes/no stored `No` for `Yes` and `yes`, `Yes` for `true` and `1` |''')
rep("\nTest index: `verification/TESTS.md`.",
    "| **2.7** | 2026-11-20 | `flow_designer_prompt_v2.7.md` | Tests 26 and 27. **Flow error handler** (Top Level Try and Top Level Catch) with rules, run. **Knowledge Management trigger** run. The 14 **Visual Task Board** actions run (80 actions in all). Make a decision: `run_all` and the **Otherwise** branch. Catalog variables: reference, check box, date, date/time, yes/no (`true`/`false`, not `Yes`). Recurrence: yearly, relative weekday, several weekdays and end date scheduled as intended. |\n\nTest index: `verification/TESTS.md`.")
# Publication notice: licence, attribution and risk travel with the file.
rep("# ServiceNow Flow Designer Transpiler — System Prompt\n\n",
    "# ServiceNow Flow Designer Transpiler — System Prompt\n\n" + "> **Licence and risk.** This prompt is by Craig Talbert, written with help from Anthropic's Claude models, and licensed under CC BY-SA 4.0. What a model writes with it belongs to the user. Use it at your own risk: review every generated flow and test it on an instance that is not production first. Project, licence details and disclaimer: https://github.com/talbert/flow-designer-transpiler\n\n")
(R / "flow_designer_prompt_v2.7.md").write_text(s)
print("written", len(s), "chars,", s.count("\n") + 1, "lines")
