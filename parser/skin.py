from collections import defaultdict
from pathlib import Path

from config import PARSER_ROOT
from model.Skin import (
  SharedSkin,
  ShipSkin,
  ShipSkinAdapter,
  ShipSkinListAdapter,
  Skin,
  SkinAdapter,
  SkinListAdapter,
)
from utility.debug import runtime
from utility.dependency import load_dependency, unload_dependency
from utility.resolver import resolve_namecode

# model\vo\shipskin.lua
SKIN_TAG = {
  1: "live2d",
  2: "bg",
  3: "effect",
  4: "dynamicbg",
  5: "bgm",
  6: "dynamic",
  7: "dynamic+",
  8: "change",
  9: "l2d+",
  10: "doube_voice",
  11: "asmr",
}


@runtime
def skin(linker: dict[str, str]) -> None:
  ship_skin_template = load_dependency("ship_skin_template")
  skin_page_template = load_dependency("skin_page_template")
  ship_data_group = load_dependency("ship_data_group")

  result: dict[str, Skin] = {}
  skin_group: dict[int, list[str]] = defaultdict(list)
  group_name: dict[int, str] = {}

  for id, data in ship_skin_template.items():
    skin_group[data.ship_group].append(id)
    name = resolve_namecode(data.name)
    type = skin_page_template.get(str(data.shop_type_id))

    if id == f"{data.ship_group}0":
      group_name[data.ship_group] = name

    result[id] = Skin(
      id=data.id,
      gid=data.ship_group,
      name=name,
      type=type.english_name if type else "Default",
      desc=resolve_namecode(data.desc),
      tag=[SKIN_TAG.get(tag, tag) for tag in data.tag],
      illustrator=data.illustrator,
      illustrator2=data.illustrator2,
      voice_actor=data.voice_actor,
      voice_actor2=data.voice_actor_2,
      bgm=linker.get(f"bgm.{data.bgm}"),
      background=linker.get(f"background.{data.bg}"),
      background2=linker.get(f"background.{data.bg_sp}"),
      painting=linker.get(f"skin.{id}.painting"),
      painting_n=linker.get(f"skin.{id}.painting_n"),
      banner=linker.get(f"skin.{id}.banner"),
      chibi=linker.get(f"skin.{id}.chibi"),
      icon=linker.get(f"skin.{id}.icon"),
      qicon=linker.get(f"skin.{id}.qicon"),
      shipyard=linker.get(f"skin.{id}.shipyard"),
    )

  ship_skin: dict[str, ShipSkin] = {}

  for data in ship_data_group.values():
    if data.group_type not in skin_group:
      continue

    skins: dict[str, Skin | SharedSkin] = {
      skin_id: result[skin_id] for skin_id in skin_group[data.group_type]
    }

    for group_id in data.share_group_id:
      if group_id not in skin_group:
        continue

      for skin_id in skin_group[group_id]:
        if result[skin_id].type.lower() in ("default", "retrofit"):
          continue

        skins[skin_id] = SharedSkin.model_construct(
          **result[skin_id].model_dump(), shared=str(group_id)
        )

    ship_skin[str(data.group_type)] = ShipSkin(
      gid=data.group_type,
      name=group_name[data.group_type],
      skins=skins,
    )

  unload_dependency("ship_skin_template", "skin_page_template", "ship_data_group")

  SKIN_PATH = Path(PARSER_ROOT, "skin.json")
  SKIN_PATH.write_bytes(SkinAdapter.dump_json(result, indent=2, ensure_ascii=False))

  SKIN_LIST_PATH = Path(PARSER_ROOT, "skin_list.json")
  SKIN_LIST_PATH.write_bytes(
    SkinListAdapter.dump_json(list(result.values()), indent=2, ensure_ascii=False)
  )

  SHIP_SKIN_PATH = Path(PARSER_ROOT, "ship_skin.json")
  SHIP_SKIN_PATH.write_bytes(ShipSkinAdapter.dump_json(ship_skin, indent=2, ensure_ascii=False))

  SHIP_SKIN_LIST_PATH = Path(PARSER_ROOT, "ship_skin_list.json")
  SHIP_SKIN_LIST_PATH.write_bytes(
    ShipSkinListAdapter.dump_json(
      [x.as_list() for x in ship_skin.values()],
      indent=2,
      ensure_ascii=False,
    )
  )
