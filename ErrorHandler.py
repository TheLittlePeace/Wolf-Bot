#ErrorHandler.py
from discord.ext import commands

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