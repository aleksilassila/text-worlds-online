import time, socket, threading, json, math
from src.player import Player
from MapGeneration.generator import Generator

class Server:
    def __init__(self, ip, port, args):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((ip, int(port)))
        self.s.listen(16)

        self.players = {}

        self.tickrate = args.tickrate
        self.max_players = args.players
        # self.map_json = json.loads(open(args.map, 'r').read())
        # self.map = self.map_json["data"]

        gen = Generator(500, 500, 400)
        self.map = [gen.getOverworld(), gen.getUnderworld()]
        self.barricades = [gen.getBarricades(), gen.getBarricades(underworld=True, octaves=2)]

        self.chars = {
            "solids": ["#", "O", "@"],
            "wall": "#",
            "barricade": "O",
            "teleport": "H",
            "empty": " ",
            "player": "@"
        }

        self.windowSize = (24 - 2, 80 - 2) # (y, x) - borders
        

    def acceptClients(self):
        while True:
            clientsocket, address = self.s.accept()
            player_id = time.time()
            self.players[player_id] = Player(player_id, clientsocket)

            print(f'[+] Player {player_id}: Connected from {address}')
            clientsocket.send(bytes(json.dumps({
                'h': self.windowSize[0],
                'w': self.windowSize[1],
                't': self.tickrate
            }) + ";", "utf-8"))
            threading.Thread(target = self.listenToPlayer, args = (player_id, ), daemon = True).start()

    def listenToPlayer(self, player_id):
        player = self.players[player_id]
        
        while True:
            data = ""
            try:
                while True:
                    data += player.clientsocket.recv(1).decode('utf-8')

                    if len(data) and data[-1] == ";":
                        break


                task = json.loads(data[:-1])
                data = ""
                if task['a'] == 'm': # If action is m: move
                    self.movePlayer(player, task['p']) # Move player to direction set in task payload p, 0,1,2,3
                elif task['a'] == 'p':
                    self.pickBlock(player)
            except OSError:
                break
            except Exception as e:
                print(e)

    def movePlayer(self, player, direction):
        current_position = player.position # (y, x)
        next_position = (0, 0) # (y, x)

        if direction == 0:
            next_position = (current_position[0] - 1, current_position[1])
        elif direction == 1:
            next_position = (current_position[0], current_position[1] + 1)
        elif direction == 2:
            next_position = (current_position[0] + 1, current_position[1])
        elif direction == 3:
            next_position = (current_position[0], current_position[1] - 1)

        next_block = self.getMapTitle(next_position[0], next_position[1], player.level)
        if not next_block in self.chars["solids"] and next_block:
            player.position = next_position
            if next_block == self.chars["teleport"]:
                if player.level == 0: # This code is garbage
                    player.level = 1
                else:
                    player.level = 0

        player.facing = direction

    def pickBlock(self, player):
        if player.facing == 0:
            title = (player.position[0] - 1, player.position[1])
        elif player.facing == 1:
            title = (player.position[0], player.position[1] + 1)
        elif player.facing == 2:
            title = (player.position[0] + 1, player.position[1])
        elif player.facing == 3:
            title = (player.position[0], player.position[1] - 1)
        
        if player.picked_block:
            if not self.getMapTitle(title[0], title[1], player.level) in self.chars["solids"]:
                player.picked_block.is_picked = False
                player.picked_block.position = (title[0], title[1])

                # Update barricades list key with the new correct one based on new position
                self.barricades[player.level][f"{title[0]}/{title[1]}"] = self.barricades[player.picked_block.level].pop(player.picked_block.barricade_id)
                self.barricades[player.level][f"{title[0]}/{title[1]}"].barricade_id = f"{title[0]}/{title[1]}"
                player.picked_block.level = player.level

                player.picked_block = None

        elif self.getMapTitle(title[0], title[1], player.level) == self.chars["barricade"]:
            b = self.barricades[player.level][f"{title[0]}/{title[1]}"]
            b.is_picked = True
            player.picked_block = b

    def getMapTitle(self, y, x, level):
        player_positions = []

        for player in self.players:
            player_positions.append(self.players[player].position)

        if 0 <= y <= (len(self.map[level]) - 1) and 0 <= x <= (len(self.map[level][0]) - 1):
            if f"{y}/{x}" in self.barricades[level] and \
               not self.barricades[level][f"{y}/{x}"].is_picked:
                return self.chars["barricade"]
            elif (y, x) in player_positions:
                return self.chars["player"]
            else:
                return self.map[level][y][x]
        else:
            return None


    def getWindow(self, current_player):
        window = []

        max_y_index = len(self.map[current_player.level])
        max_x_index = len(self.map[current_player.level][0])

        if current_player.position[0] + (math.ceil(self.windowSize[0]/2)) > max_y_index:
            start_y = max_y_index - self.windowSize[0]
        elif current_player.position[0] - (math.ceil(self.windowSize[0]/2)) < 0:
            start_y = 0
        else:
            start_y = current_player.position[0] - (math.ceil(self.windowSize[0]/2))
        
        if current_player.position[1] + (math.ceil(self.windowSize[1]/2)) > max_x_index:
            start_x = max_x_index - self.windowSize[1]
        elif current_player.position[1] - (math.ceil(self.windowSize[1]/2)) < 0:
            start_x = 0
        else:
            start_x = current_player.position[1] - (math.ceil(self.windowSize[1]/2))


        start_title = (start_y, start_x)

        # Render map rows
        for row in range(start_title[0], start_title[0] + self.windowSize[0]):
            window.append(self.map[current_player.level][row][start_title[1]:(start_title[1] + self.windowSize[1])])

        try: # These may be changed during iteration by other threads, thats why try
            # Render barricades
            for barricade in self.barricades[current_player.level]:
                barricade_object = self.barricades[current_player.level][barricade]
                # Check if barricade is in visible window
                if start_title[0] <= barricade_object.position[0] < (start_title[0] + self.windowSize[0]) and \
                   start_title[1] <= barricade_object.position[1] < (start_title[1] + self.windowSize[1]) and \
                   not barricade_object.is_picked:
                    window[barricade_object.position[0] - start_title[0]][barricade_object.position[1] - start_title[1]] = self.chars['barricade']


            # Render players
            for player in self.players:
                player_object = self.players[player]
                # Check if player is in visible window
                if start_title[0] <= player_object.position[0] < (start_title[0] + self.windowSize[0]) and \
                   start_title[1] <= player_object.position[1] < (start_title[1] + self.windowSize[1]):
                    window[player_object.position[0] - start_title[0]][player_object.position[1] - start_title[1]] = self.chars['player']
        except:
            pass

        # Get rid of that thing
        for line in range(0, len(window)): # Turn into a string
            window[line] = "".join(window[line])

        return window

    def updateClients(self):
        try: # In case self.players changes during iteration
            for player in self.players:
                player_object = self.players[player]
                try:
                    player_object.clientsocket.send(bytes(json.dumps(
                        {"w": self.getWindow(player_object), "b": player_object.picked_block != None, "l": player_object.level}
                    ) + ";", "utf-8"))
                except:
                    player_object.disconnect()
                    self.players.pop(player_object.player_id)
                    break
        except:
            pass

    def start(self):
        threading.Thread(target = self.acceptClients, daemon = True).start()
        return self