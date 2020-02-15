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

##############
# Main Class #
##############
class FancyIconLabel(QWidget):
    def __init__(self,icon_file):
        super().__init__()
        self.size=22
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setContentsMargins(0,0,0,0)
        self.setIcon(QIcon(str(icon_file)))

    def paintEvent(self,e):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.drawPixmap(0,0,self.size,self.size,self.icon.pixmap(self.size,self.size))

    def setIcon(self,icon):
        self.icon=icon
        self.update()

    def sizeHint(self):
        return QSize(self.size,self.size)
