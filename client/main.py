import argparse
from src.game import Game

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="Game server ip")
args = parser.parse_args()

ip_address = (args.ip.split(":")[0], int(args.ip.split(":")[1]))

game = Game(ip_address).start()
print(game.log)