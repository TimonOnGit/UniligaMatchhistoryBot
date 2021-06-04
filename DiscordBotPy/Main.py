from riotwatcher import LolWatcher, ApiError
from collections import Counter
import json
import pandas as pd
import site
import csv
import ChampionMap
import Settings

#API Key
watcher = LolWatcher(Settings.API_LOL)
region = 'euw1'

#Game to add
with open('add.json', "r") as f:
    game_to_add = json.load(f)

#Opens list of all teams + their players
with open('teams.json', "r") as f:
    teams = json.load(f)

#Find the game by match id
game = watcher.match.by_id(region, game_to_add['mh'])
try:
    with open('mh.log', "r") as f:
        if game_to_add['mh'] in f.read():
            print('Game already added.')
            quit()
except FileNotFoundError:
    print('No mh.log file. It will be added now.')

#Switch case. Returns role for number on scoreboard.
def role(argument):
    switcher = {
        0: 'top',
        1: 'jungle',
        2: 'mid',
        3: 'adc',
        4: 'support'
    }
    return switcher.get(argument%5)

#Adds the game to the team's csv.
def add_to_games_csv(team1, team2, tstats1, tstats2):
    df = pd.DataFrame.from_dict(team1)
    df = df.drop('games')
    csv_str = df.to_csv(header=team1)
    csv_name = f"{game_to_add['team1'].upper()}games.csv"
    with open(csv_name, 'a', newline='') as f:
        f.write(game_to_add['team1'] + ' vs ' + game_to_add['team2'] + ', Top, Jungle, Mid, Adc, Support, ')
        f.write(str(tstats1['win']) + ', ')
        f.write(str(tstats1['time']/100) + 'min\nPlayers')
        f.write(csv_str)
        f.write('\n')
    df = pd.DataFrame.from_dict(team2)
    df = df.drop('games')
    csv_str = df.to_csv(header=team2)
    csv_name = f"{game_to_add['team2'].upper()}games.csv"
    with open(csv_name, 'a', newline='') as f:
        f.write(game_to_add['team2'] + ' vs ' + game_to_add['team1'] + ', Top, Jungle, Mid, Adc, Support,')
        f.write(str(tstats2['win']) + ', ')
        f.write(str(tstats2['time']/100) + 'min\nPlayers')
        f.write(csv_str)
        f.write('\n')

#Adds team stats to tstats1 and 2. Teamstats are stats not done by one player but by the team (first turret, first dragon, etc..)
def teamstats(team1, team2):
    tstats1 = dict()
    tstats2 = dict()
    tstats1['time'] = tstats2['time'] = game['gameDuration']
    if game['teams'][0]['win'] == 'Win':
        if game_to_add['side'] == 'blue':
            tstats1['win'] = 1
            tstats2['win'] = 0
        else:
            tstats1['win'] = 0
            tstats2['win'] = 1
    else:
        if game_to_add['side'] == 'blue':
            tstats1['win'] = 0
            tstats2['win'] = 1
        else:
            tstats1['win'] = 1
            tstats2['win'] = 0
    return tstats1, tstats2

#Appends the game to the two teams csv.
def append_games():
    team1 = Counter()
    team2 = Counter()
    #Saves stats of the parctipant in a Counter object
    for i, participants in enumerate(game['participants']):
        participant_stats = Counter()
        participant_stats['champion'] = ChampionMap.get_champions_name(participants['championId'])
        participant_stats['kills'] = participants['stats']['kills']
        participant_stats['deaths'] = participants['stats']['deaths']
        participant_stats['assists'] = participants['stats']['assists']
        participant_stats['goldEarned'] = participants['stats']['goldEarned']
        participant_stats['wardsPlaced'] = participants['stats']['wardsPlaced']
        participant_stats['totalDamageChampions'] = participants['stats']['totalDamageDealtToChampions']
        participant_stats['games'] = 1
        if i < 5:
            if game_to_add['side'] == 'blue':
                team1[teams[game_to_add['team1']][role(i)]] = participant_stats
            else:
                team2[teams[game_to_add['team2']][role(i)]] = participant_stats
        else:
            if game_to_add['side'] == 'blue':
                team2[teams[game_to_add['team2']][role(i)]] = participant_stats
            else:
                team1[teams[game_to_add['team1']][role(i)]] = participant_stats
    tstats1, tstats2 = teamstats(team1, team2)
    add_to_games_csv(team1, team2, tstats1, tstats2)
    return team1, team2, tstats1, tstats2

#Appends the stats file and adds this game to the stats of the teams.
def append_stats(team1, team2, tstats1, tstats2):
    try:
        f = open('stats.json')
    except:
        pass
    try:
        stats_dict = json.load(f)
    except:
        stats_dict = Counter()
    stats = Counter()

    # Dict zu Counter casten.
    for team in stats_dict:
        tmpCounter = Counter()
        for player in stats_dict[team]:
            if type(stats_dict[team][player]) is not dict:

                tmpCounter[player] = stats_dict[team][player]
            else:
                tmpCounter[player] = Counter(stats_dict[team][player])
        stats[team] = tmpCounter

    #If there are stats for this team already they get updated. Else new stats will be made with this game.
    if game_to_add['team1'] in stats:
        for player in stats[game_to_add['team1']]:
            try:
                for key in team1[player]:
                    if type(stats[game_to_add['team1']][player][key]) is not str:
                        stats[game_to_add['team1']][player][key] += team1[player][key]
                    else:
                        stats[game_to_add['team1']][player][key] += ", " + team1[player][key]
            except:
                pass
    else:
        stats[game_to_add['team1']] = team1

    if game_to_add['team2'] in stats:
        for player in stats[game_to_add['team2']]:
            try:
                for key in team2[player]:
                    if type(stats[game_to_add['team2']][player][key]) is not str:
                        stats[game_to_add['team2']][player][key] += team2[player][key]
                    else:
                        stats[game_to_add['team2']][player][key] += ", " + team2[player][key]
            except:
                pass
    else:
        stats[game_to_add['team2']] = team2

    #Adds teamstats to the stat file. Same premise as before: If there are teamstats already they get appended.
    for key in tstats1:
        if type(tstats1[key]) is not str:
            stats[game_to_add['team1']][key] += tstats1[key]
        else:
            if key not in stats[game_to_add['team1']]:
                stats[game_to_add['team1']][key] = ""
            stats[game_to_add['team1']][key] += ", " + tstats1[key]

    for key in tstats2:
        if type(tstats2[key]) is not str:
            stats[game_to_add['team2']][key] += tstats2[key]
        else:
            if key not in stats[game_to_add['team2']]:
                stats[game_to_add['team2']][key] = ""
            stats[game_to_add['team2']][key] += ", " + tstats2[key]

    with open('stats.json', 'w') as f:
        json.dump(stats, f)

#Main driver code. Appends the game via append_games() and creates stats for this game.
#These stats then get added to the stats via append_stats.
team1, team2, tstats1, tstats2 = append_games()
append_stats(team1,team2, tstats1, tstats2)
#Adds the match history link to log file.
with open('mh.log', "a") as f:
    f.write(game_to_add['mh'] + '\n')
