import asyncio
import itertools
import json
import operator
from random import shuffle
from random import choices
import sched
import string
import time
import websockets

with open('conf.json') as conf:
    data = json.load(conf)
    
port = int(data["wsport"])
games = {}

# IF WEBSOCKETS ARENT SENDING:
# MAKE SURE TO AWAIT WEBSOCKET.SEND()
# times this mistake's been made: 3

# must match order of create.html
roles = ['Villager',
         'Monkey',
         'Seer',
         'Werewolf',
         'Doctor']

# when adding roles, do:
# 1. update the roles variable above with attention to priority
# 2. add a class for the role
# 3. update static_role_classes with the class for your role
# 4. update create.html (if you haven't already done so in #1)
# 5. edit win detection as needed (especially if you added a new class_type)

class Player:
    def __init__(self, name, player_id, websocket):
        self.name = name
        self.player_id = player_id
        self.websocket = websocket
        self.status = "alive"
        self.role = None
        self.move = ["","","",""]
        
    async def set_role(self, role):
        self.role = role
        print(role)
        await self.websocket.send("gamechat You are the " + roles[self.role])

    async def kill(self, game):
        self.status = "dead"
        await self.websocket.send("disablechat")
        await game.broadcast(Player("null", "null", "null"), "gamechat " + self.name + " has died!")
        await game.broadcast(Player("null", "null", "null"), "gamechat " + self.name + " was the " + roles[self.role] + ".")
        



        
class Villager:
    instructions = "Villagers cannot do anything during the nighttime. Hope you survive!"

    def __init__(self):
        self.class_type = "innocent"
        pass

    async def send_nighttime_cmd(self, game, target_player):
        pass

    async def register_move(self, game, target_player, button_pressed):
        move = ["","","",""]





class Seer:
    instructions = "Seers can see any one person's role during nighttime. Only you will be shown the role"
    nighttime_cmd = "Choose;one;person;to;see;their;role."

    def __init__(self):
        self.class_type = "innocent"
        pass
    
    async def send_nighttime_cmd(self, game, target_player):
        data = ';'.join(sorted([player.name for player in game.players if player.player_id != target_player.player_id and player.status == "alive"]))
        await target_player.websocket.send("showbuttons " + Seer.nighttime_cmd + " " + data)

    async def register_move(self, game, target_player, button_pressed):
        target = next((player for player in game.players if player.name == button_pressed), None)
        if target is not None:
            await target_player.websocket.send("gamewhisper " + target.name + " is the " + roles[target.role])
            target_player.move = ["", "", "", ""]



            
    
class Werewolf:
    instructions = "Werewolves can kill at nighttime."
    nighttime_cmd = "Choose;one;person;to;kill." #';' to avoid confusion with spaces
    has_nighttime_cmd = True

    def __init__(self):
        self.class_type = "killer"
    
    async def send_nighttime_cmd(self, game, target_player):
        data = ';'.join(sorted([player.name for player in game.players if player.player_id != target_player.player_id and player.status == "alive"]))
        await target_player.websocket.send("showbuttons " + Werewolf.nighttime_cmd + " " + data)

    async def register_move(self, game, target_player, button_pressed):
        deadguy = next((player for player in game.players if player.name == button_pressed), None)
        if deadguy is not None:
            deadguy.status = "dying"
            target_player.move = ["","","",""]





class Doctor:
    instructions = "Doctors can protect someone from possible death at nighttime."
    nighttime_cmd = "Choose;one;person;to;protect."

    def __init__(self):
        self.class_type = "innocent"

    async def send_nighttime_cmd(self, game, target_player):
        data = ';'.join(sorted([player.name for player in game.players if player.player_id != target_player.player_id and player.status == "alive"]))
        await target_player.websocket.send("showbuttons " + Doctor.nighttime_cmd + " " + data)

    async def register_move(self, game, target_player, button_pressed):
        healguy = next((player for player in game.players if player.name == button_pressed), None)
        if healguy is not None and not healguy.status == "dead":
            healguy.status = "alive"
            target_player.move = ["","","",""]





class Monkey:
    instructions = "Monkeys can become another person's role for the rest of the game."
    nighttime_cmd = "Choose;one;person;whose;role;you;want;to;become."

    def __init__(self):
        self.class_type = "innocent"

    async def send_nighttime_cmd(self, game, target_player):
        data = ';'.join(sorted([player.name for player in game.players if player.player_id != target_player.player_id]))
        await target_player.websocket.send("showbuttons " + Monkey.nighttime_cmd + " " + data)

    async def register_move(self, game, target_player, button_pressed):
        roleguy = next((player for player in game.players if player.name == button_pressed), None)
        if roleguy is not None:
            target_player.status = roleguy.status
            await target_player.websocket.send("gamewhisper You are the " + roles[roleguy.role])



                        
        
static_role_classes = [Villager(),
                       Monkey(),
                       Seer(),
                       Werewolf(),
                       Doctor()]





class Game:
    def __init__(self, args):
        self.data = []
        self.data = [int(x) for x in args[1:len(args)-1]]
        self.totalPlayers = int(args[len(args) - 1])
        self.players = []
        self.lock_game = False
        self.game_state = 0
        self.masterviews = []

    async def add_player(self, player):
        self.players.append(player)
        await self.broadcast(player.player_id, "gamechat " + player.name + " has joined the game!")
        playersLeft = self.totalPlayers - len(self.players)
        
        if (len(self.players) == self.totalPlayers):
            lock_game = True
            await self.broadcast(Player("null", "null", "null"), "status green Assigning Roles")
            self.game_state = 1
        else:
            await self.broadcast(Player("null", "null", "null"), "status green " + str(playersLeft) + " players needed to start!")
            await self.broadcast(Player("null", "null", "null"), "gamestate Pre-Game Chat")

    def check_id_uniqueness(self, player_id):
        try:
            for player in self.players:
                if player_id == player.player_id:
                    return False
            return True
        
        except NameError:
            return True

    async def broadcast(self, player_id, message):
        for recipient in self.players:
            if (not player_id == recipient.player_id):
                await recipient.websocket.send(message)

        for recipient in self.masterviews:
            await recipient.websocket.send(message)

    async def updateMasterviews(self):
        print("ha")
        sortedPlayers = sorted(self.players, key=lambda x: x.name, reverse=False)
        print("ha")
        formattedAlive = ';'.join(player.name for player in sortedPlayers if player.status == "alive")
        print("ha")
        formattedDead = ';'.join(player.name for player in sortedPlayers if player.status == "dead")
        print("ha")
        formattedRoles = ';'.join(roles[player.role] for player in sortedPlayers if player.status == "dead")
        if (formattedAlive == ""):
            formattedAlive = "_"
        if (formattedDead == ""):
            formattedDead = "_"
            formattedRoles = "_"    

        print("why")
        for recipient in self.masterviews:
            print("test")
            await recipient.websocket.send("statusupdate " + formattedAlive + " " + formattedDead + " " + formattedRoles)

    def get_ids(self):
        try:
            ids = []
            for player in self.players:
                ids.append(player.player_id)
            return ids
        except NameError:
            return None

    def verify_player(self, player_id):
        return player_id in self.get_ids()

    def get_player(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
        
    async def update(self):
        if (self.game_state == 1): # assigning roles
            await self.assign_roles()
            self.game_state = 2

            await self.updateMasterviews()

        elif (self.game_state == 2): # nighttime prep
            await self.broadcast(Player("null", "null", "null"), "timer 30 seconds till Daytime")
            await self.broadcast(Player("null", "null", "null"), "gamestate Nighttime")
            await self.nighttime_role_prep()
            self.time0 = time.time()
            
            self.game_state = 3
            
        elif (self.game_state == 3): # nighttime
            if (time.time() - self.time0 > 30):
                self.game_state = 4

        elif (self.game_state == 4): # daytime prep
            nobody_has_died = True
            
            for player in self.players:
                await static_role_classes[player.role].register_move(self, player, player.move[3])
                
            print("please")
            # yes i know this looks ugly but DO NOT COMBINE THE TWO LOOPS
            i = 0
            while i < len(self.players):
                if (self.players[i].status == "dying"):
                    nobody_has_died = False
                    await self.players[i].kill(self)
                i += 1

            if (nobody_has_died):
                await self.broadcast(Player("null", "null", "null"), "gamechat " + "Nobody has died.")
                
            result = await check_for_win(self)
            if result != "null":
                await self.broadcast(Player("null", "null", "null"), "gamechat " + "The " + result + " have won!")
                self.game_state = 9
            else:
                await self.broadcast(Player("null", "null", "null"), "timer 90 seconds till Voting Time")
                await self.broadcast(Player("null", "null", "null"), "gamestate Daytime")
                await self.broadcast(Player("null", "null", "null"), "hidebuttons")
                self.time0 = time.time()
                self.game_state = 5

            await self.updateMasterviews()

        elif (self.game_state == 5): # daytime
            if (time.time() - self.time0 > 90):
                self.game_state = 6

        elif (self.game_state == 6): # voting time prep
            await self.broadcast(Player("null", "null", "null"), "timer 30 seconds of Voting Time")
            await self.broadcast(Player("null", "null", "null"), "gamestate Voting Time")
            data = ';'.join(sorted([player.name for player in self.players if player.status == "alive"]))
            for player in self.players:
                if player.status == "alive":
                    await player.websocket.send("showbuttons " + "Vote;for;who;you;want;to;execute!" + " " + data)
            self.time0 = time.time()
            self.game_state = 7

        elif (self.game_state == 7): # voting time
            if (time.time() - self.time0 > 30):
                self.game_state = 8

        elif (self.game_state == 8): # execution time
            contestants = [player.name for player in self.players if player.status == "alive"]
            votes = [0] * len(contestants)
            for player in self.players:
                if (not player.move[3] == ""):
                    print("registered one vote for " + player.move[3])
                    player.move = ["", "", "", ""]
                    votes[contestants.index(player.move[3])] += 1
                    
            sorted_votes = votes
            sorted_votes.sort(reverse = True)
            if (len(sorted_votes) != 1 and sorted_votes[0] == sorted_votes[1]):
                await self.broadcast(Player("null", "null", "null"), "gamechat Tie vote! No one has died.")
            else:
                deadguy = contestants[votes.index(sorted_votes[0])]
                for player in self.players:
                    if player.name == deadguy:
                        await player.kill(self)
                        await self.broadcast(Player("null", "null", "null"), "gamechat " + deadguy + " has been voted guilty! They have died.")
            
            await self.broadcast(Player("null", "null", "null"), "hidebuttons")

            result = await check_for_win(self)
            if result != "null":
                await self.broadcast(Player("null", "null", "null"), "gamechat " + "The " + result + " have won!")
                self.game_state = 9
            else:
                self.game_state = 2

            await self.updateMasterviews()

        elif (self.game_state == 9): # game end
            for player in players:
                await self.broadcast(Player("null", "null", "null"), "gamestate Game has ended!")
                await self.broadcast(Player("null", "null", "null"), "gamechat " + player.name + " was the " + roles[player.role] + ".")

    async def nighttime_role_prep(self):
        for player in self.players:
            role = player.role
            print("role: " + str(role))

            await static_role_classes[role].send_nighttime_cmd(self, player)
            
    async def assign_roles(self):
        shuffle(self.players)
        
        cursor = 0
        current_role = 0
        for datum in self.data:
            print(datum)
            for player in self.players[cursor:cursor + datum]:
                print(current_role)
                await player.set_role(current_role)
            cursor += datum
            current_role += 1

    async def add_masterview(self, masterview):
        self.masterviews.append(masterview)
        





async def check_for_win(game):
    players = [static_role_classes[player.role].class_type for player in game.players if player.status == "alive"]
    numInnocent = players.count("innocent")
    numKiller = players.count("killer")
    
    if (numKiller > numInnocent):
        return "Killers"
    elif (numKiller == 0):
        return "Innocent"
    else:
        return "null"



    
    
async def on_connection(websocket, path):
    print("Received connection.")
    
    async for message in websocket:
        print("Received message: " + message)
        args = message.split()

        if (args[0] == "verify"):
            await verify(args, websocket)

        if (args[0] == "creategame"):
            await create_game(args, websocket)

        if (args[0] == "join"):
            await join_game(args, websocket)

        if (args[0] == "chat"):
            await chat(args, websocket)

        if (args[0] == "buttonclick"):
            games[args[1]].get_player(args[2]).move = args

        if (args[0] == "masterjoin"):
            await master_join(args, websocket)




async def master_join(args, websocket):
    if (args[1] in games):
        player_id = list(itertools.islice(gen_id(games[args[1]].get_ids(), 8), 1))[0]
        await games[args[1]].add_masterview(Player(args[2], player_id, websocket))
        
    



   
async def register_move(args):
    player = games[args[1]].get_player(args[2])
    static_role_classes(player.id).register_move(self, this, player, player.move[3])




        
async def verify(args, websocket):
    if len(args) != 3:
        await websocket.send("verifydeny Please enter a name.")
    elif args[1] not in games:
        await websocket.send("verifydeny Invalid link!")
    else:
        await websocket.send("verifyaccept")




        
async def create_game(args, websocket):
    game_id = list(itertools.islice(gen_id(games, 8), 1))[0]
    games[game_id] = Game(args)
    
    print(game_id)
    await websocket.send("createaccept " + game_id)




    
async def join_game(args, websocket):
    if (args[1] in games and not games[args[1]].lock_game):
        player_id = list(itertools.islice(gen_id(games[args[1]].get_ids(), 8), 1))[0]
        await games[args[1]].add_player(Player(args[2], player_id, websocket))
        await websocket.send("joinaccept " + player_id)
    else:
        await websocket.send("joindeny An unexpected error has occurred.")





def gen_id(history, id_length):
    charset = string.ascii_lowercase + string.digits
    while True:
        new_id = "".join(choices(charset, k=8))
        if new_id not in history:
          yield new_id





async def chat(args, websocket):
    if games[args[1]].verify_player(args[2]):
        await games[args[1]].broadcast(args[2], "chat " + games[args[1]].get_player(args[2]).name + ": " + ''.join(args[3:]))





async def game_tick():
    while True:
        for game_id in games:
            await games[game_id].update()
            
        await asyncio.sleep(1)





start_server = websockets.serve(on_connection, '0.0.0.0', port)

print("Server started on port " + str(port))

task = asyncio.get_event_loop().create_task(game_tick())
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
