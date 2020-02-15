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
from .layouts import FancyDummyLayout

##############
# Main Class #
##############

class FancyFrame(QHBoxLayout):
    def __init__(self,contents=None,parent=None):
        super().__init__()

        self.frame=QFrame()
        self.frame.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)

        if issubclass(type(contents),QWidget):
            layout=FancyDummyLayout()
            layout.addWidget(contents)
            self.frame.setLayout(layout)
        if issubclass(type(contents),QLayout):
            self.frame.setLayout(contents)

        self.setRaised(False)

        self.addWidget(self.frame)
        parent.setLayout(self) if parent!=None else None

    def isRaised(self):
        return self.raised

    def setRaised(self,raised):
        if raised:
            self.raised=True
            elevation=3
            radius=12
            self.setContentsMargins(0,6,6,15)

            shadow=QGraphicsDropShadowEffect()
            shadow.setBlurRadius(radius)
            shadow.setOffset(QPointF(0,elevation))
            shadow.setColor(QColor(0,0,0))
            self.frame.setGraphicsEffect(shadow)
            self.frame.setStyleSheet(f"""
                padding-left: 15px;
                padding-right: 30px;
                padding-top: 10px;
                padding-bottom: 10px;
                border-radius: {RADIUS};
                background-color: {FRAME_UP};
            """)

        else:
            self.raised=False
            elevation=1
            radius=8
            self.setContentsMargins(0,6,6,15)

            shadow=QGraphicsDropShadowEffect()
            shadow.setBlurRadius(radius)
            shadow.setOffset(QPointF(0,elevation))
            shadow.setColor(QColor(0,0,0))
            self.frame.setGraphicsEffect(shadow)
            self.frame.setStyleSheet(f"""
                padding-left: 15px;
                padding-right: 30px;
                padding-top: 10px;
                padding-bottom: 10px;
                border-radius: {RADIUS};
                background-color: {FRAME_DOWN};
            """)
