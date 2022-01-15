from redbot.core import commands
from discord.ext import tasks
import discord
from discord import Webhook, RequestsWebhookAdapter

#requirements for googlsheet integration
import os
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient import discovery
import logging
import io
from tabulate import tabulate
from datetime import datetime
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient import errors
from googleapiclient import http

import time
from dotenv import load_dotenv


def listfolders(client, filid, des):
    results = client.files().list(
        pageSize=1000, q="\'" + filid + "\'" + " in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    # logging.debug(folder)
    folder = results.get('files', [])
    for item in folder:
        if str(item['mimeType']) == str('application/vnd.google-apps.folder'):
            if not os.path.isdir(des+"/"+item['name']):
                os.mkdir(path=des+"/"+item['name'])
            print(item['name'])
            listfolders(client, item['id'], des+"/"+item['name'])  # LOOP un-till the files are found
        else:
            downloadfiles(client, item['id'], item['name'], des)
            print(item['name'])
    return folder


# To Download Files
def downloadfiles(client, dowid, name,dfilespath):
    request = client.files().get_media(fileId=dowid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(dfilespath + "/" + name, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())




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




load_dotenv()
url1 = os.environ.get('webhookurl')
url2 = os.environ.get('logWebHookurl')
#webhooks for logs
webhook = Webhook.from_url(str(url1), adapter=RequestsWebhookAdapter())
logWebHook = Webhook.from_url(str(url2), adapter=RequestsWebhookAdapter())

def sendLog(msg):
    logWebHook.send(msg)
    webhook.send(msg)

def sendLog_debug(msg):
    logWebHook.send(msg)
    #webhook.send(msg)


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
        listMemberCorrection.append(str(corrected[1])[1:])
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
                memberName = str(member).replace(str(z) + ": ","")
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
    spreadsheet = client.open('BDB Push Attendance')
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
            memberName = str(member).replace(str(z)+": ","")
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
    body = {
    "requests": [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": worksheet.id,
                        "tabColor": {
                            "red": 0.0,
                            "green": 1.0,
                            "blue": 0.0
                        }
                    },
                    "fields": "tabColor"
                }
            }
        ]
    }
    spreadsheet.batch_update(body)
    sendLog("Activity populated: " + area + ": https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))



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
    async def memberlist(self, ctx, role: discord.Role):
        "Get a list of users in a vocie channel"
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
    async def list_test(self, ctx, target_voice_channel: discord.VoiceChannel, area):
        """Start attendance check from <target_voice_channel> to Google Sheet.
        Use the <area> name to set the sheet name."""

        #Gather member list from target voice channel
        x = 0
        listOfMembersID = []
        listOfMembers = []
        listofroles = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                listofroles.append(str(x) + str(role.name))
            x = x + 1
        x = 0    
        for memberid in target_voice_channel.members:
            listOfMembersID.append(str(x) + ": " + str(member.id))
            x = x + 1

        await ctx.send(listOfMembers)
        await ctx.send(listofroles)
        await ctx.send(listofroles)
        
        
    @commands.command()
    async def start_activity(self,ctx,target_voice_channel: discord.VoiceChannel, area):
        """Start attendance check from <target_voice_channel> to Google Sheet.

        Use the <area> name to set the sheet name.
        The name is case sensitve, and you must surround and spaces in quotation marks
        
        Activity will be automatically updated every 10 minutes. 
        
        Use ?end_activity to end the activity
        
        Only 1 activity can be tracked at a time"""
        
        #Gather member list from target voice channel
        x = 0
        listOfMembers = []
        roleList = []
        for member in target_voice_channel.members:
            listOfMembers.append(str(x) +": " + str(member.display_name))
            for role in member.roles:
                roleList.append(str(x) + str(role.name))
            x = x + 1
        
        populate(area, listOfMembers, roleList)
        self.looper.start(area,target_voice_channel)
        
        await ctx.send("Activity tracking started for: "+area)
        
    @commands.command()
    async def pause_activity(self, ctx):
        """Stop updating shortcut. This will not close the activity on sheets. 
        
        Useful if you want to move the activity to a different voice channel
        
        After pause_updating is ran you can then ?resume_activity"""
        self.looper.cancel()
        sendLog("Activity updates paused")
        await ctx.send("Stopped any actvitiy updates.")
        
    @commands.command()
    async def resume_activity(self, ctx,target_voice_channel: discord.VoiceChannel, area):
        """Only useful to start updating an existing activity wich has been stopped with "?pause_activity" """
        #Get sheet data
        spreadsheet = client2.open('BDB Push Attendance')
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
    
        self.looper.start(area,target_voice_channel)
        sendLog("Activity resumed: " + area + ": https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
        await ctx.send("Updating resumed: " + area +" Voice Channel: " + str(target_voice_channel) +'(' + str(target_voice_channel.id) +')')
        
    
        
    @commands.command()
    async def end_activity(self,ctx,area):
        """End attendance check on <area>"""
        spreadsheet = client2.open('BDB Push Attendance')
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
        worksheet.update_title(str(area) + str(datetime.now().strftime("%d-%m-%Y")) + "(Closed)")
        body = {
        "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": worksheet.id,
                            "tabColor": {
                                "red": 1.0,
                                "green": 0.0,
                                "blue": 0.0
                            }
                        },
                        "fields": "tabColor"
                    }
                }
            ]
        }
        spreadsheet.batch_update(body)
        sendLog("Activity ended: " + area + ": https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
        await ctx.send("Activity ended: " + str(worksheet.url))
        
    @tasks.loop(seconds=300.0)
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
        spreadsheet = client2.open('BDB Push Attendance')
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
        status = worksheet.acell('K2').value
        if status == "Open":
            updateActivity(area, listOfMembers, roleList)
            sendLog_debug(area +" updated: " +  "https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
        else:
            sendLog(area + " closed from Google Sheet: " + "https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
            self.looper.cancel()
            
    @commands.command()
    async def warstats(self, ctx, file_types=("jpeg","png")):
        if not ctx.message.attachments:
            await ctx.send("Try again with attachment")        
        attachments = ctx.message.attachments
        for attachment in attachments:
            await ctx.send(attachment)
        await ctx.message.delete()

    @commands.command()
    async def tradepost(self, ctx):
        service = build('drive', 'v3', credentials=creds)
        Folder_id = "'1VFKzwum9X1j7BrLJCCfjZ_2bCIZHPplY'"  # Enter The Downloadable folder ID From Shared Link

        results = service.files().list(
            pageSize=1000, q=Folder_id+" in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    if not os.path.isdir("Folder"):
                        os.mkdir("Folder")
                    bfolderpath = os.getcwd()+"/Folder/"
                    if not os.path.isdir(bfolderpath+item['name']):
                        os.mkdir(bfolderpath+item['name'])

                    folderpath = bfolderpath+item['name']
                    listfolders(service, item['id'], folderpath)
                else:
                    if not os.path.isdir("Folder"):
                        os.mkdir("Folder")
                    bfolderpath = os.getcwd()+"/Folder/"
                    if not os.path.isdir(bfolderpath + item['name']):
                        os.mkdir(bfolderpath + item['name'])

                    filepath = bfolderpath + item['name']
                    downloadfiles(service, item['id'], item['name'], filepath)
        files = glob.glob('/home/genobear90/Folder/*')
        #for filename in os.listdir('/home/genobear90/Folder'):
        for filename in files:
            await ctx.send(file=discord.File(filename))
            await os.remove(filename)
        
        #os.removedirs('/home/genobear90/Folder/')

        await ctx.send("ok")
