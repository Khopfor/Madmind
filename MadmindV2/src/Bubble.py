# PyQt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint,QPointF, QRect,QSize,QSizeF,QRectF
from PyQt5.QtGui import QPixmap,QPainter,QColor,QPen,QIntValidator,QPalette,QFont
from PyQt5.QtSvg import *
# Local imports
from utils import *
from Edge import Edge
from BubbleContent import BubbleContent

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
        self.level=1
        self.levels=[Qt.PenStyle.SolidLine,Qt.PenStyle.SolidLine,Qt.PenStyle.DashLine,Qt.PenStyle.DotLine,Qt.PenStyle.NoPen]
        self.drawn=False
        self.moving=False
        self.lensed=False
        self.idLabel=None
        self.lastPos=self.scenePos()
        self.setZValue(5)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # Content
        self.innerSvg=None
        if self.tab :
            self.content=BubbleContent(self,latexMaker=latexMaker)
        else :
            self.latexMaker=latexMaker

        # Edges
        self.toLinks=[]
        self.fromLinks=[]
        self.edges={}

        # Style
        self.strokeWidth=2
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
        if self.tab:
            self.content.setContent(lines)
            self.setEllipseSize()
            self.initIdLabel()
        else :
            self.content=lines
    

    def initIdLabel(self):
        self.idLabel=QGraphicsTextItem(str(self.id),self)
        self.idLabel.setFont(QFont("monospace",6,5,1))
        self.setIdLabelPos()
        self.idLabel.hide()


    def setIdLabelPos(self):
        if self.idLabel:
            self.idLabel.setPos(-self.idLabel.boundingRect().width()/2,-self.idLabel.boundingRect().height()*4/5-self.b)


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
        if self.color==None:
            color=self.mindmap.bubbleColor
        else :
            color=self.color
        if "#" in color:
            pen.setColor(QColor(*hex_to_rgb(color)))
        else :
            pen.setColor(QColor(color))
        self.setPen(pen)
        self.changeLevel(0)
        if self.idLabel:
            self.idLabel.setDefaultTextColor(self.pen().color())

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
            if '(' in toid :
                [toid,w]=[int(v) for v in toid[:-1].split('(')]
                w/=10
            else :
                toid=int(toid)
                w=None
            if toid in bubbles:
                newEdge=Edge(self,bubbles[toid],mindmap=self.mindmap,width=w)
                self.addEdge(newEdge)
                bubbles[toid].addEdge(newEdge)
        for frid in self.fromLinks :
            if '(' in frid :
                [frid,w]=[int(v) for v in frid[:-1].split('(')]
                w/=10
            else :
                frid=int(frid)
                w=None
            if frid in bubbles:
                newEdge=Edge(bubbles[frid],self,mindmap=self.mindmap,width=w)
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
            e.optimizePath()

    def setEllipseSize (self,w=None,h=None):
        if self.content.innerSvg and w!=None and h!=None:
            self.a=max(np.sqrt(w*(h+w)),20/self.size)
            self.b=max(np.sqrt(h*(h+w)),20/self.size)
        # self.b=max(self.b,self.a/2.5)
        self.setRect(-self.a,-self.b,2*self.a,2*self.b)
        self.setIdLabelPos()
        # self.a*=self.size
        # self.b*=self.size

    def shrink(self):
        self.size/=1.2
        self.setScale(self.size)
        # self.tab.writeNewSize(self)
        self.updateEdges()
        self.updateStr()

    def grow(self):
        self.size*=1.2
        self.setScale(self.size)
        # self.tab.writeNewSize(self)
        self.updateEdges()
        self.updateStr()

    def changeLevel(self,incr):
        self.level=max(0,min(self.level+incr,4))
        pen=self.pen()
        pen.setStyle(self.levels[self.level])
        self.setPen(pen)
        if self.level==0:
            color=pen.color()
            color.setHsl(color.hslHue(),color.hslSaturation(),242)
            self.setBrush(color)
            self.setZValue(6)
        elif self.level==4:
            self.setBrush(QColor(*hex_to_rgb(self.mindmap.bgColor)))
            self.setZValue(4)
        else :
            self.setBrush(QColor(255,255,255))
            self.setZValue(5)
        self.updateStr()

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

    def changeColor(self,newColor):
        self.color=newColor
        pen=self.pen()
        pen.setColor(self.color)
        self.setPen(pen)
        self.shine()
        if self.idLabel:
            self.idLabel.setDefaultTextColor(self.pen().color())
        self.updateStr()

    ### Hover ###
    def hoverEnterEvent(self, event):
        if self.level!=4:
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
        if (QApplication.keyboardModifiers() == Qt.ShiftModifier):
            # self.setBrush(Qt.red)
            self.mindmap.newEdges(self)
        elif event.button()== Qt.MouseButton.LeftButton and (QApplication.keyboardModifiers() == Qt.ControlModifier):
            self.mindmap.select(self)


    def move(self,pos):
        self.moving=True
        self.setPos(pos)
        self.magnify(0)
        self.updateEdges()
        self.lastPos=pos

    def relativeMove(self,delta):
        self.move(self.scenePos()+delta)


    def mouseMoveEvent(self, event):
        self.move(event.scenePos())
        self.mindmap.moveSelected(self,event.scenePos()-event.lastScenePos())

    def mouseReleaseEvent(self, event):
        if self.moving :
            self.moving=False
            self.optimizeEdges()
            self.updateStr()
            self.mindmap.releaseSelected(self)

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

    def toString (self):
        frList,toList=[],[]
        for edgeId in self.edges:
            t=int(self.edges[edgeId].width*10)
            e=''
            if t!=13:
                e="({})".format(t)
            if edgeId[0]==self.id:
                e=str(edgeId[1])+e
                toList.append(e)
            elif edgeId[1]==self.id:
                e=str(edgeId[0])+e
                frList.append(e)
            else :
                print("Error in edge id :",edgeId)
        frStr=""
        if frList!=[]:
            frStr="from:"+str(frList)[1:-1].replace(' ','').replace("'",'')+";"
        toStr=""
        if toList!=[]:
            toStr="to:"+str(toList)[1:-1].replace(' ','').replace("'",'')+";"
        if self.color :
            if isinstance(self.color,QColor):colorHex=rgb_to_hex(self.color.getRgb()[:3])
            elif isinstance(self.color,tuple):colorHex=rgb_to_hex(self.color)
            else :colorHex=self.color
            if colorHex!="":
                colorStr=";color="+colorHex
        levelStr=""
        if self.level!=1:
            levelStr=";level="+str(self.level)
        s=("#{}:"+frStr+toStr+"x={:.1f};y={:.1f};size={:.3f}{}{}\n").format(self.id,self.scenePos().x(),self.scenePos().y(),self.size,colorStr,levelStr)
        s+=self.content.toPlainText()
        return s

    def updateStr(self):
        self.tab.textEdit.updateBubble(self)

    def getInnerSvg(self):
        if not self.innerSvg:
            self.innerSvg=self.latexMaker.makeLatexSvg(self.content)
        return self.innerSvg



    def constructFromDesc (self,desc):
        desc=desc.splitlines()

        ### First line ###
        fl=desc[0].split(':',maxsplit=1)
        if fl[0][0]!= '#' : raise ("Error in contents file : '#' missing.")
        self.id=int(fl[0][1:]) # ID
        args=fl[1].split(';')
        for a in args :
            if contains(a,"to"):
                for k in a.split(':',1)[1].split(','):
                    self.toLinks.append(k)
            elif contains(a,"from","fr"):
                self.fromLinks=[k for k in a.split(':')[1].split(',')]
            elif contains(a,"size","s"):
                if ':' in a : self.size=float(a.split(':')[1])
                elif '=' in a : self.size=float(a.split('=')[1])
                self.setScale(self.size)
            elif contains(a,"color","col","c"):
                if ':' in a : self.color=a.split(':')[1]
                elif '=' in a : self.color=a.split('=')[1]
                if self.color.isdigit() and '#' not in self.color:
                    self.color='#'+self.color
            elif contains(a,"level","lev"):
                if ':' in a : self.level=a.split(':')[1]
                elif '=' in a : self.level=a.split('=')[1]
                self.level=max(0,min(int(self.level),4))
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

    # def writePos (self):
    #     if self.tab and self.id:
    #         xStr=str(round(self.scenePos().x(),1))
    #         yStr=str(round(self.scenePos().y(),1))
    #         lines=self.tab.textEdit.toPlainText().split('\n')
    #         index=None
    #         for i,l in enumerate(lines):
    #             if "#"+str(self.id)+':' in l:
    #                 index=i
    #                 break
    #         if index!=None :
    #             [idPart,par]=lines[index].split(':',1)
    #             par=par.split(';')
    #             newX,newY=False,False
    #             for i,s in enumerate(par):
    #                 if "x" in s and "=" in s :
    #                     par[i]="x="+xStr
    #                     newX=True
    #                 if "y" in s and "=" in s :
    #                     par[i]="y="+yStr
    #                     newY=True
    #             if not newX : par.append("x="+xStr)
    #             if not newY : par.append("y="+yStr)
    #             lines[index]=idPart+':'+';'.join(par)
    #             contents='\n'.join(lines)
    #             self.tab.textEdit.setPlainText(contents)

    def removeEdge(self,edge):
        if edge.id in self.edges:
            self.edges.pop(edge.id)
            self.updateStr()

    def delete (self,scene):
        self.hide()
        while len(self.edges)>0:
            self.edges.popitem()[1].delete(scene)
        self.tab.textEdit.removeBubble(self)
        scene.removeItem(self)