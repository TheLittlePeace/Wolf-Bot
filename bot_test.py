# bot.py

# External libs
import gc
import os
from time import time, sleep
# import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
# import pytz
# import collections
# from dateutil import parser
import psycopg2

# Created files
from BotFunctions import *
from HostCommands import *
from ErrorHandler import *

load_dotenv()

#############################
# GLOBALS
#############################

TOKEN = os.getenv('DISCORD_TOKEN')
BOT = commands.Bot(command_prefix='tst-', case_insensitive=True)
PGPW = os.getenv('POSTGRESQL_PASSWORD')
PGCONN = psycopg2.connect(
    host = "localhost",
    database = "TWG",
    user = "postgres",
    password = PGPW
)



#Add all cogs
BOT.add_cog(Host_Commands())
BOT.add_cog(ErrorHandler(BOT))





BOT.run(TOKEN)
