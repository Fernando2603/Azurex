from typing import TypedDict

from pydantic import BaseModel, TypeAdapter


class EquipmentSkill(BaseModel):
  id: int
  name: str
  desc: str


class EquipmentStats(TypedDict, total=False):
  id: int
  level: int
  enhance: str
  air: int
  anti_siren: int
  antiaircraft: int
  antisub: int
  cannon: int
  damage: str
  dodge: int
  durability: int
  hit: int
  luck: int
  oxy_max: int
  raid_distance: int
  reload: int
  speed: int
  torpedo: int
  weapon_id: list[int]


class Equipment(BaseModel):
  name: str
  desc: str | None
  label: list[str]
  rarity: int
  nationality: int
  type: int
  skill: dict[str, EquipmentSkill]
  icon: str | None
  stats: dict[str, EquipmentStats]
  important: bool
  equip_limit: int
  ship_type_forbidden: list[int]


EquipmentSkillAdapter = TypeAdapter(dict[str, EquipmentSkill])
EquipmentAdapter = TypeAdapter(dict[str, Equipment])
