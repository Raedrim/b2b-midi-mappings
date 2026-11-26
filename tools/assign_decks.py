#!/usr/bin/env python3
"""Make a copy of a B2B Studio MIDI preset that drives other decks.

    python assign_decks.py                                      # asks you what you want
    python assign_decks.py preset.b2bmidi.json --left 1 --right 3
    python assign_decks.py preset.b2bmidi.json --left 2 --right 4 --no-shared

The left and right side of the controller move to the decks you pick, together with their mixer channel
strips and their Beat FX channel select. The new preset is written next to the original, which is left
alone. Works on any preset with two decks, shipped or exported from B2B Studio. Needs only Python.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SUFFIX = ".b2bmidi.json"
_DECK = re.compile(r"^d(\d+)@")
_CHANNEL = re.compile(r"^(mx@[^:]+:(?:fx\.)?ch)(\d+)(?=\.|$)")      # ch0.fader and fx.ch0
_STRIP = re.compile(r"^mx@[^:]+:ch\d+\.")


class DeckError(Exception):
    pass


def source_decks(bindings):
    return sorted({int(m.group(1)) for m in map(_DECK.match, bindings) if m})


def is_shared(target):
    """A mixer control that belongs to no channel strip: crossfader, headphones, effects."""
    return target.startswith("mx@") and not _STRIP.match(target)


def reassign(preset, left, right, shared=True):
    """Return a new preset whose lower deck is `left` and higher deck is `right` (numbered 1 to 4)."""
    if not isinstance(preset, dict) or not isinstance(preset.get("bindings"), dict):
        raise DeckError("this does not look like a B2B Studio preset: no 'bindings' object")
    for number in (left, right):
        if number not in (1, 2, 3, 4):
            raise DeckError(f"decks are numbered 1 to 4, got {number}")
    if left == right:
        raise DeckError("the left and right side need different decks")
    decks = source_decks(preset["bindings"])
    if len(decks) != 2:
        found = ", ".join(str(d + 1) for d in decks) or "none"
        raise DeckError(f"the preset must drive exactly two decks (found: {found})")
    # One lookup per key, so moving 1->2 and 2->4 at once cannot pile both decks onto deck 4.
    moves = {decks[0]: left - 1, decks[1]: right - 1}

    def move(target):
        m = _DECK.match(target)
        if m:
            return f"d{moves[int(m.group(1))]}@{target[m.end():]}"
        m = _CHANNEL.match(target)
        if m and int(m.group(2)) in moves:
            return f"{m.group(1)}{moves[int(m.group(2))]}{target[m.end():]}"
        return target

    bindings = {}
    for target, body in preset["bindings"].items():
        if not shared and is_shared(target):
            continue
        new = move(target)
        if new in bindings:
            raise DeckError(f"two bindings would both end up on {new}. Start from a preset for decks 1 and 2.")
        bindings[new] = body
    out = dict(preset)
    out["name"] = f"{preset.get('name') or 'Preset'} (decks {left}+{right})"
    if "_readme" in out:
        note = f"Reassigned by assign_decks.py: left side is Deck {left}, right side is Deck {right}."
        if not shared:
            note += " Crossfader, headphone and effect controls were left out."
        out["_readme"] = [note]
    out["bindings"] = bindings
    return out


def parse_decks(text):
    """'1,3', '1 3', '1+3' or '13' -> (1, 3)."""
    text = str(text)
    digits = re.findall(r"\d", text)
    if len(digits) != 2 or re.sub(r"[\d\s,+/-]", "", text):
        raise DeckError(f"give two decks, for example 1,3 (got {text!r})")
    left, right = (int(d) for d in digits)
    if left not in (1, 2, 3, 4) or right not in (1, 2, 3, 4) or left == right:
        raise DeckError(f"give two different decks from 1 to 4 (got {text!r})")
    return left, right


def output_path(source, left, right):
    stem = source.name[:-len(SUFFIX)] if source.name.endswith(SUFFIX) else source.stem
    stem = re.sub(r"-decks-\d-\d$", "", stem)
    return source.with_name(f"{stem}-decks-{left}-{right}{SUFFIX}")


def convert_file(source, left, right, shared=True):
    source = pathlib.Path(source)
    try:
        preset = json.loads(source.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise DeckError(f"cannot read {source}: {exc}")
    except ValueError as exc:
        raise DeckError(f"{source} is not valid JSON: {exc}")
    result = reassign(preset, left, right, shared)
    target = output_path(source, left, right)
    if target.resolve() == source.resolve():
        raise DeckError("that would overwrite the preset you started from. Start from the original instead.")
    with open(target, "w", encoding="utf-8", newline="\n") as fh:      # Path.write_text(newline=) needs 3.10
        fh.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return target, len(result["bindings"])


# ----------------------------------------------------------------- questions
def ask_preset():
    found = sorted(p for p in (HERE / "presets").glob("*" + SUFFIX) if not re.search(r"-decks-\d-\d\.", p.name))
    for i, p in enumerate(found, 1):
        print(f"  {i}. {p.name}")
    answer = input("Preset (number, or drag a preset file here): ").strip().strip("\"'")
    if answer.isdigit() and 1 <= int(answer) <= len(found):
        return found[int(answer) - 1]
    if not answer:
        raise DeckError("no preset chosen")
    return pathlib.Path(answer)


def ask_deck(side, default):
    answer = input(f"Deck for the {side} side, 1 to 4 [{default}]: ").strip()
    if not answer:
        return default
    if not answer.isdigit():
        raise DeckError(f"decks are numbered 1 to 4, got {answer!r}")
    return int(answer)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("preset", nargs="?", help="the preset to copy (asks if left out)")
    ap.add_argument("--left", type=int, help="deck for the left side, 1 to 4")
    ap.add_argument("--right", type=int, help="deck for the right side, 1 to 4")
    ap.add_argument("--no-shared", action="store_true",
                    help="leave out crossfader, headphone and effect controls, for when someone else runs them")
    args = ap.parse_args(argv)
    try:
        asking = args.preset is None or args.left is None or args.right is None
        source = pathlib.Path(args.preset) if args.preset else ask_preset()
        left = args.left if args.left is not None else ask_deck("left", 1)
        right = args.right if args.right is not None else ask_deck("right", 2)
        shared = not args.no_shared
        if asking and shared:
            shared = not input("Leave out crossfader, headphones and effects? [y/N]: ").strip().lower().startswith("y")
        target, count = convert_file(source, left, right, shared)
    except DeckError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\ncancelled", file=sys.stderr)
        return 1
    print(f"Wrote {target} ({count} bindings).")
    print("Import it in B2B Studio's MIDI settings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
