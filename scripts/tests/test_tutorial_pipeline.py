"""Consumer boundary regressions, without modifying the actual checkout."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "tutorial_check", ROOT / "scripts/check_tutorial_pipeline.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class TutorialPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(
            ROOT, self.root, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                ".git", "plugin-template", "4D-Plugin-SDK", "build", "Plugins",
                "__pycache__", ".local-tools", ".package-*",
            ),
        )
        self.git("init", "--quiet")
        for name in ("plugin-template", "4D-Plugin-SDK"):
            source = ROOT / name
            pin = CHECK.git(ROOT, "ls-files", "--stage", "--", name).split()[1]
            subprocess.run(
                ["git", "clone", "--quiet", "--shared", "--no-checkout",
                 str(source), str(self.root / name)], check=True,
            )
            subprocess.run(
                ["git", "-C", str(self.root / name), "checkout", "--quiet", pin],
                check=True,
            )
            self.git("update-index", "--add", "--cacheinfo", f"160000,{pin},{name}")
        # Local-only clone avoids network and retains the exact nested SDK pin.
        nested = self.root / "plugin-template/4D-Plugin-SDK"
        subprocess.run(
            ["git", "-c", "advice.detachedHead=false", "clone", "--quiet", "--shared",
             str(ROOT / "plugin-template/4D-Plugin-SDK"), str(nested)], check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root / "plugin-template"),
             "submodule", "init"], check=True, capture_output=True,
        )

    def git(self, *args):
        return CHECK.git(self.root, *args)

    def test_exact_pin_and_outputs(self):
        CHECK.check(self.root)

    def test_mismatched_pin(self):
        self.git("update-index", "--cacheinfo",
                 "160000," + "1" * 40 + ",plugin-template")
        with self.assertRaisesRegex(ValueError, "does not match"):
            CHECK.check(self.root)

    def test_mismatched_sdk_pin(self):
        self.git("update-index", "--cacheinfo",
                 "160000," + "1" * 40 + ",4D-Plugin-SDK")
        with self.assertRaisesRegex(ValueError, "4D-Plugin-SDK checkout"):
            CHECK.check(self.root)

    def test_uninitialized_nested_sdk(self):
        subprocess.run(
            ["git", "-C", str(self.root / "plugin-template"),
             "config", "--remove-section", "submodule.4D-Plugin-SDK"],
            check=True,
        )
        with self.assertRaisesRegex(ValueError, "Initialize canonical submodules"):
            CHECK.check(self.root)

    def test_dirty_canonical(self):
        with (self.root / "plugin-template/SKILL.md").open("a") as stream:
            stream.write("\nUnexpected edit\n")
        with self.assertRaisesRegex(ValueError, "must be clean"):
            CHECK.check(self.root)

    def test_generated_workflow_edit(self):
        with (self.root / ".github/workflows/test.yml").open("a") as stream:
            stream.write("\n# Unexpected edit\n")
        with self.assertRaises(subprocess.CalledProcessError):
            CHECK.check(self.root)

    def test_consumer_config_edit(self):
        path = self.root / "pipeline/example.json"
        path.write_text(path.read_text().replace("com.4d.example", "com.4d.changed"))
        with self.assertRaises(subprocess.CalledProcessError):
            CHECK.check(self.root)


if __name__ == "__main__":
    unittest.main()
