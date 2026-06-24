import re

from .dependency import load_dependency

NAMECODE_RE = re.compile(r"\{namecode:(\d+)\}")
COLOR_TAG_RE = re.compile(r"<color[^>]*>")
MULTISPACE_RE = re.compile(r"\s{2,}")


# can optimized more into single regex, but harder to maintain
def resolve_namecode(text: str) -> str:
  name_code = load_dependency("name_code")

  line = NAMECODE_RE.sub(
    lambda m: name_code[x].name if (x := m.group(1)) in name_code else m.group(0),
    text,
  )
  line = line.replace(" ", " ")  # noqa: RUF001
  line = line.replace("</color>", "")

  line = COLOR_TAG_RE.sub("", line)
  line = MULTISPACE_RE.sub(" ", line)
  return line.strip()
