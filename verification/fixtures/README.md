# Fixtures

These files hold records that were read from personal ServiceNow developer instances while the prompt was checked.

- `dev435256/` (an instance on the Brazil release) and `zurich/` (instance dev203052, on the Zurich release) hold definition lists, parameter lists and small samples.
- The files in this top folder came from a third instance, dev391418, on the Australia release. `_provenance.txt` records that.
- These files are exports of this project's own test flows and actions: `platform_export_tt*`, the files in `dev435256/jsonparser/`, `platform_unload_action_*` (a copy of a stock action that was made for test 3), `test2_update_version_*` and the samples named `*_ui_saved.json`.
- `dev435256/full_catalog.json` lists every trigger, logic type, step type and published action on the test instance, with its inputs and outputs. It gives identifiers, names and types. ServiceNow's description text is not in it.

Full copies of the flows and actions that ServiceNow ships are not here. If you want that material, two tools read it from your own instance. Both need the `now-sdk` command and a saved login (see the README). Both **write over a file in this folder**, so run them only when you mean to:

- `verification/tools/build_full_catalog.py` reads the full definition list, with ServiceNow's description text, and writes over `dev435256/full_catalog.json`. Do not commit that result to a public copy.
- `verification/tools/pull_usage.py` reads the stored step values of the flows on the instance and writes them to `dev435256/action_usage.json`.

The identifiers, names and interface details here belong to ServiceNow. They are here because a flow cannot be written without them.
