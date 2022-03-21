from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow, QDialog, QAction, QTabWidget, QWidget,QVBoxLayout,QStyle
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap,QPainter
from Tab import Tab
import glob
import sys
import os

VERSION=2.0

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()
        self.setGeometry(200,200,1200,900)
        self.setWindowTitle("Madmind")
        self.setWindowFlags(Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        # self.setAutoFillBackground(True)

    def initUI(self):
        # self.label=QtWidgets.QLabel(self)
        # self.label.setText("YAYYYY")
        # self.label.move(50,50)

        vbox=QVBoxLayout()
        # print(vbox.getContentsMargins())
        self.tabs=QTabWidget(self)
        # self.tabs.setStyleSheet("border-color: rgb(52, 101, 164);\nbackground-color: rgb(92, 53, 102);\ncolor: rgb(115, 210, 22);")
        # self.tabs.setDocumentMode(True)
        # self.tabs.setAutoFillBackground(True)
        # self.tabs.setGeometry(-50,-50,1200,900)
        # self.tabs.setContentsMargins(0,0,0,0)
        # self.update()
        mindmaps=os.listdir("mindmaps")
        for tabName in mindmaps :
            if tabName in ["string"]:
                self.tabs.addTab(Tab(tabName,self),tabName)
        vbox.addWidget(self.tabs)
        self.setLayout(vbox)


def window():
    app=QApplication(sys.argv)
    win=MainWindow()
    win.show()
    sys.exit(app.exec_())

window()
