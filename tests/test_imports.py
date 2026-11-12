"""Import smoke tests: every use case module must be importable on its own."""

import importlib
import subprocess
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"


def use_case_modules() -> list[str]:
    modules = []
    for path in sorted(APP_DIR.glob("application/**/use_cases/*.py")):
        if path.name == "__init__.py":
            continue
        relative = path.relative_to(APP_DIR.parent).with_suffix("")
        modules.append(".".join(relative.parts))
    return modules


class UseCaseImportTest(unittest.TestCase):
    def test_use_cases_found(self):
        self.assertTrue(use_case_modules())

    def test_each_use_case_imports_in_a_fresh_interpreter(self):
        for module in use_case_modules():
            with self.subTest(module=module):
                result = subprocess.run(
                    [sys.executable, "-c", f"import {module}"],
                    cwd=APP_DIR.parent,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr[-2000:])

    def test_app_registers_routes(self):
        main = importlib.import_module("app.main")
        paths = {route.path for route in main.app.routes}
        self.assertGreater(len(paths), 5)


if __name__ == "__main__":
    unittest.main()
