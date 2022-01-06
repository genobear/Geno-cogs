from redbot.core import commands
import discord

#requirements for googlsheet integration
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate
from datetime import datetime

from redbot.core.utils import chat_formatting as chat

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#SCANNER GSHEET CREDS
scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(ROOT_DIR, 'client.json'), scope)
client = gspread.authorize(creds)

#ATTENDANCE/ACTIVITY SHEET
scope2 = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds2 = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(ROOT_DIR, 'client2.json'), scope2)
client2 = gspread.authorize(creds2)


def sendLog(msg):
    webhook.send(msg)

def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(3)))
    return int(len(str_list) + 1)

class bdb(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def scan(self, ctx, arg):
        """This does stuff!"""
        # Your code will go here
        sheet = client.open('INS').sheet1
        sheetDetails = sheet.get_all_values()
        IDColumn = sheet.col_values(2)
        if arg in IDColumn:
            for a in sheetDetails:
                if a[1] == arg:
                    #response = ("User " + str(a[0]) + " is in these discords :\n" + a[2])
                    response = "```" + (tabulate([["Servers Found on:","Joined at:","Known Names:"],
                            [a[2],a[3],a[5]]],headers='firstrow',tablefmt='psql')) + "```"
        else:
            response = "User not in database"
        await ctx.send("%s" % response)
        
    @commands.command()
    async def invasion(self, ctx):
        """Time for Invasion?"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdb/so_we_now_have_invasion.mp3"))
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdb/YeahBro.mp3"))

    @commands.command()
    async def grav(self, ctx):
        """Grav well in 2 minutes"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdb/2minGrav.mp3"))
    
    @commands.command()
    async def yeahbro(self, ctx):
        """Grav well in 2 minutes"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdb/YeahBro.mp3"))
        
    @commands.command()
    async def yesdaddy(self, ctx):
        """Yes Daddy"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdb/Yes_Daddy.mp3"))
        
    @commands.command()
    async def beans(self, ctx):
        """Beans on Toast"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdb/beansOnToast.mp3"))

    @commands.command()
    async def weights(self, ctx):
        """Armour Weights"""
        await ctx.send(file=discord.File("/home/genobear90/share/Red-DiscordBot/data/redenv/cogs/CogManager/cogs/bdb/weights.png"))

    @commands.command()
    async def reboot(self, ctx):
        "Reboot the OS running the bot. Use with caution"
        await ctx.send("Rebooting the server...")
        os.system("sudo reboot")
        
    @commands.command()
    async def attendance(self, ctx, channel_from: discord.VoiceChannel):
        "Get a list of users in a vocie channel"

        member_names = [] #(list)
        for member in channel_from.members:
            member_names.append(member.display_name)

        await ctx.send(member_names)

    #@commands.command()   # Not in use
    # #async def upload_attendance(self, ctx, target_voice_channel: discord.VoiceChannel, activity):
    #     """Upload attendance from <target_voice_channel> to Google Sheet.
    #     You must first create the sheet with the <activity> name or date."""

    #     area = activity #Must = data given
    #     listOfMembers = []#Needs to be data gathered by bot
        
    #     #Gather member list from target voice channel
    #     for member in target_voice_channel.members:
    #         listOfMembers.append(member.display_name)
        
    #     #Add member list to google sheet
    #     worksheet = client.open('BDB Push Attendance').worksheet(area)
    #     #spreadsheet = client.open("BDB Push Attendance")
    #     next_row = next_available_row(worksheet)
        
    #     update = []
    #     x = next_row
    #     j = 0
    #     for member in listOfMembers:
    #         if j < 1000:
    #             try:
    #                 update.append({'range': 'B' + str(x) + ':' + 'D' + str(x), "values": [
    #                     [member]]})
    #                 x = x + 1
    #                 j = j + 1
    #             except Exception as e:
    #                 await ctx.send("Problem with writing user details, contact Rootoo2")
    #                 return
    #         else:
    #             worksheet.batch_update(update)
    #             update.clear()
    #             j = 0

    #     worksheet.batch_update(update)
        #Respond in discord
    #    await ctx.send(listOfMembers)
    #    await ctx.send("Memberlist Uploaded")

    @commands.command()
    async def activitycheck(self, ctx, target_voice_channel: discord.VoiceChannel, area): #populate google sheet with members in voice channel
        """Start attendance check from <target_voice_channel> to Google Sheet.
        Use the <area> name to set the sheet name"""
        
        #Gather member list from target voice channel
        x = 0
        listOfMembers = []
        listofroles = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                listofroles.append(str(x) + str(role.name))
            x = x + 1
        await ctx.send("listOfMembers:")
        await ctx.send(listOfMembers)
        await ctx.send("listofroles:")
        await ctx.send(listofroles)

        #GOOGLE SHEET MAGIC        
        worksheet1 = client2.open("BDB Push Attendance").worksheet('Template 2')
        worksheet1.duplicate(new_sheet_name=area)
        worksheet = client2.open("BDB Push Attendance").worksheet(area)
        worksheet.update('G4', str(datetime.now().strftime("%H:%M:%S")))
        worksheet.update('E4', str(datetime.now().strftime("%d-%m-%Y")))
        worksheet.update('D2', area)
        next_row = next_available_row(worksheet)
        update = []
        x = next_row + 1
        j = 0
        for member in listOfMembers:
            userRoles = []
            if j < 1000:
                if str(j) in str(member):
                    scanning = False
                    for roles in listofroles   :
                        if scanning == False:
                            if str(j) in roles:
                                userRoles.append(str(roles).replace(str(j),""))
                                scanning = not scanning
                        else:
                            if str(j + 1) in roles:
                                scanning = not scanning
                                break
                            else:
                                userRoles.append(str(roles).replace(str(j),""))
                inGameRole = ""
                discordRole = ""
                Wep1 = ""
                Wep2 = ""
                memberName = str(member).replace(str(j)+":","")
                allInGameRoles = ["DPS","Healer","Tank"]
                for positions in allInGameRoles:
                    if positions in userRoles:
                        inGameRole = positions
                        break
                allInGameWeapons = ["⛏️ Great axe","❄️ Ice Gauntlet","🎯 Musket","🛡️ Sword + Shield","❤️ Life Staff",
                "🤺 Rapier","🔱 Spear","🔥 Firestaff","🔨 War Hammer","🪓 Hatchet","⚔️ Sword & Shield(DPS)","🏹 Bow","🏰 Fort Support","🌌 Void Gauntlet"]
                allInGameWeaponsCorrections = ["Greataxe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
                                    "Rapier", "Spear", "Firestaff", "War Hammer", "Hatchet",
                                    "Sword & Shield(DPS)", "Bow", "Fort Support", "Void Gauntlet"]
                weaponCount = 0
                for weapons in allInGameWeapons:
                    if weapons in userRoles:
                        if Wep1 == "":
                            Wep1 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount],"")
                        else:
                            Wep2 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount],"")
                            break
                    weaponCount = weaponCount + 1
                allDiscordRoles = ["Consul", "Admin", "Officer", "Member", "Trial"]
                for status in allDiscordRoles:
                    if status in userRoles:
                        discordRole = status
                        break

                try:
                    update.append({'range': 'D' + str(x) + ':' + 'K' + str(x), "values": [[inGameRole,Wep1,Wep2,discordRole,memberName,str(datetime.now().strftime("%H:%M:%S")) ,]]})
                    x = x + 1
                    j = j + 1
                except Exception as e:

                    await ctx.send("error")
            else:
                worksheet.batch_update(update)
                update.clear()
                j = 0

        worksheet.batch_update(update)
    
    @commands.command()
    async def updateactivity(self, ctx, target_voice_channel: discord.VoiceChannel, area):
        """Start attendance check from <target_voice_channel> to Google Sheet.
        Use the <area> name to set the sheet name."""

        listOfMembers = []
        listofroles = []

        #Gather member list from target voice channel
        x = 0
        listOfMembers = []
        listofroles = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                listofroles.append(str(x) + str(role.name))
            x = x + 1
        await ctx.send("listOfMembers:")
        await ctx.send(listOfMembers)
        await ctx.send("listofroles:")
        await ctx.send(listofroles)

        #GOOGLE SHEET MAGIC
        worksheet = client2.open("BDB Push Attendance").worksheet(area)
        next_row = next_available_row(worksheet)
        update = []
        usersOnSheet = worksheet.col_values(8)
        usersOnSheet1 = usersOnSheet[7:]
        x = next_row + 1
        j = 0
        allDetails = worksheet.get_all_values()
        listMemberCorrection = []

        for person in listOfMembers:
            corrected = str(person).split(":")
            listMemberCorrection.append(corrected[1])
        #NEED TO ADD ROLES TO THIS FOR
        for member in listMemberCorrection:
            userRoles = []
            if j < 1000:
                if member not in usersOnSheet1:
                    if str(j) in str(listOfMembers[j]):
                        scanning = False
                        for roles in listofroles:
                            if scanning == False:
                                if str(j) in roles:
                                    userRoles.append(str(roles).replace(str(j), ""))
                                    scanning = not scanning
                            else:
                                if str(j + 1) in roles:
                                    scanning = not scanning
                                    break
                                else:
                                    userRoles.append(str(roles).replace(str(j), ""))
                    inGameRole = ""
                    discordRole = ""
                    Wep1 = ""
                    Wep2 = ""
                    memberName = str(member).replace(str(j) + ":", "")
                    allInGameRoles = ["DPS", "Healer", "Tank"]
                    for positions in allInGameRoles:
                        if positions in userRoles:
                            inGameRole = positions
                            break
                    allInGameWeapons = ["⛏️ Great axe","❄️ Ice Gauntlet","🎯 Musket","🛡️ Sword + Shield","❤️ Life Staff","🤺 Rapier",
                    "🔱 Spear","🔥 Firestaff","🔨 War Hammer","🪓 Hatchet","⚔️ Sword & Shield(DPS)","🏹 Bow","🏰 Fort Support","🌌 Void Gauntlet"]
                    allInGameWeaponsCorrections = ["Greataxe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
                                    "Rapier", "Spear", "Firestaff", "War Hammer", "Hatchet",
                                    "Sword & Shield(DPS)", "Bow", "Fort Support", "Void Gauntlet"]
                    weaponCount = 0
                    for weapons in allInGameWeapons:
                        if weapons in userRoles:
                            if Wep1 == "":
                                Wep1 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
                            else:
                                Wep2 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
                                break
                        weaponCount = weaponCount + 1
                    allDiscordRoles = ["Consul", "Admin", "Officer", "Member", "Trial"]
                    for status in allDiscordRoles:
                        if status in userRoles:
                            discordRole = status
                            break

                    try:
                        update.append({'range': 'D' + str(x) + ':' + 'K' + str(x),
                                        "values": [[inGameRole,Wep1,Wep2,discordRole,memberName, str(datetime.now().strftime("%H:%M:%S")), ]]})
                        x = x + 1
                        j = j + 1
                    except Exception as e:
                        # sendLog("Problem with writing user details, contact Rootoo2")
                        print("error")
            else:
                worksheet.batch_update(update)
                update.clear()
                j = 0 #

        yPosition = 8
        a = 7
        j = 0
       
    @commands.command()
    async def role_members(self, ctx, role: discord.Role):
        """Get list of members that has provided role"""
        memberslist = []
        for member in role.members:
            memberslist.append(member.display_name)
        response = '```' +(tabulate(memberslist, tablefmt="orgtbl", headers=[("DisplayName"), ("Name")])) + '```'
        await ctx.send(response)

    @commands.command()
    async def roletest(self, ctx, target_voice_channel: discord.VoiceChannel, area):
        """Start attendance check from <target_voice_channel> to Google Sheet.
        Use the <area> name to set the sheet name."""
        x = 0
        listOfMembers = []
        listofroles = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                listofroles.append(str(x) + str(role.name))
            x = x + 1

        await ctx.send("listOfMembers:")
        await ctx.send(listOfMembers)
        await ctx.send("listofroles:")
        await ctx.send(listofroles)
                
                

        # #Gather member list from target voice channel
        # for member in target_voice_channel.members:
        #     listOfMembers.append(member.display_name)
        #     for role in member.roles:
        #         listofroles.append(role.name)

        # await ctx.send("listOfMembers:")
        # await ctx.send(listOfMembers)
        # await ctx.send("listofroles:")
        # await ctx.send(listofroles)
