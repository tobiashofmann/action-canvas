# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Tobias Hofmann
"""Smoke tests for render_canvas.py. Standard library only.

Run from the repo root:  python3 -m unittest discover -s tests -v
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "render_canvas.py"
EXAMPLES = ROOT / "examples"

MINIMAL = """# Long title for the test
<!-- canvas-meta: lang={lang} -->
## {measure}
- Short name
## {description}
- Something is done
## {background}
- There is a reason
"""


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")


class SmokeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    def render(self, md_path):
        out = self.tmp / (md_path.stem + ".svg")
        res = run(md_path, "-o", out)
        self.assertEqual(res.returncode, 0, res.stderr)
        return res, out.read_text(encoding="utf-8")

    # --- examples -----------------------------------------------------------
    def test_examples_pass_final_check(self):
        for name in ("feature-pdf-export.md", "feature-pdf-export.de.md"):
            res = run(EXAMPLES / name, "--check", "final")
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertNotIn("arning", res.stdout, name)  # no warnings for the examples

    def test_example_svg_content(self):
        _, svg = self.render(EXAMPLES / "feature-pdf-export.md")
        self.assertIn("ACTION CANVAS", svg)
        self.assertIn("PDF export of the monthly reports for the finance team", svg)  # long title on top
        self.assertIn("PDF export of the monthly reports<", svg)                      # short measure in the box
        self.assertIn("Open Points", svg)
        self.assertNotIn("Digitalisierungsbaukasten", svg)
        self.assertIn("before merging", svg)

    def test_german_example_is_localized(self):
        _, svg = self.render(EXAMPLES / "feature-pdf-export.de.md")
        for word in ("Umsetzung", "Offene Punkte", "Zeitlicher Horizont", "Was? Wer? Wann?"):
            self.assertIn(word, svg)

    # --- checks -------------------------------------------------------------
    def test_missing_fields_fail_with_exit_1(self):
        md = self.write("bad.md", "# t\n## Measure\n- x\n")
        res = run(md, "--check", "start")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Description", res.stdout)
        self.assertIn("Background", res.stdout)

    def test_start_check_passes_with_three_fields(self):
        md = self.write("ok.md", MINIMAL.format(lang="en", measure="Measure", description="Description", background="Background"))
        self.assertEqual(run(md, "--check", "start").returncode, 0)
        self.assertEqual(run(md, "--check", "final").returncode, 1)  # later phases need more

    def test_open_placeholder_counts_as_empty(self):
        md = self.write("open.md", "# t\n## Measure\n- x\n## Description\n- _open_\n## Background\n- y\n")
        res = run(md, "--check", "start")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Description", res.stdout)

    def test_messages_follow_canvas_language(self):
        md = self.write("pt.md", "# t\n<!-- canvas-meta: lang=pt-BR -->\n## Medida\n- x\n")
        res = run(md, "--check", "start")
        self.assertEqual(res.returncode, 1)
        self.assertIn("campos em falta", res.stdout)
        self.assertIn("Descrição", res.stdout)

    def test_lang_flag_overrides(self):
        md = self.write("en.md", MINIMAL.format(lang="en", measure="Measure", description="Description", background="Background"))
        res = run(md, "--check", "start", "--lang", "de")
        self.assertIn("alle Pflichtfelder", res.stdout)

    def test_language_detected_from_headings_without_meta(self):
        md = self.write("de.md", "# t\n## Maßnahme\n- x\n")
        res = run(md, "--check", "start")
        self.assertIn("fehlende Felder", res.stdout)

    # --- Implementation warnings and truncation -------------------------------
    IMPL = MINIMAL.format(lang="en", measure="Measure", description="Description", background="Background") + """## Implementation
- Time Horizon: 2/5 – {long}
- Complexity: 3/5 – first
- Complexity: 4/5 – second
- Cost: 1/5 – low
- Risk: 2/5 – low
- An extra line without a value
"""

    def test_implementation_warnings(self):
        long = "A very long justification that keeps going well past the two lines the card can show for it"
        md = self.write("impl.md", self.IMPL.format(long=long))
        res, svg = self.render(md)
        self.assertIn("justification too long", res.stdout)
        self.assertIn("more than once", res.stdout)
        self.assertIn("without a 1-5 value", res.stdout)
        self.assertIn("4/5", svg)          # last duplicate wins
        self.assertNotIn(">3/5<", svg)
        self.assertNotIn("extra line without", svg)
        self.assertIn("…</text>", svg)  # cut justification is marked with an ellipsis
        check = run(md, "--check", "plan")
        self.assertIn("justification too long", check.stdout)  # warnings also appear with --check

    def test_short_justifications_give_no_warning(self):
        md = self.write("impl_ok.md", self.IMPL.format(long="short").replace("- Complexity: 3/5 – first\n", "").replace("- An extra line without a value\n", ""))
        res, _ = self.render(md)
        self.assertNotIn("arning", res.stdout)

    def test_long_activity_is_truncated_with_ellipsis(self):
        text = MINIMAL.format(lang="en", measure="Measure", description="Description", background="Background")
        text += "## Required Activities for Implementation\n- [ ] " + "very long activity " * 12 + "— AI — next step\n- [x] Done thing — AI — before merging\n"
        _, svg = self.render(self.write("act.md", text))
        self.assertIn("…</text>", svg)
        self.assertIn("1/2 done", svg)

    def test_many_bullets_do_not_crash(self):
        text = MINIMAL.format(lang="en", measure="Measure", description="Description", background="Background")
        text += "## Added Value\n" + "".join(f"- Benefit number {i} with some more words to wrap around\n" for i in range(40))
        _, svg = self.render(self.write("many.md", text))
        self.assertIn("full text in the Markdown", svg)

    def test_special_characters_are_escaped(self):
        text = MINIMAL.format(lang="en", measure="Measure", description="Description", background="Background").replace("Short name", "R&D <draft> \"x\"")
        _, svg = self.render(self.write("esc.md", text))
        self.assertIn("R&amp;D &lt;draft&gt;", svg)


if __name__ == "__main__":
    unittest.main()
