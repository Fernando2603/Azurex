from pydantic import BaseModel


class NameCode(BaseModel):
  id: int
  name: str
