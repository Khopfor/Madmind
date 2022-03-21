from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect,QSize
from PyQt5.QtGui import QPixmap,QPainter
from PyQt5.QtSvg import *
import glob
import sys
import os

from Canvas import Canvas

class Tab (QWidget):
    def __init__(self,tabName,parent):
        super().__init__(parent)
        self.tabName=tabName
        # # Scroll Area
        # self.scrollArea=QScrollArea()
        # self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.scrollArea.setWidget(canvas)
        # self.scrollArea.setWidgetResizable(True)

        # Contents file
        f=open("mindmaps/"+tabName+"/"+tabName+".txt",'r')
        contents=f.read()
        f.close()

        # Canvas
        self.canvas=Canvas(self)
        self.canvas.initMindmap(self)

        # Text Editor
        self.textEdit=QTextEdit(self.canvas)
        self.textEdit.setPlainText(contents)
        x,y,w,h=self.canvas.geometry().getCoords()
        self.textEdit.setGeometry(self.parent().width(),self.parent().height(),400,300)

        # Layout
        self.vLayout=QVBoxLayout(self)
        self.vLayout.addWidget(self.canvas,5)
        # self.vLayout.addWidget(self.textEdit,1)
        self.setLayout(self.vLayout)

    def keyPressEvent(self, e):
        if (e.key()==Qt.Key_S) and (QApplication.keyboardModifiers() and Qt.ControlModifier):
            f=open("mindmaps/"+self.tabName+"/"+self.tabName+".txt",'w')
            f.write(self.textEdit.toPlainText())
            f.close()
        return super().keyPressEvent(e)