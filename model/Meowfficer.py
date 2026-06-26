from typing import Literal

from pydantic import BaseModel, TypeAdapter


class MeowfficerStats(BaseModel):
  command: int
  support: int
  tactic: int


class MeowfficerSkillLevel(BaseModel):
  id: int
  desc: str | None
  opsi: str | None


class MeowfficerSkill(BaseModel):
  id: int
  name: str
  icon: str | None
  level: dict[str, MeowfficerSkillLevel]


class Meowfficer(BaseModel):
  id: int
  name: str
  rarity: str
  type: list[str]
  slot: Literal["General", "Command", "Staff"]
  timer: str | None
  nationality: int
  stats: MeowfficerStats
  skill: MeowfficerSkill
  image: str | None
  icon: str | None
  banner: str | None
  talent: list[int]


MeowfficerAdapter = TypeAdapter(dict[str, Meowfficer])
MeowfficerListAdapter = TypeAdapter(list[Meowfficer])
