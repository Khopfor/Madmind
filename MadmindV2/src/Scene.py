# PyQt imports
from math import ceil, sin
from time import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize,QTimer
from PyQt5.QtGui import QPixmap,QPainter,QColor,QFont,QKeyEvent
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
        self.bg=QGraphicsRectItem(0,0,2000,2000)
        self.bg.setBrush(QColor(250,242,232))
        bgShadow=QGraphicsDropShadowEffect(self)
        bgShadow.setBlurRadius(50)
        bgShadow.setOffset(0,0)
        self.bg.setGraphicsEffect(bgShadow)
        # pen=self.bg.pen()
        # pen.setColor()
        # self.bg.setPen(pen)
        self.setSceneRect(self.bg.rect())
        # self.addItem(self.bg)
        # self.setBackgroundBrush(QColor(120,120,120))
        self.setBackgroundBrush(QColor(250,242,232))
        self.hoveredObject=None
        # self.dynamicBgTimer=QTimer()
        # self.dynamicBgTimer.timeout.connect(self.dynamicBg)
        self.trend=1


    def initMindmap(self,tab,dirPath,progress=None):
        latexMaker=LatexMaker(LATEXCOMMANDS)
        mmName=tab.tabName
        self.mindmap=Mindmap(mmName,dirPath=dirPath,latexMaker=latexMaker,tab=tab,progress=progress)
        self.updateSceneRect()
        m=min(self.mindmap.width,self.mindmap.height)
        self.parent().scale(2000/m,2000/m)
        self.mindmap.draw(self)
        titleWords=self.mindmap.title.split(' ')
        if len(titleWords)>=3:
            titleWords[ceil(len(titleWords)/2)]='\n'+titleWords[ceil(len(titleWords)/2)]
        self.mmTitle=QGraphicsTextItem()
        self.mmTitle.setPlainText(self.mindmap.title)
        self.mmTitle.setTextWidth(self.mindmap.width/10)
        print(self.mmTitle.toPlainText())
        font=QFont("serif")
        font.setBold(True)
        self.mmTitle.setFont(font)
        self.mmTitle.setDefaultTextColor(self.bg.brush().color().lighter(102))
        self.mmTitle.setScale(10)
        # self.addItem(self.mmTitle)
        # self.dynamicBgTimer.start(200)


    def updateBgColor(self):
        if self.mindmap.bgColor :
            if "#" in self.mindmap.bgColor:
                color=QColor(*hex_to_rgb(self.mindmap.bgColor))
            elif isinstance(self.mindmap.bgColor,tuple) and len(self.mindmap.bgColor)==3:
                color=QColor(*self.mindmap.bgColor)
            # self.bg.setBrush(color)
            self.setBackgroundBrush(color)
            self.mmTitle.setDefaultTextColor(color.lighter(102))
            self.mindmap.updateEdgeColor()


    def updateSceneRect(self):
        self.setSceneRect(0,0,self.mindmap.width,self.mindmap.height)
        # self.bg.setRect(0,0,self.mindmap.width,self.mindmap.height)
        # self.setSceneRect(self.bg.rect())


    def mouseMoveEvent(self, event):
        self.mousePos=event.scenePos()
        return super().mouseMoveEvent(event)

    def dynamicBg(self):
        color=self.bg.brush().color()
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
        self.bg.setBrush(color)
        self.mmTitle.setDefaultTextColor(color.lighter(102))


    def keyPressEvent(self, event):
        propagate=True
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
        elif event.key()== Qt.Key.Key_A and QApplication.keyboardModifiers()==Qt.KeyboardModifier.ControlModifier:
            self.mindmap.selectAll()
        # elif event.key()== Qt.Key.Key_F and QApplication.keyboardModifiers()==Qt.KeyboardModifier.ControlModifier:
        #     self.mindmap.search()
        elif event.key()==Qt.Key.Key_C:
            if len(self.mindmap.selected.values())>0:
                self.mindmap.colorize(QColorDialog(QColor(list(self.mindmap.selected.values())[-1].color)).getColor())
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
        elif event.key()==Qt.Key.Key_Down and QApplication.keyboardModifiers()==Qt.KeyboardModifier.ControlModifier:
            self.mindmap.changeLevelSelected(1)
            propagate=False
        elif event.key()==Qt.Key.Key_Up and QApplication.keyboardModifiers()==Qt.KeyboardModifier.ControlModifier:
            self.mindmap.changeLevelSelected(-1)
            propagate=False
        elif event.key()==Qt.Key.Key_Plus:
            self.mindmap.growSelected()
        elif event.key()==Qt.Key.Key_Minus:
            self.mindmap.shrinkSelected()
        if propagate :
            return super().keyPressEvent(event)