from pydantic import BaseModel


class Buff(BaseModel):
  id: int
  icon: int | None = None
