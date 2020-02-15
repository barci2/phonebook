####################
# External Imports #
####################
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

####################
# Internal Imports #
####################

##############
# Main Class #
##############
class FancyButtonGroup(QButtonGroup):
    def __init__(self,buttons):
        super().__init__()
        self.setExclusive(True)
        for button in buttons:
            self.addButton(button)
