"""Builds flow_designer_prompt20261119e.md from flow_designer_prompt20261119d.md (left untouched).
Compact mode becomes the default; Appendix E (compact reference, generated from the tested files), Appendix F (SDK source comparison) and Appendix G
(legacy material moved out of the main text, unchanged) are added; the activation section gains the documented facts; a few statements are corrected."""
import pathlib, re
P = pathlib.Path(__file__).parent.parent.parent; V = P / "verification"
src = (P / "archive" / "flow_designer_prompt20261119d.md").read_text(); t = src; n = 0
def rep(old, new):
    global t, n
    assert t.count(old) == 1, f"expected 1 of {old[:70]!r}, found {t.count(old)}"
    t = t.replace(old, new); n += 1
def take(start, end):
    """Cut the block from the line starting with `start` up to the line starting with `end`; return it."""
    global t, n
    a = t.index("\n" + start) + 1; b = t.index("\n" + end, a) + 1
    blk = t[a:b]; t = t[:a] + t[b:]; n += 1
    return blk

# ---- 1. compact mode: remove the old 0.3 (its content is rewritten below as the default)
old03 = take("### 0.3 Compact mode:", "**The platform normalizes on activation.**")
COMPACT = '''## THE DEFAULT: COMPACT MODE `[RUNTIME_TESTED]`

**Unless one of the exceptions at the end of this section applies, generate compact payloads.** A compact payload is a *draft* with short blob entries and no snapshot. Activation on the target completes it: the platform fills in every parameter detail, builds the snapshot and the trigger records, and compiles the plans. This is the shape ServiceNow's own Fluent SDK writes. It removes the two riskiest parts of the full shape, the snapshot mirror and the long per-input parameter objects.

**What was tested** (Brazil Patch 1, 2026-11-19; Appendix C): SDK-built compact payloads for a custom action, a subflow and four flows went unchanged through an update set and ran. Covered: record-created, Repeat, Daily and Service Catalog triggers; Look Up Record(s), Create Record, Update Record, Get Catalog Variables, Create Catalog Task; If, Else If, Else, For Each, Set Flow Variables, Try, Catch, Do the following in Parallel, Wait for a duration, Assign Subflow Outputs; a flow variable; a subflow call; a custom action call. Activated with the API call (Section 13.1) in a scoped application and in the global scope, and with the ordinary Workflow Studio Activate button (one flow). Not tested in compact form: Send Email, Send Notification, Fire Event, Ask For Approval, Do Until, End Flow, record-updated triggers, Weekly, Monthly and Run Once triggers, and a custom action with a REST step. For those, use the entry shape in rule 3 with the names and types from Section 7, and say in `CONFIGURATION_NOTES` that the construct was not tested in compact form.

**Rules** (Appendix E has the exact field lists and one decoded example per construct; follow it literally):

1. **Flow or subflow record:** `sys_hub_flow` with `status` `draft`, `active` `false`, `version` `2`, `type` `flow` or `subflow`, `access` `public`, `flow_priority` `MEDIUM`, `run_as`, `name`, `description`, `label_cache` (Section 7.10), and `generation_source` `fluent` (the value that was tested; Workflow Studio shows a small badge for it). `master_snapshot` and `latest_snapshot` stay empty. **Emit no `sys_hub_flow_snapshot` and no snapshot-section rows.**
2. **Children:** the trigger instance, action instances, logic instances, subflow-call instances, flow variables, subflow inputs and outputs, each kind preceded by its `DELETE … flow=<flow>^sys_idNOT IN<ids>` and each action instance followed by `DELETE sys_hub_alias_mapping source_id=<that action>` (Appendix E.1). Do not emit trigger, timer, catalog-trigger, plan or version records (Section 0).
3. **Blob entries are short.** Action `values`: `{"name":…,"value":…,"displayValue":…,"scriptActive":false,"parameter":{"type":"<the input's internal type>"}}`, one entry per input you set. Logic `values`: the six-key object (Section 7.5) whose entries are `{"id":"","name":…,"value":…,"displayValue":…,"children":[],"parameter":{},"scriptActive":false}`; Set Flow Variables entries carry the flow variable's sys_id as `id` in both `inputs` and `variables`; Wait entries carry the seven parameter ids (Section 7.5.11). Trigger entries: the shape in Appendix E.3 with `parameter` `{"type":…,"name":…,"label":…}` and `triggerInstanceSysId` `""`. Subflow-call entries: `{"name":…,"value":…,"displayValue":…,"parameter":{"type":…}}`. Encode as in Section 7.1.
4. **References use definition ids here, not snapshot ids.** A built-in action step sets `action_type` **and** `action_type_parent` to the `action_type` id in Section 5.2. A custom action call sets both to the action's `sys_hub_action_type_definition` sys_id. A subflow call sets `subflow` to the subflow's `sys_hub_flow` sys_id. No `compiled_snapshot`. (The snapshot-id rules in Section 0 belong to the full shape.)
5. **`ui_id`** is the row's sys_id written with hyphens (8-4-4-4-12). Nesting, `connected_to` and the Parallel `order` rule are as in Sections 3.5 and 7.5: Catch points at its Try; the first step in a Parallel Branch has `order` `<branch order>➛<own order>`. The tested files left `connected_to` empty on Else and Else If and that worked; the platform's own value is the opening If, which is also safe.
6. **Template values** (`values` of Create Record and Update Record, `ah_fields`): `field=value^field=value^EQ`. End with `^EQ`, and write a literal caret inside a value as `^^`.
7. **Pills and `label_cache`** are exactly as in Sections 7.2.1 and 7.10.
8. **Custom action:** `sys_hub_action_type_definition` with `state` `draft`, `active` `true`; then the step instance, its `sys_variable_value` and `sys_element_mapping` rows, the step's ext inputs and outputs, the action inputs and outputs and their `sys_documentation` rows (Appendix E.5). **No snapshot, no `sys_hub_action_plan`, and no `sys_complex_object`:** the `__action_status__` output uses the shared `co_type_name=FDACTIONSTATUS`, so the name clash in Section 0.2 cannot happen.
9. **Schedule times** are read in the activating user's time zone (Section 7.4.4). The SDK's source assumes UTC; the runtime result disagrees with it: a compact Daily blob of `03:40:00` became `11:40:00` UTC on the timer record for a Pacific-time user.
10. **Fresh ids every run**, a name prefix, and the pre-flight check (Section 0.2) still apply.
11. **Activation is part of the deliverable.** Until a compact flow is activated it is a draft and does not run. Give both ways: the API call with this output's sys_ids filled in (Section 13.1; list actions, subflows and flows together), and the manual way (open in Workflow Studio, Edit, Publish for a subflow or action, Activate for a flow).
12. **When replacing ids in an existing payload,** replace them inside the decoded blobs too and re-encode (`verification/tools/reident.py`).

**Use the full published shape (Sections 2 to 10) instead when:**

- the user asks for a payload that carries its own snapshot, for example to review in the XML exactly what will run or to match a platform export;
- a custom action needs a **REST step** (Section 10.0.3), which has no compact reference. Write that action in the full shape; the flows that call it may still be compact only if they point at the action by the ids rule 4 gives, which is **untested in a mixed set**, so prefer the full shape for the whole set;
- the target is a release where completion of short entries is unconfirmed. Check by importing one compact flow first, or use the full shape.

**Never mix the two inside one record:** short entries inside a *published* flow that has a snapshot gave "Corrupted flow" (Section 0, item 2).

---

'''
rep("## 0. IMPORT-TESTED RULES `[IMPORT_TESTED]`", COMPACT + "## 0. IMPORT-TESTED RULES `[IMPORT_TESTED]`")
rep("These rules come from seventeen generated flows", "Sections 0 to 10 describe the **full published shape** and what the platform does with it. They are the fallback mode and the reference for how the Flow Designer tables work; the default mode is the section above. These rules come from seventeen generated flows")
rep("This prompt's default is still the full published shape, because it works with or without the endpoint. Section 0.3 describes the SDK's shape as a second, compact mode.",
    "That shape is this prompt's default mode (the section before Section 0); it also activates with the ordinary Workflow Studio button.")
rep("When the flow arrives as a draft without a snapshot (Section 0.3), it builds the snapshot and completes the blob entries.", "When the flow arrives as a draft without a snapshot (compact mode), it builds the snapshot and completes the blob entries.")
rep("| Compact mode: the SDK's payload shape through an update set, then the activation call (Section 0.3) |", "| Compact mode: the SDK's payload shape through an update set, then the activation call |")

# ---- 2. corrections
rep("**Note:** Unlike conditions, `template_value` fields use simple `field=value` assignments, not query operators like `ISNOTEMPTY`, `CONTAINS`, etc. Each segment sets a field value on the target record.",
    "**Note:** Unlike conditions, `template_value` fields use simple `field=value` assignments, not query operators like `ISNOTEMPTY`, `CONTAINS`, etc. Each segment sets a field value on the target record.\n\n"
    "`[SDK_SOURCE]` `[RUNTIME_TESTED]` ServiceNow's generator ends a template value with `^EQ` and writes a literal caret inside a value as `^^` (`description=…^EQ` ran correctly in compact mode). Template values without `^EQ` also ran correctly in the full shape. Use `^EQ`, and always escape a caret.")
rep("| Group members, plus manager option `[OBSERVED]` | `ApprovesRejectsAnyG[<group>]\\|AnyM` |",
    "| Group members, then a second rule set after `\\|`; the suffix `M` marks a **manual** approval rule (`[SDK_SOURCE]`; not \"manager\") `[OBSERVED]` | `ApprovesRejectsAnyG[<group>]\\|AnyM` |")
rep("- It is the call ServiceNow's Fluent SDK makes after an install (`[SDK_SOURCE]`, `post-install.ts`). It is **not documented**.",
    "- **What the instance says about it** `[OBSERVED]`: Scripted REST API \"Workflow Automation Fluent APIs\" (namespace `now`, service id `wfa_fluent`), shipped in \"ServiceNow IDE Runtime Services\"; one operation, \"Activate Flows and Actions\", described as \"Bulk activate Flow Designer flows and subflows via sys_ids.\"; its script is protected. Its access rule (\"Workflow Automation Fluent ACLs\", REST endpoint, execute) requires the role **`flow_designer`**; admin also passes. There are no sibling operations (no deactivate, status or validate).\n"
    "- **What is documented** `[DOCUMENTED]`: the behavior, not the path. The SDK CLI page for `now-sdk install` has `--skip-flow-activation` with the note \"ServiceNow IDE version 4.1.1 or later must be installed to activate flows with this command\" (Zurich and Brazil doc branches; absent from Yokohama and Xanadu). SDK release notes first mention it in 4.5.0. Unverified, from the SDK's GitHub discussions: the IDE needs Zurich Patch 8 or later; a scriptable form `sn_fd.FlowAPI.publishFlowFromFluent()` / `publishActionFromFluent()` exists; publishing fails for flows in a non-global domain; a third-party client treats HTTP 207 as partial success.\n"
    "- It is the call ServiceNow's Fluent SDK makes after an install (`[SDK_SOURCE]`, `post-install.ts`). The endpoint path itself is **not documented** anywhere official.")
rep("6. **Generate the XML** — produce complete, valid update set XML following all patterns in this prompt.",
    "6. **Generate the XML** — in compact mode unless one of its exceptions applies (the section \"The default: compact mode\"); say which mode was used and why at the top of the answer. Produce complete, valid update set XML following all patterns in this prompt.")
rep("23. **Always give the activation call** (Section 13.1) beside the manual Publish and Activate steps.",
    "23. **Always give the activation call** (Section 13.1) beside the manual Publish and Activate steps.\n"
    "24. **Compact mode is the default.** Rules 1, 2, 7, 13, 19 and 20 describe the full published shape; in compact mode there is no snapshot section, entries are short, and calls point at definition ids (the section \"The default: compact mode\").")

# ---- 3. legacy blocks moved, unchanged, to Appendix G
leg1 = take("### 7.9 Legacy Reference:", "### 7.10 ")
leg2 = take("### 10.0.1 Older Skeleton", "### 10.1 ")
rep("### 7.10 `label_cache` Entries `[IMPORT_TESTED]`", "### 7.9 Legacy Reference (Strategy B)\n\nMoved unchanged to Appendix G.1. It documents the V1 tables with explicit mapping records and is not used for new output.\n\n### 7.10 `label_cache` Entries `[IMPORT_TESTED]`")
rep("### 10.1 Complex Objects (`sys_complex_object`)", "### 10.0.1 Older Skeleton\n\nMoved unchanged to Appendix G.2. It predates the platform export in 10.0 and was never import-tested; where it differs from 10.0, 10.0 wins.\n\n### 10.1 Complex Objects (`sys_complex_object`)")

# ---- 4. Appendix C rows, then Appendices E, F, G
C_ROWS = "\n".join([
 "| Compact mode, wide: SDK-built action, subflow, main flow (For Each, If / Else If / Else, subflow call, action call, Try / Catch, Parallel, Wait), Repeat, Daily and Catalog flows, unchanged through an update set, one activation call | Three incidents and one catalog order | `TT13 IF / ELSE IF / ELSE branch for …`; work note `TT13 var [start +abel.tuter +itil] subflow [Abel Tuter] action [retuT lebA]`; tasks `TT13 branch A`, `TT13 branch B`, `TT13 caught`; requested item `TT13 catalog flow ran, note [hello from TT13 compact]`; Repeat ran two minutes after activation |",
 "| Compact flow activated with the Workflow Studio button, no API call | Two incidents | `TT14 IF branch for INC0010019 found System Administrator`; `TT14 ELSE branch for INC0010020` |",
 "| Compact flow in the global scope, activation call with scope `global` | Two incidents | `TT16 IF branch for INC0010024 found System Administrator`; `TT16 ELSE branch for INC0010025` |"])
rep("\n\n---\n\n## APPENDIX D. Reading and Auditing Existing Flows", "\n" + C_ROWS + "\n\n---\n\n## APPENDIX D. Reading and Auditing Existing Flows")
E = (V / "compact_reference.md").read_text().rstrip("\n")
F = (V / "sdk_vs_prompt_comparison.md").read_text().rstrip("\n")
F = re.sub(r"^(#{1,5}) ", lambda m: "#" * min(len(m.group(1)) + 2, 6) + " ", F, flags=re.M)   # demote headings under the appendix
shift = lambda blk: re.sub(r"^(#{2,5}) ", lambda m: "#" * min(len(m.group(1)) + 1, 6) + " ", blk, flags=re.M)
t = t.rstrip("\n") + "\n\n---\n\n" + E + "\n\n---\n\n" + "\n".join([
 "## APPENDIX F. Comparison with the Fluent SDK Source `[SDK_SOURCE]`", "",
 "A line-by-line comparison of this prompt (copy 20261119d) with the SDK flow plugin source, made on 2026-11-19. Line numbers in it refer to that copy. **Nothing in this appendix was import-tested unless a line below says so; where it disagrees with a `[RUNTIME_TESTED]` or `[IMPORT_TESTED]` rule in the main text, the tested rule wins for the full shape.** It is kept whole because it records how ServiceNow's own generator writes each record, including logic types, triggers, actions and step types this prompt does not otherwise cover.", "",
 "**How the main disagreements were settled by the tests here:**", "",
 "- *Schedule time zone (1):* the platform reads the blob time in the activating user's zone. Tested in both shapes; the SDK's UTC assumption did not hold.",
 "- *Else / Else If `connected_to` (2):* the platform's own exports point at the opening If (80 of 80 and 67 of 67 live rows); the SDK's built output left it empty and ran. Both work; previous-sibling linking was not tested.",
 "- *Subflow and custom action references (3, 4):* snapshot ids in the full shape (52 of 53 and 351 of 400 live rows, and runtime-tested); definition ids in compact mode (runtime-tested). Each belongs to its mode.",
 "- *Catch, Set Flow Variables, Assign Subflow Outputs, Wait entries (5 to 8):* the SDK's forms are the compact forms in Appendix E and ran; the forms in Section 7.5 are the platform's exported forms and ran in the full shape.",
 "- *`__action_status__` (9):* the shared `FDACTIONSTATUS` ran in a compact custom action. A per-action `FD…` object is what the platform exports for a published action and is what clashed once (Section 0.2).",
 "- *Template values (10):* `^EQ` ran in compact mode; without it ran in the full shape.", "",
 F, "", "---", "",
 "## APPENDIX G. Legacy Material (moved out of the main text, wording unchanged)", "",
 "Kept for the table knowledge it holds. Not used for new output.", "",
 "### G.1 From Section 7.9", "", shift(leg1).rstrip("\n"), "",
 "### G.2 From Section 10.0.1", "", shift(leg2).rstrip("\n"), ""]) + "\n"
n += 1
out = P / "archive" / "flow_designer_prompt20261119e.md"; out.write_text(t)
print(f"{n} edits applied; {len(src)} -> {len(t)} chars; wrote {out.name}")
