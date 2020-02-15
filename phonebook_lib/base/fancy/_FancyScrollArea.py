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

class FancyScrollArea(QScrollArea):
    def __init__(self,contents):
        super().__init__()
        if issubclass(type(contents),QLayout):
            w=QWidget()
            w.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
            w.setLayout(contents)
            self.setWidget(w)
        elif issubclass(type(contents),QWidget):
            self.setWidget(contents)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            border: 0px transparent;
            outline: 0px transparent;
        """)
