# Flow Designer Transpiler

This is a system prompt. With it, a language model can write ServiceNow Flow Designer flows, subflows and custom actions as an update set that you can import. The repository also holds the tools and tests that were used to check the prompt.

This is an independent, personal project. It is not affiliated with ServiceNow, and ServiceNow does not endorse or support it. Its author is not currently affiliated with ServiceNow. "ServiceNow", "Flow Designer" and "Workflow Studio" are trademarks of ServiceNow, Inc.

**Use it at your own risk.** A model can write a wrong flow, and a wrong flow can change or delete records. Read [DISCLAIMER.md](DISCLAIMER.md) before you use anything here.

## When to use it

ServiceNow has its own tool for writing flows as code: the Fluent SDK. If you are building a new flow inside a Fluent application, use the SDK. This prompt is for the jobs the SDK does not do:

- You must deliver an **update set**.
- You are **turning old server-side scripts into flows**: business rules, scheduled jobs, script actions.
- Your custom action needs a **REST step** or a **JSON Parser step**.
- You want to **read or check flows that already exist** on an instance. For that you must decode the records that Flow Designer writes.

The prompt says the same thing at its top. It tells the model to recommend the SDK when the SDK is the better tool.

## Quick start

1. Give the file **`flow_designer_prompt_v2.7.md`** to a capable model as its system prompt. The model needs two things:
   - **A long context window.** The prompt is about 540 KB. About a third of it is a list of trigger, logic and action definitions. The rest is rules, examples and test records.
   - **A tool that runs code.** Flow Designer stores step values as compressed text (gzip, then base64). The model must run code to make them.
2. Describe the flow you want. Give the trigger, the conditions, the steps, the table and the fields. Say if the target is the global scope or an application.
3. The model first shows you its plan for the flow and waits for your OK. Then it gives you one update-set XML file and a list of steps to follow after the import.
4. Use an instance that is **not production**. Open `System Update Sets > Retrieved Update Sets`. Import the XML, **preview** it, fix any errors and **commit** it. Then read the commit log and look for errors.
5. Publish and activate. In the designer, open each subflow and each custom action and choose Publish. Then open each flow and choose Activate. Or send the activation call that the model gives you (Section 13.1 of the prompt). That one call publishes the actions and subflows and activates the flows, and you do not need to open the designer. An administrator must send it.
6. Test with a real record. A flow with a record trigger does not start when you commit an update set.

Read the flow before you activate it. The flow that you imported is the flow that runs.

## How much you can trust it

Each rule in the prompt has a tag. The tag tells you how the rule was found.

| tag | meaning |
|---|---|
| `[RUNTIME_TESTED]` | A flow built from the rule was imported and activated, and it ran. |
| `[IMPORT_TESTED]` | The XML imported, opened in the designer and activated. |
| `[PLATFORM_EXPORT]` | The rule matches a file that the platform itself wrote. |
| `[SDK_SOURCE]` | The rule matches the source code of ServiceNow's Fluent SDK, the tool that ServiceNow itself uses to write flows. This alone does not mean the rule was import-tested. |
| `[DOCUMENTED]` | ServiceNow's documentation says it. |
| `[OBSERVED]` | The rule was checked against records on real instances. |
| `[REVERSE_ENGINEERED]` | The rule was worked out from exported files. Nobody confirmed it another way. Look here first when an import fails. |
| `[TARGET_VERIFY]` | You must check this on your own instance before you trust it. |

The tests ran on personal developer instances, mostly on the Brazil release. Other releases and other instance settings can behave differently. The update-set format for flows is not a public interface. The path of the activation call is not documented. ServiceNow can change both.

**Status.** Scripts were written from the rules, and those scripts built flows that ran. But no model has yet been given the prompt and asked to write flows with no help. Treat what the model writes as a draft. Review it on an instance that is not production.

## What is in the repository

| path | what it is |
|---|---|
| `flow_designer_prompt_v2.7.md` | The current prompt. Its version history is at the end. |
| `archive/` | Every earlier version and the dated drafts. |
| `verification/tools/` | Python tools that build and check test flows, and the `apply_patches_*` scripts that built most versions from the one before. |
| `verification/test_import_*/` | The update-set XML and the manifest for each test. |
| `verification/fixtures/` | Definition lists and small samples read from developer instances. |
| `verification/TESTS.md` | An index of the tests: what each one was for and what is in it. |
| `verification/compact_reference.md`, `verification/sdk_vs_prompt_comparison.md` | Separate copies of the text in Appendices E and F of the prompt. The second one is a little older than the appendix. |
| `verification/sdk_probe*/`, `verification/release_probe/` | Fluent SDK sources with what the SDK built from them, and a release check. They were used in testing. Only `sdk_probe/` is a complete project. |
| `verification/*.diff` | Differences between the dated drafts. |
| `tools/check_public_safe.py` | A check that keeps instance names, work items, addresses and passwords out of this repository. |

## Versions

The version is in the file name: `flow_designer_prompt_v<major>.<minor>.md`. The minor number goes up when rules are added or corrected. The major number goes up when the normal way of building a flow changes.

## Running the tools

Some tools need nothing but Python: `knowledge_check.py`, `render_catalog.py`, `fdlib.py`, `compactgen.py`, `actgen.py` and `tools/check_public_safe.py`.

Other tools read from a ServiceNow instance: `sn.py`, `catalog.py`, `runs.py`, `checkb.py`, `checklog.py`, `runcheck.py`, `pull_usage.py`, `build_full_catalog.py`, `release_probe/probe.py` and some of the `build_test*` scripts. For those you need:

- ServiceNow's `now-sdk` command, with a saved login for your instance.
- `FDT_SDK_ALIAS`: the name of that saved login. The default is the author's own, so set this.
- `FDT_SDK_DIR`: the folder where `now-sdk` should run. The default is the current folder.

The `build_test*` and `apply_patches_*` scripts are kept as a record of what was done. They were written for one test each and are not general tools.

## Words used here

- **Update set:** a file of changes that you move from one ServiceNow instance to another.
- **Preview and commit:** the two steps of loading an update set. Preview checks it. Commit applies it.
- **Scope:** the application that a record belongs to. "Global" means no special application.
- **System prompt:** the instructions that a model gets before the conversation starts.
- **Context window:** how much text a model can read at one time.
- **Fixture:** a saved sample of real records that tests are checked against.
- **Manifest:** a short file that lists what is in a test folder.
- **Hook:** a check that git runs by itself before a commit.

## How to help

The most useful thing you can send is a correction from another release. Tell us the release and patch, the rule, what you imported and what the instance did.

Before you commit, turn on the local check:

```
git config core.hooksPath .githooks
```

The check has short lists of allowed instance hosts, email domains and application scopes. It stops a commit that has anything else, and it stops work-item numbers. It also looks inside compressed values. Do not send anything from an instance that belongs to your employer or to a customer.

## Credits

Written by Craig Talbert, with help from Anthropic's Claude models: Claude Opus 4.6 through Opus 5.5, and Claude Fable 5 through 5.2.

## Licence

- The prompt and the documents: [CC BY-SA 4.0](LICENSE).
- The source code: [MIT](LICENSE-MIT).
- **What a model writes with the prompt is yours.** A flow or update set that a model writes does not count as a copy or a changed version of the prompt. You do not have to give credit for it or share it. This is true even when it holds pieces of the prompt's templates.

ServiceNow's identifiers and interface details in the lists and fixtures belong to ServiceNow. They are here because a flow cannot be written without them. See [LICENSING.md](LICENSING.md) for the details and [DISCLAIMER.md](DISCLAIMER.md) for the risks.
