# PyQt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Help (QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.w=270
        # self.setGeometry(self.parent().width()-self.w-2,self.parent().height()-400-2,self.w,self.parent().height()-202-202)
        # self.setWidgetResizable(True)
        self.setStyleSheet("""
            QWidget{
                background-color:#DDDDDD;
                border-width:0px;
                border-radius:4px;
                border-style:solid;
                border-color:grey;
                padding:3px;
            }
            QVBoxLayout{
                margin:4px;
            }
        """)
        self.opacityEffet=QGraphicsOpacityEffect(self)
        self.opacityEffet.setOpacity(0.7)
        self.setGraphicsEffect(self.opacityEffet)
        self.hide()
        self.hidden=True
        helpFile=open("templates/help.txt",'r')
        helpText=helpFile.read()
        helpFile.close()
        self.label=QLabel(helpText,parent)
        self.label.setFont(QFont("monospace",10))
        # self.label.setWordWrap(True)
        vbox=QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.setAlignment(self.label,Qt.AlignTop)
        self.setLayout(vbox)

    def hide(self):
        self.hidden=True
        return super().hide()

    def show(self):
        self.hidden=False
        return super().show()

    def toggle(self):
        if self.hidden :
            self.show()
            self.updateGeom()
        else :
            self.hide()

    def updateGeom(self):
        textEditHeight=self.parent().textEdit.height()
        height=self.parent().height()-8-textEditHeight-200
        spacing=3
        if height<100:
            self.hide()
        else :
            self.setGeometry(self.parent().width()-self.w-spacing,200+spacing,self.w,height)