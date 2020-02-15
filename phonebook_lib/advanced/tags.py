from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path

from ..base import constants as c
from ..base.comparable import Comparable
from ..base.fancy import *
from .tags_organizer import TagsOrganizer

####################################
# _ClickableTag - slave tag button #
####################################

class _ClickableTag(QPushButton,Comparable):
    def __init__(self,master,on_signal,off_signal,text):
        ### Initializing parent classes
        super(QPushButton,self).__init__()
        super(Comparable,self).__init__()

        ### Initializing variables
        self.on_signal=on_signal   # Sent when button switched on
        self.off_signal=off_signal # Sent when button switched off
        self.master=master         # Master Tag class

        ### Setting up button
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setFlat(True)
        self.setText(text)
        self.setCheckable(True)
        self.toggled.connect(self._ifClicked)
        self.setStyleSheet(f"""
            QPushButton {{
                outline: 0px transparent;
                border: 0px transparent;
                padding-left: 5px;
                padding-right: 5px;
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
        self.setFocusPolicy(Qt.NoFocus)

    #############################
    # Sending signals if toggle #
    #############################

    def _ifClicked(self,state):
        if state:
            self.on_signal()
            self.master._setAll(True)
        else:
            self.off_signal()
            self.master._setAll(False)

    ############################
    # Key for Comparable class #
    ############################

    def comparableKey(self):
        return self.text()

    def deleteLater(self):
        self.master._remove(self)
        del self.master
        super().deleteLater()

###################################
# Tag - master for Clickable Tags #
###################################

class Tag(Comparable):
    def __init__(self,on_signal,off_signal,text):
        ### Initializing parent class
        super().__init__()

        ### Initializing variables
        self.slaves=set()          # Set of slave Clickable Tags
        self.on_signal=on_signal   # Sent when button switched on
        self.off_signal=off_signal # Sent when button switched off
        self.text=text             # Tag name

    #########################################
    # Interface Functions for _ClickableTag #
    #########################################

    def _setAll(self,value):
        for slave in self.slaves:
            slave.setChecked(value)

    def _remove(self,tag):
        self.slaves.remove(tag)

    #############################
    # Slave button provisioning #
    #############################

    def clone(self):
        tag=_ClickableTag(self,self.on_signal,self.off_signal,self.text)
        self.slaves.add(tag)
        return tag

    ############################
    # Key for Comparable class #
    ############################

    def comparableKey(self):
        return self.text

    ##################################
    # Last tag - left in main layout #
    ##################################

    def lastTag(self):
        return list(self.slaves)[0]

###################################################################
# TagOption - option for removing tags while editing PersonalData #
###################################################################

class TagOption(QPushButton,Comparable):
    def __init__(self,text):
        ### Initializing parent classes
        super(QPushButton,self).__init__()
        super(Comparable,self).__init__()

        ### Setting up button
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setFlat(True)
        self.setText(text)
        self.setCheckable(True)
        self.setStyleSheet(f"""
            QPushButton {{
                outline: 0px transparent;
                border: 0px transparent;
                padding-left: 5px;
                padding-right: 5px;
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
                background: solid hsv(0{BUTTON_OPEN[5:]};
            }}
        """)
        self.setFocusPolicy(Qt.NoFocus)

    ############################
    # Key for Comparable class #
    ############################

    def comparableKey(self):
        return self.text()

##########################################################################
# TagsManager - manager for all tags and their interfacing with database #
##########################################################################

class TagsManager():
    def __init__(self,db,filter=None):
        ### Major connections
        self.db=db
        self.filter=filter
        self.tags_organizer=TagsOrganizer(db)

        ### Initializing internal variables
        self.tags=dict()            # Dictionary from tags names to Tags classes
        self.persons_tags=dict()    # Dictionary from persons and tags names to Clickable Tags
        self.tags_persons=dict()    # Dictionary from tags names to sets of persons having those
        self.proxys=dict()          # Dictionary of proxy layouts for persons
        self.completer=QCompleter() # Tags completer for editing person

    #########################
    # Convenience Functions #
    #########################

    def _checkFilter(self):
        if filter==None:
            raise AssertionError("Filter Class not set")

    #######################################
    # Interface functions for main window #
    ########################################

    def setFilter(self,filter):
        self.filter=filter

    def getTagsOrganizer(self):
        return self.tags_organizer

    ####################
    # Managing persons #
    ####################

    def addPerson(self,person):
        self._checkFilter()

        self.persons_tags[person]=dict()
        self.proxys[person]=FancySortedLayout()
        for tag in self.db.listTags(person.getName()):
            self.addTag(tag,person)

    def removePerson(self,person):
        self._checkFilter()

        for tag in [tag.text() for tag in self.proxys[person].listItems()]:
            self.removeTag(tag,person,False)
        self.proxys.pop(person)
        self.persons_tags.pop(person)

    #################################
    # Managing tags list for person #
    #################################

    def loadTags(self,person):
        self._checkFilter()

        for tag in self.db.listTags(person.getName()):
            self.addTag(tag,person)

    def updateTags(self,new_tags,person):
        self._checkFilter()

        ### Listing tags to add and to remove
        old_tags=self.listTags(person)
        if old_tags==new_tags:
            return
        added_tags=new_tags-old_tags
        removed_tags=old_tags-new_tags

        ### Adding necessary tags
        for tag in added_tags:
            self.addTag(tag,person,False)

        ### Removing necessary tags

        for tag in removed_tags:
            self.removeTag(tag,person,False)

        self.db.setTags(person.getName(),new_tags)

    def listTags(self,person):
        self._checkFilter()

        return set(self.persons_tags[person].keys()) if person in self.persons_tags.keys() else set()

    #####################################
    # Managing tag to person connection #
    #####################################

    def addTag(self,tag,person,only_loading=True):
        self._checkFilter()

        if tag not in self.tags.keys():
            if not only_loading:
                self.db.addTag(tag)
            self.tags[tag]=Tag(lambda:self.filter.filterTag(tag,True),lambda:self.filter.filterTag(tag,False),tag)
            self.tags_persons[tag]=set()
            self.tags_organizer.addTag(self.tags[tag].clone())
            self.completer.setModel(QStringListModel(list(self.tags.keys())))
        self.persons_tags[person][tag]=self.tags[tag].clone()
        self.tags_persons[tag].add(person)
        self.proxys[person].addWidget(self.persons_tags[person][tag])

    def removeTag(self,tag,person,only_loading=True):
        self._checkFilter()

        self.proxys[person].removeWidget(self.persons_tags[person][tag])
        self.persons_tags[person][tag].deleteLater()
        self.persons_tags[person].pop(tag)
        self.tags_persons[tag].remove(person)
        if not self.tags_persons[tag]:
            if not only_loading:
                self.db.deleteTag(tag)
            self.tags_persons.pop(tag)
            self.tags_organizer.removeTag(self.tags[tag].lastTag())
            self.tags[tag].lastTag().deleteLater()
            self.tags.pop(tag)
            self.completer.setModel(QStringListModel(list(self.tags.keys())))
            self.filter.filterTag(tag,False)

    def listPersons(self,tag):
        self._checkFilter()

        return self.tags_persons[tag] if tag in self.tags_persons.keys() else set()

    def getCompleter(self):
        self._checkFilter()

        return self.completer

    def proxy(self,person):
        self._checkFilter()

        return self.proxys[person]
