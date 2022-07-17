#GlobalCommands.py
import imp
import discord
from discord.ext import commands
from BotFunctions import *
import random
import json
import requests

# jokesfile = open('jokes.json')
# jokes = json.load(jokesfile)

#############################
# GLOBAL COMMANDS
#############################

class Global_Commands(commands.Cog):
    """
    Pet - Respond with a wolf emote.
        Parms:
            self:       This class
            ctx:        Commands context
    """
    @commands.command()
    async def Pet(self, ctx):
        emotes = [
            "<:crywolf:953307093404880906>",
            "<:monkaWolf:916916031203733514>",
            "<:wolfWIN:918603892604932096>",
            "<:wolf_angel:916916138330439691>",
            "<:wolf_cheer:916917019104907325>",
            "<:wolf_joy:916917069428166696>",
            "<:wolf_pthbthhhhh:916917102831616030>",
            "<:wolf_sip:916921667786276874>",
            "<:wolf_wink:916921798031990835>",
            "<:wolf_write:917528996114223115>",
            "<:wolfy_love:917254133105426432>"
        ]
        chosen = random.choice(emotes)
        await ctx.reply(chosen)
    
    """
    Joke - Respond with a random joke.
        Parms:
            self:       This class
            ctx:        Commands context
    """
    @commands.command()
    async def Joke(self, ctx):
        url = "https://icanhazdadjoke.com/"
        response = requests.get(url, headers = {"Accept": "application/json"})
        jokedict = json.loads(response.text)
        await ctx.reply(jokedict["joke"])
