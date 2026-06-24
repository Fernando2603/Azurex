"""
Dependency is designed to be strictly/strong typed module\n
Dependency model only cover used keys for efficiency
"""

from pathlib import Path
from types import TracebackType
from typing import Any, Literal, overload

from pydantic import ConfigDict, TypeAdapter

from model.dependency import (
  Buff,
  CharacterVoice,
  CommanderAbilityGroup,
  CommanderAbilityTemplate,
  CommanderDataTemplate,
  CommanderSkillTemplate,
  EquipDataStatistics,
  EquipDataTemplate,
  NameCode,
  ShipDataGroup,
  ShipSkinTemplate,
  ShipSkinWords,
  ShipSkinWordsExtra,
  SkillDataTemplate,
  SkinPageTemplate,
)

CONFIG = ConfigDict(extra="ignore", frozen=True, cache_strings=True)
SKIN_WORDS_CONFIG = ConfigDict({**CONFIG, "extra": "allow"})


ADAPTERS = {
  "buff": TypeAdapter(dict[str, Buff], config=CONFIG),
  "character_voice": TypeAdapter(dict[str, CharacterVoice], config=CONFIG),
  "commander_ability_group": TypeAdapter(dict[str, CommanderAbilityGroup], config=CONFIG),
  "commander_ability_template": TypeAdapter(dict[str, CommanderAbilityTemplate], config=CONFIG),
  "commander_data_template": TypeAdapter(dict[str, CommanderDataTemplate], config=CONFIG),
  "commander_skill_template": TypeAdapter(dict[str, CommanderSkillTemplate], config=CONFIG),
  "equip_data_statistics": TypeAdapter(dict[str, EquipDataStatistics], config=CONFIG),
  "equip_data_template": TypeAdapter(dict[str, EquipDataTemplate], config=CONFIG),
  "name_code": TypeAdapter(dict[str, NameCode], config=CONFIG),
  "ship_data_group": TypeAdapter(dict[str, ShipDataGroup], config=CONFIG),
  "ship_skin_template": TypeAdapter(dict[str, ShipSkinTemplate], config=CONFIG),
  "ship_skin_words": TypeAdapter(dict[str, ShipSkinWords], config=SKIN_WORDS_CONFIG),
  "ship_skin_words_extra": TypeAdapter(dict[str, ShipSkinWordsExtra], config=SKIN_WORDS_CONFIG),
  "skill_data_template": TypeAdapter(dict[str, SkillDataTemplate], config=CONFIG),
  "skin_page_template": TypeAdapter(dict[str, SkinPageTemplate], config=CONFIG),
}

DependencyName = Literal[
  "buff",
  "character_voice",
  "commander_ability_group",
  "commander_ability_template",
  "commander_data_template",
  "commander_skill_template",
  "equip_data_statistics",
  "equip_data_template",
  "name_code",
  "ship_data_group",
  "ship_skin_template",
  "ship_skin_words",
  "ship_skin_words_extra",
  "skill_data_template",
  "skin_page_template",
]

_DEPENDENCY_CACHE: dict[str, dict[str, Any]] = {}


@overload
def load_dependency(
  name: Literal["buff"],
) -> dict[str, Buff]: ...


@overload
def load_dependency(
  name: Literal["character_voice"],
) -> dict[str, CharacterVoice]: ...


@overload
def load_dependency(
  name: Literal["commander_ability_group"],
) -> dict[str, CommanderAbilityGroup]: ...


@overload
def load_dependency(
  name: Literal["commander_ability_template"],
) -> dict[str, CommanderAbilityTemplate]: ...


@overload
def load_dependency(
  name: Literal["commander_data_template"],
) -> dict[str, CommanderDataTemplate]: ...


@overload
def load_dependency(
  name: Literal["commander_skill_template"],
) -> dict[str, CommanderSkillTemplate]: ...


@overload
def load_dependency(
  name: Literal["equip_data_statistics"],
) -> dict[str, EquipDataStatistics]: ...


@overload
def load_dependency(
  name: Literal["equip_data_template"],
) -> dict[str, EquipDataTemplate]: ...


@overload
def load_dependency(
  name: Literal["name_code"],
) -> dict[str, NameCode]: ...


@overload
def load_dependency(
  name: Literal["ship_data_group"],
) -> dict[str, ShipDataGroup]: ...


@overload
def load_dependency(
  name: Literal["ship_skin_template"],
) -> dict[str, ShipSkinTemplate]: ...


@overload
def load_dependency(
  name: Literal["ship_skin_words"],
) -> dict[str, ShipSkinWords]: ...


@overload
def load_dependency(
  name: Literal["ship_skin_words_extra"],
) -> dict[str, ShipSkinWordsExtra]: ...


@overload
def load_dependency(
  name: Literal["skill_data_template"],
) -> dict[str, SkillDataTemplate]: ...


@overload
def load_dependency(
  name: Literal["skin_page_template"],
) -> dict[str, SkinPageTemplate]: ...


def load_dependency(name: DependencyName) -> dict[str, Any]:
  if name in _DEPENDENCY_CACHE:
    return _DEPENDENCY_CACHE[name]

  path = (Path(__file__).parents[1] / "dependency" / name).with_suffix(".json")

  if not path.exists():
    raise FileNotFoundError(path.as_posix())

  data = ADAPTERS[name].validate_json(path.read_bytes())
  _DEPENDENCY_CACHE[name] = data
  return data


def unload_dependency(*names: DependencyName) -> None:
  for name in names:
    _DEPENDENCY_CACHE.pop(name, None)


class Dependency[K: DependencyName]:
  def __init__(self, name: K) -> None:
    self.name: K = name
    self.unload = True

  @overload
  def __enter__(
    self: "Dependency[Literal['buff']]",
  ) -> dict[str, Buff]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['character_voice']]",
  ) -> dict[str, CharacterVoice]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['commander_ability_group']]",
  ) -> dict[str, CommanderAbilityGroup]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['commander_ability_template']]",
  ) -> dict[str, CommanderAbilityTemplate]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['commander_data_template']]",
  ) -> dict[str, CommanderDataTemplate]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['commander_skill_template']]",
  ) -> dict[str, CommanderSkillTemplate]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['equip_data_statistics']]",
  ) -> dict[str, EquipDataStatistics]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['equip_data_template']]",
  ) -> dict[str, EquipDataTemplate]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['name_code']]",
  ) -> dict[str, NameCode]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['ship_data_group']]",
  ) -> dict[str, ShipDataGroup]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['ship_skin_template']]",
  ) -> dict[str, ShipSkinTemplate]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['ship_skin_words']]",
  ) -> dict[str, ShipSkinWords]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['ship_skin_words_extra']]",
  ) -> dict[str, ShipSkinWordsExtra]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['skill_data_template']]",
  ) -> dict[str, SkillDataTemplate]: ...

  @overload
  def __enter__(
    self: "Dependency[Literal['skin_page_template']]",
  ) -> dict[str, SkinPageTemplate]: ...

  def __enter__(self) -> Any:
    if self.name in _DEPENDENCY_CACHE:
      self.unload = False
      return _DEPENDENCY_CACHE[self.name]

    return load_dependency(self.name)

  def __exit__(
    self,
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: TracebackType | None,
  ) -> None:
    if self.unload:
      unload_dependency(self.name)
