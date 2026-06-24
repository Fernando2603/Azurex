from pydantic import BaseModel

type CoupleEncourage = tuple[list[int | float], int, str, int]


class ShipSkinWords(BaseModel, extra="allow"):
  id: int
  voice_key: int
  voice_key_2: int
  battle: str
  couple_encourage: list[CoupleEncourage] | str
  detail: str
  drop_descrip: str
  expedition: str
  feeling1: str
  feeling2: str
  feeling3: str
  feeling4: str
  feeling5: str
  headtouch: str
  home: str
  hp_warning: str
  login: str
  lose: str
  mail: str
  main: str
  mission: str
  mission_complete: str
  profile: str
  propose: str
  skill: str
  touch: str
  touch2: str
  unlock: str
  upgrade: str
  win_mvp: str
  vote: str
  gift_prefer: str
  gift_dislike: str
