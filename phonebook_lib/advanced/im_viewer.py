from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path

from ..base import constants as c
from ..base.fancy import *

##########
# NoPage #
##########

class NoPage(QWidget):
    def __init__(self,image,date):
        super().__init__()
        FancyVGridLayout([
            [
            FancyLabel("Login from "+date),
            FancyVGridLayout.Stretch(),
            ],
            FancySlidableImage(image),
        ],zero_margins=True,parent=self)

        self.setStyleSheet(f"""
            background: {BACKGROUND} solid;
        """)

##############
# ViewerPage #
##############

class ViewerPage(QWidget):
    def __init__(self,image,date,next_action,previous_action):
        super().__init__()
        FancyVGridLayout([
            [
            FancyLabel("Login from "+date),
            FancyVGridLayout.Stretch(),
            ],
            FancySlidableImage(image,True,next_action,previous_action),
        ],zero_margins=True,parent=self)

        self.setStyleSheet(f"""
            background: {BACKGROUND} solid;
        """)

###############
# ImageViewer #
###############

class ImageViewer(QDialog):
    def __init__(self,images_list):
        super().__init__()

        self.setWindowIcon(QIcon(str(c.camera_icon_file)))

        self.setLayout(QStackedLayout())
        if len(images_list)>1:
            for (image,date) in images_list:
                self.layout().addWidget(ViewerPage(image,date,self.next,self.previous))
        else:
            self.layout().addWidget(NoPage(images_list[0][0],images_list[0][1]))

        self.setStyleSheet(f"""
            background: {BACKGROUND} solid;
        """)
        self.setContentsMargins(5,5,5,5)

    def next(self):
        self.layout().setCurrentIndex((self.layout().currentIndex()+1)%self.layout().count())

    def previous(self):
        self.layout().setCurrentIndex((self.layout().currentIndex()+self.layout().count()-1)%self.layout().count())

    def keyPressEvent(self,event):
        if event.key()==Qt.Key_Left:
            self.previous()
        elif event.key()==Qt.Key_Right:
            self.next()
        elif event.key()==Qt.Key_Escape or event.key()==Qt.Key_Return:
            self.done(0)
