import json
import re
import datetime
import numpy as np
import csv
import pytz
import random

import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import discord

from parseFunctions import parse_hist_command

from Roll import Roll
from Roller import Roller


FILENAME = 'rollers.p'

def read_from_file():
    try:
        with open(FILENAME, 'rb') as fileHandle:
            return pickle.load(fileHandle)
    except IOError:
        return []

style.use("fivethirtyeight")

with open("auth.json") as f:
    auth_dict = json.load(f)

token = auth_dict['token']
client = discord.Client()

#Open file here
rollers = read_from_file()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

def utc_to_local(utc_dt, local_tz):
    """Accepts a datetime object in UTC time, and returns the same time, in the timezone that was also passed"""
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def get_channel_members_names(channel):
    """Returns a list of all members of a channel. If the member has a nickname, the nickname is used instead of their name, otherwise their name is used"""

    names = []
    for member in channel.members:
        if member.nick is None:
            names.append(member.name)
        else:
            names.append(member.nick)

    return names

def get_user_nick(user):
    """Returns the nickname of the passed user, the name otherwise"""
    if user.nick is None:
        return user.name
    return user.nick

def write_roll_to_file():
    with open(FILENAME, 'wb') as fileHandle:
        pickle.dump(rollers, fileHandle)


async def get_roll_history(user, message, after_date=None):
    print("Getting roll history for", user)

    if after_date is None:
        today = datetime.datetime.utcnow()
        after_date = today - datetime.timedelta(days = 1)#yesterday by default

    if user not in get_channel_members_names(message.channel):
        await message.channel.send("That user is not in this channel, my guy")
        return


    roller = get_roller(user)

    rolls = roller.rolls

    #Filter rolls to be after a certain date
    rolls = [roll for roll in rolls if after_date < roll.created_at]
              
    return rolls


def get_roller(name):
    '''Returns the roller in the rollers list, that is the passed discord user'''
    global rollers
    print(rollers)
    for roller in rollers:
        if roller.name == name:
            return roller

    #we havent found them, so add them
    new_roller = Roller(name)
    rollers.append(new_roller)

    return new_roller

async def parse_roll_command(command, message):
    command = command.strip()
    args = command.split()

    if len(args) != 1:
        await message.channel.send("@" + str(get_user_nick(message.author)) + "Invalid dice expression")
        return


    dice_expression = args[0]
    # want args to be something like 1d100
    
    tokens = dice_expression.split("d")
    if tokens[0] == dice_expression:
        await message.channel.send("@" + str(get_user_nick(message.author)) + " Invalid dice expression")
        return

    if len(tokens) != 2:
        await message.channel.send("@" + str(get_user_nick(message.author)) + " Invalid dice expression")
        return

    quantity = int(tokens[0])
    dice = int(tokens[1])

    roller = None
    roll_results = [] #for if the roller rolled more than 1 die
    for i in range(quantity):
        #Roll dice
        roll_result = random.randint(1, dice)
        roll_results.append(roll_result)

        roll = Roll(dice, roll_result, message.created_at)

        #Add to Roller
        roller = get_roller(get_user_nick(message.author))
        roller.add_roll(roll)

        #Save data
        write_roll_to_file()


    if len(roll_results) == 1:
        await message.channel.send("@" + str(get_user_nick(message.author)) + " rolled **" + str(roll) + "**.")
    else:
        add_message = "("
        i = 0
        while i < len(roll_results):
            add_message = add_message + str(roll_results[i])

            if i != len(roll_results)-1:
                add_message = add_message + " + "
            i = i+1

        add_message = add_message + " = " + str(sum(roll_results)) + ")"
        await message.channel.send("@" + str(get_user_nick(message.author)) + " rolled **" + str(sum(roll_results)) + "**. " + add_message)


async def parse_hist_command(command, message):
    command = command.strip()
    args = command.split()

    if len(args) == 0:
        print("no args")
        #do stuff
        return

    date = None
    user = None

    i = 0
    not_date =  True
    while i < len(args):
        # if first arg is not one of these, its a user
        # ex. *hist andtrue today
        if not(args[i] == "hour" or args[i] == "week" or args[i] == "today" or args[i] == "month" or args[i] == "year"):
            if i == 0:
                user = args[i]
            else:
                user = user + str(' ') + str(args[i])
        else:
            break

        i = i + 1

    users = get_channel_members_names(message.channel)

    if user not in users and user is not None:
        await message.channel.send("That user is not in this channel, my guy")
        return

    # set date
    if len(args) >= i+1:
        date = args[i]
    else: 
        date = "today"


    title = None
    if user is not None:
        title = str(user) + "'s Rolls - " + date.capitalize()
    else:
        title = "Party Rolls - " + date.capitalize()

    today = datetime.datetime.utcnow()

    if date == "hour":
        after_date = today - datetime.timedelta(hours = 1)
    elif date == "today":
        after_date = today - datetime.timedelta(days = 1)
    elif date == "week":
        after_date = today - datetime.timedelta(weeks = 1)
    elif date == "month":
        after_date = today - datetime.timedelta(days = today.day)
    elif date == "year":
        after_date = today - datetime.timedelta(days = int(today.strftime("%j")))
        
    upload_message = "Rolls since " + utc_to_local(after_date, pytz.timezone('US/Eastern')).strftime("%b %d %Y %H:%M:%S")

    roll_data = [roll.roll for roll in await get_roll_history(user, message, after_date=after_date)]

    await create_histogram(message, title, roll_data, upload_message, create_csv="file" in args)




@client.event
async def on_message(message):

    if message.content.startswith('*hist ') or message.content.startswith('*hist'):
        await parse_hist_command(message.content.replace('*hist ', ''), message)
    elif message.content.startswith('*roll'):
        await parse_roll_command(message.content.replace('*roll ', ''), message)
  
async def create_histogram(message, title, data, upload_message=None, create_csv=False):
    if len(data) < 1:
        await message.channel.send("No data to make histogram")
        return

    print("Creating histogram...")
    plt.clf()

    ax = plt.axes()

    plt.title(title)
    ax.title.set_color('dimgrey')
        
    ax.set_axisbelow(True)

    # grid lines
    plt.grid(color='dimgrey', linestyle='solid')

    # grid background
    ax.set_facecolor("#36393F")

    # hide axis spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # tick frequency    
        

    # hide top and right ticks
    ax.xaxis.tick_bottom()
    ax.yaxis.tick_left()

    # lighten ticks and labels
    ax.tick_params(colors='dimgrey', direction='out')
    for tick in ax.get_xticklabels():
        tick.set_color('dimgrey')
    for tick in ax.get_yticklabels():
        tick.set_color('dimgrey')
            
    # File upload
    upload_file = None
    file_name = None

    # creating csv file or not
    if not create_csv:
        file_name = "hist.png"
        ax.hist(data, range=[1, 100], edgecolor='#E6E6E6', color='#EE6666')
        plt.savefig(file_name, facecolor="#36393F")

    else:
        file_name = "roll_data.csv"
        counts, bins, bars = ax.hist(data, bins=range(1, 102, 1), edgecolor='#E6E6E6', color='#EE6666')
        data_file_list = list(zip(bins, counts))
        
        #write to file
        with open(file_name, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data_file_list)


    upload_file = discord.File(file_name)

    if upload_message is None:
        upload_message = file_name

    print("Uploading file")
    await message.channel.send(upload_message, file=upload_file)
    print("File sent")


    if not create_csv:
        #print stats
        num_rolls = len(data)
        mean = np.mean(data)
        median = np.median(data)
        mode = np.bincount(data).argmax()
        mode_frequency = data.count(mode)

        info_str = title + " Stats\nRolls examined: " + str(num_rolls) + "\nMean: " + str(mean) + "\nMedian: " + str(median) + "\nMode: " + str(mode) + "\nMode frequency: " + str(mode_frequency)
        await message.channel.send("```\n" + info_str + "\n```")



client.run(token)

