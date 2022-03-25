from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint,QPointF, QRect,QSize,QSizeF,QRectF
from PyQt5.QtGui import QPixmap,QPainter,QColor,QPen,QIntValidator,QPalette
from PyQt5.QtSvg import *
from utils import *
from Edge import Edge
from BubbleContent import BubbleContent
import glob
import sys
import os

class Bubble(QGraphicsEllipseItem):
    ##########################################
    #### INIT ################################
    ##########################################
    def __init__(self,desc='',id=99999999,x=None,y=None,latexMaker=None,tab=None,mindmap=None,color=None):
        a,b=80,50
        super().__init__(-a,-b,2*a,2*b)
        self.a,self.b=a,b
        self.mindmap=mindmap
        self.tab=tab
        self.size=1
        self.drawn=False
        self.moving=False
        self.lensed=False
        self.idLabel=None
        self.setZValue(4)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # Content
        self.content=BubbleContent(self,latexMaker=latexMaker)

        # Edges
        self.toLinks=[]
        self.fromLinks=[]
        self.edges={}

        # Style
        self.strokeWidth=2
        if color==None:
            self.color="#33BBEE"
        else :
            self.color=color
        self.lens=1.4
        self.shadow=QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0,3)
        self.shadow.setColor(QColor(70,70,70))
        # self.setGraphicsEffect(self.shadow)

        if desc!='':
            self.descInit(desc)
        elif x!=None and y!=None :
            self.posInit(x,y,id)

        self.setStyle()
        self.check()


    def posInit (self,x,y,id):
        self.setPos(x,y)
        self.id=id
        self.initIdLabel()
        # self.idEdit=QLineEdit(self.tab.canvas)
        # self.idEdit.setValidator(QIntValidator())
        # self.idEdit.setMaxLength(8)
        # # self.idEdit.setFont(QFont())
        # self.id=None
        # self.idEdit.show()
        # self.idEdit.editingFinished.connect(self.setId)
        # self.id=int()

    def descInit (self,desc):
        lines=self.constructFromDesc(desc)
        self.content.setContent(lines)
        self.setEllipseSize()
        self.initIdLabel()
    

    def initIdLabel(self):
        self.idLabel=QGraphicsTextItem(str(self.id),self)
        self.setIdLabelPos()
        self.idLabel.hide()


    def setIdLabelPos(self):
        if self.idLabel:
            self.idLabel.setPos(-self.idLabel.boundingRect().width()/2*self.idLabel.scale(),-self.idLabel.boundingRect().height()*self.idLabel.scale()-self.b)


    # def setId(self):
    #     newId=int(self.idEdit.text())
    #     if newId != self.id :
    #         self.id=newId
    #         self.idEdit.hide()
    #         self.initIdLabel()
    #         self.mindmap.addBubble(self)
    ##############################################
    #### END INIT ################################
    ##############################################

    def setStyle(self):
        pen=self.pen()
        pen.setWidthF(self.strokeWidth)
        if "#" in self.color:
            pen.setColor(QColor(*hex_to_rgb(self.color)))
        else :
            pen.setColor(QColor(self.color))
        self.setPen(pen)
        self.setBrush(QColor(250,250,250))

    # def addEdge (self,alter):
    #     if alter.id not in self.edges:
    #         self.edges[alter.id]=Edge(self,alter)

    def addEdge(self,edge):
        if edge.id not in self.edges:
            self.edges[edge.id]=edge
            return True
        return False

    def constructEdges(self,bubbles):
        for toid in self.toLinks :
            if toid in bubbles:
                newEdge=Edge(self,bubbles[toid],bubbles=bubbles)
                self.addEdge(newEdge)
                bubbles[toid].addEdge(newEdge)
        for frid in self.fromLinks :
            if frid in bubbles:
                newEdge=Edge(bubbles[frid],self,bubbles=bubbles)
                self.addEdge(newEdge)
                bubbles[frid].addEdge(newEdge)
        # print(self.edges)

    def drawEdges(self,scene):
        for e in self.edges.values():
            if e.fr.id==self.id:
                scene.addItem(e)


    def updateEdges(self):
        for e in self.edges.values():
            e.updatePath()

    def optimizeEdges(self):
        for e in self.edges.values():
            e.optimizePath(self.mindmap.bubbles)

    def setEllipseSize (self,w=None,h=None):
        if self.content.innerSvg and w!=None and h!=None:
            self.a=max(np.sqrt(w*(h+w)),5)
            self.b=max(np.sqrt(h*(h+w)),5)
        # self.b=max(self.b,self.a/2.5)
        self.setRect(-self.a,-self.b,2*self.a,2*self.b)
        self.setIdLabelPos()
        # self.a*=self.size
        # self.b*=self.size



    def move(self,dx,dy):
        x0=self.scenePos().x()
        y0=self.scenePos().y()
        self.setPos(QPoint(x0+dx,y0+dy))

    def shrink(self):
        self.size/=1.2
        self.setScale(self.size)
        self.tab.writeNewSize(self)

    def grow(self):
        self.size*=1.2
        self.setScale(self.size)
        self.tab.writeNewSize(self)

    def magnify(self,bool):
        if bool:
            s=self.scale()*self.lens
        else :
            s=self.size
        self.setScale(s)

    def getA(self):
        return (self.a+self.strokeWidth/2)*self.size

    def getB(self):
        return (self.b+self.strokeWidth/2)*self.size


    ### Hover ###
    def hoverEnterEvent(self, event):
        self.magnify(1)
        if self.idLabel :
            self.idLabel.show()
        self.tab.canvas.scene.hoveredObject=self
        
    def hoverLeaveEvent(self, event):
        self.magnify(0)
        if self.idLabel :
            self.idLabel.hide()
        self.tab.canvas.scene.hoveredObject=None
        if self.lensed :
            for bub in self.mindmap.bubbles.values():
                bub.toggleBlur(0)
            self.lensed=False


    ### Mouse ###
    def mousePressEvent(self, event):
        # self.tab.goTo(self.id)
        if (QApplication.keyboardModifiers() and Qt.ShiftModifier):
            # self.setBrush(Qt.red)
            self.mindmap.newEdge(self)


    def mouseMoveEvent(self, event):
        # orig=event.lastScenePos()
        # updated=event.scenePos()
        # dx=updated.x()-orig.x()
        # dy=updated.y()-orig.y()
        # self.move(dx,dy)
        self.setPos(event.scenePos())
        self.magnify(0)
        self.updateEdges()

    def mouseReleaseEvent(self, event):
        self.writePos()
        self.optimizeEdges()
        self.moving=False

    def mouseDoubleClickEvent(self,event):
        if event.button() == Qt.LeftButton:
            # self.setBrush(Qt.yellow)
            self.content.showTextEdit()


    def check(self):
        if self.scenePos().x() <self.a:
            self.setPos(self.a,self.y())
        if self.scenePos().y() <self.b:
            self.setPos(self.x(),self.b)
        

    def potential(self,x,y,tl=0,A=10000,range=1.4):
        d=np.sqrt(((x-self.scenePos().x())/100)**2+((y-self.scenePos().y())/100)**2)
        z=d/(range+0.5*tl/100)
        return (-z**2+A)*np.exp(-z**4)

    def shine(self,bool=True):
        if bool :
            shine=QGraphicsDropShadowEffect()
            shine.setBlurRadius(50)
            shine.setOffset(0,0)
            shine.setColor(self.pen().color())
            self.setGraphicsEffect(shine)
        else:
            self.setGraphicsEffect(None)

    def toggleShadow(self):
        if self.graphicsEffect()==None:
            self.setGraphicsEffect(self.shadow)
        else :
            self.setGraphicsEffect(None)

    def toggleBlur(self,bool):
        if bool :
            blur=QGraphicsBlurEffect()
            self.setGraphicsEffect(blur)
            self.setZValue(3)
            for e in self.edges.values():
                e.toggleBlur(1)
        else :
            self.setGraphicsEffect(None)
            self.setZValue(4)
            for e in self.edges.values():
                e.toggleBlur(0)
        # if isinstance(self.graphicsEffect(),QGraphicsBlurEffect):
        #     self.setGraphicsEffect(None)
        # else :
        #     blur=QGraphicsBlurEffect()
        #     self.setGraphicsEffect(blur)









    def constructFromDesc (self,desc):
        desc=desc.splitlines()

        ### First line ###
        fl=desc[0].split(':',maxsplit=1)
        if fl[0][0]!= '#' : raise ("Error in contents file : '#' missing.")
        self.id=int(fl[0][1:]) # ID
        args=fl[1].split(';')
        for a in args :
            if contains(a,"to","t"):
                for k in a.split(':',1)[1].split(','):
                    self.toLinks.append(int(k))
            elif contains(a,"from","fr","f"):
                self.fromLinks=[int(k) for k in a.split(':')[1].split(',')]
            elif contains(a,"size","s"):
                if ':' in a : self.size=float(a.split(':')[1])
                elif '=' in a : self.size=float(a.split('=')[1])
                self.setScale(self.size)
            elif contains(a,"color","col","c"):
                if ':' in a : self.color=a.split(':')[1]
                elif '=' in a : self.color=a.split('=')[1]
                if self.color.isdigit() and '#' not in self.color:
                    self.color='#'+self.color
            elif contains(a,"x"):
                if '=' in a :
                    x=float(a.split('=')[1])
                    self.setPos(QPointF(x,self.y()))
                # if '>' in a : self.constraints.append({"type":"ineq","fun":lambda X:X[2*self.id]-float(a.split('>')[1])})
                # if '=' in a : self.constraints.append({"type":"eq","fun":lambda X:X[2*self.id]-float(a.split('=')[1])})
            elif contains(a,"y"):
                    y=float(a.split('=')[1])
                    self.setPos(QPointF(self.x(),y))
                # if '>' in a : self.constraints.append({"type":"ineq","fun":lambda X:X[2*self.id+1]-float(a.split('>')[1])})
                # if '=' in a : self.constraints.append({"type":"eq","fun":lambda X:X[2*self.id+1]-float(a.split('=')[1])})
            # else :
            #     print("Invalid entry :",a)

        ### Text lines ###
        lines=desc[1:]
        return lines

    def writePos (self):
        if self.tab and self.id:
            xStr=str(round(self.scenePos().x(),1))
            yStr=str(round(self.scenePos().y(),1))
            lines=self.tab.textEdit.toPlainText().split('\n')
            index=None
            for i,l in enumerate(lines):
                if "#"+str(self.id)+':' in l:
                    index=i
                    break
            if index!=None :
                [idPart,par]=lines[index].split(':',1)
                par=par.split(';')
                newX,newY=False,False
                for i,s in enumerate(par):
                    if "x" in s and "=" in s :
                        par[i]="x="+xStr
                        newX=True
                    if "y" in s and "=" in s :
                        par[i]="y="+yStr
                        newY=True
                if not newX : par.append("x="+xStr)
                if not newY : par.append("y="+yStr)
                lines[index]=idPart+':'+';'.join(par)
                contents='\n'.join(lines)
                self.tab.textEdit.setPlainText(contents)