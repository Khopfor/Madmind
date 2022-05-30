import os
import string
from typing import Iterable
# PyQt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import *
# Local imports
from utils import *

class BubbleContent(QTextEdit):
    def __init__(self,bubble,latexMaker=None):
        super().__init__(bubble.tab.canvas)
        self.bubble=bubble
        self.textEditW=600
        self.textEditH=80
        self.innerSvg=None
        self.latexMaker=latexMaker
        self.setAlignment(Qt.AlignCenter)
        # self.setPalette(QPalette(QColor(255,0,0,100),QColor(255,255,255,100)))
        self.setStyleSheet("background-color:rgba(255,255,255,0);")
        self.setFontFamily("monospace")
        self.setFontPointSize(10)
        self.hide()

    def showTextEdit(self):
        self.textEditH=max(70,1.6*self.bubble.getB())
        pos=self.bubble.tab.canvas.mapFromScene(self.bubble.pos())
        textEditX=int(pos.x()-self.textEditW/2)
        textEditY=int(pos.y()-self.textEditH/2)
        self.setGeometry(textEditX,textEditY,self.textEditW,self.textEditH)
        self.hideContent()
        self.selectAll()
        self.setAlignment(Qt.AlignCenter)
        self.setFontFamily("monospace")
        self.setFontPointSize(10)
        self.show()

    def makeInnerLatexSvg (self):
        lines=self.toPlainText()
        if type(lines)==type(""):
            lines=lines.split('\n')
        cachePath="mindmaps/"+self.bubble.tab.tabName+"/cache/"
        if not os.path.isdir(cachePath):
            os.mkdir(cachePath)
        hash=self.makeIdCode(lines)
        pdfPath=cachePath+hash+".pdf"
        svgPath=cachePath+hash+".svg"
        if not os.path.isfile(svgPath):
            if not os.path.isfile(pdfPath):
                try :
                    self.latexMaker.makePdf(lines,pdfPath,self.bubble.id==0)
                except Exception as e:
                    print("Latex error in content of bubble",self.bubble.id)
                    print("Latex error :",e)
                    self.latexMaker.makePdf(["LATEX ERROR"],pdfPath,self.bubble.id==0)
                os.system('pdf2svg '+pdfPath+" "+svgPath)
                self.fixSvg(svgPath)
            else:
                os.system('pdf2svg '+pdfPath+" "+svgPath)
                self.fixSvg(svgPath)
        if self.innerSvg!=None:
            for item in self.bubble.childItems():
                if isinstance(item,QGraphicsSvgItem):
                    item.deleteLater()
        self.innerSvg=QGraphicsSvgItem(svgPath,parent=self.bubble)
        self.innerSvg.setScale(1)
        size=self.innerSvg.boundingRect().size()
        w=size.width()/2*self.innerSvg.scale()
        h=size.height()/2*self.innerSvg.scale()
        self.bubble.setEllipseSize(w,h)
        self.innerSvg.moveBy(-w,-h)
        self.innerSvg.show()
        if os.path.isfile(pdfPath):
            os.remove(pdfPath)

    def getPlainText(self):
        return self.text

    def hideContent(self):
        if self.innerSvg!=None :
            self.innerSvg.hide()

    def setContent(self,text=None):
        self.hide()
        if text!=None :
            if type(text)==type([]):
                self.setPlainText('\n'.join(text))
            else :
                self.setPlainText(text)
        contentText=self.toPlainText()
        while len(contentText)>0 and contentText[-1]=='\n':
            contentText=contentText[:-1]
        contentText=self.fixCode(contentText)
        self.setPlainText(contentText)
        self.makeInnerLatexSvg()
        if text==None:
            text=self.bubble.tab.textEdit.toPlainText()
            i=text.find("#"+str(self.bubble.id)+':')
            if i>0:
                k=text.find('\n',i)
                if k==-1:
                    text=text+'\n'+self.toPlainText()
                else :
                    j=text.find('\n#',k+1)
                    if j==-1:
                        text=text[:k+1]+self.toPlainText()
                    else :
                        text=text[:k+1]+self.toPlainText()+'\n'+text[j:]
                self.bubble.tab.textEdit.setPlainText(text)

    def fixSvg(self,svgPath):
        f=open(svgPath,'r')
        svgCode=f.read()
        f.close()
        codeParts=svgCode.split('</defs>')
        codeParts[0]=codeParts[0].replace('</symbol>','').replace('>\n<path','').replace('<symbol','<path').replace('</g style','</g><path style')
        svgCode='</defs>'.join(codeParts)
        f=open(svgPath,'w')
        f.write(svgCode)
        f.close()


    def fixCode (self,code):
        money=code.count('$')
        if money>0 and money%2==1:
            lines=code.splitlines()
            for i in range(len(lines)):
                if lines[i].count('$')%2==1:
                    lines[i]+='$'
                    print("Latex : a '$' was missing.")
            code='\n'.join(lines)
        return code

    def mouseDoubleClickEvent(self, event):
        self.clearFocus()
        try:
            self.setContent()
            self.bubble.tab.save()
            self.bubble.optimizeEdges()
        except Exception as e:
            print(e)
        return super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setContent()
        return super().focusOutEvent(event)

    def makeIdCode (self,lines):
        def hashFunc (s):
            h=0
            k=0
            for i,c in enumerate(s) :
                h+=ord(c)
                k+=ord(c)*i
            k=k%10
            return h,k
        code=str(self.bubble.id)+'#'
        key=0
        if isinstance(lines,str):
            lines=[lines]
        for l in lines:
            h,k=hashFunc(l)
            code+=str(h)
            key+=k
        code+=str(key)
        return code