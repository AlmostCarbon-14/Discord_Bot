#!/usr/bin/env python3

import os
import discord
import threading
import asyncio
import random

from datetime import datetime
me = "304381696168427531"
USERS_LIST = "users.txt"
lock = threading.Lock()
client = discord.Client()
docket = []

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
    alarm = threading.Thread(target = alarm_thread, args= (values,))
    alarm.start()
    return "Alarm Thread [**Active**]"


#Performs alarm function
def alarm_thread(values):
    print("Acquiring Channel")
    channel = client.get_channel(417929344028114945)
    now = datetime.now()
    secs = (values[0] - now).total_seconds()
    #bot_msg = await channel.send("Herro")
    #await bot_msg.delete()



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
    print(GEN)
    print(LB)
    print(GM)
    voices = [GEN, LB, GM]
    members = []
    for voice in voices:
        members.append(voice.members)
    flatten = []
    callout = []
    ids = get_registered_ids()
    for member in members:
        for user in member:
                flatten.append(user)
    for user in ids:
        present = False
        for member in flatten:
            if str(member.id) == str(user):
                present = True
        if present == False:
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
    return "<@" + user_id.strip() + ">"

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
    msg += "**!schedule** - Lists the currently running alarms (please run this before issuing a new alarm)"
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
        ids.append(user.split(",")[1])
    return ids

@client.event
async def on_ready():
    print(str(client.user) + " has Connected To Discord!")
    await client.change_presence(activity=discord.Game(name= 'With Your Heart'))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    elif message.content.startswith("!schedule"):
        msg = ""
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
            await asyncio.sleep(random.randrange(5,15))
            bot_msg = await message.channel.send(msg)
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
        await message.channel.send(build_functions())
        await message.delete()

    elif message.content.startswith('!list_users'):
        users = list_users()
        msg = ""
        msg += "**" + "Registered Users" + "**" + "\n"
        counter = 1
        for line in users:
            msg += str(counter) + ". " + line.split(",")[0] + "\n"
            counter += 1
        bot_msg = await message.channel.send(msg)
        try:
            await asyncio.sleep(30)
            await bot_msg.delete()
            await message.delete()
        except:
            pass

    elif message.content.startswith('!alarm'):
        flag = 0
        if str(message.author.id) == me:
            flag = 1
        bot_msg = await message.channel.send(alarm_prethread(message.content, flag))
        try:
            await asyncio.sleep(random.randrange(5,15))
            await bot_msg.delete()
            await message.delete()
        except:
            pass
    return

client.run(tok)
