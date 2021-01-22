import discord
from discord.ext import commands
from discord.utils import get
import json
import atexit
import uuid


reaction_roles_data = {}

try:
	with open("reaction_roles.json") as file:
		reaction_roles_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as ex:
	with open("reaction_roles.json", "w") as file:
		json.dump({}, file)


@atexit.register
def store_reaction_roles():
	with open("reaction_roles.json", "w") as file:
		json.dump(reaction_roles_data, file)


def getMember(username, guild, client):
	try:
		userid = int(username)
		member = guild.get_member(userid)
		return member
	except ValueError:
		try:
			user = guild.get_member_named(username)
			assert user is not None
			return user
		except AssertionError:
			if username.startswith('<@') and username.endswith('>'):
				username = username[2:-1]
				if username[0] == '!':
					username = username[1:]
				userid = int(username)
				member = guild.get_member(userid)
				return member
			else:
				raise Exception(f'Invalid user {username}')


class Utilities(commands.Cog):
	"""Only for Admins"""
	def __init__(self, client):
		self.guild = None
		self.author = None
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("Admin cog ready")

	async def cog_check(self, ctx):
		admin = get(ctx.guild.roles, name="Admin")
		return admin in ctx.author.roles

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"ReactionRoles ready.")

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		role, user = self.parse_reaction_payload(payload)
		if role is not None and user is not None:
			await user.add_roles(role, reason="ReactionRole")

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		role, user = self.parse_reaction_payload(payload)
		if role is not None and user is not None:
			await user.remove_roles(role, reason="ReactionRole")

	@commands.command()
	async def shutdown(self, ctx):
		await ctx.bot.logout()

	@commands.has_permissions(manage_channels=True)
	@commands.command()
	async def reaction(
			self,
			ctx,
			emote,
			role: discord.Role,
			channel: discord.TextChannel,
			title,
			message,
	):
		"""Add a reaction"""
		embed = discord.Embed(title=title, description=message)
		msg = await channel.send(embed=embed)
		await msg.add_reaction(emote)
		self.add_reaction(ctx.guild.id, emote, role.id, channel.id, msg.id)

	@commands.has_permissions(manage_channels=True)
	@commands.command()
	async def reaction_add(
			self, ctx, emote, role: discord.Role, channel: discord.TextChannel, message_id
	):
		"""Add reaction role"""
		self.add_reaction(ctx.guild.id, emote, role.id, channel.id, message_id)

	@commands.has_permissions(manage_channels=True)
	@commands.command()
	async def reactions(self, ctx):
		"""List all reaction roles"""
		guild_id = ctx.guild.id
		data = reaction_roles_data.get(str(guild_id), None)
		embed = discord.Embed(title="Reaction Roles")
		if data is None:
			embed.description = "There are no reaction roles set up right now."
		else:
			for index, rr in enumerate(data):
				emote = rr.get("emote")
				role_id = rr.get("roleID")
				role = ctx.guild.get_role(role_id)
				channel_id = rr.get("channelID")
				message_id = rr.get("messageID")
				embed.add_field(
					name=index,
					value=f"{emote} - @{role} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
					inline=False,
				)
		await ctx.send(embed=embed)

	@commands.has_permissions(manage_channels=True)
	@commands.command()
	async def reaction_remove(self, ctx, index: int):
		"""Remove reaction role"""
		guild_id = ctx.guild.id
		data = reaction_roles_data.get(str(guild_id), None)
		embed = discord.Embed(title=f"Remove Reaction Role {index}")
		rr = None
		if data is None:
			embed.description = "Given Reaction Role was not found."
		else:
			embed.description = (
				"Do you wish to remove the reaction role below? Please react with 🗑️."
			)
			rr = data[index]
			emote = rr.get("emote")
			role_id = rr.get("roleID")
			role = ctx.guild.get_role(role_id)
			channel_id = rr.get("channelID")
			message_id = rr.get("messageID")
			_id = rr.get("id")
			embed.set_footer(text=_id)
			embed.add_field(
				name=index,
				value=f"{emote} - @{role} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
				inline=False,
			)
		msg = await ctx.send(embed=embed)
		if rr is not None:
			await msg.add_reaction("🗑️")

			def check(reaction, user):
				return (
						reaction.message.id == msg.id
						and user == ctx.message.author
						and str(reaction.emoji) == "🗑️"
				)

			reaction, user = await self.client.wait_for("reaction_add", check=check)
			data.remove(rr)
			reaction_roles_data[str(guild_id)] = data
			store_reaction_roles()

	def add_reaction(self, guild_id, emote, role_id, channel_id, message_id):
		if not str(guild_id) in reaction_roles_data:
			reaction_roles_data[str(guild_id)] = []
		reaction_roles_data[str(guild_id)].append(
			{
				"id": str(uuid.uuid4()),
				"emote": emote,
				"roleID": role_id,
				"channelID": channel_id,
				"messageID": message_id,
			}
		)
		store_reaction_roles()

	def parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
		guild_id = payload.guild_id
		data = reaction_roles_data.get(str(guild_id), None)
		if data is not None:
			for rr in data:
				emote = rr.get("emote")
				if payload.message_id == rr.get("messageID"):
					if payload.channel_id == rr.get("channelID"):
						if str(payload.emoji) == emote:
							guild = self.client.get_guild(guild_id)
							role = guild.get_role(rr.get("roleID"))
							user = guild.get_member(payload.user_id)
							return role, user
		return None, None

	@commands.command(pass_context=True, aliases=["purge"])
	@commands.has_permissions(administrator=True)
	async def clear(self, ctx, limit: int):
		"""Clears some messages"""
		await ctx.channel.purge(limit=limit)

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def lockdown(self, ctx, role: discord.Role):
		"""Locks a channel"""
		await ctx.channel.set_permissions(role, send_messages=False, embed_links=False, attach_files=False)
		await ctx.send(ctx.channel.mention + " ***is now in lockdown.***")

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def unlock(self, ctx, role: discord.Role):
		"""Unlocks a channel"""
		await ctx.channel.set_permissions(role, send_messages=True, embed_links=True, attach_files=True)
		await ctx.send(ctx.channel.mention + " ***is now unlocked.***")

	@commands.command(pass_context=True)
	async def giverole(self, ctx, user: discord.Member, role: discord.Role):
		"""Gives a role to a user"""
		await user.add_roles(role)
		await ctx.send(f"hey {ctx.author.name}, {user.name} has been giving a role called: {role.name}")

	@commands.command(aliases=['make_role'])
	@commands.has_permissions(manage_roles=True)
	async def create_role(self, ctx, *, name):
		"""Creates a role"""
		guild = ctx.guild
		await guild.create_role(name=name)
		await ctx.send(f'Role `{name}` has been created')

	@commands.command(name="slap", aliases=["warn"])
	async def slap(self, ctx, members: commands.Greedy[discord.Member], *, reason='no reason'):
		"""Warns someone"""
		slapped = ", ".join(x.name for x in members)
		await ctx.send('{} just got slapped for {}'.format(slapped, reason))

	@commands.command(name='create-channel')
	async def create_channel(self, ctx, channel_name='new-channel'):
		"""Creates a channel"""
		guild = ctx.guild
		existing_channel = discord.utils.get(guild.channels, name=channel_name)
		if not existing_channel:
			print(f'Creating a new channel: {channel_name}')
			await guild.create_text_channel(channel_name)

	@commands.command(pass_context=True)
	async def chnick(self, ctx, member: discord.Member, nick):
		"""Changes a Member`s nickname"""
		await member.edit(nick=nick)
		await ctx.send(f'Nickname was changed for {member.mention} ')

	@commands.command(name='embed', description='The embed command')
	async def embed_command(self, ctx):

		def check(ms):
			return ms.channel == ctx.message.channel and ms.author == ctx.message.author

		await ctx.send(content='What would you like the title to be?')

		msg = await self.client.wait_for('message', check=check)
		title = msg.content

		await ctx.send(content='What would you like the Description to be?')
		msg = await self.client.wait_for('message', check=check)
		desc = msg.content

		msg = await ctx.send(content='Now generating the embed...')

		embed = discord.Embed(
			title=title,
			description=desc,
			color=discord.Color.blue()
		)
		embed.set_thumbnail(url=self.client.user.avatar_url)

		embed.set_author(
			name=ctx.message.author.name,
			icon_url=ctx.message.author.avatar_url
		)

		await msg.edit(
			embed=embed,
			content=None
		)

	@commands.command()
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.User = None, reason=None):
		"""Bans a member"""
		try:
			embed = discord.Embed(colour=0xC0FF78)
			await ctx.guild.ban(member, reason=reason)
			embed.add_field(name="Banned!", value=f"{member} is banned. Reason: " + str(reason))

			await ctx.channel.send(embed=embed)
		except Exception as e:
			pass
			embed = discord.Embed(description="I don't have permission to ban them :(", colour=discord.Colour.red())

			await ctx.send(embed=embed)

	@commands.command()
	@commands.has_permissions(ban_members=True)
	async def kick(self, ctx, member: discord.User = None, reason=None):
		"""Kicks a member"""
		try:

			await ctx.guild.kick(member, reason=reason)
			embed = discord.Embed(
				description=(f"{member} is kicked. Reason: " + str(reason)),
				colour=discord.Colour.red())
			await ctx.channel.send(embed=embed)
		except Exception as e:
			pass
			embed = discord.Embed(description="I don't have permission to kick them :(", colour=discord.Colour.blue())

	@commands.command()
	async def unban(self, ctx, *, member):
		"""Unbans a member"""
		banned_users = await ctx.guild.bans()
		member_name, member_discriminator = member.split("#")

		for banned_entry in banned_users:
			user = banned_entry.user
			if (user.name, user.discriminator) == (member_name, member_discriminator):
				await ctx.guild.unban(user)
				await ctx.send(f"{user.mention} has been unbanned.:sunglasses:")
				return

	@commands.command()
	async def mute(self, ctx, member: discord.Member):
		"""Mutes a member"""
		role = ctx.guild.get_role(784168505498533920)
		guild = ctx.guild
		if role not in guild.roles:
			perms = discord.Permissions(send_messages=False, speak=False)
			await guild.create_role(name="Muted", permissions=perms)
			role = discord.utils.get(ctx.guild.roles, name="Muted")
			await member.add_roles(role)
			embed = discord.Embed(
				description=f"{member} was muted.", colour=discord.Colour.red()
			)
			await ctx.send(embed=embed)
		else:
			await member.add_roles(role)
			embed = discord.Embed(
				description=f"{member} was muted.", colour=discord.Colour.red()
			)
			await ctx.send(embed=embed)

	@mute.error
	async def mute_error(self, ctx, error):
		if isinstance(error, commands.MissingRole):
			embed = discord.Embed(description="You don't have permission to do this", colour=discord.Colour.blue())
			await ctx.send(embed=embed)
		elif isinstance(error, commands.BadArgument):
			embed = discord.Embed(description="That is not a valid member", colour=discord.Colour.blue())
			await ctx.send(embed=embed)

	@commands.command()
	async def kick(self, msgdata):
		client = msgdata['client']
		message = msgdata['message']
		args = msgdata['args']
		bot_owners = msgdata['bot_owners']
		perms = message.channel.permissions_for(message.author)
		if perms.kick_members or message.author.id in bot_owners:
			member = getMember(args[0], message.guild, client)
			if not args[1:]:
				reason = f'Kicked by {message.author}'
			else:
				reason = ' '.join(args[1:])
			await member.ban(reason=reason)
			await message.channel.send(f'{member} ({member.id}) has been banned')
		else:
			await message.channel.send('You don\'t have permission to do that')

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def unmute(self, ctx, member: discord.Member = None, reason=None):
		"""Unmutes a member"""
		role = discord.utils.get(ctx.message.guild.roles, name="Muted")
		await member.remove_roles(role)
		embed = discord.Embed(colour=discord.Colour.green(), description="Unmuted! :slight_smile: This user is unmuted!")
		await ctx.send(embed=embed)

	def send(self, param):
		pass


def setup(bot):
	bot.add_cog(Utilities(bot))
