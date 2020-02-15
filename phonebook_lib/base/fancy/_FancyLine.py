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

from ._style_constants import *

##############
# Main Class #
##############

class FancyLine(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
        self.lmin=50
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        pen=QPen()
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setColor(QColor(255,255,255))
        painter.setPen(pen)

        painter.drawLine(1,1,1,max(self.lmin,self.size().height())+1)
    def sizeHint(self):
        return QSize(2,self.lmin+2)
