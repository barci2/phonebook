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
class FancyDialog(QDialog):
    def __init__(self,title,icon_file,layout=None,parent=None):
        super().__init__() if parent==None else super().__init__(parent)
        if layout!=None:
            self.setLayout(layout)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(str(icon_file)))

        self.setStyleSheet(f"background: {BACKGROUND}")
