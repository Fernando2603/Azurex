from pathlib import Path

from config import PARSER_ROOT
from model.MeowfficerTalent import (
  MeowfficerTalent,
  MeowfficerTalentAdapter,
  MeowfficerTalentListAdapter,
  MeowfficerTalentStats,
)
from utility.debug import runtime
from utility.dependency import Dependency
from utility.resolver import resolve_namecode

MEOWFFICER_TALENT_STATS = {
  "HP": "Health",
  "FP": "Firepower",
  "EVA": "Evasion",
  "RLD": "Reload",
  "ASW": "Anti-Submarine Warfare",
  "AA": "Anti-Air",
  "AVI": "Aviation",
  "TRP": "Torpedo",
  "Accuracy": "Accuracy",
  "Torp Crit Rate": "Torpedo Critical Rate",
  "Speed": "Speed",
  "DMG dealt": "Damage Dealt",
  "DMG taken": "Damage Taken",
  "LCK": "Luck",
  "MG Crit Rate": "Main Gun Critical Rate",
}

MEOWFFICER_TALENT_TYPE_LIST = {
  "DDs": "DD",
  "CLs": "CL",
  "CAs": "CA",
  "CBs": "CB",
  "BBs": "BB",
  "IXs": "IX",
  "IXVs": "IXV",
  "IXMs": "IXM",
  "SSVs": "SSV",
  "SSs": "SS",
  "BCs": "BC",
  "<BBs": "BB",
  "BBVs": "BBV",
  "BMs": "BM",
  "CVs": "CV",
  "CVLs": "CVL",
  "AEs": "AE",
  "ARs": "AR",
  "Vanguard": "Vanguard",
  "Main Fleet": "Main",
  "E. Union": "Eagle Union",
  "R. Navy": "Royal Navy",
  "S. Empire": "Sakura Empire",
  "I. Blood": "Iron Blood",
  "D. Empery": "Dragon Empery",
  "N. Parliament": "Northern Parliament",
  "I. Libre": "Iris Libre",
  "V. Dominion": "Vichya Dominion",
}


def parse_meowfficer_talent_stats(
  add_desc: list[tuple[str, int] | tuple[str, int, str]],
) -> list[MeowfficerTalentStats]:
  result: list[MeowfficerTalentStats] = []

  for add in add_desc:
    desc, value = add[:2]
    apply: list[str] = []

    if ":" in desc:
      pos = desc.index(":")

      if "&" in desc:
        apply.extend(x.strip() for x in desc[0:pos].split("&"))
      elif "," in desc:
        apply.extend(x.strip() for x in desc[0:pos].split(","))
      else:
        apply.append(desc[0:pos])

      stat = MEOWFFICER_TALENT_STATS.get(desc[pos + 1 :].strip(), desc)
    else:
      stat = MEOWFFICER_TALENT_STATS.get(desc, desc)

    push = True
    apply = [MEOWFFICER_TALENT_TYPE_LIST.get(x, x) for x in apply]

    for talent in result:
      if (talent.stats == stat) and (talent.value == value):
        talent.apply.extend(apply)
        push = False
        break

    if push:
      result.append(
        MeowfficerTalentStats(
          apply=apply,
          stats=stat,
          value=value,
          type="percentage" if (len(add) > 2) and (add[2] == "%") else "value",
        )
      )

  return result


@runtime
def meowfficer_talent(linker: dict[str, str]) -> None:
  result: dict[str, MeowfficerTalent] = {}

  with Dependency("commander_ability_template") as commander_ability_template:
    for id, data in commander_ability_template.items():
      result[id] = MeowfficerTalent(
        id=data.id,
        group_id=data.group_id,
        name=data.name,
        desc=resolve_namecode(data.desc),
        stats=parse_meowfficer_talent_stats(data.add_desc),
        level=data.worth,
        next=data.next,
        image=linker.get(f"meowfficer.talent.{data.icon}"),
        available=True, # old API support.
      )

  MEOWFFICER_TALENT_PATH = Path(PARSER_ROOT, "meowfficer_talent.json")
  MEOWFFICER_TALENT_PATH.write_bytes(
    MeowfficerTalentAdapter.dump_json(result, indent=2, ensure_ascii=False)
  )

  MEOWFFICER_TALENT_LIST_PATH = Path(PARSER_ROOT, "meowfficer_talent_list.json")
  MEOWFFICER_TALENT_LIST_PATH.write_bytes(
    MeowfficerTalentListAdapter.dump_json(list(result.values()), indent=2, ensure_ascii=False)
  )
