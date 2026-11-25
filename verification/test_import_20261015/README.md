# Transpiler test import: run sheet (dev203052, Brazil Patch 1)

**File:** `transpiler_test_20261015.xml` (generated 2026-10-15 16:00:24 UTC from `flow_designer_prompt20261015.md`)
**Update set:** Transpiler Test 20261015 (prompt 20261015)
**Flow:** Transpiler Test 20261015. `sys_hub_flow` sys_id `1f521c92ac13a98c4cde803feb57be31`

> This run sheet is kept as a record. These are the steps that were followed on the author's developer instance, dev203052. The links point at that instance and will not work for you.

## What it contains
One flow. No step writes data.

- **Trigger:** Created on `incident`, condition `short_description=TRANSPILER_TEST_NEVER_MATCH_20261015`. The condition never matches.
- **Step 1 (order 1):** Look Up Record on `sys_user` where `user_name=admin`.
- **Step 2 (order 5):** If "Admin user found", true when step 1's `Record` is not empty.
- **Step 3 (order 10, inside the If):** Look Up Record on `sys_user_group` where `nameISNOTEMPTY`.
- **Step 4 (order 15):** Else, with `connected_to` set to the If.
- **Step 5 (order 20, inside the Else):** Look Up Record on `sys_user` where `user_name=guest`.
- **Snapshot:** a mirror of the flow.

## What changed from the 20261014 test
| Change | Why |
|---|---|
| `version` = **2** (was 1) | With 1, the flow opened empty in Workflow Studio |
| Flow imports **inactive** | Matches the platform's own export; activating builds the trigger record and plan |
| No `sys_flow_record_trigger`, `sys_hub_flow_version` or trigger plan records | The platform's own export has none of them |
| 3 cleanup lines removed | The tables do not exist: `sys_hub_flow_context`, `sys_hub_flow_output_v2`, `sys_flow_trigger_plan_snapshot` |
| End replaced by **Else** | End is "End Flow", which stops the flow; it does not close an If |
| Brazil fields added; fields that don't exist on step records removed | Matches the platform's own export |

## Steps (each one is a write on dev203052)
| # | Do this | Pass looks like |
|---|---|---|
| 1 | Open [Retrieved Update Sets](https://dev203052.service-now.com/sys_remote_update_set_list.do). Under Related Links, click **Import Update Set from XML** and upload the file | Update set shows State = Loaded |
| 2 | Open it and click **Preview Update Set** | No problems. If there are any, note the exact text |
| 3 | Click **Commit Update Set** | The [update set log](https://dev203052.service-now.com/sys_update_set_log_list.do?sysparm_query=sys_created_onONToday%40javascript%3Ags.beginningOfToday()%40javascript%3Ags.endOfToday()%5Estatus%3DError) shows no **Error** rows |
| 4 | Run read-only check **A**: did every record land as sent | — |
| 5 | Open the [flow record](https://dev203052.service-now.com/sys_hub_flow.do?sys_id=1f521c92ac13a98c4cde803feb57be31) in Workflow Studio | You see the trigger, 3 lookups, the If and the Else. **If it is empty, stop** |
| 6 | Click **Activate** | The flow activates without errors |
| 7 | Run read-only check **B** and compare what the platform built with what was sent | — |

You don't need **Test** on the flow.

## Cleanup afterwards (these are writes)
- **This test:** delete flow `1f521c92ac13a98c4cde803feb57be31` and retrieved update set `8f8f707661e644edb20c55aedf182586`.
- **The 20261014 test:** delete flow `94948049ee30ea1044eef0c0111e0c42`, then check for leftovers:
  - `sys_flow_record_trigger` `401a82fb9916261fffc2e961a6adc0b2`
  - `sys_hub_flow_version` `9e1cacca085c713aaa166571c2647625` and `e77b513753bb87d0bc30d7f0a0490e10`
  - `sys_flow_trigger_plan` `8b86df21ad4e91e20b1376c91aa5010c`
  - retrieved update set `ac5a2c76a0e4dd1aefe7ecd96404ca48`

## Gaps filled from read-only fixtures
The prompt doesn't spell these out in full:
- **Record Create trigger inputs (7.4.1):** the prompt gives ids for only 3 of the 7 inputs. The test used the 7 live entries; Brazil Created triggers have the same 7 (30 of 30).
- **Look Up Record parameter objects (7.3.3):** the prompt gives no parameter objects. I used the live ones.

All generated sys_ids and ui_ids are in `manifest.json` for the read-back.
