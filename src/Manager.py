import json
import time
from CommandToGamepadMapper import CommandToGamepadMapper
from GamePad import GamePad

config = json.load(open("./config.json", 'rb'))
gameConfig = json.load(open(config["gameConfiguration"], 'rb'))

voting_mode = config["votingMode"] == 1
teams = {}
for k,v in gameConfig["teams"].items():
    teams[k] = {
        "id": v,
        "gamepadMapper": CommandToGamepadMapper(GamePad()),
        "members": [],
        "votes" : []
    }

actions = gameConfig["actions"]

def add_member(team, member):
    teams[team]["members"].append(member)

def remove_member(team, member):
    teams[team]["members"].remove(member)

def get_members(team):
    return teams[team]["members"]

def get_gamepad_mapper(team):
    return teams[team]["gamepadMapper"]

def execute_action(member, action):
    for team in teams:
        if member in teams[team]["members"]:
            teams[team]["gamepadMapper"].exec_action(action)
            return

def execute_team_action(team, action):
    teams[team]["gamepadMapper"].exec_action(action)

def add_vote(team, vote):
    teams[team]["votes"].append(vote)

def clear_votes(team):
    teams[team]["votes"] = []

def get_most_voted(team):
    if len(teams[team]["votes"]) == 0:
        return ""
    return max(set(teams[team]["votes"]), key = teams[team]["votes"].count)

def handle_voting(client):
    while True:
        if voting_mode:
            for team in teams:
                if len(teams[team]["votes"]) > 0:
                    execute_team_action(team, actions[get_most_voted(team)])
                    clear_votes(team)
        set_info_message(client)
        time.sleep(config["votingTime"])

def handle_reaction(reaction, memberObj):
    member = memberObj.mention
    if reaction.emoji in teams: # if the reaction is a team emoji
        if teams[reaction.emoji].get("members").count(member) > 0: # if the member is already in the team remove him and stop
            remove_member(reaction.emoji, member)
            return
        for team in teams: # remove the member from all other teams
            if teams[team].get("members").count(member) > 0:
                remove_member(team, member)
        add_member(reaction.emoji, member)
        return
    if reaction.emoji in actions: # if the reaction is an action emoji
        if voting_mode:
            # find the team that the member is in
            for team in teams:
                if teams[team].get("members").count(member) > 0:
                    add_vote(team, reaction.emoji)
                    return
        else:
            execute_action(member, actions[reaction.emoji])

def set_info_message(client):
    message_string = ""
    if voting_mode:
        message_string += "Voting mode\nTimer: " + str(config["votingTime"]) + " seconds\n"
    message_string += "**Teams**\n"
    for team in teams:
        message_string += team + ": " + str(teams[team]["members"]) + "\nCurrently voting: " + get_most_voted(team) + "\n\n"
    
    client.execute_async_function_parallel(client.set_info_message, message_string)

def setup_discord_bot(discord_client):
    client = discord_client
    client.set_channel(config["channelId"])

    if voting_mode:
        client.run_parallel(handle_voting, client)