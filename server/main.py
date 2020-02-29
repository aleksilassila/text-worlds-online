import time, sys, argparse
from src.server import Server

parser = argparse.ArgumentParser(description = 'Server for Text-Worlds-Online')
parser.add_argument('address', help = 'Server bind address: [ip]:[port]')
parser.add_argument('-p', '--players', default = 4, type = int, help = 'Max players')
parser.add_argument('-m', '--map', default = './map.json', help = 'Json file containing map')
parser.add_argument('-t', '--tickrate', default = 20, type = int, help = 'How many times game state will be updated per second')
args = parser.parse_args()

ip, port = args.address.split(":")

server = Server(ip, port, args).start()

# threading.Thread(target = server.acceptClients, daemon = True).start()

while True:
    try:
        server.updateClients()
        time.sleep(1 / server.tickrate)

    except KeyboardInterrupt:
        for player in server.players:
            server.players[player].disconnect()

        server.s.close()

        sys.exit()