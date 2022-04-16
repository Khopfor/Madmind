# PyQt imports
from math import sin
from time import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize,QTimer
from PyQt5.QtGui import QPixmap,QPainter,QColor
# Local imports
from Mindmap import Mindmap
from LatexMaker import LatexMaker
from utils import hex_to_rgb

POTPARAMS="settings/potParams.json"
VIDEOPARAMS="settings/videoParams.json"
LATEXCOMMANDS="settings/latexCommands.json"

class Scene (QGraphicsScene):
    def __init__(self,parent):
        super().__init__(parent)
        self.boundaries=QGraphicsRectItem(0,0,2000,2000)
        pen=self.boundaries.pen()
        pen.setColor(QColor(180,180,180))
        self.boundaries.setPen(pen)
        self.setSceneRect(self.boundaries.rect())
        self.addItem(self.boundaries)
        self.setBackgroundBrush(QColor(250,242,232))
        # self.setBackgroundBrush(QColor(247,247,247))
        self.hoveredObject=None
        self.dynamicBgTimer=QTimer()
        self.dynamicBgTimer.timeout.connect(self.dynamicBg)
        self.trend=1


    def initMindmap(self,tab,contents,progress=None):
        latexMaker=LatexMaker(LATEXCOMMANDS)
        mmName=tab.tabName
        self.mindmap=Mindmap(mmName,contents,latexMaker=latexMaker,tab=tab,progress=progress)
        self.updateBgColor()
        self.updateSceneRect()
        self.mindmap.draw(self)
        self.dynamicBgTimer.start(200)


    def updateBgColor(self):
        if self.mindmap.bgColor :
            if "#" in self.mindmap.bgColor:
                self.setBackgroundBrush(QColor(*hex_to_rgb(self.mindmap.bgColor)))
            elif isinstance(self.mindmap.bgColor,tuple) and len(self.mindmap.bgColor)==3:
                self.setBackgroundBrush(QColor(*self.mindmap.bgColor))
            self.mindmap.updateEdgeColor()


    def updateSceneRect(self):
        self.boundaries.setRect(0,0,self.mindmap.width,self.mindmap.height)
        self.setSceneRect(self.boundaries.rect())


    def mouseMoveEvent(self, event):
        self.mousePos=event.scenePos()
        return super().mouseMoveEvent(event)

    def dynamicBg(self):
        color=self.backgroundBrush().color()
        hsl=color.getHslF()
        l=hsl[2]
        mml=QColor(*hex_to_rgb(self.mindmap.bgColor)).lightnessF()
        # if l>min(1,mml+0.02):
        #     self.trend=-1
        # elif l<=max(0,mml-0.02):
        #     self.trend=1
        # l+=self.trend/400
        l=0.025*sin(2*3.141592*time()/10)+mml+0.025*(1-2*(mml>0.5))
        color.setHslF(hsl[0],hsl[1],l,hsl[3])
        self.setBackgroundBrush(color)


    def keyPressEvent(self, event):
        if event.key()== Qt.Key.Key_N:
            x=self.mousePos.x()#*self.sceneRect().width()
            y=self.mousePos.y()#*self.sceneRect().height()
            self.mindmap.newBubble(x,y,self)
            self.update()
        # elif event.key()== Qt.Key.Key_S and QApplication.keyboardModifiers()==Qt.KeyboardModifier.ControlModifier:
        #     self.parent().parent().save
        elif event.key()== Qt.Key.Key_S and not QApplication.keyboardModifiers():
            for bub in self.mindmap.bubbles.values():
                bub.toggleShadow()
        elif event.key()==Qt.Key.Key_Delete :
            self.mindmap.deleteSelection()
        elif event.key()==Qt.Key.Key_Escape:
            self.mindmap.deselectAll()
        elif self.hoveredObject :
            if event.key()==Qt.Key.Key_Plus:
                self.hoveredObject.grow()
            elif event.key()==Qt.Key.Key_Minus:
                self.hoveredObject.shrink()
            elif event.key()==Qt.Key.Key_L:
                self.hoveredObject.magnify(1)
                self.hoveredObject.lensed=True
                for bub in self.mindmap.bubbles.values():
                    if bub!=self.hoveredObject:
                        bub.toggleBlur(1)
        return super().keyPressEvent(event)