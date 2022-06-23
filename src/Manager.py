import json
from CommandToGamepadMapper import CommandToGamepadMapper
from GamePad import GamePad

config = json.load(open("./config.json", 'rb'))
gameConfig = json.load(open(config["gameConfiguration"], 'rb'))

voting_mode = config["votingMode"]
# Team structure
# {
#    "1️⃣" : {
#       "id" : 0,                                               # Team ID
#       "gamepadMapper: Instance<CommandToGamepadMapper>,       # Instance of CommandToGamepadMapper
#       "members" : ["@Stealthix"],                            # List of members
#       "votes" : ["⬅️","⬅️", "❎"]                           # Holds the currently voted actions for the team       
#    }
# }
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

def add_vote(team, vote):
    teams[team]["votes"].append(vote)

def clear_votes(team):
    teams[team]["votes"] = []

def get_most_voted(team):
    return  max(set(teams[team]["votes"]), key = teams[team]["votes"].count)

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
            add_vote(reaction.emoji, member)
        else:
            execute_action(member, actions[reaction.emoji])

def set_info_message(client):
    message_string = ""
    for team in teams:
        message_string += team + ": " + str(teams[team]["members"]) + "\n"
    client.execute_async_function_parallel(client.set_info_message, message_string)

def setup_discord_bot(discord_client):
    client = discord_client
    client.set_channel(config["channelId"])