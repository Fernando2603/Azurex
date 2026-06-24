import hashlib
import re
from collections import defaultdict
from pathlib import Path
from typing import TypedDict, cast

import requests
from azlassets import config, versioncontrol
from azlassets.classes import Client, HashRow, UserConfig, VersionType
from pydantic import BaseModel, TypeAdapter
from requests.adapters import HTTPAdapter
from UnityPy import AssetsManager
from urllib3.util.retry import Retry

# exception is mostly asset that not available in EN
# but dev forgot to remove it in dependencies
ASSET_EXCEPTION = {
  "painting/jiuyuan_2_tex",
  "painting/sheer_tex",
  "painting/wululu_2_tex",
  "painting/wululu_tex",
  "painting/yueshen_tex",
  "painting/bonawendu_tex",
  "painting/salana_2_tex",
  "painting/maoyin_2_tex",
  "painting/lulutiye_tex",
  "painting/970206_tex",
  "painting/salana_tex",
  "painting/maoyin_tex",
  "painting/33_tex",
  "painting/mat",
  "painting/ui-painting_tex",
  "painting/unknown2_memory",
  "custom_builtin",
  # 2026-06-13
  "painting/andelieyam_pt_tex",
  "painting/970708_tex",
  "painting/mengmeng_pt_tex",
  "painting/970705_tex",
  "painting/970109_tex",
  "painting/970108_tex",
  "painting/970112_tex",
  "painting/970706_tex",
  "painting/970211_tex",
  "painting/970506_tex",
}

IGNORE_DEPENDENCIES = {"painting/mat_v1f1", "painting/mat", "custom_builtin"}


class MonoBehaviourValue(TypedDict):
  m_FileName: str
  m_Dependencies: list[str]


class MonoBehaviour(TypedDict):
  m_Keys: list[str]
  m_Values: list[MonoBehaviourValue]


class PaintingFilteMap(BaseModel):
  res_list: list[str]
  key: str


class OBBVersion(BaseModel):
  version: str
  files: list[str]


class OBBData(BaseModel):
  server: str
  version: str
  filemap: dict[str, HashRow]
  vtype: dict[str, OBBVersion]


HOST = "https://raw.githubusercontent.com"
OBB_URL = f"{HOST}/Fernando2603/AzurLaneOBB/main/EN.json"
PAINTING_RE = re.compile(r"^.*?\/painting\/")
PAINTING_FILTE_MAP_URL = f"{HOST}/Fernando2603/AzurLaneData/main/sharecfg/painting_filte_map.json"
PAINTING_FILTE_MAP_ADAPTER = TypeAdapter(dict[str, PaintingFilteMap])


class PaintingMap:
  def __init__(self, client: Client, userconfig: UserConfig) -> None:
    self.client = client
    self.userconfig = userconfig
    self.clientconfig = config.load_client_config(client=client)

    self.root = Path(userconfig.asset_directory, client.name)
    self.session = requests.Session()

    self.session.mount(
      "https://",
      HTTPAdapter(
        max_retries=Retry(
          total=10,  # pyright: ignore[reportCallIssue]
          backoff_factor=0.5,  # pyright: ignore[reportCallIssue]
          status_forcelist=[500, 502, 503, 504],  # pyright: ignore[reportCallIssue]
        ),
      ),
    )

    self.validated: set[str] = set()
    self.dependent: dict[str, dict[str, str]] = defaultdict(dict)
    self.linker: dict[str, set[str]] = defaultdict(set)
    self.size: dict[str, int] = {}
    self.obb: set[str] = set()

    self.parse_painting_filte_map()

  def __repr__(self) -> str:
    return f"<{self.__class__.__name__} {self.client.name}>"

  def fetch_painting_filte_map(self) -> dict[str, PaintingFilteMap]:
    response = self.session.get(PAINTING_FILTE_MAP_URL)
    response.raise_for_status()
    return PAINTING_FILTE_MAP_ADAPTER.validate_python(response.json())

  def fetch_obb_data(self) -> OBBData:
    response = self.session.get(OBB_URL)
    response.raise_for_status()
    return OBBData.model_validate(response.json())

  def parse_painting_filte_map(self) -> None:
    # ensure clearing when called multiple times
    self.validated.clear()
    self.dependent.clear()
    self.linker.clear()
    self.size.clear()
    self.obb.clear()

    bundle = Path(self.root, "AssetBundles/dependencies")

    if not bundle.exists():
      raise FileNotFoundError(bundle.as_posix())

    painting_filte_map = self.fetch_painting_filte_map()
    res_to_deps: dict[str, list[list[str]]] = defaultdict(list)

    for painting_filte in painting_filte_map.values():
      for res in painting_filte.res_list:
        res_to_deps[res].append(painting_filte.res_list)

    env = AssetsManager(bundle.as_posix())
    obj = next((obj for obj in env.objects if obj.type.name == "MonoBehaviour"), None)  # type: ignore

    if not obj:
      raise ValueError(f"MonoBehaviour not found in {bundle.as_posix()}")

    data = cast(MonoBehaviour, obj.parse_as_dict())
    keys = data["m_Keys"]
    values = {
      PAINTING_RE.sub("painting/", x["m_FileName"]): x["m_Dependencies"]
      for x in data["m_Values"]
      if "/painting/" in x["m_FileName"]
    }

    for name, dependencies in values.items():
      if not dependencies:
        continue

      # dependent must have a .prefab
      # _tex cant have 'prefab' which not an dependent
      # known misleading dependent as 2024-07-16
      # painting/unknown2_memory_tex
      # painting/qiye_dark_memory_tex
      # painting/mat_v1f1
      # painting/mat
      if name.endswith("_tex") or (name in IGNORE_DEPENDENCIES):
        continue

      self.dependent[name][name] = ""
      self.linker[name].add(name)

      for dependency in dependencies:
        if dependency not in keys:
          raise ValueError(f"dependencies m_Keys doesn't contain '{dependency}'")

        if dependency in ("shader", "custom_builtin") or dependency.startswith("artresource"):
          continue

        self.linker[dependency].add(name)
        self.dependent[name][dependency] = ""

    unlinked_names = set(values.keys()) - set(self.linker.keys()) - set(self.dependent.keys())

    for name in unlinked_names:
      if not name.endswith("_tex"):
        continue

      prefab_list: set[str] = set()

      if name in res_to_deps:
        for res_list in res_to_deps[name]:
          for dependency in res_list:
            if (dependency not in self.linker) or (dependency == "painting/touming_tex"):
              continue

            prefab_list.update(self.linker[dependency])

      else:
        if name not in ASSET_EXCEPTION:
          print(f"WARN: {name} doesn't match any dependencies in painting_filte_map.json")

        continue

      for prefab in prefab_list:
        self.dependent[prefab][name] = ""

      self.linker[name] = prefab_list

    version_controller = versioncontrol.VersionController(self.root)

    for vtype in (VersionType.AZL, VersionType.PAINTING):
      hashrows = version_controller.load_hash_file(vtype)

      if hashrows is None:
        raise ValueError("Failed to load Painting Hashrow")

      for hashrow in hashrows:
        if hashrow.filepath in self.linker:
          self.size[hashrow.filepath] = hashrow.size

          for link in self.linker[hashrow.filepath]:
            self.dependent[link][hashrow.filepath] = hashrow.md5hash

    obb_data = self.fetch_obb_data()
    self.obb = set(self.linker).intersection(obb_data.filemap)

  def check_dependency(self, filepath: str, filehash: str) -> bool:
    fullpath = Path(self.root, "AssetBundles", filepath)

    if not fullpath.exists():
      raise FileNotFoundError(fullpath.as_posix())

    return filehash == hashlib.md5(fullpath.read_bytes()).hexdigest()

  def get_dependencies(self, filepath: str, download: bool = True) -> dict[str, set[str]]:
    dependencies: dict[str, set[str]] = {}

    if filepath not in self.linker:
      if filepath not in ASSET_EXCEPTION:
        raise ValueError(f"{filepath} not found in linker. perhaps dependency outdated?")

      print(f"WARN: {filepath} is exception an in PaintingMap.")
      return dependencies

    for link in self.linker[filepath]:
      if link in dependencies:
        continue

      dependencies[link] = set()

      for dependency, md5hash in self.dependent[link].items():
        if dependency in self.validated:
          dependencies[link].add(dependency)
          continue

        try:
          if not self.check_dependency(filepath=dependency, filehash=md5hash):
            raise ValueError(f"{dependency} is outdated.")

        except (ValueError, FileNotFoundError) as error:
          if not download:
            raise error

          self.download_asset(HashRow(dependency, self.size[dependency], md5hash))

        self.validated.add(dependency)
        dependencies[link].add(dependency)

    self.dependencies = dependencies
    return dependencies

  def download_asset(self, hashrow: HashRow) -> None:
    print(f"{self.__class__.__name__}: Download {hashrow.filepath}")
    fullpath = Path(self.root, "AssetBundles", hashrow.filepath)

    if hashrow.filepath in self.obb:
      repository = "https://api.github.com/repos/Fernando2603/AzurLaneOBB/contents"
      response = self.session.get(
        url=f"{repository}/{self.client.name}/AssetBundles/{hashrow.filepath}",
        headers={"Accept": "application/vnd.github.v3.raw"},
      )

    else:
      response = self.session.get(
        url=f"{self.clientconfig.cdnurl}/android/resource/{hashrow.md5hash}"
      )

    response.raise_for_status()

    if len(response.content) != hashrow.size:
      raise ValueError(f"Received asset {hashrow.filepath} has wrong size.")

    if hashlib.md5(response.content).hexdigest() != hashrow.md5hash:
      raise ValueError(f"Received asset {hashrow.filepath} has wrong hash.")

    fullpath.parent.mkdir(parents=True, exist_ok=True)
    fullpath.write_bytes(cast(bytes, response.content))
