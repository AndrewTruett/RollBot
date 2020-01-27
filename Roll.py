import random

class Roll:
    """This class represents a single roll instance, created from typing a roll command"""
    def __init__(self, dice, roll, created_at):
        self._dice = dice #the 100 in d100
        self._roll = roll
        self._created_at = created_at


        # make sure values are reasonable
        if roll < 1:
            raise ValueError("Number of dice cannot be less than 1")


        if dice < 2:
            raise ValueError("Die value cannot be less than 2")

        if dice > 1000000:
            raise ValueError("Die value cannot exceed 1,000,000")


    @property
    def dice(self):
        return self._dice

    @property
    def roll(self):
        return self._roll

    @property
    def created_at(self):
        return self._created_at

    def __str__(self):
        return str(self._roll)

    def __repr__(self):
        return str(self._roll)