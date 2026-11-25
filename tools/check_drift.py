#!/usr/bin/env python3
"""Check that the B2B Studio controls used by our mappings still exist in the app.

Reads the public web client (the same files a browser downloads) once, and looks for every control
id the mappings bind to. It is a best-effort check on a minified bundle, so it reports only ids that
are *missing*; it cannot prove behaviour is unchanged.

    python tools/check_drift.py                  # fetch https://b2bstudio.live
    python tools/check_drift.py --bundle FILE    # check a saved bundle instead (used by tests)

Exit code 0: everything found. 1: some used controls are gone (drift). 2: the client could not be read,
which is reported separately so it is not mistaken for drift.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import b2bmap  # noqa: E402

URL = "https://b2bstudio.live"
UA = "b2bstudio-midi-mappings drift check (https://github.com; weekly, one page)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def read_bundle(base):
    html = fetch(base)
    assets = re.findall(r'(?:src|href)="(/assets/[^"]+\.js)"', html)
    mains = [a for a in assets if "/main" in a] or assets[:1]
    if not mains:
        raise RuntimeError("no script found on the page")
    text = ""
    for a in mains:
        text += fetch(base.rstrip("/") + a)
    return text


def control_regex(cid):
    """Regex that finds a control id in the minified client. {n} is a template placeholder there."""
    if "{n}" in cid:
        return re.compile(re.escape(cid).replace(r"\{n\}", r"\$\{[A-Za-z_$]\w*\}"))
    return re.compile(r"[`\"']" + re.escape(cid) + r"[`\"']")


def used_controls(registry):
    """Map each control a mapping binds to -> list of (controller, example target)."""
    used = {}
    for d in b2bmap.controllers():
        mapping, entries = b2bmap.compile_controller(d)
        for e in entries:
            m = b2bmap._TARGET.match(e.target)
            if not m:
                continue
            _, spec_name, cid = m.groups()
            spec = registry["specs"].get(spec_name)
            if spec is None:
                continue
            if cid.startswith("screen/"):
                key = (spec_name, "screen/" + cid[len("screen/"):].split("=")[0])
            else:
                base, _, sub = cid.partition("/")
                key = (spec_name, base + ("/" + sub if sub else ""))
            used.setdefault(key, (d.name, e.target))
    return used


def needle_for(spec, name):
    """Return (description, regex) for a used control."""
    if name.startswith("screen/"):
        return name, re.compile(re.escape(name) + r"|`" + re.escape(name[len("screen/"):]) + r"`")
    if "/" in name:
        return name, re.compile(re.escape(name))
    pattern_ids = [c for c in list(spec.get("controls", {})) + list(spec.get("extra", {})) if "{n}" in c]
    for pid in pattern_ids:
        if re.fullmatch(re.escape(pid).replace(r"\{n\}", r"\d+"), name):
            return pid, control_regex(pid)
    return name, control_regex(name)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", help="path to a saved client bundle instead of fetching")
    ap.add_argument("--url", default=URL)
    args = ap.parse_args(argv)

    registry = b2bmap.load_registry()
    try:
        text = pathlib.Path(args.bundle).read_text(encoding="utf-8", errors="replace") if args.bundle else read_bundle(args.url)
    except Exception as exc:
        print(f"Could not read the B2B Studio client: {exc}")
        return 2
    if "cdj-3000x" not in text or "djm-a9" not in text:
        print("The client was downloaded but no longer looks like what this script expects "
              "(the CDJ and mixer definitions were not found). The site may have changed shape; "
              "this is not necessarily drift.")
        return 2

    missing = []
    used = used_controls(registry)
    for (spec_name, name), (controller, example) in sorted(used.items()):
        desc, rx = needle_for(registry["specs"][spec_name], name)
        if not rx.search(text):
            missing.append((controller, example, desc))
    print(f"Checked {len(used)} control(s) used by {len(b2bmap.controllers())} controller(s).")
    if not missing:
        print("All of them are still in the client.")
        return 0
    print(f"\n{len(missing)} control(s) are no longer found in the client:\n")
    for controller, example, desc in missing:
        print(f"- `{desc}` (used by `{controller}`, for example `{example}`)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
