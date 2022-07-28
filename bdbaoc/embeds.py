import discord


async def scan_embed(ctx, member: discord.Member, resultfound: bool)-> discord.Embed:
    embedok = discord.Embed(
                title="Scan Results",
                url="https://docs.google.com/spreadsheets/d/1hph6Xpfp9zngJBMzi24MChRK5Alz5Qt4Uz1nQ8L_m84/edit#gid=0",
                description="Results Below",
                color=discord.Color.random())
    embedok.set_thumbnail(url="https://cdn.discordapp.com/avatars/839574978088796210/296b1a22e987d97431902d0e1db2bae2.png")
    embedok.add_field(name="Servers Found on:", value=f"Found on Value", inline="True")
    embedok.add_field(name="Joined at:", value=f"Joined at Value", inline="True")
    embedok.add_field(name=" ", value=f" ", inline="false")
    embedok.add_field(name="Known Usernames:", value=f"Known Usernames Value", inline="True")
    embedok.add_field(name="Known Nicknames:", value=f"Known Nicknames Value", inline="True")
    embedok.set_footer(text="Powered by Backdoor Bandito")

    embednok = discord.Embed(
                title="Scan Results",
                url="https://docs.google.com/spreadsheets/d/1hph6Xpfp9zngJBMzi24MChRK5Alz5Qt4Uz1nQ8L_m84/edit#gid=0",
                description="User not in Database",
                color=discord.Color.random())
    embednok.set_thumbnail(url="https://cdn.discordapp.com/avatars/839574978088796210/296b1a22e987d97431902d0e1db2bae2.png")
    embednok.set_footer(text="Powered by Backdoor Bandito")


    if resultfound:
        return embedok
    else:
        return embednok