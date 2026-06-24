"""
Since github have push size limit about 2gb, split commit by chunk is required
this also solve the problem with os console character length on 'git add -- file'
"""

import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

from azlassets import config, versioncontrol
from azlassets.classes import Client, VersionType

from config import ROOT

MAX_COMMIT_SIZE = 1800 * 1024 * 1024  # 1800mb
MAX_ARG_SIZE = os.sysconf("SC_ARG_MAX") if hasattr(os, "sysconf") else 32767


def ls_files(repository: str) -> Iterator[str]:
  # git ls-files doesn't have streaming mode
  # this gonna take a while on large repository
  output = subprocess.check_output(
    [
      "git",
      "-C",
      repository,
      "ls-files",
      "-m",
      "-o",
      "-d",
      "--exclude-standard",
      "-z",
    ],
    stderr=subprocess.DEVNULL,
  )

  for entry in output.split(b"\0"):
    if entry:
      yield entry.decode()


def git_add(repository: str, files: list[str]) -> None:
  base_cmd = ["git", "-C", repository, "add", "--"]
  base_len = sum(len(s) + 1 for s in base_cmd)

  batch: list[str] = []
  batch_len = base_len
  batch_count = 0

  for file in files:
    if (batch_len + len(file) + 1) > MAX_ARG_SIZE:
      batch_count += 1

      print(f">   Adding batch {batch_count} ({len(batch)} files)...")
      subprocess.check_call([*base_cmd, *batch])

      batch = []
      batch_len = base_len

    batch.append(file)
    batch_len += len(file) + 1

  if batch:
    batch_count += 1

    if batch_count > 1:
      print(f">   Adding batch {batch_count} ({len(batch)} files)...")

    subprocess.check_call([*base_cmd, *batch])


def get_branch(repository: str) -> str:
  return (
    subprocess.check_output(
      ["git", "-C", repository, "branch", "--show-current"],
      stderr=subprocess.DEVNULL,
    )
    .decode()
    .strip()
  )


def get_unpushed_shas(repository: str) -> list[str]:
  branch = get_branch(repository)

  try:
    return (
      subprocess.check_output(
        ["git", "-C", repository, "log", f"origin/{branch}..HEAD", "--format=%H", "--reverse"],
        stderr=subprocess.DEVNULL,
      )
      .decode()
      .splitlines()
    )

  except subprocess.CalledProcessError:
    print("> No upstream found, assuming fresh repo...")
    return (
      subprocess.check_output(
        ["git", "-C", repository, "log", "--format=%H", "--reverse"],
        stderr=subprocess.DEVNULL,
      )
      .decode()
      .splitlines()
    )


def commit(repository: str = ".", message: str = "update") -> None:
  root = Path(ROOT, repository)
  print(f"> Repository: {root.as_posix()}")

  chunk_size = 0
  chunk_file: list[str] = []
  chunk_index = 0

  def flush_chunk(last: bool = False) -> None:
    nonlocal chunk_size, chunk_index

    if not chunk_file:
      return

    chunk_index += 1
    size_mb = chunk_size / 1024 / 1024

    if last and chunk_index == 1:
      print(f"> Committing {len(chunk_file)} files ({size_mb:.1f}mb)...")
    else:
      print(f"> Committing chunk {chunk_index} with {len(chunk_file)} files ({size_mb:.1f}mb)...")

    git_add(root.as_posix(), chunk_file)

    subprocess.check_call(
      [
        "git",
        "-C",
        root.as_posix(),
        "commit",
        "-m",
        message if last and chunk_index == 1 else f"{message} {chunk_index}",
      ]
    )

    chunk_file.clear()
    chunk_size = 0

  print("> Scanning working tree for changes...")

  for file in ls_files(root.as_posix()):
    path = Path(root, file)
    size = path.stat().st_size if path.exists() else 0

    if chunk_size + size >= MAX_COMMIT_SIZE:
      flush_chunk()

    chunk_size += size
    chunk_file.append(file)

  flush_chunk(last=True)

  if chunk_index == 0:
    print("> Working tree clean. Nothing to commit.\n")
    return

  branch = get_branch(root.as_posix())
  shas = get_unpushed_shas(root.as_posix())

  print(f"> Pushing {len(shas)} commit(s) to origin/{branch}...")

  for i, sha in enumerate(shas, start=1):
    print(f">   [{i}/{len(shas)}] {sha[:7]}...")
    subprocess.check_call(
      ["git", "-C", root.as_posix(), "push", "origin", f"{sha}:refs/heads/{branch}"]
    )

  print("> Done.\n")


def get_version(client: Client) -> str:
  userconfig = config.load_user_config()
  client_directory = Path(userconfig.asset_directory, client.name)
  versioncontroller = versioncontrol.VersionController(client_directory)

  return versioncontroller.load_version_string(VersionType.AZL) or "update"


if __name__ == "__main__":
  message = get_version(Client.EN)

  commit("AzurAssets", message)
  commit("AzurLane", message)
  commit(".", message)
