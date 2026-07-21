from pathlib import Path
from typing import cast

from PIL import Image
from UnityPy import AssetsManager
from UnityPy.classes import AnimationClip, Sprite
from UnityPy.enums import ClassIDType


class Emoji:
  def __init__(self, root: Path, filepath: str) -> None:
    self.path = Path(root, filepath)

    if not self.path.exists():
      raise FileNotFoundError(self.path.as_posix())

    self.asset = AssetsManager(self.path.as_posix())
    self.duration = 0
    self.images: list[Image.Image] = []

    if clip := self.get_animation_clip():
      self.duration = 1000 / clip.m_SampleRate
      self.images = self.get_frames(clip)
      return

    for obj in self.asset.objects:  # type: ignore
      if obj.type == ClassIDType.Sprite:
        self.images.append(self.get_image(obj.parse_as_object()))  # type: ignore

  def get_animation_clip(self) -> AnimationClip | None:
    for obj in self.asset.objects:  # type: ignore
      if obj.type == ClassIDType.AnimationClip:
        return obj.parse_as_object()  # type: ignore

  def get_frames(self, clip: AnimationClip) -> list[Image.Image]:
    sprite_by_path_id: dict[int, Sprite] = {
      o.path_id: cast(Sprite, o.parse_as_object())
      for o in self.asset.objects  # type: ignore
      if o.type == ClassIDType.Sprite
    }

    result: list[Image.Image] = []

    for pptr in clip.m_ClipBindingConstant.pptrCurveMapping:  # type: ignore
      path_id = pptr.m_PathID

      if path_id not in sprite_by_path_id:
        raise KeyError(path_id)

      result.append(self.get_image(sprite_by_path_id[path_id]))

    return result

  def get_image(self, sprite: Sprite) -> Image.Image:
    image = sprite.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    canvas = Image.new("RGBA", (int(sprite.m_Rect.width), int(sprite.m_Rect.height)), (0, 0, 0, 0))
    off_x = int(sprite.m_RD.textureRectOffset.x)
    off_y = int(sprite.m_RD.textureRectOffset.y)
    canvas.paste(image, (off_x, off_y), image)
    image = canvas.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    return image

  @staticmethod
  def try_save_image(image: Image.Image, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
      target.unlink()
      print(f'WARN: Replacing "{target}".')

    image.save(target, lossless=True)
    return target

  def save(self, path: Path) -> Path | None:
    if self.duration == 0:
      if len(self.images) == 1:
        return self.try_save_image(self.images[0], path.with_suffix(".webp"))

      if len(self.images) > 1:
        for index, image in enumerate(self.images, start=1):
          self.try_save_image(image, path.with_suffix("").joinpath(f"{index}.webp"))

        return path

      return

    target = path.with_suffix(".webp")
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
      target.unlink()
      print(f'WARN: Replacing "{target}".')

    self.images[0].save(
      target,
      save_all=True,
      append_images=self.images[1:],
      duration=self.duration,
      loop=0,
      lossless=True,
    )

    return target
