from Roll import Roll

class Roller:

    def __init__(self, name):
        self._rolls = []
        self._name = name



    def add_roll(self, roll):
        self._rolls.append(roll)

    def clear_rolls(self):
        self._rolls = []

    @property
    def rolls(self):
        return self._rolls

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return str(self._name) + str(self._rolls)

    def __str__(self):
        return str(self._name) + str(self._rolls)