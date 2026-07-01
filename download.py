import subprocess
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


def download(client: Client):
  subprocess.run(["azl", "download", "EN"])

  userconfig = config.load_user_config()
  clientconfig = config.load_client_config(client)
  client_directory = Path(userconfig.asset_directory, client.name)
  versioncontroller = versioncontrol.VersionController(client_directory)

  for vtype, version in get_version(clientconfig).items():
    versioncontroller.save_version_string(vtype, version)

if __name__ == '__main__':
  download(Client.EN)