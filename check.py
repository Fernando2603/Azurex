from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from azlassets import config, protobuf, versioncontrol
from azlassets.classes import Client, VersionType


def get_version(clientconfig: config.ClientConfig) -> dict[VersionType, str]:
  response = protobuf.get_version_response(  # type: ignore
    clientconfig.gateip, clientconfig.gateport
  )

  if response is None:
    raise ValueError("failed to get version response")

  result: dict[VersionType, str] = {}

  for version in response.pb.version:
    if version.startswith("$"):
      value = versioncontrol.parse_version_string(version)
      result[value.version_type] = value.version

  return result


def check(client: Client):
  userconfig = config.load_user_config()
  clientconfig = config.load_client_config(client)
  client_directory = Path(userconfig.asset_directory, client.name)
  versioncontroller = versioncontrol.VersionController(client_directory)

  with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
    version = get_version(clientconfig)

  should_update: bool = False

  version_types = (
    VersionType.AZL,
    VersionType.PAINTING,
    VersionType.MANGA,
    VersionType.PIC,
    VersionType.CV,
    VersionType.BGM,
  )

  for vtype in version_types:
    old = versioncontroller.load_version_string(vtype)
    new = version[vtype]

    if versioncontrol.compare_version_string(new, old):
      should_update = True
      break

  print(version[VersionType.AZL], should_update)


if __name__ == "__main__":
  check(Client.EN)
