import os
import subprocess
from time import sleep, time
# PyQt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize,QTimer
from PyQt5.QtGui import QPixmap,QPainter,QTextCursor
# Local imports
from TextEdit import TextEdit
from Help import Help
from Canvas import Canvas
from utils import contains,findDir

class Tab (QWidget):
    def __init__(self,tabId,tabWidget):
        super().__init__()
        self.tabId=tabId
        self.tabWidget=tabWidget
        self.tabText=self.getTabText()
        self.lastSvgTime=0
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.save)
        # Canvas
        self.canvas=Canvas(self)
        # Text Edit Area
        self.textEdit=TextEdit(self)
        self.keepText=""
        # Help
        self.help=Help(self)
        # VBox
        vbox=QVBoxLayout(self)
        ### New Mindmap option ###
        newLabel=QLabel("Create a new mindmap :")
        vbox.addWidget(newLabel)
        self.newLineEdit=QLineEdit()
        newButton=QPushButton("Create")
        newButton.clicked.connect(self.createNewMindmap)
        hbox=QHBoxLayout()
        hbox.addWidget(self.newLineEdit)
        hbox.addWidget(newButton)
        vbox.addLayout(hbox)
        ### Open existing Mindmap ###
        openLabel=QLabel("Open an existing mindmap :")
        openLabel.setAlignment(Qt.AlignLeft)
        vbox.addWidget(openLabel)
        self.choiceWidget=QWidget(self)
        # tree={}
        # def makeTree (dirName,parents,path):
        #     mmdir=False
        #     ls=os.listdir(path)
        #     for o in ls :
        #         if ".txt" in o :
        #             mmdir=True
        #     if mmdir :
        #         b=tree
        #         for p in parents:
        #             b=b[p]
        #         b=b.append(dirName)
        #     else :
        #         for o in ls:
        #             if os.path.isdir(path+"/"+o):
        #                 print(o)
        #                 makeButtons(o,path+"/"+o)
        # makeTree("mindmaps",[],"mindmaps")
        def makeButtons (dirName,path):
            mmdir=False
            ls=os.listdir(path)
            for o in ls :
                if ".txt" in o :
                    mmdir=True
            if mmdir :
                button=QPushButton(dirName,self)
                button.clicked.connect(lambda:self.loadChosenMindmap(button))
                vbox.addWidget(button)
            else :
                widget=QLabel(dirName,self)
                vbox.addWidget(widget)
                for o in ls:
                    if os.path.isdir(path+"/"+o):
                        makeButtons(o,path+"/"+o)
        makeButtons("mindmaps","mindmaps")
        # mindmapList=os.listdir("mindmaps")
        # self.buttongroup = QButtonGroup()
        # self.buttongroup.buttonClicked[QAbstractButton].connect(self.loadChosenMindmap)
        # for i,mmName in enumerate(mindmapList) :
        #     button=QPushButton(mmName,self)
        #     self.buttongroup.addButton(button, 1)
        #     # button.setFont(QtGui.QFont("Sanserif", 15))
        #     vbox.addWidget(button)

        self.setLayout(vbox)
        self.choiceWidget.setLayout(vbox)
        self.choiceWidget.setGeometry(QRect(10,10,250,40*20))

        

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
        loadingWidget=QWidget(self)
        loadingVBox=QVBoxLayout()
        loadingLabel=QLabel("Loading...")
        loadingVBox.addWidget(loadingLabel,Qt.AlignBottom)
        loadingProgress=QProgressBar()
        loadingVBox.addWidget(loadingProgress,Qt.AlignTop)
        loadingWidget.setLayout(loadingVBox)
        loadingWidget.show()
        self.canvas.initMindmap(self,dirPath=findDir(MindmapName,"mindmaps"),progress=loadingProgress)
        loadingWidget.setParent(None)
        self.canvas.show()
        self.textEdit.setPlainText(self.canvas.scene.mindmap.getContents())
        self.textEdit.setGeometry(self.parent().width()-402,self.parent().height()-202,400,200)
        self.textEdit.show()
        if self.tabWidget.parent().width()<700:
            self.tabWidget.parent().resize(1000,900)
        self.timer.start(60000)

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
            self.textEdit.updateGeom()
            self.help.updateGeom()

    def toggleHelp(self):
        self.help.toggle()

    def keyPressEvent(self, e):
        if (e.key()==Qt.Key_S) and (QApplication.keyboardModifiers()==Qt.ControlModifier):
            self.save(True)
        elif (e.key()==Qt.Key_H):
            self.toggleHelp()
        elif (e.key()==Qt.Key_W) and (QApplication.keyboardModifiers()== Qt.ControlModifier):
            self.tabWidget.removeTab(self.tabId)
        return super().keyPressEvent(e)

    def save (self,user=False):
        if self.keepText!=self.textEdit.toPlainText():
            if user :
                self.canvas.scene.mindmap.readHeaders(self.textEdit.toPlainText())
                self.canvas.scene.updateBgColor()
                self.canvas.scene.updateSceneRect()
            print("Saving.")
            f=open(self.canvas.scene.mindmap.dirPath+"/"+self.tabName+".txt",'w')
            f.write(self.textEdit.toPlainText())
            f.close()
            self.keepText=self.textEdit.toPlainText()
            if time()-self.lastSvgTime>2*60 or (user and time()-self.lastSvgTime>20):
                self.lastSvgTime=time()
                os.system("python src/SvgMaker.py "+self.tabName+" "+self.canvas.scene.mindmap.dirPath+" &")




















    # def writeNewEdge(self,e):
    #     def insertId (id1,id2,way):
    #         contents=self.textEdit.toPlainText()
    #         idIndex=contents.find("#"+str(id1)+":")
    #         endLineIndex=contents.find('\n',idIndex)
    #         if endLineIndex==-1:toIndex=contents.find(way+':',idIndex)
    #         else :toIndex=contents.find(way+':',idIndex,endLineIndex)
    #         if toIndex==-1:
    #             colonIndex=contents.find(':',idIndex)
    #             contents=contents[:colonIndex+1]+way+":"+str(id2)+';'+contents[colonIndex+1:]
    #         else:
    #             semicolonIndex=contents.find(';',toIndex)
    #             contents=contents[:semicolonIndex]+','+str(id2)+contents[semicolonIndex:]
    #         self.textEdit.setPlainText(contents)
    #     insertId(e.fr.id,e.to.id,'to')
    #     insertId(e.to.id,e.fr.id,'from')

    # def writeNewSize(self,bub):
    #     size=str(round(bub.size,3))
    #     contents=self.textEdit.toPlainText()
    #     idIndex=contents.find("#"+str(bub.id)+":")
    #     endLineIndex=contents.find('\n',idIndex)
    #     if endLineIndex==-1:sizeIndex=contents.find("size",idIndex)
    #     else :sizeIndex=contents.find("size",idIndex,endLineIndex)
    #     if sizeIndex==-1:
    #         if endLineIndex==-1:
    #             contents=contents+';size='+size
    #         else :
    #             contents=contents[:endLineIndex]+";size="+size+';'+contents[endLineIndex:]
    #     else:
    #         semicolonIndex=contents.find(';',sizeIndex)
    #         delimIndex=contents.find('=',sizeIndex,semicolonIndex)
    #         if delimIndex!=-1:
    #             contents=contents[:delimIndex+1]+size+contents[semicolonIndex:]
    #     self.textEdit.setPlainText(contents)