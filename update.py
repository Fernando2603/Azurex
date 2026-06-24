import json
from pathlib import Path

import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Dependency(BaseModel):
  repository: str
  branch: str
  files: list[str]

  @property
  def links(self) -> list[str]:
    return [f"{self.repository}/{self.branch}/{file}" for file in self.files]


def update() -> None:
  dependency = Dependency.model_validate_json(Path("config/dependency.json").read_bytes())
  session = requests.Session()
  session.mount(
    "https://",
    HTTPAdapter(
      max_retries=Retry(
        total=10,  # pyright: ignore[reportCallIssue]
        backoff_factor=0.5,  # pyright: ignore[reportCallIssue]
        status_forcelist=[500, 502, 503, 504],  # pyright: ignore[reportCallIssue]
      ),
    ),
  )

  path = Path("dependency")
  path.mkdir(parents=True, exist_ok=True)

  for link in dependency.links:
    response = session.get(link)
    response.raise_for_status()

    name = link.rsplit("/", 1)[1]
    data = response.json()

    if "all" in data:
      del data["all"]

    data = {k: v for k, v in data.items() if v is not None}

    (path / name).write_text(
      json.dumps(data, indent=2, ensure_ascii=False),
      encoding="utf-8",
    )


if __name__ == "__main__":
  update()
