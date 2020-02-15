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
from ._FancyIconLabel import FancyIconLabel
from ._FancyLabel import FancyLabel
from ..layouts import *

##############
# Main Class #
##############
class FancyAcquaintanceLabel(QWidget):
    def __init__(self,acquaintance):
        super().__init__()
        self.setContentsMargins(0,0,0,0)
        self.icon=FancyIconLabel(c.acquaintance_icon_file)
        self.label=FancyLabel(c.acquaintance_levels[acquaintance-1])
        self.setLayout(FancyHLayout([self.label,self.icon,0],h_align='l'))

    def setAcquaintance(self,acquaintance):
        self.label.setText(c.acquaintance_levels[acquaintance-1])
