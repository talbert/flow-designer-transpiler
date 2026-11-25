# Test index

Each folder named `test_import*` holds the update set for one test, and a manifest that lists what is in it. Almost every update set was imported and committed on a personal developer instance. One folder holds two files, and one update set was only previewed. The table says which.

- The first two folders were tested on instance dev203052. All the others were tested on dev435256, on the Brazil release.
- A flow or action name starts with `TT` and the test number. For example, `TT19 Compact REST` belongs to test 19.
- Some folders are a second or third attempt. The first attempt found a mistake, the rule was corrected, and the test ran again.
- This page says what each test was for. The results are in Appendix C of the prompt.

| folder | what it tested | flows and actions in the update set |
|---|---|---|
| `test_import` | First import test. One flow: a record trigger, two lookups and an If. No step writes data. | Transpiler Test 20261014 |
| `test_import_20261015` | Second import test. Adds an Else branch. Also sets the flow's `version` field to 2, which the first test showed is needed. | Transpiler Test 20261015 |
| `test_import_20261119a` | Smallest working flow shapes, the label cache, and the Daily and Service Catalog triggers. | TT3a Min A names only; TT3a Min B ids no boilerplate; TT3a Full with label cache; TT3a Daily; TT3a Catalog |
| `test_import_20261119b` | A subflow, and a flow that uses built-in action steps. | TT3b Subflow; TT3b Actions |
| `test_import_20261119c` | A generated custom action in the full shape. | TT3d Generated Action (action) |
| `test_import_20261119d` | A generated custom action in the full shape, next version. | TT3e Generated Action (action) |
| `test_import_20261119e` | First runtime test: record created and updated triggers, approval, notification, a subflow call, and the Weekly, Monthly and Run Once triggers. | TT4 Subflow; TT4 Runtime Created; TT4 Runtime Updated; TT4 Runtime Approval; TT4 Runtime Notification; TT4 Weekly; TT4 Monthly; TT4 Run Once; TT4 Scratch Action (action) |
| `test_import_20261119f` | The Created or Updated trigger, the Repeat trigger, and Weekly with a day name. | TT5 Runtime Created or Updated; TT5 Repeat; TT5 Weekly with day name |
| `test_import_20261119g` | Activation by the API call, with no click in the designer. | TT6 Subflow; TT6 Runtime No Click; TT6 Scratch Action (action) |
| `test_import_20261119h` | Parallel branches, Wait and Try, and three scheduled triggers. | TT7 Parallel Wait Try; TT7 Daily tonight; TT7 Weekly tonight; TT7 Monthly tonight |
| `test_import_20261119i` | A flow with several steps that pass data to each other. | TT8 Runtime Multi Step; TT6 Runtime No Click; TT8 Multi Step Action (action) |
| `test_import_20261119j` | A Service Catalog flow with a catalog item and a variable. | TT9 Runtime Catalog |
| `test_import_20261119k` | A flow and an action inside a scoped application. | TT10 Scoped Flow; TT10 Scoped Action (action) |
| `test_import_20261119l` | The payload shape that the Fluent SDK writes, sent through an update set. This folder holds two files: the second and third attempts. | TT12 SDK Shape Via Update Set |
| `test_import_20261119m` | A compact draft, activated in the designer. | TT14 Compact Studio Activate |
| `test_import_20261119n` | Compact mode with many parts at once: a custom action, a subflow, a main flow, and flows with catalog, daily and repeat triggers. | TT13 Subflow; TT13 Compact Catalog; TT13 Compact Daily; TT13 Compact Main; TT13 Compact Repeat; TT13 Action (action) |
| `test_import_20261119o` | A compact flow in the global scope. | TT16 Compact Global |
| `test_import_20261119p` | A compact custom action with a Script step, published by the API call. | TT17 Compact Script Publish |
| `test_import_20261119q` | A compact custom action with a JSON Parser step. | TT18 Compact JSON Parser; TT18 JSON Parser Action (action) |
| `test_import_20261119r` | The rest of the compact constructs: event, email, Do Until, loop control, approval, notification, a REST step and the scheduled triggers. | TT19 Compact Event Email Until; TT19 Compact Updated; TT19 Compact Approval; TT19 Compact Notification; TT19 Compact Loop Control; TT19 Compact REST; TT19 Compact Weekly; TT19 Compact Monthly; TT19 Compact Run Once; TT19 REST Action (action) |
| `test_import_20261119s` | The REST step, second attempt. | TT19b Compact REST; TT19b REST Action (action) |
| `test_import_20261119t` | The REST step, third attempt. | TT19c Compact REST; TT19c REST Action (action) |
| `test_import_20261119u` | Seven actions written from their catalog lines only. | TT20 Catalog Actions |
| `test_import_20261119v` | Create or Update Record with its coalesce fields. | TT20b Create or Update |
| `test_import_20261120a` | Many more actions from catalog lines: waits, attachments, email, record helpers, change helpers and catalog actions. | TT21A Waits and Attachments; TT21B Email Actions; TT21C Record Helpers; TT21D Change Helpers; TT21E Catalog Actions |
| `test_import_20261120b` | Make a decision, Go back to, Dynamic Flow and Append to Flow Variables. | TT22A Decision and Go Back; TT22B Decision Branches and Dynamic Flow; TT22C Append To Flow Variables |
| `test_import_20261120c` | The Inbound Email, SLA Task and Recurrence triggers. | TT23A Inbound Email; TT23B SLA Task; TT23C Recurrence |
| `test_import_20261120d` | The catalog actions one at a time, to find the one that failed. | TT21E1 Submit Catalog Item; TT21E2 Record Producer; TT21E3 Catalog Item Variables; TT21E4 Object To String Array |
| `test_import_20261120e` | Corrected re-runs of the catalog, email, record and change actions. This set was previewed only and not committed, because a name collided. | TT21E5 Submit Catalog Item JSON; TT21E6 Record Producer JSON; TT21B2 Email Actions; TT21C2 CI Support Group; TT21D2 Change Helpers; TT21A2 Copy Attachment; TT22C Append To Flow Variables |
| `test_import_20261120e2` | The same re-runs, second round. | TT21E5 Submit Catalog Item JSON; TT21E6 Record Producer JSON; TT21B2 Email Actions; TT21C2 CI Support Group; TT21D2 Change Helpers; TT21A2 Copy Attachment |
| `test_import_20261120f` | Append to Flow Variables with a one-item list. | TT22C2 Append List Form |
| `test_import_20261120g` | Inbound Email with an empty reply table, and one more form of catalog item inputs. | TT23A2 Inbound Email New; TT21E7 Submit Catalog Item Guess |
| `test_import_20261120h` | How to write catalog variable values: another attempt. | TT21E8 Submit Catalog Item Inputs; TT21E9 Record Producer Inputs |
| `test_import_20261120i` | How to write catalog variable values: another attempt. | TT21E10 Submit Catalog Item Inputs; TT21E11 Record Producer Inputs |
| `test_import_20261120j` | How to write catalog variable values: the form that works. | TT21E12 Submit Catalog Item Inputs; TT21E13 Record Producer Inputs |
| `test_import_20261120k` | Append to Flow Variables from the prompt's own rules, Wait For Message, Send Message and Wait For Email Reply. | TT24A Append From Rules; TT24B Wait For Message; TT24C Send Message; TT24D Wait For Email Reply; TT24 Send Flow Message (action) |
| `test_import_20261120l` | Recurrence: once, daily, weekly and monthly. | TT25 Recurrence Once; TT25 Recurrence Daily; TT25 Recurrence Weekly; TT25 Recurrence Monthly |
| `test_import_20261120m` | The flow error handler, the Visual Task Board actions, the Knowledge Management trigger and more Recurrence forms. | TT26A Error Handler; TT26V Visual Task Board; TT26K Knowledge Publish; TT26R Recurrence Yearly; TT26R Recurrence Every2Days; TT26R Recurrence TwoWeekdays; TT26R Recurrence SecondTuesday; TT26R Recurrence EndDate |
| `test_import_20261120n` | Make a decision with run-all and Otherwise, catalog variable types, and board lanes. | TT27D Decision Run All Otherwise; TT27E Catalog Variable Types; TT27V Board Lanes |
| `test_import_20261120o` | A Yes/No catalog variable. | TT27Y Yes No Variable |
