from pathlib import Path
from typing import Literal, TypedDict

from config import PARSER_ROOT
from model.Meowfficer import (
  Meowfficer,
  MeowfficerAdapter,
  MeowfficerListAdapter,
  MeowfficerSkill,
  MeowfficerSkillLevel,
  MeowfficerStats,
)
from utility.debug import runtime
from utility.dependency import load_dependency, unload_dependency


class _MeowfficerData(TypedDict):
  slot: Literal["Command", "Staff", "General"]
  timer: str | None
  type: list[str]


# manual insert, because slot, type & timer is processed in server
# support legacy meowfficer are included
MEOWFFICER_DATA = {
  "10011": _MeowfficerData(slot="Command", timer="10:24:00", type=["DD"]),
  "10021": _MeowfficerData(slot="General", timer="10:45:00", type=["BB", "BC", "BBV"]),
  "11011": _MeowfficerData(slot="Command", timer="06:09:00", type=["DD"]),
  "11021": _MeowfficerData(slot="Staff", timer="05:36:00", type=["CV", "CVL"]),
  "12011": _MeowfficerData(slot="Staff", timer="02:03:00", type=["CV", "CVL"]),
  "12021": _MeowfficerData(slot="Staff", timer="02:25:00", type=["CL", "CA", "CB"]),
  "20011": _MeowfficerData(slot="Staff", timer="10:05:00", type=["BB", "BC", "BBV"]),
  "20021": _MeowfficerData(slot="Command", timer="10:27:00", type=["BB", "BC", "BBV"]),
  "21011": _MeowfficerData(slot="Staff", timer="06:16:00", type=["CL", "CA", "CB"]),
  "21021": _MeowfficerData(slot="Staff", timer="05:30:00", type=["DD"]),
  "21031": _MeowfficerData(slot="Staff", timer="06:43:00", type=["CV", "CVL"]),
  "21041": _MeowfficerData(slot="Staff", timer="07:26:00", type=["BB", "BC", "BBV"]),
  "22011": _MeowfficerData(slot="Staff", timer="02:17:00", type=["BB", "BC", "BBV"]),
  "22021": _MeowfficerData(slot="Staff", timer="01:39:00", type=["CL", "CA", "CB"]),
  "30011": _MeowfficerData(slot="Staff", timer="09:58:00", type=["CV", "CVL"]),
  "30021": _MeowfficerData(slot="Command", timer="09:40:00", type=["CL", "CA", "CB"]),
  "31011": _MeowfficerData(slot="Staff", timer="05:37:00", type=["CV", "CVL"]),
  "31021": _MeowfficerData(slot="Staff", timer="06:23:00", type=["DD"]),
  "32011": _MeowfficerData(slot="Staff", timer="02:06:00", type=["CL", "CA", "CB"]),
  "32021": _MeowfficerData(slot="Staff", timer="01:55:00", type=["BB", "BC", "BBV"]),
  "40011": _MeowfficerData(slot="Command", timer="09:35:00", type=["SS", "SSV"]),
  "40021": _MeowfficerData(slot="Staff", timer="10:03:00", type=["BB", "BC", "BBV"]),
  "41011": _MeowfficerData(slot="Staff", timer="06:45:00", type=["BB", "BC", "BBV"]),
  "41021": _MeowfficerData(slot="Staff", timer="05:57:00", type=["SS", "SSV"]),
  "41031": _MeowfficerData(slot="Staff", timer="05:52:00", type=["SS", "SSV"]),
  "42011": _MeowfficerData(slot="Staff", timer="01:54:00", type=["CL", "CA", "CB"]),
  "42021": _MeowfficerData(slot="Staff", timer="02:32:00", type=["DD"]),
}


def parse_meowfficer_rarity(rarity: int) -> str:
  match rarity:
    case 2:
      return "Normal"
    case 3:
      return "Rare"
    case 4:
      return "Elite"
    case 5:
      return "Super Rare"
    case 6:
      return "Ultra Rare"
    case _:
      raise ValueError(f"Unknown rarity {rarity}")


def parse_meowfficer_skill(skill: int, icon: str | None) -> MeowfficerSkill:
  commander_skill_template = load_dependency("commander_skill_template")

  level: dict[str, MeowfficerSkillLevel] = {}
  current_id = skill

  while current_id != 0:
    if str(current_id) not in commander_skill_template:
      raise ValueError(f"Meowfficer skill '{current_id}' not found ")

    data = commander_skill_template[str(current_id)]

    level[str(data.lv)] = MeowfficerSkillLevel(
      id=data.id,
      desc=data.desc,
      opsi=data.desc_world,
    )

    current_id = data.next_id

  return MeowfficerSkill(
    id=skill,
    name=commander_skill_template[str(skill)].name,
    icon=icon,
    level=level,
  )


@runtime
def meowfficer(linker: dict[str, str]) -> None:
  commander_data_template = load_dependency("commander_data_template")
  result: dict[str, Meowfficer] = {}

  for id, data in commander_data_template.items():
    result[id] = Meowfficer(
      id=data.id,
      name=data.name,
      rarity=parse_meowfficer_rarity(data.rarity),
      type=MEOWFFICER_DATA.get(id, {}).get("type", []),  # type: ignore
      slot=MEOWFFICER_DATA.get(id, {}).get("slot", "General"),  # type: ignore
      timer=MEOWFFICER_DATA.get(id, {}).get("timer", None),  # type: ignore
      nationality=data.nationality,
      stats=MeowfficerStats(
        command=data.command_value,
        support=data.support_value,
        tactic=data.tactic_value,
      ),
      skill=parse_meowfficer_skill(data.skill_id, linker.get(f"meowfficer.skill.{data.skill_id}")),
      image=linker.get(f"meowfficer.image.{id}"),
      icon=linker.get(f"meowfficer.icon.{id}"),
      banner=linker.get(f"meowfficer.banner.{id}"),
      talent=data.ability_show,
    )

  unload_dependency("commander_data_template", "commander_skill_template")

  MEOWFFICER_PATH = Path(PARSER_ROOT, "meowfficer.json")
  MEOWFFICER_PATH.write_bytes(MeowfficerAdapter.dump_json(result, indent=2, ensure_ascii=False))

  MEOWFFICER_LIST_PATH = Path(PARSER_ROOT, "meowfficer_list.json")
  MEOWFFICER_LIST_PATH.write_bytes(
    MeowfficerListAdapter.dump_json(list(result.values()), indent=2, ensure_ascii=False)
  )
