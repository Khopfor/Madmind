import numpy as np
from scipy.optimize import fsolve,minimize
# PyQt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint,QPointF, QRect,QSize,QSizeF
from PyQt5.QtGui import QPixmap,QPainter,QColor,QPen,QPainterPath,QPolygonF
# Local imports
from utils import *


class Edge (QGraphicsPathItem):
    def __init__(self,fr,to,text='',style=None,mindmap=None):
        super().__init__()
        self.fr=fr
        self.to=to
        self.id=(self.fr.id,self.to.id)
        self.params=[1,5,5,1]
        self.opti=True
        self.setZValue(0)
        self.width=1.3
        self.color=QColor(5,5,5)
        pen=self.pen()
        pen.setWidthF(self.width)
        pen.setColor(self.color)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.arrow=QGraphicsPolygonItem(parent=self)
        arrowPen=self.arrow.pen()
        arrowPen.setWidthF(self.width)
        arrowPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrowPen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.arrow.setPen(arrowPen)
        self.updatePath()
        # print(self.points)
        self.index=-1
        self.long=False
        if style :
            for c in style :
                if c=='l':
                    self.long=True
                if c=='t':
                    self.width*=1.7
        self.text=text

        self.mindmap=mindmap
        if self.opti and self.mindmap:
            self.optimizePath()

        # print(self.P([0,1.5,1.5,0.5]),self.P([1,1.5,1.5,1.5]))


    # def P(self,k):
    #     if k==0:return self.fr.scenePos()
    #     elif k==1:return self.

    def P (self,X):
        P0=QPointF(self.fr.x()+self.fr.getA()*np.cos(X[0]),self.fr.y()+self.fr.getB()*np.sin(X[0]))
        if X[1] <=1.3 : X[1]=1.3
        P1=P0*X[1]+(1-X[1])*self.fr.scenePos()
        P3=QPointF(self.to.x()+(self.to.getA()+0.5)*np.cos(X[3]),self.to.y()+(self.to.getB()+0.5)*np.sin(X[3]))
        if X[2] <=1.3 : X[2]=1.3
        P2=P3*X[2]+(1-X[2])*self.to.scenePos()
        return P0,P1,P2,P3

    def shrink(self):
        if self.width > 0.2:
            self.width/=1.4
        self.updateWidth()
        # self.tab.writeNewWidth(self)

    def grow(self):
        if self.width < 5:
            self.width*=1.4
        self.updateWidth()
        # self.tab.writeNeWidth(self)

    def shine(self,bool=True):
        if bool :
            shine=QGraphicsDropShadowEffect()
            shine.setBlurRadius(10)
            shine.setOffset(0,0)
            shine.setColor(self.pen().color())
            self.setGraphicsEffect(shine)
        else:
            self.setGraphicsEffect(None)

    def updateWidth(self):
        pen=self.pen()
        pen.setWidthF(self.width)
        self.setPen(pen)
        arrowPen=self.arrow.pen()
        arrowPen.setWidthF(self.width)
        self.arrow.setPen(arrowPen)


    def updatePath(self):
        if not self.opti:
            dx=self.fr.scenePos().x()-self.to.scenePos().x()
            dy=self.fr.scenePos().y()-self.to.scenePos().y()
            self.params[0]=self.a(self.fr.getA(),self.fr.getB(),dx,dy)
            # self.params[3]=self.a(self.to.getA(),self.to.getB(),-dx,-dy)
            self.params[3]=np.sign(dy)*np.pi/2
        P0,P1,P2,P3=self.P(self.params)
        pp=QPainterPath(P0)
        pp.cubicTo(P1,P2,P3)
        A1,A2=self.arrowMaker(P0,P1,P2,P3)
        pp.lineTo(A1)
        pp.moveTo(P3)
        pp.lineTo(A2)
        self.setPath(pp)
        # self.arrow.setPolygon(self.arrowMaker(P0,P1,P2,P3))

    def optimizePath(self):
        if self.opti :
            X0=np.array(self.params)
            def f(X):
                return self.energy(X)
            bounds=[(None,None),(1.1,50),(1.1,50),(None,None)]
            res=minimize(f,X0,bounds=bounds)
            self.params,success,msg=res.x,res.success,res.message
            # print("Success :",success,"|",msg,res.x,self.params)
            self.updatePath()


    def energy(self,X):
        E_edges=0
        E_bypass=0
        P0,P1,P2,P3=self.P(X)
        l=lengthBezier(P0,P1,P2,P3,20)
        E_edges+=l**2

        # if l > 30 :
        #     for t in [0.25,0.5,0.75]:
        #         P=Bezier(t,P0,P1,P2,P3)
        #         for id2 in bubbles:
        #             if self.fr.id!=id2 and id2!=self.to.id:
        #                 E_bypass+=5*bubbles[id2].potential(P.x(),P.y())
        # print("E=",E_edges,E_bypass)
        E=E_edges+E_bypass
        return E

    # def plot(self):
    #     X=np.linspace(-np.pi,np.pi,1000)
    #     Y=[self.energy(x,self.fr.mindmap.bubbles) for x in X]
    #     plt.plot(X,Y)
    #     plt.show()

    def place (self,X,origin=np.array([0,0]),scale=1):
        self.points=self.computePoints(X,method='')
        for i in range (len(self.points)) :
            self.points[i]=self.points[i]*scale+origin

    def computePoints (self,X,method="length"):
        P0,P1,P2,P3=self.handlePointsMethod(X)
        if method=="length":
            l=X[self.index+2]
            P2=self.lengthMethod(X,P0,P1,l,P3)
        return [P0,P1,P2,P3]

    def lengthMethod (self,X,P0,P1,l,P3):
        x_to,y_to=self.mindmap.bubbles[self.toid].checkConstraints(X=X)
        j=[self.mindmap.bubbles[self.toid].xIndex,self.mindmap.bubbles[self.toid].yIndex]
        toCenter=np.array([x_to,y_to])
        def f (u):
            u=abs(u)+1.3
            P2=P3*u+(1-u)*toCenter
            return (lengthBezier(P0,P1,P2,P3,N=20)-l)**2
        u=abs(minimize(f,3).x[0])+1.3
        # print(u)
        P2=P3*u+(1-u)*toCenter
        # print(P2)
        return P2


    def arrowMaker (self,P0,P1,P2,P3,scale=1):
        P=Bezier(0.88,P0,P1,P2,P3)
        length=6*scale
        angle=35*np.pi/180
        Z=1+(P3.x()-P.x())**2/(P3.y()-P.y())**2

        chi=length*norm(P-P3)*np.cos(angle)
        x1,x2=P3.x()+length/np.sqrt(Z)*(np.cos(angle)*(P.x()-P3.x())/abs(P.y()-P3.y())+np.sin(angle)),P3.x()+length/np.sqrt(Z)*(np.cos(angle)*(P.x()-P3.x())/abs(P.y()-P3.y())-np.sin(angle))
        y1,y2=P3.y()+(chi-(x1-P3.x())*(P.x()-P3.x()))/(P.y()-P3.y()),P3.y()+(chi-(x2-P3.x())*(P.x()-P3.x()))/(P.y()-P3.y())
        # polygon= QPolygonF([QPointF(x1,y1),P3,QPointF(x2,y2)])
        return QPointF(x1,y1),QPointF(x2,y2)
        # arrow=draw.Lines(x1,y1,*P3,x2,y2,close=False,fill="none",stroke=self.color,stroke_width=self.width*scale,stroke_linecap='round',stroke_linejoin='round')

    def a (self,a,b,dx,dy):
        if dx==0:
            return -np.sign(dy)*np.pi/2
        else :
            t=np.arctan(a/b*dy/dx)
            if dx>0:
                t+=np.sign(dy)*np.pi
            return t

    def reverse(self):
        # TO DO
        pass

    def toggleBlur(self,bool):
        if bool :
            blur=QGraphicsBlurEffect()
            self.setGraphicsEffect(blur)
        else :
            self.setGraphicsEffect(None)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if event.button()== Qt.MouseButton.LeftButton and QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            self.mindmap.select(self)
        elif QApplication.keyboardModifiers()== Qt.KeyboardModifier.ControlModifier :
            self.grow()
        elif QApplication.keyboardModifiers() == Qt.KeyboardModifier.ShiftModifier :
            self.shrink()
        elif QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier :
            self.reverse()
        return super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        print("hovered!")
        self.tab.canvas.scene.hoveredObject=self
        return super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.tab.canvas.scene.hoveredObject=None
        return super().hoverEnterEvent(event)

    def delete(self,scene):
        self.fr.removeEdge(self)
        self.to.removeEdge(self)
        scene.removeItem(self)