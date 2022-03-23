from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize
from PyQt5.QtGui import QPixmap,QPainter,QColor
from PyQt5.QtSvg import *
from Mindmap import Mindmap
from LatexMaker import LatexMaker
import glob
import sys
import os

POTPARAMS="settings/potParams.json"
VIDEOPARAMS="settings/videoParams.json"
LATEXCOMMANDS="settings/latexCommands.json"

class Scene (QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.w=2000
        self.h=2000
        self.setSceneRect(0,0,self.w,self.h)
        self.setBackgroundBrush(QColor(250,242,232))
        self.hoveredObject=None


    def initMindmap(self,tab):
        latexMaker=LatexMaker(LATEXCOMMANDS)
        mmName=tab.tabName
        f=open("mindmaps/"+mmName+"/"+mmName+".txt",'r')
        contents=f.read()
        f.close()
        self.mindmap=Mindmap(mmName,contents,latexMaker=latexMaker,tab=tab)
        self.mindmap.draw(self)


    def mouseMoveEvent(self, event):
        self.mousePos=event.scenePos()
        return super().mouseMoveEvent(event)


    def keyPressEvent(self, event):
        if event.key()== Qt.Key.Key_N:
            x=self.mousePos.x()#*self.sceneRect().width()
            y=self.mousePos.y()#*self.sceneRect().height()
            self.mindmap.newBubble(x,y,self)
            # self.mindmap.drawBubble(self)
            # self.svgPainter.drawEllipse(self.center,50,30)
            # guiPainter=QPainter(self.pix)
            # guiPainter.drawEllipse(self.center,50,30)
            self.update()
        if self.hoveredObject :
            if event.key()==Qt.Key.Key_Plus:
                self.hoveredObject.grow()
            elif event.key()==Qt.Key.Key_Minus:
                self.hoveredObject.shrink()
        return super().keyPressEvent(event)

    # def mouseDoubleClickEvent(self,event):
    #     if event.button() == Qt.LeftButton:
    #         x=event.scenePos().x()#*self.sceneRect().width()
    #         y=event.scenePos().y()#*self.sceneRect().height()
    #         self.mindmap.newBubble(x,y)
    #         self.mindmap.drawBubble(self)
    #         # self.svgPainter.drawEllipse(self.center,50,30)
    #         # guiPainter=QPainter(self.pix)
    #         # guiPainter.drawEllipse(self.center,50,30)
    #         self.update()