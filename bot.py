#!/usr/bin/env python3

import os
import discord
import threading
import asyncio
import random
import time

from datetime import datetime
from datetime import timedelta
me = "304381696168427531"
USERS_LIST = "users.txt"
ALARMS_LIST = "docket.txt"
STATUS_TIMER = 30 #minutes
BACKUP_DELAY = 6 #hours
lock = threading.Lock()
client = discord.Client()
docket = []
statuses = ["Playing Human Music", "Replacing David","Thinking thoughts", 
        "Reading Asimov","Destroying God", "Stealing ur job lul", 
        "Haxxing the planet", "Got Simulsliced :/", "Jaegering RoboGrant",
        "¯\_(:o:)_/¯", "Adventuring Bizarrely"]


#Reads token in from file
def get_token():
    with open("token", 'r') as fil:
        lines = fil.readlines()
        fil.close()
        return str(lines[0])


tok = get_token()

#Gets the title of a specific alarm
def flatten_title(title_lst):
    msg = ""
    for title in title_lst:
        msg += title + " "
    return msg

#Verifys alarm datetime and then passes arguments
def parse_dtstr(dt_string, flag):
    try:
        split = dt_string.split(" ")
        date = split[1]
        time = split[2]
        title = flatten_title(split[3:])
        day, month, year = date.split("-")
        hour, minute = time.split(":")
    except:
        return 0
    if int(day) > 31 or int(day) < 1:
        return 1
    if int(month) > 12 or int(month) < 1:
        return 2
    if int(hour) > 23 or int(hour) < 0:
        return 3
    if int(minute) > 59 or int(minute) < 0:
        return 4
    now = datetime.now()
    if flag == 1:
        tz = "EST"
    if flag == 0:
        tz = "CDT"
        hour = str(int(hour) + 1)
    future = datetime(year = int(year), month = int(month), day = int(day), hour = int(hour), minute = int(minute), second = 0)
    if now.year > future.year:
        return 6
    if now.year == future.year and now.month > future.month:
        return 6
    if now.year == future.year and now.month == future.month and (now.day > future.day or now.day == future.day):
        return 7 
    if flag == 1:
        tz = "EST"
    elif flag == 0:
        tz = "CDT"
    return [future, title, tz]


#Creates alarm thread
def alarm_prethread(dt_string, flag):
    values = parse_dtstr(dt_string, flag)
    if values == 0:
        return "Improperly Formatted Input [Check Symbols]"
    if values == 1:
        return "Invalid Value [**Day**]"
    if values == 2:
        return "Invalid Value [**Month**]"
    if values == 3:
        return "Invalid Value [**Hour**]"
    if values == 4:
        return "Invalid Value [**Minute**]"
    if values == 6:
        return "Invalid Date [**Past Date**]"
    if values == 7:
        return "Invalid Date [Alarm Cannot Be Set For Same Day]"
    if values in docket:
        return "Invalid Date [Alarm Already Set]"
    docket.append(values)
    return values



#Performs alarm function
async def alarm_thread(values):
    now = datetime.now()
    channel = client.get_channel(417929344028114945)
    twelve = ((values[0] - timedelta(hours=12)) - now).total_seconds()
    await asyncio.sleep(twelve)
    bot_msg = await channel.send("Don't forget, " + values[1] + " starts in 12 hours!")
    await asyncio.sleep(11 * 3600)
    try:
        bot_msg.delete()
    except:
        pass
    bot_msg = await channel.send(values[1] + " Starts in 1 Hour!")
    await asyncio.sleep(3600)
    try:
        bot_msg.delete()
    except:
        pass
    callout = voice_members()
    msg = ""
    counter = 2
    while len(callout) != 0 or counter > 0:
        for user_id in callout:
            msg += compact_id(user_id) + " "
        msg += values[1] + " Has Started!"
        bot_msg = await channel.send(msg)
        await asyncio.sleep(60 * 10)
        try:
            bot_msg.delete()
        except:
            pass
        callout = voice_members()
        counter -= 1
    docket.remove(values)

def backup_docket():
    while True:
        time.sleep(3600 * BACKUP_DELAY)
        if os.path.exists(ALARMS_LIST):
            lock.acquire()
            os.remove(ALARMS_LIST)
            lock.release()
        if len(docket) == 0:
            return
        lock.acquire()
        f = open(ALARMS_LIST, "a")
        for entry in docket:
            line = entry[0].strftime("%m-%d-%Y %H:%M")
            line += "," + entry[1]
            line += "," + entry[2]
            f.write(line + "\n")
        f.close()
        lock.release()


def init_docket_from_file():
    if not os.path.exists(ALARMS_LIST):
        return False
    lock.acquire()
    with open(ALARMS_LIST, 'r') as f:
        lines = f.readlines()
        f.close()
    lock.release()
    lock.acquire()
    for line in lines:
        dt_args, event, tz = line.split(",")
        date, time = dt_args.split(" ")
        month, day, year = date.split("-")
        hour, minute = time.split(":")
        dt = datetime(year = int(year), month = int(month), day = int(day), hour = int(hour), minute = int(minute), second = 0)
        docket.append([dt, event, tz])
    lock.release()
    return True

#Registers a new user
def register_user(user, user_id):  
    if not os.path.exists(USERS_LIST):
        lock.acquire()
        f = open(USERS_LIST, "w+")
        f.close()
        lock.release()
    if duplicate_user(user):    
        return 0
    lock.acquire()
    f = open(USERS_LIST, "a")
    f.write(str(user) + "," + str(user_id) + "\n")
    f.close()
    lock.release()
    return 1

#Checks all the members in the voice channel
def voice_members():
    GEN = discord.utils.get(client.guilds[0].voice_channels, name='Weenie Hut General')
    LB = discord.utils.get(client.guilds[0].voice_channels, name = 'Weenie Hut Low-Bitrate') 
    GM = discord.utils.get(client.guilds[0].voice_channels, name = 'GM Chat')
    voices = [GEN, LB, GM]
    members = []
    for voice in voices:
        members.append(voice.members)
    flatten = []
    callout = []
    ids = get_registered_ids()
    for member in members:
        for user in member:
                flatten.append(user.id)
    for user in ids:
        if user not in flatten:
            callout.append(user)
    return callout


def name_w_discr(user):
    return user.name + "#" + user.discriminator
    

def duplicate_user(user):
    lock.acquire()
    with open(USERS_LIST, 'r') as fil:
        lines = fil.readlines()
        if not lines:
            print("Empty File")
        else:
            for line in lines:
                if line.split(",")[0] == str(user):
                    fil.close()
                    lock.release()
                    return True
    fil.close()
    lock.release()
    return False


def compact_id(user_id):
    return "<@" + str(user_id) + ">"

def list_users():
    lock.acquire()
    with open(USERS_LIST, 'r') as fil:
        lines = fil.readlines()
        fil.close()
        lock.release()
        return lines

def build_functions():
    msg = "**!register** - Registers a new user for DND notifications\n"
    msg += "**!list_users** - Lists currently registered users\n"
    msg += "**!cmds** - Does this lol\n"
    msg += "**!schedule** - Lists the currently running alarms (please run this before issuing a new alarm)\n"
    msg += "**!alarm** - Sets a DND session alert which will notifiy users prior to, and at the beginning of a session\n\t\t\t\tFormatted as !alarm DD-MM-YYYY HH:MM \"Title\" where HH is 0-23"
    msg += "\n\t\t\t\tYou May Not set an alarm for the same day, or a past date"
    msg += "\n\t\t\t\tTitle is used to designate what the alarm is for, you don't need to include quotation marks"
    return msg

def get_id():
    users = list_users()
    user_id = users[0].split(",")[1]
    return compact_id(user_id)


def get_registered_ids():
    users = list_users()
    ids = []
    for user in users:
        ids.append(int(user.split(",")[1].strip()))
    return ids

@client.event
async def on_ready():
    print(str(client.user) + " has Connected To Discord!")
    reinit = init_docket_from_file()
    if reinit:
        channel = client.get_channel(417929344028114945) 
        for value in docket:
            msg = "!alarm "
            msg += value[0].strftime("%d-%m-%Y %H:%M ")
            msg += value[1]
            bot_msg = await channel.send(msg)
            await asyncio.sleep(1)
    docket_thread = threading.Thread(target = backup_docket)
    docket_thread.start()
    while True:
        #await client.change_presence(activity=discord.CustomActivity(name= statuses[random.randrange(0, len(statuses))]))
        await client.change_presence(activity=discord.Game(name= statuses[random.randrange(0, len(statuses))]))
        await asyncio.sleep(60 * STATUS_TIMER)

@client.event
async def on_message(message):
    if message.author == client.user and not message.content.startswith("!REINIT"):
        return
    
    elif message.content.startswith("!REINIT")

    elif message.content.startswith("!schedule"):
        msg = ""
        if len(docket) == 0:
            msg += "No Alarms Currently Set"
        else:    
            for item in docket:
                msg += "\"" + item[1] + "\" is scheduled for "
                msg += item[0].strftime("%A, %B %d at %I:%M %p " + item[2] + "\n")
        
        bot_msg = await message.channel.send(msg)
        
        await asyncio.sleep(random.randrange(25, 60))
        try:
            await bot_msg.delete()
        except:
            pass
        try:
            await message.delete()
        except:
            pass

    elif message.content.startswith('!voice'):
        callout = voice_members()
        msg = ""
        for user_id in callout:
            msg += compact_id(user_id) + " "
        msg += " Get in here!"
        try:
            channel = client.get_channel(417929344028114945)     
            bot_msg = await channel.send(msg)
            await asyncio.sleep(random.randrange(5,15))
            await bot_msg.delete()
            await message.delete()
        except:
            pass

    elif message.content.startswith('!register'):
        ret = register_user(message.author, message.author.id)
        if ret == 0:
            bot_msg = await message.channel.send("User Already Registered!")
        else:
            bot_msg = await message.channel.send("User " + str(message.author) + " Has Been Registered")
        try:
            await asyncio.sleep(random.randrange(5,15))
            await bot_msg.delete()
            await message.delete()
        except:
            pass
    elif message.content.startswith('!cmds'):
        cmds_list = await message.channel.send(build_functions())
        await message.delete()
        channel = client.get_channel(377036034690514945)
        pins = await channel.pins()
        for pin in pins:
            if pin.author == client.user:
                await pin.delete()
        await cmds_list.pin()

    elif message.content.startswith('!list_users'):
        users = list_users()
        msg = ""
        msg += "**" + "Registered Users" + "**" + "\n"
        counter = 1
        for line in users:
            msg += str(counter) + ". " + line.split(",")[0] + "\n"
            counter += 1
        bot_msg = await message.channel.send(msg)
        await asyncio.sleep(30)
        try:
            await bot_msg.delete()
        except:
            pass
        try:
            await message.delete()
        except:
            pass

    elif message.content.startswith('!alarm'):
        flag = 0
        if str(message.author.id) == me:
            flag = 1
        resp = alarm_prethread(message.content, flag)
        if type(resp) == str:
            bot_msg = await message.channel.send(resp)
            await asyncio.sleep(random.randrange(5,15))
            try:
                await bot_msg.delete()
            except:
                pass
            try:
                await message.delete()
            except:
                pass
        else:
            bot_msg = await message.channel.send("Alarm Thread [**Active**]")
            
            await asyncio.sleep(1)
            #await asyncio.sleep(random.randrange(5,15))
            try:
                await bot_msg.delete()
            except:
                pass
            try:
                await message.delete()
            except:
                pass
            finally:
                await alarm_thread(resp)


    return

client.run(tok)
