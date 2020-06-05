#!/usr/bin/env python3

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


def p_colour(data: Dict[str, Any]) -> Any:
  parsed = ((*lookup[key], p_rgb(value))
            for key, value in data.items()
            if key.startswith("Ansi") and key.endswith("Color"))
  groups = {}
  for name, bright, hex in parsed:
    coll: Dict[str, str] = groups.setdefault(bright, {})
    coll[name] = hex
  return groups


data: Dict[str, Any] = load_json("profile.json")
parsed = p_colour(data)
serialized = dumps(parsed)

print(serialized)
