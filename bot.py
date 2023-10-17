# bot.py

# External libs
import os
from discord.ext import commands
from dotenv import load_dotenv

# Created files
from BotFunctions import *
from HostCommands import *
from PlayerCommands import *
from GlobalCommands import *
from Listeners import *
# from RunGame import *

load_dotenv()

#############################
# GLOBALS
#############################
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.presences = True
intents.members = True
BOT = commands.Bot(command_prefix = '$', case_insensitive = True,
    intents = intents)

#Add all cogs
BOT.add_cog(Host_Commands())
BOT.add_cog(Player_Commands())
BOT.add_cog(Global_Commands())
# BOT.add_cog(Bot_Run_Game())
BOT.add_cog(ErrorHandler(BOT))
BOT.add_cog(voteRoomWatch(BOT))
BOT.add_cog(whoIsPat(BOT))

#Run the bot
BOT.run(TOKEN)
