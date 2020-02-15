from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path
import random

comparable_id_set=set()

class Comparable():
    def __init__(self):
        global comparable_id_set
        self.comparable_id=random.randint(0,2**64-1)
        while self.comparable_id in comparable_id_set:
            self.comparable_id=random.randint(0,2**64-1)
        comparable_id_set.add(self.comparable_id)

    def __del__(self):
        global comparable_id_set
        comparable_id_set.remove(self.comparable_id)

    def __lt__(self,comparable_object):
        return self.comparable_id<comparable_object.comparable_id

    def __hash__(self):
        return self.comparable_id

    def comparableKey(self):
        raise AssertionError("comparableKey function not defined, must return a value by which to compare the object")
