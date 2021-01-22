import random
from discord.ext import commands
import links
import about_text as wm
import colors, dice
import asyncio
import discord
import aiohttp


errortxt = ('That is not formatted properly or valid positive integers weren\'t used, ',
            'the proper format is:\n`[Prefix]minesweeper <columns> <rows> <bombs>`\n\n',
            'You can give me nothing for random columns, rows, and bombs.')
errortxt = ''.join(errortxt)


class Fun(commands.Cog):
    """This category is about... well... Fun"""
    def __init__(self, client):
        self.guild = None
        self.author = None
        self.client = client

    @commands.command()
    async def ssp(self, ctx, args):
        """Rock, paper, scissors"""
        ssp_choice = ['scissor', 'stone', 'paper']
        choice = random.choice(ssp_choice)

        if choice == 'scissor' and args == 'scissor':
            s = discord.Embed(title='✂ Scissors', description='Drawn 🙄', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)
        elif choice == 'scissor' and args == 'stone':
            s = discord.Embed(title='✂ Scissors', description='You win 🎉', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)
        elif choice == 'scissor' and args == 'paper':
            s = discord.Embed(title='✂ Scissors', description='You lose 😂', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)

        elif choice == 'stone' and args == 'scissor':
            s = discord.Embed(title='Stone', description='You lose 😂', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)
        elif choice == 'stone' and args == 'stone':
            s = discord.Embed(title='Stone', description='Drawn 🙄', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)
        elif choice == 'stone' and args == 'paper':
            s = discord.Embed(title='Stone', description='You win 🎉', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)

        elif choice == 'paper' and args == 'scissor':
            s = discord.Embed(title='📜 Paper', description='You win 🎉', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)
        elif choice == 'paper' and args == 'stone':
            s = discord.Embed(title='📜 Paper', description='You lose 😂', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)
        elif choice == 'paper' and args == 'paper':
            s = discord.Embed(title='📜 Paper', description='Drawn 🙄', color=colors.fun)
            s.set_author(name='')
            await ctx.send(embed=s)

        else:
            n = discord.Embed(title='Dont try to cheat', description='Invalid choice', color=colors.red)
            n.set_author(name='')
            await ctx.send(embed=n)

    @commands.command()
    async def minesweeper(self, ctx, columns=None, rows=None, bombs=None):
        if columns is None or rows is None and bombs is None:
            if columns is not None or rows is not None or bombs is not None:
                await ctx.send(errortxt)
                return
            else:
                # Gives a random range of columns and rows from 4-13 if no arguments are given
                # The amount of bombs depends on a random range from 5 to this formula:
                # ((columns * rows) - 1) / 2.5
                # This is to make sure the percentages of bombs at a given random board isn't too high
                columns = random.randint(4, 13)
                rows = random.randint(4, 13)
                bombs = columns * rows - 1
                bombs = bombs / 2.5
                bombs = round(random.randint(5, round(bombs)))
        try:
            columns = int(columns)
            rows = int(rows)
            bombs = int(bombs)
        except ValueError:
            await ctx.send(errortxt)
            return
        if columns > 13 or rows > 13:
            await ctx.send('The limit for the columns and rows are 13 due to discord limits...')
            return
        if columns < 1 or rows < 1 or bombs < 1:
            await ctx.send('The provided numbers cannot be zero or negative...')
            return
        if bombs + 1 > columns * rows:
            await ctx.send(
                ':boom:**BOOM**, you have more bombs than spaces on the grid or you attempted to make all of the spaces bombs!')
            return

        # Creates a list within a list and fills them with 0s, this is our makeshift grid
        grid = [[0 for num in range(columns)] for num in range(rows)]

        # Loops for the amount of bombs there will be
        loop_count = 0
        while loop_count < bombs:
            x = random.randint(0, columns - 1)
            y = random.randint(0, rows - 1)
            # We use B as a variable to represent a Bomb (this will be replaced with emotes later)
            if grid[y][x] == 0:
                grid[y][x] = 'B'
                loop_count = loop_count + 1
            # It will loop again if a bomb is already selected at a random point
            if grid[y][x] == 'B':
                pass

        # The while loop will go though every point though our makeshift grid
        pos_x = 0
        pos_y = 0
        while pos_x * pos_y < columns * rows and pos_y < rows:
            # We need to predefine this for later
            adj_sum = 0
            # Checks the surrounding points of our "grid"
            for (adj_y, adj_x) in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                # There will be index errors, we can just simply ignore them by using a try and exception block
                try:
                    if grid[adj_y + pos_y][adj_x + pos_x] == 'B' and adj_y + pos_y > -1 and adj_x + pos_x > -1:
                        # adj_sum will go up by 1 if a surrounding point has a bomb
                        adj_sum = adj_sum + 1
                except Exception as error:
                    pass
            # Since we don't want to change the Bomb variable into a number,
            # the point that the loop is in will only change if it isn't "B"
            if grid[pos_y][pos_x] != 'B':
                grid[pos_y][pos_x] = adj_sum
            # Increases the X values until it is more than the columns
            # If the while loop does not have "pos_y < rows" will index error
            if pos_x == columns - 1:
                pos_x = 0
                pos_y = pos_y + 1
            else:
                pos_x = pos_x + 1

        # Builds the string to be Discord-ready
        string_builder = []
        for the_rows in grid:
            string_builder.append(''.join(map(str, the_rows)))
        string_builder = '\n'.join(string_builder)
        # Replaces the numbers and B for the respective emotes and spoiler tags
        string_builder = string_builder.replace('0', '||:zero:||')
        string_builder = string_builder.replace('1', '||:one:||')
        string_builder = string_builder.replace('2', '||:two:||')
        string_builder = string_builder.replace('3', '||:three:||')
        string_builder = string_builder.replace('4', '||:four:||')
        string_builder = string_builder.replace('5', '||:five:||')
        string_builder = string_builder.replace('6', '||:six:||')
        string_builder = string_builder.replace('7', '||:seven:||')
        string_builder = string_builder.replace('8', '||:eight:||')
        final = string_builder.replace('B', '||:bomb:||')

        percentage = columns * rows
        percentage = bombs / percentage
        percentage = 100 * percentage
        percentage = round(percentage, 2)

        embed = discord.Embed(title='\U0001F642 Minesweeper \U0001F635', color=discord.Colour.blue())
        embed.add_field(name='Columns:', value=columns, inline=True)
        embed.add_field(name='Rows:', value=rows, inline=True)
        embed.add_field(name='Total Spaces:', value=columns * rows, inline=True)
        embed.add_field(name='\U0001F4A3 Count:', value=bombs, inline=True)
        embed.add_field(name='\U0001F4A3 Percentage:', value=f'{percentage}%', inline=True)
        embed.add_field(name='Requested by:', value=ctx.author.display_name, inline=True)
        await ctx.send(content=f'\U0000FEFF\n{final}', embed=embed)

    @minesweeper.error
    async def minesweeper_error(self, ctx, error):
        await ctx.send(errortxt)
        return

    @commands.command()
    async def rolldice(self, ctx):
        """Roll some dice"""
        dice_ = [f'{dice.dice_1}',
                 f'{dice.dice_2}',
                 f'{dice.dice_3}',
                 f'{dice.dice_4}',
                 f'{dice.dice_5}',
                 f'{dice.dice_6}']

        rolldice = discord.Embed(description=f'You rolled a {random.choice(dice_)}',
                                 color=colors.fun)
        rolldice.set_author(name='Roll a dice', icon_url=links.giveaway_fun)
        rolldice.set_footer(text=wm.footer)
        await ctx.send(embed=rolldice)

    @commands.command(pass_context=True)
    async def coinflip(self, ctx):
        """Wanna bet? Flip a coin!"""
        flip = random.choice([
            f'https://upload.wikimedia.org/wikipedia/de/thumb/8/80/2_euro_coin_Eu_serie_1.png/220px-2_euro_coin_Eu_serie_1.png',
            f'https://www.zwei-euro.com/wp-content/uploads/2019/02/DE-2002.gif'])
        flipcoin = discord.Embed()
        flipcoin.colour = 0x12423
        flipcoin.set_thumbnail(
            url="https://media1.tenor.com/images/938e1fc4fcf2e136855fd0e83b1e8a5f/tenor.gif?itemid=5017733")
        flipcoin1 = await ctx.send(embed=flipcoin)
        coin = discord.Embed()
        coin.set_thumbnail(url=f'{flip}')
        await asyncio.sleep(2)
        await flipcoin1.delete()
        await ctx.send(embed=coin)

    @commands.command()
    async def tournament(self, ctx, tc1: discord.Member, tc2: discord.Member, tc3: discord.Member, tc4: discord.Member):
        """Uno game"""
        try:
            user = [tc1, tc2, tc3, tc4]
            hitu1 = f'{tc1} choose a card!'
            hitu2 = f'{tc2} choose a card!'
            hitu3 = f'{tc3} choose a card!'
            hitu4 = f'{tc4} choose a card!'
            rndmc = ['https://i.pinimg.com/originals/9b/bb/70/9bbb7015af1bcd420ee07d89048cebf7.jpg',
                     'https://pics.me.me/thumb_earth-angry-german-kid-spellcastor-tuner-he-rages-about-lag-and-52634494.png',
                     'https://www.memesmonkey.com/images/memesmonkey/cb/cbc69b7a454ec9f50fa0616ca3d4d4d9.jpeg',
                     'https://i.imgur.com/gq8aDzq.jpg',
                     'https://i.redd.it/gqse7u1cudw31.png',
                     'https://i.imgur.com/yeD5fGI.gif',
                     'https://images-na.ssl-images-amazon.com/images/I/51jxIccbroL._AC_.jpg',
                     'https://images-cdn.9gag.com/photo/aDzZ1LO_460s.jpg']

            fight = discord.Embed(description=f'{tc1} vs. {tc2} vs. {tc3} vs. {tc4}')
            fight.set_author(name='Battle', icon_url=links.battle)
            fight.set_thumbnail(url='https://media3.giphy.com/media/dw5SDFsmqFhYs/giphy.gif')
            fight.set_footer(text=wm.footer)
            fight1 = await ctx.send(embed=fight)

            hit = discord.Embed(title=hitu1, color=colors.fun)
            hit.set_image(url=random.choice(rndmc))
            hit_ = await ctx.send(embed=hit)
            await asyncio.sleep(7)

            hit2 = discord.Embed(title=hitu2, color=colors.fun)
            hit2.set_image(url=random.choice(rndmc))
            hit2_ = await ctx.send(embed=hit2)
            await asyncio.sleep(7)

            hit3 = discord.Embed(title=hitu3, color=colors.fun)
            hit3.set_image(url=random.choice(rndmc))
            hit3_ = await ctx.send(embed=hit3)
            await asyncio.sleep(7)

            hit4 = discord.Embed(title=hitu4, color=colors.fun)
            hit4.set_image(url=random.choice(rndmc))
            hit4_ = await ctx.send(embed=hit4)
            await asyncio.sleep(7)

            hit5 = discord.Embed(title=hitu1, color=colors.fun)
            hit5.set_image(url=random.choice(rndmc))
            hit5_ = await ctx.send(embed=hit5)
            await asyncio.sleep(7)

            hit6 = discord.Embed(title=hitu2, color=colors.fun)
            hit6.set_image(url=random.choice(rndmc))
            hit6_ = await ctx.send(embed=hit6)
            await asyncio.sleep(7)

            hit7 = discord.Embed(title=hitu3, color=colors.fun)
            hit7.set_image(url=random.choice(rndmc))
            hit7_ = await ctx.send(embed=hit7)
            await asyncio.sleep(7)

            hit8 = discord.Embed(title=hitu4, color=colors.fun)
            hit8.set_image(url=random.choice(rndmc))
            hit8_ = await ctx.send(embed=hit8)
            await asyncio.sleep(7)

            hit9 = discord.Embed(title=hitu2, color=colors.fun)
            hit9.set_image(url=random.choice(rndmc))
            hit9_ = await ctx.send(embed=hit9)
            await asyncio.sleep(7)

            hit10 = discord.Embed(title=hitu1, color=colors.fun)
            hit10.set_image(url=random.choice(rndmc))
            hit10_ = await ctx.send(embed=hit10)
            await asyncio.sleep(7)

            hit11 = discord.Embed(title=hitu2, color=colors.fun)
            hit11.set_image(url=random.choice(rndmc))
            hit11_ = await ctx.send(embed=hit11)
            await asyncio.sleep(7)

            hit12 = discord.Embed(title=hitu1, color=colors.fun)
            hit12.set_image(url=random.choice(rndmc))
            hit12_ = await ctx.send(embed=hit12)
            await asyncio.sleep(7)

            await fight1.delete()
            await hit_.delete()
            await hit2_.delete()
            await hit3_.delete()
            await hit4_.delete()
            await hit5_.delete()
            await hit6_.delete()
            await hit7_.delete()
            await hit8_.delete()
            await hit9_.delete()
            await hit10_.delete()
            await hit12_.delete()
            winner = discord.Embed(title=f'{random.choice(user)} WINS!!!\n', description=f'{tc1}'
                                                                                         f' VS. '
                                                                                         f'{tc2}'
                                                                                         f'explore more commands with /help',
                                   color=colors.red)
            winner.set_thumbnail(
                url='https://cdna.artstation.com/p/assets/images/images/015/814/178/original/jean-baptiste-gabert-pokemonmockup.gif?1549763590')
            winner.set_footer(text=wm.footer)
            await ctx.send(embed=winner)
        except:
            error = discord.Embed(title='Cant find any user', description='User ```<@user>``')
            await ctx.send(embed=error)

    @commands.command(name="whoami")
    async def whoami(self, ctx):
        """Tells you who you are"""
        await ctx.send(f"You are {ctx.message.author.name}")

    @commands.command()
    async def hack(self, ctx, member: discord.Member):
        random_id = ['20390940',
                     '20930948',
                     '09479398',
                     '03984988',
                     '94883099',
                     '98477490',
                     '37729902',
                     '98765421',
                     '93893893',
                     '08589498',
                     '88489920',
                     '84990201',
                     '94789435',
                     '98839897',
                     '49732974',
                     '97398394',
                     '80489033',
                     '98479883',
                     '97878820',
                     '08839004',
                     '98308934',
                     '09029389',
                     '98308483',
                     '84083887',
                     '08480388',
                     '98408036',
                     '39729993',
                     '39383479',
                     '47859789',
                     '48749749',
                     '70909585']
        passwords = ['Hisj09',
                     'o093y*gh',
                     'Im43fpiN10&',
                     '3i9eiih8',
                     'sok30wok',
                     '39iwi9i',
                     '3kw903ewo',
                     'ekw0kw0',
                     'wokkwooks',
                     'k0okwok',
                     'ko8928',
                     '30ij9i7',
                     '49ie990ko',
                     '30ke0eo',
                     '3003eokeo',
                     '30ek9eki9',
                     '3oke0emiddj',
                     '30e0w0lks8',
                     '48jeijsiji8',
                     '49kred8',
                     '82u2waji',
                     '22ll0la',
                     '30ks0so0',
                     '55omf09',
                     '30309oe',
                     '10009',
                     '10993k',
                     '10020oski',
                     '20keosoo20',
                     'bd489475998',
                     '4u8dhig7t',
                     'o4j9uerri8',
                     '4eud9i4u',
                     '4ue9re9'
                     ]
        y = passwords
        x = random_id
        message = await ctx.send(content=f"🔄 Hacking {member}")
        await asyncio.sleep(5)
        await message.edit(content="❌ Firewall blocking access")
        await asyncio.sleep(5)
        await message.edit(content="✅ Firewall hacked")
        await asyncio.sleep(5)
        await message.edit(content=f"💸 Apple Account password is {random.choice(y)}")
        await asyncio.sleep(5)
        await message.edit(content=f"〽 Credit Card ID is {random.choice(x)}")
        await asyncio.sleep(5)
        await message.edit(content=f"💫 Discord ID is {random.choice(x)}")
        await asyncio.sleep(5)
        await message.edit(content=f"🔄 Google Account password is {random.choice(y)}")
        await asyncio.sleep(5)
        await message.edit(content=f"🔄 Microsoft Account password is {random.choice(y)}")
        await asyncio.sleep(5)
        await message.edit(content=f"🔄 Bank Lock Code is {random.choice(x)}")
        await asyncio.sleep(5)
        await message.edit(content="🔄 Covering all traces")
        await asyncio.sleep(5)
        await message.edit(content="🔄 Destroying browser memory")
        await asyncio.sleep(5)
        await message.edit(content=f"✅ Finished hacking {member}")

    @commands.command()
    async def say(self, ctx, *, message):
        """Makes the bot say something"""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="republicAnthem")
    async def republicAnthem(self, ctx):
        """Plays the Reppy Anthem"""
        await ctx.send(f"https://www.youtube.com/watch?v=aQ_zW_PgWeA%22")

    @commands.command(name="separatistAnthem")
    async def separatistAnthem(self, ctx):
        """Plays the Seppy Anthem"""
        await ctx.send(f"https://www.youtube.com/watch?v=0IBW9mT_PxM&t=2s%22")

    @commands.command()
    async def num(self, ctx: commands.Context):
        """Number guessing-game"""
        await ctx.send(ctx.message.author.mention + ' Would you like to play "guess number" game?')
        randomnum = random.randint(1, 100)
        attempts = 5

        def check(m):
            return (m.author == ctx.author
                    and m.channel == ctx.channel)

        while attempts > 0:
            guess = ""

            while not guess.isdigit():
                await ctx.send(ctx.author.mention + ', write a natural number from 1 to 100 or q (quit)')

                try:
                    msg = await self.client.wait_for('message', timeout=15, check=check)
                    guess = msg.content
                except asyncio.TimeoutError:
                    await ctx.send('Timeout exceed, quitting...')
                    return
                except ValueError:
                    pass

            quitwords = ('q', 'quit', 'exit')
            if guess in quitwords:
                await ctx.send('Quitting...')
                return

            guess = int(guess)

            if guess < randomnum:
                await ctx.send('It is bigger')
            elif guess > randomnum:
                await ctx.send('It is smaller')
            else:
                await ctx.send(f'Ladies and gentlemen, {ctx.author.mention} got it. My number was: {randomnum}')
                return

            attempts -= 1

        await ctx.send(f'You failed! My number was {randomnum}')

    @commands.command(aliases=['8ball', 'ball'])
    async def _8ball(self, ctx, *, question):
        """Answers for your life"""

        responses = ['As I see it, yes.',
                     'Ask again later.',
                     'Better not tell you now.',
                     'Cannot predict now.',
                     'Concentrate and ask again.',
                     'Don’t count on it.',
                     'It is certain.',
                     'It is decidedly so.',
                     'Most likely.',
                     'My reply is no.',
                     'My sources say no.',
                     'Outlook not so good.',
                     'Outlook good.',
                     'Reply hazy, try again.',
                     'Signs point to yes.',
                     'Very doubtful.',
                     'Without a doubt.',
                     'Yes.',
                     'Yes – definitely.',
                     'You may rely on it.'
                     ]
        q = ("Question: " + question)
        a = ("Answer: " + random.choice(responses))
        embed = discord.Embed(
            title=q,
            description=a,
            colour=discord.Colour.blue()
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["facepalm"])
    async def fp(self, ctx):
        """Idiotic memes to laugh at"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r/facepalm/top.json") as response:
                j = await response.json()

        data = j["data"]["children"][random.randint(0, 25)]["data"]
        image_url = data["url"]
        title = data["title"]
        em = discord.Embed(description=f"[**{title}**]({image_url})", colour=discord.Colour.blue())
        em.set_image(url=image_url)
        em.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author}")
        await ctx.send(embed=em)

    @commands.command(aliases=["maymay", "memes"])
    async def meme(self, ctx):
        """Em... well... memes?"""

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r/memes/top.json") as response:
                j = await response.json()

        data = j["data"]["children"][random.randint(0, 25)]["data"]
        image_url = data["url"]
        title = data["title"]
        em = discord.Embed(description=f"[**{title}**]({image_url})", colour=discord.Colour.blue())
        em.set_image(url=image_url)
        em.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author}")
        await ctx.send(embed=em)

    @commands.command(aliases=["prequelmeme", "pre"])
    async def prequel(self, ctx):
        """Star Wars memes"""

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r/PrequelMemes/top.json") as response:
                j = await response.json()

        data = j["data"]["children"][random.randint(0, 25)]["data"]
        image_url = data["url"]
        title = data["title"]
        em = discord.Embed(description=f"[**{title}**]({image_url})", colour=discord.Colour.blue())
        em.set_image(url=image_url)
        em.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author}")
        await ctx.send(embed=em)

    @commands.command(aliases=["ot"])
    async def OTmemes(self, ctx):
        """Star Wars memes"""

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r/OTMemes/top.json") as response:
                j = await response.json()

        data = j["data"]["children"][random.randint(0, 25)]["data"]
        image_url = data["url"]
        title = data["title"]
        em = discord.Embed(description=f"[**{title}**]({image_url})", colour=discord.Colour.blue())
        em.set_image(url=image_url)
        em.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author}")
        await ctx.send(embed=em)

    @commands.command(aliases=['knockout'])
    async def KO(self, ctx, member):
        """Punch the person you hate"""

        gifslist = ['https://media.tenor.com/images/e302b70e805f045816c100a92325b824/tenor.gif',
                    'https://media1.tenor.com/images/3da22c373b5506939514773ad496b170/tenor.gif?itemid=11751811',
                    'https://media1.tenor.com/images/b3dddda27a439a9951fdd0de5a0644e6/tenor.gif?itemid=15872871',
                    'https://media1.tenor.com/images/3b0d7cc04fb09adb1ccc96a23b98dd86/tenor.gif?itemid=6032176',
                    'https://media1.tenor.com/images/97248cf32942f467c4a049acbae8981e/tenor.gif?itemid=3555140',
                    'https://media1.tenor.com/images/c7dece5cdd4cee237e232e0c5d955042/tenor.gif?itemid=4902914']
        gifs = random.choice(gifslist)

        embed = discord.Embed(
            description=f"{member} Has been Knocked Out!",
            colour=discord.Colour.blue()
        )
        embed.set_image(url=gifs)
        await ctx.send(embed=embed)

    @commands.command()
    async def gunfight(self, ctx, user: discord.Member):
        """Who is quicker at drawing his gun?"""
        global response
        choices = ['fire', 'draw', 'shoot', 'bang', 'pull', 'boom']
        gun = random.choice(choices)
        if ctx.message.author == user:
            await ctx.send("**You can't fight yourself!**")
        else:
            await ctx.send(f"{user.mention} **Do you accept the challenge?** ``yes``** or** ``no``?")

        def check(m):
            return m.channel == ctx.channel and m.author == user

        if ctx.message.author != user:
            try:
                response = await self.client.wait_for('message', check=check, timeout=15)
            except:
                await ctx.send(f"**Looks like {user.mention} doesn't want to play :frowning:**")
        tr = random.randrange(5)

        if response.content.lower() == "yes":
            await ctx.send(f"{user.mention} **has accepted the challenge**  :slight_smile:")
            await asyncio.sleep(2)
            await ctx.send("**Get Ready, it will start at any moment!**")
            await asyncio.sleep(tr)
            await ctx.send(f"**Type** ``{gun}`` **now!**")

        if response.content.lower() == "no":
            await ctx.send(f"{user.mention} has declined your request :frowning:")

        user1 = ctx.author
        user2 = user

        def check(n):
            return n.author == user1 or n.author == user2

        message = await self.client.wait_for("message", check=check)
        if message.author == user1:
            if message.content == gun:
                await ctx.send(f"{user1.mention} **Has Won!**")

        else:
            if message.content == gun:
                await ctx.send(f"{user2.mention} **Has Won!**")

    @commands.command(name='..')
    async def command(self, ctx):
        """Indeed..."""
        await ctx.send("Indeed...")


def setup(bot):
    bot.add_cog(Fun(bot))
