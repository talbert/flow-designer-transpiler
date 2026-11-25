"""Build flow_designer_prompt_v2.3.md from v2.2: Appendix H (every trigger, logic type, step type and published action on the test instance, with inputs and outputs),
results of tests 20 and 20b (actions written from catalog lines), plain descriptions as input. Local files only. Every replacement must match exactly once."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_catalog as rc
R = pathlib.Path(__file__).parent.parent.parent
s = (R / "archive" / "flow_designer_prompt_v2.2.md").read_text()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
N = rc.COUNTS

rep("**Prompt version 2.2** (2026-11-19).", "**Prompt version 2.3** (2026-11-19).")

# a plain description is a valid input
rep("and produce valid **Update Set XML** that creates equivalent Flow Designer flows, subflows, or custom actions.",
    "and produce valid **Update Set XML** that creates equivalent Flow Designer flows, subflows, or custom actions. **A plain description of a flow, subflow or action is an equally valid input** "
    "(\"when an incident is updated to priority 1, look up the group's manager and ask for approval\"): build it from the same rules, choosing building blocks from Section 5 and Appendix H. "
    "Section 12 applies only when the input is a script.")

# compact rule 4: actions outside Section 5.2
rep("A custom action call sets both to the action's `sys_hub_action_type_definition` sys_id.",
    "A custom action call sets both to the action's `sys_hub_action_type_definition` sys_id. **Any other published action** (Appendix H) is written the same way: both fields = the sys_id on its Appendix H line "
    "(its definition id), one short entry per input set, `parameter.type` = the type printed for that input `[RUNTIME_TESTED]` (test 20: seven actions never used before, two of them in a spoke's scope called from a global flow).")

# Section 5 pointer
rep("Step types reference `sys_flow_step_definition`.",
    "Step types reference `sys_flow_step_definition`.\n\n"
    f"**The tables in 5.1 to 5.4 hold the definitions this prompt has generation rules for. Appendix H lists every definition found on the test instance** ({N['triggers']} triggers, {N['logic']} logic types, "
    f"{N['steps']} step types, {N['actions']} published actions with their inputs and outputs) and says what a line there is enough for.")

# critical rule 27 (inserted after rule 26)
i = s.index("26. **REST name-value items carry `attributes`**"); e = s.index("\n", i)
s = s[:e + 1] + ("27. **An action outside Section 5.2 is written from its Appendix H line**, in compact mode: definition id in both type fields, input names and types as printed, choice inputs set to a stored value from the brackets, "
                 "output pills spelled exactly as the output element is printed (capitals and spaces included). If the line has no `T`, say in `CONFIGURATION_NOTES` that the action was not run in testing. "
                 "**Create or Update Record needs `^coalesce_fields=<field>[,<field>]` at the end of `fields`** (Appendix H.0).\n") + s[e + 1:]

# Appendix C rows
anchor = "| Compact custom action with Script, REST and Script steps; pills in a query parameter and a header; echo endpoint |"
i = s.index(anchor); e = s.index("\n", i)
s = s[:e + 1] + ("| Compact flow of seven actions never used before, written from Appendix H lines only: Log, Create Task, Create or Update Record, Update Multiple Records, Add Worknote and Create Incident Task on Incident (both ITSM Spoke), Delete Record (test 20) | One incident | "
                 "Log row `TT20 log for INC0010040`; `TASK0020391` created and then updated by Update Multiple Records (`count` 1); work note `TT20 worknote via ITSM Spoke`; `TASK0020392` created by the spoke action and then deleted; "
                 "description `TT20 task [TASK0020391] upsert [created] count [1] itask [TASK0020392]`. A second incident: run `ERROR` at Create or Update Record (`Error during insert of sys_user`), because `fields` had no `coalesce_fields` |\n"
                 "| Create or Update Record with `^coalesce_fields=user_name` (test 20b) | Two incidents | `TT20b upsert [created] user [INC0010042]`, then `TT20b upsert [updated] user [INC0010043]`; one user row, updated once |\n") + s[e + 1:]

# Appendix H
fence = lambda rows: "```text\n" + "\n".join(rows) + "\n```\n"
H = f'''## APPENDIX H. Definition Catalog `[OBSERVED]` `[TARGET_VERIFY]`

Every trigger definition, flow logic definition, step type and published action found on the test instance (Brazil Patch 1 with IntegrationHub installed, read 2026-11-19 from `sys_hub_trigger_definition`, `sys_hub_flow_logic_definition`, `sys_flow_step_definition`, `sys_hub_action_type_definition` and their input and output tables). Test records are left out. The lists can be rebuilt for another release with `verification/tools/build_full_catalog.py` and `render_catalog.py`.

### H.0 How to read a line, and what it is enough for

```text
<T or -> <sys_id> | <name> | in: <input>, <input> | out: <output>, <output>
```

- **`T`** = generated from this prompt's rules and run on the test instance (Appendix C). **`-`** = never generated or run here.
- An input or output is `<element>:<internal type>`. `*` after the element = mandatory. `(table)` = the table a reference or document id points at. `[a/b/c]` = the stored values of a choice. `-` = none.
- `[package_private]` or `[private]` after a name = the action cannot be called from outside its own application.
- **These ids are the shipped record ids.** A definition exists on a target only if its application or plugin is installed there. For every non-Global action used, name its application in `CONFIGURATION_NOTES` and tell the user to check `sys_hub_action_type_definition` for the sys_id before import.

**Actions (H.4, H.5): a line is enough.** `[RUNTIME_TESTED]` In compact mode an action step is `action_type` = `action_type_parent` = the line's sys_id, plus one short entry per input you set (compact rule 3) with `parameter.type` = the printed type. Test 20 did this for seven actions that had never been used, with nothing but their lines; all seven ran, including two ITSM Spoke actions called from a global flow. The ten actions in Section 5.2 work with either id (the `action_type` id in 5.2, tests 12 to 19; the definition id printed here, test 20).

- **Outputs in pills:** spell the element exactly as printed, capitals and spaces included: `{{{{<ui_id>.Incident Task.number}}}}`, `{{{{<ui_id>.Record.number}}}}`, `{{{{<ui_id>.count}}}}` `[RUNTIME_TESTED]`.
- **Choice inputs:** the stored value (`info`), not the label (`Info`).
- **A line does not show conventions inside a value.** One is known: **Create or Update Record** finds the existing row by the fields named at the end of `fields`: `user_name=tt20b.user^first_name=TT20B^coalesce_fields=user_name` (no `^EQ`; several fields comma-separated) `[RUNTIME_TESTED]`. Without `coalesce_fields` the action inserts every time, and the run errors on a unique field. Other actions without a `T` may have conventions of their own; say so in `CONFIGURATION_NOTES` when you use one.

**Triggers (H.1): a line is NOT enough.** The table and condition of the record triggers and the day and time values of the schedules are not rows in `sys_hub_trigger_input`, so they are not printed here; the inputs printed are the advanced options. Generate only the triggers that have rules (Section 7.4, Appendix B, and the compact entries after the compact rules). For any other trigger, build the flow without it and follow Section 7.8.

**Flow logic (H.2): a line is NOT enough.** Nesting, `connected_to` and the six-key `values` object come from Sections 3.5 and 7.5. A logic type with `-` that is also absent from Section 5.3 (Decision, Placeholder, Top Level Try, Top Level Catch, Update Flow Template) has no rules in this prompt: do not guess its shape; follow Section 7.8.

**Step types (H.3): a line is NOT enough.** A step inside a custom action also needs its variable values, mapping rows and, for some types, extra records (Section 10). Only Script, REST and JSON Parser have rules. For another step type, use a Script step that does the same work, or call the matching action from the flow instead.

### H.1 Trigger definitions ({N['triggers']})

The `type` is the value of `trigger_type` on the trigger instance.

{fence(rc.S['triggers'])}
### H.2 Flow logic definitions ({N['logic']})

{fence(rc.S['logic'])}
### H.3 Step types ({N['steps']})

{fence(rc.S['steps'])}
### H.4 Actions in the Global scope ({N['global']})

{fence(rc.S['actions_global'])}
### H.5 Actions in other applications ({N['other']} in {N['scopes']} applications)

A `#` line names the application and its scope.

{fence(rc.S['actions_other'])}
---

'''
rep("## VERSION HISTORY", H + "## VERSION HISTORY")

# version history
i = s.index("| **2.2** | 2026-11-19 |"); e = s.index("\n", i)
s = s[:e + 1] + (f"| **2.3** | 2026-11-19 | `flow_designer_prompt_v2.3.md` | **Appendix H: the full definition catalog** ({N['triggers']} triggers, {N['logic']} logic types, {N['steps']} step types, {N['actions']} published actions, "
                 "with inputs, outputs and choice values). Tests 20 and 20b: seven actions never used before ran from their catalog lines alone; `coalesce_fields` rule for Create or Update Record; rule 27. "
                 "A plain description is named as a valid input. |\n") + s[e + 1:]
(R / "archive" / "flow_designer_prompt_v2.3.md").write_text(s)
print("written", len(s), "chars,", s.count("\n") + 1, "lines")
