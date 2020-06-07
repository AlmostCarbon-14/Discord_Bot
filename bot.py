#!/usr/bin/env python3

import os
import discord
import threading
import asyncio

from datetime import datetime

USERS_LIST = "users.txt"

client = discord.Client()

def get_token():
    with open("token", 'r') as fil:
        lines = fil.readlines()
        fil.close()
        return str(lines[0])


tok = get_token()


def parse_dtstr(dt_string):
    try:
        _, date, time = dt_string.split(" ")
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
    return [day, month, year, hour, minute]

def alarm_prethread(dt_string):
    values = parse_dtstr(dt_string)
    if values == 0:
        return "Improperly Formatted Input [Check Symbols]"
    if values == 1:
        return "Invalid Day Value"
    if values == 2:
        return "Invalid Month Value"
    if values == 3:
        return "Invalid Hour Value"
    if values == 4:
        return "Invalid Minute Value"
    if values == 6:
        return "Invalid Date"
    if values == 7:
        return "Invalid Date [Alarm Cannot Be Set For Same Day]"
    alarm = threading.Thread(target = alarm_thread, args= (values,))
    return "Alarm Thread [Active]"

def alarm_thread(values):
    print(values)

def register_user(user, user_id):
        if not os.path.exists(USERS_LIST):
            f = open(USERS_LIST, "w+")
            f.close()
        if duplicate_user(user):
                return 0
        f = open(USERS_LIST, "w+")
        f.write(str(user) + "," + str(user_id) + "\n")
        f.close()
        return 1

def voice_members():
   # GEN = discord.utils.get(client.guilds[0].voice_channels, name='Weenie Hut General')
   # LB = discord.utils.get(client.guilds[0].voice_channels, name = 'Weenie Hut Low-Bitrate') 
    
    GM = discord.utils.get(client.guilds[0].voice_channels, name = 'General')
    #GM = discord.utils.get(client.guilds[0].voice_channels, name = 'GM Chat')
    #print(GEN)
    #print(LB)
    #print(GM)
    #voices = [GEN, LB, GM]
    voices = [GM]
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
    with open(USERS_LIST, 'r') as fil:
        lines = fil.readlines()
        if not lines:
            print("Empty File")
        else:
            for line in lines:
                if line.split(",")[0] == str(user):
                    fil.close()
                    return True
    fil.close()
    return False


def compact_id(user_id):
    return "<@" + user_id.strip() + ">"

def list_users():
    with open(USERS_LIST, 'r') as fil:
        lines = fil.readlines()
        fil.close()
        return lines

def build_functions():
    msg = "**!register** - Registers a new user for DND notifications\n"
    msg += "**!list_users** - Lists currently registered users\n"
    msg += "**!cmds** - Does this lol\n"
    msg += "**!alarm** - Sets a DND session alert which will notifiy users prior to, and at the beginning of a session\n\t\t\t\tFormatted as !alarm DD-MM-YYYY HH:MM where HH is 0-23"
    msg += "\n\t\t\t\tYou May Not set an alarm for the same day, or a past date, please do not do this Ryan"
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

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    elif message.content.startswith('!voice'):
        callout = voice_members()
        msg = ""
        for user_id in callout:
            msg += compact_id(user_id) + " "
        msg += " Get in here!"
        await message.channel.send(msg)

    elif message.content.startswith('!register'):
        ret = register_user(message.author, message.author.id)
        if ret == 0:
            bot_msg = await message.channel.send("User Already Registered!")
        else:
            bot_msg = await message.channel.send("User " + str(message.author) + " Has Been Registered")
        await asyncio.sleep(5)
        await bot_msg.delete()
        await message.delete()

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
        await asyncio.sleep(30)
        await bot_msg.delete()
        await message.delete()

    elif message.content.startswith('!alarm'):
        bot_msg = await message.channel.send(alarm_prethread(message.content))
        await asyncio.sleep(5)
        await bot_msg.delete()
        await message.delete()
    else:
        print(message.content)
        print(message.author)

client.run(tok)
