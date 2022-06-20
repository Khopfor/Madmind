import sys
# PyQt imports
from PyQt5.QtWidgets import QApplication,QMainWindow, QDialog, QAction, QTabWidget, QWidget,QVBoxLayout,QStyle
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QIcon
# Local imports
from Tab import Tab

VERSION=2.0

class MainWindow(QDialog):
    resized = pyqtSignal()
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setGeometry(150,100,500,600)
        self.setWindowTitle("Madmind")
        self.setWindowIcon(QIcon("icons/AppIcon.svg"))
        self.setWindowIconText("Madmind")
        self.setWindowFlags(Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        self.initUI()
        # self.setAutoFillBackground(True)
        self.resized.connect(self.resizeTabs)

    def initUI(self):
        # self.label=QtWidgets.QLabel(self)
        # self.label.setText("YAYYYY")
        # self.label.move(50,50)

        vbox=QVBoxLayout()
        # print(vbox.getContentsMargins())  
        self.tabNb=0
        self.tabs={}
        self.tabWidget=QTabWidget(self)
        # self.adjustSize()
        self.tabWidget.setGeometry(0,0,self.width(),self.height())
        # self.tabWidget.setStyleSheet("border-color: rgb(52, 101, 164);\nbackground-color: rgb(92, 53, 102);\ncolor: rgb(115, 210, 22);")
        # self.tabWidget.setDocumentMode(True)
        # self.tabWidget.setAutoFillBackground(True)
        # self.tabWidget.setGeometry(-50,-50,1200,900)
        # self.tabWidget.setContentsMargins(0,0,0,0)
        # self.update()
        # mindmaps=os.listdir("mindmaps")
        # for tabName in mindmaps :
        #     if tabName in ["integrability"]:
        # self.tabWidget.addTab(Tab("",self),"")
        self.createNewTab()
        # vbox.addWidget(self.tabWidget)
        # self.setLayout(vbox)

    def createNewTab(self):
        newTab=Tab(self.tabNb,self.tabWidget)
        self.tabs[self.tabNb]=newTab
        self.tabWidget.addTab(newTab,"New Tab")
        self.tabNb+=1
        self.resizeTabs()
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(newTab))

    def resizeTabs(self):
        self.tabWidget.setGeometry(0,0,self.width(),self.height())
        self.tabWidget.updateGeometry()
        for tab in self.tabs.values():
            tab.resizeElements(self.width(),self.height())

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MainWindow, self).resizeEvent(event)

    def keyPressEvent(self, event):
        if (event.key()==Qt.Key_T) and (QApplication.keyboardModifiers()== Qt.ControlModifier):
            self.createNewTab()
        # return super().keyPressEvent(event)


def window():
    app=QApplication(sys.argv)
    win=MainWindow()
    win.show()
    app.exec_()

window()
