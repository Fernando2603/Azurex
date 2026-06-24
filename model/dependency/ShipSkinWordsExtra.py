from pydantic import BaseModel


class ShipSkinWordsExtra(BaseModel, extra="allow"):
  id: int
  battle: list[tuple[int, str]] | str
  detail: list[tuple[int, str]] | str
  expedition: list[tuple[int, str]] | str
  feeling1: list[tuple[int, str]] | str
  feeling2: list[tuple[int, str]] | str
  feeling3: list[tuple[int, str]] | str
  feeling4: list[tuple[int, str]] | str
  feeling5: list[tuple[int, str]] | str
  headtouch: list[tuple[int, str]] | str
  home: list[tuple[int, str]] | str
  hp_warning: list[tuple[int, str]] | str
  login: list[tuple[int, str]] | str
  lose: list[tuple[int, str]] | str
  main: list[tuple[int, str]] | str
  main_extra: list[tuple[int, str]] | str
  mail: list[tuple[int, str]] | str
  mission: list[tuple[int, str]] | str
  mission_complete: list[tuple[int, str]] | str
  profile: list[tuple[int, str]] | str
  skill: list[tuple[int, str]] | str
  touch: list[tuple[int, str]] | str
  touch2: list[tuple[int, str]] | str
  unlock: list[tuple[int, str]] | str
  upgrade: list[tuple[int, str]] | str
  win_mvp: list[tuple[int, str]] | str
