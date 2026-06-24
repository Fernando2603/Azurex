from pydantic import BaseModel


class ShipSkinTemplate(BaseModel):
  id: int
  name: str
  group_index: int
  ship_group: int
  illustrator: int
  illustrator2: int
  shop_type_id: int
  desc: str
  tag: list[int]
  painting: str
  bg: str
  bg_sp: str
  bgm: str
  voice_actor: int
  voice_actor_2: int

