from pydantic import BaseModel, TypeAdapter


class Skin(BaseModel):
  id: int
  gid: int
  name: str
  type: str
  desc: str
  tag: list[str | int]
  illustrator: int
  illustrator2: int
  voice_actor: int
  voice_actor2: int
  bgm: str | None
  background: str | None
  background2: str | None
  painting: str | None
  painting_n: str | None
  banner: str | None
  chibi: str | None
  icon: str | None
  qicon: str | None
  shipyard: str | None


class SharedSkin(Skin):
  shared: str


class ShipSkin(BaseModel):
  gid: int
  name: str
  skins: dict[str, Skin | SharedSkin]

  def as_list(self) -> "ShipSkinList":
    return ShipSkinList.model_construct(
      gid=self.gid,
      name=self.name,
      skins=list(self.skins.values()),
    )


class ShipSkinList(BaseModel):
  gid: int
  name: str
  skins: list[Skin | SharedSkin]

  def as_dict(self) -> ShipSkin:
    return ShipSkin.model_construct(
      gid=self.gid,
      name=self.name,
      skins={str(v.id): v for v in self.skins},
    )


SkinAdapter = TypeAdapter(dict[str, Skin])
SkinListAdapter = TypeAdapter(list[Skin])

ShipSkinAdapter = TypeAdapter(dict[str, ShipSkin])
ShipSkinListAdapter = TypeAdapter(list[ShipSkinList])
