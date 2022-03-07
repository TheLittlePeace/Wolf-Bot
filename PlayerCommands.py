#PlayerCommands.py
import discord
from discord.ext import commands
from BotFunctions import *

#############################
# PLAYER-SPECIFIC COMMANDS
#############################
class Host_Commands(commands.Cog):

    """
    
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def PhaseEnd(ctx, totimezone="UTC"):
        totimezone = totimezone.upper()
        global PHASE_END_TIME
        global PHASE_END_TIMEZONE
        if PHASE_END_TIME == "":
            await ctx.send ("No phase set!")
            return
        newtime = doConvertTimezone(PHASE_END_TIME, PHASE_END_TIMEZONE, 
            totimezone)
        splitdate = newtime.split(" ")
        message = "Phase will end on " + str(datetime.strptime(splitdate[0], 
            "%Y-%m-%d").strftime("%A, %B %d"))
        message += " at " + str(datetime.strptime(splitdate[1], 
            "%H:%M:%S").strftime("%I:%M %p"))
        message += " " + totimezone
        await ctx.send(message)
    #end PhaseEnd command

    """
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def PhaseLeft(ctx):
        throwaway = await doPhaseLeft(ctx)
    #end PhaseLeft command

    """
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def Time(ctx, totimezone="UTC"):
        totimezone = totimezone.upper()
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        newtime = doConvertTimezone(current_time, "EST", totimezone)
        message_info = await ctx.send("Current time: " + newtime + " " + 
            totimezone)
    #end Time command