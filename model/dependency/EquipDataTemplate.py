from pydantic import BaseModel


class EquipDataTemplateProperty(BaseModel):
  id: int
  prev: int
  next: int
  level: int
  # restore_gold: int
  # restore_item: list[tuple[int, int]]
  # destory_gold: int
  # destory_item: list[tuple[int, int]]
  # trans_use_gold: int
  # trans_use_item: list[tuple[int, int]]


class EquipDataTemplateBase(EquipDataTemplateProperty):
  type: int
  group: int
  important: int
  equip_limit: int
  # upgrade_formula_id: list[int]
  ship_type_forbidden: list[int]


class EquipDataTemplateUpgrade(EquipDataTemplateProperty):
  base: int


type EquipDataTemplate = EquipDataTemplateBase | EquipDataTemplateUpgrade
