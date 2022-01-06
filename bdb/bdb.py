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
    str_list = list(filter(None, sheet.col_values(8)))
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

    @commands.command()
    async def start_activity(self, ctx, target_voice_channel: discord.VoiceChannel, area): #populate google sheet with members in voice channel
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
        #await ctx.send(listofroles)

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
                allInGameRoles = ["DPS","HEALER","TANK"]
                for positions in allInGameRoles:
                    if positions in userRoles:
                        inGameRole = positions
                        break
                allInGameWeapons = ["⛏️ Great axe","❄️ Ice Gauntlet","🎯 Musket","🛡️ Sword + Shield","❤️ Life Staff",
                "🤺 Rapier","🔱 Spear","🔥 Firestaff","🔨 War Hammer","🪓 Hatchet","⚔️ Sword & Shield(DPS)","🏹 Bow","🏰 Fort Support","🌌 Void Gauntlet"]
                allInGameWeaponsCorrections = ["Great axe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
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
                allDiscordRoles = ["⚜️","Consul", "Admin", "Officer", "Member", "Trial"]
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
                await ctx.send("Activity populated as1: "+area)
                update.clear()
                j = 0

        worksheet.batch_update(update)
        await ctx.send("Activity populated as2: "+area)
    @commands.command()
    async def update_activity(self, ctx, target_voice_channel: discord.VoiceChannel, area):
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
        #await ctx.send(listofroles)

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
                    allInGameRoles = ["DPS", "HEALER", "TANK"]
                    for positions in allInGameRoles:
                        if positions in userRoles:
                            inGameRole = positions
                            break
                    allInGameWeapons = ["⛏️ Great axe","❄️ Ice Gauntlet","🎯 Musket","🛡️ Sword + Shield","❤️ Life Staff","🤺 Rapier",
                    "🔱 Spear","🔥 Firestaff","🔨 War Hammer","🪓 Hatchet","⚔️ Sword & Shield(DPS)","🏹 Bow","🏰 Fort Support","🌌 Void Gauntlet"]
                    allInGameWeaponsCorrections = ["Great axe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
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
                    allDiscordRoles = ["⚜️","Consul", "Admin", "Officer", "Member", "Trial"]
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
                        await ctx.send("error")
            else:
                worksheet.batch_update(update)
                
                update.clear()
                j = 0 #

        yPosition = 8
        a = 7
        j = 0
       
        for user in usersOnSheet1: #For users on sheet
            if user not in listMemberCorrection: # if user is not in dicord channel
                if allDetails[a][9] == "": # They dont have a clock out time
                    memberName = allDetails[a][7]
                    clockIn = allDetails[a][8]
                    clockOut = str(datetime.now().strftime("%H:%M:%S"))
                    update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                                "values": [[memberName, clockIn, clockOut]]}) #Clock them out
                    j = j + 1
                    a = a + 1
                    yPosition = yPosition + 1
                else:
                    a = a + 1
                    yPosition = yPosition + 1
            else:
                if allDetails[a][9] != "":
                    memberName = allDetails[a][7]
                    clockIn = allDetails[a][8]
                    clockOut = allDetails[a][9]
                    notes = allDetails[a][10]
                    if notes == "Pushed a second time":
                        update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                                    "values": [[memberName, clockIn, clockOut, "Pushed multiple times"]]})
                        j = j + 1
                        a = a + 1
                        yPosition = yPosition + 1
                    if notes == "":
                        update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                                "values": [[memberName, clockIn, clockOut, "Pushed a second time"]]})
                        j = j + 1
                        a = a + 1
                        yPosition = yPosition + 1
                else:
                    a = a + 1
                    yPosition = yPosition + 1
        #print(update)
        worksheet.batch_update(update)
        await ctx.send("Activity updated on:"+area)


