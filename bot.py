#!/usr/bin/env python3

import os
import threading
import asyncio
import random
import time
import sys

from datetime import datetime
from datetime import timedelta

me = "304381696168427531"
USERS_LIST = "users.txt"
ALARMS_LIST = "docket.txt"
PATH = "/home/pi/Discord_Bot/"
PM_MSG = "pm.log"
#PATH = "/home/conor/Discord_Bot/"
STATUS_TIMER = 30 #minutes
BACKUP_DELAY = 6 #hours
lock = threading.Lock()
docket = []

statuses = ["Human Music", "Replacing David","Thinking thoughts", 
        "Reading Asimov","Destroying God", "Stealing ur job lul", 
        "Haxxing the planet", "Got Simulsliced :/", "Jaegering RoboGrant",
        "¯\_(:o:)_/¯", "Adventuring Bizarrely", "With Your Heart",
        "Doxxing the RNC", "Pong!", "Dividing By 0" ]

sending = ['Arriving From The Void...', 'A Black Hole Has Sent a Message To You...', 'Pssssst Here Take This...', '(╯°□°)╯ ']


#Reads token in from file
def get_token():
    with open(PATH + "token", 'r') as fil:
        lines = fil.readlines()
        fil.close()
        return str(lines[0])


tok = get_token()
#os.system("." + PATH + "fts.py")
#if not os.path.exists(PATH + "status.sys"):
#    sys.exit("First time setup failure")
#os.system("sudo rm " + PATH + "status.sys")

import discord #Ugh I'm so sorry this is here, it's just in case I have to migrate platforms I know it's hideous
intents = discord.Intents.all()
client = discord.Client(intents=intents)

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
    if flag == 1:
        tz = "EST"
    if flag == 0:
        tz = "CDT"
        hour = str(int(hour) + 1)   #Adjusting time zone differences because datetime.now will be an hour before them
    
    now = datetime.now()
    future = datetime(year = int(year), month = int(month), day = int(day), hour = int(hour), minute = int(minute), second = 0)
    if now.year > future.year:
        return 6
    if now.year == future.year and now.month > future.month:
        return 6
    if now.year == future.year and now.month == future.month and (now.day > future.day or now.day == future.day):
        return 7 
    return [future, title, tz]


#Creates alarm thread
def alarm_prethread(dt_string, flag):
    values = parse_dtstr(dt_string, flag)
    if values == 0:
        return "Improperly Formatted Input [**Check Symbols**]"
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
        return "Invalid Date [**Alarm Cannot Be Set For Same Day**]"
    if values in docket:
        return "Invalid Date [**Alarm Already Set**]"
    docket.append(values)
    return values

#Function to replace common code
async def delete_msg(msg):
    try:
        await msg.delete()
    except:
        pass


#Performs alarm function
async def alarm_thread(values):
    now = datetime.now()
    channel = client.get_channel(417929344028114945)    #Squawks
    twelve = ((values[0] - timedelta(hours=12)) - now).total_seconds() #Gets total number of seconds from 12 hours before alarm, and now
    
    await asyncio.sleep(twelve)
    bot_msg = await channel.send("Don't forget, " + values[1] + " starts in 12 hours!")
    await asyncio.sleep(11 * 3600)      #Waits until 1 hour before starting
    await delete_msg(bot_msg)
    
    bot_msg = await channel.send(values[1] + " Starts in 1 Hour!")
    await asyncio.sleep(3600)           #Waits until starting
    await delete_msg(bot_msg)
    callout = voice_members()
    counter = 2
    
    while len(callout) != 0 or counter > 0: #Runs twice, or until everyone is in voice call
        msg = ""
        for user_id in callout:
            msg += compact_id(user_id) + " "
        msg += values[1] + " Has Started!"
        bot_msg = await channel.send(msg)
        await asyncio.sleep(60 * 10)    #Waits 10 min
        try:
            await bot_msg.delete()
        except:
            pass
        finally:
            callout = voice_members()   #Recounts everyone whos in call
            counter -= 1
    docket.remove(values)

#Backs up docket into file every 6 hours, in case of LOP
def backup_docket():
    while True:
        time.sleep(3600 * BACKUP_DELAY)
        if os.path.exists(PATH + ALARMS_LIST): #deletes current alarms list
            lock.acquire()              #This is to prevent having to check doubles
            os.remove(PATH + ALARMS_LIST)      #Also only keeps current alarms in docket.txt
            lock.release()
        if len(docket) == 0:
            return
        lock.acquire()
        f = open(PATH + ALARMS_LIST, "a")
        for entry in docket:            #Writes to file as date, title, timezone
            line = entry[0].strftime("%m-%d-%Y %H:%M")
            line += "," + entry[1]
            line += "," + entry[2]
            f.write(line + "\n")
        f.close()
        lock.release()

#Used to reinit alarm threads
def init_docket_from_file():
    if not os.path.exists(PATH + ALARMS_LIST): #Doesn't run if there's no file obs
        return False
    lock.acquire()
    with open(PATH + ALARMS_LIST, 'r') as f:
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
    if not os.path.exists(PATH + USERS_LIST):
        lock.acquire()
        f = open(PATH + USERS_LIST, "w+")
        f.close()
        lock.release()
    if duplicate_user(user):            #Doesn't add duplicate users
        return 0
    lock.acquire()
    f = open(PATH + USERS_LIST, "a")
    f.write(str(user) + "," + str(user_id) + "\n")
    f.close()
    lock.release()
    return 1

async def move_around():
    GEN = discord.utils.get(client.guilds[0].voice_channels, name='Weenie Hut General')
    LB = discord.utils.get(client.guilds[0].voice_channels, name = 'Super Weenie Hut General')
    LB2 = discord.utils.get(client.guilds[0].voice_channels, name = 'HORNY JAIL')
    GM = discord.utils.get(client.guilds[0].voice_channels, name = 'GM Chat')
    voices = [GEN, LB, LB2, GM]
    members = []
    for voice in voices:
        for member in voice.members:
            members.append(member)   #Gets all the users ids per channel
    for x in range(random.randint(0, 10)):
        user_choice = random.randint(0, len(members) - 1)
        channel_choice = random.randint(0, len(voices) - 1)
        try:
            print("Moving {} to {}".format(members[user_choice], voices[channel_choice]))
            await members[user_choice].move_to(voices[channel_choice])
        except:
            pass

#Checks all the members in the voice channel
def voice_members():
    GEN = discord.utils.get(client.guilds[0].voice_channels, name='Weenie Hut General')
    LB = discord.utils.get(client.guilds[0].voice_channels, name = 'Weenie Hut Low-Bitrate')
    LB2 = discord.utils.get(client.guilds[0].voice_channels, name = 'Weenie Hut Low-Bitrate II')
    GM = discord.utils.get(client.guilds[0].voice_channels, name = 'GM Chat')
    voices = [GEN, LB, LB2, GM]
    members = []
    for voice in voices:
        members.append(voice.members)   #Gets all the users ids per channel
    flatten = []
    callout = []
    ids = get_registered_ids()          #Gets all the ids from users.txt
    for member in members:
        for user in member:
                flatten.append(user.id) #Makes a list from list of lists
    for user in ids:
        if user not in flatten:
            callout.append(user)
    return callout

#Formatter for checking by username/id
def name_w_discr(user):
    return user.name + "#" + user.discriminator
    
#Checks to see if user has already registered
def duplicate_user(user):
    lock.acquire()
    with open(PATH + USERS_LIST, 'r') as fil:
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

#Formatter for discord tagging by id
def compact_id(user_id):
    return "<@" + str(user_id) + ">"

#Get's all the users in a file
def list_users():
    lock.acquire()
    with open(PATH + USERS_LIST, 'r') as fil:
        lines = fil.readlines()
        fil.close()
        lock.release()
        return lines

def pm_log(sender, msg, receiver):
    lock.acquire()
    today = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    with open(PATH + PM_MSG, 'a') as fil:
        fil.write("\n{}\t{} SENT {} TO {}\n".format(dt_string, sender, msg, receiver))
        fil.close()
    lock.release()

#Strips ID from Username#NUM, ID
def strip_id(string):
    half = string.split('#')[1]
    half = half.split(',')[1]
    return int(half[:-1])

def strip_short_id(string):
    return int(string.split('#')[1].split(',')[0])


def strip_username(string):
    return string.split('#')[0]


#Pairs off all of the registered members
def random_pairings():
    users = list_users()
    ids = get_registered_ids()
    ret = {}
    for ide in ids:
        choice = random.choice(users)
        while ((ide == 314161673755688962 and strip_short_id(choice) == 9334) 
                or strip_id(choice) == ide 
                or (ide == 304388792603770900 and strip_short_id(choice) == 4778)): #if Ryan gets reece, someone gets themselves, or reece gets ryan
            choice = random.choice(users)
        users.remove(choice)
        ret[ide] = strip_username(choice) 
    return ret


def get_server_members(member):
    for user in client.get_all_members():
        if member.lower() in str(user).lower():
            return user
    return None



#Appendable list of functions to be added to as needed
def build_functions():
    msg = "**!register** - Registers a new user for DND notifications\n"
    msg += "**!list_users** - Lists currently registered users\n"
    msg += "**!cmds** - Does this lol\n"
    msg += "**!irritate_everyone** - who can say\n"
    msg += "**!pm** - Sends anonymous DM to another user, formatted like !pm user message"
    msg += "\n\t\t\t\tuser is just some word that's unique to that person\'s username"
    msg += "\n\t\t\t\tFor instance, if you wanted to message Ryan you could use human or tree\n" 
    msg += "**!secret** - Runs the secret santa roulette\n"
    msg += "**!schedule** - Lists the currently running alarms (please run this before issuing a new alarm)\n"
    msg += "**!alarm** - Sets a DND session alert which will notifiy users prior to, and at the beginning of a session\n\t\t\t\tFormatted as !alarm DD-MM-YYYY HH:MM \"Title\" where HH is 0-23"
    msg += "\n\t\t\t\tYou May Not set an alarm for the same day, or a past date"
    msg += "\n\t\t\t\tTitle is used to designate what the alarm is for, you don't need to include quotation marks"
    return msg

#Gets all of the ids in a file
def get_registered_ids():
    users = list_users()
    ids = []
    for user in users:
        ids.append(int(user.split(",")[1].strip()))
    return ids

def flatten(message):
    ret = random.choice(sending) + " \""
    for word in message:
        ret += word + " "
    ret += "\""
    return ret

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
    if message.author == client.user and not message.content.startswith("!alarm"):
        return

    elif message.content.startswith("!pm"):
        msg = message.content.split(" ")
        user = get_server_members(msg[1])
        if user == None:
            bot_msg = await("Message Send Failed, Invalid Recipient")
            await asyncio.sleep(random.randrange(15, 20))
            delete_msg(bot_msg)
        else:
            print(flatten(msg[2:]))
            pm_log(message.author.name, flatten(msg[2:]), user.name)
            await user.send(flatten(msg[2:]))
            #await asyncio.sleep(3600 * 24)
            #await user.send("- {}".format(str(message.author.name)))    
        await delete_msg(message)

    elif message.content.startswith("!irritate_everyone"):
        await message.pin()
        await move_around()


    elif message.content.startswith("!secret"):
        pairs = random_pairings()
        for key in pairs:
            user = await client.fetch_user(key)
            await user.send("Hello! Your randomly assigned Secret Santa Recipient is {}! Good Luck!".format(pairs[key]))
            await asyncio.sleep(3)

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
        await delete_msg(bot_msg)
        await delete_msg(message)

#This is for testing purposes only
#    elif message.content.startswith('!voice'):
#        callout = voice_members()
#        msg = ""
#        for user_id in callout:
#            msg += compact_id(user_id) + " "
#        msg += " Get in here!"
#        channel = client.get_channel(417929344028114945)     
#        bot_msg = await channel.send(msg)
#        await asyncio.sleep(random.randrange(5,15))
#        await bot_msg.delete()
#        await message.delete()

    elif message.content.startswith('!register'):
        ret = register_user(message.author, message.author.id)
        if ret == 0:
            bot_msg = await message.channel.send("User Already Registered!")
        else:
            bot_msg = await message.channel.send("User " + str(message.author) + " Has Been Registered")
        await asyncio.sleep(random.randrange(5,15))
        delete_msg(bot_msg)
        delete_msg(message)

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
        await delete_msg(bot_msg)
        await delete_msg(message)

    elif message.content.startswith('!alarm'):
        flag = 0
        
        if str(message.author.id) == me:
            flag = 1
        resp = alarm_prethread(message.content, flag)
        
        if type(resp) == str:
            bot_msg = await message.channel.send(resp)
            await asyncio.sleep(random.randrange(5,15))
            await delete_msg(bot_msg)
            await delete_msg(message)
        
        else:
            bot_msg = await message.channel.send("Alarm Thread [**Active**]")
            await asyncio.sleep(random.randrange(5,15))
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
try:
    client.run(tok)
except TypeError:
    os.system("python3 -m pip install -U discord.py")
    try:
        client.run(tok)
    except:
        print("Somethings Gone Wrong")

