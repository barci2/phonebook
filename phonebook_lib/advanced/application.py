from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path
from hashlib import sha512
from datetime import datetime
import threading
import numpy as np

from ..base import constants as c
from ..base.fancy import *
from .database import Database
from .personal_data import PersonalData
from .tags import Tag,TagsManager
from .filter import PersonalDataFilter
from ..base.fancy import *
from .selector import Selector
from .photo_crypt import PhotoCrypt
from .im_viewer import ImageViewer
from .face_detector import FaceDetector
from .camera import Camera
from .messenger_api import Messenger

###############
# Main Window #
###############

class MainWindow(QWidget):
    def __init__(self):
        ### Initializing parent classes
        super().__init__()

        ### Setting up window
        self.setWindowIcon(QIcon(str(c.application_icon_file)))
        self.setWindowTitle("Phonebook")
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.setStyleSheet(f"background: {BACKGROUND}")

        ### Inintializing Database
        self.db=Database(c.db_file,self.warning)

        ### Initializing Encryptions and Authentication
        self.camera=Camera()
        self.face_detector=FaceDetector(self.db,self.warning)
        self.photo_crypt=PhotoCrypt(self.db,c.sneaky_photos_directory,"HASH_INIT")
        self.decryptDatabase()

        ### Setting up management classes
        selected_label=FancySelectedLabel()
        self.selector=Selector(selected_label)
        self.tags=TagsManager(self.db)
        self.filter=PersonalDataFilter(self.db,self.tags,self.selector)
        self.selector.setFilter(self.filter)
        self.tags.setFilter(self.filter)
        self.messenger=Messenger(self.db,self.selector,self.warning)

        ### Setting up layout
        rating=FancyRatingLabel(c.default_rating,modifiable=True)
        rating.ratingChanged.connect(self.filter.filterRating)

        self.setLayout(FancyVLayout([]))
        top_frame=FancyTopFrame(FancyVLayout([
            FancyTitleLabel("Phonebook"),
            FancyHLayout([
                FancyIconButton(self.createNewName,c.new_item_icon_file),
                FancyIconButton(self.messenger.sendMessageGui,c.messenger_icon_file),
                FancyIconButton(self.changePassword,c.key_icon_file),
                FancyIconButton(self.updatePhoto,c.camera_icon_file),
                0
            ]),
            FancyVLayout.Spacing(5),
            FancyHLayout([
                FancyNameFilter(self.filter,"Name"),
                rating,
                selected_label,
                1
            ],h_align='l'),
            self.tags.getTagsOrganizer()
        ],spacing=2,zero_margins=False))
        self.layout().addWidget(top_frame)

        scroll_area=FancyScrollArea(self.filter)
        self.layout().addWidget(scroll_area)

    def updatePhoto(self):
        image=self.camera.takeProperPhoto()
        if type(image)!=type(None):
            self.face_detector.setFace(image)

    def warning(self,text):
        FancyMessageBox([FancyMessageBox.Ok],c.alert_icon_file,"Warning",text,self).exec()

    def decryptDatabase(self):
        ### Taking photo
        image=self.camera.takeSneakyPhoto()

        ### Setting up password dialog
        p_le=FancySecureLineEdit("Password")

        dialog=FancyDialog("Phonebook Password",c.key_icon_file)
        layout=FancyVGridLayout([
            FancyLabel("Enter Phonebook Password"),
            p_le,
            [FancyTextButton(dialog.accept,"Ok"),FancyTextButton(dialog.reject,"Cancel")]
        ],zero_margins=False)
        dialog.setLayout(layout)

        result=dialog.exec()
        if result!=FancyDialog.Accepted:
            self.photo_crypt.saveImage(image,str(self.photo_crypt.now()))
            exit()

        ### Checking password credibility
        self.pass_enc=sha512(p_le.text().encode("8859")*2).hexdigest()

        if p_le.text()=='':
            self.photo_crypt.saveImage(image,str(self.photo_crypt.now()))
            self.warning("Password cannot be empty")
            exit()

        if not self.db.decrypt(p_le.text()):
            exit()
        if not self.db.checkDecrypted():
            self.photo_crypt.saveImage(image,str(self.photo_crypt.now()))
            self.warning("Wrong Password")
            exit()

        ### Setting up PhotoCrypt
        self.photo_crypt.loadRsaKey()
        self.photo_crypt.loadImages()
        images_list=self.photo_crypt.listImages()
        self.photo_crypt.deleteAllImages()
        self.photo_crypt.saveImage(image,str(self.photo_crypt.now()))

        security_warnings_list=self.photo_crypt.dumpWarnings()

        if len(security_warnings_list):
            self.warning("The following security issues have been noticed:\n"+''.join([' '*4+warning+'\n' for warning in security_warnings_list]))

        ### Displaying Captured Images and filtering them
        self.face_detector.loadEmbedding()
        images_list=[(image,self.photo_crypt.bytesToDate(int(t)).strftime("%Y-%m-%d %H:%M:%S")) for (image,t) in images_list if not self.face_detector.checkFace(image)]
        if len(images_list):
            viewer=ImageViewer(images_list)
            viewer.exec_()


    def changePassword(self):
        po_le=FancySecureLineEdit("Old Password")
        p1_le=FancySecureLineEdit("New Password")
        p2_le=FancySecureLineEdit("Retype Password")

        dialog=FancyDialog("Phonebook Password",c.key_icon_file)
        layout=FancyVGridLayout([
            FancyLabel("Enter Phonebook Password"),
            po_le,
            p1_le,
            p2_le,
            [FancyTextButton(dialog.accept,"Ok",no_focus_policy=False),FancyTextButton(dialog.reject,"Cancel",no_focus_policy=False)]
        ],zero_margins=False)
        dialog.setLayout(layout)

        result=dialog.exec()
        if result!=FancyDialog.Accepted:
            return

        if self.pass_enc!=sha512(po_le.text().encode("8859")*2).hexdigest():
            self.warning("Wrong old password")
            return

        if p1_le.text()!=p2_le.text():
            self.warning("New passwords don't match")
            return

        if not self.db.encrypt(p1_le.text()):
            return
        self.pass_enc=sha512(p1_le.text().encode("8859")*2).hexdigest()

    def createNewName(self):
        dialog=FancyDialog("New Contact",c.new_item_icon_file)
        line_edit=FancyLineEdit("New Name")
        dialog.setLayout(FancyVGridLayout([
            line_edit,
            [FancyTextButton(dialog.accept,"Ok",no_focus_policy=False),FancyTextButton(dialog.reject,"Cancel",no_focus_policy=False)]
        ],zero_margins=False))

        result=dialog.exec()
        if result==QDialog.Accepted:
            self.filter.addPerson(line_edit.text(),new=True)

    def eventFilter(self,object,event):
        if type(event)!=QKeyEvent:
            return False

        if event.key() in [ord('A'),ord('a')] and int(event.modifiers())==Qt.CTRL:
            self.selector.setAll(not self.selector.isAllChecked())
            return True
        return False
