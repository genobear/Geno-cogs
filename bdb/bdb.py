from redbot.core import commands
from discord.ext import tasks
import discord
from discord import Webhook, RequestsWebhookAdapter

#requirements for googlsheet integration
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate
from datetime import datetime

import time



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

#webhooks for logs
rooWebHook = Webhook.from_url(
    "https://discord.com/api/webhooks/881474354150539354/AGBcwDltuKJjlbr8LtuL-v5sLeAp6caJgLE_ENJ22cYfCuMPYS68yLXReU57IG6gQUZg",
    adapter=RequestsWebhookAdapter())
webhook = Webhook.from_url(
    "https://discord.com/api/webhooks/880536784197537892/GUJ3aBOsW9XYEXj7qux-3i9BQYjEiblGdkh8tb10cMwmfyc9_3CnoiQ3b-JBPykiRMi_",
    adapter=RequestsWebhookAdapter())
logWebHook = Webhook.from_url("https://discord.com/api/webhooks/881593296168812544/FitcJOcRG8iIAul_ML8PXYz9jIN3T7O5b9M7S3E8X3t2S-M_E0H04OpjA1Bgbs5Sm3c4", adapter=RequestsWebhookAdapter())

def sendLog(msg):
    rooWebHook.send(msg)
    logWebHook.send(msg)
    webhook.send(msg)

def get_lists(target_voice_channel: discord.VoiceChannel):
    #Gather member list from target voice channel
    x = 0
    listOfMembers = []
    roleList = []
    for member in target_voice_channel.members:
        listOfMembers.append(str(x) +": " + str(member.display_name))
        for role in member.roles:
            roleList.append(str(x) + str(role.name))
        x = x + 1

#internal function to find next available row
def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(8)))
    return int(len(str_list) + 1)

def loop(area, listOfMembers, roleList):
    status = "Open"
    while status == "Open":
        sendLog("Inside loop")
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
        status = worksheet.acell('K2').value
        if status == "Open":
            sendLog("Inside loop If statement")
            updateActivity(area, listOfMembers, roleList)
            sendLog("Activity updated on: "+ area)
        else:
            sendLog(area+": Closed from google sheet")
            break
        time.sleep(60)

def updateActivity(area, listOfMembers, roleList):
    worksheet = client.open("BDB Push Attendance").worksheet(area)
    next_row = next_available_row(worksheet)
    usersOnSheet = worksheet.col_values(8)
    usersOnSheet1 = usersOnSheet[7:]
    z = 0
    x = next_row + 1
    j = 0
    allDetails = worksheet.get_all_values()
    listMemberCorrection = []
    update = []
    for person in listOfMembers:
        corrected = str(person).split(":")
        listMemberCorrection.append(corrected[1])
    for member in listMemberCorrection:
        userRoles = []
        inGameRole = ""
        discordRole = ""
        Wep1 = ""
        Wep2 = ""
        if j < 1000:
            if member not in usersOnSheet1:
                if str(z) in str(listOfMembers[z]):
                    for roles in roleList:
                        if str(z) in roles:
                            userRoles.append(str(roles).replace(str(z), ""))
                memberName = str(member).replace(str(z) + ":", "")
                for positions in allInGameRoles:
                    if positions in userRoles:
                        inGameRole = positions
                        break
                weaponCount = 0
                for weapons in allInGameWeapons:
                    if weapons in userRoles:
                        if Wep1 == "":
                            Wep1 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
                        else:
                            Wep2 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
                            break
                    weaponCount = weaponCount + 1
                for status in allDiscordRoles:
                    if status in userRoles:
                        discordRole = status
                        break
                try:
                    update.append({'range': 'D' + str(x) + ':' + 'K' + str(x),
                                   "values": [[inGameRole,Wep1,Wep2,discordRole,memberName, str(datetime.now().strftime("%H:%M:%S")), ]]})
                    x = x + 1
                    j = j + 1
                    z = z + 1
                except Exception as e:
                    # sendLog("Problem with writing user details, contact Rootoo2")
                    print("error")
            else:
                z = z + 1
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

                if len(str(allDetails[a][9]).splitlines()) < len(str(allDetails[a][8]).splitlines()):
                    memberName = allDetails[a][7]
                    clockIn = str(allDetails[a][8])
                    clockOut = str(allDetails[a][9]) + "\n" + str(datetime.now().strftime("%H:%M:%S"))
                    update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                                   "values": [[memberName, clockIn, clockOut]]})
                    j = j + 1
                    a = a + 1
                    yPosition = yPosition + 1
                else:
                    a = a + 1
                    yPosition = yPosition + 1
        else: #If they are in the channel
            if allDetails[a][9] != "": #They do have a clock out time
                if len(str(allDetails[a][9]).splitlines()) == len(str(allDetails[a][8]).splitlines()):
                    memberName = allDetails[a][7]
                    clockIn = str(allDetails[a][8]) + "\n" + str(datetime.now().strftime("%H:%M:%S"))
                    clockOut = allDetails[a][9]

                    update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                               "values": [[memberName, clockIn, clockOut]]})
                    j = j + 1
                    a = a + 1
                    yPosition = yPosition + 1
            else:
                a = a + 1
                yPosition = yPosition + 1
    print(update)
    worksheet.batch_update(update)
    

def populate(area, listOfMembers, roleList):
    worksheet1 = client.open("BDB Push Attendance").worksheet('Template 2') #Opens Sheet for reading
    worksheet1.duplicate(new_sheet_name=area) #Duplicates sheet from template
    worksheet = client.open("BDB Push Attendance").worksheet(area) #Opens new duplicated sheet
    worksheet.update('G4', str(datetime.now().strftime("%H:%M:%S"))) #Populate time
    worksheet.update('E4', str(datetime.now().strftime("%d-%m-%Y"))) #Populate time
    worksheet.update('D2', area) #populates area
    worksheet.update('K2', "Open") #Populates sheet status
    next_row = next_available_row(worksheet) #Calculates next row
    update = [] #Update array
    x = next_row + 1 #x variable for row
    j = 0 #j variable for max amount of updates in single batch
    z = 0 #z variable for gettings roles from list
    for member in listOfMembers:
        userRoles = []
        inGameRole = ""
        discordRole = ""
        Wep1 = ""
        Wep2 = ""
        if j < 1000:
            if str(z) in str(member):
                for roles in roleList:
                    if str(z) in roles:
                        userRoles.append(str(roles).replace(str(z),""))
            memberName = str(member).replace(str(z)+":","")
            for positions in allInGameRoles:
                if positions in userRoles:
                    inGameRole = positions
                    break
            weaponCount = 0
            for weapons in allInGameWeapons:
                if weapons in userRoles:
                    if Wep1 == "":
                        Wep1 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount],"")
                    else:
                        Wep2 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount],"")
                        break
                weaponCount = weaponCount + 1
            for status in allDiscordRoles:
                if status in userRoles:
                    discordRole = status
                    break
            try:
                update.append({'range': 'D' + str(x) + ':' + 'K' + str(x), "values": [[inGameRole,Wep1,Wep2,discordRole,memberName,str(datetime.now().strftime("%H:%M:%S")) ,]]})
                x = x + 1
                j = j + 1
                z = z + 1
            except Exception as e:
                print("error")
        else:
            worksheet.batch_update(update)
            update.clear()
            j = 0
    worksheet.batch_update(update)



#Static Data
allInGameWeapons = ["⛏️ Great axe", "❄️ Ice Gauntlet", "🎯 Musket", "🛡️ Sword + Shield", "❤️ Life Staff",
                                "🤺 Rapier", "🔱 Spear", "🔥 Firestaff", "🔨 War Hammer", "🪓 Hatchet",
                                "⚔️ Sword & Shield(DPS)", "🏹 Bow", "🏰 Fort Support", "🌌 Void Gauntlet"]
allInGameWeaponsCorrections = ["Great axe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
                                           "Rapier", "Spear", "Firestaff", "War Hammer", "Hatchet",
                                           "Sword & Shield(DPS)", "Bow", "Fort Support", "Void Gauntlet"]
allInGameRoles = ["DPS", "HEALER", "TANK"]
allDiscordRoles = ["⚜️","Consul", "Admin", "Officer", "Member", "Trial"]


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

    # @commands.command()
    # async def start_activity(self, ctx, target_voice_channel: discord.VoiceChannel, area): #populate google sheet with members in voice channel
    #     """Start attendance check from <target_voice_channel> to Google Sheet.

    #     Use the <area> name to set the sheet name.
    #     The name is case sensitve, and you must surround and spaces in quotation marks"""
        
    #     #Gather member list from target voice channel
    #     x = 0
    #     listOfMembers = []
    #     listofroles = []
    #     for member in target_voice_channel.members:
    #         listOfMembers.append(str(x) +": " + str(member.display_name))
    #         for role in member.roles:
    #             listofroles.append(str(x) + str(role.name))
    #         x = x + 1


    #     #GOOGLE SHEET MAGIC        
    #     worksheet1 = client2.open("BDB Push Attendance").worksheet('Template 2')
    #     worksheet1.duplicate(new_sheet_name=area)
    #     worksheet = client2.open("BDB Push Attendance").worksheet(area)
    #     worksheet.update('G4', str(datetime.now().strftime("%H:%M:%S")))
    #     worksheet.update('E4', str(datetime.now().strftime("%d-%m-%Y")))
    #     worksheet.update('D2', area)
    #     next_row = next_available_row(worksheet)
    #     update = []
    #     x = next_row + 1
    #     j = 0
    #     for member in listOfMembers:
    #         userRoles = []
    #         if j < 1000:
    #             if str(j) in str(member):
    #                 scanning = False
    #                 for roles in listofroles   :
    #                     if scanning == False:
    #                         if str(j) in roles:
    #                             userRoles.append(str(roles).replace(str(j),""))
    #                             scanning = not scanning
    #                     else:
    #                         if str(j + 1) in roles:
    #                             scanning = not scanning
    #                             break
    #                         else:
    #                             userRoles.append(str(roles).replace(str(j),""))
    #             inGameRole = ""
    #             discordRole = ""
    #             Wep1 = ""
    #             Wep2 = ""
    #             memberName = str(member).replace(str(j)+":","")
    #             allInGameRoles = ["DPS","HEALER","TANK"]
    #             for positions in allInGameRoles:
    #                 if positions in userRoles:
    #                     inGameRole = positions
    #                     break
    #             allInGameWeapons = ["⛏️ Great axe","❄️ Ice Gauntlet","🎯 Musket","🛡️ Sword + Shield","❤️ Life Staff",
    #             "🤺 Rapier","🔱 Spear","🔥 Firestaff","🔨 War Hammer","🪓 Hatchet","⚔️ Sword & Shield(DPS)","🏹 Bow","🏰 Fort Support","🌌 Void Gauntlet"]
    #             allInGameWeaponsCorrections = ["Great axe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
    #                                 "Rapier", "Spear", "Firestaff", "War Hammer", "Hatchet",
    #                                 "Sword & Shield(DPS)", "Bow", "Fort Support", "Void Gauntlet"]
    #             weaponCount = 0
    #             for weapons in allInGameWeapons:
    #                 if weapons in userRoles:
    #                     if Wep1 == "":
    #                         Wep1 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount],"")
    #                     else:
    #                         Wep2 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount],"")
    #                         break
    #                 weaponCount = weaponCount + 1
    #             allDiscordRoles = ["⚜️","Consul", "Admin", "Officer", "Member", "Trial"]
    #             for status in allDiscordRoles:
    #                 if status in userRoles:
    #                     discordRole = status
    #                     break

    #             try:
    #                 update.append({'range': 'D' + str(x) + ':' + 'K' + str(x), "values": [[inGameRole,Wep1,Wep2,discordRole,memberName,str(datetime.now().strftime("%H:%M:%S")) ,]]})
    #                 x = x + 1
    #                 j = j + 1
    #             except Exception as e:

    #                 await ctx.send("error")
    #         else:
    #             worksheet.batch_update(update)
    #             await ctx.send("Activity populated as1: "+area)
    #             update.clear()
    #             j = 0

    #     worksheet.batch_update(update)
    #     await ctx.send("Activity populated as: "+area)

    # @commands.command()
    # async def update_activity(self, ctx, target_voice_channel: discord.VoiceChannel, area):
    #     """Update attendance from <target_voice_channel> to an existing Google Sheet.

    #     Use the <area> name to set the sheet name.
    #     The name is case sensitve, and you must surround and spaces in quotation marks"""



    #     #GOOGLE SHEET MAGIC
    #     worksheet = client2.open("BDB Push Attendance").worksheet(area)
    #     next_row = next_available_row(worksheet)
    #     update = []
    #     usersOnSheet = worksheet.col_values(8)
    #     usersOnSheet1 = usersOnSheet[7:]
    #     x = next_row + 1
    #     j = 0
    #     allDetails = worksheet.get_all_values()
    #     listMemberCorrection = []

    #     for person in listOfMembers:
    #         corrected = str(person).split(":")
    #         listMemberCorrection.append(corrected[1])
    #     #NEED TO ADD ROLES TO THIS FOR
    #     z = 0
    #     for member in listMemberCorrection:
    #         userRoles = []
    #         if j < 1000:
    #             if member not in usersOnSheet1:
    #                 if str(z) in str(listOfMembers[z]):
    #                     scanning = False
    #                     for roles in listofroles:
    #                         if scanning == False:
    #                             if str(z) in roles:
    #                                 userRoles.append(str(roles).replace(str(z), ""))
    #                                 scanning = not scanning
    #                         else:
    #                             if str(z + 1) in roles:
    #                                 scanning = not scanning
    #                                 break
    #                             else:
    #                                 userRoles.append(str(roles).replace(str(z), ""))
    #                 inGameRole = ""
    #                 discordRole = ""
    #                 Wep1 = ""
    #                 Wep2 = ""
    #                 memberName = str(member).replace(str(z) + ":", "")
    #                 allInGameRoles = ["DPS", "HEALER", "TANK"]
    #                 for positions in allInGameRoles:
    #                     if positions in userRoles:
    #                         inGameRole = positions
    #                         break
    #                 allInGameWeapons = ["⛏️ Great axe","❄️ Ice Gauntlet","🎯 Musket","🛡️ Sword + Shield","❤️ Life Staff","🤺 Rapier",
    #                 "🔱 Spear","🔥 Firestaff","🔨 War Hammer","🪓 Hatchet","⚔️ Sword & Shield(DPS)","🏹 Bow","🏰 Fort Support","🌌 Void Gauntlet"]
    #                 allInGameWeaponsCorrections = ["Great axe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
    #                                 "Rapier", "Spear", "Firestaff", "War Hammer", "Hatchet",
    #                                 "Sword & Shield(DPS)", "Bow", "Fort Support", "Void Gauntlet"]
    #                 weaponCount = 0
    #                 for weapons in allInGameWeapons:
    #                     if weapons in userRoles:
    #                         if Wep1 == "":
    #                             Wep1 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
    #                         else:
    #                             Wep2 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
    #                             break
    #                     weaponCount = weaponCount + 1
    #                 allDiscordRoles = ["⚜️","Consul", "Admin", "Officer", "Member", "Trial"]
    #                 for status in allDiscordRoles:
    #                     if status in userRoles:
    #                         discordRole = status
    #                         break

    #                 try:
    #                     update.append({'range': 'D' + str(x) + ':' + 'K' + str(x),
    #                                     "values": [[inGameRole,Wep1,Wep2,discordRole,memberName, str(datetime.now().strftime("%H:%M:%S")), ]]})
    #                     x = x + 1
    #                     j = j + 1
    #                     z = z + 1
    #                 except Exception as e:
    #                     # sendLog("Problem with writing user details, contact Rootoo2")
    #                     await ctx.send("error")
    #             else:
    #                 z = z + 1
    #         else:
    #             worksheet.batch_update(update)
    #             update.clear()
    #             j = 0 #

    #     yPosition = 8
    #     a = 7
    #     j = 0
       
    #     for user in usersOnSheet1: #For users on sheet
    #         if user not in listMemberCorrection: # if user is not in dicord channel
    #             if allDetails[a][9] == "": # They dont have a clock out time
    #                 memberName = allDetails[a][7]
    #                 clockIn = allDetails[a][8]
    #                 clockOut = str(datetime.now().strftime("%H:%M:%S"))
    #                 update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
    #                             "values": [[memberName, clockIn, clockOut]]}) #Clock them out
    #                 j = j + 1
    #                 a = a + 1
    #                 yPosition = yPosition + 1
    #             else:
    #                 a = a + 1
    #                 yPosition = yPosition + 1
    #         else:
    #             if allDetails[a][9] != "":
    #                 memberName = allDetails[a][7]
    #                 clockIn = allDetails[a][8]
    #                 clockOut = allDetails[a][9]
    #                 notes = allDetails[a][10]
    #                 if notes == "Pushed a second time":
    #                     update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
    #                                 "values": [[memberName, clockIn, clockOut, "Pushed multiple times"]]})
    #                     j = j + 1
    #                     a = a + 1
    #                     yPosition = yPosition + 1
    #                 if notes == "":
    #                     update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
    #                             "values": [[memberName, clockIn, clockOut, "Pushed a second time"]]})
    #                     j = j + 1
    #                     a = a + 1
    #                     yPosition = yPosition + 1
    #             else:
    #                 a = a + 1
    #                 yPosition = yPosition + 1
    #     #print(update)
    #     worksheet.batch_update(update)
    #     await ctx.send("Activity updated on:"+area)

    @commands.command()
    async def list_test(self, ctx, target_voice_channel: discord.VoiceChannel, area):
        """Start attendance check from <target_voice_channel> to Google Sheet.
        Use the <area> name to set the sheet name."""

        #Gather member list from target voice channel
        x = 0
        listOfMembers = []
        listofroles = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                listofroles.append(str(x) + str(role.name))
            x = x + 1

        await ctx.send(listOfMembers)
        await ctx.send(listofroles)
        
        
    @commands.command()
    async def start_activity(self,ctx,target_voice_channel: discord.VoiceChannel, area):
        """Start attendance check from <target_voice_channel> to Google Sheet.

        Use the <area> name to set the sheet name.
        The name is case sensitve, and you must surround and spaces in quotation marks
        
        Activity will be automatically updated every 10 minutes. 
        
        Use ?end_activity to end the activity
        
        Only 1 activity can be tracked at a time
        Please use ?update_activity to track a different voice channel/activity"""
        
        #Gather member list from target voice channel
        x = 0
        listOfMembers = []
        roleList = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                roleList.append(str(x) + str(role.name))
            x = x + 1
        await ctx.send(area)
        await ctx.send(roleList)
        await ctx.send(listOfMembers)
        sendLog("populate")
        populate(area, listOfMembers, roleList)
        self.looper.start(area,target_voice_channel)
        sendLog("after looper start")
        
    @commands.command()
    async def update_activity(self, ctx,target_voice_channel: discord.VoiceChannel, area ):
        """Use if you want to start updating from a different <target_voice_channel> or a different <area>.
        
        This will cancel any on going updates.
        
        Activity will be automatically updated every 10 minutes."""
        self.looper.cancel()
        await self.looper.start(area,target_voice_channel)
        await ctx.send("Started automatically updating activity: " + area + "for voice channeL: " + str(target_voice_channel))
    
        
    @commands.command()
    async def end_activity(self,ctx,area):
        """End attendance check from <targ_v"""
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
        worksheet.update('K2', "Closed")  # Populates sheet status
        allDetails = worksheet.get_all_values()
        usersOnSheet = worksheet.col_values(8)
        usersOnSheet1 = usersOnSheet[7:]
        update = []
        a = 7
        j = 0
        yPosition = 8
        for user in usersOnSheet1:
            if j < 1000:
                clockIn = str(allDetails[a][8])
                clockOut = str(allDetails[a][9])
                memberName = allDetails[a][7]
    
                if len(clockIn.splitlines()) == len(clockOut.splitlines()):
                    a = a + 1
                    yPosition = yPosition + 1
    
                else:
                    if len(clockOut.splitlines()) < len(clockIn.splitlines()):
                        clockOut = str(datetime.now().strftime("%H:%M:%S"))
                        update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                                       "values": [[memberName, clockIn, clockOut]]})
                        a = a + 1
                        yPosition = yPosition + 1
                        j = j + 1
            else:
                worksheet.batch_update(update)
                update.clear()
                j = 0  #
        worksheet.batch_update(update)
        self.looper.cancel()
        if self.looper().is_being_cancelled:
            await ctx.send("Activity Looper Stopped")
        
    @tasks.loop(seconds=600.0)
    async def looper(self,area,target_voice_channel: discord.VoiceChannel):
        #Gather member list from target voice channel
        x = 0
        listOfMembers = []
        roleList = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                roleList.append(str(x) + str(role.name))
            x = x + 1
        #def loop(area, listOfMembers, roleList):
        status = "Open"
        #while status == "Open":
        sendLog("Inside looper")
        sendLog("Area: "+area)
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
        status = worksheet.acell('K2').value
        if status == "Open":
            sendLog("Inside loop If statement")
            updateActivity(area, listOfMembers, roleList)
            sendLog("Activity updated on: "+ area)
        else:
            sendLog(area+": Closed from google sheet")
            self.looper.cancel()
            
    @looper.after_loop
    async def on_looper_cancel(self):
        if self.looper.is_being_cancelled and l



