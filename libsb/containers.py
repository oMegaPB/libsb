import datetime
import json
import typing as t
from dataclasses import dataclass
from functools import cached_property

from PIL import Image

from . import utils
from .enums import *
from .errors import *
from .loreToImage.writer import LoreWriter
from .typings import xJsonT

__all__ = [
    "Mayor",
    "ElectionResult",
    "NewsItem",
    "AuctionBid",
    "AuctionItem",
    "GemstoneSlot",
    "Gemstone",
    "PartialPlayer",
    "Enchantment",
    "Item",
    "CatacombsStats",
]

@dataclass
class Mayor:
    votes: int
    key: str
    name: str
    perks: t.List[xJsonT]
    
    def __repr__(self) -> str:
        return f"<Mayor name={self.name}, votes={self.votes}, key={self.key}>"
    
@dataclass
class ElectionResult:
    last_updated: datetime.datetime
    current: Mayor
    previous_elections: t.List[Mayor]
    next: t.List[Mayor]
    
    def __repr__(self) -> str:
        return f"<ElectionResult current={self.current.name}, lastUpdated={self.last_updated}>"
    
@dataclass
class NewsItem:
    item: t.Dict[str, str]
    link: str
    text: str
    title: str
    
    def __repr__(self) -> str:
        return f"<NewsItem link={self.link}, text={self.text}, item={self.item['material'].lower()}>"

@dataclass
class AuctionBid:
    auction_id: str
    bidder: "PartialPlayer"
    amount: int
    bid_at: datetime.datetime

    def __repr__(self) -> str:
        return f"<AuctionBid auction={self.auction_id}, amount={self.amount}, bidder={self.bidder}>"

@dataclass
class Item:
    name: str
    lore: str
    rarity: ItemRarity
    gemstone_slots: t.List["GemstoneSlot"]
    parsed_item_bytes: xJsonT
    type: ItemType

    @property
    def count(self) -> int:
        return self.parsed_item_bytes["Count"]

    @classmethod
    def empty(cls):
        return cls("", "", ItemRarity.Unknown, [], {}, ItemType.Unknown)
    
    def __repr__(self) -> str:
        if not self.name:
            return "<Item Empty>"
        return f"<Item {self.name} x{self.count}>"
        
    @cached_property
    def pet_level(self) -> int:
        if self.is_pet():
            return utils.get_pet_level(self.name)
        raise IsNotAPet()

    @property
    def lore_with_name(self) -> str:
        return self.parsed_item_bytes["tag"]["display"]["Name"] + "\n" + self.parsed_item_bytes["tag"]["display"]["Lore"]

    @cached_property
    def item_image(self) -> Image.Image:
        return LoreWriter(self.lore_with_name).get_image()
    
    @property
    def opened_gemstone_slots(self) -> int:
        return sum(not z.is_closed for z in self.gemstone_slots)

    def is_pet(self) -> bool:
        return bool(self.parsed_item_bytes["tag"]["ExtraAttributes"].get("petInfo", False))

    @cached_property
    def pet_exp(self) -> float | None:
        if self.is_pet():
            info = self.parsed_item_bytes["tag"]["ExtraAttributes"]["petInfo"]
            exp = json.loads(info)["exp"]
            return utils.CuteInt(round(exp, 3))
        raise IsNotAPet()

    @cached_property
    def enchantments(self) -> t.List["Enchantment"]:
        info = self.parsed_item_bytes["tag"]["ExtraAttributes"]["enchantments"]
        return [Enchantment(type=EnchantmentType.parse(k), tier=v) for k, v in info.items()]

    @property
    def id(self) -> str:
        return self.parsed_item_bytes["tag"]["ExtraAttributes"]["id"]

    @property
    def recombed(self) -> bool:
        return bool(self.parsed_item_bytes["tag"]["ExtraAttributes"].get("rarity_upgrades", False))

    @property
    def is_shiny(self) -> bool:
        return bool(self.parsed_item_bytes["tag"]["ExtraAttributes"].get("shiny", False))

    @property
    def is_dungeon_item(self) -> bool:
        return bool(self.parsed_item_bytes["tag"]["ExtraAttributes"].get("dungeon_item", False))
    
@dataclass
class AuctionItem(Item):
    uuid: str
    seller: "PartialPlayer"
    profile: str
    coop: t.List["PartialPlayer"]
    started: datetime.datetime
    expires_at: datetime.datetime
    starting_bid: int
    highest_bid: int
    bids: t.List[AuctionBid]
    expired: bool
    sold: bool
    is_bin: bool
    
    @property
    def is_alive(self) -> bool:
        return not self.sold and not self.expired
    
    def __repr__(self) -> str:
        return f"<AuctionItem name={self.name} price={self.starting_bid} alive={self.is_alive} rarity={self.rarity.name}>"

@dataclass
class Gemstone:
    quality: GemstoneQuality
    type: GemstoneType

    def __repr__(self) -> str:
        return f"<Gemstone {self.quality.name} {self.type.name}>"

@dataclass
class GemstoneSlot:
    gemstone: t.Optional[Gemstone]

    def __repr__(self) -> str:
        if self.gemstone is None:
            return f"<GemstoneSlot Empty>"
        elif self.is_closed:
            return f"<GemstoneSlot Closed>"
        return f"<GemstoneSlot {self.gemstone.quality.name} {self.gemstone.type.name}>"
    
    @classmethod
    def empty(cls):
        return cls(None)
    
    @property
    def is_closed(self) -> bool:
        return self.gemstone is not None \
            and self.gemstone.quality is GemstoneQuality.Unknown \
            and self.gemstone.type is GemstoneType.Unknown

@dataclass
class PartialPlayer:
    uuid: str # TODO: extract info

    def __repr__(self) -> str:
        return f"<PartialPlayer uuid={self.uuid}>"

@dataclass
class Enchantment:
    type: EnchantmentType
    tier: int

@dataclass
class CatacombsStats:
    name: str
    rank: str
    experience: float
    catacombs: t.Dict[str, t.Dict[str, float]]
    master_catacombs: t.Dict[str, t.Dict[str, float]]
    player_classes: t.Dict[str, t.Dict[str, float]]
    selected_dungeon_class: str
    secrets: int