import base64
import datetime
import io
import re
import typing as t
from dataclasses import dataclass
import nbt.nbt as nbt

T = t.TypeVar("T")

from .enums import *
from .errors import *
from .typings import *

GEMSTONE_PATTERN = re.compile(r"§[a-z0-9]+\[§[a-z0-9]+.§[a-z0-9]\]+")
COLOR_PATTERN = re.compile(r"§[0-9A-fklmnorKLMNOR]")
ITEM_TYPE_PATTERN = re.compile(r"(?P<is_recombed>a )?(?P<is_shiny>SHINY )?(?P<rarity>\S+)?(?P<is_dungeon> DUNGEON)?(?P<type>.+[^ a-])?")
PET_LEVEL_REGEX = re.compile(r"\[Lvl (\d+)\] .+")

CATACOMBS_LEVELS = {x: y + 1 for x, y in enumerate([50, 125, 235, 395, 625, 955, 1425, 2095, 3045, 4385, 6275, 8940, 12700, 17960, 25340, 35640, 50040, 70040, 97640, 135640, 188140, 259640, 356640, 488640, 668640, 911640, 1239640, 1684640, 2284640, 3084640, 4149640, 5559640, 7459640, 9959640, 13259640, 17559640, 23159640, 30359640, 39559640, 51559640, 66559640, 85559640, 109559640, 139559640, 177559640, 225559640, 285559640, 360559640, 453559640, 569809640])}

PET_LEVELS = {
    "COMMON": [100, 210, 330, 460, 605, 765, 940, 1130, 1340, 1570, 1820, 2095, 2395, 2725, 3085, 3485, 3925, 4415, 4955, 5555, 6215, 6945, 7745, 8625, 9585, 10635, 11785, 13045, 14425, 15935, 17585, 19385, 21345, 23475, 25785, 28285, 30985, 33905, 37065, 40485, 44185, 48185, 52535, 57285, 62485, 68185, 74485, 81485, 89285, 97985, 107685, 118485, 130485, 143785, 158485, 174685, 192485, 211985, 233285, 256485, 281685, 309085, 338885, 371285, 406485, 444685, 486085, 530885, 579285, 631485, 687685, 748085, 812885, 882285, 956485, 1035685, 1120385, 1211085, 1308285, 1412485, 1524185, 1643885, 1772085, 1909285, 2055985, 2212685, 2380385, 2560085, 2752785, 2959485, 3181185, 3418885, 3673585, 3946285, 4237985, 4549685, 4883385, 5241085, 5624785, 6036485],
    "UNCOMMON": [765, 940, 1130, 1340, 1570, 1820, 2095, 2395, 2725, 3085, 3485, 3925, 4415, 4955, 5555, 6215, 6945, 7745, 8625, 9585, 10635, 11785, 13045, 14425, 15935, 17585, 19385, 21345, 23475, 25785, 28285, 30985, 33905, 37065, 40485, 44185, 48185, 52535, 57285, 62485, 68185, 74485, 81485, 89285, 97985, 107685, 118485, 130485, 143785, 158485, 174685, 192485, 211985, 233285, 256485, 281685, 309085, 338885, 371285, 406485, 444685, 486085, 530885, 579285, 631485, 687685, 748085, 812885, 882285, 956485, 1035685, 1120385, 1211085, 1308285, 1412485, 1524185, 1643885, 1772085, 1909285, 2055985, 2212685, 2380385, 2560085, 2752785, 2959485, 3181185, 3418885, 3673585, 3946285, 4237985, 4549685, 4883385, 5241085, 5624785, 6036485, 6478185, 6954885, 7471585, 8033285, 8644985],
    "RARE": [1820, 2095, 2395, 2725, 3085, 3485, 3925, 4415, 4955, 5555, 6215, 6945, 7745, 8625, 9585, 10635, 11785, 13045, 14425, 15935, 17585, 19385, 21345, 23475, 25785, 28285, 30985, 33905, 37065, 40485, 44185, 48185, 52535, 57285, 62485, 68185, 74485, 81485, 89285, 97985, 107685, 118485, 130485, 143785, 158485, 174685, 192485, 211985, 233285, 256485, 281685, 309085, 338885, 371285, 406485, 444685, 486085, 530885, 579285, 631485, 687685, 748085, 812885, 882285, 956485, 1035685, 1120385, 1211085, 1308285, 1412485, 1524185, 1643885, 1772085, 1909285, 2055985, 2212685, 2380385, 2560085, 2752785, 2959485, 3181185, 3418885, 3673585, 3946285, 4237985, 4549685, 4883385, 5241085, 5624785, 6036485, 6478185, 6954885, 7471585, 8033285, 8644985, 9311685, 10038385, 10830085, 11691785, 12628485],
    "EPIC": [3485, 3925, 4415, 4955, 5555, 6215, 6945, 7745, 8625, 9585, 10635, 11785, 13045, 14425, 15935, 17585, 19385, 21345, 23475, 25785, 28285, 30985, 33905, 37065, 40485, 44185, 48185, 52535, 57285, 62485, 68185, 74485, 81485, 89285, 97985, 107685, 118485, 130485, 143785, 158485, 174685, 192485, 211985, 233285, 256485, 281685, 309085, 338885, 371285, 406485, 444685, 486085, 530885, 579285, 631485, 687685, 748085, 812885, 882285, 956485, 1035685, 1120385, 1211085, 1308285, 1412485, 1524185, 1643885, 1772085, 1909285, 2055985, 2212685, 2380385, 2560085, 2752785, 2959485, 3181185, 3418885, 3673585, 3946285, 4237985, 4549685, 4883385, 5241085, 5624785, 6036485, 6478185, 6954885, 7471585, 8033285, 8644985, 9311685, 10038385, 10830085, 11691785, 12628485, 13645185, 14746885, 15938585, 17225285, 18611985],
    "LEGENDARY": [5555, 6215, 6945, 7745, 8625, 9585, 10635, 11785, 13045, 14425, 15935, 17585, 19385, 21345, 23475, 25785, 28285, 30985, 33905, 37065, 40485, 44185, 48185, 52535, 57285, 62485, 68185, 74485, 81485, 89285, 97985, 107685, 118485, 130485, 143785, 158485, 174685, 192485, 211985, 233285, 256485, 281685, 309085, 338885, 371285, 406485, 444685, 486085, 530885, 579285, 631485, 687685, 748085, 812885, 882285, 956485, 1035685, 1120385, 1211085, 1308285, 1412485, 1524185, 1643885, 1772085, 1909285, 2055985, 2212685, 2380385, 2380385, 2380385, 2380385, 2380385, 3418885, 3673585, 3946285, 4237985, 4549685, 4883385, 5241085, 5624785, 6036485, 6478185, 6954885, 7471585, 8033285, 8644985, 9311685, 10038385, 10830085, 11691785, 12628485, 13645185, 14746885, 15938585, 17225285, 18611985, 20108685, 21725385, 23472085, 25358785]
}
class CuteInt(int):
    def __repr__(self) -> str:
        return f"{self:,}"
    
    __str__ = __repr__

def parse_item_bytes(raw: str) -> xJsonT:
    def parse_tag(tag: t.Any) -> t.Any:
        if isinstance(tag, nbt.TAG_List):
            return [parse_tag(i) for i in tag.tags]
        elif isinstance(tag, nbt.TAG_Compound):
            return {[s:=parse_tag(i), i.name][1]: "\n".join(s) if i.name.lower() == "lore" else parse_item_bytes(base64.b64encode(s).decode()) if isinstance(s, bytearray) else s for i in tag.tags}
        else:
            return tag.value
    tag = nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw)))
    return parse_tag(tag)

def normalize_perks(perks: t.List[xJsonT]) -> t.List[xJsonT]:
    return [{"name": x["name"], "description": clear_text(x["description"])} for x in perks]

def clear_text(text: str) -> str:
    return COLOR_PATTERN.sub("", text)
            
def get_date(ts: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(int(str(ts)[:10]))

@dataclass
class CatacombsLevelInfo:
    exp_from_new_level: float
    exp_needed_for_new_level: float
    percent_to_new_level: float
    current_exp: float
    current_level: int

def get_catacombs_level(exp: float) -> CatacombsLevelInfo:
    if exp < 51:
        return CatacombsLevelInfo(exp, 50, exp*2, exp, 0)
    data = [*enumerate(map(lambda x: (x[1] > exp, x[1]), [*CATACOMBS_LEVELS.items()]))]
    for x in data:
        if x[1][0]:
            needed = data[x[0]][1][1]-data[x[0]-1][1][1]
            new_exp = exp-data[x[0]-1][1][1]
            return CatacombsLevelInfo(round(new_exp, 1), needed, round((new_exp) / needed, 2), round(exp, 1), x[0])
    level = 50
    total_exp = exp
    exp -= 569_809_640.0
    while True:
        if exp - 200_000_000 >= 0:
            exp -= 200_000_000
            level += 1
        else:
            break
    return CatacombsLevelInfo(exp, 200_000_000, round(exp/200_000_000*100, 2), total_exp, level)

def parse_item_data(lore: str) -> xJsonT:
    data = clear_text(lore.splitlines()[-1])
    match = ITEM_TYPE_PATTERN.search(data)
    if match is not None:
        result = match.groupdict()
        for key in result.keys():
            if key.startswith("is_"):
                result[key] = bool(result[key])
            else:
                if result[key] is not None:
                    result[key] = result[key].strip()
        return result
    raise InvalidArgument()

def get_pet_level(name: str) -> int:
    ret = PET_LEVEL_REGEX.search(name)
    if ret is not None:
        return int(ret.groups()[0])
    return -1

class cached_property:
    def __init__(self, func) -> None:
        self.func: t.Callable[[t.Any], t.Any] = func
        self.value = None
    
    def __get__(self, instance: t.Any, type: t.Type[t.Any]) -> t.Any:
        if not hasattr(instance, f"__{self.func.__name__}"):
            setattr(instance, f"__{self.func.__name__}", self.func(instance))
        return getattr(instance, f"__{self.func.__name__}")

def get_rank(data: xJsonT) -> str:
    if 'monthlyPackageRank' in data['player'] and data['player']['monthlyPackageRank'] != 'NONE':
        rank = 'MVP++'
    elif 'newPackageRank' in data['player']:
        rank = data['player']['newPackageRank']
    elif 'packageRank' in data['player']:
        rank = data['player']['packageRank']
    else:
        rank = ''
    prefix = None
    try:
        prefix = data['player']['prefix'].replace('§', '&')
        if prefix == '&c[OWNER]':
            rank = 'OWNER'
        elif prefix == '&d[PIG&b+++&d]':
            rank = 'PIG+++'
    except KeyError:
        rank = rank.replace('_', '').replace('PLUS', '+')
    try:
        rank = data['player']['rank']
        if rank == 'GAME_MASTER':
            rank = 'GM'
    except KeyError:
        pass
    if rank != '':
        rank = '[' + rank + ']'
    return rank

def as_chunks(iterable: t.List[T], n: int) -> t.List[t.List[T]]:
    return [iterable[x:x+n] for x in range(0, len(iterable), n)]


