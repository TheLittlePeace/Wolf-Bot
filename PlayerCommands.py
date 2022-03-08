#PlayerCommands.py
import discord
from discord.ext import commands
from BotFunctions import *

#############################
# PLAYER-SPECIFIC COMMANDS
#############################
class Player_Commands(commands.Cog):

    """
    PhaseEnd - Get the time the phase will end.
        Parms:
            self:       The commands functionality
            ctx:        The bot functionality
            totimezone: The timezone to use for the time. Default UTC
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def PhaseEnd(self, ctx, totimezone="UTC"):
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
    PhaseLeft - Displays how much time is left in the phase.
        Parms:
            self:   The commands functionality
            ctx:    The bot functionality   
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def PhaseLeft(self, ctx):
        throwaway = await doPhaseLeft(ctx)
    #end PhaseLeft command

    """
    Time - display the current time in a specified timezone.
        Parms:
            self:       The commands functionality
            ctx:        The bot functionality
            totimezone: The timezone to display the time in. Default UTC
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def Time(self, ctx, totimezone="UTC"):
        totimezone = totimezone.upper()
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        newtime = doConvertTimezone(current_time, "EST", totimezone)
        message_info = await ctx.send("Current time: " + newtime + " " + 
            totimezone)
    #end Time command