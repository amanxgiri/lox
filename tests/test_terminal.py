"""Optional terminal tests; run run.ps1 once to cache the JLine library."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
JLINE = ROOT / "build" / "lib" / "jline-3.30.6.jar"


@unittest.skipUnless(JLINE.exists(), "Run run.ps1 once to download the optional terminal library")
class TerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="terminal-tests-", dir=ROOT / "build")
        cls.addClassCleanup(cls.workspace.cleanup)
        cls.classes = Path(cls.workspace.name) / "classes"
        cls.classes.mkdir()
        cls.classpath = os.pathsep.join([str(cls.classes), str(JLINE)])
        sources = sorted((ROOT / "jlox").glob("*.java"))
        sources += sorted((ROOT / "terminal").glob("*.java"))
        sources += [ROOT / "tests" / "TerminalChecks.java"]
        result = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-cp", cls.classpath,
             "-d", str(cls.classes), *map(str, sources)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode:
            raise AssertionError(result.stderr)

    def test_highlighter_preserves_source_and_styles_lox_tokens(self):
        result = subprocess.run(
            ["java", "-cp", self.classpath, "tests.TerminalChecks"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Terminal highlighting checks passed.\n")
        self.assertEqual(result.stderr, "")

    def test_redirected_input_uses_plain_prompt_even_with_editor_installed(self):
        environment = dict(os.environ, TERM="xterm-256color")
        environment.pop("NO_COLOR", None)
        result = subprocess.run(
            ["java", "-cp", self.classpath, "jlox.Lox"],
            input='fun f() {\nreturn 42;\n}\nprint f();\n', env=environment,
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "> ... ... > 42\n> ")
        self.assertEqual(result.stderr, "")

    def test_file_execution_does_not_add_color_codes(self):
        result = subprocess.run(
            ["java", "-cp", self.classpath, "jlox.Lox", str(ROOT / "examples" / "demo.lox")],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (ROOT / "examples" / "demo.expected").read_text())
        self.assertEqual(result.stderr, "")
