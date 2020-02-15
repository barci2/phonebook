from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os,mimetypes
from .fbchat import Session,Client,User,ExternalError,HTTPError
import time

from ..base import constants as c
from ..base.fancy import *

mimetypes.init()

class MessageLabel(QLabel):
    def __init__(self,message,top=False,bottom=False):
        super().__init__()
        font=QFont("Segoe UI")
        font.setWeight(QFont.Normal)
        font.setPointSize(11)
        self.setFont(font)
        self.setText(message)
        self.setStyleSheet("""
        border-bottom-left-radius: 16px;
        border-bottom-right-radius: {bottom}px;
        border-top-left-radius: 16px;
        border-top-right-radius: {top}px;
        padding: 8px;
        background: solid qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #6df, stop: 1 #27f
        );
        color: #fff;
        """.format(bottom=(2 if bottom else 16),top=(2 if top else 16)))

class FileLabel(QLabel):
    def __init__(self,message,top=False,bottom=False):
        super().__init__()
        font=QFont("Segoe UI")
        font.setWeight(QFont.Normal)
        font.setPointSize(11)
        self.setFont(font)
        self.setText(message)
        self.setStyleSheet("""
        border-bottom-left-radius: 16px;
        border-bottom-right-radius: {bottom}px;
        border-top-left-radius: 16px;
        border-top-right-radius: {top}px;
        padding: 8px;
        background: solid qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #fff, stop: 1 #6df
        );
        color: #27f;
        """.format(bottom=(2 if bottom else 16),top=(2 if top else 16)))

class MessageTextEdit(QTextEdit):
    def __init__(self,placeholder):
        super().__init__()
        font=QFont("Segoe UI")
        font.setWeight(QFont.Normal)
        font.setPointSize(11)
        self.setFont(font)

        self.placeholder=placeholder
        self.setPlaceholderText(placeholder)
        self.textChanged.connect(self.updateSize)
        self.updateSize()

        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.setStyleSheet("""
            border-bottom-left-radius: 15px;
            border-bottom-right-radius: 2px;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            background: solid qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #6df, stop: 1 #27f
            );
            padding: 8px;
            color: #fff;
        """)

    def calcSize(self):
        fm=QFontMetrics(self.font())
        text=self.toPlainText()
        return min(max(fm.size(0,text).width()+len(text)+35,fm.size(0,self.placeholder).width()+22,190),c.screen_dims[0]-50),min(max(fm.size(0,text).height()+text.count('\n')+24,fm.size(0,self.placeholder).height()+24),c.screen_dims[1]-180)

    def focusOutEvent(self,event):
        super().focusOutEvent(event)

    def updateSize(self):
        w,h=self.calcSize()
        self.setMinimumWidth(w)
        self.setFixedHeight(h)

class FileDrop(QPushButton):
    def __init__(self):
        super().__init__()
        font=QFont("Segoe UI")
        font.setWeight(QFont.Normal)
        font.setPointSize(11)
        self.setFont(font)
        self.unsetFile()
        self.clicked.connect(self.selectFile)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            border-bottom-left-radius: 15px;
            border-bottom-right-radius: 15px;
            border-top-left-radius: 15px;
            border-top-right-radius: 2px;
            background: solid qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #fff, stop: 1 #6df
            );
            padding: 6px;
            color: #27f;
        """)

    def dragEnterEvent(self,event):
        event.acceptProposedAction()
        self.setCheckable(True)
        self.setChecked(True)

    def dragLeaveEvent(self,event):
        self.setChecked(False)
        self.setCheckable(False)

    def dropEvent(self,event):
        event.acceptProposedAction()
        self.setChecked(False)
        self.setCheckable(False)
        path=event.mimeData().urls()[0].path()
        if os.path.isfile(path):
            self.setFile(path)
        else:
            self.unsetFile()

    def unsetFile(self):
        self.setText("Attach File")
        self.path=None

    def setFile(self,path):
        self.path=path
        self.setText(os.path.split(path)[1])
        self.update()

    def getFiles(self):
        return [(os.path.split(self.path)[1],open(self.path,"rb"),mimetypes.types_map[os.path.splitext(self.path)[1]] if os.path.splitext(self.path)[1] in mimetypes.types_map else "text/plain")] if self.path!=None else []

    def getFilesNames(self):
        return [self.text()] if self.path!=None else []

    def selectFile(self):
        dialog=QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():
            self.setFile(dialog.selectedFiles()[0])
        else:
            self.unsetFile()

class Messenger():
    def __init__(self,db,selector,warning_signal):
        self.db=db
        self.selector=selector
        self.warning=warning_signal
        self.session=None
        self.client=None

    def loginDialog(self):
        dialog=FancyDialog("Messenger Sign In",c.messenger_icon_file)
        login_le=FancyLineEdit("User",self.db.getOption("MESSENGER_USER"))
        password_le=FancySecureLineEdit("Password",self.db.getOption("MESSENGER_PASSWORD"))
        layout=FancyVGridLayout([
            login_le,
            password_le,
            [FancyTextButton(dialog.accept,"Sign In"),FancyTextButton(dialog.reject,"Cancel")],
            FancyVGridLayout.Stretch()
        ],zero_margins=False)
        dialog.setLayout(layout)
        if dialog.exec_()==FancyDialog.Accepted:
            login=login_le.text()
            pwd=password_le.text()
            self.login(user=login,password=pwd)
            if self.session!=None:
                self.db.setOption("MESSENGER_USER",login)
                self.db.setOption("MESSENGER_PASSWORD",pwd)

    def login(self,user=None,password=None):
        if user==None or password==None:
            user,password=self.db.getOption("MESSENGER_USER"),self.db.getOption("MESSENGER_PASSWORD")
        try:
            self.session=Session.login(user,password)
            self.client=Client(session=self.session)
        except ExternalError as e:
            if e.message.startswith("Login failed"):
                self.warning("Invalid user or password to messenger")
                self.session=None
                self.client=None
                return
            else:
                raise e
        except HTTPError as e:
            self.warning("Internet not avaliable")
            self.session=None
            self.client=None
            return

        if not self.session.is_logged_in():
            self.warning("Invalid user or password to messenger")
            self.session=None
            self.client=None

    def isId(self,login):
        return login.isdigit()

    def getUser(self,url):
        if self.session==None:
            raise AssertionError("Session not initialized")
        base="https://www.messenger.com/t/"
        if not url.startswith(base):
            return None
        login=url[len(base):]
        if self.isId(login):
            return User(session=self.session,id=login)
        else:
            fetches=list(self.client.search_for_users(name=login,limit=1))
            return fetches[0] if len(fetches) else None

    def getUsers(self,persons_list):
        if self.session==None:
            return [],"User not logged in"
        report=""
        users=[]
        for person in persons_list:
            user=self.getUser(person.messenger)
            if user==None:
                report+="Could not connect to conversaiton with {name}\n".format(person.getName())
            else:
                users.append(user)
        return users,report

    def sendMessage(self,persons_list,message,files=[],files_names=[],separate_lines=False):
        try:
            if len(files)>0:
                files=self.session._upload(files)
        except:
            self.warning("Could not upload files")
            files=[]

        users,report=self.getUsers(persons_list)
        if report!="":
            self.warning(report)
        if users==[]:
            return

        infos=list(self.client.fetch_thread_info([user.id for user in users]))
        names=[user_data.name for user_data in infos]

        dialog=FancyDialog("",c.messenger_icon_file)

        n=message.count('\n')
        layout=FancyVGridLayout([FancyLabel("To:\n"+"".join(sorted([name+(',' if i%3!=2 else ",\n") for i,name in enumerate(names)])))]+
            (
                ([MessageLabel('\n'.join(message.split('\n')[:20])+('\n...' if n>20 else ''),False,len(files))] if message!="" else
                []) if not separate_lines else
                [MessageLabel(line,i!=0,i!=n or len(files)>0) for i,line in enumerate(message.split('\n')) if line!='' and i<20]
            )+
            ([MessageLabel("...",True,len(files)>0)] if n>20 and separate_lines else [])+
            [FileLabel(file_name,message!="" or i!=0,i!=len(files_names)-1) for i,file_name in enumerate(files_names)]+
            [
                [FancyTextButton(dialog.accept,"Send"),FancyTextButton(dialog.reject,"Cancel")],
                FancyVGridLayout.Stretch()
        ],zero_margins=False)

        dialog.setLayout(layout)
        if not dialog.exec_():
            return

        b=True

        for user in users:
            try:
                if separate_lines:
                    for line in message.split('\n'):
                        user.send_text(line)
                        time.sleep(1)
                    user.send_files(files)
                    time.sleep(1)
                else:
                    user.send_text(message,files=files)
                    time.sleep(1)
            except:
                self.warning("Message to {name} not sent".format(name=user.name))
                b=False

        if b:
            self.warning("Messages sent successfully")

    def sendMessageGui(self):
        persons_list=self.selector.listChecked()
        if len(persons_list)==0:
            return
        if self.session==None:
            self.loginDialog()
        if self.session==None:
            return

        separate=False
        dialog=FancyDialog("Message Creator",c.messenger_icon_file)
        text_edit=MessageTextEdit("Message Text")
        text_edit.show()
        filedrop=FileDrop()
        def sendSeparate():
            nonlocal dialog,separate
            separate=True
            dialog.accept()
        layout=FancyVGridLayout([
            text_edit,
            filedrop,
            [FancyTextButton(dialog.accept,"Send In One Line"),FancyTextButton(sendSeparate,"Send In Separate Lines",sendSeparate),FancyTextButton(dialog.reject,"Cancel")],
            FancyVGridLayout.Stretch()
        ],zero_margins=False)
        dialog.setLayout(layout)
        if dialog.exec_()==FancyDialog.Accepted:
            if text_edit.toPlainText()=="" and len(filedrop.getFiles())==0:
                self.warning("Cannot send an empty message")
                return
            self.sendMessage(persons_list,text_edit.toPlainText(),filedrop.getFiles(),filedrop.getFilesNames(),separate)
