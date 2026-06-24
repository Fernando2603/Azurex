from pydantic import BaseModel


class EquipDataStatisticsEquipParameters(BaseModel, extra="allow"):
  ambush_extra: int | None = None
  avoid_extra: int | None = None
  range: int | None = None
  hunting_lv: int | None = None


class EquipDataStatisticsProperty(BaseModel):
  id: int
  icon: str | None = None
  descrip: str | None = None
  damage: str | None = None
  value_1: str | None = None
  value_2: int | None = None
  value_3: int | None = None
  attribute_1: str | None = None
  attribute_2: str | None = None
  attribute_3: str | None = None
  torpedo_ammo: int | None = None
  anti_siren: int | None = None
  speciality: str | None = None
  skill_id: list[tuple[int, int]] | None = None
  hidden_skill_id: list[tuple[int, int]] | None = None
  weapon_id: list[int] | None = None
  ammo_icon: list[int] | None = None
  equip_parameters: EquipDataStatisticsEquipParameters | None = None


# there some distinct in Base & Upgrade, but this is enough for parser usage
class EquipDataStatisticsBase(EquipDataStatisticsProperty):
  name: str
  type: int
  rarity: int
  nationality: int
  label: list[str]

  # unused exlusive property
  # equip_info: list[int | tuple[int, int]]
  # property_rate: list[None]
  # ammo: int
  # tech: int
  # part_sub: list[int]
  # part_main: list[int]


class EquipDataStatisticsUpgrade(EquipDataStatisticsProperty):
  id: int
  base: int
  type: int | None = None
  name: str | None = None
  label: list[str] | None = None


EquipDataStatistics = EquipDataStatisticsBase | EquipDataStatisticsUpgrade
