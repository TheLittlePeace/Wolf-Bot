#PlayerCommands.py
import imp
import discord
from discord.ext import commands
from BotFunctions import *
import collections
import inspirobot

#############################
# PLAYER-SPECIFIC COMMANDS
#############################
class Player_Commands(commands.Cog):

    """
    PhaseEnd - Get the time the phase will end.
        Parms:
            self:       This class
            ctx:        Commands context
            totimezone: The timezone to use for the time. Default UTC
    """
    @commands.command(
        help = (
            "Returns the time that the current phase will end.\n"
            "You can specify the timezone you want returned, like EST, UTC, "
            "PST, etc. Defaults to UTC if not specified."
        ),
        brief = "\tGet current phase end",
        usage = "[ToTimezone]"
    )
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def PhaseEnd(self, ctx, totimezone="UTC"):
        totimezone = totimezone.upper()
        phaseendtime = getGlobalData("PHASE_END_TIME")
        if(phaseendtime == None):
            await customError("Phase End Not Found!")
            return
        phaseendtzone = getGlobalData("PHASE_END_TZONE")
        if(phaseendtzone == None):
            await customError("Phase End Not Found!")
            return
        if phaseendtime == "":
            await ctx.send ("No phase set!")
            return
        newtime = doConvertTimezone(phaseendtime, phaseendtzone, 
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
            self:   This class
            ctx:    Commands context
    """
    @commands.command(
        help = (
            "Displays how much time is left in the current phase."
        ),
        brief = "\tHow long until phase end",
        usage = ""
    )
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def PhaseLeft(self, ctx):
        throwaway = await doPhaseLeft(ctx)
    #end PhaseLeft command

    """
    Time - display the current time in a specified timezone.
        Parms:
            self:       This class
            ctx:        Commands context
            totimezone: The timezone to display the time in. Default UTC
    """
    @commands.command(
        help = (
            "Displays the current time in a specified timezone.\n"
            "Can specify a timezone such as EST, UTC, PST, etc. Defaults to "
            "UTC."
        ),
        brief = "\tCurrent time for a timezone",
        usage = "[ToTimezone]"
    )
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def Time(self, ctx, totimezone="UTC"):
        totimezone = totimezone.upper()
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        newtime = doConvertTimezone(current_time, "EPT", totimezone)
        message_info = await ctx.send("Current time: " + newtime + " " + 
            totimezone)
    #end Time command

    """
    Votes - Display the current vote phase's tally
        Parms:
            self:   This class
            ctx:    Commands context
    """
    @commands.command(
        help = (
            "Displays the current vote standings. Orders them by the most "
            "votes to the least."
        ),
        brief = "\tCurrent vote standings.",
        usage = ""
    )
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def Votes(self, ctx):
        global PGCONN
        cur = PGCONN.cursor()
        vote_id = getGlobalData('CURRENT_VOTE_ID')
        ret_dict = {}
        response = "__Current Vote Standing:__\n"
        living_players = await getLiving(ctx)
        for memb in living_players:
            sql = "SELECT COUNT(*) FROM playervotes WHERE lower(vote) = %s AND id = %s"
            cur.execute(sql, (memb.name.lower(), str(vote_id)))
            votes = cur.fetchone()
            # response += "**" + memb.name + "**: " + str(votes[0]) + "\n"
            ret_dict[memb.display_name] = votes[0]
        sorted_x = sorted(ret_dict.items(), key = lambda kv: kv[1], 
            reverse = True)
        sorted_dict = collections.OrderedDict(sorted_x)
        for key in sorted_dict:
            response += "**" + key + "**: " + str(sorted_dict[key]) + "\n"
        await ctx.send(response)
        cur.close()
        
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
    @commands.has_any_role("The Werewolf Council", "Host", "Living", "Dead")
    async def Inspire(self, ctx):
        quote = inspirobot.generate()
        await ctx.send(quote.url)




        