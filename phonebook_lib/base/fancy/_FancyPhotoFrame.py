####################
# External Imports #
####################
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import cv2

####################
# Internal Imports #
####################

from ._style_constants import *

##############
# Main Class #
##############
class FancyPhotoFrame(QWidget):
    def __init__(self,image,height=100):

        ### image processing
        h,w,colors=image.shape
        self.w=int(w*height/h)
        self.h=height
        r=min(h,w)//2
        xc,yc=w//2,h//2
        x,y=np.meshgrid(np.arange(w),np.arange(h))
        d2=(x-xc)**2+(y-yc)**2
        mask=(d2<=r**2)*255
        image=np.concatenate((image,mask.reshape(h,w,1)),2)


        super().__init__()
        h,w,colors=image.shape
        bytesPerLine=colors*w
        q=QImage(image.astype(np.uint8).data,w,h,bytesPerLine,QImage.Format_RGBA8888).smoothScaled(self.w,self.h)
        self.image=QPixmap.fromImage(q)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet(f"""
            background: {BACKGROUND};
        """)

    def paintEvent(self,event):
        print("AAA")
        painter=QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.drawPixmap(5,5,self.image)
        painter.setPen(QPen(QColor(255,255,255),3))
        painter.setBrush(QColor(0,0,0,0))
        r=min(self.w,self.h)//2
        painter.drawEllipse(2+self.w//2-r,2+self.h//2-r,r*2+6,r*2+6)
        painter.end()

    def sizeHint(self):
        return QSize(self.w+10,self.h+10)
