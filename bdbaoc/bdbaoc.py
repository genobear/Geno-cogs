#core redbot/discord stuff
from redbot.core import commands
from redbot.core.utils.predicates import MessagePredicate
from discord.ext import tasks
import discord
import asyncio


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
#geno shit
from dotenv import load_dotenv #Use to load secrets. Like webhook URL etc.
from .embeds import scan_embed

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

async def sendError(Emsg):
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
        driver.implicitly_wait(20)
        driver.get(Website)
        driver.find_element(By.XPATH, "/html/body/aoc-web-root/aoc-web-sign-up-form/div/div[3]/form/div[7]/div/aoc-web-form-field-input-wrap/div/input").send_keys(code)
        time.sleep(4)
        driver.find_element(By.XPATH, "/html/body/aoc-web-root/aoc-web-sign-up-form/div/div[3]/form/div[7]/div/span/aoc-web-button-wrap/div/div/div").click()

        try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Code applied')]")
            driver.close()
            return True
        except:
            driver.close()
            return False

    @commands.command()
    async def scan(self, ctx, *, member: discord.Member):
        """This does stuff!"""
        # Your code will go here
        foundon = None
        joinedat = None
        usernames = None
        nicks = None
        sheet = client.open('BDB AoC Member Check').worksheet("New User Data List")
        sheetDetails = sheet.get_all_values()
        IDColumn = sheet.col_values(2)
        if str(member.id) in IDColumn:
            resultfound = True
            for a in sheetDetails:
                if a[1] == str(member.id):
                    foundon=a[2]
                    joinedat=a[3]
                    usernames=a[5]
                    nicks=a[7]
                    embed = await scan_embed(member,resultfound,foundon,joinedat,usernames,nicks)
        else:
            resultfound = False
            embed = await scan_embed(member,resultfound,foundon,joinedat,usernames,nicks)
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
            """This does stuff on member join!"""
            server = member.guild
            if server == None:
                await sendError("Server is None. Private Message or some new fangled Discord thing?.. Anyways there be an error, the user was {}".format(member.name))
                return
            foundon = None
            joinedat = None
            usernames = None
            nicks = None
            sheet = client.open('BDB AoC Member Check').worksheet("New User Data List")
            sheetDetails = sheet.get_all_values()
            IDColumn = sheet.col_values(2)
            if str(member.id) in IDColumn:
                resultfound = True
                for a in sheetDetails:
                    if a[1] == str(member.id):
                        foundon=a[2]
                        joinedat=a[3]
                        usernames=a[5]
                        nicks=a[7]
                        embed = await scan_embed(member,resultfound,foundon,joinedat,usernames,nicks)
            else:
                resultfound = False
                embed = await scan_embed(member,resultfound,foundon,joinedat,usernames,nicks)
            channel = server.get_channel(1002630843438739553)#welcome=740319045320048784  genotests=751900786862194798  scanner=1002630843438739553       
            if channel is None:
                await sendError('bdbaoc.py: Channel not found. It was most likely deleted. User joined: {}'.format(member.name))
                return
            await channel.send(embed=embed)
            
            #await channel.message.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        seriarole = 949444637481926716
        sianrole = 949444808806653962
        madnickrole = 949444850770661408
        mokamokarole = 949444915987886141
        weirole = 949444982958333952
        kaysarrrole = 953689778413518890
        tharrole = 977824460306513921
        legendary = 949444728158572584
        epic = 949444553654534184

        card = None
        gift = None
           
        if message.author == self.bot.user:
            return
        if message.embeds:
            for embed in message.embeds:
                description = embed.description
                if 'Gift: 🟣 Epic' in description:
                    gift = epic
                elif 'Gift: 🟠 Legendary' in description:
                    gift = legendary
                if 'Card: Seria' in description:
                    card = seriarole
                elif 'Card: Sian' in description:
                    card = sianrole
                elif 'Card: Madnick' in description:
                    card = madnickrole
                elif 'Card: Mokamoka' in description:
                    card = mokamokarole
                elif 'Card: Wei' in description:
                    card = weirole            
                elif 'Card: Kaysarr' in description:
                    card = kaysarrrole
                elif 'Card: Thar' in description:
                    card =  tharrole

                if gift == None and card == None:
                    return
                # await message.channel.send(message.embeds[0].description)
                if card == None:
                    await message.channel.send(f"<@&{gift}>")
                else:
                    await message.channel.send(f"<@&{card}><@&{gift}>")
        else:
            return

    @commands.command()
    async def embedtest(self, ctx):
        embed = discord.Embed(
            title="Scan Results",
            url="https://docs.google.com/spreadsheets/d/1hph6Xpfp9zngJBMzi24MChRK5Alz5Qt4Uz1nQ8L_m84/edit#gid=0",
            description="This is an embed that will show how to build an embed and the different components",
            color=discord.Color.random())
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/839574978088796210/296b1a22e987d97431902d0e1db2bae2.png")
        embed.add_field(name="Servers Found on:", value=f"Found on Value", inline="True")
        embed.add_field(name="Joined at:", value=f"Joined at Value", inline="True")
        embed.add_field(name="Known Usernames:", value=f"Known Usernames Value", inline="False")
        embed.add_field(name="Known Nicknames:", value=f"Known Nicknames Value", inline="True")
        embed.set_footer(text="Powered by Backdoor Bandito")
        await ctx.send(embed=embed)
        
    @commands.command()
    async def getcode(self, ctx):
        await ctx.send("Check your DM's!")
        def clearLastEntry():
            refSheet = client.open('BDB AoC Member Check').worksheet("Referrals ").get_all_values()
            writeToSheet = client.open('BDB AoC Member Check').worksheet("Referrals ")
            update = []
            update.append(
                {'range': 'A' + str(len(refSheet)) + ':' + 'D' + str(len(refSheet)), "values": [["", "", "", ""]]})
            update.append({'range': 'D' + str(len(refSheet) - 1) + ':' + 'D' + str(len(refSheet) - 1),
                           "values": [["Awaiting Hand Out"]]})
            writeToSheet.batch_update(update)
            update.clear()

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
                await ctx.author.send(
                    f"""**PART 1**
1. Follow the link to create an account({outMessage})
2. Make sure the given referal code is applied
3. Sign up and wait for the success popup
**PART2**
After you have created your account
1. To get your code https://ashesofcreation.com/settings/referrals
2. Click generate referral code
3. Wait for a new box to pup up with your code. BE PATIENT, this can take a while"""
                    )

                update = []
                update.append({'range': 'D' + str(len(refSheet)) + ':' + 'D' + str(len(refSheet)), "values": [[discordUsername]]})
                update.append({'range': 'A' + str(len(refSheet) + 1) + ':' + 'B' + str(len(refSheet) + 1), "values": [[discordUsername, discordID]]})
                writeToSheet.batch_update(update)
                update.clear()
                codeValidated = False
                allCodesOnSheet = writeToSheet.col_values(3)
                loopCount = 0
                maxAllowLoopCount = 3
                #Ask User for generated ref code
                while codeValidated == False:
                    if loopCount < maxAllowLoopCount:
                        await ctx.author.send("Please type in your generated code, you have 5 minutes.")
                        
                        authorid = str(ctx.author.id)
                        def check(m):                                                   
                            return  str(m.author.id) == authorid
                            
                        try:    
                            code = await self.bot.wait_for("message", check=check, timeout=300.0)
                        except asyncio.TimeoutError:
                            await ctx.author.send("Timeout, use command again!")
                            clearLastEntry()
                            return                            
                        else:
                            await ctx.author.send("Checking code...")
                            code = code.content

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
                                    loopCount = loopCount + 1
                                    await ctx.author.send("Code Invalid")
                            else:
                                await ctx.author.send("Code already in use")
                    else:
                        codeValidated = True
                        sendError("User has maxed out loops")
                        clearLastEntry()
                        await ctx.author.send("Too many tries")
            else:
                apologyMessage = "Sorry no codes available currently waiting for " + refSheet[-1][0] + " to provide their code. If this continues to be a problem please contact an officer."
                await ctx.author.send(apologyMessage)
        else:
            for a, userID in enumerate(refSheet):
                if userID[1] == discordID:
                    #OutPutUser
                    message = "You've already been assigned a code. You're code has come frome " + refSheet[a-1][0] +", if you have an issue with this please contact an officer. Here is your code: \n" + refSheet[a-1][2]
                    await ctx.author.send(message)