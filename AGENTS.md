# Agent entrypoint

Before creating or updating any build, version, release workflow or pipeline
helper, initialize the pinned submodules with
`git submodule update --init --recursive` and read
[`plugin-template/SKILL.md`](plugin-template/SKILL.md), followed by its linked
pipeline contract and development guide. Nested skills are not automatically
discovered; this explicit entrypoint is mandatory.

The canonical source is the `plugin-template` gitlink, not a floating branch or
download. Edit consumer configuration in `pipeline/example.json`, regenerate
through that pin and run `python3 scripts/check_tutorial_pipeline.py`.
Never hand-edit generated files listed in
`.github/plugin-pipeline-generated.json`. Keep tutorial prose, product source
and consumer checks outside generated ownership.

Preserve the historical greeting behavior and SDK gitlink. The only
release-facing actions are **Bump version** and **Build**; **Build and Test**
is separate unsigned validation. Never dispatch signing or publication, change
credentials, merge pull requests or reuse a renamed repository's old URL as
part of tutorial maintenance.
