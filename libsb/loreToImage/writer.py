from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

COLORS = {
    "0": "#000000",
    "1": "#0000AA",
    "2": "#00AA00",
    "3": "#00AAAA",
    "4": "#AA0000",
    "5": "#AA00AA",
    "6": "#FFAA00",
    "7": "#AAAAAA",
    "8": "#555555",
    "9": "#5555FF",
    "a": "#55FF55",
    "b": "#55FFFF",
    "c": "#FF5555",
    "d": "#FF55FF",
    "e": "#FFFF55",
    "f": "#FFFFFF",
}
class LoreWriter:
    def __init__(self, lore: str) -> None:
        self.path = Path(__file__).parent
        self.x = 15
        self.y = 10
        self.width = 590
        self.lines = lore.split("\n")
        self.height = (25 * len(self.lines)) + 15
        self.initialize_fonts()
        self.image = None
    
    def draw_text(self, *args, **kwargs) -> None:
        self.draw.text(*args, **kwargs)
    
    def get_image(self) -> Image.Image:
        if self.image is None:
            bold = False
            image = Image.new("RGBA", (self.width, self.height), color="black")
            self.draw = ImageDraw.Draw(image, "RGBA")
            for x in self.lines:
                for y in x.split("§")[1:]:
                    if y[0] == "l":
                        bold = True
                    if y[0] in COLORS.keys():
                        color = ImageColor.getcolor(COLORS[y[0]], "RGBA")
                    for z in y[1:]:
                        if z.isascii():
                            if not bold:
                                self.draw_text(xy=(self.x, self.y), text=z, font=self.ascii_regular, fill=color) # type: ignore
                            else:
                                self.draw_text(xy=(self.x-5, self.y), text=z, font=self.bold, fill=color) # type: ignore
                            if z in ["i", "l", ",", ".", ":", "[", "]", " ", "'"]:
                                self.x += 7
                            elif z in "tI":
                                self.x += 9
                            else:
                                self.x += 14
                        else:
                            self.draw_text(xy=(self.x, self.y), text=z, font=self.uni_regular, fill=color) # type: ignore
                            self.x += 16
                    self.x += 3
                    bold = False
                self.y += 24
                self.x = 15
            self.image = image
        return self.image
    
    def initialize_fonts(self) -> None:
        size, encoding = 22, ""
        self.ascii_regular = ImageFont.truetype(self.path.joinpath("fonts", "regular.otf").open("rb"), size=size, encoding=encoding)
        self.uni_regular = ImageFont.truetype(self.path.joinpath("fonts", "minecraft-unicode.otf").open("rb"), size=16, encoding=encoding)
        self.bold = ImageFont.truetype(self.path.joinpath("fonts", "bold.otf").open("rb"), size=size, encoding=encoding)
        self.italic = ImageFont.truetype(self.path.joinpath("fonts", "italic.otf").open("rb"), size=size, encoding=encoding)
        self.bolditalic = ImageFont.truetype(self.path.joinpath("fonts", "bolditalic.otf").open("rb"), size=size, encoding=encoding)

if __name__ == "__main__":
    lore = u"""
§8✿ §d§dAncient Necron's Boots §6✪§6✪§6✪§6✪§6✪§c➎
§7Gear Score: §d737 §8(1088)
§7Strength: §c+79 §9(+35) §8(+120)
§7Crit Chance: §c+15% §9(+15%) §8(+22.5%)
§7Crit Damage: §c+33% §8(+48%)
§7Health: §a+226.5 §e(+60) §9(+7) §8(+339.2)
§7Defense: §a+155.5 §e(+30) §9(+7) §8(+235.2)
§7Intelligence: §a+36 §9(+25) §8(+56)
 §8[§7❁§8] §8[§7⚔§8]

§7§lLegion V§9, §9Depth Strider III§9, §9Feather Falling X
§7Ferocious Mana VII§9, §7Growth VI§9, §9Protection VI
§7Rejuvenate V§9, §7Sugar Rush III

§7§cYou do not have a high enough
§cEnchanting level to use some of
§cthe enchantments on this item!

§d◆ §cR§6a§ei§an§bb§9o§dw§9 Rune III

§7Reduces the damage you take from
§7withers by §c10%§7.

§6Full Set Bonus: Witherborn §7(0/4)
§7Spawns a wither minion every
§7§e30 §7seconds up to a maximum
§7§a1 §7wither. Your withers will
§7travel to and explode on nearby
§7enemies.

§9Ancient Bonus
§7Grants §a+1 §9☠ Crit Damage
§9§7per §cCatacombs §7level.

§8✿ Pure Black Dyed
§7§4❣ §cRequires §aThe Catacombs Floor
§aVII Completion§c.
§d§l§ka§r §d§l§d§lMYTHIC DUNGEON BOOTS §d§l§ka"""
    writer = LoreWriter(lore)
    writer.get_image().show()