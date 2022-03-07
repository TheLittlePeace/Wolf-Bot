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



@BOT.command()
async def PhaseEnd(ctx, totimezone="UTC"):
    totimezone = totimezone.upper()
    global PHASE_END_TIME
    global PHASE_END_TIMEZONE
    if PHASE_END_TIME == "":
        await ctx.send ("No phase set!")
        return
    newtime = doConvertTimezone(PHASE_END_TIME, PHASE_END_TIMEZONE, totimezone)
    splitdate = newtime.split(" ")
    message = "Phase will end on " + str(datetime.strptime(splitdate[0], 
        "%Y-%m-%d").strftime("%A, %B %d"))
    message += " at " + str(datetime.strptime(splitdate[1], 
        "%H:%M:%S").strftime("%I:%M %p"))
    message += " " + totimezone
    await ctx.send(message)
#end PhaseEnd command

@BOT.command()
async def PhaseLeft(ctx):
    throwaway = await doPhaseLeft(ctx)
#end PhaseLeft command

@BOT.command()
async def PhaseCountdown(ctx):
    global PHASE_END_TIME
    global PHASE_END_TIMEZONE
    message_info = await doPhaseLeft(ctx)
    if message_info["success"] == False:
        return
    message_id = message_info["messageinfo"].id
    channel = ctx.channel
    message = await channel.fetch_message(message_id)
    phaseendtime = datetime.strptime(doConvertTimezone(PHASE_END_TIME, 
        PHASE_END_TIMEZONE, "EST"), "%Y-%m-%d %H:%M:%S")

    while True:
        now = datetime.now()
        if now >= phaseendtime:
            await message.edit(content = "Time is up!")
            break
        timelist = doTimeDiff(phaseendtime, now)
        hours = timelist[0]
        minutes = timelist[1]
        seconds = timelist[2]
        await message.edit(content = "Time remaining: " + str(hours) + 
            " hours, " + str(minutes) + " minutes and " + str(seconds) + 
            " seconds")
        gc.collect
        sleep(.85)

@BOT.command()
async def Time(ctx, totimezone="UTC"):
    totimezone = totimezone.upper()
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    newtime = doConvertTimezone(current_time, "EST", totimezone)
    message_info = await ctx.send("Current time: " + newtime + " " + totimezone)
    # await ctx.send("Ignore this plz: " + str(message_info.id))
#end Time command

BOT.run(TOKEN)
