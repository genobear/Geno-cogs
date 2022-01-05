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
    str_list = list(filter(None, sheet.col_values(2)))
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
        
        listOfMembers = []

        #Gather member list from target voice channel
        for member in target_voice_channel.members:
            listOfMembers.append(member.display_name)
        
        #add to google sheet
        worksheet1 = client2.open("BDB Push Attendance").worksheet('Template')
        worksheet1.duplicate(new_sheet_name=area)
        worksheet = client2.open("BDB Push Attendance").worksheet(area)
        worksheet.update('D2', str(datetime.now().strftime("%d-%m-%Y, %H:%M:%S")))
        worksheet.update('C1', area)
        next_row = next_available_row(worksheet)
        update = []
        x = next_row
        j = 0
        for member in listOfMembers:
            if j < 1000:
                try:
                    update.append({'range': 'C' + str(x) + ':' + 'F' + str(x), "values": [[member,str(datetime.now().strftime("%H:%M:%S")) ,]]})
                    x = x + 1
                    j = j + 1
                except Exception as e:
                    #sendLog("Problem with writing user details, contact Rootoo2")
                    await ctx.send("error")
            else:
                worksheet.batch_update(update)
                update.clear()
                j = 0

        worksheet.batch_update(update)
        await ctx.send("Activity check started for" + area)
    
    @commands.command()
    async def updateactivity(self, ctx, target_voice_channel: discord.VoiceChannel, area):
        """Start attendance check from <target_voice_channel> to Google Sheet.
        Use the <area> name to set the sheet name."""

        listOfMembers = []

        worksheet = client2.open("BDB Push Attendance").worksheet(area)
        next_row = next_available_row(worksheet)
        update = []
        usersOnSheet = worksheet.col_values(3)
        usersOnSheet1 = usersOnSheet[3:]
        
        await ctx.send(usersOnSheet1)

        x = next_row
        j = 0
        allDetails = worksheet.get_all_values()
        for member in listOfMembers:
            if j < 1000:
                if member not in usersOnSheet1:
                    try:
                        update.append({'range': 'C' + str(x) + ':' + 'F' + str(x),
                                    "values": [[member, str(datetime.now().strftime("%d-%m-%Y, %H:%M:%S")), ]]})
                        x = x + 1
                        j = j + 1
                    except Exception as e:
                        # sendLog("Problem with writing user details, contact Rootoo2")
                        await ctx.send("error")
                else:
                    yPosition = 1
                    a = 0
                    for user in usersOnSheet:
                        if user == member:
                            if allDetails[a][4] == "":
                                memberName = allDetails[a][2]
                                clockIn = allDetails[a][3]
                                clockOut = str(datetime.now().strftime("%H:%M:%S"))
                                update.append({'range': 'C' + str(yPosition) + ':' + 'F' + str(yPosition),"values": [[memberName, clockIn,clockOut ]]})
                                j = j + 1
                                break
                            else:
                                memberName = allDetails[a][2]
                                clockIn = allDetails[a][3]
                                clockOut = allDetails[a][4]
                                notes = allDetails[a][5]
                                if notes == "Pushed a second time":
                                    update.append({'range': 'C' + str(yPosition) + ':' + 'F' + str(yPosition),
                                                "values": [[memberName, clockIn, clockOut, "Pushed multiple times"]]})
                                    j = j + 1
                                    break
                                else:
                                    if notes == "Pushed multiple times":
                                        break
                                    update.append({'range': 'C' + str(yPosition) + ':' + 'F' + str(yPosition),"values": [[memberName, clockIn, clockOut, "Pushed a second time"]]})
                                    j = j + 1
                                    break
                        else:
                            a = a + 1
                            yPosition = yPosition + 1

            else:
                worksheet.batch_update(update)
                update.clear()
                j = 0

        worksheet.batch_update(update)
        await ctx.send(listOfMembers)
        await ctx.send("Activity updated for" + area)
       
    @commands.command()
    async def role_members(self, ctx, role: discord.Role):
        """Get list of members that has provided role"""
        memberslist = []
        for member in role.members:
            memberslist.append(member.display_name)
        response = '```' +(tabulate(memberslist, tablefmt="orgtbl", headers=[("DisplayName"), ("Name")])) + '```'
        await ctx.send(response)
