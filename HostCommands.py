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
    @commands.command(
        help = (
            "Set the end for the current phase.\n"
            "First argument is the date and time - it's fairly flexible, but "
            "be specific. You _NEED_ to surround it in double quotes, or else "
            "wolf bot will think it's more than one argument. Example, \""
            "1/16/23 6:00 PM\"\n"
            "The second argument is simply the timezone that you're using for "
            "setting the time. Example, EST, UTC, PST, etc."
        ),
        brief = "\tSet the end for the current phase.",
        usage = "[\"DateTime\"] [Timezone]"
    )
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
    @commands.command(
        help = (
            "Displays how much time is left in the phase, and then edits it "
            "every ~second.\n"
            "This command is NOT perfect. Discord doesn't like it constantly "
            "being monitored I guess, and it ends up slowing down "
            "considerably. I would recomend only using this if there is at "
            "most 30 minutes left."
        ),
        brief = "\tPhase Countdown Timer",
        usage = ""
    )
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
    @commands.command(
        help = (
            "Swap the roles of player(s) to dead.\n"
            "You can put in as many players as you want as separate arguments. "
            "For example, \ndz peace jburd\n will kill all three of them."
        ),
        brief = "\tKill player(s)",
        usage = "[Player1] [Player2] ... [PlayerN]"
    )
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
    @commands.command(
        help = (
            "Swap the roles of player(s) to alive.\n"
            "You can put in as many players as you want as separate arguments. "
            "For example, \ndz peace jburd\n will mark all three of them as "
            "living. This is useful for the very beginning of the game to make "
            "all players living."
        ),
        brief = "\tMark player(s) as living",
        usage = "[Player1] [Player2] ... [PlayerN]"
    )
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
    @commands.command(
        help = (
            "For every player that is not Living, Dead, or Host,"
            "mark them as a spectator.\n"
            "Use this command at the beginning of the game, after Livify."
        ),
        brief = "\tMark player(s) as spectators",
        usage = ""
    )
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
    @commands.command(
        help = (
            "Removes game roles from specified players.\n"
            "You can specify one or more players to remove game-related roles "
            "from. For example, \ndz peace jburd\n will remove all from those "
            "three.\nAlternatively, you can specify ALL instead of a player's "
            "name, and it will remove them from everybody.\n"
            "Useful for the end of the game. NOTE: specifying ALL _WILL_ "
            "remove your Host privilages, so use with caution!"
        ),
        brief = "\tRemove game-related roles from player(s)",
        usage = "[Player1] [Player2] ... [PlayerN] OR [ALL]"
    )
    @commands.has_any_role("The Werewolf Council", "Host")
    async def removeGameRoles(self, ctx: commands.Context, *args):
        await ctx.send("Working on it...")
        if(args[0] == 'ALL'):
            membs = ctx.guild.members
            loopvar = list()
            for m in membs:
                if m.bot:
                    continue
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
        await ctx.send("Done!")
                
    """
    setVoting - turn voting on or off
        Parms:
            self:   The commands functionality
            ctx:    The bot context
            onoff:  Whether to turn voting on or off. Accepts only ON and OFF
    """
    @commands.command(
        help = (
            "Sets the status of voting.\n"
            "Simply specify either ON or OFF to turn it on and off, "
            "respectively. Turning it on will reset the vote count."
        ),
        brief = "\tTurn voting on or off.",
        usage = "[On/Off]"
    )
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
    @commands.command(
        help = (
            "Have wolf bot send a message to a specified channel.\n"
            "The first argument is the full name of the channel you want to "
            "send it to. For example, general, twg-signups, etc.\n"
            "The second argument is the message you want to send, surrounded "
            "by double-quotes. For example, \"Hello world!\""
        ),
        brief = "\tHave wolf bot speak for you",
        usage = "[Channel] [\"Message\"]"
    )
    @commands.has_any_role("The Werewolf Council", "Host")
    async def Say(self, ctx: commands.Context, 
        channel: str, message: str):
        endChannel = discord.utils.get(ctx.guild.channels, name=channel)
        if(endChannel == None):
            await customError(ctx, "Channel not found.")
            return
        await endChannel.send(message)
    #end Say

    """
    addPlayer - Add a player to the game.
        Parms:
            self:       The commands functionality
            ctx:        The bot context
            username:   The user's base name to be used
            userid:     The user's Discord ID.
    """
    @commands.command(
        help = (
            "Add a player to the wolf game database. This should be done "
            "whenever someone joins the server.\n"
            "The first argument is just the player's basic name, for example, "
            "TheLittlePeace, __DZ, JBurd67, etc.\n"
            "The second argument is the player's Discord ID. If you do not "
            "know how to get that, it may be a good idea to have someone like "
            "Peace do this for you."
        ),
        brief = "\tAdd a player to the wolf game database",
        usage = "[PlayerName] [DiscordID]"
    )
    @commands.has_any_role("The Werewolf Council", "Host")
    async def addPlayer(self, ctx: commands.Context, username: str, userid: int):
        success = setUser(username, userid)
        if(success == False):
            customError(ctx, "Failed adding user!")
        else:
            await ctx.reply(username + " added.")
    #end addPlayer

    """
    addNickname - Add a player's nickname
        Parms:
            self:       The commands functionality
            ctx:        The bot context
            userid:     The player's Discord ID
            nickname:   The nickname to be added
    """
    @commands.command(
        help = (
            "Add a nickname for a specific player. This is mostly used for "
            "the voting room, so wolf bot knows who is who.\n"
            "The first argument is the player's Discord ID. If you do not "
            "know how to get that, it may be a good idea to have someone like "
            "Peace do this for you.\n"
            "The second argument is the nickname to give the player. If there "
            "happens to be a space in the nickname, make sure you wrap it in "
            "double-quotes."
        ),
        brief = "\tAdd a nickname for a player to the database.",
        usage = "[DiscordID] [Nickname]"
    )
    @commands.has_any_role("The Werewolf Council", "Host")
    async def addNickname(self, ctx: commands.Context, userid: str, nickname: str):
        success = doAddNickname(userid, nickname)
        if(success == False):
            customError(ctx, "Failed adding nickname!")
        else:
            await ctx.reply(nickname + " added.")

