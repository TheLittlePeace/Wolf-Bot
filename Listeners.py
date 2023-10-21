#ErrorHandler.py
from discord.ext import commands
from BotFunctions import * 
from discord import *

#############################
# ERROR HANDLING
#############################

class ErrorHandler(commands.Cog):
    """A cog for global error handling."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, 
            error: commands.CommandError):
        
        message = "Beep boop, something went wrong. "
        message += "Review the command and try again.\n"
        message += "Use !help [command] for more information.\n"
        message += "Error text: " + str(error)
        print(error)
        await ctx.reply(message)
#end ErrorHandler

#############################
# VOTE ROOM WATCH
#############################
class voteRoomWatch(commands.Cog):
    """A cog for monitoring the voting room"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """
    Monitor the voting room. If the voting variable is ON, record each player's
    votes in the playervotes table.
    """
    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        vote_status = getGlobalData('VOTING')
        voter = message.author
        global PGCONN
        #Check to see if message has content and it was sent through voting-room
        #   and that voting is turned on
        if(message.content != None 
        and channel.name == 'voting-room'
        and vote_status.upper() == 'ON'
        and get(message.guild.roles, name = 'Living') in voter.roles):
            vote_round_id = getGlobalData("CURRENT_VOTE_ID")
            voter_name = voter.name
            votee_id = getUserID(message.content.strip())
            if(votee_id == False):
                await message.reply("Who the fuck is that?")
                return
            cur = PGCONN.cursor()
            query = "SELECT username FROM members WHERE userid = %s"
            cur.execute(query, (votee_id,))
            ret = cur.fetchone()
            votee_name = ret[0]

            query = """INSERT INTO playervotes (id, voter_name, vote) 
            VALUES (%s, %s, %s)
            ON CONFLICT(id, voter_name) DO UPDATE
                SET vote = %s"""
            cur.execute(query, (vote_round_id, voter_name, votee_name, 
                votee_name))
            PGCONN.commit()
            
            #make sure that worked
            query = """SELECT vote FROM playervotes WHERE id = %s 
            AND voter_name = %s"""
            cur.execute(query, (vote_round_id, voter_name))
            ret = cur.fetchone()
            if(ret == None):
                message.reply("Something went wrong with the voting process!")
                message.reply("Blame Peace, and tell him to fix me!")

            cur.close()
    #end on_message
            
#############################
# WHI IS PAT?
#############################
class whoIsPat(commands.Cog):
    """A cog for monitoring every channel for pat"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """
    Monitor every room for Pat. When Pat is said, reply appropriately.
    """
    @commands.Cog.listener()
    async def on_message(self, message):
        msg_in = message.content
        bot_auth = message.author.bot
        if msg_in != self.bot.command_prefix:
            if (string_found("pat", msg_in.lower())
            and not bot_auth):
                await message.reply("WHO the *FUCK* is Pat?")
        return
        