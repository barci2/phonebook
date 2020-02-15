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

class FancyTopFrame(QFrame):
    def __init__(self,contents=None,parent=None):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

        if issubclass(type(contents),QWidget):
            layout=FancyDummyLayout()
            layout.addWidget(contents)
            self.setLayout(layout)
        if issubclass(type(contents),QLayout):
            self.setLayout(contents)

        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(QPointF(0,1))
        shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(shadow)
        self.setStyleSheet(f"""
            outline: 0px;
            padding: 0px;
            border 0px;
            background-color: {FRAME_DOWN};
        """)
        self.setContentsMargins(0,0,0,6)
