import numpy as np
import drawSvg as draw
from scipy.optimize import fsolve,minimize

from utils import Bezier, lengthBezier


class Edge ():
    def __init__(self,frid,toid,fr,to,text='',style=None):
        fr=np.array(fr)
        to=np.array(to)
        self.points=[fr,fr+(to-fr)/3,fr+(to-fr)*2/3,to]
        self.frid=frid
        self.toid=toid
        self.index=-1
        self.color="black"
        self.width=1.3
        self.long=False
        if style :
            for c in style :
                if c=='l':
                    self.long=True
                if c=='t':
                    self.width*=1.7
        self.text=text

    def place (self,X,bubbles,origin=np.array([0,0]),scale=1):
        self.points=self.computePoints(X,bubbles,method='')
        for i in range (len(self.points)) :
            self.points[i]=self.points[i]*scale+origin

    def computePoints (self,X,bubbles,method="length"):
        P0,P1,P2,P3=self.handlePointsMethod(X,bubbles)
        if method=="length":
            l=X[self.index+2]
            P2=self.lengthMethod(X,P0,P1,l,P3,bubbles)
        return [P0,P1,P2,P3]

    def lengthMethod (self,X,P0,P1,l,P3,bubbles):
        x_to,y_to=bubbles[self.toid].checkConstraints(X=X)
        j=[bubbles[self.toid].xIndex,bubbles[self.toid].yIndex]
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


    def handlePointsMethod (self,X,bubbles):
        x_fr,y_fr=bubbles[self.frid].checkConstraints(X=X)
        x_to,y_to=bubbles[self.toid].checkConstraints(X=X)
        # i=[bubbles[self.frid].xIndex,bubbles[self.frid].yIndex]
        # j=[bubbles[self.toid].xIndex,bubbles[self.toid].yIndex]
        # a_fr=bubbles[self.frid].a+bubbles[self.frid].width/2+self.width/2
        # b_fr=bubbles[self.frid].b+bubbles[self.frid].width/2+self.width/2
        # P0=np.array([X[i[0]]+a_fr*np.cos(X[self.index]),X[i[1]]+b_fr*np.sin(X[self.index])])
        # t1=(abs(X[self.index+1])+1.3)#/np.linalg.norm(self.points[0]-np.array(X[2*self.frid:2*self.frid+2]))+1
        # P1=P0*t1+(1-t1)*np.array([X[i[0]],X[i[1]]])
        # a_to=bubbles[self.toid].a+bubbles[self.toid].width/2+self.width/2
        # b_to=bubbles[self.toid].b+bubbles[self.toid].width/2+self.width/2
        # P3=np.array([X[j[0]]+a_to*np.cos(X[self.index+3]),X[j[1]]+b_to*np.sin(X[self.index+3])])
        # t2=(abs(X[self.index+2])+1.3)#/np.linalg.norm(self.points[3]-np.array(X[2*self.toid:2*self.toid+2]))+1
        # P2=P3*t2+(1-t2)*np.array([X[j[0]],X[j[1]]])
        a_fr=bubbles[self.frid].a+bubbles[self.frid].width/2
        b_fr=bubbles[self.frid].b+bubbles[self.frid].width/2
        P0=np.array([x_fr+a_fr*np.cos(X[self.index]),y_fr+b_fr*np.sin(X[self.index])])
        t1=(abs(X[self.index+1])+1.1)#/np.linalg.norm(self.points[0]-np.array(X[2*self.frid:2*self.frid+2]))+1
        P1=P0*t1+(1-t1)*np.array([x_fr,y_fr])
        a_to=bubbles[self.toid].a+bubbles[self.toid].width/2+self.width/2
        b_to=bubbles[self.toid].b+bubbles[self.toid].width/2+self.width/2
        P3=np.array([x_to+a_to*np.cos(X[self.index+3]),y_to+b_to*np.sin(X[self.index+3])])
        t2=(abs(X[self.index+2])+1.1)#/np.linalg.norm(self.points[3]-np.array(X[2*self.toid:2*self.toid+2]))+1
        P2=P3*t2+(1-t2)*np.array([x_to,y_to])
        return [P0,P1,P2,P3]

    def draw (self,img,scale):
        bezier=self.bezierMaker(scale)
        img.append(bezier,z=0)
        img.draw(self.arrowMaker(scale),z=0)
        if self.text :
            print(self.text)
            img.append(draw.Text(self.text, 20*scale, path=bezier))#,text_anchor="middle", valign='top'),z=5)

    def bezierMaker (self,scale):
        P0,P1,P2,P3=self.points
        bezier=draw.Path(fill="none", stroke=self.color, stroke_width=self.width*scale, stroke_linecap='round')
        # bezier=draw.Raw('<path d="M {} {} C {} {}, {} {}, {} {}" stroke="black" fill="none"/>'.format(P0[0],P0[1],P1[0],P1[1],P2[0],P2[1],P3[0],P3[1]))
        bezier.M(P0[0],P0[1])
        bezier.C(P1[0],P1[1],P2[0],P2[1],P3[0],P3[1])
        # bezier.Z()
        return bezier

    def arrowMaker (self,scale):
        P=Bezier(0.88,*self.points)
        P3=self.points[3]
        length=6*scale
        angle=35*np.pi/180
        Z=1+(P3[0]-P[0])**2/(P3[1]-P[1])**2
        chi=length*np.linalg.norm(P-P3)*np.cos(angle)
        x1,x2=P3[0]+length/np.sqrt(Z)*(np.cos(angle)*(P[0]-P3[0])/abs(P[1]-P3[1])+np.sin(angle)),P3[0]+length/np.sqrt(Z)*(np.cos(angle)*(P[0]-P3[0])/abs(P[1]-P3[1])-np.sin(angle))
        y1,y2=P3[1]+(chi-(x1-P3[0])*(P[0]-P3[0]))/(P[1]-P3[1]),P3[1]+(chi-(x2-P3[0])*(P[0]-P3[0]))/(P[1]-P3[1])
        arrow=draw.Lines(x1,y1,*P3,x2,y2,close=False,fill="none",stroke=self.color,stroke_width=self.width*scale,stroke_linecap='round',stroke_linejoin='round')
        return arrow

    def t (self,a,b,dx,dy):
        if dx==0:
            return -np.sign(dy)*np.pi/2
        else :
            t=np.arctan(a/b*dy/dx)
            if dx>0:
                t+=np.sign(dy)*np.pi
            return t