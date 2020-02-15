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

##############
# Main Class #
##############
class FancyHLayout(QHBoxLayout):
    def __init__(self,items,h_align='n',v_align='n',spacing=5,zero_margins=True,parent=None):
        super().__init__() if parent==None else super().__init__(parent)

        alignment=Qt.Alignment()
        if h_align=='l':
            alignment|=Qt.AlignLeft
        if h_align=='r':
            alignment|=Qt.AlignRight
        if h_align=='c':
            alignment|=Qt.AlignHCenter
        if v_align=='t':
            alignment|=Qt.AlignTop
        if v_align=='b':
            alignment|=Qt.AlignBottom
        if v_align=='c':
            alignment|=Qt.AlignVCenter

        self.setSpacing(spacing)
        if zero_margins:
            self.setContentsMargins(0,0,0,0)

        for item in items:
            if issubclass(type(item),QWidget):
                self.addWidget(item,alignment=alignment)
            elif issubclass(type(item),QLayout):
                self.addLayout(item)
            elif issubclass(type(item),QSpacerItem):
                self.addSpacerItem(item)
            elif type(item)==int:
                self.addStretch(item)

    def Spacing(tab_size):
        return QSpacerItem(tab_size,0)

    def Stretch(factor=0):
        return factor
