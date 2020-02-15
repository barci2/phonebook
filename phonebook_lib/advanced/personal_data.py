from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path
import random
import webbrowser
import unidecode

from ..base import constants as c
from ..base.fancy import *
from .database import Database
from ..base.comparable import Comparable
from .tags import Tag,TagOption
from ..base.fancy import *
class PersonalData(QWidget,Comparable):
    def __init__(self,name,db,tags,filter,selector,rating=None):
        # Initializing Inherited Classes
        super(QWidget,self).__init__()
        super(Comparable,self).__init__()

        # Big Classes
        self.db=db
        self.tags=tags
        self.filter=filter
        self.selector=selector

        # Downloading Data
        self.name=name
        self.phone_number=db.getPhoneNumber(name)
        self.email=db.getEmail(name)
        self.linkedin=db.getLinkedIn(name)
        self.researchgate=db.getResearchGate(name)
        self.messenger=db.getMessenger(name)
        self.acquaintance=db.getAcquaintance(name)
        if rating==None:
            self.rating=self.db.getRating(name)
        else:
            self.rating=rating
            db.setRating(name,rating)

        # Loading self into Big Classes
        self.tags.addPerson(self)
        self.selector.addPerson(self)

        # Initializing Layout
        text_edit=FancyTextEdit(lambda text:db.setAdditionalInfo(self.name,text),"Additional Info",db.getAdditionalInfo(self.name))

        self.name_label=FancyNameLabel(self.name)
        self.phone_number_label=FancyLabel(self.phone_number if self.phone_number!=None else "")
        self.email_label=FancyLabel(self.email if self.email!=None else "")
        self.rating_label=FancyRatingLabel(self.rating)
        self.acquaintance_label=FancyAcquaintanceLabel(self.acquaintance)

        self.linkedin_button=FancyIconButton(self.showLinkedIn, c.linkedin_icon_file)
        self.researchgate_button=FancyIconButton(self.showResearchGate,c.researchgate_icon_file)
        self.messenger_button=FancyIconButton(self.showMessenger,c.messenger_icon_file)

        self.text_edit=FancyTextEdit(lambda s:self.db.setAdditionalInfo(self.name,s),"Additional Info",self.db.getAdditionalInfo(self.name))

        self.grid_layout=QGridLayout()
        self.grid_layout.addWidget(FancyLine(),0,0,5,1)
        self.grid_layout.setColumnMinimumWidth(1,5)
        self.grid_layout.setRowMinimumHeight(1,5)
        self.grid_layout.addWidget(self.name_label,0,2,3,1)
        self.grid_layout.addWidget(self.phone_number_label,0,3)
        self.grid_layout.addWidget(self.email_label,0,4)
        self.grid_layout.addWidget(self.rating_label,0,5)
        self.grid_layout.addWidget(self.acquaintance_label,0,6)
        self.grid_layout.addLayout(FancyHLayout([
            self.linkedin_button,
            self.researchgate_button,
            self.messenger_button,
            FancyIconButton(self.edit,c.edit_item_icon_file),
            FancyIconButton(lambda: self.filter.deletePerson(self),c.delete_item_icon_file),
            self.tags.proxy(self),
            FancyHLayout.Stretch()
        ],spacing=0,h_align='l',v_align='c'),2,3,1,4)
        self.grid_layout.setRowMinimumHeight(3,0)
        self.grid_layout.addWidget(self.text_edit,4,2,1,5)
        self.grid_layout.setColumnStretch(7,1)
        self.grid_layout.setContentsMargins(0,0,0,0)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setHorizontalSpacing(5)

        self.frame=FancyFrame(self.grid_layout,parent=self)
        self.buildLayout()
        text_edit.setStyleSheet(f"color: {TEXT_LIGHT}")

    def edit(self):
        tags=FancySortedLayout()
        for tag in self.tags.listTags(self):
            tags.addWidget(TagOption(tag))

        name_le=FancyLineEdit("Name",self.name)
        phone_number_le=FancyLineEdit("Phone Number",self.phone_number)
        email_le=FancyLineEdit("Email",self.email)
        linkedin_le=FancyLineEdit("LinkedIn Address",self.linkedin)
        researchgate_le=FancyLineEdit("Research Gate Address",self.researchgate)
        messenger_le=FancyLineEdit("Messenger Address",self.messenger)
        tag_le=FancyLineEdit("Tag",completer=self.tags.getCompleter())

        rating_label=FancyRatingLabel(self.rating)
        rating_s=FancySlider(1,5,self.rating,rating_label.setRating)

        line_edit_group=LineEditGroup([name_le,phone_number_le,email_le,linkedin_le,researchgate_le,messenger_le,tag_le,rating_s])

        acquaintance_buttons_list=[FancyTextSwitch(lambda:None,level) for level in c.acquaintance_levels]
        acquaintance_buttons_group=FancyButtonGroup(acquaintance_buttons_list)
        acquaintance_buttons_list[self.acquaintance-1].setChecked(True)


        def addNewTag(tags,tag_le):
            if tag_le.text()=="" or tag_le.text() in tags.listValues():
                tag_le.setText("")
                return
            tags.addWidget(TagOption(tag_le.text()))
            tag_le.setText("")
        tag_le.editingFinished.connect(lambda:addNewTag(tags,tag_le))

        dialog=FancyDialog("Edit",c.edit_item_icon_file)
        layout=FancyVGridLayout([
            [FancyLabel("Name"),name_le],
            [FancyLabel("Phone Number"),phone_number_le],
            [FancyLabel("Email"),email_le],
            [FancyLabel("LinkedIn Address"),linkedin_le],
            [FancyLabel("Research Gate Address"),researchgate_le],
            [FancyLabel("Messenger Address"),messenger_le],
            [rating_label,rating_s],
            FancyHLayout(acquaintance_buttons_list),
            [FancyLabel("New Tag"),tag_le],
            tags,
            [FancyTextButton(dialog.accept,"Ok"),FancyTextButton(dialog.reject,"Cancel")]
        ],zero_margins=False)
        dialog.setLayout(layout)

        result=dialog.exec()
        if result==FancyDialog.Accepted:
            self.name=self.db.rename(self.name,name_le.text())
            self.filter.updateName(self)
            self.phone_number=self.db.setPhoneNumber(self.name,phone_number_le.text())
            self.email=self.db.setEmail(self.name,email_le.text())
            self.linkedin=self.db.setLinkedIn(self.name,linkedin_le.text())
            self.researchgate=self.db.setResearchGate(self.name,researchgate_le.text())
            self.messenger=self.db.setMessenger(self.name,messenger_le.text())
            self.rating=self.db.setRating(self.name,rating_s.value())
            self.acquaintance=self.db.setAcquaintance(self.name,-acquaintance_buttons_group.checkedId()-1)
            self.buildLayout()

            self.tags.updateTags({tag.text() for tag in tags.listItems() if not tag.isChecked()},self)

    def buildLayout(self):
        self.name_label.setText(self.name)
        self.phone_number_label.setText(self.phone_number if self.phone_number!=None else "")
        self.email_label.setText(self.email if self.email!=None else "")
        self.linkedin_button.hide() if self.linkedin==None else self.linkedin_button.show()
        self.researchgate_button.hide() if self.researchgate==None else self.researchgate_button.show()
        self.messenger_button.hide() if self.messenger==None else self.messenger_button.show()
        self.rating_label.setRating(self.rating)
        self.acquaintance_label.setAcquaintance(self.acquaintance)

    def showLinkedIn(self):
        webbrowser.open(self.linkedin,new=2)

    def showResearchGate(self):
        webbrowser.open(self.researchgate,new=2)

    def showMessenger(self):
        webbrowser.open(self.messenger,new=2)

    def getName(self):
        return self.name

    def getSortableName(self):
        return unidecode.unidecode(self.name)

    def getRating(self):
        return self.rating

    def updateRating(self,rating):
        self.rating=rating
        self.filter.updateRating(self)

    def hideTextEdit(self):
        self.grid_layout.setRowMinimumHeight(3,0)
        self.text_edit.hide()
        self.grid_layout.update()

    def showTextEdit(self):
        self.grid_layout.setRowMinimumHeight(3,5)
        self.text_edit.show()
        self.grid_layout.update()

    def getWidths(self):
        return (self.name_label.calcWidth(),self.phone_number_label.calcWidth(),self.email_label.calcWidth(),self.rating_label.layout().contentsRect().width(),self.acquaintance_label.layout().contentsRect().width())

    def updateWidths(self,widths):
        self.grid_layout.setColumnMinimumWidth(2,widths[0])
        self.grid_layout.setColumnMinimumWidth(3,widths[1])
        self.grid_layout.setColumnMinimumWidth(4,widths[2])
        self.grid_layout.setColumnMinimumWidth(5,widths[3])
        self.grid_layout.setColumnMinimumWidth(6,widths[4])

    def mousePressEvent(self,event):
        if event.button()!=Qt.LeftButton:
            return
        if int(event.modifiers())==Qt.CTRL:
            self.selector.setPerson(self,not self.frame.isRaised())
        elif int(event.modifiers())==0:
            self.selector.setOnlyActive(self)

    def mouseDoubleClickEvent(self,event):
        if event.button()!=Qt.LeftButton:
            return
        self.filter.hideTextEdits()
        self.showTextEdit()

    def setActive(self,active):
        self.frame.setRaised(active)
        if not active:
            self.hideTextEdit()
