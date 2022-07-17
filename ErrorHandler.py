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

"""
customError - Raise a custom error message, for things that won't be caught.
    Parms:
        ctx:    The bot functionality
        errTxt: The custom text to display.
    Outputs:
        The custom error message to the user that raised it.
"""
async def customError(ctx, errTxt):
    message = "Beep boop, something went wrong. "
    message += "Review the command and try again.\n"
    message += "Use !help [command] for more information.\n"
    message += "Error text: " + errTxt
    print(errTxt)
    await ctx.reply(message)
