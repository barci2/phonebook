from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path
from sortedcontainers import SortedSet
from bisect import bisect

from ..base import constants as c
from .personal_data import PersonalData
from ..base.fancy import *

class NameFilter():
    def __init__(self,s,person=None,endian=False):
        self.endian=endian
        self.s=s
        self.person=person

    def setEndian(self,value):
        self.endian=value

    def __lt__(self,s):
        if not self.endian^s.endian:
            if self.s==s.s:
                if self.person==None and s.person==None:
                    return False
                if self.person==None and s.person!=None:
                    return not self.endian
                if self.person!=None and s.person==None:
                    return s.endian
                return self.person<s.person
            return self.s<s.s
        if s.endian and self.s.startswith(s.s):
            return True
        if self.endian and s.s.startswith(self.s):
            return False
        if self.s==s.s:
            if self.person==None and s.person==None:
                return False
            if self.person==None and s.person!=None:
                return not self.endian
            if self.person!=None and s.person==None:
                return s.endian
            return self.person<s.person
        return self.s<s.s

    def __eq__(self,s):
        return (not self<s) and (not s<self)

    def __hash__(self):
        return hash((self.s,self.person))

class PersonalDataFilter(QVBoxLayout):
    def __init__(self,db,tags,selector,rating=c.default_rating,tab_size=c.tab_size):
        ### Layout Initializing
        super().__init__()
        self.addStretch(2)
        self.setSpacing(0)

        ### Major Connections
        self.db=db
        self.tags=tags
        self.selector=selector

        ### Internal Variables
        self.persons=dict()            # Persons Dictionary (person:{'filters':0,'old name':name})
        self.filtered_tags=set()       # List of filtered tags names for evaluating filtering after adding a person
        self.rating=c.default_rating   # Current Rating Filter
        self.rating_filtered=set()     # List of persons filtered by rating
        self.names_set=SortedSet()     # Names set used for sorting
        self.names_filters=SortedSet() # List of filters by names and persons
        self.name_filtered=set()       # List of persons filtered by name
        self.current_name_filter=""    # Name filter to update persons with

        ### Loading Persons From Database
        for name in self.db.listNames():
            self.addPerson(name)
        self.updateWidths()
        self.filterRating(rating)

    #########################
    # Convenience Functions #
    #########################

    def listPersons(self):
        return set(self.persons.keys())

    def addFilter(self,person,n=1):
        if 'filters' not in self.persons[person].keys():
            self.persons[person]['filters']=0

        if 0>=self.persons[person]['filters']>=-n+1:
            person.hide()
            self.selector.disablePerson(person)
        self.persons[person]['filters']+=n

    def removeFilter(self,person,n=1):
        self.persons[person]['filters']-=n
        if 0>=self.persons[person]['filters']>=-n+1:
            person.show()
            self.selector.enablePerson(person)

    ############################
    # Name Filtering Functions #
    ############################

    def filterName(self,name):
        self.current_name_filter=name
        l=list(self.names_filters)
        persons=set(filter.person for filter in l[bisect(l,NameFilter(name)):bisect(l,NameFilter(name,endian=True))])
        for person in persons:
            if person in self.name_filtered:
                self.name_filtered.remove(person)
                self.removeFilter(person)

        for person in self.listPersons()-persons:
            if person not in self.name_filtered:
                self.name_filtered.add(person)
                self.addFilter(person)

    def updateNameFiltering(self,person):
        if any(NameFilter(self.current_name_filter)<NameFilter(name_filter,person)<NameFilter(self.current_name_filter,endian=True) for name_filter in person.getName().split(' ')):
            if person in self.name_filtered:
                name_filtered.remove(person)
                self.removeFilter(person)
        else:
            if person not in self.name_filtered:
                name_filtered.add(person)
                self.addFilter(person)

    ############################
    # Tags Filtering Functions #
    ############################

    def filterTag(self,tag,mode):
        ### Regulating if tag is being filtered
        if (tag in self.filtered_tags) ^ (not mode):
            return
        self.filtered_tags.add(tag) if mode else self.filtered_tags.remove(tag)

        ### Filtering persons not having a tag by tag
        for person in self.listPersons()-self.tags.listPersons(tag):
            self.addFilter(person) if mode else self.removeFilter(person)

    ##############################
    # Rating Filtering Functions #
    ##############################

    def filterRating(self,rating):
        ### Updating Rating Value
        self.rating=rating

        ### Filtering Persons By Rating
        for person in self.listPersons():
            self.updateRating(person)

    def updateRating(self,person):
        ### Filter On
        if person.getRating()<self.rating and person not in self.rating_filtered:
            self.addFilter(person)
            self.rating_filtered.add(person)

        ### Filter Off
        if person.getRating()>=self.rating and person in self.rating_filtered:
            self.rating_filtered.remove(person)
            self.removeFilter(person)

    #################
    # Adding Person #
    #################

    def addPerson(self,name,new=False):
        ### Creating new PersonalData object
        if new:
            if self.db.addName(name)==None:
                return
            person=PersonalData(name,self.db,self.tags,self,self.selector,self.rating)
        else:
            person=PersonalData(name,self.db,self.tags,self,self.selector)

        ### Updating person's name
        self.names_set.add(person.getSortableName())
        self.persons[person]=dict()
        self.persons[person]['old name']=name
        self.persons[person]['old sortable name']=person.getSortableName()
        self.names_filters.add(NameFilter(name,person))

        if new:
            self.updateWidths()

        ### Inserting PersonalData in proper place
        self.insertWidget(bisect(list(self.names_set),person.getSortableName())-1,person)

        ### Updating person's filters
        if person.getRating()<self.rating:
            self.rating_filtered.add(person)

        self.addFilter(person,len(self.filtered_tags-self.tags.listTags(person))+(person in self.rating_filtered))

        ### Edit if a new person
        if new:
            person.edit()

    ############################
    # Updating Persons' Widths #
    ############################

    def updateWidths(self):
        widths=tuple(max(tuple(person.getWidths()[i] for person in self.persons)+(0,)) for i in range(5))
        for person in self.persons:
            person.updateWidths(widths)

    ################################
    # Disabling Persons' Text Edit #
    ################################

    def hideTextEdits(self):
        for person in self.persons:
            person.hideTextEdit()

    ###################
    # Removing Person #
    ###################

    def deletePerson(self,person):
        ### Confirmation with message box
        message_box=FancyMessageBox([FancyMessageBox.Ok,FancyMessageBox.Cancel],c.question_icon_file,"","Are you sure you want to delete {person}?".format(person=person.getName()))
        if not message_box.exec():
            return

        ### Deleting person's data
        name=self.persons[person]['old name']
        sortable_name=self.persons[person]['old sortable name']

        self.db.deleteName(name)
        self.tags.removePerson(person)
        self.selector.removePerson(person)

        self.persons.pop(person)
        self.names_set.remove(sortable_name)
        self.removeWidget(person)
        self.names_filters.remove(NameFilter(name,person))

        self.updateWidths()

        person.deleteLater()

    ##########################
    # Updating Person's Name #
    ##########################

    def updateName(self,person):
        ### Checking if action is necessary
        if person.getName()==self.persons[person]['old name']:
            return

        ### Executing action
        self.names_filters.remove(NameFilter(self.persons[person]['old name'],person))
        self.names_filters.add(NameFilter(person.getName(),person))
        self.updateNameFiltering(person)

        self.names_set.remove(self.persons[person]['old sortable name'])
        self.names_set.add(person.getSortableName())
        self.removeWidget(person)
        self.insertWidget(bisect(list(self.names_set),person.getSortableName())-1,person)
        self.persons[person]['old name']=person.getName()
        self.persons[person]['old sortable name']=person.getSortableName()
