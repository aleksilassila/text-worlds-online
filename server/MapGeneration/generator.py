import noise
from src.barricade import Barricade

class Generator:
    def __init__(self, width=int, height=int):
        self.height = height
        self.width = width
        self.overworld = []
        self.underworld = []

    def getOverworld(self):
        self.overworld = self.generateHeights(sensitivity=0.3, scale=0.02, octaves=2, persistence=1)
        grass = self.generateDepths(sensitivity=-0.1, scale=0.02, octaves=2, persistence=1)
        teleports = self.generateDepths(sensitivity=-0.5, scale=0.02, octaves=5, persistence=1, char="H") 

        # Merge layers
        for y in range(0, self.height):
            for x in range(0, self.width):
                if teleports[y][x] == "H":
                    self.overworld[y][x] = "H"
                elif grass[y][x] == ".":
                    self.overworld[y][x] = "."

        return self.overworld

    def getUnderworld(self):
        self.underworld = self.generateHeights(sensitivity=0, scale=0.02, octaves=2, persistence=1)
        grass = self.generateDepths(sensitivity=-0.3, scale=0.02, octaves=2, persistence=1, char="_")
        teleports = self.generateDepths(sensitivity=-0.5, scale=0.02, octaves=5, persistence=1, char="H") 

        # Merge layers
        for y in range(0, self.height):
            for x in range(0, self.width):
                if teleports[y][x] == "H":
                    self.underworld[y][x] = "H"
                elif grass[y][x] == "_":
                    self.underworld[y][x] = "_"

        return self.underworld

    def getBarricades(self, octaves=1, persistence=0.5, lacunarity=2.0, sensitivity=0.65, scale=0.05, underworld=False):
        barricades = {}

        for y in range(0, self.height):
            for x in range(0, self.width):
                if noise.snoise2(x * scale * 3, y * scale * 3, persistence=persistence,lacunarity=lacunarity, octaves=octaves) > sensitivity:
                    if not underworld: # Generate for overworld
                        if not self.overworld[y][x] in ["#", "H"]:
                            barricades[f"{y}{x}"] = Barricade(y, x, f"{y}{x}") # Assign id to each barricade based on initial coordinates
                    else: # Generate for underworld
                        if not self.underworld[y][x] in ["#", "H"]:
                            barricades[f"{y}{x}"] = Barricade(y, x, f"{y}{x}") # Assign id to each barricade based on initial coordinates

        return barricades

    def generateHeights(self, octaves=1, persistence=0.5, lacunarity=2.0, sensitivity=0.3, scale=0.05, char="#"):
        noiseMap = []

        for y in range(0, self.height):
            noiseMap.append([])

            for x in range(0, self.width):
                if noise.snoise2(x * scale, y * scale, persistence=persistence,lacunarity=lacunarity, octaves=octaves) > sensitivity:
                    noiseMap[y].append(char)
                else:
                    noiseMap[y].append(" ")

        return noiseMap

    def generateDepths(self, octaves=1, persistence=0.5, lacunarity=2.0, sensitivity=0.3, scale=0.05, char="."):
        noiseMap = []

        for y in range(0, self.height):
            noiseMap.append([])

            for x in range(0, self.width):
                if noise.snoise2(x * scale, y * scale, persistence=persistence,lacunarity=lacunarity, octaves=octaves) < sensitivity:
                    noiseMap[y].append(char)
                else:
                    noiseMap[y].append(" ")

        return noiseMap

    # Testing
    def test(self, o=1, p=0.5, l=2.0, s=0.3, sc=0.05):
        noiseMap = []

        for y in range(0, self.height):
            noiseMap.append("")

            for x in range(0, self.width):
                if noise.snoise2(x * sc, y * sc, persistence=p,lacunarity=l, octaves=o) > s:
                    noiseMap[y] += "#"
                else:
                    noiseMap[y] += " "

        self.printMap(noiseMap)

    def printMap(self, noiseMap):
        for line in range(0, len(noiseMap) - 1):
            print(noiseMap[line])
"""
from MapGeneration.generator import Generator
g = Generator(240, 80, 0.05)
g.test()

For caves
g.test(s=0, sc=0.02, o=2, p=1)
For overworld
g.test(s=3, sc=0.02, o=2, p=1)

from MapGeneration.generator import Generator
g = Generator(80, 24, 0.05)
g.generateBase()
g.generateGrass()
g.printMap()
"""