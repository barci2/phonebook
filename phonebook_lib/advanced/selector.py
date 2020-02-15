from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ..base import constants as c

############
# Selector #
############

class Selector():
    def __init__(self,selected_label):
        ### Variables Definitions
        self.enabled=set()                 # Set of all not filtered persons
        self.checked=set()                 # Set of all checked persons
        self.selected_label=selected_label # Label for number of selected persons
        self.filter=None

    def setFilter(self,filter):
        self.filter=filter

    def addPerson(self,person):
        self.enabled.add(person)

    def removePerson(self,person):
        if person in self.enabled:
            self.enabled.remove(person)
        if person in self.checked:
            self.checked.remove(person)

    def disablePerson(self,person):
        self.enabled.remove(person)

    def enablePerson(self,person):
        self.enabled.add(person)

    def setPerson(self,person,mode):
        if self.filter==None:
            raise AssertionError("Filter not set")

        if mode and person not in self.checked:
            self.checked.add(person)
            person.setActive(True)
            self.selected_label.setSelected(len(self.checked),len(self.filter.listPersons()))

        elif not mode and person in self.checked:
            self.checked.remove(person)
            person.setActive(False)
            self.selected_label.setSelected(len(self.checked),len(self.filter.listPersons()))


    def isAllChecked(self):
        return self.enabled.issubset(self.checked)

    def setAll(self,mode):
        for person in self.enabled:
            self.setPerson(person,mode)

    def setOnlyActive(self,active_person):
        for person in self.enabled:
            if person!=active_person:
                self.setPerson(person,False)
        self.setPerson(active_person,True)

    def listChecked(self):
        return self.checked
