from pydantic import BaseModel, TypeAdapter


class BackgroundMusic(BaseModel):
  title: str
  size: int
  duration: float
  bitrate: float
  sample_rate: int
  link: str


BackgroundMusicAdapter = TypeAdapter(dict[str, BackgroundMusic])
