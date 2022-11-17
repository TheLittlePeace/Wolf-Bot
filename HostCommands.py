# HostCommands.py
import discord
from discord.ext import commands
from datetime import datetime
from dateutil import parser
from time import sleep
import gc
from BotFunctions import *
from Listeners import *

#############################
# HOST-SPECIFIC COMMANDS
#############################
class Host_Commands(commands.Cog):
    
    """
    SetPhaseEnd - Set the ending of the current phase.
        Parms:
            self:       The commands functionality
            ctx:        The bot functionality
            intime:     The time to be entered. Fuzzy matches.
            intimezone: Timezone for the aformentioned time.
        Output:
            Confirmation that the time was set correctly, or an error.
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def SetPhaseEnd(self, ctx, intime, intimezone):
        intime = parser.parse(intime, fuzzy=True)
        intimezone = intimezone.upper()
        end_time = str(intime)
        end_timezone = intimezone
        success = setGlobalData("Phase_End_Time", end_time)
        if(success == False):
            await customError(ctx, "Failed to connect to Database [WRITE/" +
                "UPDATE Phase_End_Time]")
        success = setGlobalData("Phase_End_TZone", end_timezone)
        if(success == False):
            await customError(ctx, "Failed to connect to Database [WRITE/" +
                "UPDATE Phase_End_TZone")
        splitdate = end_time.split(" ")
        message = "Phase end set to " + str(datetime.strptime(splitdate[0],
            "%Y-%m-%d").strftime("%A, %B %d"))
        message += " at " + str(datetime.strptime(splitdate[1], 
            "%H:%M:%S").strftime("%I:%M %p"))
        message += " " + end_timezone
        await ctx.send(message)
    #end SetPhaseEnd command

    """
    PhaseCountdown - Displays how much time is left in the phase, and then 
                     edits it every ~second
        Parms:
            self:   The commands functionality
            ctx:    The bot functionality
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def PhaseCountdown(self, ctx):
        phaseendtime = getGlobalData("PHASE_END_TIME")
        if(phaseendtime == None):
            await customError(ctx, "Phase End Not Found!")
            return
        phaseendtzone = getGlobalData("PHASE_END_TZONE")
        if(phaseendtzone == None):
            await customError(ctx, "Phase End Not Found!")
            return
        message_info = await doPhaseLeft(ctx)
        if message_info["success"] == False:
            return
        message_id = message_info["messageinfo"].id
        channel = ctx.channel
        message = await channel.fetch_message(message_id)
        phaseendtime = datetime.strptime(doConvertTimezone(phaseendtime, 
            phaseendtzone, "EPT"), "%Y-%m-%d %H:%M:%S")

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

    """
    Kill - Swap the roles of a player from living to dead.
        Parms:
            self:   The commands functionality
            ctx:    The bot functionality
            args:   The player(s) to "kill"
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def Kill(self, ctx: commands.Context, *args):
        for name in args:
            result = await removeRole(ctx, name, "Living")
            if(result != True):
                await customError(ctx, result)
            result = await giveRole(ctx, name, "Dead")
            if(result != True):
                await customError(ctx, result)
            await ctx.send(name + " has been killed.")
    #end Kill command

    """
    Livify - Swap the roles of a player from dead to living.
        Parms:
            self:   The commands functionality
            ctx:    The bot functionality
            args:   The player(s) to "revive"
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def Livify(self, ctx: commands.Context, *args):
        for name in args:
            result = await removeRole(ctx, name, "Dead")
            if(result != True):
                await customError(ctx, result)
            result = await giveRole(ctx, name, "Living")
            if(result != True):
                await customError(ctx, result)
            await ctx.send(name + " is alive.")
    #end Livify command

    """
    handleSpectators - give all non-living, dead, or host players the Spectator
                        role.
        Parms:
            self:   The commands functionality
            ctx:    The bot functionality
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def handleSpectators(self, ctx: commands.Context):
        livingrole = get(ctx.guild.roles, name = 'Living')
        deadrole = get(ctx.guild.roles, name = 'Dead')
        hostrole = get(ctx.guild.roles, name = 'Host')
        members = ctx.guild.members
        for member in members:
            if(livingrole in member.roles or
                    deadrole in member.roles or
                    hostrole in member.roles or
                    member.bot == True):
                continue
            result = await giveRole(ctx, member.name, 'Spectator')
            await ctx.send(member.name + " made a Spectator.")
    #end handleSpectators

    """
    removeGameRoles - remove all game-related roles.
        Parms:
            self:   The commands functionality
            ctx:    The bot functionality
            args:   The players to apply it to. Can specify ALL.
                    WARNING: This can remove the Host role.
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def removeGameRoles(self, ctx: commands.Context, *args):
        if(args[0] == 'ALL'):
            membs = ctx.guild.members
            loopvar = list()
            for m in membs:
                loopvar.append(m.name)
            loopvar = tuple(loopvar)
        else:
            loopvar = args
        for name in loopvar:
            result = await removeRole(ctx, name, "Dead")
            if(result != True):
                await customError(ctx, result)
            result = await removeRole(ctx, name, "Living")
            if(result != True):
                await customError(ctx, result)
            result = await removeRole(ctx, name, "Host")
            if(result != True):
                await customError(ctx, result)
            result = await removeRole(ctx, name, "Spectator")
            if(result != True):
                await customError(ctx, result)
                
    """
    setVoting - turn voting on or off
        Parms:
            self:   The commands functionality
            ctx:    The bot context
            onoff:  Whether to turn voting on or off. Accepts only ON and OFF
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def setVoting(self, ctx: commands.Context, onoff: str):
        if(onoff.lower() != 'on' and onoff.lower() != 'off'):
            await customError(ctx, "This command only accepts 'On' or 'Off'")
            return
        setGlobalData('VOTING', onoff.upper())
        channel = discord.utils.get(ctx.guild.channels, name='voting-room')
        if(onoff.lower() == 'on'):
            vote_id = getGlobalData('CURRENT_VOTE_ID')
            vote_id = int(vote_id)
            vote_id += 1
            setGlobalData('CURRENT_VOTE_ID', str(vote_id))
            await channel.send("----------START VOTE----------")
        else:
            await channel.send("-----------END VOTE-----------")
    #end setVoting

    """
    Say - Just say a message in a specified channel.
        Parms:
            self:       The commands functionality
            ctx:        The bot context
            channel:    The channel to send it to
            message:    The message to send
    """
    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def Say(self, ctx: commands.Context, 
        channel: str, message: str):
        endChannel = discord.utils.get(ctx.guild.channels, name=channel)
        if(endChannel == None):
            await customError(ctx, "Channel not found.")
            return
        await endChannel.send(message)
    #end Say

    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def addPlayer(self, ctx: commands.Context, username: str, userid: int):
        success = setUser(username, userid)
        if(success == False):
            customError(ctx, "Failed adding user!")
    #end addPlayer

    @commands.command()
    @commands.has_any_role("The Werewolf Council", "Host")
    async def addNickname(self, ctx: commands.Context, userid: int, nickname: str):
        success = doAddNickname(userid, nickname)
        if(success == False):
            customError(ctx, "Failed adding nickname!")

