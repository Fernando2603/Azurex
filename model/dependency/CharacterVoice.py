from pydantic import BaseModel


class CharacterVoice(BaseModel):
  spine_action: str
  l2d_action: str
  unlock_condition: tuple[int, int]
  sp_trans_l2d: int
  resource_key: str
  profile_index: int
  voice_name: str
  key: str

