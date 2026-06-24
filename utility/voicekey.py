from collections.abc import Iterator
from typing import cast

from model.dependency import CoupleEncourage

from .dependency import load_dependency

_MAIN_VOICEKEY_LENGTH_CACHE: dict[int, int] = {}


def get_main_voicekey_length(gid: int) -> int:
  if gid in _MAIN_VOICEKEY_LENGTH_CACHE:
    return _MAIN_VOICEKEY_LENGTH_CACHE[gid]

  ship_skin_words = load_dependency("ship_skin_words")

  data = ship_skin_words.get(f"{gid}0")
  length = len(data.main.split("|")) if data and (data.main not in ("", "nil")) else 0

  _MAIN_VOICEKEY_LENGTH_CACHE[gid] = length
  return length


def get_resource_key(key: str) -> str:
  character_voice = load_dependency("character_voice")

  if key in character_voice:
    return character_voice[key].resource_key

  if key.startswith("couple_encourage"):
    return key.replace("couple_encourage", "link")

  if key.startswith("main"):
    return key.replace("main", "main_")

  raise ValueError(f"Unknown resource_key '{key}'")


def get_voicekey_event(
  key: str,
  group_index: int,
  extra: str | None = None,
  suffix: str | None = None,
) -> str:
  resource_key = get_resource_key(key)

  if group_index != 0:
    resource_key += f"_{group_index}"

  if extra is not None:
    resource_key += f"_ex{extra}"

  if suffix is not None:
    resource_key += suffix

  return resource_key


def collect_voicekeys(
  id: str,
  gid: int,
  group_index: int,
) -> Iterator[tuple[str, str | CoupleEncourage, str]]:
  character_voice = load_dependency("character_voice")
  ship_skin_words = load_dependency("ship_skin_words")
  ship_skin_words_extra = load_dependency("ship_skin_words_extra")

  if id in ship_skin_words:
    for key, value in ship_skin_words[id]:
      if (isinstance(value, list) and not value) or (value == ""):
        continue

      if (key not in character_voice) and (key not in ("main", "couple_encourage")):
        continue

      value = cast(str, value)

      if key == "main":
        for index, line in enumerate(value.split("|"), start=1):
          vk = f"{key}{index}"
          yield (vk, line, get_voicekey_event(vk, group_index=group_index, suffix=".ogg"))

      elif key == "couple_encourage":
        value = cast(list[CoupleEncourage], value)

        for index, couple_encourage in enumerate(value, start=1):
          vk = f"{key}{index}"

          yield (
            vk,
            couple_encourage,
            get_voicekey_event(vk, group_index=group_index, suffix=".ogg"),
          )

      else:
        yield (key, value, get_voicekey_event(key, group_index=group_index, suffix=".ogg"))

  if id in ship_skin_words_extra:
    for key, value in ship_skin_words_extra[id]:
      if not isinstance(value, list) or not value:
        continue

      if (key not in character_voice) and (key not in ("main", "main_extra")):
        continue

      value = cast(list[tuple[int, str]], value)

      for extra, line in value:
        if key not in ("main", "main_extra"):
          yield (
            f"{key}_ex",
            line,
            get_voicekey_event(key, group_index=group_index, extra=str(extra), suffix=".ogg"),
          )
          continue

        if line in ("nil", ""):
          continue

        base_offset = 0 if key == "main" else get_main_voicekey_length(gid)

        for i, v in enumerate(line.split("|"), start=1):
          vk = f"main{i + base_offset}"
          yield (
            f"{vk}_ex",
            v,
            get_voicekey_event(vk, group_index=group_index, extra=str(extra), suffix=".ogg"),
          )
