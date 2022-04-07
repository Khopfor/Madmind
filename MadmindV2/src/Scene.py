# PyQt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize
from PyQt5.QtGui import QPixmap,QPainter,QColor
# Local imports
from Mindmap import Mindmap
from LatexMaker import LatexMaker

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


    def initMindmap(self,tab,contents,progress=None):
        latexMaker=LatexMaker(LATEXCOMMANDS)
        mmName=tab.tabName
        self.mindmap=Mindmap(mmName,contents,latexMaker=latexMaker,tab=tab,progress=progress)
        self.mindmap.draw(self)


    def mouseMoveEvent(self, event):
        self.mousePos=event.scenePos()
        return super().mouseMoveEvent(event)


    def keyPressEvent(self, event):
        if event.key()== Qt.Key.Key_N:
            x=self.mousePos.x()#*self.sceneRect().width()
            y=self.mousePos.y()#*self.sceneRect().height()
            self.mindmap.newBubble(x,y,self)
            self.update()
        elif event.key()== Qt.Key.Key_S:
            for bub in self.mindmap.bubbles.values():
                bub.toggleShadow()
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