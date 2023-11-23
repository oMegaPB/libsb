import difflib
from enum import Enum

__all__ = [
    "GemstoneType",
    "GemstoneQuality",
    "ItemRarity",
    "ItemType",
    "EnchantmentType"
]

class GemstoneType(Enum):
    Jade = "a"
    Amber = "6"
    Topaz = "e"
    Sapphire = "b"
    Amethyst = "5"
    Jasper = "d"
    Ruby = "c"
    Opal = "f"
    Unknown = "-1"
    
    @classmethod
    def parse(cls, type: str) -> "GemstoneType":
        for x in cls:
            if type[0] == x.value:
                return x
        return cls.Unknown

class GemstoneQuality(Enum):
    Rough = "f"
    Flawed = "a"
    Fine = "9"
    Flawless = "5"
    Perfect = "6"
    Unknown = "-1"

    @classmethod
    def parse(cls, type: str) -> "GemstoneQuality":
        for x in cls:
            if type[0] == x.value:
                return x
        return cls.Unknown

class ItemRarity(Enum):
    Common = "COMMON"
    Uncommon = "UNCOMMON"
    Rare = "RARE"
    Epic = "EPIC"
    Legendary = "LEGENDARY"
    Mythic = "MYTHIC"
    Divine = "DIVINE"
    Special = "SPECIAL"
    VerySpecial = "VERY_SPECIAL"
    Unknown = "UNKNOWN"

    @classmethod
    def parse(cls, rarity: str) -> "ItemRarity":
        for x in cls:
            if rarity == x.value:
                return x
        return cls.Unknown

class ItemType(Enum):
    Helmet = "HELMET"
    Chestplate = "CHESTPLATE"
    Leggings = "LEGGINGS"
    Boots = "BOOTS"
    Item = "ITEM"
    Accessory = "ACCESSORY"
    Deployable = "DEPLOYABLE"
    Wand = "WAND"
    Gloves = "GLOVES"
    Necklace = "NECKLACE"
    Cloak = "CLOAK"
    Belt = "BELT"
    Bracelet = "BRACELET"
    Sword = "SWORD"
    Pickaxe = "PICKAXE"
    Longsword = "LONGSWORD"
    Bow = "BOW"
    Axe = "AXE"
    Hoe = "HOE"
    Shears = "SHEARS"
    FishingRod = "FISHING ROD"
    FishingWeapon = "FISHING WEAPON"
    Cosmetic = "COSMETIC"
    Drill = "DRILL"
    PetItem = "PET ITEM"
    HATCCESSORY = "HATCCESSORY"
    VACUUM = "VACUUM"
    MISC = None
    Unknown = "UNKNOWN"

    @classmethod
    def parse(cls, rarity: str) -> "ItemType":
        for x in cls:
            if rarity == x.value:
                return x
        return cls.Unknown

class EnchantmentType(Enum):
    BaneOfArthropods = 0x0
    Champion = 0x1
    Cleave = 0x2
    Critical = 0x3
    Cubism = 0x4
    DivineGift = 0x5
    DragonHunter = 0x6
    EnderSlayer = 0x7
    Execute = 0x8
    Experience = 0x9
    FireAspect = 0xa
    FirstStrike = 0xb
    GiantKiller = 0xc
    Impaling = 0xd
    Knockback = 0xe
    Lethality = 0xf
    LifeSteal = 0x10
    Looting = 0x11
    Luck = 0x12
    ManaSteal = 0x13
    Prosecute = 0x14
    Scavenger = 0x15
    Sharpness = 0x16
    Smite = 0x17
    Smoldering = 0x18
    Syphon = 0x19
    Tabasco = 0x1a
    Thunderbolt = 0x1b
    Thunderlord = 0x1c
    TitanKiller = 0x1d
    TripleStrike = 0x1e
    Vampirism = 0x1f
    Venomous = 0x20
    Vicious = 0x21
    Chance = 0x22
    DragonTracer = 0x23
    Flame = 0x24
    InfiniteQuiver = 0x25
    Piercing = 0x26
    Overload = 0x27
    Power = 0x28
    Punch = 0x29
    Snipe = 0x2a
    Hecatomb = 0x2b
    AquaAffinity = 0x2c
    BigBrain = 0x2d
    BlastProtection = 0x2e
    CounterStrike = 0x2f
    DepthStrider = 0x30
    FeatherFalling = 0x31
    FerociousMana = 0x32
    FireProtection = 0x33
    FrostWalker = 0x34
    GreatSpook = 0x35
    Growth = 0x36
    HardenedMana = 0x37
    ManaVampire = 0x38
    ProjectileProtection = 0x39
    Protection = 0x3a
    Reflection = 0x3b
    Rejuvenate = 0x3c
    Respiration = 0x3d
    StrongMana = 0x3e
    Respite = 0x3f
    Thorns = 0x40
    Transylvanian = 0x41
    TrueProtection = 0x42
    SmartyPants = 0x43
    SugarRush = 0x44
    Cayenne = 0x45
    GreenThumb = 0x46
    Prosperity = 0x47
    Quantum = 0x48
    Cultivating = 0x49
    Compact = 0x4a
    Dedication = 0x4b
    Delicate = 0x4c
    Efficiency = 0x4d
    Fortune = 0x4e
    Harvesting = 0x4f
    Pristine = 0x50
    Rainbow = 0x51
    Replenish = 0x52
    SilkTouch = 0x53
    SmeltingTouch = 0x54
    Sunder = 0x55
    TurboCacti = 0x56
    TurboCane = 0x57
    TurboCocoa = 0x58
    TurboCarrot = 0x59
    TurboMelon = 0x5a
    TurboMushrooms = 0x5b
    TurboPotato = 0x5c
    TurboPumpkin = 0x5d
    TurboWarts = 0x5e
    TurboWheat = 0x5f
    Angler = 0x60
    Blessing = 0x61
    Caster = 0x62
    Charm = 0x63
    Corruption = 0x64
    Expertise = 0x65
    Frail = 0x66
    LuckOfTheSea = 0x67
    Lure = 0x68
    Magnet = 0x69
    Piscary = 0x6a
    SpikedHook = 0x6b
    Bank = 0x6c
    BobbinTime = 0x6d
    Chimera = 0x6e
    Combo = 0x6f
    Duplex = 0x70
    Reiterate = Duplex
    FatalTempo = 0x71
    Flash = 0x72
    HabaneroTactics = 0x73
    Inferno = 0x74
    LastStand = 0x75
    Legion = 0x76
    NoPainNoGain = 0x77
    OneForAll = 0x78
    Rend = 0x79
    SoulEater = 0x7a
    Swarm = 0x7b
    TheOne = 0x7c
    UltimateJerry = 0x7d
    UltimateWise = 0x7e
    Wisdom = 0x7f
    Unknown = 0x80

    @classmethod
    def parse(cls, enchant: str) -> "EnchantmentType":
        enchants = {
            "luck_of_the_sea": cls.LuckOfTheSea,
            "ultimate_wise": cls.UltimateWise,
        }
        enchant = enchant.replace("ultimate_", "")
        if enchant in enchants.keys():
            return enchants[enchant]
        matches = difflib.get_close_matches(enchant, [x.name for x in cls])
        if matches:
            return getattr(cls, matches[0])
        return cls.Unknown