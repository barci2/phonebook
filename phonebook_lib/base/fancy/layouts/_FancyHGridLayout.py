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
class FancyHGridLayout(QGridLayout):
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

        rows=max(len(line) for line in items if type(line)==list)
        for column,line in enumerate(items):
            if type(line)!=list:
                if issubclass(type(line),QWidget):
                    self.addWidget(line,0,column,rows,1,alignment=alignment)
                elif issubclass(type(line),QLayout):
                    self.addLayout(line,0,column,rows,1)
                elif type(line)==int:
                    self.setColumnStretch(column,line)
            else:
                for row,item in enumerate(line):
                    if issubclass(type(item),QWidget):
                        self.addWidget(item,row,column,alignment=alignment)
                    elif issubclass(type(item),QLayout):
                        self.addLayout(item,row,column)
                    elif type(item)==int:
                        self.setRowStretch(row,item)

    def Spacing(tab_size):
        return QSpacerItem(tab_size,0)

    def Stretch(factor=1):
        return factor
