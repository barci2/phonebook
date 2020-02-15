####################
# External Imports #
####################
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from bisect import bisect
from sortedcontainers import SortedSet

####################
# Internal Imports #
####################

##############
# Main Class #
##############
class FancySortedLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.dict=dict()
        self.set=SortedSet()
        self.addStretch()
        self.setSpacing(3)
        self.setContentsMargins(0,0,0,0)

    def addWidget(self,widget):
        key=widget.comparableKey()
        self.dict[widget]=key
        self.set.add(key)

        super().insertWidget(bisect(list(self.set),key)-1,widget)

    def removeWidget(self,widget):
        key=self.dict[widget]

        self.set.remove(key)
        self.dict.pop(widget)

        super().removeWidget(widget)

    def updateWidget(self,widget):
        self.removeWidget(widget)
        self.addWidget(widget)

    def listItems(self):
        return self.dict.keys()
    def listValues(self):
        return self.dict.values()
    def count(self):
        return super().count()-1
