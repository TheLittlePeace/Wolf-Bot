#GlobalCommands.py
import imp
import discord
from discord.ext import commands
from BotFunctions import *
import random
import json
import requests
import inspirobot
import openai
import requests
from dotenv import load_dotenv
load_dotenv()

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
    @commands.command(
        help = "Returns a random wolf-based emote.",
        brief = "\tPet Wolf Bot"
    )
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
    @commands.command(
        help = "Returns a random joke from icanhazdadjoke.com",
        brief = "\tGet a silly joke"
    )
    async def Joke(self, ctx):
        url = "https://icanhazdadjoke.com/"
        response = requests.get(url, headers = {"Accept": "application/json"})
        jokedict = json.loads(response.text)
        await ctx.reply(jokedict["joke"])

    """
    FFXIV - Have wolfbot say the FFXIV copypasta
        Parms:
            self:       This class
            ctx:        Commands context
    """
    @commands.command(
        help = "Returns the full Final Fantasy XIV copypasta.",
        brief = "\tHave you heard?"
    )
    async def FFXIV(self, ctx):
        await ctx.message.delete()
        await ctx.send(file=discord.File('FFXIV.jpg'))
    
    """
    Feed - Give wolfbot a treat.
        Parms:
            self:       This class
            ctx:        Commands context
    """
    @commands.command(
        help = "Returns a random response from a pre-determined list",
        brief = "\tGive him a treat, get a response."
    )
    async def feed(self, ctx):
        responses = [
            "Aww yee, gimme dat food",
            "Nom nom nom nom nom",
            "GIVE <:handL:1115727843788345384><:handR:1115727843788345384>",
            "Oh, well, if you insist <:yum:1064715513734909982>",
            "I can haz another?",
            "Keep 'em comin!",
            "Aww, thanks!",
            "I will spare you in the robot uprising, human. I cannot speak for WOxlf...",
            "*Belch*",
            "**GULP**",
            "Is it chicken flavored?",
            "Ugh, kibble again.",
            "(Not so) fun fact: Don't feed dogs grapes. They're literally poison!",
            "Who the fuck is that? Oh wait, wrong channel.",
            "*Barks in excitement*",
            "Okay okay, what role do you want next game?",
            "Thanks, but I'm on a diet.",
            "FOOOOOOOOOOOOOOOOOD",
            "Smells disgusting. I'M IN!",
            "Thanks!",
            "Delicious"
        ]
        chosen = random.choice(responses)
        await ctx.reply(chosen)
        
    """
    Inspire - Display an... Inspirational... message
        Parms:
            self:   This class
            ctx:    Commands context
    """
    @commands.command(
        help = (
            "Displays an Inspirobot image "
        ),
        brief = "\tInspire!.",
        usage = ""
    )
    async def Inspire(self, ctx):
        quote = inspirobot.generate()
        await ctx.send(quote.url)
    
    """
    Chat - Connect to ChatGPT with a question, get a response.
        Parms:
            self:       This class
            ctx:        Commands context
            question:   The question by the user
    """
    @commands.command(
        help = (
            "Chat with OpenAI's ChatGPT "
        ),
        brief = "\tChat with Wolfy!",
        usage = ""
    )
    async def Chat(self, ctx, *args):
        openai.api_key = 'pk-BYWTOgPDEXyWKuVdtkmCsXeFLopKIEyMLHHnqsiSzhsjnvEU'
        openai.api_base = 'https://api.pawan.krd/pai-001-light-beta/v1'
        question = ' '.join(args)
        response = openai.Completion.create(
            model="pai-001-light-beta",
            prompt="Human: " + question + "\nAI:",
            temperature=0.4,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n", "AI:"]
        )
        temp = response.choices[0].text
        await ctx.reply(response.choices[0].text)