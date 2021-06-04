import discord
import json
client = discord.Client()


@client.event
async def on_ready():
    print("Bot ready!")

def add_help(message):
    return message.channel.send('To add a game type: .add <Match history link> <Team Tag1> <Team Tag2> <Side of Team1(Blue, Red)>')

def matchhistory_cleaner(message):
    if message.startswith('https://'):
        message = message[8:]
    if message.startswith('www.'):
        message = message[4:]
    if message.startswith('matchhistory.euw.leagueoflegends.com/'):
        message = message[37:]
    return message[23:33]

def add(message):
    split = message.content.split(' ')
    if len(split) != 5:
        return add_help(message)
    with open('teams.json', 'r') as f:
        tags = json.load(f)
    teamnames = list()
    for key in tags.keys():
        teamnames.append(key)
    split[2] = split[2].upper()
    split[3] = split[3].upper()
    if 'matchhistory.euw.leagueoflegends.com/en/' not in split[1]:
        return message.channel.send("You need a valid match history link that starts with: https://matchhistory.euw.leagueoflegends.com/en/#match-history/EUW1/")
    if split[2] not in teamnames:
        return message.channel.send('You need to type the tag of your team!')
    if split[3] not in teamnames:
        return message.channel.send('You need to type the tag of the other team!')
    if split[4] != ('red' or 'blue'):
        return message.channel.send('Specify which side you were in that game!')
    tmpDict = dict()
    tmpDict['mh'] = matchhistory_cleaner(split[1])
    tmpDict['team1'] = split[2]
    tmpDict['team2'] = split[3]
    tmpDict['side'] = split[4]
    with open('add.json', 'w') as f:
        json.dump(tmpDict, f)
    try:
        exec(open('Main.py').read())
    except:
        return message.channel.send('Something strange happened... (Game probably already added.)')
    return message.channel.send('Done!')

def team(message):
    split = message.content.split(' ')
    split[1] = split[1].upper()
    f = open('teams.json')
    teams = json.load(f)
    if len(split) == 7:
        tmpDict = dict()
        tmpDict['top'] = split[2]
        tmpDict['jungle'] = split[3]
        tmpDict['mid'] = split[4]
        tmpDict['adc'] = split[5]
        tmpDict['support'] = split[6]
        teams[split[1]] = tmpDict
        with open('teams.json', 'w') as file:
            json.dump(teams, file)
    if len(split) == 4:
        try:
            teams[split[1]][split[2]] = split[3]
            with open('teams.json', 'w') as file:
                json.dump(teams, file)
            return message.channel.send(f'{split[2]} of team {split[1]} changed.')
        except:
            return message.channel.send('Team does not exist. .tags to get a list of all teams.')
    return message.channel.send('Team added!')

def tags(message):
    f = open('teams.json')
    teams = json.load(f)
    str = "Currently registered teams: "
    for team in teams:
        str += team + " "
    return message.channel.send(str)

def help(message):
    add = "To add a game type: `.add <Match history link> <Team Tag1> <Team Tag2> <Side of Team1(Blue, Red)>`\n"
    team = "To add a team type: `.team <Team Tag> <Toplaner> <Jungler> <Midlaner> <Adc> <Support>`\n"
    change = "To change a player type: `.team <Team Tag> <Lane> <New Player Name>`\n"
    tags = "To see all tags type: `.tags\n`"
    return message.channel.send(add + team + change + tags)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('.help'):
        await help(message)
    if message.content.startswith('.add'):
        await add(message)
    if message.content.startswith('.team'):
        await team(message)
    if message.content.startswith('.tags'):
        await tags(message)
client.run(Settings.API_DISCORD)
