from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import time
import numpy as np

from ..base import constants as c
from ..base.fancy import *

class TimerImageWidget(QLabel):
    def __init__(self,image):
        self.start=None

        super().__init__()

        self.setImage(image)
        self.setFocusPolicy(Qt.NoFocus)
        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(QPointF(0,5))
        shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(shadow)

    def startTimer(self):
        self.start=time.time()
    def setImage(self,image):
        height,width,colors=image.shape
        bytesPerLine=3*width
        q=QImage(image.astype(np.uint8).data,width,height,bytesPerLine,QImage.Format_RGB888)
        if self.start==None:
            self.setPixmap(QPixmap.fromImage(q))
            return

        pix=QPixmap.fromImage(q)
        number=10-int(time.time()-self.start)
        if number<=0:
            self.setPixmap(pix)
            return

        painter=QPainter(pix)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        font=QFont("Times",60,QFont.Bold)
        painter.setFont(font)

        cx=q.rect().width()//2
        cy=q.rect().height()//2
        s=time.time()-self.start-int(time.time()-self.start)
        o=(time.time()-self.start)*1.3
        a=max(min(2-s*6,1),0)*255

        gradient=QConicalGradient(cx,cy,90-5+360*o)
        gradient.setColorAt(0,QColor(0,0,0,0))
        gradient.setColorAt(0.5,QColor(0,0,0))

        pen=QPen(QBrush(gradient),10)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        mw=QFontMetrics(font).width(str(number))//2
        mh=QFontMetrics(font).height()//2

        a=(max(min(2-s*4,1),0))*255
        painter.translate(-cx*s*3,-cy*s*3)
        painter.scale(1+s*3,1+s*3)

        painter.setPen(QColor(0,0,0,a))
        painter.drawText(QRect(cx-mw,cy-mh+15,mw*2,mh*2),QPainter.HighQualityAntialiasing,str(number))


        painter.end()
        self.setPixmap(pix)

    def stopTimer(self):
        self.start=None

class TimerDialog(QDialog):
    def __init__(self,camera):
        super().__init__()
        self.camera=camera
        self.ok_button=FancyTextButton(self.accept,"Ok")
        self.retry_button=FancyTextButton(self.shoot,"Retry")
        self.cancel_button=FancyTextButton(self.reject,"Cancel")
        self.image=TimerImageWidget(np.ones(c.camera_image_dims))
        layout=FancyVGridLayout([
            self.image,
            [self.ok_button,self.retry_button,self.cancel_button]
        ],zero_margins=False)
        self.setLayout(layout)
        self.setUpdatesEnabled(True)
        self.setModal(True)
        self.f=True

        self.setStyleSheet(f"""
            background: {BACKGROUND} solid;
        """)

    def shoot(self):
        self.ok_button.hide()
        self.retry_button.hide()
        self.cancel_button.hide()
        self.repaint()
        self.camera.takeTimerPhoto(self.image,self.repaint)
        self.ok_button.show()
        self.retry_button.show()
        self.cancel_button.show()
        self.repaint()

    def paintEvent(self,event):
        super().paintEvent(event)
        if self.f:
            self.f=False
            self.shoot()

class Camera():
    def __init__(self):
        self.image=None
    def takeSneakyPhoto(self):
        cam=cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        ret,frame=cam.read()
        cv2.waitKey(2000)
        ret,frame=cam.read()
        if not ret:
            raise AssertionError("Image feed not avaliable")
        cam.release()
        frame=frame[:,::-1,[2,1,0]].astype(np.uint8,order='C',casting='unsafe')
        return frame

    def takeTimerPhoto(self,image,update_dialog):
        cam=cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        _,frame=cam.read()
        image.setImage(frame)
        t=time.time()
        image.startTimer()
        while time.time()-t<10:
            _,frame=cam.read()
            frame=frame[:,::-1,[2,1,0]].astype(np.uint8,order='C',casting='unsafe')
            image.setImage(frame)
            update_dialog()
            cv2.waitKey(1)
        self.image=frame
        image.stopTimer()
        image.setImage(frame)
        cam.release()

    def takeProperPhoto(self):
        d=TimerDialog(self)
        return self.image if d.exec_()==TimerDialog.Accepted else None
