from collections import UserString
from redbot.core import commands
from discord.ext import tasks
import discord
from discord import Webhook, RequestsWebhookAdapter

#requirements for googlsheet integration
import os, sys
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
import re

import time
from dotenv import load_dotenv

import cv2
import pytesseract
import string

import time
from datetime import datetime, date, time, timedelta

from discord.utils import get

import pickle

from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import MessagePredicate, ReactionPredicate
import asyncio
import contextlib
from PIL import Image

import numpy as np


#for google image folders and loukans tradepost pictures
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


# To Download Files from google drive
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



#for gsheet client.json
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CSVFile = os.path.join(ROOT_DIR, 'CSV Files/')

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



#secretly load webhook
load_dotenv()
webhookurl = os.environ.get('webhookurl')
logWebHookurl = os.environ.get('logWebHookurl')
rooWebHookCriticalurl = os.environ.get('rooWebHookCriticalurl')
rooNonWebHookCriturl = os.environ.get('rooNonWebHookCriturl')
#webhooks for logs
webhook = Webhook.from_url(str(webhookurl), adapter=RequestsWebhookAdapter())
logWebHook = Webhook.from_url(str(logWebHookurl), adapter=RequestsWebhookAdapter())
rooWebHookCritical = Webhook.from_url(str(rooWebHookCriticalurl), adapter=RequestsWebhookAdapter())
rooNonWebHookCrit = Webhook.from_url(str(rooNonWebHookCriturl), adapter=RequestsWebhookAdapter())

#Send detailed log - Complete
def sendLog(Urgency, Status,Value,Line, Area,Comment):
    msg = "Time of Log = " + str(datetime.now().strftime("%H:%M:%S")) + "\n" + "Urgency = " + Urgency + "\n" + "Error Code / Name of Log = " + str(Status) + "\n" +"Line = " + str(Line) + "\n" + "Value = " + str(Value) + "\n" + "Area = " + str(Area) + "\n" +"Comment = " + Comment

    if Urgency == "Critical":
        rooWebHookCritical.send(msg)
    if Urgency == "Warning":
        rooNonWebHookCrit.send(msg)
    if Urgency == "Update":
        rooNonWebHookCrit.send(msg)
    
    logWebHook.send(msg)
    #webhook.send(msg)

def sendLog_debug(msg):
    logWebHook.send(msg)
    #webhook.send(msg)

#Gets all roles - Need to get roleList and userList from bot
def getAllRoles(placeInList, users, roleList):
    def getRole(numerInList):
        userRoles = []
        for roles in roleList:
            roles = roles.split(":")
            if str(numerInList) == roles[0]:
                userRoles.append(str(roles[1]))
        return userRoles
    def getInGameRole(userRoles):
        for positions in allInGameRoles:
            if positions in userRoles:
                inGameRole = positions
                return inGameRole
    def getInDiscordRole(userRoles):
        for status in allDiscordRoles:
            if status in userRoles:
                discordRole = status
                return discordRole
    def getWeapons(userRoles, Wep1):
        weaponCount = 0
        for weapons in allInGameWeapons:
            if weapons in userRoles:
                if Wep1 == "":
                    Wep1 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
                    return Wep1
                else:
                    if Wep1 not in weapons:
                        Wep2 = str(weapons).replace(allInGameWeaponsCorrections[weaponCount], "")
                        return Wep2
            weaponCount = weaponCount + 1
    def getDiscordName(placeInList):
        for names in users:
            if placeInList == str(names).split(":")[0]:
                return str(names).split(":")[1]

    userRoles = getRole(placeInList)
    inGameRole = getInGameRole(userRoles)
    discordRole = getInDiscordRole(userRoles)
    Wep1 = getWeapons(userRoles, "")
    Wep2 = getWeapons(userRoles, Wep1)
    discordName = getDiscordName(placeInList)

    return [inGameRole,discordRole ,Wep1,Wep2,discordName]

#genuinely cant remember if this is used
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

#Next Avail Row - Complete
def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(8)))
    return int(len(str_list) + 1)

def updateVersionNumber(globalSheet):
    allData = globalSheet.get_all_values()
    currentBuild = allData[9][1]
    previousBuild = currentBuild
    newCurrentBuild = float(currentBuild) + 0.01
    globalSheet.update('B10', newCurrentBuild)
    globalSheet.update('B14', previousBuild)

def updateActivity(area, idList, users, roleList):
    worksheet = client.open("BDB Push Attendance").worksheet(area)
    next_row = next_available_row(worksheet)
    usersOnSheet = worksheet.col_values(3)
    discordIDOnSheet = usersOnSheet[7:]
    z = 0
    x = next_row + 1
    j = 0
    allDetails = worksheet.get_all_values()
    idListCorrection = [i.split(":")[1] for i in idList]
    update = []
    for discordID in idList:
        removeNumber = str(discordID).split(":")
        discordID = removeNumber[1]
        if j < 1000:
            if discordID not in discordIDOnSheet:  # If memberID not in sheet add them and their roles
                roles = getAllRoles(removeNumber[0], users, roleList)
                inGameRole = roles[0]
                discordRole = roles[1]
                Wep1 = roles[2]
                Wep2 = roles[3]
                memberName = roles[4]
                try:
                    update.append({'range': 'C' + str(x) + ':' + 'K' + str(x),
                                   "values": [[discordID,inGameRole, Wep1, Wep2, discordRole, memberName,
                                               str(datetime.now().strftime("%H:%M:%S")), ]]})
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
            j = 0  #
    yPosition = 8
    a = 7
    j = 0
    for user in discordIDOnSheet:  # For users on sheet
        if user not in idListCorrection:  # if user is not in dicord channel
            if allDetails[a][9] == "":  # They dont have a clock out time
                memberName = allDetails[a][7]
                clockIn = allDetails[a][8]
                clockOut = str(datetime.now().strftime("%H:%M:%S"))
                update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                               "values": [[memberName, clockIn, clockOut]]})  # Clock them out
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
        else:  # If they are in the channel
            if allDetails[a][9] != "":  # They do have a clock out time
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
    

def populate(name, users, roleList, idList): # needs idlist passing from start activity command
    spreadsheet = client.open('BDB Push Attendance')
    worksheet1 = client.open("BDB Push Attendance").worksheet("Template 2") #Opens Sheet for reading
    worksheet1.duplicate(new_sheet_name=name) #Duplicates sheet from template
    worksheet = client.open("BDB Push Attendance").worksheet(name) #Opens new duplicated sheet
    worksheet.update('G4', str(datetime.now().strftime("%H:%M:%S"))) #Populate time
    worksheet.update('E4', str(datetime.now().strftime("%d-%m-%Y"))) #Populate time
    worksheet.update('D2', name) #populates area
    worksheet.update('K2', "Open") #Populates sheet status
    next_row = next_available_row(worksheet) #Calculates next row
    update = [] #Update array
    x = next_row + 1 #x variable for row
    j = 0 #j variable for max amount of updates in single batch
    z = 0 #z variable for gettings roles from list
    for memberID in idList:
        removeNumber = str(memberID).split(":")
        discordID = removeNumber[1]
        roles = getAllRoles(removeNumber[0], users, roleList) #needs to pass rolelist userlist
        inGameRole = roles[0]
        discordRole = roles[1]
        Wep1 = roles[2]
        Wep2 = roles[3]
        memberName = roles[4]
        if j < 1000:
            try:
                update.append({'range': 'C' + str(x) + ':' + 'K' + str(x), "values": [[discordID,inGameRole,Wep1,Wep2,discordRole,memberName,str(datetime.now().strftime("%H:%M:%S"))]]})
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
                        #"hidden" : False,
                        "tabColor": {
                            "red": 0.0,
                            "green": 1.0,
                            "blue": 0.0
                        }
                    },
                    "fields": "tabColor",
                    #"fields": "hidden"
                }
            }
        ]
    }
    spreadsheet.batch_update(body)
    sendLog_debug("Activity populated: " + name + ": https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))


def getName(img):
    image = cv2.imread(convetImageRGB(img))
    # Edit for accuracy (Image read)
    thresh = cv2.threshold(image, 165, 255, cv2.THRESH_BINARY)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
    imgStats = 255 - close
    y = 0
    x = 0
    h = 700
    w = 250
    crop = imgStats[y:y + h, x:x + w]
    crop = cv2.resize(crop, None, fx=1.5, fy=1.5)
    nameOffImage = str(pytesseract.image_to_string(crop, config='--psm 6 --oem 3')).split("\n")
    nameOffImage = list(filter(None, nameOffImage))
    return nameOffImage

#Corrects war stat row data - Complete
def rowCorrection(rowData, nameOffImage):
    with open(f'{ROOT_DIR}/zeroCorrectionList', 'rb') as fp:
        zeroCorrectionList = pickle.load(fp)
    with open(f'{ROOT_DIR}/correctName', 'rb') as fp:
        nameCorrectionList = pickle.load(fp)
    with open(f'{ROOT_DIR}/incorrectName', 'rb') as fp:
        nameIncorrectionList = pickle.load(fp)
    def nameCorrection(name):
        if name:
            if name in nameIncorrectionList:
                for a, names in enumerate(nameIncorrectionList):
                    if names == name:
                        name = nameCorrectionList[a]
                        return name
            else:
                return name
        else:
            return None
    try:
        imgErrorCorrection = rowData.split()# Splits data by comma
        for a, entry in enumerate(imgErrorCorrection):
            if entry in zeroCorrectionList:
                imgErrorCorrection[a] = "0"
        # # Cross refrence numbers
        # if imgErrorCorrection[0] in name:
        #     del imgErrorCorrection[0]
        #sendLog("Warning", imgErrorCorrection, "", "", "", "")
        for b, word in enumerate(imgErrorCorrection):
            for letter in word:
                if letter in string.punctuation:
                    imgErrorCorrection[b] = imgErrorCorrection[b].replace(letter, "")
                    sendLog("Check for consistency", "232", word, "Punctuation removal",
                            "if this was a zero add value to zeroCorrectionList using function", "")
        for c, word in enumerate(imgErrorCorrection):
            if word.isdecimal() == False:
                imgErrorCorrection[c] = re.sub("[^0-9]", "", word)
                if imgErrorCorrection[c].isdecimal() == False:
                    del imgErrorCorrection[c]
                    sendLog("Warning", "Deleting Row Data", word, "246", "Row Data Correction","Ensure this was meant to be deleted")
        imgErrorCorrection = list(filter(None, imgErrorCorrection))

        for k, stuff in enumerate(nameOffImage):
            for l, data in enumerate(stuff.split()):
                if data.isdecimal():
                    if data in imgErrorCorrection:
                        name = ", ".join(stuff.split()[:l])
                        name = nameCorrection(name)
                        imgErrorCorrection.insert(0, name.replace(",", ""))
                        break
        if len(imgErrorCorrection) < 7:
            sendLog("Critical", "N/A", rowData, imgErrorCorrection, nameOffImage,
                    "Some fucky shit in row correction")
            print(imgErrorCorrection)
            print(nameOffImage)
            return None

        return imgErrorCorrection
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sendLog("Critical",e,imgErrorCorrection, (exc_type, fname, exc_tb.tb_lineno), "Row Correction","Some fucky shit in row correction")


def convetImageRGB(img):
    filname = "conversion.png"
    col = Image.open(img)
    gray = col.convert('L')
    # Let numpy do the heavy lifting for converting pixels to pure black or white
    bw = np.asarray(gray).copy()
    # Pixel range is 0...255, 256/2 = 128
    bw[bw < 128] = 0  # Black
    bw[bw >= 128] = 255  # White
    # Now we put it back in Pillow/PIL land
    imfile = Image.fromarray(bw)
    imfile.save(f"{ROOT_DIR}/conversion/" + str(filname))
    path = f"{ROOT_DIR}/conversion/" + filname
    return path
#getsImageData
def imgProcession(img):
    with open(f'{ROOT_DIR}/zeroCorrectionList', 'rb') as fp:
        zeroCorrectionList = pickle.load(fp)

    def processImage(crop):
        nameOffImage = str(pytesseract.image_to_string(crop, config='--psm 6')).split("\n")
        nameOffImage = list(filter(None, nameOffImage))
        if '\x0c' in nameOffImage:
            nameOffImage.remove('\x0c')

        if all(i.isdecimal() for i in nameOffImage):
            return nameOffImage
        else:
            for a, data in enumerate(nameOffImage):
                logWebHook.send(a)
                logWebHook.send(data)
                if data.isdecimal() == False:
                    for character in data:
                        if character.isdecimal() == False:
                            data[a].replace(character, "")
            return nameOffImage
    def getName(img):
        image = cv2.imread(convetImageRGB(img))
        # Edit for accuracy (Image read)
        thresh = cv2.threshold(image, 165, 255, cv2.THRESH_BINARY)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        close = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
        imgStats = 255 - close
        y = 0
        x = 0
        h = 700
        w = 250
        crop = imgStats[y:y + h, x:x + w]
        crop = cv2.resize(crop, None, fx=1.5, fy=1.5)
        nameOffImage = str(pytesseract.image_to_string(crop, config='--psm 6 --oem 3')).split("\n")
        nameOffImage = list(filter(None, nameOffImage))
        if '\x0c' in nameOffImage:
            nameOffImage.remove('\x0c')
        return nameOffImage

    def getDataOffImage(img, y, x, h, w, numberOffNames, printWhat):
        crop = img[y:y + h, x:x + w]
        nameOffImage = processImage(cv2.resize(crop, None, fx=1.5, fy=1.5))
        if all(i.isdecimal() for i in nameOffImage):
            return nameOffImage
        else:
            for a, data in enumerate(nameOffImage):
                if data.isdecimal() == False:
                    if data in zeroCorrectionList:
                        nameOffImage[a] = "0"
        if len(nameOffImage) < numberOffNames:
            print(printWhat)
            print(nameOffImage)
        return nameOffImage

    def CheckForNewZeros(score,kill,death,assist,heal,damage):
        if scores[0] == "Zero Correction":
            print("This needs to be added to the zero correction list =   " + str(score[1]))
            return False
        if kill[0] == "Zero Correction":
            print("This needs to be added to the zero correction list =   " + str(kill[1]))
            return False
        if death[0] == "Zero Correction":
            print("This needs to be added to the zero correction list =   " + str(death[1]))
            return False
        if assist[0] == "Zero Correction":
            print("This needs to be added to the zero correction list =   " + str(assist[1]))
            return False
        if heal[0] == "Zero Correction":
            print("This needs to be added to the zero correction list =   " + str(heal[1]))
            return False
        if damage[0] == "Zero Correction":
            print("This needs to be added to the zero correction list =   " + str(damage[1]))
            return False
        return True

    def convetImageRGB(img):
        filname = "conversion.png"
        col = Image.open(img)
        gray = col.convert('L')
        # Let numpy do the heavy lifting for converting pixels to pure black or white
        bw = np.asarray(gray).copy()
        # Pixel range is 0...255, 256/2 = 128
        bw[bw < 128] = 0  # Black
        bw[bw >= 128] = 255  # White
        # Now we put it back in Pillow/PIL land
        imfile = Image.fromarray(bw)
        imfile.save(f"{ROOT_DIR}/conversion/" + str(filname))
        path = f"{ROOT_DIR}/conversion/" + filname
        return path



    imgStats = cv2.imread(convetImageRGB(img))
    # Edit for accuracy (Image read)
    thresh = cv2.threshold(imgStats, 150, 255, cv2.THRESH_BINARY)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    close = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
    result = 255 - close




    names = getName(img)
    scores = getDataOffImage(result, 0, 250, 700, 125,len(names), "Getting Scores")
    kills = getDataOffImage(result, 0, 400, 700, 125,len(names), "Getting Kills")
    deaths = getDataOffImage(result, 0, 530, 700, 125, len(names),"Getting Deaths")
    assists = getDataOffImage(result, 0, 665, 700, 110,len(names), "Getting Assists")
    heals = getDataOffImage(result, 0, 730, 700, 200,len(names), "Getting Healing")
    damages = getDataOffImage(result, 0, 900, 700, 150,len(names), "Getting Damage")
    if CheckForNewZeros(scores,kills,deaths,assists,heals,damages) == True:
        fullScoreboard = []
        for a, rows in enumerate(names):
            if rows == names[a]:
                name = names[a]
                score = scores[a]
                kill = kills[a]
                death = deaths[a]
                assist = assists[a]
                heal = heals[a]
                damage = damages[a]
                userRow = [name,score,kill,death,assist,heal,damage]
                fullScoreboard.append(userRow)
        return fullScoreboard
    exit()

def updateGlobalStatWar(discordID, discordIDFromGlobal,globalAllData, score, kills,deaths, assissts, healing, damage):#NOT A COMMAND
    if discordID.isdecimal():
        if discordID in discordIDFromGlobal:
            for f, data in enumerate(discordIDFromGlobal):
                if data == discordID:
                    if globalAllData[f + 7][11] != "":
                        totalWarsGlobal = int(globalAllData[f + 7][11].replace(",", "")) + 1
                        scoreGlobal = int(globalAllData[f + 7][12].replace(",", "")) + int(score)
                        killsGlobal = int(globalAllData[f + 7][13].replace(",", "")) + int(kills)
                        deathsGlobal = int(globalAllData[f + 7][14].replace(",", "")) + int(deaths)
                        assisstsGlobal = int(globalAllData[f + 7][15].replace(",", "")) + int(assissts)
                        healingGlobal = int(globalAllData[f + 7][16].replace(",", "")) + int(healing)
                        damageGlobal = int(globalAllData[f + 7][17].replace(",", "")) + int(damage)
                        return (
                            {'range': 'L' + str(f + 8) + ':' + 'R' + str(f + 8),
                             "values": [[totalWarsGlobal, scoreGlobal, killsGlobal, deathsGlobal,
                                         assisstsGlobal, healingGlobal, damageGlobal]]})
                    else:
                        totalWarsGlobal = 1
                        scoreGlobal = score
                        killsGlobal = kills
                        deathsGlobal = deaths
                        assisstsGlobal = assissts
                        healingGlobal = healing
                        damageGlobal = damage
                        return ({'range': 'L' + str(f + 8) + ':' + 'R' + str(f + 8),
                                                  "values": [[totalWarsGlobal, scoreGlobal, killsGlobal, deathsGlobal,
                                                              assisstsGlobal, healingGlobal, damageGlobal]]})

def updateGlobalStatEvent(discordID, discordIDFromGlobal,globalAllData):#NOT A COMMAND
    if discordID.isdecimal():
        if discordID in discordIDFromGlobal:
            for f, data in enumerate(discordIDFromGlobal):
                if data == discordID:
                    if globalAllData[f + 7][10] != "":
                        totalWarsGlobal = int(globalAllData[f + 7][10].replace(",", "")) + 1

                        return (
                            {'range': 'K' + str(f + 8) + ':' + 'K' + str(f + 8),
                             "values": [[totalWarsGlobal]]})
                    else:
                        totalWarsGlobal = 1
                        return ({'range': 'K' + str(f + 8) + ':' + 'K' + str(f + 8),
                                                  "values": [[totalWarsGlobal]]})

#Static Data
allInGameWeapons = ["⛏️ Great axe", "❄️ Ice Gauntlet", "🎯 Musket", "🛡️ Sword + Shield", "❤️ Life Staff",
                                "🤺 Rapier", "🔱 Spear", "🔥 Firestaff", "🔨 War Hammer", "🪓 Hatchet",
                                "⚔️ Sword & Shield(DPS)", "🏹 Bow", "🏰 Fort Support", "🌌 Void Gauntlet"]
allInGameWeaponsCorrections = ["Great axe", "Ice Gauntlet", "Musket", "Sword + Shield", "Life Staff",
                                           "Rapier", "Spear", "Firestaff", "War Hammer", "Hatchet",
                                           "Sword & Shield(DPS)", "Bow", "Fort Support", "Void Gauntlet"]
allInGameRoles = ["DPS", "HEALER", "TANK"]
allDiscordRoles = ["⚜️","Consul", "Admin", "Officer", "Member", "Trial"]

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

def timeCalculation(clockIn, clockOut):
    def calculateTime(inClock, outClock):
        inClock.replace("\n", "")
        outClock.replace("\n", "")
        inClock = inClock.split(":")
        outClock = outClock.split(":")
        return timedelta(hours=int(outClock[0]), minutes=int(outClock[1]), seconds=int(outClock[2])) - timedelta(hours=int(inClock[0]), minutes=int(inClock[1]), seconds=int(inClock[2]))
    clockIn.replace("'", "").replace(" ", "")
    clockOut.replace("'", "").replace(" ", "")
    clockIn = clockIn.splitlines()
    clockOut = clockOut.splitlines()
    clockOut = list(filter(None, clockOut))
    clockIn = list(filter(None, clockIn))
    totalTime = []
    for a, time in enumerate(clockIn):
        rowCalculation = calculateTime(time, clockOut[a]).seconds
        totalTime.append(rowCalculation)
    finalTime = 0
    for time in totalTime:
        finalTime += time

    convertedTime = timedelta(seconds=finalTime)
    return convertedTime

def updateGlobalEventStats(discordID, time,discordIDFromGlobal, globalAllData):
    if discordID in discordIDFromGlobal:
        for f, data in enumerate(discordIDFromGlobal):
            if data == discordID:
                if globalAllData[f + 7][9].isdecimal():
                    totalEventsGlobal = int(globalAllData[f + 7][9]) + 1
                    timeToWork = globalAllData[f + 7][8]
                    timeToWork = timeToWork.replace(" day, ", ":").replace(" days, ", ":").split(":")
                    if len(timeToWork) == 3:
                        timeOffSheet = timedelta(hours=int(timeToWork[0]), minutes=int(timeToWork[1]), seconds=int(timeToWork[2])).seconds
                        finalTime = time.seconds + timeOffSheet
                        finalTime = str(timedelta(seconds=finalTime))
                        return ({'range': 'I' + str(f + 8) + ':' + 'J' + str(f + 8), "values": [[finalTime, totalEventsGlobal]]})
                    else:
                        timeOffSheet = timedelta(hours=int(timeToWork[1]), minutes=int(timeToWork[2]), seconds=int(timeToWork[3])).seconds
                        daysToSeconds = int(timeToWork[0]) * 86400
                        daysPlusTime = daysToSeconds + timeOffSheet
                        finalTime = time.seconds + daysPlusTime
                        finalTime = str(timedelta(seconds=finalTime))
                        return ({'range': 'I' + str(f + 8) + ':' + 'J' + str(f + 8),"values": [[finalTime, totalEventsGlobal]]})
                else:
                    totalEventsGlobal = 1
                    timeToBoard = str(timedelta(seconds=time.seconds))

                    return ({'range': 'I' + str(f + 8) + ':' + 'J' + str(f + 8), "values": [[timeToBoard, totalEventsGlobal]]})

hours = 0
secs = 0

#Get discord ID - Complete 
def getDiscordID(inGameName, namesFromGlobalListData, discordIDs):
    discordUsername = inGameName.replace(" ", "")
    for letter in discordUsername:
        if letter in string.punctuation:
            discordUsername = discordUsername.replace(letter, "")
    for a, name in enumerate(namesFromGlobalListData):
        name = name.replace(" ", "")
        for letter in name:
            if letter in string.punctuation:
                name = name.replace(letter, "")
        if str(name).upper() == discordUsername.upper():
            return discordIDs[a]
        if str(name).upper() in discordUsername.upper():
            return discordIDs[a]
    sendLog("Warning", "Person Not Detected In Company", inGameName, "414", "Get Discord ID Function","Person Not in company check name matches discord name")
    return "Not in company"

class bdb(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    async def updateGlobalListOfMembers(self, ctx):
        guild = ctx.guild
        role = get(guild.roles, id=926088568265388033)

        x = 0    
        roleList = []
        idList = []
        users = []
        for member in role.members:
            users.append(str(x) + ":" + str(member.display_name))
            idList.append(str(x) + ":" + str(member.id))
            for role in member.roles:
                roleList.append(str(x) + ":" + str(role.name))
            x = x + 1

        worksheet = client.open("BDB Push Attendance").worksheet("BDB Global Leaderboard")
        IDonSheet = worksheet.col_values(3)[7:]
        allValues = worksheet.get_all_values()
        positionsTaken = []

        def getPlace():
            for n, place in enumerate(IDonSheet):
                if place == "":
                    x = n + 8
                    if x not in positionsTaken:
                        positionsTaken.append(x)
                        return x
            return len(IDonSheet) + 8
        update = []
        j = 0
        for ID in idList:
            if j < 1000:
                removeNumber = str(ID).split(":")
                if str(removeNumber[1]) not in IDonSheet:
                    x = getPlace()
                    #Add them to sheet
                    discordID = removeNumber[1]
                    roles = getAllRoles(removeNumber[0], users, roleList)
                    inGameRole = roles[0]
                    discordRole = roles[1]
                    Wep1 = roles[2]
                    Wep2 = roles[3]
                    discordName = roles[4]

                    update.append({'range': 'C' + str(x) + ':' + 'H' + str(x), "values": [[discordID, inGameRole, Wep1, Wep2, discordRole,discordName]]})
                    j = j + 1
                else:
                    placeToUpdate = 8
                    for ID_on_List in IDonSheet:
                        if ID_on_List == str(removeNumber[1]):
                            roles = getAllRoles(removeNumber[0], users, roleList)
                            inGameRole = roles[0]
                            discordRole = roles[1]
                            Wep1 = roles[2]
                            Wep2 = roles[3]
                            discordName = roles[4]
                            update.append({'range': 'D' + str(placeToUpdate) + ':' + 'H' + str(placeToUpdate),"values": [[inGameRole, Wep1, Wep2, discordRole, discordName]]})
                            j = j + 1
                            placeToUpdate = placeToUpdate + 1
                        else:
                            placeToUpdate = placeToUpdate + 1
            else:
                worksheet.batch_update(update)
                update.clear()
                j = 0
        worksheet.batch_update(update)
        await ctx.send("global update")



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
        "Get a list of users in a voie channel"
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
    async def start_activity(self,ctx,target_voice_channel: discord.VoiceChannel, name):
        """Start attendance check from <target_voice_channel> to Google Sheet.

        Use the <name> to set the sheet name.
        The name is case sensitve, and you must surround and spaces in quotation marks
        
        Activity will be automatically updated every 10 minutes. 
        
        Use ?end_activity to end the activity
        
        Only 1 activity can be tracked at a time"""
        
        #Gather member list from target voice channel
        x = 0
        users = []
        roleList = []
        idList = []   

        for member in target_voice_channel.members:
            users.append(str(x) + ":" + str(member.display_name))
            idList.append(str(x) + ":" + str(member.id))
            for role in member.roles:
                roleList.append(str(x) + ":" + str(role.name))
            x = x + 1

        populate(name, users, roleList, idList)
        #populate(area, listOfMembers, roleList)
        self.looper.start(name,target_voice_channel)
        
        await ctx.send("Activity tracking started for: "+ name)
        
    @commands.command()
    async def pause_activity(self, ctx):
        """Stop updating shortcut. This will not close the activity on sheets. 
        
        Useful if you want to move the activity to a different voice channel
        
        After pause_updating is ran you can then ?resume_activity"""
        self.looper.cancel()
        sendLog_debug("Activity updates paused")
        await ctx.send("Stopped any actvitiy updates.")
        
    @commands.command()
    async def resume_activity(self, ctx,target_voice_channel: discord.VoiceChannel, area):
        """Only useful to start updating an existing activity wich has been stopped with "?pause_activity" """
        #Get sheet data
        spreadsheet = client2.open('BDB Push Attendance')
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
    
        self.looper.start(area,target_voice_channel)
        sendLog_debug("Activity resumed: " + area + ": https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
        await ctx.send("Updating resumed: " + area +" Voice Channel: " + str(target_voice_channel) +'(' + str(target_voice_channel.id) +')')
        
    
        
    @commands.command()
    async def end_activity(self,ctx,area):
        """End attendance check on <area>"""
    #def Close(area):#command
        await self.updateGlobalListOfMembers(ctx)
        spreadsheet = client2.open('BDB Push Attendance')
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
        worksheet.update('K2', "Closed")  # Populates sheet status
        worksheet.update('I4', str(datetime.now().strftime("%H:%M:%S")))
        dataFromGlobalList = client.open("BDB Push Attendance").worksheet("BDB Global Leaderboard")
        discordIDFromGlobal = dataFromGlobalList.col_values(3)[7:]
        allGlobalData = dataFromGlobalList.get_all_values()
        allDetails = worksheet.get_all_values()
        idOnSheet = worksheet.col_values(3)
        usersOnSheet1 = idOnSheet[7:]
        update = []
        updateGlobal = []
        a = 7
        j = 0
        yPosition = 8
        for user in usersOnSheet1:
            if j < 1000:
                clockIn = str(allDetails[a][8])
                clockOut = str(allDetails[a][9])
                memberName = allDetails[a][7]
                memberID = allDetails[a][2]

                if len(clockIn.splitlines()) == len(clockOut.splitlines()):
                    totalTimeAttened = timeCalculation(clockIn, clockOut)
                    update.append({'range': 'K' + str(yPosition) + ':' + 'K' + str(yPosition),
                                "values": [[str(totalTimeAttened)]]})
                    updateGlobal.append(updateGlobalEventStats(memberID, totalTimeAttened, discordIDFromGlobal,allGlobalData))
                    a = a + 1
                    yPosition = yPosition + 1
                    j = j + 1
                else:
                    if len(clockOut.splitlines()) < len(clockIn.splitlines()):
                        if clockOut != "":
                            clockOut = clockOut + "\n" +  str(datetime.now().strftime("%H:%M:%S"))
                        else:
                            clockOut = str(datetime.now().strftime("%H:%M:%S"))                        
                        totalTimeAttened = timeCalculation(clockIn, clockOut)
                        print(totalTimeAttened)
                        update.append({'range': 'H' + str(yPosition) + ':' + 'K' + str(yPosition),
                                    "values": [[memberName, clockIn, clockOut, str(timedelta(seconds=totalTimeAttened.seconds))]]})
                        updateGlobal.append(
                            updateGlobalEventStats(memberID, totalTimeAttened, discordIDFromGlobal, allGlobalData))
                        a = a + 1
                        yPosition = yPosition + 1
                        j = j + 1
            else:
                updateGlobal = list(filter(None, updateGlobal))
                dataFromGlobalList.batch_update(updateGlobal)
                updateGlobal.clear()
                worksheet.batch_update(update)
                update.clear()
                j = 0  #
        updateGlobal = list(filter(None, updateGlobal))
        try:
            if "test" in area:
                await ctx.send("test in area, not updating global")
            else:
                dataFromGlobalList.batch_update(updateGlobal)
                updateVersionNumber(dataFromGlobalList)
        except Exception as e:
            sendLog("Critical", "Tryiong to update global", e, "830", "Event Ending", "Weird Shit updating global")
        worksheet.batch_update(update)
        self.looper.cancel()
        worksheet.update_title(str(area) + " " + str(datetime.now().strftime("%d-%m-%Y")) + " (Closed)")
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
        sendLog_debug("Activity ended: " + area + ": https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
        await ctx.send("Activity ended: " + str(worksheet.url))
        
    @tasks.loop(seconds=300.0)
    async def looper(self,area,target_voice_channel: discord.VoiceChannel):
        #Gather member list from target voice channel
        x = 0
        
        roleList = []
        idList = []
        users = []

        for member in target_voice_channel.members:
            users.append(str(x) + ":" + str(member.display_name))
            idList.append(str(x) + ":" + str(member.id))
            for role in member.roles:
                roleList.append(str(x) + ":" + str(role.name))
            x = x + 1

        #def loop(area, listOfMembers, roleList):
        status = "Open"
        spreadsheet = client2.open('BDB Push Attendance')
        worksheet = client.open("BDB Push Attendance").worksheet(area)  # Opens new duplicated sheet
        status = worksheet.acell('K2').value
        if status == "Open":
            updateActivity(area, idList, users, roleList)
            sendLog_debug(area +" updated: " +  "https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
        else:
            sendLog_debug(area + " closed from Google Sheet: " + "https://docs.google.com/spreadsheets/d/"+str(spreadsheet.id)+"/edit#gid="+str(worksheet.id))
            self.looper.cancel()
            
    @commands.command()
    async def warstats(self, ctx, Name, file_types=("jpeg","png")):
        leadboardImages = []
    
        await self.updateGlobalListOfMembers(ctx)
        dataFromGlobalList = client.open("BDB Push Attendance").worksheet("BDB Global Leaderboard")
        discordIDFromGlobal = dataFromGlobalList.col_values(3)[7:]
        globalAllData = dataFromGlobalList.get_all_values()
        namesFromGlobalList = dataFromGlobalList.col_values(8)[7:]
        namesFromGlobalList = [each_string.upper().replace(" ", "") for each_string in namesFromGlobalList]
        for a, word in enumerate(namesFromGlobalList):
            for letter in word:
                if letter in string.punctuation:
                    namesFromGlobalList[a] = word.replace(letter, "")
        worksheet1 = client.open("BDB Push Attendance").worksheet('Template For War')
        worksheet1.duplicate(new_sheet_name=Name)



        worksheet = client.open("BDB Push Attendance").worksheet(Name)
        worksheet.update('D2', Name)
        x = 8
        update = []
        updateGlobalStats = []
        j = 1
        peopleNotInCompany = []

        if not ctx.message.attachments:
            await ctx.send("Try again with images attached")
            return        
        attachments = ctx.message.attachments
        #save attachments locally
        k=0
        for attachment in attachments:            
            filename = f"{ROOT_DIR}/Images/Image_{k}.png"
            await attachment.save(filename)
            await ctx.send(filename + " saved")
            k=k+1
        #prepate local images for tesseract
        numberOfDiscordIDs = []
        for image in sorted(os.listdir(f'{ROOT_DIR}/Images/')):
            image = f"{ROOT_DIR}/Images/" + image
            issue = image
            #textOffImage = imgProcession(image)
            try:
                image = cv2.imread(convetImageRGB(image),0)
                #Edit for accuracy (Image read)
                thresh = cv2.threshold(image, 170, 255, cv2.THRESH_BINARY)[1]
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
                close = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
                result = 255 - close
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sendLog("Critical", e, "Issue", (exc_type, fname, exc_tb.tb_lineno),
                        "Row Creation current row, check for consistency = " + str(issue), "Fucky shit reading img text")
            textOffImage = str(pytesseract.image_to_string(cv2.resize(result[0:0 + 1080, 250:500 + 1920], None, fx=1.7, fy=1.7),config='--psm 6')).split("\n")
            nameOffImage = str(pytesseract.image_to_string(cv2.resize(result[0:0 + 1080, 0:300 + 120], None, fx=1.7, fy=1.7),config='--psm 6')).split("\n")
            nameOffImage = list(filter(None, nameOffImage))
            if '\x0c' in nameOffImage:
                nameOffImage.remove('\x0c')
            if '\x0c' in textOffImage:
                textOffImage.remove('\x0c')
            textOffImage = list(filter(None, textOffImage))

            for baseRow in textOffImage:
                try:
                    row = rowCorrection(baseRow, nameOffImage)
                    if row != None:
                        if row[0]:
                            discordID = getDiscordID(row[0],namesFromGlobalList, discordIDFromGlobal)
                            if discordID != "Not in company":
                                numberOfDiscordIDs.append(discordID)
                            name = row[0]
                            score = row[1]
                            kills = row[2]
                            deaths = row[3]
                            assissts = row[4]
                            healing = row[5]
                            damage = row[6]
                            if discordID.isdecimal():
                                updateGlobalStats.append(updateGlobalStatWar(discordID,discordIDFromGlobal,globalAllData,score,kills,deaths,assissts,healing,damage))
                            else:
                                peopleNotInCompany.append(name)
                            if j < 1000:
                                update.append({'range': 'C' + str(x) + ':' + 'K' + str(x),
                                            "values": [[discordID,j,name,score,kills,deaths,assissts,healing,damage]]})
                                x = x + 1
                                j = j + 1
                            else:
                                worksheet.batch_update(update)
                                update.clear()
                                j = 0
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    sendLog("Critical",e,row,(exc_type, fname, exc_tb.tb_lineno),"Row Creation current row, check for consistency = " + str(j), "Fucky shit writing to sheet")
        print(updateGlobalStats)
        worksheet.batch_update(update)
        worksheet.update_title(str(Name) + " " + str(datetime.now().strftime("%d-%m-%Y")))
        await ctx.send("```"+"People not in company/n"+str(peopleNotInCompany)+"```")

        
        if "test" in Name:
            await ctx.send("test in Name, not updating global")
        else:
            # if len(discordID) < 50:
            #     #Ask question is this data correct, if no don't update global. If yes update gloabl and version number.
            #     randomVariableToNotThrowError = 1
            #     await ctx.send(f"discordID length is {len(discordID)} im not updating global")
            can_react = ctx.channel.permissions_for(ctx.me).add_reactions
            
            message="Would you like to update the global leaderboard with this data?"
            if not can_react:
                message += " (y/n)"
            query: discord.Message = await ctx.send(message)
            if can_react:
                # noinspection PyAsyncCall
                start_adding_reactions(query, ReactionPredicate.YES_OR_NO_EMOJIS)
                pred = ReactionPredicate.yes_or_no(query, ctx.author)
                event = "reaction_add"
            else:
                pred = MessagePredicate.yes_or_no(ctx)
                event = "message"
            try:
                await ctx.bot.wait_for(event, check=pred, timeout=300)
            except asyncio.TimeoutError:
                await query.delete()
                await ctx.send("Not updating global leaderboard, deleting old files")
                for filename in os.listdir(f'{ROOT_DIR}/Images'):
                    await ctx.send(filename)
                    if os.path.exists(f'{ROOT_DIR}/Images/'+filename):
                        os.remove(f'{ROOT_DIR}/Images/'+filename)
                        await ctx.send(f"{filename} deleted")
                return

            if not pred.result:
                if can_react:
                    await query.delete()
                    await ctx.send("Not updating global leaderboard, deleting old files")
                    for filename in os.listdir(f'{ROOT_DIR}/Images'):
                        await ctx.send(filename)
                        if os.path.exists(f'{ROOT_DIR}/Images/'+filename):
                            os.remove(f'{ROOT_DIR}/Images/'+filename)
                            await ctx.send(f"{filename} deleted")
                    return
                else:
                    await ctx.send("OK then.")
                    await ctx.send("Not updating global leaderboard, deleting old files")
                    for filename in os.listdir(f'{ROOT_DIR}/Images'):
                        await ctx.send(filename)
                        if os.path.exists(f'{ROOT_DIR}/Images/'+filename):
                            os.remove(f'{ROOT_DIR}/Images/'+filename)
                            await ctx.send(f"{filename} deleted")
                    return
            else:
                if can_react:
                    with contextlib.suppress(discord.Forbidden):
                        await query.clear_reactions()


                     
            #await ctx.invoke(ctx.bot.get_cog("Core").reload, *updated_cognames)
            await ctx.send("Updating global leaderboard")
            dataFromGlobalList.batch_update(updateGlobalStats)
            updateVersionNumber(dataFromGlobalList)
        
        #duplicate to public sheet
        template = client.open("BDB War Stats History").worksheet('Template For War')
        template.duplicate(new_sheet_name=Name)
        publicSheetForWar = client.open("BDB War Stats History").worksheet(Name)
        publicSheetForWar.update('D2', Name)
        publicSheetForWar.batch_update(update)
        publicSheetForWar.update_title(str(Name) + " " + str(datetime.now().strftime("%d-%m-%Y")))

        #await ctx.message.delete()
        for filename in os.listdir(f'{ROOT_DIR}/Images'):
            await ctx.send(filename)
            if os.path.exists(f'{ROOT_DIR}/Images/'+filename):
                 os.remove(f'{ROOT_DIR}/Images/'+filename)
                 await ctx.send(f"{filename} deleted")

    @commands.command()
    async def eventstats(self, ctx, Name, file_types=("jpeg", "png")):
        leadboardImages = []

        await self.updateGlobalListOfMembers(ctx)
        dataFromGlobalList = client.open("BDB Push Attendance").worksheet("BDB Global Leaderboard")
        discordIDFromGlobal = dataFromGlobalList.col_values(3)[7:]
        globalAllData = dataFromGlobalList.get_all_values()
        namesFromGlobalList = dataFromGlobalList.col_values(8)[7:]
        namesFromGlobalList = [each_string.upper().replace(" ", "") for each_string in namesFromGlobalList]
        for a, word in enumerate(namesFromGlobalList):
            for letter in word:
                if letter in string.punctuation:
                    namesFromGlobalList[a] = word.replace(letter, "")
        worksheet1 = client.open("BDB Push Attendance").worksheet('Template For War')
        worksheet1.duplicate(new_sheet_name=Name)

        worksheet = client.open("BDB Push Attendance").worksheet(Name)
        worksheet.update('D2', Name)
        x = 8
        update = []
        updateGlobalStats = []
        j = 1
        peopleNotInCompany = []

        if not ctx.message.attachments:
            await ctx.send("Try again with images attached")
            return
        attachments = ctx.message.attachments
        # save attachments locally
        k = 0
        for attachment in attachments:
            filename = f"{ROOT_DIR}/Images/Image_{k}.png"
            await attachment.save(filename)
            await ctx.send(filename + " saved")
            k = k + 1
        # prepate local images for tesseract
        numberOfDiscordIDs = []
        for image in sorted(os.listdir(f'{ROOT_DIR}/Images/')):
            image = f"{ROOT_DIR}/Images/" + image
            issue = image
            # textOffImage = imgProcession(image)
            try:
                image = cv2.imread(convetImageRGB(image), 0)
                # Edit for accuracy (Image read)
                thresh = cv2.threshold(image, 170, 255, cv2.THRESH_BINARY)[1]
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
                close = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
                result = 255 - close
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                sendLog("Critical", e, "Issue", (exc_type, fname, exc_tb.tb_lineno),
                        "Row Creation current row, check for consistency = " + str(issue),
                        "Fucky shit reading img text")
            textOffImage = str(
                pytesseract.image_to_string(cv2.resize(result[0:0 + 1080, 250:500 + 1920], None,fx=1.7, fy=1.7),
                                            config='--psm 6')).split("\n")
            nameOffImage = str(
                pytesseract.image_to_string(cv2.resize(result[0:0 + 1080, 0:300 + 120], None, fx=1.7, fy=1.7),
                                            config='--psm 6')).split("\n")
            nameOffImage = list(filter(None, nameOffImage))
            if '\x0c' in nameOffImage:
                nameOffImage.remove('\x0c')
            if '\x0c' in textOffImage:
                textOffImage.remove('\x0c')
            textOffImage = list(filter(None, textOffImage))

            for baseRow in textOffImage:
                try:
                    row = rowCorrection(baseRow, nameOffImage)
                    if row != None:
                        if row[0]:
                            discordID = getDiscordID(row[0], namesFromGlobalList, discordIDFromGlobal)
                            if discordID != "Not in company":
                                numberOfDiscordIDs.append(discordID)
                            name = row[0]
                            score = row[1]
                            kills = row[2]
                            deaths = row[3]
                            assissts = row[4]
                            healing = row[5]
                            damage = row[6]
                            if discordID.isdecimal():
                                updateGlobalStats.append(
                                    updateGlobalStatEvent(discordID, discordIDFromGlobal, globalAllData))
                            else:
                                peopleNotInCompany.append(name)
                            if j < 1000:
                                update.append({'range': 'C' + str(x) + ':' + 'K' + str(x),
                                               "values": [[discordID, j, name, score, kills, deaths, assissts, healing,
                                                           damage]]})
                                x = x + 1
                                j = j + 1
                            else:
                                worksheet.batch_update(update)
                                update.clear()
                                j = 0
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    sendLog("Critical", e, row, (exc_type, fname, exc_tb.tb_lineno),
                            "Row Creation current row, check for consistency = " + str(j),
                            "Fucky shit writing to sheet")
        print(updateGlobalStats)
        worksheet.batch_update(update)
        worksheet.update_title(str(Name) + " " + str(datetime.now().strftime("%d-%m-%Y")))
        await ctx.send("```" + "People not in company/n" + str(peopleNotInCompany) + "```")

        if "test" in Name:
            await ctx.send("test in Name, not updating global")
        else:
            # if len(discordID) < 50:
            #     #Ask question is this data correct, if no don't update global. If yes update gloabl and version number.
            #     randomVariableToNotThrowError = 1
            #     await ctx.send(f"discordID length is {len(discordID)} im not updating global")
            can_react = ctx.channel.permissions_for(ctx.me).add_reactions

            message = "Would you like to update the global leaderboard with this data?"
            if not can_react:
                message += " (y/n)"
            query: discord.Message = await ctx.send(message)
            if can_react:
                # noinspection PyAsyncCall
                start_adding_reactions(query, ReactionPredicate.YES_OR_NO_EMOJIS)
                pred = ReactionPredicate.yes_or_no(query, ctx.author)
                event = "reaction_add"
            else:
                pred = MessagePredicate.yes_or_no(ctx)
                event = "message"
            try:
                await ctx.bot.wait_for(event, check=pred, timeout=300)
            except asyncio.TimeoutError:
                await query.delete()
                await ctx.send("Not updating global leaderboard, deleting old files")
                for filename in os.listdir(f'{ROOT_DIR}/Images'):
                    await ctx.send(filename)
                    if os.path.exists(f'{ROOT_DIR}/Images/' + filename):
                        os.remove(f'{ROOT_DIR}/Images/' + filename)
                        await ctx.send(f"{filename} deleted")
                return

            if not pred.result:
                if can_react:
                    await query.delete()
                    await ctx.send("Not updating global leaderboard, deleting old files")
                    for filename in os.listdir(f'{ROOT_DIR}/Images'):
                        await ctx.send(filename)
                        if os.path.exists(f'{ROOT_DIR}/Images/' + filename):
                            os.remove(f'{ROOT_DIR}/Images/' + filename)
                            await ctx.send(f"{filename} deleted")
                    return
                else:
                    await ctx.send("OK then.")
                    await ctx.send("Not updating global leaderboard, deleting old files")
                    for filename in os.listdir(f'{ROOT_DIR}/Images'):
                        await ctx.send(filename)
                        if os.path.exists(f'{ROOT_DIR}/Images/' + filename):
                            os.remove(f'{ROOT_DIR}/Images/' + filename)
                            await ctx.send(f"{filename} deleted")
                    return
            else:
                if can_react:
                    with contextlib.suppress(discord.Forbidden):
                        await query.clear_reactions()

            # await ctx.invoke(ctx.bot.get_cog("Core").reload, *updated_cognames)
            await ctx.send("Updating global leaderboard")
            dataFromGlobalList.batch_update(updateGlobalStats)
            updateVersionNumber(dataFromGlobalList)

        # duplicate to public sheet
        template = client.open("BDB War Stats History").worksheet('Template For War')
        template.duplicate(new_sheet_name=Name)
        publicSheetForWar = client.open("BDB War Stats History").worksheet(Name)
        publicSheetForWar.update('D2', Name)
        publicSheetForWar.batch_update(update)
        publicSheetForWar.update_title(str(Name) + " " + str(datetime.now().strftime("%d-%m-%Y")))

        # await ctx.message.delete()
        for filename in os.listdir(f'{ROOT_DIR}/Images'):
            await ctx.send(filename)
            if os.path.exists(f'{ROOT_DIR}/Images/' + filename):
                os.remove(f'{ROOT_DIR}/Images/' + filename)
                await ctx.send(f"{filename} deleted")

    @commands.command()
    async def zeroCorrectionList(self, ctx, item):
        with open(f'{ROOT_DIR}/zeroCorrectionList', 'rb') as fp:
            itemlist = pickle.load(fp)

        itemlist.append(item)

        with open(f'{ROOT_DIR}/zeroCorrectionList', 'wb') as fp:
            pickle.dump(itemlist, fp)
        await ctx.send(f"{item} added to list")

    @commands.command()
    async def zeroCorrectionListShow(self, ctx):
        with open(f'{ROOT_DIR}/zeroCorrectionList', 'rb') as fp:
            itemlist = pickle.load(fp)
        await ctx.send("```"+str(itemlist)+"```")

    @commands.command()
    async def zeroCorrectionListDelete(self, ctx, item):
        with open(f'{ROOT_DIR}/zeroCorrectionList', 'rb') as fp:
            itemlist = pickle.load(fp)

        itemlist.remove(item)

        with open(f'{ROOT_DIR}/zeroCorrectionList', 'wb') as fp:
            pickle.dump(itemlist, fp)

        sendLog("Warning", "Removing Item Zero Correction List", itemlist, "219",
                "Zero correction List updated by removing -" + str(item), "")
        
        sendLog("Warning","Changing Zero Correction List",itemlist, "219","Zero correction List updated with -" + str(item),"")
        await ctx.send("Deleted")

    @commands.command()
    async def nameCorrectionList(self, ctx, incorrectName, correctName):
        with open(f'{ROOT_DIR}/incorrectName', 'rb') as fp:
            incorrectNameList = pickle.load(fp)
        with open(f'{ROOT_DIR}/correctName', 'rb') as fp:
            correctNameList = pickle.load(fp)

        incorrectNameList.append(incorrectName)
        correctNameList.append(correctName)

        with open(f'{ROOT_DIR}/incorrectName', 'wb') as fp:
            pickle.dump(incorrectNameList, fp)

        with open(f'{ROOT_DIR}/correctName', 'wb') as fp:
            pickle.dump(correctNameList, fp)

        sendLog("Warning","Changing incorrect name List",incorrectNameList, "219","Zero correction List updated with -" + incorrectName,"")
        sendLog("Warning", "Changing Correct name List", correctNameList, "219","Zero correction List updated with -" + correctName, "")
        await ctx.send("Name Corrected")

    @commands.command()
    async def nameCorrectionListShow(self, ctx):
        with open(f'{ROOT_DIR}/incorrectName', 'rb') as fp:
            itemlist = pickle.load(fp)
        await ctx.send("```"+str(itemlist)+"```")
        with open(f'{ROOT_DIR}/correctName', 'rb') as fp:
            itemlist2 = pickle.load(fp)
        await ctx.send("```"+str(itemlist2)+"```")
    #COMMANDS
    @commands.command()    
    async def nameCorrectionListDelete(self, ctx, incorrectNameToRemove, correctNameToRemove):
        with open(f'{ROOT_DIR}/incorrectName', 'rb') as fp:
            itemlist = pickle.load(fp)
        with open(f'{ROOT_DIR}/correctName', 'rb') as fp:
            itemlist2 = pickle.load(fp)
        itemlist.remove(incorrectNameToRemove)
        itemlist2.remove(correctNameToRemove)
        with open(f'{ROOT_DIR}/incorrectName', 'wb') as fp:
            pickle.dump(itemlist, fp)

        with open(f'{ROOT_DIR}/correctName', 'wb') as fp:
            pickle.dump(itemlist2, fp)


        sendLog("Warning", "Removing Item Zero Correction List", itemlist, "219",
                "Zero correction List updated by removing -" + str(incorrectNameToRemove), "")
        sendLog("Warning", "Removing Item Zero Correction List", itemlist, "219",
                "Zero correction List updated by removing -" + str(correctNameToRemove), "")
        
        await ctx.send("List Deleted")
        #Only to be ran when clearing our global list fully. Basically wiping all Data - Complete
        #This can be discord command, get full member list, rolelist and id list and pass to getAllRoles
    @commands.command()
    async def populateGlobalList(self, ctx, role: discord.Role):
        worksheet = client.open("BDB Push Attendance").worksheet("BDB Global Leaderboard")
        IDonSheet = worksheet.col_values(3)[7:]
        listOfCurrentMembersID = []
        update = []
        j = 0
        x = 8
        idList = [] 
        users = []
        roleList = []
        k = 0

        filename = str(role) + "members"
        filename2 = str(role) + "roles"
        filename3 = str(role) + "membersID"
        for member in role.members:
            users.append(str(k) + ":" + str(member.display_name))
            idList.append(str(k) + ":" + str(member.id))
            for role in member.roles:
                roleList.append(str(k) + ":" + str(role.name))
            k = k + 1

        for ID in idList:
            if j < 1000:
                removeNumber = str(ID).split(":")
                if str(removeNumber[1]) not in IDonSheet:
                    # Add them to sheet
                    discordID = removeNumber[1]
                    roles = getAllRoles(removeNumber[0], users, roleList) #need to pass some userlists
                    inGameRole = roles[0]
                    discordRole = roles[1]
                    Wep1 = roles[2]
                    Wep2 = roles[3]
                    discordName = roles[4]

                    update.append({'range': 'C' + str(x) + ':' + 'H' + str(x),
                                "values": [[discordID, inGameRole, Wep1, Wep2, discordRole, discordName]]})
                    listOfCurrentMembersID.append(
                        str(removeNumber[1]).upper().replace(" ", ""))  # Need to add user to sheet
                    j = j + 1
                    x = x + 1
            else:
                worksheet.batch_update(update)
                update.clear()
                j = 0
        worksheet.batch_update(update)
        await ctx.send("Global List Populated")
        textfile = open(f"{filename}.txt", "w")
        textfile.write(str(users))
        textfile.close()
        textfile = open(f"{filename2}.txt", "w")
        textfile.write(str(roleList))
        textfile.close()
        textfile = open(f"{filename3}.txt", "w")
        textfile.write(str(idList))
        textfile.close()
        await ctx.send(file=discord.File(f"{filename}.txt"))
        await ctx.send(file=discord.File(f"{filename2}.txt"))
        await ctx.send(file=discord.File(f"{filename3}.txt"))



    # @commands.command()
    # async def tradepost(self, ctx):
    #     service = build('drive', 'v3', credentials=creds)
    #     Folder_id = "'1VFKzwum9X1j7BrLJCCfjZ_2bCIZHPplY'"  # Enter The Downloadable folder ID From Shared Link

    #     for filename in os.listdir('/home/genobear90/Folder'):
    #     #for filename in files:
    #         if os.path.exists('/home/genobear90/Folder/'+filename+'/'+filename):
    #             os.remove('/home/genobear90/Folder/'+filename+'/'+filename)                
    #         os.rmdir('/home/genobear90/Folder/'+filename)

    #     results = service.files().list(
    #         pageSize=1000, q=Folder_id+" in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
    #     items = results.get('files', [])
    #     if not items:
    #         print('No files found.')
    #     else:
    #         print('Files:')
    #         for item in items:
    #             if item['mimeType'] == 'application/vnd.google-apps.folder':
    #                 if not os.path.isdir("Folder"):
    #                     os.mkdir("Folder")
    #                 bfolderpath = os.getcwd()+"/Folder/"
    #                 if not os.path.isdir(bfolderpath+item['name']):
    #                     os.mkdir(bfolderpath+item['name'])

    #                 folderpath = bfolderpath+item['name']
    #                 listfolders(service, item['id'], folderpath)
    #             else:
    #                 if not os.path.isdir("Folder"):
    #                     os.mkdir("Folder")
    #                 bfolderpath = os.getcwd()+"/Folder/"
    #                 if not os.path.isdir(bfolderpath + item['name']):
    #                     os.mkdir(bfolderpath + item['name'])

    #                 filepath = bfolderpath + item['name']
    #                 downloadfiles(service, item['id'], item['name'], filepath)
    #     #files = glob.glob('/home/genobear90/Folder/*')
    #     for filename in sorted(os.listdir('/home/genobear90/Folder')):
    #     #for filename in files:
    #         await ctx.send(file=discord.File('/home/genobear90/Folder/'+filename+'/'+filename))
    #         os.remove('/home/genobear90/Folder/'+filename+'/'+filename)
    #         os.rmdir('/home/genobear90/Folder/'+filename)
        
    #     #os.removedirs('/home/genobear90/Folder/')

    #     await ctx.send("Data maintained by LOUKAN")
