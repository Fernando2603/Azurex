from pydantic import BaseModel


class CommanderAbilityGroup(BaseModel):
  id: int
  ability_list: list[int]
