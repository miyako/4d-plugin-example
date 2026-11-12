# 4D Plugin Example

[English](README.md) | [日本語](README.ja.md)

A worked native 4D greeting plugin tutorial in
[`miyako/4d-plugin-example`](https://github.com/miyako/4d-plugin-example).
Product code and teaching material live here; executable pipeline code is
generated from the immutable `plugin-template` submodule.

## Greeting command

```4d
$greeting:=example_greeting("Miyako"; example_greeting_morning)
// "Good morning Miyako"
$automatic:=example_greeting("宮古")
// Greeting selected from the current local time
```

`example_greeting(name {; type}): Text` accepts a Text name and an optional
Longint type. Unicode and empty names are covered by the 4D tests.

| Constant | Value | Greeting |
|---|---|---|
| `example_greeting_default` | 0 | Local time: 03:00–11:59 morning, 12:00–17:59 afternoon, otherwise evening |
| `example_greeting_morning` | 1 | `Good morning ` |
| `example_greeting_afternoon` | 2 | `Good afternoon ` |
| `example_greeting_evening` | 3 | `Good evening ` |

The manifest maps selector 1 to the command; `constants.xlf` declares its
constants. The C++ implementation calls the SDK only within the plugin
invocation. This is the original small teaching example, not a general-purpose
string-processing library.

## Source and pins

The greeting implementation, manifest, constants, native IDE projects and 4D
test project are preserved from
[`f8e20f0`](https://github.com/miyako/4d-plugin-template/tree/f8e20f052407c3e74c33192884dc82b31a2bd27a/example).
Only CMake, the bundle Info.plist template and root `VERSION` use the canonical
example overlay. CMake is the authoritative build path: the historical Xcode
and Visual Studio projects remain reference material, not the release path.

`plugin-template` pins published commit
[`5a9997767fe3f6ba31e0da9ccdd1be74c891168f`](https://github.com/miyako/4d-plugin-template/commit/5a9997767fe3f6ba31e0da9ccdd1be74c891168f)
on the **unmerged**
[`miyako/4d-plugin-template#30`](https://github.com/miyako/4d-plugin-template/pull/30)
branch, not canonical `main`. Inspect the exact pin with
`git ls-tree HEAD plugin-template`; changes to that branch cannot change this
checkout. The baseline `4D-Plugin-SDK` gitlink is unchanged at
[`cd97d1876d4258b56d2516e8ad2816f4ee93e0b5`](https://github.com/4d/4D-Plugin-SDK/tree/cd97d1876d4258b56d2516e8ad2816f4ee93e0b5).
Always clone recursively:

```sh
git clone --recurse-submodules https://github.com/miyako/4d-plugin-example.git
cd 4d-plugin-example
git submodule update --init --recursive
```

## Build

Use CMake 3.20+, a C++20 compiler and the pinned SDK. On macOS, install the
Xcode command-line tools:

```sh
cmake -S example -B example/build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0
cmake --build example/build --config Release --parallel
```

On Windows, use a Visual Studio developer shell with the C++ workload:

```powershell
cmake -S example -B example/build -A x64
cmake --build example/build --config Release --parallel
```

The plugin is installed into `example/example-test/Plugins/`: a macOS
`example.bundle`, or `example/Contents/Windows64/example.4DX` plus resources on
Windows. `VERSION` is the only version source; CMake writes both macOS bundle
version fields and `CFBundlePackageType=BNDL`. Windows uses the static CRT.
The pipeline targets universal macOS (deployment target 11.0) and Windows x64;
that target is not a claim that every OS/runtime combination has been tested.
There are no third-party library dependencies or native CTest cases.

## Test with 4D and tool4d

Open `example/example-test/Project/example.4DProject` in a compatible 4D runtime
and run `test_example_greeting`. The tests cover all explicit types, Unicode,
empty input and local-time selection. For headless tests, use `test_all`, which
runs the same assertions and writes an exact `PASS` line.

The project compatibility version is `2101` (21.1). The generated
`.github/actions/tool4d-test/action.yml` downloads the matching tool4d runtime
from the official 4D release service, selecting the host architecture on macOS
and x64 on Windows. The runtime patch is resolved by that service's `latest`
endpoint, not pinned by this repository. For a locally installed tool4d:

```sh
mkdir -p example/example-test/Resources
/path/to/tool4d.app/Contents/MacOS/tool4d --dataless \
  --startup-method=test_all \
  "--project=$PWD/example/example-test/Project/example.4DProject"
```

```powershell
New-Item -ItemType Directory -Force example/example-test/Resources | Out-Null
& C:\path\to\tool4d.exe --dataless --startup-method=test_all `
  "--project=$PWD/example/example-test/Project/example.4DProject"
```

Require exit status zero **and** an exact `PASS` output line.
**Build and Test** runs unsigned native builds and these tests on macOS and
Windows, then validates the same-run combined ZIP/DMG layout and re-tests the
extracted plugin. Test-only ad-hoc seals are not production signatures.

## Release actions

| Action | Purpose |
|---|---|
| **Bump version** | Manual patch/minor/major selection; commits only source `VERSION` on `main`. No tag, build, release or workflow dispatch. |
| **Build** | Manual dispatch on `main`, no version/tag/bump inputs. Preflights the immutable event SHA, checked-in version, SDK gitlink and release/tag availability before native work. |

**Build and Test** is separate unsigned validation, not a third release action.
**Pipeline drift** is consumer-only consistency validation. Neither publishes.
The canonical filenames remain `.github/workflows/bump-version.yml`,
`test.yml` and `release.yml`.

**Build** tests, assembles, Developer ID signs and notarizes the macOS
distribution, verifies final ZIP/DMG bytes and installed behavior, and only then
publishes `vX.Y.Z` at the exact built SHA. Existing releases/assets are never
overwritten and tags never move; a same-SHA orphan tag can be reused. Tag pushes
do not automatically publish. Windows distribution remains unsigned.

Signing credentials belong in the `release-signing` environment. Follow the
[canonical user-only secrets guide](plugin-template/.github/instructions/plugin-dev.instructions.md#required-github-secrets-for-release)
for the six required secrets and environment protection. Only the user should
run its credential helper; agents must not read keys, modify keychains or upload
credentials. Credentials do not authorize a release. This tutorial setup does
not dispatch signing/publication or demonstrate production notarization.

## Regenerate and check the pipeline

Read [AGENTS.md](AGENTS.md), then
[`plugin-template/SKILL.md`](plugin-template/SKILL.md). Consumer-owned
configuration is `pipeline/example.json`; `.github/plugin-pipeline.json` is
generated, not the editing source. Generated ownership is recorded in
`.github/plugin-pipeline-generated.json`. Product source, this README and its
Japanese translation, agent entrypoints and consumer checks are not generated.

```sh
git submodule update --init --recursive
python3 plugin-template/scripts/generate_plugin_pipeline.py \
  --config pipeline/example.json --output . --update-managed
python3 scripts/check_tutorial_pipeline.py
python3 -m unittest discover -s scripts/tests -p test_tutorial_pipeline.py -v
actionlint
```

The check requires clean, initialized submodules matching the indexed gitlinks,
then runs the exact pinned generator with `--check` and generated
`scripts/check_pipeline.py`. It detects pin mismatches, edited canonical input,
consumer-config/generated drift and unexpected workflows. **Pipeline drift**
runs this check and negative regression tests in CI. Its consumer-owned
`pipeline-drift.yml` is explicitly declared in `consumer_workflows`, never
rendered or overwritten by the generator.

For a deliberate canonical update, fetch a reviewed **published** commit,
check it out detached in `plugin-template`, stage that gitlink with
`git add plugin-template`, initialize recursively, regenerate, check and commit
the pin and generated changes together. `--update-managed` refuses to overwrite
hand-edited managed bytes; do not bypass that guard. No SDK update is needed.
Canonical packaging/publication regression tests can also run locally:

```sh
python3 -m unittest discover -s scripts/tests -v
```

These are synthetic tests, not actual signing or publication.
