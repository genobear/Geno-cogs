from redbot.core import commands
from discord.ext import tasks
import discord

class bdbaoc(commands.Cog):
    "Version 2 of the great BDB cog."

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def invasion(self, ctx):
        """Time for Invasion?"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdbaoc/so_we_now_have_invasion.mp3"))
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdbaoc/YeahBro.mp3"))

    @commands.command()
    async def grav(self, ctx):
        """Grav well in 2 minutes"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdbaoc/2minGrav.mp3"))
    
    @commands.command()
    async def yeahbro(self, ctx):
        """Grav well in 2 minutes"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdbaoc/YeahBro.mp3"))
        
    @commands.command()
    async def yesdaddy(self, ctx):
        """Yes Daddy"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdbaoc/Yes_Daddy.mp3"))
        
    @commands.command()
    async def beans(self, ctx):
        """Beans on Toast"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdbaoc/beansOnToast.mp3")) 

    @commands.command()
    async def memberlist(self, ctx, role: discord.Role):
        "Get a list of members, roles and ID's. Input a discord role."
        x = 0
        roleList = []
        member_names = [] #(list)
        listOfMembersID = []
        
        filename = str(role) + "members"
        filename2 = str(role) + "roles"
        filename3 = str(role) + "membersID"
        
        for member in role.members:
            member_names.append(str(x) + ":" + str(member.display_name))
            listOfMembersID.append(str(x) + ":" + str(member.id))
            for role in member.roles:
                roleList.append(str(x) + ":" + str(role.name))
            x = x + 1

        textfile = open(f"{filename}.txt", "w")
        textfile.write(str(member_names))
        textfile.close()
        textfile = open(f"{filename2}.txt", "w")
        textfile.write(str(roleList))
        textfile.close()
        textfile = open(f"{filename3}.txt", "w")
        textfile.write(str(listOfMembersID))
        textfile.close()
        await ctx.send(file=discord.File(f"{filename}.txt"))
        await ctx.send(file=discord.File(f"{filename2}.txt"))
        await ctx.send(file=discord.File(f"{filename3}.txt"))
        #await ctx.send(member_names) 

    @commands.command()
    async def test(self, ctx):
        await ctx.send(f"Your discord ID is {ctx.author.id}")       