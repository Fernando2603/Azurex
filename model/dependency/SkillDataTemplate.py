from typing import Any

from pydantic import BaseModel, field_validator

type SkillDescAddBlock = list[tuple[str, str] | tuple[str, int] | tuple[str]]


class SkillDataTemplate(BaseModel):
  id: int
  desc: str
  type: int
  name: str
  max_level: int
  desc_add: dict[str, SkillDescAddBlock] | str

  @field_validator("desc_add", mode="before")
  @classmethod
  def validate_desc_add(cls, value: Any) -> Any:
    if not isinstance(value, list):
      return value

    return {str(i): v for i, v in enumerate(value, start=1)}  # type: ignore[return-value]
