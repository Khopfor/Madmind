# PyQt imports
from PyQt5.QtWidgets import *


class TextEdit (QTextEdit):
    def __init__(self,parent):
        super().__init__(parent)
        self.setFontFamily("monospace")
        self.hide()
        self.h=150
        self.w=400

    def removeBubble(self,bub):
        text=self.toPlainText()
        startIndex=text.find("#{}:".format(bub.id))
        if startIndex>=0:
            endIndex=text.find("\n#",startIndex+1)
            if endIndex>=0:
                text=text[0:startIndex]+'\n'+text[endIndex:]
            else :
                text=text[0:startIndex]
            self.setPlainText(text)
        else:
            print("Error while removing bubble : ID",bub.id,"doesn't exist.")

    def updateBubble(self,bub):
        text=self.toPlainText()
        startIndex=text.find("#{}:".format(bub.id))
        if startIndex>=0:
            endIndex=text.find("\n#",startIndex+1)
            if endIndex>=0:
                text=text[0:startIndex]+bub.toString()+'\n'+text[endIndex:]
            else :
                text=text[0:startIndex]+bub.toString()
            self.setPlainText(text)
        else:
            print("Error while updating bubble : ID",bub.id,"doesn't exist.")

    def updateGeom(self):
        self.setGeometry(self.parent().parent().width()-2-self.w,self.parent().parent().height()-self.h-2,self.w,self.h)