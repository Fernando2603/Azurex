from pydantic import BaseModel


class CommanderSkillTemplate(BaseModel):
  lv: int
  exp: int
  effect_tactic: list[int]
  effect_tactic_world: list[int]
  name: str
  prev_id: int
  icon: str
  desc_world: str
  next_id: int
  desc: str
  id: int
