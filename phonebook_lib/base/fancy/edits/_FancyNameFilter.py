####################
# External Imports #
####################
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

####################
# Internal Imports #
####################

from .._style_constants import *
from ._FancyLineEdit import FancyLineEdit

##############
# Main Class #
##############
class FancyNameFilter(FancyLineEdit):
    def __init__(self,filter,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.textChanged.connect(lambda:filter.filterName(self.text()))
