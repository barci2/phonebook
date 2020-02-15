####################
# External Imports #
####################
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np

####################
# Internal Imports #
####################

from ._style_constants import *
from .. import constants as c

##############
# Main Class #
##############
class FancySlidableImage(QLabel):
    def __init__(self,image=None,draw_arrows=False,next_action=lambda:None,previous_action=lambda:None):
        super().__init__()

        self.arrow=0
        self.margin=100

        self.draw_arrows=draw_arrows
        self.next_action=next_action
        self.previous_action=previous_action

        self.setMouseTracking(True)
        self.setImage(image) if type(image)!=type(None) else None
        self.setFocusPolicy(Qt.NoFocus)

    def mouseEnterEvent(self,event):
        self.mouseMoveEvent(event)

    def mouseLeaveEvent(self,event):
        self.arrow=0
        self.setImage(self.image)

    def checkPos(self,pos):
        if pos.x()<=self.margin and self.arrow!=-1:
            self.arrow=-1
            self.setImage(self.image)
        elif pos.x()>=c.camera_image_dims[1]-self.margin and self.arrow!=1:
            self.arrow=1
            self.setImage(self.image)
        elif c.camera_image_dims[1]-self.margin>=pos.x()>=self.margin:
            self.arrow=0
            self.setImage(self.image)

    def mouseMoveEvent(self,event):
        self.checkPos(event.pos())

    def showEvent(self,event):
        self.checkPos(self.mapFromGlobal(QCursor().pos()))

    def mousePressEvent(self,event):
        if self.arrow==-1:
            self.previous_action()
        if self.arrow==1:
            self.next_action()

    def setImage(self,image):
        self.image=image
        height,width,colors=image.shape
        bytesPerLine=colors*width
        q=QImage(image.astype(np.uint8).data,width,height,bytesPerLine,QImage.Format_RGB888)
        pix=QPixmap.fromImage(q)

        if not self.draw_arrows:
            self.setPixmap(pix)
            return

        painter=QPainter(pix)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        margin=self.margin

        pen=QPen()
        pen.setWidth(10)
        pen.setCapStyle(Qt.FlatCap)
        pen.setJoinStyle(Qt.MiterJoin)

        left_arrow=QPainterPath()
        left_arrow.moveTo(60,c.camera_image_dims[0]//2-20)
        left_arrow.lineTo(40,c.camera_image_dims[0]//2)
        left_arrow.lineTo(60,c.camera_image_dims[0]//2+20)

        right_arrow=QPainterPath()
        right_arrow.moveTo(c.camera_image_dims[1]-60,c.camera_image_dims[0]//2-20)
        right_arrow.lineTo(c.camera_image_dims[1]-40,c.camera_image_dims[0]//2)
        right_arrow.lineTo(c.camera_image_dims[1]-60,c.camera_image_dims[0]//2+20)

        if self.arrow==-1:
            pen.setColor(QColor(255,255,255))
            painter.setPen(pen)
            painter.drawPath(left_arrow)
            painter.fillRect(0,0,margin,c.camera_image_dims[0],QColor(255,255,255,50))
        else:
            pen.setColor(QColor(255,255,255,150))
            painter.setPen(pen)
            painter.drawPath(left_arrow)

        if self.arrow==1:
            pen.setColor(QColor(255,255,255))
            painter.setPen(pen)
            painter.drawPath(right_arrow)
            painter.fillRect(c.camera_image_dims[1]-margin,0,margin,c.camera_image_dims[0],QColor(255,255,255,50))
        else:
            pen.setColor(QColor(255,255,255,150))
            painter.setPen(pen)
            painter.drawPath(right_arrow)

        painter.end()
        self.setPixmap(pix)
