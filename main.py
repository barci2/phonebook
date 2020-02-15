import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from phonebook_lib.base import constants as c
from phonebook_lib.advanced.application import MainWindow

app=QApplication(sys.argv)
window=MainWindow()

app.installEventFilter(window)

window.setWindowIcon(QIcon(str(c.application_icon_file)))
window.setWindowTitle("Phonebook")
window.show()
app.exec_()
