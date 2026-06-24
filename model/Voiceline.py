from pydantic import BaseModel, TypeAdapter


class Voicekey(BaseModel):
  link: str | None
  line: str


class VoicekeyCoupleEncourage(Voicekey):
  type: int
  list: list[int | float]
  count: int


type Voiceline = dict[str, Voicekey | VoicekeyCoupleEncourage]

VoicelineAdapter = TypeAdapter(dict[str, Voiceline])
VoicelinkAdapter = TypeAdapter(dict[str, dict[str, str]])
