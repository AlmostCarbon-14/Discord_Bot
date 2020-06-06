#!/usr/bin/env python3

import os
import discord
tok = "NzE4NTY4NDgyMDg1NTM1Nzg1.XtrGyw.5vFE5zfmyKGQCIKCme9TI7LI8VE"
USERS_LIST = "users.txt"

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


client = discord.Client()

@client.event
async def on_ready():
        print(str(client.user) + " has Connected To Discord!")

@client.event
async def on_message(message):
        if message.author == client.user:
            return
        
        elif message.content.startswith('!voice'):
            for guild in client.guilds:
                for member in guild.members:
                    print(member)
            users = list_users()
            

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
