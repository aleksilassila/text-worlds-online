class Barricade:
    def __init__(self, y, x, barricade_id):
        self.barricade_id = barricade_id
        self.position = (y, x)
        self.is_picked = False