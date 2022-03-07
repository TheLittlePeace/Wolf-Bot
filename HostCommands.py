# HostCommands.py
import discord
from discord.ext import commands
from datetime import datetime
from dateutil import parser
from time import sleep
import gc
from BotFunctions import *

#############################
# HOST-SPECIFIC COMMANDS
#############################
class Host_Commands(commands.Cog):
    
    """
    SetPhaseEnd - Set the ending of the current phase.
        Parms:
            self - The commands functionality
            ctx - The bot functionality
            intime - The time to be entered. Fuzzy matches.
            intimezone - Timezone for the aformentioned time.
        Outputs:
            Confirmation that the time was set correctly, or an error.
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def SetPhaseEnd(self, ctx, intime, intimezone):
        global PHASE_END_TIME
        global PHASE_END_TIMEZONE
        intime = parser.parse(intime, fuzzy=True)
        intimezone = intimezone.upper()
        PHASE_END_TIME = str(intime)
        PHASE_END_TIMEZONE = intimezone
        splitdate = PHASE_END_TIME.split(" ")
        message = "Phase end set to " + str(datetime.strptime(splitdate[0],
            "%Y-%m-%d").strftime("%A, %B %d"))
        message += " at " + str(datetime.strptime(splitdate[1], 
            "%H:%M:%S").strftime("%I:%M %p"))
        message += " " + PHASE_END_TIMEZONE
        await ctx.send(message)
    #end SetPhaseEnd command

    """
    Kill - Swap the roles of a player from living to dead.
        Parms:
            self - The commands functionality
            ctx - The bot functionality
            inuser - The player to "kill"
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def Kill(self, ctx, inuser: discord.Member):
        await inuser.add_roles("Dead")
        await inuser.remove_roles("Living")
    #end Kill command

    """
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
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