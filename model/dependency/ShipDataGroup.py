from pydantic import BaseModel


class ShipDataGroup(BaseModel):
  group_type: int
  share_group_id: list[int]
