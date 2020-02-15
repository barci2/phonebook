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

#############
# Init Code #
#############
size=40
font=QFont("Montserrat")
font.setWeight(QFont.Bold)
font.setPointSize(size)

##############
# Main Class #
##############
class FancyTitleLabel(QLabel):
    def __init__(self,text):
        super().__init__()
        self.setContentsMargins(0,0,0,0)
        global font
        self.setFont(font)
        self.setText(text)
        self.setStyleSheet(f"""
            color: {TEXT_LIGHT};
            padding: 0px;
        """)

    def calcWidth(self):
        return QFontMetrics(self.font()).width(self.text())
