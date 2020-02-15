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

class FancySlider(QSlider):
    def __init__(self,min_val,max_val,value,value_changed):
        super().__init__(Qt.Horizontal)
        self.setMinimum(min_val)
        self.setMaximum(max_val)
        self.setValue(value)
        self.valueChanged.connect(value_changed)
        self.setStyleSheet(f"""
            outline-color: white;
        """)
