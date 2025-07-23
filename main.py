import logging
from datetime import datetime

import discord
import requests
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import tasks

from config import Config, ConfigKeys

config = Config()
logger = logging.getLogger("hedonistflavorsnotifier.main")
logging.basicConfig(level=logging.INFO)
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    hedonist_flavors.start()


@bot.slash_command(
    name="register",
    description="Register a channel for notifications",
    guild_ids=["596141925766004739"]
)
async def register(ctx: discord.ApplicationContext):
    channels = config.get(ConfigKeys.REGISTERED_CHANNELS)
    if ctx.interaction.channel_id in channels:
        await ctx.interaction.respond("This channel is already registered!")
    else:
        channels.append(ctx.interaction.channel_id)
        config.set(ConfigKeys.REGISTERED_CHANNELS, channels)
        await ctx.interaction.respond("Registered this channel for Hedonist Flavor Updates!")


@bot.slash_command(
    name="deregister",
    description="Deregister a channel for notifications",
    guild_ids=["596141925766004739"]
)
async def deregister(ctx: discord.ApplicationContext):
    channels = config.get(ConfigKeys.REGISTERED_CHANNELS)
    if not ctx.interaction.channel_id in channels:
        await ctx.interaction.respond("This channel is not registered!")
    else:
        channels.remove(ctx.interaction.channel_id)
        config.set(ConfigKeys.REGISTERED_CHANNELS, channels)
        await ctx.interaction.respond("Deregistered this channel for Hedonist Flavor Updates!")

@tasks.loop(seconds=15)
async def hedonist_flavors():
    logger.info("Checking Hedonist Flavors")
    req = requests.get("https://hedonistchocolates.com/shop/available-ice-cream-flavors")
    bs = BeautifulSoup(req.text, "html.parser")
    strong_tags = bs.find_all("strong")
    flavors = []
    current_flavor = ""
    for strong_tag in strong_tags:
        if strong_tag.text.startswith("-"):
            if current_flavor != "":
                flavors.append(current_flavor)
            current_flavor = strong_tag.text
        else:
            if current_flavor:
                current_flavor += strong_tag.text
    if flavors != config.get(ConfigKeys.LAST_FLAVORS):
        channels = config.get(ConfigKeys.REGISTERED_CHANNELS)
        logger.info(f"Flavors have updated, notifying {len(channels)} channels!")
        config.set(ConfigKeys.LAST_FLAVORS, flavors)
        embed = Embed(
            title="Hedonist Ice Cream Flavors",
            url="https://hedonistchocolates.com/shop/available-ice-cream-flavors",
            description=f"**Flavors have been updated!**\n{"\n".join(flavors)}",
            timestamp=datetime.now()
        )
        for channel in channels:
            await bot.get_channel(channel).send(embed=embed)
    else:
        logger.info("Flavors are the same")

bot.run(config.get(ConfigKeys.DISCORD_BOT_TOKEN))