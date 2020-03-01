class Barricade:
    def __init__(self, y, x, barricade_id, level):
        self.barricade_id = barricade_id
        self.position = (y, x)
        self.level = level
        self.is_picked = False