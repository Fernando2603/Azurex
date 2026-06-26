from copy import deepcopy
from pathlib import Path

from config import PARSER_ROOT
from model.Skill import Skill, SkillAdapter, SkillIconAdapter
from utility.debug import runtime
from utility.dependency import load_dependency, unload_dependency
from utility.resolver import resolve_namecode


def get_skill_desc(id: str) -> str:
  skill_data_template = load_dependency("skill_data_template")
  skill = skill_data_template[id]

  if isinstance(skill.desc_add, str):
    return skill.desc

  line = skill.desc

  # desc_add have frozen trait from pydantic, copy before edit to be safe
  upgrade = deepcopy(skill.desc_add)

  # searching unfinished desc_add for retrofit/upgraded skill
  if max([int(k) for k in skill.desc_add], default=0) != len(skill.desc_add):
    prev_skill = skill_data_template.get(str(int(id) // 100))

    if (prev_skill is not None) and not isinstance(prev_skill.desc_add, str):
      for index, prev_desc_add in prev_skill.desc_add.items():
        if str(index) not in upgrade:
          upgrade[str(index)] = prev_desc_add

    # do nothing if doesnt match, just leave it

  for index, value in upgrade.items():
    line = line.replace(f"${index}", f"{value[0][0]} ({value[-1][0]})")

  return resolve_namecode(line)


@runtime
def skill(linker: dict[str, str]) -> None:
  skill_data_template = load_dependency("skill_data_template")

  result: dict[str, Skill] = {}

  for id, data in skill_data_template.items():
    if (
      (data.type == 0)
      or ("future content" in data.name.lower())
      or (data.max_level not in (1, 3, 10))
    ):
      continue

    result[id] = Skill(
      id=data.id,
      type=data.type,  # type: ignore
      name=resolve_namecode(data.name),
      desc=get_skill_desc(id),
      icon=linker.get(f"skill.{id}"),
      max_level=data.max_level,
    )

  unload_dependency("skill_data_template")

  SKILL_PATH = Path(PARSER_ROOT, "skill.json")
  SKILL_PATH.write_bytes(SkillAdapter.dump_json(result, indent=2, ensure_ascii=False))

  SKILL_ICON_PATH = Path(PARSER_ROOT, "skill_icon.json")
  SKILL_ICON_PATH.write_bytes(
    SkillIconAdapter.dump_json({k: v.icon for k, v in result.items()}, indent=2, ensure_ascii=False)
  )
