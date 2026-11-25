# Transpiler test import — run sheet (dev203052, Zurich P10)

**File:** `transpiler_test_20261014.xml` (generated 2026-10-14 21:03:03 UTC from `flow_designer_prompt20261014.md`)
**Update set:** Transpiler Test 20261014 (prompt 20261014)
**Flow:** Transpiler Test 20261014 — `sys_hub_flow` sys_id `94948049ee30ea1044eef0c0111e0c42`

> This run sheet is kept as a record. These are the steps that were followed on the author's developer instance, dev203052. The links point at that instance and will not work for you.

## What it contains (one flow, nothing that writes data)
- Trigger: **Created** on `incident`, condition `short_description=TRANSPILER_TEST_NEVER_MATCH_20261014` (never matches)
- Step 1 (order 1): Look Up Record — `sys_user` where `user_name=admin`
- Step 2 (order 5): If — "Admin user found" (`Record` of step 1 is not empty)
- Step 3 (order 10, inside the If): Look Up Record — `sys_user_group` where `nameISNOTEMPTY`
- Step 4 (order 15): End
- Plus the `sys_flow_record_trigger`, `sys_hub_flow_version`, snapshot mirror, and trigger plan

## Steps (each is a write on dev203052)
| # | Do this | Pass looks like |
|---|---|---|
| 1 | Open [Retrieved Update Sets](https://dev203052.service-now.com/sys_remote_update_set_list.do) → Related Links → **Import Update Set from XML** → upload the file | Update set appears with State = Loaded |
| 2 | Open it → **Preview Update Set** | Note the exact text of any preview problem; ideally there is none |
| 3 | **Commit Update Set** | Commits without errors |
| 4 | Run read-only check **A**: did every record land as sent | — |
| 5 | Open the flow: [sys_hub_flow record](https://dev203052.service-now.com/sys_hub_flow.do?sys_id=94948049ee30ea1044eef0c0111e0c42) → open it in Flow Designer / Workflow Studio | Trigger, 2 lookups, If (with the pill), End all render |
| 6 | Click **Activate** / **Publish** (whichever is offered). If it is greyed out, stop | Publishes without errors |
| 7 | Run read-only check **B** and compare what the platform regenerated with what was sent | — |

Do not use **Test** on the flow; it is not needed.

## Cleanup afterwards (these are writes)
Delete the flow `94948049ee30ea1044eef0c0111e0c42` (deleting in Flow Designer removes its snapshot, steps, trigger plan), then check for leftovers:
`sys_flow_record_trigger` `401a82fb9916261fffc2e961a6adc0b2`, `sys_hub_flow_version` `9e1cacca085c713aaa166571c2647625`, `sys_flow_trigger_plan` `8b86df21ad4e91e20b1376c91aa5010c`, and the retrieved update set `ac5a2c76a0e4dd1aefe7ecd96404ca48`.

## Prompt findings from building this (fixed in later versions)
1. **End block parent:** Section 3.5's nesting example shows End with an empty `parent_ui_id`; Section 7.5.4 says End's `parent_ui_id` = the opening If's `ui_id`. Live Zurich data matches 7.5.4 (e.g. End `459d90ba…` → If ui `6d813392…`). The 3.5 example is wrong. This file follows 7.5.4.
2. **Pill output names are case-sensitive:** Look Up Record's output element is `Record` (capital R). Section 7.2.1 examples use lowercase `.record`.
3. **Template gaps filled from read-only Zurich fixtures:**
   - 7.4.1 lists 7 inputs but gives ids for only table/condition/run_on_extended and no full entry objects; used the 7 live Zurich entries (run_when_setting 1e4859f3…, run_flow_in 3f1b9e4e…, run_when_user_setting ed7a5537…, run_when_user_list f89c5177…).
   - 7.3.3 gives ids/types but no parameter objects for Look Up Record; used live Zurich parameter objects, converted to the full shape per the 7.3 note.
   - Section 3.1 now says to emit sys_flow_record_trigger but gives only a field list, no XML template; built from the Zurich fixture fields.

All generated sys_ids/ui_ids are in `manifest.json` for the read-back.
