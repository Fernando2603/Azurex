import json
import os
from pathlib import Path
from typing import Literal

from config import LINK, LINKER_EXTRACT, LINKER_SOURCE, LINKER_TARGET
from utility.debug import runtime
from utility.dependency import Dependency, unload_dependency
from utility.ls_tree import ls_tree
from utility.voicekey import collect_voicekeys

type SubdirParent = Literal[
  "background",
  "bgm",
  "equipment",
  "meowfficer",
  "skin",
  "skill",
  "voiceline",
]

PARENT: dict[SubdirParent, str] = {
  "background": "images/background",
  "bgm": "audio/bgm",
  "equipment": "images/equipment",
  "meowfficer": "images/meowfficer",
  "skin": "images/skin",
  "skill": "images/skill",
  "voiceline": "audio/voiceline",
}

ASSET_LINK = LINK.rstrip("/")


def link(source: str, target: str) -> None:
  src = Path(LINKER_SOURCE, source)

  # while checked by untracked is efficient
  # we never know if some code are slipped
  if not src.exists():
    return

  dst = Path(LINKER_TARGET, target)

  # expected to be run on actions so r[epo always start at fresh
  # this make local machine run faster]
  if dst.exists():
    return

  dst.parent.mkdir(parents=True, exist_ok=True)
  os.link(src, dst)


def get_file_list(source: str) -> tuple[set[str], set[str]]:
  tracked = set(ls_tree(LINKER_SOURCE.as_posix(), source))
  untracked = get_untracked_files(source)
  return tracked, untracked


def get_untracked_files(source: str) -> set[str]:
  src = Path(LINKER_SOURCE, source)

  if not src.exists():
    return set()

  return {file.relative_to(LINKER_SOURCE).as_posix() for file in src.rglob("*") if file.is_file()}


@runtime
def link_extract_to_source() -> None:
  if not LINKER_EXTRACT.exists():
    return

  for file in LINKER_EXTRACT.rglob("*"):
    if not file.is_file():
      continue

    target = LINKER_SOURCE / file.relative_to(LINKER_EXTRACT)
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
      continue

    os.link(file, target)


@runtime
def background(files: dict[str, str]) -> None:
  parent = PARENT["background"]
  tracked, untracked = get_file_list("EN/bg")

  for path in tracked | untracked:
    if not path.startswith("EN/bg/star_level_bg"):
      continue

    name = path.rsplit("_", 1)[1]
    target = f"{parent}/{name}"
    files[f"background.{Path(name).stem}"] = f"{ASSET_LINK}/{target}"

    if path in untracked:
      link(path, target)


@runtime
def bgm(files: dict[str, str]) -> None:
  parent = PARENT["bgm"]
  tracked, untracked = get_file_list("EN/cue")

  for path in tracked | untracked:
    if not path.startswith("EN/cue/bgm"):
      continue

    name = path.split("/")[2].replace(" ", "_")[4:]
    target = f"{parent}/{name}.{path.rsplit('.', 1)[1]}"
    files[f"bgm.{Path(name).stem}"] = f"{ASSET_LINK}/{target}"

    if path in untracked:
      link(path, target)


@runtime
def equipment(files: dict[str, str]) -> None:
  parent = PARENT["equipment"]
  tracked, untracked = get_file_list("EN/equips")
  file_list = tracked | untracked

  with Dependency("equip_data_statistics") as equip_data_statistics:
    for data in equip_data_statistics.values():
      if (data.icon is None) or (data.icon == ""):
        continue

      source = f"EN/equips/{data.icon}.png"

      if source not in file_list:
        continue

      target = f"{parent}/{data.icon}.png"
      files[f"equipment.{data.icon}"] = f"{ASSET_LINK}/{target}"

      if source in untracked:
        link(source, target)


@runtime
def meowfficer(files: dict[str, str]) -> None:
  ASSET_FOLDER = {
    "banner": "EN/commanderhrz",
    "icon": "EN/commandericon",
    "image": "EN/commanderpainting",
    "skill": "EN/commanderskillicon",
    "talent": "EN/commandertalenticon",
  }

  def _get_asset_id(id: str, rarity: int) -> str:
    if rarity == 3:
      return "10000"

    elif rarity == 4:
      return id[:-2] + "00"

    return id

  parent = PARENT["meowfficer"]

  with Dependency("commander_data_template") as commander_data_template:
    for asset_type in ("banner", "icon", "image"):
      tracked, untracked = get_file_list(ASSET_FOLDER[asset_type])
      file_list = tracked | untracked

      for data in commander_data_template.values():
        source = f"{ASSET_FOLDER[asset_type]}/{data.painting}.png"

        if source not in file_list:
          continue

        asset_id = _get_asset_id(id=str(data.id), rarity=data.rarity)
        target = f"{parent}/{asset_id}/{asset_type}.png"
        files[f"meowfficer.{asset_type}.{asset_id}"] = f"{ASSET_LINK}/{target}"

        if source in untracked:
          link(source, target)

  with Dependency("commander_skill_template") as commander_skill_template:
    tracked, untracked = get_file_list(ASSET_FOLDER["skill"])
    file_list = tracked | untracked

    for data in commander_skill_template.values():
      if data.icon == "":
        continue

      source = f"{ASSET_FOLDER['skill']}/{data.icon}.png"

      if source not in file_list:
        continue

      target = f"{parent}/skill/{data.icon}.png"
      files[f"meowfficer.skill.{data.icon}"] = f"{ASSET_LINK}/{target}"

      if source in untracked:
        link(source, target)

  with Dependency("commander_ability_template") as commander_ability_template:
    tracked, untracked = get_file_list(ASSET_FOLDER["talent"])
    file_list = tracked | untracked

    for data in commander_ability_template.values():
      if data.icon == "":
        continue

      icon = data.icon.lower()
      source = f"{ASSET_FOLDER['talent']}/{icon}.png"

      if source not in file_list:
        continue

      target = f"{parent}/talent/{icon}.png"
      files[f"meowfficer.talent.{data.icon}"] = f"{ASSET_LINK}/{target}"

      if source in untracked:
        link(source, target)


@runtime
def skin(files: dict[str, str]) -> None:
  ASSET_FOLDER = {
    "painting": "EN/painting",
    "banner": "EN/herohrzicon",
    "chibi": "EN/shipmodels",
    "icon": "EN/squareicon",
    "qicon": "EN/qicon",
    "shipyard": "EN/shipyardicon",
  }

  parent = PARENT["skin"]

  with Dependency("ship_skin_template") as ship_skin_template:
    for asset_type, folder in ASSET_FOLDER.items():
      tracked, untracked = get_file_list(folder)
      file_list = tracked | untracked

      for id, data in ship_skin_template.items():
        painting = data.painting.lower()
        source = f"{folder}/{painting}.png"

        if (asset_type == "painting") and ((pns := f"{folder}/{painting}_n.png") in file_list):
          pnt = f"{parent}/{id}/painting_n.png"
          files[f"skin.{id}.painting_n"] = f"{ASSET_LINK}/{pnt}"

          if pns in untracked:
            link(pns, pnt)

        if source not in file_list:
          continue

        target = f"{parent}/{id}/{asset_type}.png"
        files[f"skin.{id}.{asset_type}"] = f"{ASSET_LINK}/{target}"

        if source in untracked:
          link(source, target)


@runtime
def skill(files: dict[str, str]) -> None:
  parent = PARENT["skill"]
  tracked, untracked = get_file_list("EN/skillicon")
  file_list = tracked | untracked

  with Dependency("skill_data_template") as skill_data_template, Dependency("buff") as buff:
    for skill_id in skill_data_template:
      if skill_id not in buff:
        continue

      icon = buff[skill_id].icon

      if icon is None:
        continue

      source = f"EN/skillicon/{icon}.png"

      if source not in file_list:
        continue

      target = f"{parent}/{icon}.png"
      files[f"skill.{skill_id}"] = f"{ASSET_LINK}/{target}"

      if source in untracked:
        link(source, target)


@runtime
def voiceline(files: dict[str, str]) -> None:
  parent = PARENT["voiceline"]
  tracked, untracked = get_file_list("EN/cue")
  file_list = tracked | untracked

  def get_voicekey_source(filename: str, gid: int) -> str | None:
    for folder in (f"cv-{gid}", f"cv-{gid}-battle", f"cv-{gid}-gift"):
      resource = f"EN/cue/{folder}/{filename}"

      if resource in file_list:
        return resource

    return None

  with Dependency("ship_skin_template") as ship_skin_template:
    for id, data in ship_skin_template.items():
      for voicekey, _, filename in collect_voicekeys(id, data.ship_group, data.group_index):
        source = get_voicekey_source(filename, data.ship_group)

        if (source is None) or (source not in file_list):
          continue

        target = f"{parent}/{id}/{voicekey}.ogg"
        files[f"voiceline.{id}.{voicekey}"] = f"{ASSET_LINK}/{target}"

        if source in untracked:
          link(source, target)

  # unload collect_voicekeys dependency
  unload_dependency("character_voice", "ship_skin_words", "ship_skin_words_extra")


@runtime
def linker() -> None:
  files: dict[str, str] = {}

  link_extract_to_source()
  background(files)
  bgm(files)
  equipment(files)
  meowfficer(files)
  skin(files)
  skill(files)
  voiceline(files)

  (Path(__file__).parent / "linker.json").write_text(
    json.dumps(files, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )


if __name__ == "__main__":
  linker()
