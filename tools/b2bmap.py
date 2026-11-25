#!/usr/bin/env python3
"""b2bmap: build, check and extend B2B Studio MIDI mappings.

Every controller lives in controllers/<slug>/ and is described by one file, mapping.yaml.
This tool turns that file into the importable presets and the mapping tables.

    python tools/b2bmap.py new <slug> --name "Vendor Model" --port "MIDI input name"
    python tools/b2bmap.py learn <slug>        # press controls, name them, get YAML
    python tools/b2bmap.py targets [words]     # search the B2B Studio control ids
    python tools/b2bmap.py build  [<slug>]     # write presets and docs
    python tools/b2bmap.py check               # validate everything (this is what CI runs)

Needs PyYAML (pip install -r tools/requirements.txt). `learn` also needs mido and python-rtmidi.
The format is documented in docs/MAPPING-FORMAT.md.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import pathlib
import re
import sys
import threading
import time

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is missing. Run: pip install -r tools/requirements.txt")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTROLLERS = ROOT / "controllers"
REGISTRY = pathlib.Path(__file__).with_name("targets.json")
OPTION_KEYS = {"rel", "invert", "sens", "pos"}
REL_VALUES = {"2c", "binoff", "signed"}
KINDS = {"note", "cc", "pb"}


class MappingError(Exception):
    pass


# ------------------------------------------------------------------ templates
_FIELD = re.compile(r"\{(\w+)(?::([^{}]*))?\}")


def fmt(template, ctx, where):
    """Fill {name} and {name:spec} from ctx. Nothing else is evaluated."""
    def sub(m):
        name, spec = m.group(1), m.group(2)
        if name not in ctx:
            raise MappingError(f"{where}: unknown variable {{{name}}} (known: {', '.join(sorted(ctx)) or 'none'})")
        try:
            return format(ctx[name], spec or "")
        except (ValueError, TypeError) as exc:
            raise MappingError(f"{where}: bad format for {{{name}:{spec}}}: {exc}")
    out = _FIELD.sub(sub, str(template))
    leftover = re.search(r"\{[^{}]*\}", out)
    if leftover:
        raise MappingError(f"{where}: {leftover.group(0)} is not a variable. Only {{name}} and {{name:format}} are filled in.")
    return out


def to_int(text, where, what):
    try:
        return int(str(text).strip(), 0)
    except ValueError:
        raise MappingError(f"{where}: {what} must be a whole number, got {text!r}")


def parse_msg(text, where):
    """'note 0 0x0B' -> ('note', 0, 11). The number may add parts: 'note 7 0x20+3'."""
    parts = str(text).split(None, 2)
    if not parts or parts[0] not in KINDS:
        raise MappingError(f"{where}: msg must start with note, cc or pb, got {text!r}")
    kind = parts[0]
    if kind == "pb":
        if len(parts) < 2:
            raise MappingError(f"{where}: pb needs a channel, e.g. 'pb 0'")
        ch, num = to_int(parts[1], where, "channel"), 0
    else:
        if len(parts) < 3:
            raise MappingError(f"{where}: msg needs a kind, channel and number, e.g. 'note 0 0x0B'")
        ch = to_int(parts[1], where, "channel")
        num = sum(to_int(p, where, "number") for p in parts[2].replace(" ", "").split("+"))
    if not 0 <= ch <= 15:
        raise MappingError(f"{where}: channel {ch} is outside 0-15 (channels start at 0)")
    if not 0 <= num <= 127:
        raise MappingError(f"{where}: number {num} is outside 0-127")
    return kind, ch, num


# ------------------------------------------------------------------ expansion
class Entry:
    __slots__ = ("section", "target", "kind", "ch", "num", "opts", "doc", "custom", "only", "share", "where")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def src(self, port):
        return f"{port}|{self.kind}|{self.ch}|{self.num}"

    def applies_to(self, name, profile):
        if not self.only:
            return True
        wanted = set(self.only)
        return name in wanted or bool(wanted & set(profile.get("tags", [])))


def load_mapping(path):
    try:
        data = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise MappingError(f"{path}: not valid YAML: {exc}")
    if not isinstance(data, dict):
        raise MappingError(f"{path}: expected a mapping at the top level")
    for key in ("name", "profiles", "bindings"):
        if key not in data:
            raise MappingError(f"{path}: missing required key '{key}'")
    if not isinstance(data["profiles"], dict) or not data["profiles"]:
        raise MappingError(f"{path}: 'profiles' needs at least one profile")
    for pname, p in data["profiles"].items():
        if not isinstance(p, dict) or not p.get("port"):
            raise MappingError(f"{path}: profile '{pname}' needs a 'port' (the MIDI input name)")
    return data


def expand(mapping, source="mapping.yaml"):
    decks = mapping.get("decks") or []
    entries = []
    section = [None]
    counter = [0]

    def binding(node, ctx):
        counter[0] += 1
        where = f"{source} binding #{counter[0]}"
        if not isinstance(node, dict):
            raise MappingError(f"{where}: each binding must be a mapping, got {node!r}")
        for req in ("target", "msg"):
            if req not in node:
                raise MappingError(f"{where}: missing '{req}'")
        if ("doc" in node) == ("why" in node):
            raise MappingError(f"{where} ({node['target']}): give exactly one of 'doc' (a 1:1 mapping) or "
                               "'why' (a judgement call, explain it)")
        unknown = set(node) - {"target", "msg", "doc", "why", "opts", "only", "only_decks", "repeat", "items", "share"}
        if unknown:
            raise MappingError(f"{where}: unknown key(s) {sorted(unknown)}")
        if "only_decks" in node and "d" in ctx and ctx["d"] not in node["only_decks"]:
            return
        if "items" in node:
            items = []
            for item in node["items"]:
                items.append(dict(item) if isinstance(item, dict) else {"v": item})
        elif "repeat" in node:
            items = [{} for _ in range(to_int(node["repeat"], where, "repeat"))]
        else:
            items = [None]
        for i, item in enumerate(items):
            c = dict(ctx)
            if item is not None:
                c.update(item)
                c.update(i=i, i1=i + 1, letter=chr(65 + i) if i < 26 else str(i + 1))
            w = f"{where} ({node['target']})"
            opts = dict(node.get("opts") or {})
            bad = set(opts) - OPTION_KEYS
            if bad:
                raise MappingError(f"{w}: unknown option(s) {sorted(bad)}; allowed: {sorted(OPTION_KEYS)}")
            if "rel" in opts and opts["rel"] not in REL_VALUES and opts["rel"] is not True:
                raise MappingError(f"{w}: rel must be one of {sorted(REL_VALUES)}")
            kind, ch, num = parse_msg(fmt(node["msg"], c, w), w)
            why = "why" in node
            entries.append(Entry(
                section=section[0], target=fmt(node["target"], c, w), kind=kind, ch=ch, num=num, opts=opts,
                doc=fmt(node["why" if why else "doc"], c, w), custom=why,
                only=node.get("only") and ([node["only"]] if isinstance(node["only"], str) else list(node["only"])),
                share=bool(node.get("share")), where=w))

    def walk(nodes, ctx):
        for node in nodes:
            if isinstance(node, dict) and set(node) == {"section"}:
                section[0] = fmt(node["section"], ctx, f"{source} section")
            elif isinstance(node, dict) and "for" in node:
                if node["for"] != "decks":
                    raise MappingError(f"{source}: only 'for: decks' is supported, got {node['for']!r}")
                for deck in decks:
                    if "only_decks" in node and deck.get("d") not in node["only_decks"]:
                        continue
                    walk(node.get("bindings") or [], {**ctx, **deck})
            elif isinstance(node, dict) and "bindings" in node and "target" not in node:
                # a group: only for some decks, used inside a 'for: decks' block
                if "only_decks" in node and ctx.get("d") not in node["only_decks"]:
                    continue
                walk(node["bindings"] or [], ctx)
            else:
                binding(node, ctx)

    walk(mapping["bindings"] or [], {})
    return entries


# ----------------------------------------------------------------- validation
def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


_TARGET = re.compile(r"^([a-z0-9]+)@([a-z0-9-]+):(.+)$")


def _control_matchers(spec):
    exact, patterns = set(), []
    for cid in list(spec.get("controls", {})) + list(spec.get("extra", {})):
        if "{n}" in cid:
            patterns.append(re.compile("^" + re.escape(cid).replace(r"\{n\}", r"\d+") + "$"))
        else:
            exact.add(cid)
    return exact, patterns


def check_target(target, registry):
    """Return (error, warning). Both None when the target is known."""
    m = _TARGET.match(target)
    if not m:
        return f"{target}: expected <unit>@<spec>:<control>, for example d0@cdj-3000x:play", None
    unit, spec_name, cid = m.groups()
    spec = registry["specs"].get(spec_name)
    if spec is None:
        return None, f"{target}: spec '{spec_name}' is not in tools/targets.json, so the control was not checked"
    units = spec.get("units", "")
    if units == "mx":
        ok = unit == "mx"
    else:
        lo, hi = re.fullmatch(r"d(\d+)-d(\d+)", units).groups()
        ok = bool(re.fullmatch(r"d\d+", unit)) and int(lo) <= int(unit[1:]) <= int(hi)
    if not ok:
        return f"{target}: unit '{unit}' is not valid for {spec_name} (expected {units})", None
    if cid.startswith("screen/") and "screen" in spec:
        name = cid[len("screen/"):].split("=")[0]
        arg = "=" in cid
        if name not in spec["screen"]:
            return f"{target}: unknown screen target '{name}' (known: {', '.join(spec['screen'])})", None
        if name in ("loop", "jump", "key"):
            try:
                float(cid.split("=", 1)[1])
            except (IndexError, ValueError):
                return f"{target}: screen/{name} needs a number, for example screen/{name}=4", None
        elif arg:
            return f"{target}: screen/{name} takes no number", None
        return None, None
    exact, patterns = _control_matchers(spec)
    base, _, sub = cid.partition("/")
    known = base in exact or any(p.match(base) for p in patterns) or any(
        fnmatch.fnmatch(base, w) for w in spec.get("wildcards", []))
    if not known:
        return (f"{target}: '{base}' is not a known control of {spec_name}. Search with "
                f"'python tools/b2bmap.py targets {base[:4]}', or add it to tools/targets.json if the app has it."), None
    if sub and sub not in spec.get("subs", {}).get(base, []):
        return f"{target}: '{base}' has no '/{sub}' part (known: {spec.get('subs', {}).get(base, []) or 'none'})", None
    return None, None


def validate(mapping, entries, registry, source):
    errors, warnings = [], []
    seen_warn = set()
    for e in entries:
        err, warn = check_target(e.target, registry)
        if err:
            errors.append(f"{source}: {err}")
        if warn and warn not in seen_warn:
            seen_warn.add(warn)
            warnings.append(f"{source}: {warn}")
    for pname, profile in mapping["profiles"].items():
        by_target, by_src = {}, {}
        for e in entries:
            if not e.applies_to(pname, profile):
                continue
            if e.target in by_target:
                errors.append(f"{source}: profile '{pname}': {e.target} is bound twice "
                              f"({by_target[e.target].where} and {e.where})")
            by_target[e.target] = e
            by_src.setdefault(e.src(profile["port"]), []).append(e)
        for src, group in by_src.items():
            if len(group) > 1 and not all(g.share for g in group):
                names = ", ".join(g.target for g in group)
                errors.append(f"{source}: profile '{pname}': {src} drives several targets ({names}). "
                              "If that is intended (one control shared by both decks), add 'share: true' to each.")
    return errors, warnings


# --------------------------------------------------------------------- output
def preset_readme(mapping, pname, profile):
    ctx = {"port": profile["port"], "profile": pname, "title": profile.get("title", mapping["name"]),
           "name": mapping["name"]}
    lines = []
    for src in (profile.get("readme") or [], mapping.get("readme") or []):
        lines += [fmt(x, ctx, f"readme of profile {pname}") for x in src]
    lines.append('Each binding has a "doc" or "why" note explaining it; B2B Studio ignores it. '
                 "Notes starting with CUSTOM mean the controller has no matching control, so the mapping is a judgement call.")
    return lines


def render(slug, mapping, entries):
    """Return {path: text} for every generated file of one controller."""
    out = {}
    base = CONTROLLERS / slug
    for pname, profile in mapping["profiles"].items():
        port = profile["port"]
        title = profile.get("title", mapping["name"])
        used = [e for e in entries if e.applies_to(pname, profile)]
        bindings = {}
        for e in used:
            doc = ("CUSTOM: " if e.custom else "") + e.doc
            bindings[e.target] = {"src": e.src(port), **e.opts, "doc": doc}
        preset = {"app": "B2B Studio", "kind": "midi-preset", "version": 1, "name": title,
                  "_readme": preset_readme(mapping, pname, profile), "bindings": bindings}
        out[base / "presets" / f"{slug}-{pname}.b2bmidi.json"] = json.dumps(preset, indent=2, ensure_ascii=False) + "\n"
        if profile.get("docs"):
            out[base / "docs" / f"MAPPING-{pname}.md"] = render_table(title, used, port)
    return out


def render_table(title, used, port):
    lines = [f"# Mapping reference - {title}", "",
             f"Generated from `mapping.yaml` by `tools/b2bmap.py`; do not edit by hand. MIDI input: `{port}`.", "",
             "Channels are shown 1-based (ch1 is the controller's first MIDI channel). "
             "**Custom** rows are judgement calls: the controller has no matching control, or the target is repurposed."]
    current = object()
    for e in used:
        if e.section != current:
            current = e.section
            lines += ["", f"## {current or 'Bindings'}", "",
                      "| Controller message | B2B Studio target | Notes | What it does |", "|---|---|---|---|"]
        kind = {"note": "Note", "cc": "CC", "pb": "Pitch bend"}[e.kind]
        msg = f"{kind} ch{e.ch + 1}" if e.kind == "pb" else f"{kind} 0x{e.num:02X} ch{e.ch + 1}"
        notes = ", ".join(x for x in (["custom"] if e.custom else []) +
                          [f"{k}={v}" for k, v in e.opts.items()] if x)
        lines.append(f"| {msg} | `{e.target}` | {notes} | {e.doc.replace('|', chr(92) + '|')} |")
    return "\n".join(lines) + "\n"


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def controllers(slug=None):
    if slug:
        d = CONTROLLERS / slug
        if not (d / "mapping.yaml").exists():
            raise MappingError(f"controllers/{slug}/mapping.yaml does not exist")
        return [d]
    return sorted(d for d in CONTROLLERS.iterdir() if (d / "mapping.yaml").exists()) if CONTROLLERS.exists() else []


def compile_controller(d):
    path = d / "mapping.yaml"
    mapping = load_mapping(path)
    entries = expand(mapping, f"controllers/{d.name}/mapping.yaml")
    return mapping, entries


# ------------------------------------------------------------------- commands
def cmd_build(args):
    registry = load_registry()
    for d in controllers(args.slug):
        mapping, entries = compile_controller(d)
        errors, warnings = validate(mapping, entries, registry, f"controllers/{d.name}")
        for w in warnings:
            print("warning:", w)
        if errors:
            raise MappingError("\n".join(errors))
        for path, text in render(d.name, mapping, entries).items():
            write_text(path, text)
            print("wrote", path.relative_to(ROOT).as_posix())
    return 0


_LINK = re.compile(r"\]\(([^)\s#]+)(#[^)]*)?\)")


def check_links():
    bad = []
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts or "node_modules" in md.parts:
            continue
        for m in _LINK.finditer(md.read_text(encoding="utf-8")):
            t = m.group(1)
            if t.startswith(("http://", "https://", "mailto:")):
                continue
            target = (md.parent / t).resolve()
            if CONTROLLERS in md.resolve().parents:
                folder = CONTROLLERS / md.resolve().relative_to(CONTROLLERS).parts[0]
                if folder not in target.parents and target != folder:
                    bad.append(f"{md.relative_to(ROOT).as_posix()}: link to {t} leaves the controller folder "
                               "and would break in the release zip")
                    continue
            if ROOT not in target.parents and target != ROOT:
                continue                      # ../../issues and friends: GitHub web routes, not files
            if not target.exists():
                bad.append(f"{md.relative_to(ROOT).as_posix()}: broken link to {t}")
    return bad


def cmd_check(args):
    registry = load_registry()
    errors, warnings = [], []
    found = controllers()
    if not found:
        errors.append("no controllers found")
    for d in found:
        rel = f"controllers/{d.name}"
        try:
            mapping, entries = compile_controller(d)
        except MappingError as exc:
            errors.append(str(exc))
            continue
        e, w = validate(mapping, entries, registry, rel)
        errors += e
        warnings += w
        if not (d / "README.md").exists():
            errors.append(f"{rel}: README.md is missing")
        if not e:
            for path, text in render(d.name, mapping, entries).items():
                on_disk = path.read_text(encoding="utf-8") if path.exists() else None
                if on_disk is None or on_disk.replace("\r\n", "\n") != text:
                    errors.append(f"{path.relative_to(ROOT).as_posix()} is out of date. "
                                  "Run: python tools/b2bmap.py build")
        for py in sorted(d.glob("*.py")):
            try:
                compile(py.read_text(encoding="utf-8"), str(py), "exec")
            except SyntaxError as exc:
                errors.append(f"{rel}/{py.name}: syntax error on line {exc.lineno}: {exc.msg}")
    errors += check_links()
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    if errors:
        print(f"\n{len(errors)} problem(s).")
        return 1
    print(f"OK: {len(found)} controller(s) valid, presets and docs up to date.")
    return 0


def search_targets(registry, words):
    words = [w.lower() for w in words]
    hits = []
    for spec_name, spec in registry["specs"].items():
        unit = "mx" if spec.get("units") == "mx" else "d{N}"
        items = dict(spec.get("controls", {}))
        items.update(spec.get("extra", {}))
        for cid, name in sorted(items.items()):
            text = f"{spec_name} {cid} {name}".lower()
            if all(w in text for w in words):
                hits.append((f"{unit}@{spec_name}:{cid}", name))
        if "screen" in spec and all(w in "screen loop jump key time needle" for w in words):
            hits += [(f"{unit}@{spec_name}:screen/{s}" + ("=N" if s in ("loop", "jump", "key") else ""), "") for s in spec["screen"]]
    return hits


def cmd_targets(args):
    hits = search_targets(load_registry(), args.words)
    for target, name in hits:
        print(f"{target:<44} {name}")
    if not hits:
        print("no match. The app may have it anyway: learn it in B2B Studio, export, and read the key.")
    else:
        print("\n{n} stands for a number, {N} for the deck index (d0 is Deck 1). Add /touch, /push, /rev where the docs say so.")
    return 0


TEMPLATE = '''# Mapping for {name}. Format: docs/MAPPING-FORMAT.md
# Quick way to fill this in: python tools/b2bmap.py learn {slug}
name: "{name}"

profiles:
  default:
    title: "{name}"
    port: "{port}"          # the MIDI input name, exactly as B2B Studio lists it
    docs: true              # also write docs/MAPPING-default.md

# Keep 'bindings' as the last key: 'learn' appends to the end of the file.
# An example (remove the # signs, or let `learn` write bindings like this for you):
#   - target: "d0@cdj-3000x:play"
#     msg: "note 0 0x0B"
#     doc: "PLAY/PAUSE button. 1:1 with the CDJ PLAY/PAUSE."
bindings:
'''

README_STUB = '''# {name}

Mapping of the {name} for B2B Studio. Describe here:

- what the preset gives you,
- how to set it up (anything beyond importing the preset: a wake-up message, drivers, modes),
- what you tested on hardware and on which operating system,
- known limitations.

The importable preset is in `presets/` and the table of every binding is in `docs/`. Both are generated from
`mapping.yaml`: edit that file, then run `python tools/b2bmap.py build`.
'''


def cmd_new(args):
    slug = args.slug
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise MappingError("slug must be lowercase letters, digits and dashes, for example 'ddj-flx4'")
    d = CONTROLLERS / slug
    if d.exists():
        raise MappingError(f"controllers/{slug} already exists")
    write_text(d / "mapping.yaml", TEMPLATE.format(slug=slug, name=args.name, port=args.port))
    write_text(d / "README.md", README_STUB.format(name=args.name))
    print(f"Created controllers/{slug}/mapping.yaml and README.md")
    print(f"Next: python tools/b2bmap.py learn {slug}     then     python tools/b2bmap.py check")
    return 0


# ----------------------------------------------------------------------- learn
def guess_relative(samples):
    """Guess the encoding of an endless encoder from the values it sent, or None if it looks absolute."""
    vals = [v for v in samples]
    if len(vals) < 3:
        return None
    if all(57 <= v <= 71 and v != 64 for v in vals) and len({v > 64 for v in vals}) == 2:
        return "binoff"
    if all(1 <= v <= 8 or 120 <= v <= 127 for v in vals) and any(v >= 120 for v in vals):
        return "2c"
    if all(1 <= v <= 8 or 65 <= v <= 72 for v in vals) and any(v >= 65 for v in vals):
        return "signed"
    return None


def append_binding(path, text, registry=None):
    """Append YAML text to the mapping and validate the result; roll the file back if anything is wrong.

    With a registry this also catches an unknown target, a target bound twice and a controller message
    that would drive two targets, so `learn` never leaves a file that `check` would reject.
    """
    original = pathlib.Path(path).read_text(encoding="utf-8")
    mapping = yaml.safe_load(original)
    if list(mapping)[-1] != "bindings":
        raise MappingError("'bindings' must be the last key in mapping.yaml for 'learn' to append to it")
    write_text(pathlib.Path(path), original.rstrip("\n") + "\n" + text)
    try:
        m = load_mapping(path)
        entries = expand(m, str(path))
        if registry is not None:
            errors, _ = validate(m, entries, registry, "mapping.yaml")
            if errors:
                raise MappingError("\n".join(e.split(": ", 1)[-1] for e in errors))
    except (MappingError, yaml.YAMLError):
        write_text(pathlib.Path(path), original)
        raise


def yaml_quote(s):
    return json.dumps(s, ensure_ascii=False)


def binding_text(target, kind, ch, num, doc, why, opts):
    msg = f"{kind} {ch}" if kind == "pb" else f"{kind} {ch} 0x{num:02X}"
    lines = [f"  - target: {yaml_quote(target)}", f"    msg: {yaml_quote(msg)}"]
    if opts:
        lines.append("    opts: {" + ", ".join(f"{k}: {yaml_quote(v) if isinstance(v, str) else str(v).lower()}"
                                                for k, v in opts.items()) + "}")
    lines.append(f"    {'why' if why else 'doc'}: {yaml_quote(doc)}")
    return "\n".join(lines) + "\n"


def capture(next_message, timeout=None):
    """Wait for one control gesture. Returns (kind, channel, number, cc_values)."""
    fine = {}
    deadline = None if timeout is None else time.time() + timeout
    while True:
        msg = next_message(0.2)
        if msg is None:
            if deadline and time.time() > deadline:
                return None
            continue
        if msg.type == "note_on" and msg.velocity > 0:
            return ("note", msg.channel, msg.note, [])
        if msg.type == "pitchwheel":
            return ("pb", msg.channel, 0, [])
        if msg.type != "control_change":
            continue
        n = msg.control
        if 32 <= n < 64 and time.time() - fine.get((msg.channel, n - 32), 0) < 0.15:
            continue                      # the fine byte of a 14-bit pair we already saw
        if n < 32:
            fine[(msg.channel, n)] = time.time()
        values = [msg.value]
        end = time.time() + 0.6           # keep reading while the control is still moving
        while time.time() < end:
            more = next_message(0.1)
            if more is not None and more.type == "control_change" and (more.channel, more.control) == (msg.channel, n):
                values.append(more.value)
                end = time.time() + 0.4
        return ("cc", msg.channel, n, values)


def cmd_learn(args):
    try:
        import mido
    except ImportError:
        raise MappingError("learn needs mido and python-rtmidi: pip install -r tools/requirements.txt")
    d = CONTROLLERS / args.slug
    path = d / "mapping.yaml"
    mapping = load_mapping(path) if path.exists() else None
    if mapping is None:
        raise MappingError(f"controllers/{args.slug}/mapping.yaml does not exist. Run: python tools/b2bmap.py new {args.slug}")
    profile = mapping["profiles"].get(args.profile) or next(iter(mapping["profiles"].values()))
    registry = load_registry()
    inputs = mido.get_input_names()
    want = args.input or profile["port"]
    name = next((n for n in inputs if want.lower() in n.lower()), None)
    if name is None:
        print("MIDI inputs found:", ", ".join(inputs) or "none")
        raise MappingError(f"no MIDI input matching '{want}'. Plug the controller in, close B2B Studio and any "
                           "other MIDI program, or pass --input NAME.")
    wake = mapping.get("wake")
    out = None
    if wake:
        out_name = next((n for n in mido.get_output_names() if want.lower() in n.lower()), None)
        if out_name:
            out = mido.open_output(out_name)
            data = [int(x, 16) for x in str(wake["sysex"]).split()]
            interval = float(wake.get("interval", 2))

            def keepalive():
                while True:
                    try:
                        out.send(mido.Message("sysex", data=data))
                    except Exception:
                        return
                    time.sleep(interval)
            threading.Thread(target=keepalive, daemon=True).start()
    import queue
    q = queue.Queue()
    port = mido.open_input(name, callback=q.put)

    def next_message(timeout):
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None

    print(f"Listening on {name}. Close B2B Studio first (Windows lets only one program read the controller).")
    print("Move or press one control at a time. Press Enter at a prompt to skip it. Ctrl+C to finish.\n")
    added = 0
    try:
        while True:
            print("Waiting for a control...")
            got = capture(next_message)
            kind, ch, num, values = got
            opts = {}
            msg_text = f"{kind} {ch}" if kind == "pb" else f"{kind} {ch} 0x{num:02X}"
            print(f"Heard: {msg_text}" + (f"   (values {values[:8]})" if values else ""))
            rel = guess_relative(values) if kind == "cc" else None
            if rel:
                print(f"  It looks like an endless encoder ({rel}); adding rel: {rel}.")
                opts["rel"] = rel
            target = ask_target(registry)
            if not target:
                print("  skipped.\n")
                continue
            if not input("  Does the controller have a matching control? [Y/n] ").strip().lower().startswith("n"):
                why = False
                prompt = "  What does it do (one line)? "
            else:
                why = True
                prompt = "  Why this mapping (one line)? "
            doc = input(prompt).strip() or "TODO: describe this control."
            try:
                append_binding(path, binding_text(target, kind, ch, num, doc, why, opts), registry)
            except (MappingError, yaml.YAMLError) as exc:
                print(f"  not saved: {exc}\n")
                continue
            added += 1
            print(f"  saved ({added} so far).\n")
    except (KeyboardInterrupt, EOFError):
        print(f"\nDone. {added} binding(s) added to controllers/{args.slug}/mapping.yaml.")
        print("Next: python tools/b2bmap.py build && python tools/b2bmap.py check")
    finally:
        port.close()
    return 0


def ask_target(registry):
    while True:
        text = input("  Target (search words, or a full id; Enter to skip): ").strip()
        if not text:
            return None
        if "@" in text and ":" in text:
            err, warn = check_target(text, registry)
            if err:
                print("  ", err)
                continue
            return text
        hits = search_targets(registry, text.split())
        if not hits:
            print("   no match; try other words (python tools/b2bmap.py targets).")
            continue
        for i, (target, name) in enumerate(hits[:12], 1):
            print(f"   {i:>2}. {target:<42} {name}")
        if len(hits) > 12:
            print(f"   ... {len(hits) - 12} more; add words to narrow it down")
        pick = input("  Number, or search again: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= min(12, len(hits)):
            target = hits[int(pick) - 1][0]
            return finish_target(target)
        if pick:
            text = pick


def finish_target(target):
    """Fill in the {N} / {n} placeholders and =N arguments."""
    if "{N}" in target:
        target = target.replace("{N}", input("  Deck index (0 for Deck 1, 1 for Deck 2): ").strip() or "0")
    if "{n}" in target:
        target = target.replace("{n}", input("  Number for {n} (channel 0-3, hot cue 0-7, ...): ").strip() or "0")
    if target.endswith("=N"):
        target = target[:-1] + (input("  Value (beats or semitones): ").strip() or "1")
    return target


# ------------------------------------------------------------------------ main
def main(argv=None):
    for stream in (sys.stdout, sys.stderr):      # control names contain symbols a legacy Windows code page cannot print
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build", help="write presets and docs from mapping.yaml")
    p.add_argument("slug", nargs="?")
    p.set_defaults(fn=cmd_build)
    p = sub.add_parser("check", help="validate every controller; fails if generated files are stale")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("targets", help="search B2B Studio control ids")
    p.add_argument("words", nargs="*")
    p.set_defaults(fn=cmd_targets)
    p = sub.add_parser("new", help="scaffold controllers/<slug>")
    p.add_argument("slug")
    p.add_argument("--name", required=True, help='for example "Vendor Model"')
    p.add_argument("--port", required=True, help="the MIDI input name as B2B Studio lists it")
    p.set_defaults(fn=cmd_new)
    p = sub.add_parser("learn", help="press controls and append bindings to mapping.yaml")
    p.add_argument("slug")
    p.add_argument("--profile")
    p.add_argument("--input", help="part of the MIDI input name (default: the profile's port)")
    p.set_defaults(fn=cmd_learn)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except MappingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
