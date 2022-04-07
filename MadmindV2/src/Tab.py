import os
from time import sleep
# PyQt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize,QTimer
from PyQt5.QtGui import QPixmap,QPainter,QTextCursor
# Local imports
from Canvas import Canvas
from utils import contains

class Tab (QWidget):
    def __init__(self,tabId,tabWidget):
        super().__init__()
        self.tabId=tabId
        self.tabWidget=tabWidget
        self.tabText=self.getTabText()
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.save)
        # Canvas
        self.canvas=Canvas(self)
        # Text Edit Area
        self.textEdit=QTextEdit(self)
        self.textEdit.setFontFamily("monospace")
        self.textEdit.hide()
        # VBox
        vbox=QVBoxLayout(self)
        # Open existing Mindmap
        openLabel=QLabel("Open an existing mindmap :")
        openLabel.setAlignment(Qt.AlignLeft)
        vbox.addWidget(openLabel)
        self.choiceWidget=QWidget(self)
        mindmapList=os.listdir("mindmaps")
        self.buttongroup = QButtonGroup()
        self.buttongroup.buttonClicked[QAbstractButton].connect(self.loadChosenMindmap)
        for i,mmName in enumerate(mindmapList) :
            button=QPushButton(mmName,self)
            self.buttongroup.addButton(button, 1)
            # button.setFont(QtGui.QFont("Sanserif", 15))
            vbox.addWidget(button)
        # New Mindmap option
        newLabel=QLabel("Create a new mindmap :")
        vbox.addWidget(newLabel)
        self.newLineEdit=QLineEdit()
        newButton=QPushButton("Create")
        newButton.clicked.connect(self.createNewMindmap)
        hbox=QHBoxLayout()
        hbox.addWidget(self.newLineEdit)
        hbox.addWidget(newButton)
        vbox.addLayout(hbox)

        self.choiceWidget.setLayout(vbox)
        self.choiceWidget.setGeometry(QRect(10,10,250,40*len(self.buttongroup.buttons())))

    def setTabText(self,text,temp=False):
        if not temp :
            self.tabText=text
        self.tabWidget.setTabText(self.tabId,text)

    def getTabText(self):
        return self.tabWidget.tabText(self.tabId)

    def loadChosenMindmap(self,button):
        self.loadMindmap(button.text())

    def createNewMindmap(self):
        name=self.newLineEdit.text()
        if contains(name,'\n','/','\\'):
            print("Invalid mindmap name.")
        else:
            dirPath="mindmaps/"+name
            if os.path.isdir(dirPath):
                print("This mindmap already exists.")
            else :
                os.mkdir(dirPath)
                os.mkdir(dirPath+"/cache")
                f=open(dirPath+"/"+name+".txt",'w')
                try :
                    template=open("templates/headers.txt",'r')
                    headers=template.read()
                    template.close()
                except:pass
                f.write(headers)
                f.close()
            self.loadMindmap(name)


    def loadMindmap(self,MindmapName):
        self.tabName=MindmapName
        self.setTabText(self.tabName)
        self.choiceWidget.setParent(None)
        # for button in self.buttongroup.buttons():
        #    vbox.removeWidget(button)
        #    button.deleteLater()
        loadingWidget=QWidget(self)
        loadingVBox=QVBoxLayout()
        loadingLabel=QLabel("Loading...")
        loadingVBox.addWidget(loadingLabel,Qt.AlignBottom)
        loadingProgress=QProgressBar()
        loadingVBox.addWidget(loadingProgress,Qt.AlignTop)
        loadingWidget.setLayout(loadingVBox)
        loadingWidget.setLayout(loadingVBox)
        loadingWidget.show()
        # vbox.addWidget(loading)
        # vbox.update()
        f=open("mindmaps/"+MindmapName+"/"+MindmapName+".txt",'r')
        contents=f.read()
        f.close()
        self.canvas.initMindmap(self,contents,loadingProgress)
        loadingWidget.setParent(None)
        self.canvas.show()
        self.textEdit.setPlainText(contents)
        self.textEdit.setGeometry(self.parent().width()-402,self.parent().height()-202,400,200)
        self.textEdit.show()
        if self.tabWidget.parent().width()<700:
            self.tabWidget.parent().resize(1000,900)
        self.timer.start(15000)

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
        if (e.key()==Qt.Key_S) and (QApplication.keyboardModifiers()==Qt.ControlModifier):
            self.save()
        elif (e.key()==Qt.Key_W) and (QApplication.keyboardModifiers()== Qt.ControlModifier):
            self.tabWidget.removeTab(self.tabId)
        return super().keyPressEvent(e)

    def save (self):
        f=open("mindmaps/"+self.tabName+"/"+self.tabName+".txt",'w')
        f.write(self.textEdit.toPlainText())
        f.close()