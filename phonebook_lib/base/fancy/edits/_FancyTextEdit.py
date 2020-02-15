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

#############
# Init Code #
#############

font=QFont("Segoe UI")
font.setWeight(QFont.Normal)
font.setPointSize(11)

##############
# Main Class #
##############
class FancyTextEdit(QTextEdit):
    def __init__(self,editing_finished_signal,placeholder="",text=""):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        global font
        self.setFont(font)
        self.setText(text)
        self.setPlaceholderText(placeholder)
        self.placeholder=placeholder
        self.textChanged.connect(self.updateSize)
        self.editing_finished_signal=editing_finished_signal
        self.updateSize()

        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(QPointF(0,1))
        shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(shadow)
        #self.setContentsMargins(0,0,0,3)
        self.setStyleSheet(f"""
            color: {TEXT_LIGHT};
            background-color: {EDIT};
            padding: 2px;
            border-radius: {RADIUS};
        """)

        self.hide()

    def calcSize(self):
        fm=QFontMetrics(self.font())
        text=self.toPlainText()
        return max(fm.size(0,text).width()+25,fm.size(0,self.placeholder).width()+10,190),max(fm.size(0,text).height()+text.count('\n')+12,fm.size(0,self.placeholder).height()+12)
    def updateSize(self):
        w,h=self.calcSize()
        self.setFixedWidth(w)
        self.setFixedHeight(h)
    def focusOutEvent(self,event):
        super().focusOutEvent(event)
        self.editing_finished_signal(self.toPlainText())
