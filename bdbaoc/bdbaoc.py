#core redbot/discord stuff
from redbot.core import commands
from discord.ext import tasks
import discord

#######################
####rootooo stuff####
#######################
import os
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")
# chrome_options.headless = True # also works

from discord import Webhook, RequestsWebhookAdapter

############################################

from dotenv import load_dotenv #Use to load secrets. Like webhook URL etc.

#Conect to Database
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(ROOT_DIR, '.env')
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(ROOT_DIR, 'client2.json'), scope)
client = gspread.authorize(creds)
sheetName = 'BDB AoC Member Check'
Website = 'https://ashesofcreation.com/sign-up'

load_dotenv(dotenv_path) #loads secrets from .env file in root.
roowebhookurl = os.environ.get('rooWebHook')
BDBLOGGERURL = os.environ.get('BDBLOGGER')

rooWebHook = Webhook.from_url(
    str(roowebhookurl),
    adapter=RequestsWebhookAdapter())
BDBLOGGER = Webhook.from_url(
    str(BDBLOGGERURL), 
    adapter=RequestsWebhookAdapter())

def sendError(Emsg):
    rooWebHook.send(Emsg)
    BDBLOGGER.send(Emsg)


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
        await ctx.send(f"ctx.author {ctx.author}")
        await ctx.send(f"roowebhookurl:{roowebhookurl}")
        await ctx.send(f"BDBLOGGERURL:{BDBLOGGERURL}")
        await ctx.send(f"dotenvpath: {dotenv_path}")


    @commands.command()
    async def rootdir(self, ctx):
        await ctx.send(f"ROOT_DIR is: {ROOT_DIR}")

    async def checkCode(self, code):
        driver = webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)
        driver.implicitly_wait(10)
        driver.get(Website)
        driver.find_element(By.XPATH, "/html/body/aoc-web-root/aoc-web-sign-up-form/div/div[3]/form/div[7]/div/aoc-web-form-field-input-wrap/div/input").send_keys(code)
        time.sleep(2)
        driver.find_element(By.XPATH, "/html/body/aoc-web-root/aoc-web-sign-up-form/div/div[3]/form/div[7]/div/span/aoc-web-button-wrap/div/div/div").click()

        try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Code applied')]")
            driver.close()
            return True
        except:
            driver.close()
            return False

    @commands.command()
    async def requestCode(self, ctx, code):
        notInSheet = True
        #What Geno needs to get
        discordID = str(ctx.author.id)
        discordUsername = str(ctx.author)
        if discordID == "333347542727262210":
            await ctx.author.send("Dot fuck off you greedy fuck.")

        refSheet = client.open('BDB AoC Member Check').worksheet("Referrals ").get_all_values()

        for x in refSheet:
            if discordID in x:
                notInSheet = False
        if notInSheet:
            if 'Awaiting Hand Out' in refSheet[-1]:
                writeToSheet = client.open('BDB AoC Member Check').worksheet("Referrals ")
                #OutPutToUser
                outMessage = "https://ashesofcreation.com/sign-up/r/" + str(refSheet[-1][2])

                await ctx.author.send(outMessage)

                update = []
                update.append({'range': 'D' + str(len(refSheet)) + ':' + 'D' + str(len(refSheet)), "values": [[discordUsername]]})
                update.append({'range': 'A' + str(len(refSheet) + 1) + ':' + 'B' + str(len(refSheet) + 1), "values": [[discordUsername, discordID]]})
                writeToSheet.batch_update(update)
                update.clear()
                codeValidated = False
                allCodesOnSheet = writeToSheet.col_values(3)
                loopCount = 0
                maxAllowLoopCount = 15
                #Ask User for generated ref code
                while codeValidated == False:
                    if loopCount < maxAllowLoopCount:
                        #await ctx.author.send("Please type in your generated code")
                        #code = input()
                        if code not in allCodesOnSheet:
                            if await self.checkCode(code) == True:
                                await ctx.author.send("Code Validated")
                                codeValidated = True
                                update2 = []
                                update2.append({'range': 'C' + str(len(refSheet) + 1) + ':' + 'D' + str(len(refSheet) + 1),"values": [[code, "Awaiting Hand Out"]]})
                                writeToSheet.batch_update(update2)
                                update2.clear()
                            else:
                                codeValidated = False
                                await ctx.author.send("Code Invalid")
                        else:
                            await ctx.author.send("Code already in use")
                        codeValidated = True
                    else:
                        sendError("User has maxed out loops")
                        print("Too many tries")
            else:
                apologyMessage = "Sorry no codes available currently waiting for " + refSheet[-1][0] + " to provide their code. If this continues to be a problem please contact an officer."
                await ctx.author.send(apologyMessage)
        else:
            for a, userID in enumerate(refSheet):
                if userID[1] == discordID:
                    #OutPutUser
                    await ctx.author.send(a)
                    message = "You've already been assigned a code. You're code has come frome " + refSheet[a-1][0] +", if you have an issue with this please contact an officer. Here is your code: \n" + refSheet[a-1][2]
                    await ctx.author.send(message)

        #BlockSecondDiscordRef
        #Spit Out Old One