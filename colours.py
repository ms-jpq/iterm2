#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from functools import reduce
from json import dumps, load
from typing import *

lookup = {
    "Ansi 0 Color":  ("black",   False),
    "Ansi 8 Color":  ("black",   True),
    "Ansi 1 Color":  ("red",     False),
    "Ansi 9 Color":  ("red",     True),
    "Ansi 2 Color":  ("green",   False),
    "Ansi 10 Color": ("green",   True),
    "Ansi 3 Color":  ("yellow",  False),
    "Ansi 11 Color": ("yellow",  True),
    "Ansi 4 Color":  ("blue",    False),
    "Ansi 12 Color": ("blue",    True),
    "Ansi 5 Color":  ("magenta", False),
    "Ansi 13 Color": ("magenta", True),
    "Ansi 6 Color":  ("cyan",    False),
    "Ansi 14 Color": ("cyan",    True),
    "Ansi 7 Color":  ("white",   False),
    "Ansi 15 Color": ("white",   True),
}


def load_json(name: str) -> Any:
  with open(name) as fd:
    return load(fd)


def colour_hex(val: float) -> str:
  hex = format(int(val * 255), "x")
  return "00" if hex == "0" else hex


def p_rgb(val: Any) -> str:
  assert val["Color Space"] == "sRGB"
  red = colour_hex(val["Red Component"])
  green = colour_hex(val["Green Component"])
  blue = colour_hex(val["Blue Component"])
  return f"#{red}{green}{blue}"


Parsed = Dict[bool, Dict[str, str]]


def p_colour(data: Dict[str, Any]) -> Parsed:
  parsed = ((*lookup[key], p_rgb(value))
            for key, value in data.items()
            if key.startswith("Ansi") and key.endswith("Color"))
  groups = {}
  for name, bright, hex in parsed:
    coll: Dict[str, str] = groups.setdefault(bright, {})
    coll[name] = hex
  return groups


def p_misc(data: Dict[str, any]) -> Dict[str, str]:
  misc_colours: Dict[str, Any] = {key: value
                                  for key, value in data.items()
                                  if "Color" in key and key not in lookup}
  foregroud = p_rgb(misc_colours["Foreground Color"])
  background = p_rgb(misc_colours["Background Color"])
  cursor = p_rgb(misc_colours["Cursor Color"])
  cursor_text = p_rgb(misc_colours["Cursor Text Color"])
  return {"foregroud": foregroud,
          "background": background,
          "cursor": cursor,
          "cursor_text": cursor_text}


def p_args() -> Namespace:
  parser = ArgumentParser()
  parser.add_argument("--ttyd", action="store_true")
  parser.add_argument("--alacritty", action="store_true")
  return parser.parse_args()


def p_ttyd(parsed: Parsed, misc: Dict[str, str]) -> Any:
  def title_case(sym: str) -> str:
    return sym[0].upper() + sym[1:]
  required = {key: val
              for key, val in misc.items()
              if key != "cursor_text"}
  acc = {f"bright{title_case(colour)}" if bright else colour: hex
         for bright, coll in parsed.items()
         for colour, hex in coll.items()}
  return {**acc, **required}


def p_alacritty(parsed: Parsed, misc: Dict[str, str]) -> Any:
  acc = {}
  primary = {}
  cursor = {}
  primary["foregroud"] = misc["foregroud"]
  primary["background"] = misc["background"]
  cursor["cursor"] = misc["cursor"]
  cursor["text"] = misc["cursor_text"]
  acc["primary"] = primary
  acc["cursor"] = cursor
  acc["bright"] = parsed[True]
  acc["normal"] = parsed[False]
  return acc


def main() -> None:
  args = p_args()
  data: Dict[str, Any] = load_json("profile.json")
  parsed = p_colour(data)
  misc_colours = p_misc(data)
  if args.ttyd:
    ttyd = p_ttyd(parsed, misc_colours)
    serialized = dumps(ttyd, indent=2)
    print(serialized)
  else:
    alacritty = p_alacritty(parsed, misc_colours)
    serialized = dumps(alacritty, indent=2)
    print(serialized)


main()
