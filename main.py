import discord
from discord.ext import commands
from pretty_help import PrettyHelp


bot = commands.Bot(command_prefix=".", description='A bot specially made for fun', owner_id=762628291508043786, case_insensitive=True)
bot.load_extension('cog_admin')
bot.load_extension('cog_info')
bot.load_extension('cog_calculator')
bot.load_extension('cog_stuff')
bot.help_command = PrettyHelp()
bot.help_command = PrettyHelp(index_title="CatsyBot Help Page", no_category="Other Stuff")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=".help | on " + str(len(bot.guilds)) + " Servers.", type=0))
    print('Darth Cats is online')
    print('██████╗░░█████╗░████████╗  ██╗░██████╗  ██████╗░███████╗░█████╗░██████╗░██╗░░░██╗')
    print('██╔══██╗██╔══██╗╚══██╔══╝  ██║██╔════╝  ██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗░██╔╝')
    print('██████╦╝██║░░██║░░░██║░░░  ██║╚█████╗░  ██████╔╝█████╗░░███████║██║░░██║░╚████╔╝░')
    print('██╔══██╗██║░░██║░░░██║░░░  ██║░╚═══██╗  ██╔══██╗██╔══╝░░██╔══██║██║░░██║░░╚██╔╝░░')
    print('██████╦╝╚█████╔╝░░░██║░░░  ██║██████╔╝  ██║░░██║███████╗██║░░██║██████╔╝░░░██║░░░')


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occurred: {str(error)}")


@bot.listen()
async def on_message(message):
    if message.content.startswith('Hello there'):
        msg = 'General Kenobi... you are a bold one'.format(message)
        await message.channel.send(msg)


bot.run("TOKEN")
