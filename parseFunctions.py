















'''
    try:
        roll = Roll(dice, , message.author, message.created_at)
    except ValueError as e:
        print(e)
        return 

    # we know it was a valid roll command - save the user that rolled
    global rollers

    # if we didnt already have them, add them
    if message.author not in rollers:
        rollers = np.append(rollers, Roller(message.author))
    
    # find the user that rolled
    roller_user_names = []

    for roller in rollers:
        roller_user_names.append(get_user_nick(roller.user))

    roller = np.where(roller_user_names == get_user_nick(message.author))

    print(roller_user_names.index(get_user_nick(message.author)))
    print(roller_user_names)
    print(get_user_nick(message.author))
    print(roller)

    
    if len(roll.rolls) == 1:
        await message.channel.send("@" + str(get_user_nick(message.author)) + " rolled " + str(roll) + ".")
    else:
        add_message = "("
        i = 0
        while i < len(roll.rolls):
            add_message = add_message + str(roll.rolls[i])

            if i != len(roll.rolls)-1:
                add_message = add_message + " + "
            i = i+1

        add_message = add_message + " = " + str(roll) + ")"
        await message.channel.send("@" + str(get_user_nick(message.author)) + " rolled " + str(roll) + ". " + add_message)
'''
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
        afterDate = today - datetime.timedelta(hours = 1)
    elif date == "today":
        afterDate = today - datetime.timedelta(days = 1)
    elif date == "week":
        afterDate = today - datetime.timedelta(weeks = 1)
    elif date == "month":
        afterDate = today - datetime.timedelta(days = today.day)
    elif date == "year":
        afterDate = today - datetime.timedelta(days = int(today.strftime("%j")))
        
    upload_message = "Rolls since " + utc_to_local(afterDate, pytz.timezone('US/Eastern')).strftime("%b %d %Y %H:%M:%S")

    await create_histogram(message, title, await get_roll_history(user, message.channel, afterDate=afterDate), upload_message, create_csv="file" in args)