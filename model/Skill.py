from enum import IntEnum

from pydantic import BaseModel, TypeAdapter


class SkillType(IntEnum):
  offense = 1
  defense = 2
  support = 3


class Skill(BaseModel):
  id: int
  type: SkillType
  name: str
  desc: str
  icon: str | None
  max_level: int


SkillAdapter = TypeAdapter(dict[str, Skill])
SkillListAdapter = TypeAdapter(list[Skill])
