from pydantic import BaseModel


class CommanderDataTemplate(BaseModel):
  bg: str
  exp: int
  tactic_value: int
  rarity: int
  name: str
  ability_show: list[int]
  group_type: int
  skill_id: int
  ability_refresh_type: int
  desc: str
  command_value: int
  nationality: int
  painting: str
  exp_cost: int
  max_level: int
  support_value: int
  id: int
