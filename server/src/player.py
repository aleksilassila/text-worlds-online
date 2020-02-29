class Player:
    def __init__(self, player_id, clientsocket):
        self.clientsocket = clientsocket
        self.player_id = player_id
        self.position = (400, 400) # y / x
        self.health = 5
        self.bullets = []

    def disconnect(self):
        self.clientsocket.close()
        print(f'Player {self.player_id}: Disconnected')
