import json
from pathlib import Path
from typing import cast

from config import PARSER_ROOT
from model.dependency import (
  EquipDataStatisticsBase,
  EquipDataStatisticsUpgrade,
  EquipDataTemplateBase,
)
from model.Equipment import (
  Equipment,
  EquipmentAdapter,
  EquipmentSkill,
  EquipmentSkillAdapter,
  EquipmentStats,
)
from utility.debug import runtime
from utility.dependency import load_dependency, unload_dependency
from utility.resolver import resolve_namecode


def parse_equipment_skill(skill_list: list[tuple[int, int]]) -> dict[str, EquipmentSkill]:
  skill_data_template = load_dependency("skill_data_template")

  result: dict[str, EquipmentSkill] = {}

  for skill, _ in skill_list:
    data = skill_data_template.get(str(skill))

    if not data:
      continue

    result[str(skill)] = EquipmentSkill(
      id=skill,
      name=resolve_namecode(data.name),
      desc=resolve_namecode(data.desc),
    )

  return result


def parse_equipment_statistics(base: str) -> dict[str, EquipmentStats]:
  equip_data_statistics = load_dependency("equip_data_statistics")
  equip_data_template = load_dependency("equip_data_template")

  attribute_names: dict[str, str] = {
    f"value_{i}": getattr(equip_data_statistics[base], f"attribute_{i}")
    for i in range(1, 5)
    if hasattr(equip_data_statistics[base], f"attribute_{i}")
  }

  current_equip_id: str = base
  previous_statistics: dict[str, int] = {}
  equipment_statistics: dict[str, EquipmentStats] = {}

  while current_equip_id != "0":
    current_statistics = cast(EquipDataStatisticsUpgrade, equip_data_statistics[current_equip_id])
    current_template = equip_data_template[current_equip_id]

    current_data = EquipmentStats()

    if (damage := current_statistics.damage) is not None:
      current_data["damage"] = damage

    for key, attribute in attribute_names.items():
      if (value := getattr(current_statistics, key)) is not None:
        previous_statistics[attribute] = int(value)
        current_data[attribute] = int(value)

      elif attribute in previous_statistics:
        current_data[attribute] = previous_statistics[attribute]

    if (anti_siren := current_statistics.anti_siren) is not None:
      current_data["anti_siren"] = int(anti_siren / 100)

    if ((weapon_id := current_statistics.weapon_id) is not None) and (len(weapon_id) > 0):
      current_data["weapon_id"] = weapon_id

    level = str(current_template.level or 0)
    # should do level-1 for the key... to get 0 indexed...
    # but it's already too late at this rate, just keep the legacy
    equipment_statistics[level] = EquipmentStats(
      {
        "id": int(current_equip_id),
        "level": int(level),
        "enhance": f"+{max(0, int(level) - 1)}",
        **current_data,
      }
    )

    current_equip_id = str(current_template.next)

  return equipment_statistics


@runtime
def equipment(linker: dict[str, str]) -> None:
  equip_data_statistics = load_dependency("equip_data_statistics")
  equip_data_template = load_dependency("equip_data_template")
  result: dict[str, Equipment] = {}
  skills: dict[str, EquipmentSkill] = {}

  for id, data in equip_data_template.items():
    if not isinstance(data, EquipDataTemplateBase):
      continue

    statistics = cast(EquipDataStatisticsBase, equip_data_statistics[id])
    equipment_skill: dict[str, EquipmentSkill] = {}

    if (skill_id := statistics.skill_id) is not None:
      equipment_skill = parse_equipment_skill(skill_id)
      skills.update(equipment_skill)

    result[id] = Equipment(
      name=resolve_namecode(statistics.name),
      desc=resolve_namecode(statistics.descrip) if statistics.descrip else None,
      label=statistics.label,
      rarity=statistics.rarity,
      nationality=statistics.nationality,
      type=statistics.type,
      skill=equipment_skill,
      icon=linker.get(f"equipment.{statistics.icon}"),
      stats=parse_equipment_statistics(id),
      important=bool(data.important),
      equip_limit=data.equip_limit,
      ship_type_forbidden=data.ship_type_forbidden,
    )

  unload_dependency("equip_data_statistics", "equip_data_template", "skill_data_template")

  EQUIPMENT_PATH = Path(PARSER_ROOT, "equipment.json")
  EQUIPMENT_PATH.write_bytes(EquipmentAdapter.dump_json(result, indent=2, ensure_ascii=False))

  EQUIPMENT_ICON_PATH = Path(PARSER_ROOT, "equipment_icon.json")
  EQUIPMENT_ICON_PATH.write_text(
    json.dumps({k: v.icon for k, v in result.items()}, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )

  EQUIPMENT_SKILL_PATH = Path(PARSER_ROOT, "equipment_skill.json")
  EQUIPMENT_SKILL_PATH.write_bytes(
    EquipmentSkillAdapter.dump_json(skills, indent=2, ensure_ascii=False)
  )
