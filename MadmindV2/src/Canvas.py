from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize
from PyQt5.QtGui import QPixmap,QPainter,QColor
from PyQt5.QtSvg import *
import numpy as np
from Scene import Scene
import glob
import sys
import os


class Canvas(QGraphicsView):
    def __init__(self,tab):
        super().__init__(tab)
        self.scene=Scene()
        self.setScene(self.scene)
        self.setRenderHints(QPainter.Antialiasing)
        self.scale(0.5,0.5)
        self.centerOn(0,0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setGeometry(tab.geometry())
        self.minimap=QGraphicsView(self)
        self.minimap.setScene(self.scene)
        self.minimap.setGeometry(self.width()-202,2,200,200)
        self.minimap.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.minimap.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.minimap.scale(0.1,0.1)
        self.minimap.setWindowOpacity(0.5)
        self.show()
        # self.setBackgroundBrush(QColor(0,0,0))
        # self.label=QtWidgets.QLabel(self)
        # self.label.setText(tabName)
        # self.label.move(50,50)
        # self.pix=QPixmap(QSize(5000,5000))
        # self.pix.fill(Qt.white)
        # self.svg=QSvgWidget("mindmaps/"+tabName+"/"+"Integrability.svg")
        # self.vbox=QVBoxLayout()
        # self.vbox.addWidget(self.label)
        # self.vbox.addWidget(self.svg,Qt.AlignCenter,Qt.AlignCenter)
        # self.setLayout(self.vbox)
                # self.generator = QSvgGenerator()
        # self.generator.setFileName(tabName+".svg")
        # self.generator.setSize(QSize(400, 400))
        # self.generator.setViewBox(QRect(0, 0, 400, 400))
        # self.svgPainter=QPainter(self.generator)
        # self.pix=QPixmap(self.rect().size())
        # self.scrollArea.setLayout(QVBoxLayout)

    # def paintEvent(self, event):
    #     guiPainter=QPainter(self)
    #     guiPainter.drawPixmap(QPoint(),self.pix)
    #     self.painter=QPainter(self)
        # if not self.center.isNull():
            # print(self.center)
        #     self.guiPainter.drawEllipse(self.center,50,30)

    # def mousePressEvent(self, event):
    #     if event.buttons() and Qt.LeftButton:
    #         pass

    def initMindmap(self,tab):
        self.scene.initMindmap(tab)

    def mousePressEvent(self, event):
        if event.button()== Qt.MouseButton.RightButton :
            print("YAYYYY")
            self.resetTransform()
            self.centerOn(0,0)
            self.scale(0.5,0.5)
        else :
            return super().mousePressEvent(event)


    def wheelEvent(self, event):
        if (QApplication.keyboardModifiers() and Qt.ControlModifier):
            delta=event.angleDelta().y()
            zoom=1.015
            if delta>0:
                dx=np.sign(delta)*(event.pos().x()-self.width()/2)
                dy=np.sign(delta)*(event.pos().y()-self.height()/2)
                norm=np.sqrt(dx**2+dy**2)
                l=min(1,self.width()*(1-1/zoom)/2/norm**2,self.height()*(1-1/zoom)/2/norm**2)
                self.scale(zoom,zoom)
                self.centerOn(self.mapToScene(dx+self.width()/2,dy+self.height()/2))
            elif delta<0:
                self.scale(1/zoom,1/zoom)
        else :
            return super().wheelEvent(event)

    # def mouseMoveEvent(self, event):
    #     # print(event.pos())
    #     # print(self.mapFromScene(event.pos()))
    #     # print(self.viewport().width(),self.viewport().height())
    #     # print(self.width(),self.height())
    #     print()
    #     return super().mouseMoveEvent(event)

    # def mouseDoubleClickEvent(self,event):
        # if event.buttons() and Qt.LeftButton:
    #         x=event.scenePos().x()#*self.sceneRect().width()
    #         y=event.scenePos().y()#*self.sceneRect().height()
    #         self.bubbles.append(Bubble(x=x,y=y))
    #         self.scene.addItem(self.bubbles[-1])
    #         # self.svgPainter.drawEllipse(self.center,50,30)
    #         # guiPainter=QPainter(self.pix)
    #         # guiPainter.drawEllipse(self.center,50,30)
    #         self.update()

    # def mouseMoveEvent(self,event):
    #    if event.buttons() and Qt.LeftButton:
    #         print(event.pos())