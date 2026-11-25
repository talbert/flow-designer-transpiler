# Licensing

Copyright (c) 2026 Craig Talbert.

## Two licences

The licence depends on the kind of file.

| what | licence |
|---|---|
| The prompt (`flow_designer_prompt_v*.md` and everything in `archive/`), the README files, the test index and the other documents | [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE) (CC BY-SA 4.0) |
| Source code: every `.py`, `.ts`, `.js` and shell file, the commit hook and the workflow file | [MIT](LICENSE-MIT) |

Some files need a clearer answer:

| file | answer |
|---|---|
| Test update sets in `verification/test_import*/` (all of them, also the first two that are not named `TT`), their `manifest.json` files, the `.diff` files, `verification/release_probe/*.json` and `FILE_ID.DIZ` | Written for this project. CC BY-SA 4.0. |
| Code samples inside the prompt (Python, shell, JavaScript) | You may use them under MIT as well as under CC BY-SA 4.0. |
| `verification/sdk_probe*/src/` | Written for this project. MIT. |
| `verification/sdk_probe*/update/` and `generated/keys.ts` | Output of ServiceNow's Fluent SDK, built from the sources above. The author claims no rights in the parts the SDK wrote. |
| In `verification/fixtures/`: `platform_export_tt*`, the files in `dev435256/jsonparser/`, `platform_unload_action_*` (a copy of a stock action that was made for test 3), `test2_update_version_*` and the samples named `*_ui_saved.json` | Exports of this project's own test flows and actions. The project's part is CC BY-SA 4.0. The record structure is ServiceNow's. |
| Every other file in `verification/fixtures/` | Records read from ServiceNow's platform: identifiers, names, types and small samples. They belong to ServiceNow. See below. |

## What a model writes is yours

This is an extra permission from the author. It is added to CC BY-SA 4.0. It covers the author's own work. If other people add to this project later, they are asked to give the same permission.

A model or a person can use the prompt to write flows, update sets, XML and other output. That output does not count as a copy or a changed version of the prompt. In the words of the licence, it is not Adapted Material. The author claims no rights in it. You do not have to give credit for it, and you do not have to share it under the same licence. This is also true when the output holds pieces of the prompt's examples, templates and identifiers.

Share-alike still applies to the prompt itself. If you change the prompt and pass your version to other people, your version has the same licence.

## What the licences do not cover

The prompt's lists and the files in `verification/fixtures/` hold ServiceNow's identifiers, definition names, interface details and exported platform records. They belong to ServiceNow. They are here for reference, and because a flow cannot be written without them. The licences above give you no rights in them.

"ServiceNow", "Flow Designer" and "Workflow Studio" are trademarks of ServiceNow, Inc. This project is not affiliated with ServiceNow, and ServiceNow does not endorse or support it. Its author is not currently affiliated with ServiceNow.

## No warranty

Both licences say that the material comes with no warranty. [DISCLAIMER.md](DISCLAIMER.md) says the same in plain words and adds the risks of this project. The disclaimer is not a condition of either licence.
