# bot.py

# External libs
import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Created files
from BotFunctions import *
from HostCommands import *
from PlayerCommands import *
from GlobalCommands import *
from Listeners import *
from Bot.bot import ChatBot
from Bot.ai import ChatAI
# from RunGame import *

load_dotenv()

#############################
# GLOBALS
#############################
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.presences = True
intents.members = True

#Main - run the bot
def main():
    global TOKEN
    BOT = commands.Bot(command_prefix = '!', case_insensitive = True,
        intents = intents)
    asyncio.run(load_cogs(BOT))
    BOT.run(TOKEN)
    
    client = ChatBot(1)
    client.set_response_chance(0.10)
    client.add_channel('canned-ham')
    client.run(TOKEN)

#Add all cogs
async def load_cogs(BOT):
    await BOT.add_cog(Host_Commands())
    await BOT.add_cog(Player_Commands())
    await BOT.add_cog(Global_Commands())
    await BOT.add_cog(ErrorHandler(BOT))
    await BOT.add_cog(voteRoomWatch(BOT))
    await BOT.add_cog(whoIsPat(BOT))

main()