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
        self.map = Generator(500, 500, 0.05).getMap()


        self.chars = {
            "solids": ["#", "O"],
            "wall": "#",
            "empty": " ",
            "player": "@"
        }

        self.windowSize = (24 - 2, 80 - 2) # (y, x) - borders
        

    def acceptClients(self):
        while True:
            clientsocket, address = self.s.accept()
            player_id = time.time()
            self.players[player_id] = Player(player_id, clientsocket)

            print(f'Connection from {address}. Assigning to player {player_id}')
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
                    data += player.clientsocket.recv(1024).decode('utf-8')

                    if len(data) and data[-1] == ";":
                        break

            except:
                player.disconnect()
                self.players.pop(player_id)

                break

            # try:
            task = json.loads(data[:-1])
            data = ""
            if task['a'] == 'm': # If action is m: move
                self.movePlayer(player, task['p']) # Move player to direction set in task payload p, 0,1,2,3

            # except:
            #     pass

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

        if not self.getMapTitle(next_position[0], next_position[1]) in self.chars["solids"]:
            player.position = next_position

    def getMapTitle(self, y, x):
        if 0 <= y <= (len(self.map) - 1) and 0 <= x <= (len(self.map[0]) - 1): 
            return self.map[y][x]
        else:
            return None


    def getWindow(self, current_player):
        window = []

        max_y_index = len(self.map) - 1
        max_x_index = len(self.map[0]) - 1

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

        # Render map lines
        for line in range(start_title[0], start_title[0] + self.windowSize[0]):
            window.append(list(self.map[line][start_title[1]:(start_title[1] + self.windowSize[1])]))

        # Render players
        for player in self.players:
            player_object = self.players[player]
            if start_title[0] <= player_object.position[0] <= (start_title[0] + self.windowSize[0]) and start_title[1] <= player_object.position[1] <= (start_title[1] + self.windowSize[1]):
                window[player_object.position[0] - start_title[0]][player_object.position[1] - start_title[1]] = self.chars['player']

        for line in range(0, len(window)): # Turn into a string
            window[line] = "".join(window[line])

        return window

    def updateClients(self):
        try:
            for player in self.players:
                self.players[player].clientsocket.send(bytes(json.dumps(self.getWindow(self.players[player])) + ";", "utf-8"))

        except:
            pass

    def start(self):
        threading.Thread(target = self.acceptClients, daemon = True).start()
        return self