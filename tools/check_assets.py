#!/usr/bin/env python3
"""Check published profile assets and SVG timelines without third-party packages."""

import math
import re
import struct
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"


def check_file(path):
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError) as error:
        return [f"{path.name}: {error}"]
    errors = []
    for element in tree.iter():
        if element.tag in {SVG + "script", SVG + "foreignObject"}:
            errors.append(f"{path.name}: executable SVG content is not allowed")
        if any(name.lower().startswith("on") for name in element.attrib):
            errors.append(f"{path.name}: event handlers are not allowed")
        if element.tag not in {SVG + "animate", SVG + "animateTransform"}:
            continue
        values, times = element.get("values"), element.get("keyTimes")
        if values is None or times is None:
            errors.append(f"{path.name}: animation missing values or keyTimes")
            continue
        try:
            points = [float(value) for value in times.split(";")]
        except ValueError:
            errors.append(f"{path.name}: non-numeric keyTimes")
            continue
        if len(values.split(";")) != len(points) or len(points) < 2:
            errors.append(f"{path.name}: values and keyTimes need matching sequences")
        if not points or not all(math.isfinite(point) for point in points):
            errors.append(f"{path.name}: non-finite keyTimes")
        elif (
            points[0] != 0
            or points[-1] != 1
            or any(not 0 <= point <= 1 for point in points)
            or any(b <= a for a, b in zip(points, points[1:]))
        ):
            errors.append(f"{path.name}: keyTimes must increase from 0 to 1")
    return errors


class ProfileMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets, self.links, self.anchors, self.errors = [], [], set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "iframe", "form"}:
            self.errors.append(f"<{tag}> is not supported in a GitHub profile")
        if attrs.get("id") or attrs.get("name"):
            self.anchors.add(attrs.get("id") or attrs["name"])
        if tag == "img":
            if not attrs.get("alt", "").strip():
                self.errors.append("Profile image needs descriptive alt text")
            if attrs.get("src"):
                self.assets.append(attrs["src"])
        if tag == "source" and attrs.get("srcset"):
            self.assets.extend(
                value.strip().split()[0] for value in attrs["srcset"].split(",")
            )
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])


def profile_contract(path):
    text = path.read_text(encoding="utf-8")
    parser = ProfileMarkup()
    parser.feed(text)
    parser.links.extend(re.findall(r"(?<!!)\[[^\]]+\]\(([^\s)]+)\)", text))
    parser.assets.extend(re.findall(r"!\[[^\]]*\]\(([^\s)]+)\)", text))
    errors = list(parser.errors)
    for value in parser.assets + parser.links:
        url = urlsplit(value)
        if url.scheme:
            if url.scheme not in {"https", "mailto"}:
                errors.append(f"Unsupported link scheme: {value}")
            continue
        target = (path.parent / unquote(url.path)).resolve()
        if url.path and (
            not target.is_relative_to(ROOT.resolve()) or not target.is_file()
        ):
            errors.append(f"Missing or external local reference: {value}")
        if not url.path and url.fragment and url.fragment not in parser.anchors:
            errors.append(f"Missing explicit profile anchor: {value}")
    local_assets = {
        (path.parent / unquote(urlsplit(value).path)).resolve()
        for value in parser.assets
        if not urlsplit(value).scheme
    }
    return errors, parser, local_assets


def check(root=None):
    global ROOT
    if root is not None:
        ROOT = Path(root)
    errors, contracts = [], []
    for name in ["README.md", "README.zh-CN.md"]:
        result, parser, assets = profile_contract(ROOT / name)
        errors.extend(f"{name}: {error}" for error in result)
        contracts.append((parser, assets))
    if contracts[0][1] != contracts[1][1]:
        errors.append("English and Chinese profiles must use the same artwork")
    if set(contracts[0][0].links) - {"README.zh-CN.md"} != set(
        contracts[1][0].links
    ) - {"README.md"}:
        errors.append("English and Chinese profile destinations have drifted")
    for path in sorted((ROOT / "assets").rglob("*.svg")):
        errors.extend(check_file(path))
    for path in contracts[0][1]:
        if path.suffix == ".png" and path.is_file():
            data = path.read_bytes()
            if (
                data[:8] != b"\x89PNG\r\n\x1a\n"
                or len(data) < 24
                or min(struct.unpack(">II", data[16:24])) <= 0
            ):
                errors.append(f"Invalid PNG dimensions: {path.name}")
    return errors, len(contracts[0][1])


if __name__ == "__main__":
    issues, count = check()
    if issues:
        print("\n".join(issues), file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {count} referenced images, bilingual links and SVG timelines")
