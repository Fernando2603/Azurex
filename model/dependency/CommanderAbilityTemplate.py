from pydantic import BaseModel


class CommanderAbilityTemplate(BaseModel):
  id: int
  next: int
  worth: int
  group_id: int
  cost: int
  name: str
  desc: str
  icon: str
  add: list[tuple[int, list[int], list[int], int, int]]
  add_desc: list[tuple[str, int] | tuple[str, int, str]]
