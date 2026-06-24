import shutil
from pathlib import Path

import requests
from azlassets import config, versioncontrol
from azlassets.classes import Client, VersionType
from pydantic import TypeAdapter

from config import PARSER_ROOT, ROOT
from parser.bgm import bgm
from parser.equipment import equipment
from parser.meowfficer import meowfficer
from parser.meowfficer_talent import meowfficer_talent
from parser.skill import skill
from parser.skin import skin
from parser.voiceline import voiceline
from utility.debug import runtime

BADGE_URL = "https://img.shields.io/badge/{}-{}-{}?style=flat-square"
PARENT = Path(PARSER_ROOT, "versions")
PARENT.mkdir(parents=True, exist_ok=True)
LinkerAdapter = TypeAdapter(dict[str, str])


def create_version_badge(name: str, version: str, color: str = "blue") -> None:
  response = requests.get(BADGE_URL.format(name, version, color))

  if response.status_code == 200:
    Path(PARENT, f"{name}.svg").write_bytes(response.content)


@runtime
def parse_version() -> None:
  userconfig = config.load_user_config()
  client_directory = Path(userconfig.asset_directory, Client.EN.name)
  versioncontroller = versioncontrol.VersionController(client_directory)

  for vtype in VersionType:
    version = versioncontroller.load_version_string(vtype)

    if not version:
      continue

    create_version_badge(vtype.name, version)
    Path(PARENT, f"{vtype.name}.txt").write_text(version, encoding="utf-8")


@runtime
def copy_docs() -> None:
  for file in Path(ROOT, "docs").iterdir():
    target = Path(PARSER_ROOT, "docs", file.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file, target)


@runtime
def parse() -> None:
  path = Path(__file__).parent / "linker.json"

  if not path.exists():
    raise FileNotFoundError(path.as_posix())

  linker = LinkerAdapter.validate_json(path.read_bytes())

  bgm(linker)
  equipment(linker)
  meowfficer(linker)
  meowfficer_talent(linker)
  skill(linker)
  skin(linker)
  voiceline(linker)

  copy_docs()
  parse_version()


if __name__ == "__main__":
  parse()
