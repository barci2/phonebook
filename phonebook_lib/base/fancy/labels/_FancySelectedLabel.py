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
from ... import constants as c
from ._FancyLabel import FancyLabel
from ..layouts import *

##############
# Main Class #
##############
class FancySelectedLabel(FancyLabel):
    def __init__(self):
        super().__init__("")
    def setSelected(self,x,n):
        self.setText("Selected:  "+str(x)+'/'+str(n) if x else "")
