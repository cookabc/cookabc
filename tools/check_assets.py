#!/usr/bin/env python3
"""Fail if a generated SVG animation has a broken SMIL timeline."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"


def check_file(path: Path) -> list[str]:
    errors = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [f"{path.name}: {exc}"]
    for el in tree.iter(f"{SVG}animate"):
        values = el.get("values")
        key_times = el.get("keyTimes")
        if values is None or key_times is None:
            errors.append(f"{path.name}: <animate> missing values or keyTimes")
            continue
        vals = values.split(";")
        kts = key_times.split(";")
        if len(vals) != len(kts):
            errors.append(
                f"{path.name}: values ({len(vals)}) != keyTimes ({len(kts)})"
            )
            continue
        try:
            times = [float(item) for item in kts]
        except ValueError:
            errors.append(f"{path.name}: non-numeric keyTimes")
            continue
        if times[0] != 0:
            errors.append(f"{path.name}: keyTimes must start at 0")
        if any(item < 0 or item > 1 for item in times):
            errors.append(f"{path.name}: keyTimes outside 0..1")
        if any(b <= a for a, b in zip(times, times[1:])):
            errors.append(f"{path.name}: keyTimes must strictly increase")
    return errors


def main() -> int:
    files = sorted((ROOT / "assets").glob("*.svg"))
    if not files:
        print("no SVGs in assets/", file=sys.stderr)
        return 1
    errors: list[str] = []
    for path in files:
        errors.extend(check_file(path))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"checked {len(files)} svgs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
