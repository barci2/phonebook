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
class FancyTextSwitch(QPushButton):
    def __init__(self,checked_signal,text,no_focus_policy=False):
        super().__init__()
        self.clicked.connect(checked_signal)
        self.setFocusPolicy(Qt.NoFocus) if no_focus_policy else None
        self.setText(text)

        font=QFont("Segoe UI")
        font.setPointSize(11)
        font.setWeight(50)
        self.setFont(font)
        self.setCheckable(True)

        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(QPointF(0,1))
        shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(shadow)
        self.setContentsMargins(0,0,0,3)

        self.setStyleSheet(f"""
            QPushButton {{
                outline: 0px transparent;
                border: 0px transparent;
                padding-left: 25px;
                padding-right: 25px;
                padding-top: 5px;
                padding-bottom: 5px;
            }}
            QPushButton::closed {{
                color: {BUTTON_TEXT_CLOSED};
                background: solid {BUTTON_CLOSED};
            }}
            QPushButton::hover {{
                color: {BUTTON_TEXT_HOVER};
                background: solid {BUTTON_HOVER};
            }}
            QPushButton::open {{
                color: {BUTTON_TEXT_OPEN};
                background: solid {BUTTON_OPEN};
            }}
        """)
