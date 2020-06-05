#!/usr/bin/env python3

from json import dumps, load
from typing import *


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
  parsed = {key: p_rgb(value) for key, value in data.items()
            if key.startswith("Ansi") and key.endswith("Color")}
  return parsed


data: Dict[str, Any] = load_json("profile.json")
parsed = p_colour(data)
serialized = dumps(parsed)

print(serialized)
