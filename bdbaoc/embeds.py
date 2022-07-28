import discord


async def scan_embed(ctx, member: discord.Member, resultfound: bool,foundon,joinedat,usernames=None,nicks=None)-> discord.Embed:
    if usernames is "" or None:
        usernames = "-"
    if nicks is "" or None:
        nicks = "-"

    #SOMETHING FOUND EMBED 
    embedok = discord.Embed(
                title="Scan Results",
                url="https://docs.google.com/spreadsheets/d/1hph6Xpfp9zngJBMzi24MChRK5Alz5Qt4Uz1nQ8L_m84/edit#gid=0",
                color=discord.Color.random())
    embedok.set_thumbnail(url="https://cdn.discordapp.com/avatars/839574978088796210/296b1a22e987d97431902d0e1db2bae2.png")
    embedok.add_field(name="Servers Found on:", value=f"{foundon}", inline="True")
    embedok.add_field(name="Joined at:", value=f"{joinedat}", inline="True")
    embedok.add_field(name="-", value="-", inline="false")
    embedok.add_field(name="Known Usernames:", value=f"{usernames}", inline="True")
    embedok.add_field(name="Known Nicknames:", value=f"{nicks}", inline="True")
    embedok.set_footer(text="Powered by Backdoor Bandito")
    embedok.set_author(name=member.display_name, url=member.avatar_url, icon_url=member.avatar_url)

    #USER NOT IN DATABASE EMBED
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