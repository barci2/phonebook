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
from ._FancyDialog import FancyDialog
from ..buttons import FancyTextButton
from ..labels import FancyLabel
from ..layouts import *

##############
# Main Class #
##############
class FancyMessageBox(FancyDialog):

    Ok="Ok"
    Cancel="Cancel"

    def __init__(self,buttons,icon_file,title,text,parent=None):
        super().__init__(title,icon_file) if parent==None else super().__init__(title,icon_file,parent=parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.setWindowIcon(QIcon(str(icon_file)))
        self.setWindowTitle(title)

        buttons_objects=[]
        for button in buttons:
            if button=="Ok":
                b=FancyTextButton(self.accept,"Ok")
                #b.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
                buttons_objects.append(b)
            elif button=="Cancel":
                b=FancyTextButton(self.reject,"Cancel")
                #b.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
                buttons_objects.append(b)
        FancyVLayout([
            FancyLabel(text),
            FancyHLayout(buttons_objects)
        ],parent=self,zero_margins=False)

        self.setStyleSheet(f"background: {BACKGROUND}")
