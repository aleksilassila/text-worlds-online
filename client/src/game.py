import curses, argparse, socket, json
from time import sleep
from threading import Thread

class Game:
    def __init__(self, address):
        self.version = "0.3.1"
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address

        self.size = (0, 0) # Screen size (h, w)
        self.map = []

        self.picked = False
        self.level = 0

        self.log = ""


    # Connecting and receiving data

    def connect(self):
        self.s.connect(self.address)

        message = ""
        while True:
            message += self.s.recv(1).decode('utf-8')
            if len(message) and message[-1] == ";":
                if message[:-1] == 'full':
                    print('Session is full.')
                    break
                else:
                    data = json.loads(message[:-1])
                    break

        self.size = (data['h'], data['w'])
        self.tickrate = data['t']

    def update(self): # Update map data
        message = ""

        while True:
            try:
                message += self.s.recv(1).decode('utf-8')

                if message[-1] == ";":
                    parsed = json.loads(message[:-1])
                    self.map = parsed["w"]
                    self.picked = parsed["b"]
                    self.level = parsed["l"]
                    message = ""
            except:
                message = ""



    def listen(self):
        Thread(target = self.update, daemon = True).start()


    # Game mechanics & sending data

    def move(self, direction):
        self.s.send(bytes(json.dumps({'a': 'm', 'p': direction}) + ";", "utf-8")) # Action: Move, payload: direction

    def shoot(self, direction):
        try:
            self.s.send(bytes(json.dumps({'a': 's', 'p': direction}) + ";", "utf-8"))
        except:
            pass

    def pick(self):
        try:
            self.s.send(bytes(json.dumps({'a': 'p'}) + ";", "utf-8"))
        except:
            pass


    # Drawing & Curses

    def addTexts(self):
        self.window.addstr(0, 2, f" Text-Worlds-Online v{self.version} ")
        if self.picked:
            self.window.addstr(self.size[0] + 1, 2, f" Block picked: O ")
        else:
            self.window.addstr(self.size[0] + 1, 2, f" Block picked: ──")
        
        self.window.addstr(self.size[0] + 1, 20, f" Level: {self.level} ")


    def draw(self):
        self.window.erase()
        self.window.border(0)
        self.addTexts()

        if len(self.map):
            for line in range(0, self.size[0]):
                self.window.addstr(line + 1, 1, self.map[line])

    def getPlayerInput(self, stdscr):
        self.window = curses.newwin(self.size[0] + 2, self.size[1] + 2, 0, 0)
        self.window.keypad(True)
        self.window.timeout(round(1000 / self.tickrate))

        curses.curs_set(0)
        curses.noecho()
        
        while True:
            try:
                key = self.window.getch()

                if key == 87 or key == 119: # w/W, Move
                    self.move(0)
                elif key == 68 or key == 100: # d/D
                    self.move(1)
                elif key == 83 or key == 115: # s/S
                    self.move(2)
                elif key == 65 or key == 97: # a/A
                    self.move(3)
                
                if key == curses.KEY_UP: # Shoot
                    self.shoot(0)
                elif key == curses.KEY_RIGHT:
                    self.shoot(1)
                elif key == curses.KEY_DOWN:
                    self.shoot(2)
                elif key == curses.KEY_LEFT:
                    self.shoot(3)

                if key == 32: # Space
                    self.pick()


            except KeyboardInterrupt:
                break

            self.draw()

    # Start game

    def start(self):
        self.connect()
        self.listen()
        curses.wrapper(self.getPlayerInput)
        return self