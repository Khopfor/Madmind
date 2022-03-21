from logging import raiseExceptions
from PIL import Image, ImageDraw, ImageFont
from utils import *
import drawSvg as draw
import numpy as np
from Edge import Edge
import Mindmap
import matplotlib.pyplot as plt

class Bubble ():
    def __init__(self,desc='',id=0,index=[0,1],lines=[],edges=[],latexMaker=None):

        ### Default parameters ###
        self.id=id
        self.xIndex,self.yIndex=index

        # Position
        self.x=0
        self.y=100*id
        self.center=np.array([self.x,self.y])
        self.fixed=False

        # Shape
        self.size=1
        # 1=scale
        self.a=40*self.size
        self.b=10*self.size

        # Style
        self.width=3
        self.color="#663366"
        self.bg="white"

        # Edges
        self.edges={}
        self.toLinks=[]
        self.fromLinks=[]

        self.constraints=[None,None]
        self.placed=0

        ### Construct from text description ###
        if desc != '':
            lines=self.constructFromDesc(desc)

        self.innerSvg=latexMaker.makeLatexSvg(lines,self.id==0)
        self.findEllipseSize()
        self.radius=(self.a+self.b)/2

        self.mindmap=None
        for l in lines:
            if "MINDMAP" in l:
                with open(l.split(':')[1].replace(' ',''),'r') as f:
                    self.mindmap=f.readlines()
                    f.close()
        if self.mindmap :
            self.mindmap=Mindmap.Mindmap(self.mindmap,origin=self.center,scale=self.radius/4000)

        # self.preamble = "\\documentclass{article}\\usepackage{amsmath,amsfonts}\\begin{document}\\pagenumbering{gobble}\\Huge"


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
                    self.toLinks.append(k)
            elif contains(a,"from","fr","f"):
                self.fromLinks=[k for k in a.split(':')[1].split(',')]
            elif contains(a,"size","s"):
                if ':' in a : self.size=float(a.split(':')[1])
                elif '=' in a : self.size=float(a.split('=')[1])
                self.width*=self.size
            elif contains(a,"color","col","c"):
                if ':' in a : self.color=a.split(':')[1]
                elif '=' in a : self.color=a.split('=')[1]
                if self.color.isdigit() and '#' not in self.color:
                    self.color='#'+self.color
            elif contains(a,"x"):
                if '=' in a :
                    x=float(a.split('=')[1])
                    self.constraints[0]=x
                    self.x=x
                # if '>' in a : self.constraints.append({"type":"ineq","fun":lambda X:X[2*self.id]-float(a.split('>')[1])})
                # if '=' in a : self.constraints.append({"type":"eq","fun":lambda X:X[2*self.id]-float(a.split('=')[1])})
            elif contains(a,"y"):
                    y=float(a.split('=')[1])
                    self.constraints[1]=y
                    self.y=y
                # if '>' in a : self.constraints.append({"type":"ineq","fun":lambda X:X[2*self.id+1]-float(a.split('>')[1])})
                # if '=' in a : self.constraints.append({"type":"eq","fun":lambda X:X[2*self.id+1]-float(a.split('=')[1])})
            # else :
            #     print("Invalid entry :",a)

        ### Text lines ###
        lines=desc[1:]

        return lines


    def findEllipseSize (self):
        if self.innerSvg :
            w=self.innerSvg.width/2
            h=self.innerSvg.height/2
            self.a=np.sqrt(w*(h+w))
            self.b=np.sqrt(h*(h+w))
        self.b=max(self.b,self.a/2.5)
        self.a*=self.size
        self.b*=self.size
    

    def constructEdges (self,bubbles):
        N=len(bubbles)
        def readEdge (e):
            style=''
            pathText=''
            e=e.replace(' ','').replace('\n','')
            if ':' in e :
                e,pathText=e.split(':')
            while e and not e.isdigit() :
                style+=e[0]
                e=e[1:]
            return int(e),style,pathText
        for e in self.toLinks :
            e,style,pathText=readEdge(e)
            if e in bubbles and not (e in self.edges and self.edges[e]):
                bubbles[e].fromLinks.append(str(self.id))
                self.edges[e]=Edge(self.id,e,self.center,bubbles[e].center,style=style,text=pathText)
        for e in self.fromLinks :
            e,style,pathText=readEdge(e)
            if e in bubbles and not (self.id in bubbles[e].edges and bubbles[e].edges[self.id]):
                bubbles[e].edges[self.id]=Edge(e,self.id,bubbles[e].center,self.center,style=style,text=pathText)
    

    def place (self,X,bubbles,origin=np.array([0,0]),scale=1):
        if self.constraints[0]==None :
            self.x=X[self.xIndex]
        if self.constraints[1]==None :
            self.y=X[self.yIndex]
        self.x=self.x*scale+origin[0]
        self.y=self.y*scale+origin[1]
        self.center=np.array([self.x,self.y])
        for e in self.edges.values():
            e.place(X,bubbles,origin,scale)

    def initPlace (self,bubbles,x,y):
        # self.placed=2
        # childrenNb=len(self.edges)
        # N=len(bubbles)
        # prevx=self.x-self.radius*childrenNb-10
        # for i,c in enumerate(self.edges) :
        #     # c=int(c.replace('l',''))
        #     if c in bubbles and not bubbles[c].placed:
        #         bubbles[c].pos([prevx+10+bubbles[c].a,self.y-self.b-bubbles[c].b-25])
        #         # print("bubble ",c," placed at ",[prevx+20+bubbles[c].a/2,self.y-self.b/2-80],"!!")
        #         bubbles[c].placed=1
        #         prevx+=10+2*bubbles[c].a
        # for i,c in enumerate(self.edges) :
        #     # c=int(c.replace('l',''))
        #     if c in bubbles and bubbles[c].placed<2:
        #         bubbles[c].placeChildren(bubbles)
        #         bubbles[c].placed=2
        #         # print("place children of ",c)
        if self.placed ==0:
            self.pos(x=x,y=y)
            self.placed=1
        if self.placed <2:
            childrenNb=len(self.edges)
            N=len(bubbles)
            xSpacing,ySpacing=36,52
            prevx=self.x-100*(childrenNb-1)-xSpacing
            for i,e in enumerate(self.edges):
                x=prevx+xSpacing+bubbles[e].a
                y=self.y-self.b-bubbles[e].b-ySpacing
                bubbles[e].initPlace(bubbles,x,y)
                prevx+=xSpacing+2*bubbles[e].a
            self.placed=2


    def pos (self,center=None,x=None,y=None):
        if center :
            x,y=self.checkConstraints(center[0],center[1])
            self.center=np.array([x,y])
            self.x=x
            self.y=y
        elif x and y :
            self.x,self.y=self.checkConstraints(x,y)
        else :
            print("Error in positioning.")


    def draw (self,img,scale):
        if self.mindmap :
            self.mindmap.draw(img)
        for e in self.edges.values() :
            e.draw(img,scale)
        img.append(self.ellipseMaker(scale),z=1)
        # img.append(draw.Circle(self.x, self.y, self.radius, fill='white', stroke='black', stroke_width=2))
        img.draw(self.innerSvg, x=self.x, y=self.y, center=True, scale=scale*self.size,z=1)

    
    def ellipseMaker (self,scale):
        ellipse=draw.Path(fill=self.bg,stroke=self.color,stroke_width=self.width*scale)
        ellipse.M(self.x, self.y+self.b*scale)
        ellipse.A(self.a*scale, self.b*scale, 0, True, True, self.x-1, self.y+self.b*scale)  # Ellipse path
        ellipse.Z()
        return ellipse

    def checkConstraints(self,x=None,y=None,X=[]):
        if self.constraints[0]!=None:
            x=self.constraints[0]
        else :
            if X!=[]:
                x=X[self.xIndex]
        if self.constraints[1]!=None:
            y=self.constraints[1]
        else :
            if X!=[]:
                y=X[self.yIndex]
        return x,y

    def potential (self,x,y,x2=None,y2=None,tl=0,A=10000,range=1.4,func="sqBell"):
        # epsilon=1e-6
        # r=self.radius+tl/2
        # print(self.radius)
        if not x2 : x2=self.x
        if not y2 : y2=self.y
        d=np.sqrt(((x-x2)/self.a)**2+((y-y2)/self.b)**2)
        # return A*(1/(dsq+epsilon)-1/(r**2+epsilon))
        z=d/(range+0.5*tl/self.radius)
        if func=="sqBell":
            return self.sqBell(z,A)
        elif func=="cliff":
            return self.cliff(z,A)
        elif func=="inv":
            return self.inv(z,A)
        else:
            return self.sqBell(z,A)

    def inv (self,x,A=1):
        return A/(x+1)

    def cliff (self,x,A=1):
        return (1-x)/(1/A+x**20)

    def sqBell (self,x,A=1):
        return (-x**2+A)*np.exp(-x**4)

    def plotpot (self):
        X=np.linspace(-1,200,1000)
        Y=[self.potential(x,0,20) for x in X]
        plt.ylim(-10,2e4)
        plt.plot(X,Y)
        plt.show()

# bub=Bubble()
# print(bub.a)
# bub.plotpot()
# print(Bubble().potential(0,0,0))