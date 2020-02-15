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
class FancyIconButton(QPushButton):
    def __init__(self,checked_signal,icon_file,no_focus_policy=False):
        super().__init__()
        self.clicked.connect(checked_signal)
        self.setFocusPolicy(Qt.NoFocus) if no_focus_policy else None
        icon=QIcon(str(icon_file))
        self.setIcon(icon)

        self.setStyleSheet("""
            QPushButton {
                outline: 0px transparent;
                border: 0px transparent;
                padding-left: 0px;
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                background-color: rgba(0,0,0,0);
            }
        """)
        self._off_style()
        self.pressed.connect(self._on_style)
        self.released.connect(self._off_style)

    def _on_style(self):
        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(QPointF(0,1))
        shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(shadow)

    def _off_style(self):
        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(21)
        shadow.setOffset(QPointF(0,5))
        shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(shadow)
