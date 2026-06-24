from typing import Literal

from pydantic import BaseModel, TypeAdapter


class MeowfficerTalentStats(BaseModel):
  apply: list[str]
  stats: str
  value: int
  type: Literal["percentage", "value"]


class MeowfficerTalent(BaseModel):
  id: int
  group_id: int
  name: str
  desc: str
  stats: list[MeowfficerTalentStats]
  level: int
  next: int
  image: str | None
  available: bool


MeowfficerTalentAdapter = TypeAdapter(dict[str, MeowfficerTalent])
MeowfficerTalentListAdapter = TypeAdapter(list[MeowfficerTalent])
