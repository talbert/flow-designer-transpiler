"""Build flow_designer_prompt_v2.4.md from v2.3: value formats by input type (read from 1,364 action steps in shipped flows on the test instance) and
guidance on which catalog actions to reach for. Local files only. Every replacement must match exactly once."""
import pathlib
R = pathlib.Path(__file__).parent.parent.parent
s = (R / "archive" / "flow_designer_prompt_v2.3.md").read_text()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
rep("**Prompt version 2.3** (2026-11-19).", "**Prompt version 2.4** (2026-11-20).")
NEW = '''**Value format by input type** `[OBSERVED]`. Read from the 1,364 action steps of the flows shipped on the test instance (159 different actions). The type printed on a catalog line tells you how to write the value. `value` and `displayValue` may be the same text unless the row says otherwise.

| Printed type | How shipped flows write the value | Example |
|---|---|---|
| `string`, `string_full_utf8`, `multi_small`, `url`, `GUID` | Text, one pill, or text with pills | `Opened by field is blank for {{Created or Updated_1.current.number}}` |
| `table_name` | The table's name (786 of 804), or a pill | `incident` |
| `document_id` | Always one record pill (598 of 598) | `{{<ui_id>.Record}}`, `{{Created_1.current}}` |
| `reference` | One record pill (314), or a bare sys_id with the record's display value in `displayValue` (108) | `cea3ad767f4422104deb1630be86655a` |
| `choice` | The stored value from the brackets, never the label | `sort_asc` |
| `boolean` | `1` or `0` as text (310 of 328), or a pill. `true` and `false` were accepted in tests 19 and 20. Leave the entry out to keep the default | `1` |
| `integer`, `decimal` | The number as text, or a pill | `1000` |
| `conditions` | An encoded query, pills allowed inline, **no** `^EQ` at the end | `state=3^ORstate=4^ORstate=7`, `user={{subflow.user}}^inherited=false` |
| `template_value` | `field=value^field=value` (Section 7.2.2); end with `^EQ` when you write it | `state=10^EQ` |
| `field_name` | The column name on the table the action works on | `approval_history` |
| `glide_duration` | `1970-01-01 HH:MM:SS` for a fixed length (add days to the date for longer), or a pill | `1970-01-01 00:01:00` = one minute |
| `glide_date_time` | `YYYY-MM-DD HH:MM:SS`, or a pill | |
| `schedule_date_time` | A JSON object as text (Section 7.3, Ask For Approval `due_date`) | `{"action":"none","date_type":"actual","date":"{}","duration":1,"duration_type":"days","schedule":"","schedule_label":""}` |
| `approval_rules` | The rule text of Section 7.3 | `ApprovesAnyU[{{static.<user sys_id>}}]` |
| `slushbucket` | Comma-separated `<sys_id>:<table>` pairs | `<variable sys_id>:item_option_new,<variable sys_id>:item_option_new` |
| `json`, `records`, `glide_list` | Only ever one pill from an earlier step, a subflow input or a flow variable (18 of 18 for `json`); no literal was seen | `{{flow_variable.parsed_input}}` |
| `html` | HTML text. Shipped flows wrap each pill in a `<span class="data_parent_pill" … data-pillvalue="{{…}}">` element; a pill written plainly inside HTML was not tested | `<p>test body</p>` |
| `password2` | A pill only. Never write a secret into a flow | `{{subflow.password}}` |

**Which actions to reach for.** The catalog is long because shipped products bring their own helper actions. For a flow written from a description, choose in this order:

1. The actions with a `T`: they have run.
2. **General building blocks in the Global scope** (26, not yet run): Wait For Condition (the most used untested action: 56 shipped flows), Wait For Email Reply, Wait For Message, Add a Pause, Send SMS, SLA Percentage Timer, Look Up Attachment, Copy Attachment, Move Attachment, Delete Attachment, Get Attachments on Record, Check Attachment Readiness, Look Up Email Attachments, Move Email Attachments to Record, Associate Record to Email, Get Email Header, Get Latest Response Text From Email, Create Outage, Create Task Outage Relationship, Create Problem Record from Incident, Submit Catalog Item Request, Record Producer, Get Catalog Item Variables, Get Catalog Item from Task, Create Remote Table Record, Object To String Array.
3. **ITSM Spoke** (28 not yet run; two ran): incident, problem, change and request helpers such as Create Incident, Add Comment, Update Assignment Group, Create Standard Change Request.
4. **Messaging and boards** (58: Slack WebHooks, Connect Spoke, Visual Task Board Spoke, Omni-Experience): they need a connection, credential or board set up on the target. Name that need in `CONFIGURATION_NOTES`.
5. **Everything else** (about 336 helpers of single products such as Docker, CICD, Password Reset, App Engine, CMDB lifecycle, One API, and 29 marked private): use one only when the request names that product. When a plain Create Record, Update Record or Look Up Record does the job, prefer it.

'''
rep("**Triggers (H.1): a line is NOT enough.**", NEW + "**Triggers (H.1): a line is NOT enough.**")
i = s.index("| **2.3** | 2026-11-19 |"); e = s.index("\n", i)
s = s[:e + 1] + ("| **2.4** | 2026-11-20 | `flow_designer_prompt_v2.4.md` | Appendix H.0 gained **value formats by input type**, read from the 1,364 action steps of shipped flows, "
                 "and an order of preference for catalog actions (tested, general building blocks, ITSM Spoke, messaging, product helpers). |\n") + s[e + 1:]
(R / "archive" / "flow_designer_prompt_v2.4.md").write_text(s)
print("written", len(s), "chars,", s.count("\n") + 1, "lines")
