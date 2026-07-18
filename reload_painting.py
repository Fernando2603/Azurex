import asyncio
import multiprocessing
from pathlib import Path
from typing import cast

from azlassets import config, downloader
from azlassets.classes import BundlePath, Client, HashRow
from azlassets.versioncontrol import parse_hash_rows
from azurpaint import Azurpaint
from azurpaint.exception import PrefabNotFound
from PIL import Image

from utility.painting_map import PaintingMap

downloader_semaphore = asyncio.Semaphore(30)

# hardcoded path, im lazy asf
async def download_one(
  host: downloader.AzurlaneAsyncDownloader,
  dst: Path,
  hashrow: HashRow,
) -> bool:
  assetpath = Path(dst, hashrow.filepath)
  async with downloader_semaphore:
    return await host.download_asset(hashrow.md5hash, assetpath, hashrow.size)


async def download():
  path = Path("./ClientAssets/EN/hashes-painting.csv")
  dst = Path("./ClientAssets/EN/AssetBundles")

  async with downloader.AzurlaneAsyncDownloader(
    cdn_url="https://blhxusstatic.yo-star.com",
    useragent="",
  ) as host:
    hashrows = parse_hash_rows(path.read_text(encoding="utf-8"))
    await asyncio.gather(*(download_one(host, dst, h) for h in hashrows))


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
    try:
      azurpaint = Azurpaint(path=root, prefab=filepath)
    except PrefabNotFound:
      return None

    if len(dependencies):
      azurpaint.load(dependencies)

    painting = azurpaint.create(trim=True, downscale=True)
    target = Path(target, filepath).with_suffix(".png")

    return try_save_image(painting, target)

  except Exception as e:
    print(f"ERROR processing {filepath}: {e}")

  return None


def extract(client: Client) -> None:
  userconfig = config.load_user_config()
  client_directory = Path(userconfig.asset_directory, client.name)
  extract_directory = Path(userconfig.extract_directory, client.name)

  painting_map = PaintingMap(client=client, userconfig=userconfig)
  prefab_list: set[str] = set()

  downloaded_files: list[BundlePath] = [
    BundlePath(Path(f"ClientAssets/EN/AssetBundles/painting/{path.name}"), f"painting/{path.name}")
    for path in Path("ClientAssets/EN/AssetBundles/painting").glob("*")
  ]

  for file in downloaded_files:
    if file not in painting_map.linker:
      continue

    prefab_list.update(painting_map.get_dependencies(file.inner).keys())

  def _filter(bundlepath: BundlePath) -> bool:
    if bundlepath.inner.split("/")[0] in cast(list[str], userconfig.extract_filter):
      return not userconfig.extract_isblacklist

    return userconfig.extract_isblacklist

  tasks_args: list[tuple[Path, str, Path, list[str]]] = []
  filtered_bundles = filter(_filter, set(downloaded_files))

  for bundlepath in filtered_bundles:
    try:
      dependencies: list[str] = []
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
    except Exception:
      pass

  with multiprocessing.Pool(processes=max(1, multiprocessing.cpu_count() - 1)) as pool:
    pool.starmap(extract_assetbundle, tasks_args)

  print("Extract Assets Completed!")


if __name__ == "__main__":
  asyncio.run(download())
  extract(Client.EN)
