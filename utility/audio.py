import io
from pathlib import Path
from typing import cast

from acb.acb import ACBFile
from pydub import AudioSegment


def extract_audio(root: Path, filepath: str, target: Path) -> list[Path]:
  source = Path(root, filepath)
  output: list[Path] = []

  if not source.exists():
    raise FileNotFoundError(source.as_posix())

  try:
    with ACBFile(source, hca_keys="0x2354E95356C72") as acb:
      for track in acb.track_list.tracks:
        name = cast(str, track.name)
        dest = Path(target, source.stem, name).with_suffix(".ogg")
        dest.parent.mkdir(parents=True, exist_ok=True)

        data = acb.get_track_data(track)
        audio = AudioSegment.from_file(io.BytesIO(data), format="hca")

        if dest.exists():
          print(f'WARN: Replacing "{dest.as_posix()}".')

        # character voice
        # default quality = 3
        if source.name.lower().startswith("cv"):
          audio.export(dest, format="ogg")

        # higher quality other than character voice
        # for bgm sound with quality lower than 5 is unbearable
        else:
          audio.export(dest, format="ogg", parameters=["-q:a", "5"], tags={"title": name})

        output.append(dest)

  except KeyError:
    if source.suffix != "f":
      raise

  return output
