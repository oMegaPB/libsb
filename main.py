import asyncio
import datetime
import os
import sys
import typing as t

import libsb.utils as utils
from libsb import ApiClient, AuctionItem, ItemRarity

APIKEY = os.environ['HAPIKEY']

async def gemstone_slots(): # items with opened gemstone slots
    async with ApiClient(APIKEY) as client:
        items = [x for x in await client.fetch_all_auctions() if "Witherborn" in x.lore and not "Wither" in x.name and x.is_alive and x.is_bin and x.gemstone_slots]
        items.sort(key=lambda x: x.starting_bid)
        for x in items[:25]:
            print(x.name, x.starting_bid, x.rarity, x.uuid, x.opened_gemstone_slots)
        while True:
            try:
                num = input(">>> ")
                if num == "q":
                    exit()
                items[int(num)].item_image.show()
            except Exception as e:
                print(e.__class__, e)

async def pets_above_lvl_100(): # pets that can be ugraded and flipped
    KAT_FLOWER_PRICE = 575_000

    names = {
        "baby yeti": 14_000_000 + KAT_FLOWER_PRICE * 12,
        "blue whale": 11_200_000 + KAT_FLOWER_PRICE * 12,
        "jellyfish": 15_000_000 + KAT_FLOWER_PRICE * 10,
        "tiger": 15_700_000 + KAT_FLOWER_PRICE * 12,
        "griffin": 30_000_000,
        "lion": 15_000_000 + KAT_FLOWER_PRICE * 12,
        "ocelot": 1_250_000 + KAT_FLOWER_PRICE * 5,
        "enderman": 40_000_000 + KAT_FLOWER_PRICE * 12,
        "blaze": 40_000_000 + KAT_FLOWER_PRICE * 12
    }
    async with ApiClient(APIKEY) as client:
        items: t.List[AuctionItem] = []
        leg_lvl100: t.List[AuctionItem] = []
        for item in await client.fetch_all_auctions():
            if item.rarity is ItemRarity.Mythic:
                continue
            if any(z in item.name.lower() for z in names.keys()) and "[Lvl 100]" in item.name and item.is_alive and item.is_bin:
                if item.pet_exp and item.pet_exp > 2.545 * 10**7:
                    if item.rarity is not ItemRarity.Legendary:
                        items.append(item)
                    else:
                        leg_lvl100.append(item)
        items.sort(key=lambda x: x.starting_bid)
        print("================================================")
        for k, v in names.items():
            cheapest = client.lowestbin_sort(k, leg_lvl100)
            if cheapest:
                price = cheapest[0].starting_bid
            else:
                print(f"Cheapest LEG [Lvl 100] {k} NOT FOUND:", f"upgrade: {utils.CuteInt(v)}.")
                continue
            print(f"Cheapest LEG [Lvl 100] {k} is:", price, f"upgrade: {utils.CuteInt(v)}. min price: {utils.CuteInt(price - v)}")
        print("===================================================================")
        for x in items[:25]:
            print(x, x.uuid, x.pet_exp)
        while True:
            try:
                num = input(">>> ")
                if num == "q":
                    exit()
                items[int(num)].item_image.show()
            except Exception as e:
                print(e.__class__, e)

async def rat_prices(): # ive invested in rat skins so
    async with ApiClient(APIKEY) as client:
        profit = 0
        auctions = await client.fetch_all_auctions()
        rats = {
            "PiRate Rat Skin": [1, 37_500_000],
            "Junk Rat Rat Skin": [2, 30_000_000],
            "SecuRaty Guard Rat Skin": [1, 46_400_000],
            "SecRat Service Rat Skin": [1, 68_890_000],
            "KaRate Rat Skin": [1, 64_599_999],
            "Mr Claws Rat Skin": [1, 31_000_000],
            "Squeakheart Rat Skin": [3, 29_200_200],
            "Gym Rat Rat Skin": [2, 39_900_000]
        }
        for name, v in rats.items():
            amount, price = v
            lowest_rat = client.lowestbin_sort(name, auctions)
            if not lowest_rat:
                print(f"No skins found: {name}. prob alot price? (bought for {utils.CuteInt(price)} x{amount})")
            else:
                cur_profit = (lowest_rat[0].starting_bid - price) * amount
                print(f"lb price: {lowest_rat[0].starting_bid}. bought: {utils.CuteInt(price)} x{amount}. {name} PROFIT: {utils.CuteInt(cur_profit)}")
                profit += cur_profit
        print(f"Total Profit: {utils.CuteInt(profit)}")
                

async def cata_stats(): # catacombs check for user
    name = sys.argv[1]
    async with ApiClient(APIKEY) as client:
        ret = "=============================================\n"
        stats = await client.cata_stats(name)
        info = utils.get_catacombs_level(stats.experience)
        total_runs = sum(sum(getattr(stats, x, {}).get("tier_completions", {}).values()) for x in ["catacombs", "master_catacombs"])
        ret += f"{stats.rank} {stats.name} ||cata {info.current_level}|| {info.percent_to_new_level}% to {info.current_level+1}\n"
        ret += "Selected Class: " + stats.selected_dungeon_class.capitalize() + "\n"
        for k, v in stats.player_classes.items():
            level = utils.get_catacombs_level(v['experience']).current_level
            ret += f"{k} {level} | "
        ret = ret [:-2] + "\n"
        ret += f"Secrets Found: {utils.CuteInt(stats.secrets)} ({round(stats.secrets / total_runs, 2)} per run)\n\nFastest Time: S+\n"
        for x in ["catacombs", "master_catacombs"]:
            for y in map(str, range(5, 8)):
                minutes, seconds = divmod(datetime.timedelta(microseconds=getattr(stats, x, {}).get("fastest_time_s_plus", {}).get(y, 0) * 1000).seconds, 60)
                seconds = "%.2d" % seconds
                ret += f"{x.capitalize()} floor {y}: {minutes}:{seconds}\n"
            ret += "\n"
        ret = ret[:-1] + "============================================="
        print(ret)

if __name__ == "__main__":
    with asyncio.Runner() as runner:
        runner.run(cata_stats())