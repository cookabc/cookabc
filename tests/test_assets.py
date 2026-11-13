from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_assets
from check_assets import check_file, profile_contract
from unittest.mock import patch
import base64


class AssetTests(unittest.TestCase):
    def svg(self, body):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "sample.svg"
        path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{body}</svg>')
        return path

    def test_broken_and_nonfinite_timelines_fail(self):
        for times in ["0;NaN;1", "0;inf;1", "0;0.5;0.4", "0.1;0.5;1", "0;0.5;0.9"]:
            self.assertTrue(
                check_file(self.svg(f'<animate values="0;1;2" keyTimes="{times}"/>'))
            )
        self.assertTrue(
            check_file(self.svg('<animate values="0;1" keyTimes="0;0.5;1"/>'))
        )

    def test_static_svg_and_complete_animation_are_supported(self):
        self.assertEqual(check_file(self.svg('<rect width="10" height="10"/>')), [])
        self.assertEqual(
            check_file(self.svg('<animate values="0;1" keyTimes="0;1"/>')), []
        )

    def test_executable_svg_content_is_rejected(self):
        for body in ["<script/>", "<foreignObject/>", '<rect onclick="run()"/>']:
            self.assertTrue(check_file(self.svg(body)))

    def test_local_references_alt_text_and_explicit_anchors_are_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "README.md"
            path.write_text('<img src="missing.png"><a href="#missing">Jump</a>')
            errors, _, _ = profile_contract(path)
            self.assertTrue(any("alt text" in error for error in errors))
            self.assertTrue(any("local reference" in error for error in errors))
            self.assertTrue(any("anchor" in error for error in errors))

    def test_raster_only_profiles_do_not_require_an_svg(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "assets").mkdir()
            image = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l1cAAAAASUVORK5CYII="
            )
            (root / "assets/image.png").write_bytes(image)
            for name, other in [
                ("README.md", "README.zh-CN.md"),
                ("README.zh-CN.md", "README.md"),
            ]:
                (root / name).write_text(
                    f'<img src="assets/image.png" alt="Sample"><a href="{other}">Language</a>'
                )
            with patch.object(check_assets, "ROOT", root):
                errors, count = check_assets.check()
            self.assertEqual(errors, [])
            self.assertEqual(count, 1)


class TypographyContractTests(unittest.TestCase):
    """DESIGN.md 的字体参数与 render.py 的 Type 实例不许悄悄漂移。"""

    def test_design_typography_matches_renderer(self):
        import re
        root = Path(__file__).resolve().parents[1]
        # 只用标准库解析 DESIGN.md 的 front matter：typography 下是简单的 key: "value"
        front = (root / "DESIGN.md").read_text(encoding="utf-8").split("---")[1]
        section = front.split("typography:", 1)[1].split("\n\n", 1)[0]
        spec = {
            k.strip(): v.strip().strip('"')
            for k, v in (line.split(":", 1) for line in section.splitlines() if ":" in line)
        }
        # 先守文档本身：四个字体声部必须都在，且参数写全
        expected_doc = {
            "display": ("wdth 62", "wght 900"),
            "pair": ("wdth 78", "wght 800", "opsz 96"),
            "label": ("wdth 72", "wght 800"),
            "text": ("wdth 88", "wght 500"),
        }
        for key, tokens in expected_doc.items():
            for token in tokens:
                self.assertIn(token, spec[key], f"DESIGN.md {key} 缺 {token}")

        # 再守代码：render.py 的 Type 实例化参数与文档逐条对应（纯文本读取，
        # 不 import，系统 python 无 uharfbuzz / fontTools 也能跑）
        source = (root / "tools" / "render.py").read_text(encoding="utf-8")
        expected_code = [
            ('DISPLAY = Type(FONTS / "archivo-latin.woff2", {"wdth": 62, "wght": 900})'),
            ('PAIR = Type(FONTS / "bricolage-grotesque-latin.woff2", {"wdth": 78, "wght": 800, "opsz": 96})'),
            ('LABEL = Type(FONTS / "archivo-latin.woff2", {"wdth": 72, "wght": 800}, tracking=0.02)'),
            ('TEXT = Type(FONTS / "archivo-latin.woff2", {"wdth": 88, "wght": 500})'),
        ]
        for line in expected_code:
            self.assertIn(line, source, f"render.py 字体参数与 DESIGN.md 漂移: {line}")
        # 数字统计行必须显式走 tnum（Ark Pixel 无 tnum 时由 has_tnum 守卫跳过）
        self.assertIn('tnum=True', source)
        self.assertIn('self.has_tnum', source)
