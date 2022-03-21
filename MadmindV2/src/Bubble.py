from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint,QPointF, QRect,QSize,QSizeF
from PyQt5.QtGui import QPixmap,QPainter,QColor,QPen
from PyQt5.QtSvg import *
from utils import *
from Edge import Edge
import glob
import sys
import os

class Bubble(QGraphicsEllipseItem):
    ##########################################
    #### INIT ################################
    ##########################################
    def __init__ (self,desc='',id=0,x=0,y=0,a=80,b=40,latexMaker=None,tab=None,mindmap=None):
        super().__init__(-a,-b,2*a,2*b)
        self.id=id
        self.a=a
        self.b=b
        self.mindmap=mindmap
        self.tab=tab
        self.size=1
        self.drawn=False
        self.moving=False
        self.setPos(x,y)
        self.setZValue(2)
        self.setAcceptHoverEvents(True)

        # Edges
        self.toLinks=[]
        self.fromLinks=[]
        self.edges={}

        # Style
        self.strokeWidth=2
        self.color="#CCAACC"
        self.pen=QPen()
        self.lens=1.4
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        ### Construct from text description ###
        if desc != '':
            lines=self.constructFromDesc(desc)
        # Generates inner svg
        try:
            cachePath="mindmaps/"+self.tab.tabName+"/cache/"
            pdfPath=cachePath+"tempSnippet.pdf"
            svgPath=cachePath+"tempSnippet.svg"
            latexMaker.makePdf(lines,pdfPath,self.id==0)
            os.system('pdf2svg '+pdfPath+" "+svgPath)
            f=open(svgPath,'r')
            svgCode=f.read()
            f.close()
            svgCode=svgCode.replace('</symbol>','').replace('>\n<path','').replace('<symbol','<path').replace('</g style','</g><path style')
            f=open(svgPath,'w')
            f.write(svgCode)
            f.close()
            self.innerSvg=QGraphicsSvgItem(svgPath,parent=self)
        except :
            self.innerSvg=None
            # os.system('cp '+svgPath+" "+svgPath+str(self.id))
        if self.innerSvg:
            self.innerSvg.setScale(1)
            size=self.innerSvg.boundingRect().size()
            w=size.width()/2*self.innerSvg.scale()
            h=size.height()/2*self.innerSvg.scale()
            self.findEllipseSize(w,h)
            self.innerSvg.moveBy(-w,-h)
            self.setRect(-self.a,-self.b,2*self.a,2*self.b)


        # Id label
        self.idLabel=QGraphicsTextItem(str(self.id),self)
        self.idLabel.moveBy(-self.idLabel.boundingRect().width()/2*self.idLabel.scale(),-self.idLabel.boundingRect().height()*self.idLabel.scale()-self.b)
        self.idLabel.hide()

        self.pen.setWidthF(self.strokeWidth)
        if "#" in self.color:
            self.pen.setColor(QColor(*hex_to_rgb(self.color)))
        else :
            self.pen.setColor(QColor(self.color))
        self.setPen(self.pen)
        self.setBrush(QColor(240,240,240))

        # try:
        # snippet=latexMaker.makeLatexSvg(lines,self.id==0)
        # if snippet!=None:
            # latexMaker.saveSvgAsPng(snippet,"mindmaps/"+self.tab.tabName+"/cache/tempSnippet.png")
            # self.innerImg=QGraphicsPixmapItem(QPixmap("mindmaps/"+self.tab.tabName+"/cache/tempSnippet.png"))
            # self.innerImg.setPos(self.scenePos())
            # self.tab.canvas.scene.addItem(self.innerImg)
        # self.tab.canvas.scene.addItem(self.innerSvg)
        # except:
        #     pass


        self.check()


    ##############################################
    #### END INIT ################################
    ##############################################

    # def addEdge (self,alter):
    #     if alter.id not in self.edges:
    #         self.edges[alter.id]=Edge(self,alter)

    def addEdge(self,edge):
        if edge.id not in self.edges:
            self.edges[edge.id]=edge

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

    def findEllipseSize (self,w,h):
        if self.innerSvg :
            self.a=np.sqrt(w*(h+w))
            self.b=np.sqrt(h*(h+w))
        self.b=max(self.b,self.a/2.5)
        # self.a*=self.size
        # self.b*=self.size



    def move(self,dx,dy):
        x0=self.scenePos().x()
        y0=self.scenePos().y()
        self.setPos(QPoint(x0+dx,y0+dy))



    def magnify(self,bool):
        if bool:
            s=self.lens
        else :
            s=1
        self.setScale(s*self.size)
        # rect=self.rect()
        # rect.setSize(QSizeF(s*2*self.a,s*2*self.b))
        # self.setRect(rect)
        # self.move(sgn*(self.lens-1)*self.a,sgn*(self.lens-1)*self.b)



    def hoverEnterEvent(self, event):
        self.magnify(1)
        self.idLabel.show()



    def hoverLeaveEvent(self, event):
        self.magnify(0)
        self.idLabel.hide()



    def mousePressEvent(self, event):
        pass



    def mouseMoveEvent(self, event):
        orig=event.lastScenePos()
        updated=event.scenePos()
        dx=updated.x()-orig.x()
        dy=updated.y()-orig.y()
        self.move(dx,dy)
        self.magnify(0)
        self.updateEdges()



    def mouseReleaseEvent(self, event):
        self.writePos()
        self.optimizeEdges()
        self.moving=False



    def mouseDoubleClickEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.setBrush(Qt.yellow)



    def keyPressEvent(self, event):
        print("hello")
        if self.isUnderMouse() :
            if event.key()==Qt.Key.Key_Plus:
                self.size*=1.2
            if event.key()==Qt.Key.Key_Minus:
                self.size/=1.2
            self.setScale(self.size)
            if (event.key()==Qt.Key.Key_Control):
                print("yay")
                self.tab.canvas.centerOn(self.scenePos())
        return super().keyPressEvent(event)


    def writePos (self):
        if self.tab:
            lines=self.tab.textEdit.toPlainText().split('\n')
            for i,l in enumerate(lines):
                if "#"+str(self.id)+':' in l:
                    index=i
                    break
            l=lines[index].split(';')
            newX,newY=False,False
            for i,s in enumerate(l):
                if "x" in s and "=" in s :
                    l[i]="x="+str(self.scenePos().x())
                    newX=True
                if "y" in s and "=" in s :
                    l[i]="y="+str(self.scenePos().y())
                    newY=True
            if not newX : l.append("x="+str(self.scenePos().x()))
            if not newY : l.append("y="+str(self.scenePos().y()))
            lines[index]=';'.join(l)
            contents='\n'.join(lines)
            self.tab.textEdit.setPlainText(contents)



    def check(self):
        if self.scenePos().x() <self.a:
            self.setPos(self.a,self.y())
        if self.scenePos().y() <self.b:
            self.setPos(self.x(),self.b)
        

    def potential(self,x,y,tl=0,A=10000,range=1.4):
        d=np.sqrt(((x-self.scenePos().x())/100)**2+((y-self.scenePos().y())/100)**2)
        z=d/(range+0.5*tl/100)
        return (-z**2+A)*np.exp(-z**4)





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
                self.strokeWidth*=self.size
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