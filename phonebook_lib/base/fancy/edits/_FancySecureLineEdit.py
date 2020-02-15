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

from .._style_constants import *
from ._FancyLineEdit import FancyLineEdit

##############
# Main Class #
##############
class FancySecureLineEdit(FancyLineEdit):
    def __init__(self,placeholder="",text=""):
        super().__init__(placeholder,text)
        self.setEchoMode(QLineEdit.Password)
