from subprocess import check_output


def ls_tree(repository: str, folder: str | None = None) -> dict[str, str]:
  args = [
    "git",
    "-C",
    repository,
    "-c",
    "core.quotepath=false",
    "ls-tree",
    "-r",
    "--format=%(path)<LS_TREE_SEPARATOR>%(objectname)",
    "HEAD",
  ]

  if folder is not None:
    args.append(folder)

  result = check_output(args, text=True)
  return dict(line.split("<LS_TREE_SEPARATOR>") for line in result.splitlines())
