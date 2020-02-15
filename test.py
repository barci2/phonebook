from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import cv2

app=QApplication([])

from phonebook_lib.base.fancy import *
x=cv2.imread('../../Pictures/business_face.jpg',-1)[:,:,[2,1,0]].copy()

w=QWidget()
w.setLayout(FancyVLayout([0,FancyHLayout([0,FancyPhotoFrame(x),0]),0]))
w.show()
app.exec_()
