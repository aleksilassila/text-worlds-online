import noise

class Generator:
    def __init__(self, width=int, height=int, scale=int):
        self.height = height
        self.width = width
        self.map = []
        self.scale = scale

    def generateBase(self):
        for y in range(0, self.height):
            self.map.append("")

            for x in range(0, self.width):
                if noise.snoise2(x * self.scale, y * self.scale, persistence=.4,lacunarity=4, octaves=3) > 0.3:
                    self.map[y] += "#"
                else:
                    self.map[y] += " "

    def generateBarricades(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if noise.snoise2(x * self.scale * 3, y * self.scale * 3, persistence=.4,lacunarity=4, octaves=3) > 0.5 and not self.map[y][x] == "#":
                    self.map[y] = list(self.map[y])
                    self.map[y][x] = "O"
                    self.map[y] = "".join(self.map[y])

    def generateGrass(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if noise.snoise2(x * self.scale, y * self.scale, persistence=.4,lacunarity=4, octaves=3) < -0.3 :
                    self.map[y] = list(self.map[y])
                    self.map[y][x] = "."
                    self.map[y] = "".join(self.map[y])

    def printMap(self):
        for line in range(0, len(self.map) - 1):
            print(self.map[line])

    def getMap(self):
        self.generateBase()
        self.generateGrass()
        self.generateBarricades()
        return self.map
"""
g = Generator(80, 24, 0.05)
g.generateBase()
g.generateGrass()
g.printMap()
"""