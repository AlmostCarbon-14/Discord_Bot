#!/usr/bin/env python3

import os
import discord
USERS_LIST = "users.txt"

client = discord.Client()

def get_token():
    with open("token", 'r') as fil:
        lines = fil.readlines()
        fil.close()
        return str(lines[0])


tok = get_token()


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
            await message.channel.send("User Already Registered!")
        else:
            await message.channel.send("User " + str(message.author) + " Has Been Registered")
        
    elif message.content.startswith('!list_users'):
        users = list_users()
        msg = ""
        msg += "**" + "Registered Users" + "**" + "\n"
        counter = 1
        for line in users:
            msg += str(counter) + ". " + line.split(",")[0] + "\n"
            counter += 1
        await message.channel.send(msg)
    
    elif message.content.startswith('!alarm'):
        callout = get_id()
        await message.channel.send(callout)
    else:
        print(message.content)
        print(message.author)

client.run(tok)
