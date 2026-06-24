from pydantic import BaseModel


class SkinPageTemplate(BaseModel):
  id: int
  english_name: str
