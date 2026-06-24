from pathlib import Path

from config import PARSER_ROOT
from model.Voiceline import (
  Voicekey,
  VoicekeyCoupleEncourage,
  Voiceline,
  VoicelineAdapter,
  VoicelinkAdapter,
)
from utility.debug import runtime
from utility.dependency import Dependency, unload_dependency
from utility.resolver import resolve_namecode
from utility.voicekey import collect_voicekeys


@runtime
def voiceline(linker: dict[str, str]) -> None:
  result: dict[str, Voiceline] = {}

  with Dependency("ship_skin_template") as ship_skin_template:
    for id, data in ship_skin_template.items():
      voiceline: Voiceline = {}

      for voicekey, value, _ in collect_voicekeys(id, data.ship_group, data.group_index):
        link = linker.get(f"voiceline.{id}.{voicekey}")

        if (value == "nil") and (link is None):
          continue

        if isinstance(value, str):
          voiceline[voicekey] = Voicekey(link=link, line=value)
          continue

        requirement, count, line, type = value
        voiceline[voicekey] = VoicekeyCoupleEncourage(
          link=link,
          line=resolve_namecode(line),
          type=type,
          list=requirement,
          count=count,
        )

      result[id] = voiceline

  # unload collect_voicekeys dependency
  unload_dependency("character_voice", "ship_skin_words", "ship_skin_words_extra")

  VOICELINE_PATH = Path(PARSER_ROOT, "voiceline.json")
  VOICELINE_PATH.write_bytes(VoicelineAdapter.dump_json(result, indent=2, ensure_ascii=False))

  VOICELINK_PATH = Path(PARSER_ROOT, "voicelink.json")
  VOICELINK_PATH.write_bytes(
    VoicelinkAdapter.dump_json(
      {k: {xk: xv.link for xk, xv in v.items() if xv.link is not None} for k, v in result.items()},
      indent=2,
      ensure_ascii=False,
    )
  )
