from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ..base import constants as c
from ..base.fancy import *
from ..base.comparable import Comparable

###############################################
# GhostTag - grey, inactive version of the tag #
###############################################

class GhostTag(QPushButton,Comparable):
    def __init__(self,text):
        super(QPushButton,self).__init__()
        super(Comparable,self).__init__()

        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setFlat(True)
        self.setText(text)
        self.setEnabled(False)
        self.setStyleSheet(f"""
            QPushButton {{
                outline: 0px transparent;
                border: 0px transparent;
                padding-left: 5px;
                padding-right: 5px;
                padding-top: 5px;
                padding-bottom: 5px;
                color: {FAKE_TAG_TEXT};
                background: solid {FAKE_TAG};
            }}
        """)
        self.setFocusPolicy(Qt.NoFocus)

    def comparableKey(self):
        return self.text()

#########################################
# TagsOrganizer - organizer of top tags #
#########################################

class TagsOrganizer(QWidget):
    def __init__(self,db,margin=5):
        ### Static Variables Definition
        self.mime_tags=dict()                   # List of all tags and their layouts

        ### Layout Variables
        self.m=margin # Margin for creating new line
        self.lm=10    # Margin at the top and the bottom
        self.s=4      # Spacing between lines

        ### Graphical Stuff
        super().__init__()
        FancyVLayout([FancySortedLayout() for _ in range(db.numRow()+1)],parent=self)
        self.layout().setSpacing(self.s)
        self.layout().setContentsMargins(10,self.lm,0,self.lm)

        ### Drag&Drop Variables Definition
        self.db=db                 # Database
        self.clicked_tag=None      # Which tag has been pressed or is being transported
        self.insertion_point=None  # Potential insertion point height for a dragged tag
        self.ghost_tag=None        # Ghost tag for the clicked tag
        self.ghost_tag_layout=None # Layout in which the ghost tag sits

    #########################
    # Convenience Functions #
    #########################

    def checkMimeData(self,mime_data):
        return mime_data.hasText() and self.clicked_tag!=None and mime_data.text()==self.clicked_tag.text()

    def calcTagPlace(self,y): # return values: place, create_new_tag
        if y<0 or y>self.contentsRect().height():
            return None,False

        n=self.layout().count() # WHAT IF number of tags is 0
        h=self.contentsRect().height()
        jump=(h-self.lm*2+self.s)//n
        y-=self.lm

        if y<self.m:
            return 0,False

        if y+self.s-self.s//2>=jump*n-self.m:
            return n,True

        new=((y+self.s-self.s//2)%jump<self.m or (y+self.s-self.s//2)%jump>=jump-self.m)

        i=min((y+self.m+self.s-self.s//2)//jump,n-(not new))
        return i,new

    #####################
    # Drawing Functions #
    #####################

    def paintEvent(self,e):

        painter=QPainter(self)
        painter.eraseRect(self.rect())
        painter.setRenderHint(QPainter.Antialiasing)

        if self.insertion_point==None:
            return

        y=self.insertion_point

        pen=QPen()
        pen.setColor(QColor(255,255,255))
        pen.setWidth(6)
        pen.setCapStyle(Qt.FlatCap)
        pen.setJoinStyle(Qt.MiterJoin)

        painter.setPen(pen)
        painter.setBrush(QColor(0,0,0,0))

        path=QPainterPath()
        path.moveTo(3,y+self.lm-6)
        path.lineTo(9,y+self.lm)
        path.lineTo(3,y+self.lm+6)

        painter.drawPath(path)


    def drawInsertionHint(self,index):
        if self.clicked_tag==None:
            raise AssertionError("No tag is being dragged right now")

        self.resetHints()

        n=self.layout().count()
        h=self.contentsRect().height()
        jump=(h-self.lm*2+self.s)//n

        self.insertion_point=jump*index-self.s//2
        self.update()

    def drawGhostTag(self,index):
        if self.ghost_tag!=None and self.layout().indexOf(self.ghost_tag_layout)!=index:
            self.ghost_tag_layout.removeWidget(self.ghost_tag)
            self.ghost_tag.deleteLater()
            self.ghost_tag=None
            self.ghost_tag_layout=None
        elif self.ghost_tag!=None:
            return

        self.resetHints()
        self.ghost_tag=GhostTag(self.clicked_tag.text())
        self.ghost_tag_layout=self.layout().itemAt(index)
        self.ghost_tag_layout.addWidget(self.ghost_tag)

    def resetHints(self):
        if self.ghost_tag!=None:
            self.ghost_tag_layout.removeWidget(self.ghost_tag)
            self.ghost_tag.deleteLater()
            self.ghost_tag=None
            self.ghost_tag_layout=None

        if self.insertion_point!=None:
            self.insertion_point=None
            self.update()

    #############################
    # Tags Management Functions #
    #############################

    def addTag(self,tag):
        n=self.db.getRow(tag.text())
        self.layout().itemAt(n).addWidget(tag)
        tag.installEventFilter(self)
        self.mime_tags[tag.text()]=(tag,self.layout().itemAt(n))
        if len(self.mime_tags)>=2:
            self.setAcceptDrops(True)

    def removeTag(self,tag):
        self.layout().itemAt(0).removeWidget(tag)
        self.mime_tags.pop(tag.text())
        if len(self.mime_tags)<=1:
            self.setAcceptDrops(False)

    #####################################################
    # For accepting possible drops (changes mouse icon) #
    #####################################################

    def dragLeaveEvent(self,event):
        self.resetHints()

    def dragEnterEvent(self,event):
        event.acceptProposedAction() if self.checkMimeData(event.mimeData()) else None

    def dragMoveEvent(self,event):
        if not self.checkMimeData(event.mimeData()):
            return

        pos,new=self.calcTagPlace(event.pos().y())

        if new:
            self.drawInsertionHint(pos)
        else:
            self.drawGhostTag(pos)

        event.acceptProposedAction()

    #################
    # Tag Drag&Drop #
    #################

    def raiseTag(self,tag):
        app=QApplication.instance()
        area=self.window()
        app.installEventFilter(area)
        tag.hide()
        old_layout=self.mime_tags[tag.text()][1]
        old_layout.removeWidget(tag)
        self.db.setRow(tag.text(),0)
        self.mime_tags[tag.text()]=(tag,None)
        if old_layout.count()==0:
            if self.layout().indexOf(old_layout)==0:
                self.db.setRow(tag.text(),1)
            self.db.removeRow(self.layout().indexOf(old_layout))
            self.layout().removeItem(old_layout)
        data=QMimeData()
        data.setText(tag.text())
        drag=QDrag(self.parent())
        drag.setMimeData(data)
        drag.exec_()
        if self.mime_tags[tag.text()][1]==None:
            self.layout().itemAt(0).addWidget(tag)
            self.mime_tags[tag.text()]=(tag,self.layout().itemAt(0))
            self.resetHints()
        tag.show()
        app.removeEventFilter(area)


    def dropEvent(self,event):
        if not self.checkMimeData(event.mimeData()):
            return

        self.resetHints()

        i,new=self.calcTagPlace(event.pos().y())
        tag=self.clicked_tag

        i=self.db.setRow(tag.text(),i,new)

        if new:
            l=FancySortedLayout()
            self.layout().insertLayout(i,l)
        else:
            l=self.layout().itemAt(i)

        l.addWidget(tag)
        self.mime_tags[event.mimeData().text()]=(tag,l)

    def mouseMoveEvent(self,event):
        if self.clicked_tag==None:
            return

        if len(self.mime_tags)<=1:
            return

        clicked_tag=self.clicked_tag
        self.raiseTag(clicked_tag)
        self.clicked_tag=None

    def eventFilter(self,tag,event):
        if event.type() not in [QEvent.MouseMove,QEvent.MouseButtonPress,QEvent.MouseButtonRelease,QEvent.MouseButtonDblClick]:
            return False

        if event.type() in [QEvent.MouseButtonPress,QEvent.MouseButtonDblClick]:
            self.clicked_tag=tag
            return False

        if event.type()==QEvent.MouseMove:
            return False

        if event.type()==QEvent.MouseButtonRelease:
            self.clicked_tag=None
            return False
