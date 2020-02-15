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

font=QFont("Segoe UI")
font.setWeight(QFont.Normal)
font.setPointSize(11)

##############
# Main Class #
##############

class FancyLineEdit(QLineEdit):
    def __init__(self,placeholder="",text="",completer=None):
        super().__init__()
        global font
        self.setFont(font)
        self.setText(text)
        self.setPlaceholderText(placeholder)
        self.group=None
        self.textChanged.connect(self.updateGroup)
        self.placeholder=placeholder
        if completer!=None:
            self.setCompleter(completer)

        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(QPointF(0,1))
        shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(shadow)
        self.setContentsMargins(0,0,0,3)

        self.setStyleSheet(f"""
            color: {TEXT_LIGHT};
            background-color: {EDIT};
            border: black solid 1px;
            outline: 0px transparent;
            padding: 2px;
            border-radius: {RADIUS};
        """)

    def calcWidth(self):
        fm=QFontMetrics(self.font())
        return max(fm.width(self.text()),fm.width(self.placeholder))+7
    def setLineEditGroup(self,group):
        self.group=group
    def updateGroup(self):
        if self.group!=None:
            self.group.update()
