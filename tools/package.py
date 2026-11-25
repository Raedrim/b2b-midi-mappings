#!/usr/bin/env python3
"""Build the release archives into dist/.

    python tools/package.py v1.2.0

Writes one zip per controller (<slug>-<version>.zip: the controller folder without build artefacts, plus
the LICENSE), a zip with just the importable presets of every controller, and SHA256SUMS. The macOS
launcher keeps its executable bit inside the zip.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SKIP_DIRS = {".venv", "__pycache__", ".git"}
EXECUTABLE = {".command", ".sh"}
FIXED_TIME = (2026, 1, 1, 0, 0, 0)       # reproducible archives


def add(zf, path, arcname):
    info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
    mode = 0o755 if path.suffix in EXECUTABLE else 0o644
    info.external_attr = (0o100000 | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, path.read_bytes())


def files_under(folder):
    for p in sorted(folder.rglob("*")):
        if p.is_file() and not (set(p.relative_to(folder).parts) & SKIP_DIRS) and p.suffix != ".pyc":
            yield p


def main(version):
    if not version:
        sys.exit("usage: python tools/package.py <version>, for example v1.2.0")
    DIST.mkdir(exist_ok=True)
    for old in DIST.glob("*"):
        old.unlink()
    controllers = sorted(d for d in (ROOT / "controllers").iterdir() if (d / "mapping.yaml").exists())
    if not controllers:
        sys.exit("no controllers found")
    outputs = []
    for d in controllers:
        out = DIST / f"{d.name}-{version}.zip"
        with zipfile.ZipFile(out, "w") as zf:
            for p in files_under(d):
                add(zf, p, f"{d.name}/{p.relative_to(d).as_posix()}")
            add(zf, ROOT / "LICENSE", f"{d.name}/LICENSE")
        outputs.append(out)
    out = DIST / f"presets-{version}.zip"
    with zipfile.ZipFile(out, "w") as zf:
        for d in controllers:
            for p in sorted((d / "presets").glob("*.b2bmidi.json")):
                add(zf, p, f"{d.name}/{p.name}")
        add(zf, ROOT / "LICENSE", "LICENSE")
    outputs.append(out)
    sums = "".join(f"{hashlib.sha256(o.read_bytes()).hexdigest()}  {o.name}\n" for o in outputs)
    with open(DIST / "SHA256SUMS", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sums)
    for o in outputs:
        print(f"{o.name}  ({o.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
