#!/usr/bin/env python3
"""Rebuild tools/targets.json from the B2B Studio web client.

targets.json lists the control ids B2B Studio accepts as binding targets. `b2bmap.py check` validates
mappings against it, and `check_drift.py` watches the app for removed controls. When B2B Studio adds or
renames a control, run this to refresh the list:

    python tools/sync_targets.py                  # read https://b2bstudio.live
    python tools/sync_targets.py --bundle FILE    # read a saved client bundle

It reads the control lists of the CDJ-3000X and the DJM-A9 out of the minified client, so it is
best-effort. Review the diff (`git diff tools/targets.json`) before committing. The sub-parts such as
`jog/touch`, the `screen/...` shortcuts and the extra `jogtop` are not in those lists and are kept as
written in this file.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_drift  # noqa: E402

REGISTRY = pathlib.Path(__file__).with_name("targets.json")
BS = chr(92)


def match_end(s, i):
    """Index just after the bracket that closes the one at s[i], skipping strings and template literals."""
    pair = {"[": "]", "{": "}", "(": ")"}
    stack = []
    n = len(s)
    while i < n:
        c = s[i]
        if c in "\"'":
            q = c
            i += 1
            while s[i] != q:
                i += 2 if s[i] == BS else 1
        elif c == "`":
            i += 1
            while s[i] != "`":
                if s[i] == BS:
                    i += 2
                    continue
                if s[i] == "$" and s[i + 1] == "{":
                    i = match_end(s, i + 1)
                    continue
                i += 1
        elif c in pair:
            stack.append(pair[c])
        elif c in ")]}":
            if c != stack.pop():
                raise ValueError(f"unbalanced bracket near offset {i}")
            if not stack:
                return i + 1
        i += 1
    raise ValueError("ran off the end of the bundle")


def normalise(cid):
    return re.sub(r"\$\{[A-Za-z_$]\w*\}", "{n}", cid)


def ids_in(segment):
    out = {}
    for a in re.findall(r"\{id:`([^`]+)`", segment):
        out.setdefault(normalise(a), 1)
    return out


def controls_array(s, spec_id):
    i = s.find("id:`%s`" % spec_id)
    if i < 0:
        raise ValueError(f"spec '{spec_id}' not found in the client")
    k = s.find("controls:[", i)
    return s[k:match_end(s, k + len("controls:"))]


def function_body(s, name):
    i = s.find("function %s(" % name)
    k = s.find("{", s.find(")", i))
    return s[k:match_end(s, k)]


def extract(s, previous):
    names = {}
    for m in re.finditer(r'"?([A-Za-z0-9{}.]+)"?:\{name:`([^`]+)`', s):
        names.setdefault(m.group(1).replace("{i}", "{n}").replace("{m}", "{n}"), m.group(2))

    cdj = ids_in(controls_array(s, "cdj-3000x"))
    cdj.pop("screen", None)

    a9_seg = controls_array(s, "djm-a9")
    a9 = ids_in(a9_seg)
    # the channel strips are built by a helper that the controls array spreads in
    for pattern in (r"\.\.\.[A-Za-z_$][\w$]*\.flatMap\(\(e,t\)=>([A-Za-z_$][\w$]*)\(",
                    r"\.\.\.[A-Za-z_$][\w$]*\.map\(\(e,t\)=>([A-Za-z_$][\w$]*)\("):
        for fn in re.findall(pattern, a9_seg):
            a9.update(ids_in(function_body(s, fn)))

    def drop(k):
        return (k.endswith("Lamp") and k != "scfx.lockLamp") or ".led" in k or k.startswith(("lt.", "sb."))

    old = previous.get("specs", {}).get("cdj-3000x", {})
    reg = {
        "_note": "Control ids B2B Studio accepts as binding targets, read from its web client by "
                 "tools/sync_targets.py. {n} stands for a number. Add an id here when the app has it and "
                 "this file does not.",
        "specs": {
            "cdj-3000x": {
                "units": "d0-d3",
                "controls": {k: names.get(k, "") for k in sorted(cdj) if not drop(k)},
                "subs": old.get("subs", {"jog": ["touch"], "rotary": ["push"], "direction": ["rev", "sliprev"]}),
                "extra": old.get("extra", {"jogtop": "JOG WHEEL (platter top)"}),
                "screen": old.get("screen", ["loop", "jump", "key", "time", "needle"]),
            },
            "djm-a9": {
                "units": "mx",
                "controls": {k: names.get(k, "") for k in sorted(a9) if not drop(k)},
            },
        },
    }
    return reg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", help="path to a saved client bundle instead of fetching")
    ap.add_argument("--url", default=check_drift.URL)
    args = ap.parse_args(argv)
    try:
        text = (pathlib.Path(args.bundle).read_text(encoding="utf-8", errors="replace")
                if args.bundle else check_drift.read_bundle(args.url))
        previous = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}
        reg = extract(text, previous)
    except Exception as exc:
        print(f"error: could not read the control lists: {exc}", file=sys.stderr)
        return 1
    with open(REGISTRY, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(reg, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    c, a = (len(reg["specs"][k]["controls"]) for k in ("cdj-3000x", "djm-a9"))
    print(f"wrote tools/targets.json: {c} CDJ-3000X controls, {a} DJM-A9 controls")
    print("Review with: git diff tools/targets.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
