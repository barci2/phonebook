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
from ... import constants as c
from ._FancyIconLabel import FancyIconLabel
from ._FancyLabel import FancyLabel
from ..layouts import *

##############
# Main Class #
##############
class FancyRatingLabel(QWidget):
    ratingChanged=pyqtSignal(int)
    def __init__(self,rating,modifiable=False):
        super().__init__()
        self.setContentsMargins(0,0,0,0)
        self.icon=FancyIconLabel(c.rating_icon_file)
        self.rating=rating
        self.modifiable=modifiable
        self.label=FancyLabel(str(rating)+'/'+str(c.max_rating))
        self.setLayout(FancyHLayout([self.label,self.icon,0],h_align='l'))

        def mousePressEvent(event,self=self):
            if event.button()!=Qt.LeftButton:
                return
            self.rating=self.rating%c.max_rating+1
            self.setRating(self.rating)
            self.ratingChanged.emit(self.rating)

        if modifiable:
            self.mousePressEvent=mousePressEvent

    def setRating(self,rating):
        self.rating=rating
        self.label.setText(str(rating)+'/'+str(c.max_rating))
