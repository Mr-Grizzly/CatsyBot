import discord
from discord.ext import commands
import datetime
import asyncio


snipe_message_content = None
snipe_message_author = None
snipe_message_id = None


class Tools(commands.Cog):
    """All commands which tell you info are here"""
    def __init__(self, client):
        self.guild = None
        self.author = None
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        global snipe_message_content
        global snipe_message_author
        global snipe_message_id

        snipe_message_content = message.content
        snipe_message_author = message.author.name
        snipe_message_id = message.id
        await asyncio.sleep(60)

        if message.id == snipe_message_id:
            snipe_message_author = None
            snipe_message_content = None
            snipe_message_id = None

    @commands.command()
    async def snipe(self, message):
        if snipe_message_content is None:
            await message.channel.send("There`s nothing to snipe.")
        else:
            embed = discord.Embed(description=f"{snipe_message_content}", colour=discord.Colour.blue())
            embed.set_footer(text=f"Asked by {message.author.name}#{message.author.discriminator}",
                             icon_url=message.author.avatar_url)
            embed.set_author(name=f"{snipe_message_author}")
            await message.channel.send(embed=embed)
            return

    @commands.command()
    async def ping(self, ctx):
        """PING PONG"""
        await ctx.send(f":ping_pong: Pong with {str(round(self.client.latency, 2))}")

    @commands.command()
    async def invite(self, ctx):
        """Gives you the invite link"""
        example = discord.Embed(
            title="Invite Link",
            url="https://discord.com/api/oauth2/authorize?client_id=796082374248103958&permissions=473169015&scope=bot",
            description="Click the title of this message to invite CatsyBot to your server.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=example)

    @commands.command()
    async def servers(self, ctx):
        activeservers = self.client.guilds
        for guild in activeservers:
            await ctx.send(guild.name)
            print(guild.name)

    @commands.command()
    async def suggest(self, ctx, command, *, description):
        """Suggest a command. Note: the suggestions go to the Test server"""
        embed = discord.Embed(title='Command Suggestion',
                              description=f'Suggested by: {ctx.author.mention}\nCommand Name: *{command}*',
                              color=discord.Color.green())
        embed.add_field(name='Description', value=description)
        channel = ctx.guild.get_channel(798154347678400583)
        msg = await channel.send(embed=embed)
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')

    @commands.command()
    async def DMsuggest(self, ctx, suggestion):
        """Suggest through DMs"""
        dm_user = self.client.get_user(762628291508043786)
        await dm_user.send("{} suggested this: '{}'".format(ctx.author.mention, suggestion))

    @commands.command()
    async def testserver(self, ctx):
        """Invites you to the test server"""
        example = discord.Embed(
            title="Invite Link",
            url="https://discord.gg/ajqAeW4MHp",
            description="Click the Title to get invited to Darth Cat's test server",
            color=discord.Color.blue()
        )
        await ctx.send(embed=example)

    @commands.command(aliases=["mc"])
    async def member_count(self, ctx):
        """Tells you how many members there are"""
        a = ctx.guild.member_count
        b = discord.Embed(title=f"members in {ctx.guild.name}", description=a, color=discord.Color(0xffff00))
        await ctx.send(embed=b)

    @commands.command()
    async def info(self, ctx, *, member: discord.Member):
        """Tells you some info about a user"""
        fmt = '{0} joined on {0.joined_at} and has {1} roles.'
        await ctx.send(fmt.format(member, len(member.roles)))

    class MemberRoles(commands.MemberConverter):
        async def convert(self, ctx, argument):
            member = await super().convert(ctx, argument)
            return [role.name for role in member.roles[1:]]

    @commands.command()
    async def roles(self, ctx, *, member: MemberRoles):
        """Tells you a members roles"""
        await ctx.send('I see the following roles: ' + ', '.join(member))

    @commands.command()
    async def serverinfo(self, ctx):
        """Tells you some info about the current server"""
        name = str(ctx.guild.name)
        description = str(ctx.guild.description)

        owner = str(ctx.guild.owner)
        identification = str(ctx.guild.id)
        region = str(ctx.guild.region)
        count = str(ctx.guild.member_count)
        created_at = str(ctx.guild.created_at)

        icon = str(ctx.guild.icon_url)

        embed = discord.Embed(
            title=name + "Server Information",
            description=description,
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Server ID", value=identification, inline=True)
        embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(name="Member Count", value=count, inline=True)
        embed.add_field(name="Created at", value=created_at, inline=True)

        await ctx.send(embed=embed)

    @commands.command(case_insensitive=True, aliases=["remind", "remindme", "remind_me"])
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    async def reminder(self, ctx, time, *, reminder):
        print(time)
        print(reminder)
        user = ctx.message.author
        embed = discord.Embed(color=0x55a7f7, timestamp=datetime.datetime.utcnow())
        embed.set_footer(
            text="If you have any questions, suggestions or bug reports, please join our support Discord Server: https://discord.gg/KsYMRP9dW7",
            icon_url=f"{self.client.user.avatar_url}")
        seconds = 0
        if reminder is None:
            embed.add_field(name='Warning',
                            value='Please specify what do you want me to remind you about.')  # Error message
        if time.lower().endswith("d"):
            seconds += int(time[:-1]) * 60 * 60 * 24
            counter = f"{seconds // 60 // 60 // 24} days"
        if time.lower().endswith("h"):
            seconds += int(time[:-1]) * 60 * 60
            counter = f"{seconds // 60 // 60} hours"
        elif time.lower().endswith("m"):
            seconds += int(time[:-1]) * 60
            counter = f"{seconds // 60} minutes"
        elif time.lower().endswith("s"):
            seconds += int(time[:-1])
            counter = f"{seconds} seconds"
        if seconds == 0:
            embed.add_field(name='Warning',
                            value='Please specify a proper duration, send `reminder_help` for more information.')
        elif seconds < 300:
            embed.add_field(name='Warning',
                            value='You have specified a too short duration!\nMinimum duration is 5 minutes.')
        elif seconds > 7776000:
            embed.add_field(name='Warning',
                            value='You have specified a too long duration!\nMaximum duration is 90 days.')
        else:
            await ctx.send(f"Alright, I will remind you about {reminder} in {counter}.")
            await asyncio.sleep(seconds)
            await ctx.send(f"Hi, you asked me to remind you about {reminder} {counter} ago.")
            return
        await ctx.send(embed=embed)

    @commands.command(name="reminder_help")
    async def reminder_help(self, ctx):
        """Help about reminders"""
        await ctx.send(f"Instead of writing the name of duration, write the first letter of the duration name.")

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(f'{member.display_name} joined on {member.joined_at}')

    @commands.command(name='coolbot')
    async def cool_bot(self, ctx):
        """Is the bot cool?"""
        await ctx.send('This bot is cool. :)')

    @commands.command(name='top_role', aliases=['toprole'])
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: discord.Member = None):
        """Simple command which shows the members Top Role."""

        if member is None:
            member = ctx.author

        await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member = None):
        """A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked."""

        if not member:
            member = ctx.author

        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))

        embed.add_field(name='\uFEFF', value=perms)

        await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Tools(bot))
