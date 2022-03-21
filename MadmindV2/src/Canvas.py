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
        super().__init__()
        self.scene=Scene()
        self.setScene(self.scene)
        self.setRenderHints(QPainter.Antialiasing)
        self.scale(0.5,0.5)
        self.centerOn(0,0)
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
            x=event.angleDelta().y()
            # print(event.x(),event.y())
            # p=2
            # zoom=(p-(p-1)*np.exp(-(x/100)**2))
            # print(zoom)
            zoom=1.015
            dx=event.pos().x()-self.width()/2
            dy=event.pos().y()-self.height()/2
            # print(self.mapFromScene(event.pos()))
            norm=np.sqrt(dx**2+dy**2)
            l=min(1,self.width()*(1-1/zoom)/2/norm,self.height()*(1-1/zoom)/2/norm)
            # self.centerOn(l*dx+self.width()/2,l*dy+self.height()/2)
            self.centerOn(self.mapToScene(dx+self.width()/2,dy+self.height()/2))
            # print(dx,dy)
            # print(l)
            if x>0:
                self.scale(zoom,zoom)
            elif x<0:
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