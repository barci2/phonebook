from pysqlcipher3 import dbapi2 as sqlite3
from pathlib import Path
import phonenumbers
import urllib
import json
import numpy as np
import os

from ..base import constants as c
from .photo_crypt import PhotoCrypt

class Database():
    def __init__(self,db_file,warning_signal):
        self.db=sqlite3.connect(str(db_file),check_same_thread=False)
        self.db_cursor=self.db.cursor()
        self.warning_signal=warning_signal
        self("PRAGMA cipher_add_random=phonebook")

    #########################
    # Convenience Functions #
    #########################

    def checkDecrypted(self):
        try:
            self.db_cursor.execute("SELECT * FROM Options WHERE false")
        except sqlite3.DatabaseError as e:
            if e.args==("file is not a database",):
                return False
            raise e
        return True

    def decrypt(self,p):
        if p=='':
            self.warning_signal("Password cannot be empty")
            return False
        self("PRAGMA key='{p}'",disarm=False,p=p)
        self("PRAGMA kdf_iter=1000000")

        return True

    def encrypt(self,p):
        if p=='':
            self.warning_signal("Password cannot be empty")
            return False
        self("PRAGMA rekey='{p}'",disarm=False,p=p)
        return True

    def disarm(self,s):
        return urllib.parse.quote(str(s) if type(s)!=bytes else s.decode('8859'))

    def arm(self,s):
        return urllib.parse.unquote(s) if type(s)==str else s

    def __call__(self,query,disarm=True,**kwargs):
        kwargs={arg:(self.disarm(kwargs[arg]) if disarm else kwargs[arg]) for arg in kwargs}
        r=self.db_cursor.execute(query.format(**kwargs))
        self.db.commit()
        return [tuple(self.arm(element) for element in row) if len(row)>1 else self.arm(row[0]) for row in r]

    ###########
    # Options #
    ###########

    def checkOption(self,option):
        return self("SELECT * FROM Options WHERE Name='{option}'",option=option)!=[]

    def setOption(self,option,value):
        if not self.checkOption(option):
            raise AssertionError("Option not recognized")
        self("UPDATE Options SET Value='{value}' WHERE Name='{option}'",value=value,option=option)
        return self.getOption(option)

    def getOption(self,option):
        if not self.checkOption(option):
            raise AssertionError("Option not recognized")
        return self("SELECT Value FROM Options WHERE Name='{option}'",option=option)[0]

    ########
    # Name #
    ########

    def listNames(self):
        return [row[0] for row in self('SELECT * FROM Contacts')]

    def checkName(self,name):
        return self("SELECT * FROM Contacts WHERE Name = '{name}'",name=name)!=[]

    def addName(self,name,rating=1):
        if name=="":
            self.warning_signal("Name cannot be empty")
            return None
        if not self.checkName(name):
            self("INSERT INTO Contacts VALUES ('{name}',NULL,NULL,NULL,NULL,NULL,NULL,'%5B%5D',1,{rating})",name=name,rating=rating)
            return name
        else:
            self.warning_signal("Name already exists")
            return None

    def deleteName(self,name):
        if name=="":
            self.warning_signal("Name cannot be empty")
            return None
        self("DELETE FROM Contacts WHERE Name = '{name}'",name=name)
        return None

    def rename(self,old_name,new_name):
        if new_name=="":
            self.warning_signal("Name cannot be empty")
            return old_name

        if old_name!=new_name and not self.checkName(new_name):
            self("UPDATE Contacts SET Name = '{new_name}' WHERE Name = '{old_name}'",new_name=new_name,old_name=old_name)
            return new_name
        else:
            if old_name!=new_name:
                self.warning_signal("Name already exists")
                return old_name
            return new_name

    ################
    # Phone Number #
    ################

    def getPhoneNumber(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        l=self("SELECT [Phone Number] FROM Contacts WHERE Name = '{name}'",name=name)
        return l[0] if l[0]!='' else None

    def setPhoneNumber(self,name,phone_number):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        if phone_number!='':
            try:
                number=phonenumbers.parse(phone_number)
            except phonenumbers.NumberParseException as e:
                if e.error_type==phonenumbers.NumberParseException.INVALID_COUNTRY_CODE:
                    try:
                        number=phonenumbers.parse(phone_number,region=c.phone_default_region)
                    except:
                        self.warning_signal("Invalid phone number")
                        return self.getPhoneNumber(name)
                else:
                    self.warning_signal("Invalid phone number")
                    return self.getPhoneNumber(name)
            except:
                self.warning_signal("Invalid phone number")
                return self.getPhoneNumber(name)

            formatted_number=phonenumbers.format_number(number,phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        else:
            formatted_number=''

        self("UPDATE Contacts SET 'Phone Number' = '{number}' WHERE Name = '{name}'",number=formatted_number,name=name)
        return formatted_number if formatted_number!='' else None

    #########
    # Email #
    #########

    def getEmail(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        l=self("SELECT Email FROM Contacts WHERE Name = '{name}'",name=name)
        return l[0] if l[0]!='' else None

    def setEmail(self,name,email):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None

        email=email.strip().lower()

        if email!='' and '@' not in email or ' ' in email or '\n' in email:
            self.warning_signal("Invalid Email")
            return self.getEmail(name)

        self("UPDATE Contacts SET 'Email' = '{email}' WHERE Name='{name}'",email=email,name=name)
        return email if email!='' else None

    ###################
    # Additional Info #
    ###################

    def getAdditionalInfo(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        return self("SELECT [Additional Info] FROM Contacts WHERE Name = '{name}'",name=name)[0]

    def setAdditionalInfo(self,name,info):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        self("UPDATE Contacts SET 'Additional Info'='{info}' WHERE Name='{name}'",info=info,name=name)

    ############
    # LinkedIn #
    ############

    def getLinkedIn(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        l=self("SELECT LinkedIn FROM Contacts WHERE Name = '{name}'",name=name)
        return l[0] if l[0]!='' else None

    def setLinkedIn(self,name,linkedin):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        self("UPDATE Contacts SET 'LinkedIn'='{linkedin}' WHERE Name='{name}'",linkedin=linkedin,name=name)
        return linkedin if linkedin!='' else None

    #################
    # Research Gate #
    #################

    def getResearchGate(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        l=self("SELECT [Research Gate] FROM Contacts WHERE Name = '{name}'",name=name)
        return l[0] if l[0]!='' else None

    def setResearchGate(self,name,researchgate):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        self("UPDATE Contacts SET 'Research Gate'='{researchgate}' WHERE Name='{name}'",researchgate=researchgate,name=name)
        return researchgate if researchgate!='' else None

    #############
    # Messenger #
    #############

    def getMessenger(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        l=self("SELECT Messenger FROM Contacts WHERE Name = '{name}'",name=name)
        return l[0] if l[0]!='' else None

    def setMessenger(self,name,messenger):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        self("UPDATE Contacts SET 'Messenger'='{messenger}' WHERE Name='{name}'",messenger=messenger,name=name)
        return messenger if messenger!='' else None

    ########
    # Tags #
    ########

    def checkTag(self,tag):
        return self("SELECT * FROM Tags WHERE Tag = '{tag}'",tag=tag)!=[]

    def addTag(self,tag,row=0):
        if self.checkTag(tag):
            self.warning_signal("Tag already exists")
            return None
        self("INSERT INTO Tags VALUES ('{tag}','{row}')",tag=tag,row=row)
        return tag

    def getRow(self,tag):
        if not self.checkTag(tag):
            self.warning_signal("Tag does not exist")
            return None

        return self("SELECT Row FROM Tags WHERE Tag = '{tag}'",tag=tag)[0]

    def removeRow(self,row):
        if self("SELECT * FROM Tags WHERE Row = {row}",row=row)!=[]:
            self.warning_signal("Row has tags in it")
            return None

        self("UPDATE Tags SET Row = Row-1 WHERE Row > {row}",row=row)

    def setRow(self,tag,row,new=False):
        if not self.checkTag(tag):
            self.warning_signal("Tag does not exist")
            return None

        if new:
            self("UPDATE Tags SET Row = Row+1 WHERE Row >= {row}",row=row)
        self("UPDATE Tags SET Row = {row} WHERE Tag = '{tag}'",row=row,tag=tag)
        return self.getRow(tag)

    def numRow(self):
        num=self("SELECT MAX(Row) FROM Tags")[0]
        return num if num!=None else 0

    def deleteTag(self,tag):
        if not self.checkTag(tag):
            self.warning_signal("Tag does not exist")
            return None

        self("DELETE FROM Tags WHERE Tag = '{tag}'",tag=tag)
        return None

    def _listAllTags(self):
        return list(self("SELECT Tag FROM Tags"))

    def listTags(self,name=None):
        if name==None:
            return self._listAllTags()
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return set()

        return set(json.loads(self("SELECT Tags FROM Contacts WHERE Name='{name}'",name=name)[0]))

    def setTags(self,name,tags):
        tags=list(tags)
        if name!=None and not self.checkName(name):
            self.warning_signal("Name does not exist")
            return self.listTags(name)
        for tag in tags:
            if not self.checkTag(tag):
                self.warning_signal("Tag does not exist")
                return self.listTags(name)
        self("UPDATE Contacts SET Tags='{tags}' WHERE Name='{name}'",tags=json.dumps(tags),name=name)
        return tags

    ################
    # Acquaintance #
    ################

    def getAcquaintance(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        return int(self("SELECT Acquaintance FROM Contacts WHERE Name = '{name}'",name=name)[0])

    def setAcquaintance(self,name,acquaintance):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        self("UPDATE Contacts SET 'Acquaintance'='{acquaintance}' WHERE Name = '{name}'",acquaintance=acquaintance,name=name)
        return acquaintance

    ##########
    # Rating #
    ##########

    def getRating(self,name):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        return min(self("SELECT Rating FROM Contacts WHERE Name = '{name}'",name=name)[0],c.max_rating)

    def setRating(self,name,rating):
        if not self.checkName(name):
            self.warning_signal("Name does not exist")
            return None
        rating=min(rating,c.max_rating)
        self("UPDATE Contacts SET Rating = '{rating}' WHERE Name = '{name}'",rating=rating,name=name)
        return rating
