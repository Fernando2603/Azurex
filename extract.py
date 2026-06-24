import itertools
import multiprocessing
from collections.abc import Generator
from pathlib import Path
from typing import cast

from azlassets import config, extractor, versioncontrol
from azlassets.classes import BundlePath, Client, SimpleVersionResult, VersionType
from azurpaint import Azurpaint
from azurpaint.exception import PrefabNotFound
from PIL import Image
from UnityPy import AssetsManager
from UnityPy.classes import Sprite, Texture2D
from UnityPy.enums import ClassIDType
from UnityPy.files import ObjectReader

from utility.audio import extract_audio
from utility.painting_map import PaintingMap


def load_images(
  filepath: str,
) -> Generator[tuple[ObjectReader[Texture2D | Sprite], Texture2D | Sprite], None, None]:
  am = AssetsManager(filepath)
  type = ClassIDType.Sprite if filepath in ("attricon", "shiptype") else ClassIDType.Texture2D

  for obj in am.objects:  # type: ignore
    if obj.type == type:
      yield obj, obj.parse_as_object()


def try_save_image(image: Image.Image, target: Path) -> Path:
  target.parent.mkdir(parents=True, exist_ok=True)

  if target.exists():
    target.unlink()
    print(f'WARN: Replacing "{target}".')

  image.save(target)
  return target


def extract_assetbundle(
  root: Path,
  filepath: str,
  target: Path,
  dependencies: list[str],
) -> Path | None:
  try:
    if filepath.startswith("cue/"):
      if not filepath.endswith(".b"):
        return None

      extract_audio(root, filepath, Path(target, "cue"))
      return Path(target, filepath).with_suffix("")

    if filepath.startswith("painting/"):
      try:
        azurpaint = Azurpaint(path=root, prefab=filepath)
      except PrefabNotFound:
        return None

      if len(dependencies):
        azurpaint.load(dependencies)

      painting = azurpaint.create(trim=True, downscale=True)
      target = Path(target, filepath).with_suffix(".png")

      return try_save_image(painting, target)

    path = Path(root, filepath)
    all_images: list[tuple[Image.Image, str]] = []

    for reader, image_object in load_images(str(path)):
      if image_object.m_Name == "UISprite":
        continue

      if "char" in (reader.container or ""):  # type:ignore
        continue

      all_images.append((image_object.image, image_object.m_Name))

    if len(all_images) == 1:
      image, imgname = all_images[0]
      target = Path(target, filepath).parent.joinpath(imgname.lower() + ".png")
      return try_save_image(image, target)

    if len(all_images) > 1:
      img_target_dir = Path(target, filepath).parent.joinpath(path.name)

      for image, imgname in all_images:
        target = Path(img_target_dir, imgname.lower() + ".png")
        try_save_image(image, target)

      return img_target_dir

  except Exception as e:
    print(f"ERROR processing {filepath}: {e}")

  return None


def extract(client: Client) -> None:
  userconfig = config.load_user_config()
  client_directory = Path(userconfig.asset_directory, client.name)
  extract_directory = Path(userconfig.extract_directory, client.name)

  version_types = (
    VersionType.AZL,
    VersionType.PAINTING,
    VersionType.MANGA,
    VersionType.PIC,
    VersionType.CV,
    VersionType.BGM,
  )

  versioncontroller = versioncontrol.VersionController(client_directory)
  downloaded_files_collection: list[list[BundlePath]] = []
  painting_map = PaintingMap(client=client, userconfig=userconfig)
  prefab_list: set[str] = set()

  for vtype in version_types:
    vstring = versioncontroller.load_version_string(vtype)

    if not vstring:
      raise ValueError(f"{vtype} not found")

    vresult = SimpleVersionResult(version=vstring, version_type=vtype)
    downloaded_files = extractor.get_diff_files(versioncontroller, vresult)
    downloaded_files_collection.append(downloaded_files)

    if vtype != VersionType.PAINTING:
      continue

    for file in downloaded_files:
      if file not in painting_map.linker:
        continue

      prefab_list.update(painting_map.get_dependencies(file.inner).keys())

  def _filter(bundlepath: BundlePath) -> bool:
    if bundlepath.inner.split("/")[0] in cast(list[str], userconfig.extract_filter):
      return not userconfig.extract_isblacklist

    return userconfig.extract_isblacklist

  tasks_args: list[tuple[Path, str, Path, list[str]]] = []
  filtered_bundles = filter(_filter, set(itertools.chain(*downloaded_files_collection)))

  for bundlepath in filtered_bundles:
    dependencies: list[str] = []

    if bundlepath.inner.startswith("painting/"):
      painting_dependencies = painting_map.get_dependencies(bundlepath.inner)

      if bundlepath.inner in painting_dependencies:
        dependencies = list(painting_dependencies[bundlepath.inner])

    tasks_args.append(
      (
        Path(client_directory, "AssetBundles"),
        bundlepath.inner,
        extract_directory,
        dependencies,
      )
    )

  with multiprocessing.Pool(processes=max(1, multiprocessing.cpu_count() - 1)) as pool:
    pool.starmap(extract_assetbundle, tasks_args)

  print("Extract Assets Completed!")
  create_readme_version(client, client_directory, extract_directory)


def create_readme_version(client: Client, client_directory: Path, extract_directory: Path) -> None:
  vlist: list[str] = []

  for vtype in VersionType:
    version = Path(client_directory, vtype.version_filename).read_text(encoding="utf-8").strip()
    badge = f"https://img.shields.io/badge/{vtype.name}-{version}-blue?style=flat-square"
    value = f"![]({badge})"
    vlist.append(value)

  Path(extract_directory, "README.md").write_text(
    f"# AzurAssets/{client.name}\n{'\n'.join(vlist)}",
    encoding="utf-8",
  )
  print(f"Generated -> {Path(extract_directory, 'README.md')}")


if __name__ == "__main__":
  extract(Client.EN)
