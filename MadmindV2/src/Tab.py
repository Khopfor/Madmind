from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize
from PyQt5.QtGui import QPixmap,QPainter,QTextCursor
from PyQt5.QtSvg import *
import glob
import sys
import os

from matplotlib.widgets import Widget

from Canvas import Canvas

class Tab (QWidget):
    def __init__(self,tabId,tabWidget):
        super().__init__()
        self.tabId=tabId
        self.tabWidget=tabWidget
        self.canvas=None
        # Buttons
        widget=QWidget(self)
        self.vbox=QVBoxLayout(self)
        # self.vbox.setStyleSheet("border: 0px")
        mindmapList=os.listdir("mindmaps")
        self.buttongroup = QButtonGroup()
        self.buttongroup.buttonClicked[QAbstractButton].connect(self.loadMindmap)
        for i,mmName in enumerate(mindmapList) :
            button=QPushButton(mmName,self)
            self.buttongroup.addButton(button, 1)
            # button.setFont(QtGui.QFont("Sanserif", 15))
            self.vbox.addWidget(button)
        # self.vbox.setGeometry(QRect(0,0,100,100))
        widget.setLayout(self.vbox)
        widget.setGeometry(QRect(0,0,200,40*len(self.buttongroup.buttons())))
        # self.setLayout(self.vbox)

    def loadMindmap(self,button):
        self.tabName=button.text()
        for button in self.buttongroup.buttons():
           self.vbox.removeWidget(button)
           button.deleteLater()
        self.tabWidget.setTabText(self.tabId,self.tabName)
        loading=QLabel("Loading...",self)
        self.vbox.addWidget(loading)
        self.vbox.update()
        # Canvas
        self.canvas=Canvas(self)
        self.canvas.initMindmap(self)
        # Text Editor
        f=open("mindmaps/"+self.tabName+"/"+self.tabName+".txt",'r')
        contents=f.read()
        f.close()
        self.textEdit=QTextEdit(self)
        self.textEdit.setPlainText(contents)
        # x,y,w,h=self.canvas.geometry().getCoords()
        self.textEdit.setGeometry(self.parent().width()-402,self.parent().height()-202,400,200)
        self.textEdit.show()
        self.vbox.removeWidget(loading)

    def goTo(self,target):
        if isinstance(target,int):
            target='#'+str(target)+':'
        doc = self.textEdit.document()
        # self.textEdit.setFocus()
        for i,line in enumerate(self.textEdit.toPlainText().split('\n')):
            if target in line:
                n=i
                cursor = QTextCursor(doc.findBlockByLineNumber(n))
                self.textEdit.setTextCursor(cursor)
                break
        self.textEdit.verticalScrollBar().setValue(10)

    def resizeElements(self,w,h):
        if self.canvas!=None:
            self.canvas.setGeometry(0,0,w,h)
            self.canvas.minimap.setGeometry(self.canvas.width()-202,2,200,200)
            self.textEdit.setGeometry(self.parent().width()-402,self.parent().height()-202,400,200)

    def writeNewEdge(self,e):
        def insertId (id1,id2,way):
            contents=self.textEdit.toPlainText()
            idIndex=contents.find("#"+str(id1)+":")
            endLineIndex=contents.find('\n',idIndex)
            if endLineIndex==-1:toIndex=contents.find(way+':',idIndex)
            else :toIndex=contents.find(way+':',idIndex,endLineIndex)
            if toIndex==-1:
                colonIndex=contents.find(':',idIndex)
                contents=contents[:colonIndex+1]+way+":"+str(id2)+';'+contents[colonIndex+1:]
            else:
                semicolonIndex=contents.find(';',toIndex)
                contents=contents[:semicolonIndex]+','+str(id2)+contents[semicolonIndex:]
            self.textEdit.setPlainText(contents)
        insertId(e.fr.id,e.to.id,'to')
        insertId(e.to.id,e.fr.id,'from')

    def writeNewSize(self,bub):
        size=str(round(bub.size,3))
        contents=self.textEdit.toPlainText()
        idIndex=contents.find("#"+str(bub.id)+":")
        endLineIndex=contents.find('\n',idIndex)
        if endLineIndex==-1:sizeIndex=contents.find("size",idIndex)
        else :sizeIndex=contents.find("size",idIndex,endLineIndex)
        if sizeIndex==-1:
            if endLineIndex==-1:
                contents=contents+';size='+size
            else :
                contents=contents[:endLineIndex]+";size="+size+';'+contents[endLineIndex:]
        else:
            semicolonIndex=contents.find(';',sizeIndex)
            delimIndex=contents.find('=',sizeIndex,semicolonIndex)
            if delimIndex!=-1:
                contents=contents[:delimIndex+1]+size+contents[semicolonIndex:]
        self.textEdit.setPlainText(contents)

    def keyPressEvent(self, e):
        if (e.key()==Qt.Key_S) and (QApplication.keyboardModifiers() and Qt.ControlModifier):
            f=open("mindmaps/"+self.tabName+"/"+self.tabName+".txt",'w')
            f.write(self.textEdit.toPlainText())
            f.close()
        return super().keyPressEvent(e)