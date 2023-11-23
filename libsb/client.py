import asyncio
import collections
import datetime
import json
import typing as t
from io import BytesIO

import bs4
from curl_cffi.requests.models import Response

from . import utils
from .base import ClientBase
from .containers import *
from .enums import *
from .errors import *
from .typings import xJsonT

__all__ = [
    "ApiClient",
]

class ApiClient(ClientBase):

    async def api_request(self, path: str, method: str = "GET", **kwargs) -> Response:
        url = f"{self.base}{path}"
        ns = "".join([f"?{x}={y}" for x, y in kwargs.items() if y is not None])
        request = await self.session.request(method, url + ns)
        if request.status_code == 403:
            resp = request.json()
            raise InvalidApiKey(code=request.status_code, description=resp["cause"])
        return request
        
    async def fetch_elections(self) -> ElectionResult:
        data = (await self.api_request("/resources/skyblock/election")).json()
        last_updated = utils.get_date(data["lastUpdated"])
        candidates = data["mayor"]["election"]["candidates"]
        mayor_info = [x for x in candidates if x["name"] == data["mayor"]["name"]][0]
        votes, key, name, perks = mayor_info["votes"], mayor_info["key"], mayor_info["name"], mayor_info["perks"]
        current = Mayor(votes=votes, key=key, name=name, perks=utils.normalize_perks(perks))
        previous = sorted([Mayor(votes=x["votes"], key=x["key"], name=x["name"], perks=utils.normalize_perks(x["perks"])) for x in candidates[1:]], key=lambda x: x.votes)
        if data.get("current") is not None:
            next = sorted([Mayor(votes=x["votes"], key=x["key"], name=x["name"], perks=utils.normalize_perks(x["perks"])) for x in data["current"]["candidates"]], key=lambda x: x.votes)
        else:
            next = []
        return ElectionResult(last_updated=last_updated, next=next, previous_elections=previous, current=current)
    
    async def fetch_all_items(self, path: str = "items.json") -> bool:
        data = (await self.api_request("/resources/skyblock/items")).json()
        json.dump(data, open(path, "w"), indent=4)
        return True

    async def fetch_bazaar(self, path: str = "bazaar.json") -> bool:
        data = (await self.api_request("/skyblock/bazaar")).json()
        json.dump(data, open(path, "w"), indent=4)
        return True
    
    async def fetch_news(self) -> t.List[NewsItem]:
        data = (await self.api_request(f"/skyblock/news")).json()
        items = [NewsItem(item=x["item"], link=x["link"], text=x["text"], title=x["title"]) for x in data["items"]]
        return items
    
    def _dict_to_item(self, x: xJsonT) -> Item:
        if not x and isinstance(x, dict):
            return Item.empty()
        lore = x["tag"]["display"]["Lore"]
        idata = utils.parse_item_data(lore)
        return Item(
            name=utils.clear_text(x["tag"]["display"]["Name"]),
            lore=utils.clear_text(lore),
            rarity=ItemRarity.parse(idata["rarity"]),
            type=ItemType.parse(idata["type"]),
            gemstone_slots=self.parse_gemstones(lore),
            parsed_item_bytes=x
        )

    def _dict_to_auction(self, x: xJsonT) -> AuctionItem:
        item_bytes = x["item_bytes"]
        if isinstance(item_bytes, dict):
            item_bytes = item_bytes["data"]
        is_bin = x.get("bin", False)
        parsed_item_bytes = utils.parse_item_bytes(item_bytes)["i"][0]
        display = parsed_item_bytes["tag"]["display"]
        lore = x["item_lore"] if "item_lore" in x.keys() else display["Lore"]
        data = utils.parse_item_data(lore)
        return AuctionItem(
            uuid=x["uuid"] if "uuid" in x.keys() else x["auction_id"], 
            seller=PartialPlayer(uuid=x["auctioneer"]) if "auctioneer" in x.keys() else PartialPlayer(uuid=x["seller"]), 
            profile=x["profile_id"] if "profile_id" in x.keys() else x["seller_profile"], 
            coop=[PartialPlayer(uuid=z) for z in x["coop"]] if "coop" in x.keys() else [],
            started=utils.get_date(x["start"]) if "start" in x.keys() else datetime.datetime.fromtimestamp(0),
            expires_at=utils.get_date(x["end"]) if "end" in x.keys() else utils.get_date(x["timestamp"]),
            rarity=ItemRarity.parse(data["rarity"]),
            starting_bid=utils.CuteInt(x["starting_bid"]) if "starting_bid" in x.keys() else utils.CuteInt(x["price"]),
            parsed_item_bytes=parsed_item_bytes,
            lore=lore,
            name=x["item_name"] if "item_name" in x.keys() else display["Name"],
            highest_bid=utils.CuteInt(x["highest_bid_amount"]) if "highest_bid_amount" in x.keys() else utils.CuteInt(x["price"]),
            bids=[
                AuctionBid(bidder=PartialPlayer(uuid=z["bidder"]), auction_id=z["auction_id"], amount=utils.CuteInt(z["amount"]), bid_at=utils.get_date(z["timestamp"]))
                for z in x["bids"]
            ] if "bids" in data.keys() else [],
            is_bin=is_bin,
            gemstone_slots=self.parse_gemstones(lore),
            expired=int(datetime.datetime.now().timestamp()) > int(str(x["end"])[:-3]) if "end" in x.keys() else True,
            sold=((is_bin and not not x["bids"]) or (not is_bin and int(datetime.datetime.now().timestamp()) > int(str(x["end"])[:-3]))) if "end" in x.keys() else True,
            type=ItemType.parse(data["type"])
        ) 
    
    async def fetch_auctions(self, name: str, profile: t.Optional[str] = None) -> t.List[AuctionItem]:
        player = await self.name_to_uuid(name)
        data = (await self.api_request("/skyblock/auction", player=player, profile=profile)).json()
        return [self._dict_to_auction(x) for x in data["auctions"] if not x["claimed"]]
    
    async def cata_stats(self, ign: str, profile: t.Optional[str] = None) -> tuple[str, str, xJsonT]:
        uuid = await self.name_to_uuid(ign)
        profiles, player = await asyncio.gather(
            self.api_request("/skyblock/profiles", uuid=uuid, profile=profile), 
            self.api_request("/player", uuid=uuid)
        )
        data, playerdata, ret = profiles.json(), player.json(), {}
        secrets = playerdata["player"]["achievements"]["skyblock_treasure_hunter"]
        for x in data["profiles"]:
            if x["selected"]:
                dungeons = x["members"][uuid]["dungeons"]["dungeon_types"]
                ret["experience"] = dungeons["catacombs"]["experience"]
                for y in ["catacombs", "master_catacombs"]:
                    for z in ["tier_completions", "fastest_time_s_plus"]:
                        ret.setdefault(y, {})[z] = dungeons[y][z]
                ret["player_classes"] = x["members"][uuid]["dungeons"]["player_classes"]
                ret["selected_dungeon_class"] = x["members"][uuid]["dungeons"]["selected_dungeon_class"]
                return utils.get_rank(playerdata), playerdata["player"]["displayname"], {**ret, "secrets": secrets}
        raise UnknownError()

    async def name_to_uuid(self, name: str) -> str:
        if name in self._uuid_cache.values():
            return [key for key in self._uuid_cache.items() if key[1] == name][0][0]
        r = await self.session.request("GET", f"https://mcuuid.net/?q={name}") # TODO api.mojang.com
        soup = bs4.BeautifulSoup(r.text, "lxml")
        tag = soup.find("input", {"id": "results_raw_id"})
        if tag is not None:
            uuid = getattr(tag, "attrs")["value"]
            self._uuid_cache[uuid] = name
            return uuid
        raise HTTPError(500, "Tag not found")
    
    async def uuid_to_name(self, uuid: str) -> str:
        if uuid in self._uuid_cache.keys():
            return self._uuid_cache[uuid]
        resp = await self.session.request("GET", f"https://mcuuid.net/?q={uuid}") # TODO api.mojang.com
        try:
            soup = bs4.BeautifulSoup(resp.text, "lxml")
            name = soup.find_all("input")[1].attrs.get("value")
            self._uuid_cache[uuid] = name
            return name
        except (Exception, KeyError, IndexError) as e:
            print(e.__class__, e)
            print(resp.text)
            raise RuntimeError(self.uuid_to_name.__name__) from e
    
    async def render_skin(self, uuid: str) -> BytesIO:
        response = await self.session.request("GET", f"https://crafatar.com/renders/body/{uuid}?overlay=true")
        if response.status_code == 200:
            _io = BytesIO(response.content)
            return [_io.seek(0), _io][1]
        else:
            raise HTTPError(response.status_code)

    def parse_gemstones(self, lore: str) -> t.List[GemstoneSlot]:
        result: t.List[str] = utils.GEMSTONE_PATTERN.findall(lore)
        if result is not None:
            groups = [x.split("§") for x in result]
            slots = sum(x[2][:-1] != "8" for x in groups)
            if slots:
                gemstones = [
                    GemstoneSlot(Gemstone(GemstoneQuality.parse(x[1]), GemstoneType.parse(x[2]))) 
                    if x[2][0] != "7" else GemstoneSlot.empty() 
                    for x in groups
                ]
                return gemstones
        return []
    
    async def fetch_all_auctions(self, fetch_all: bool = True) -> t.List[AuctionItem]:
        resp = await self.api_request("/skyblock/auctions", page=0)
        page_0 = resp.json()
        auctions = [self._dict_to_auction(x) for x in page_0["auctions"]]
        if fetch_all:
            tasks = []
            async def task(page: int):
                resp = await self.api_request("/skyblock/auctions", page=page)
                if resp.ok:
                    return [self._dict_to_auction(x) for x in resp.json()["auctions"]]
                return []
            for z in range(1, page_0["totalPages"] + 1):
                tasks.append(task(z))
            result = await asyncio.gather(*tasks)
            return sum(result, []) + auctions
        return auctions

    def lowestbin_sort(self, name: str, auctions: t.List[AuctionItem]) -> t.List[AuctionItem]:
        pred: t.Callable[[AuctionItem], bool] = lambda auction: name.lower() in auction.name.lower() and auction.is_alive and auction.is_bin
        items = sorted(filter(pred , auctions), key=lambda x: x.starting_bid)
        return items
    
    async def auction_from_uuid(self, uuid: str) -> AuctionItem | None:
        resp = await self.api_request("/skyblock/auction", uuid=uuid)
        data = resp.json()
        if resp.ok and data["auctions"]:
            return self._dict_to_auction(data["auctions"][0])
    
    async def ended_auctions(self) -> t.List[AuctionItem]:
        resp = await self.api_request("/skyblock/auctions_ended")
        data = resp.json()["auctions"]
        return [self._dict_to_auction(item) for item in data]
    
    async def fetch_inventory(self, name: str, profile: t.Optional[str] = None) -> t.List[t.List[Item]]:
        uuid = await self.name_to_uuid(name)
        request = await self.api_request("/skyblock/profiles", uuid=uuid, profile=profile)
        data = request.json()
        items: t.List[Item] = []
        for x in data["profiles"]:
            if x["selected"]:
                for x in utils.parse_item_bytes(x["members"][uuid]["inventory"]["inv_contents"]["data"])["i"]:
                    items.append(self._dict_to_item(x))
        deq = collections.deque(utils.as_chunks(items, 9))
        deq.rotate(-1)
        return [*deq]