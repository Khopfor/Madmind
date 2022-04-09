import numpy as np
# PyQt imports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize
from PyQt5.QtGui import QPixmap,QPainter,QColor
# Local imports
from Scene import Scene


class Canvas(QGraphicsView):
    def __init__(self,tab):
        super().__init__(tab)
        self.scene=Scene(self)
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
        self.opacityEffet=QGraphicsOpacityEffect(self.minimap)
        self.opacityEffet.setOpacity(0.9)
        self.minimap.setGraphicsEffect(self.opacityEffet)
        # self.minimap.setWindowOpacity(0.5)
        self.hide()

    def initMindmap(self,tab,contents,progress=None):
        self.scene.initMindmap(tab,contents,progress)

    def mousePressEvent(self, event):
        if event.button()== Qt.MouseButton.RightButton :
            self.resetTransform()
            self.centerOn(0,0)
            self.scale(0.5,0.5)
        else :
            return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.minimap.update()
        return super().mouseReleaseEvent(event)


    def wheelEvent(self, event):
        if (QApplication.keyboardModifiers() == Qt.ControlModifier):
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