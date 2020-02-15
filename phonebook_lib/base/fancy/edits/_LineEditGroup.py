1####################
# External Imports #
####################
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

####################
# Internal Imports #
####################

##############
# Main Class #
##############
class LineEditGroup():
    def __init__(self,line_edit_list):
        self.l=line_edit_list
        for le in self.l:
            if issubclass(type(le),QLineEdit):
                le.setLineEditGroup(self)
        self.update()
    def update(self):
        w=0
        for le in self.l:
            if issubclass(type(le),QLineEdit):
                w=max(w,le.calcWidth())
        for le in self.l:
            le.setFixedWidth(w)
