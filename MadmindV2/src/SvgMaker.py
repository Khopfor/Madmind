from math import ceil
from sys import argv
import os
from matplotlib.pyplot import close
import numpy as np
import drawSvg as draw
from Mindmap import Mindmap
from LatexMaker import LatexMaker

LATEXCOMMANDS="settings/latexCommands.json"

class Progress():
    def __init__(self,printFunc=None):
        self.progress=0
        self.printFunc=printFunc

    def setValue(self,v):
        self.progress=v-50
        self.display()

    def incr (self,a):
        self.progress+=a
        self.display()

    def display(self):
        if self.printFunc:
            self.printFunc(self.progress)

class SvgMaker():
    def __init__(self,mmName):
        print("Making svg for mindmap {}...".format(mmName))
        print(" 0%",end='\r')
        f=open("mindmaps/{}/{}.txt".format(mmName,mmName),'r')
        contents=f.read()
        f.close()
        latexMaker=LatexMaker(LATEXCOMMANDS)
        progress=Progress(self.printProgress)
        self.mindmap=Mindmap(mmName,contents,latexMaker=latexMaker,progress=progress)
        xmin,xmax,ymin,ymax=None,None,None,None
        k=3/4
        Ntot=self.mindmap.countBubbles()
        for bub in self.mindmap.bubbles.values():
            pos=bub.scenePos()
            innerSvg=bub.getInnerSvg()
            if innerSvg :
                w=innerSvg.width/2*k
                h=innerSvg.height/2*k
                bub.a=np.sqrt(w*(h+w))
                bub.b=np.sqrt(h*(h+w))
            a=bub.a*bub.size
            b=bub.b*bub.size
            if not xmin or xmin > pos.x()-a-10:xmin=pos.x()-a-10
            if not xmax or xmax < pos.x()+a+10:xmax=pos.x()+a+10
            if not ymin or ymin > -pos.y()-b-10:ymin=-pos.y()-b-10
            if not ymax or ymax < -pos.y()+b+10:ymax=-pos.y()+b+10
            progress.incr(35/Ntot)
        width=xmax-xmin
        height=ymax-ymin
        bgColor="rgb(250,242,232)"
        svg=draw.Drawing(width,height,origin=(xmin,ymin),displayInline=False)
        svg.draw(draw.Rectangle(xmin,ymin,width,height,fill=bgColor),z=0)
        for bub in self.mindmap.bubbles.values():
            x=bub.x()
            y=-bub.y()
            ellipse=draw.Ellipse(x,y,bub.a*bub.size,bub.b*bub.size,fill="white",stroke=bub.color,stroke_width=2*bub.size)
            svg.append(ellipse,z=2)
            innerSvg=bub.getInnerSvg()
            if innerSvg :
                w=innerSvg.width/2*bub.size*k
                h=innerSvg.height/2*bub.size*k
                svg.draw(innerSvg,x=x-w,y=y-h,scale=bub.size*k,z=3)
            for e in bub.edges.values():
                e.optimizePath()
                P0,P1,P2,P3=e.P(e.params)
                svg.append(self.bezierMaker((P0,P1,P2,P3)),z=1)
                A1,A2=e.arrowMaker(P0,P1,P2,P3,1)
                svg.draw(draw.Lines(A1.x(),-A1.y(),P3.x(),-P3.y(),A2.x(),-A2.y(),fill="None",stroke="black",stroke_width=1.3,stroke_linecap='round',stroke_linejoin='round'),z=2)
                # svg.draw(arrow,z=5)
            progress.incr(15/Ntot)
        svgpath="mindmaps/{}/{}.svg".format(mmName,mmName)
        svg.saveSvg(svgpath)
        print("Svg ready !")
        # self.minify(svgpath)
        # os.system("eog "+svgpath)

    def bezierMaker (self,points):
        P0,P1,P2,P3=points
        bezier=draw.Path(fill="none", stroke="black", stroke_width=1.3, stroke_linecap='round')
        # bezier=draw.Raw('<path d="M {} {} C {} {}, {} {}, {} {}" stroke="black" fill="none"/>'.format(P0[0],P0[1],P1[0],P1[1],P2[0],P2[1],P3[0],P3[1]))
        bezier.M(P0.x(),-P0.y())
        bezier.C(P1.x(),-P1.y(),P2.x(),-P2.y(),P3.x(),-P3.y())
        return bezier

    def getSymbolId (self,s,start):
        sub='id="'
        idStart=s.find(sub,start)
        idEnd=s.find('">',idStart)
        return s[idStart+len(sub):idEnd]

    def printProgress(self,v):
        print("{}%".format(ceil(v)),end='\r')

    def minify(self,svgPath):
        svgFile=open(svgPath,'r')
        svgCode=svgFile.read()
        svgFile.close()
        cursor=svgCode.find("<defs>")
        if cursor!=-1:
            symbolStart=svgCode.find("<symbol ")
            symbolEnd=svgCode.find("</symbol>",symbolStart)
            while symbolStart!=-1:
                id=self.getSymbolId(svgCode,symbolStart)
                pathStart=svgCode.find("<path ",symbolStart,symbolEnd)
                if pathStart!=-1:
                    pathEnd=svgCode.find("/>",pathStart)
                    other=svgCode.find(svgCode[pathStart:pathEnd+2],pathEnd)
                    while other!=-1:
                        otherSymbolStart=svgCode.find("<symbol ",other-80)
                        otherSymbolEnd=svgCode.find("</symbol>",otherSymbolStart)
                        otherId=self.getSymbolId(svgCode,otherSymbolStart)
                        # print(id,"|",otherId)
                        # print(svgCode[otherSymbolStart:otherSymbolEnd+9])
                        svgCode=svgCode[:otherSymbolStart]+svgCode[otherSymbolEnd+9:]
                        svgCode=svgCode.replace(otherId,id)
                        other=svgCode.find(svgCode[pathStart:pathEnd+2],pathEnd)
                symbolStart=svgCode.find("<symbol ",symbolEnd)
                symbolEnd=svgCode.find("</symbol>",symbolStart)
            svgFile=open(svgPath,'w')
            svgFile.write(svgCode)
            svgFile.close()



SvgMaker(argv[1])