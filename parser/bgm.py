import json
from pathlib import Path
from typing import cast

from tinytag import Ogg, TinyTag

from config import PARSER_ROOT
from model.BackgroundMusic import BackgroundMusic, BackgroundMusicAdapter
from utility.debug import runtime


def load_previous_bgm() -> dict[str, BackgroundMusic]:
  path = PARSER_ROOT / "bgm.json"

  if not path.exists():
    return {}

  return BackgroundMusicAdapter.validate_json(path.read_bytes())


@runtime
def bgm(linker: dict[str, str]) -> None:
  storage = Path(PARSER_ROOT, "audio", "bgm")

  if not storage.exists():
    return

  result = load_previous_bgm()

  for file in storage.rglob("*.ogg"):
    if not file.is_file():
      continue

    tag = cast(Ogg, TinyTag.get(file))  # type: ignore
    title = file.stem

    result[title] = BackgroundMusic(
      title=title,
      size=int(tag.filesize),  # type: ignore
      duration=float(tag.duration),
      bitrate=float(tag.bitrate),
      sample_rate=int(tag.samplerate),
      link=linker[f"bgm.{title}"], # using rglob, linker always available
    )

  BGM_PATH = Path(PARSER_ROOT, "bgm.json")
  BGM_PATH.write_bytes(BackgroundMusicAdapter.dump_json(result, indent=2, ensure_ascii=False))

  BGM_LINK_PATH = Path(PARSER_ROOT, "bgm_link.json")
  BGM_LINK_PATH.write_text(
    json.dumps({k: v.link for k, v in result.items()}, indent=2, ensure_ascii=False),
    encoding="utf-8",
  )
