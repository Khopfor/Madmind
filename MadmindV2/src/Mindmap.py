from math import ceil

from numpy import isin
# Local imports
from Bubble import Bubble
from Edge import Edge
from utils import cleanStr, contains, hex_to_rgb

class Mindmap():
    def __init__(self,name,contents,latexMaker=None,tab=None,progress=None):
        self.name=name
        self.title=""
        self.width=2000
        self.height=2000
        self.tab=tab
        self.bubbles={}
        self.latexMaker=latexMaker
        self.lastId=-10
        self.newEdgeFr=None
        self.bgColor="#faf2e8"
        self.bubbleColor=None
        self.selected={}

        ### Headers and settings ###
        self.readHeaders(contents)
        self.constructBubbles(contents,progress) # Creation of the bubbles
        self.constructEdges(progress)

    # Reads headers
    def readHeaders (self,contents):
        headers=contents[:contents.find('\n#')]
        headers=headers.split('|')
        for h in headers :
            if h!='':
                [k,v]=cleanStr(h).split(':')
                if "itle" in k :
                    self.title=v
                    if self.title!="<title>":
                        if self.tab :
                            self.tab.setTabText(self.title)
                elif contains(k,"idth"):
                    self.width=int(v)
                elif contains(k,"eight"):
                    self.height=int(v)
                elif "ubble" in k and "olor" in k :
                    self.bubbleColor=v
                elif contains(k,"bgColor","BgColor","Bg Color","bg color"):
                    self.bgColor=v

    def contrastedColor(self):
        bg=self.bgColor
        if bg :
            if "#" in bg:
                bg=hex_to_rgb(bg)
            if isinstance(bg,tuple):
                if bg[0]+bg[1]+bg[2]>3*255/2:
                    color=(5,5,5)
                else :
                    color=(250,250,250)
            return color
        else :
            return None

    def updateEdgeColor(self):
        color=self.contrastedColor()
        if color:
            for bub in self.bubbles.values():
                for e in bub.edges.values():
                    e.changeColor(color)
            

    def newBubble(self,x,y,scene):
        newBubble=Bubble(x=x,y=y,id=self.lastId+10,latexMaker=self.latexMaker,tab=self.tab,mindmap=self,color=self.bubbleColor)
        self.lastId+=10
        if newBubble.id not in self.bubbles:
            self.bubbles[newBubble.id]=newBubble
            contents=self.tab.textEdit.toPlainText()
            if contents[-1]!='\n': contents+='\n'
            contents+="\n#{}:x={};y={}".format(newBubble.id,x,y)
            self.tab.textEdit.setPlainText(contents)
            scene.addItem(newBubble)
            newBubble.drawn=True
        else :
            print("Error : id already used.")


    # Constructs the bubbles
    def constructBubbles (self,contents,progress=None):          
        # if type(contents)==type(""):
        #     lines=contents.splitlines()
        # i=0
        # while '#0' not in lines[i]:
        #     i+=1
        # contents='\n'.join(lines[i:]).split('#')

        if "#0:" in contents :
            contents=contents[contents.find("#0:"):].split('#')
            Ntot=len(contents)
            for i,desc in enumerate(contents) :
                if desc!='' and "¤" not in desc :
                    # try :
                    id=int(desc.split(':',1)[0])
                    if id in self.bubbles :
                        print("ID Error : ID '"+str(id)+"' not unique.")
                    else :
                        self.bubbles[id]=Bubble(desc='#'+desc,latexMaker=self.latexMaker,tab=self.tab,mindmap=self,color=self.bubbleColor)
                        self.lastId=max(self.lastId,id)
                        # print("Bubble",id,"created at",self.bubbles[id].scenePos())
                    # except :
                    #     print("Invalid entry : ",desc)
                    if progress!=None:
                        progress.setValue(ceil(i/Ntot*50))


    def newEdges(self,bubble):
        for object in self.selected.values():
            if object != bubble and isinstance(object,Bubble):
                newEdge=Edge(object,bubble,mindmap=self,color=self.contrastedColor())
                if object.addEdge(newEdge) and bubble.addEdge(newEdge) :
                    self.tab.canvas.scene.addItem(newEdge)
                    # self.tab.writeNewEdge(newEdge)
                    object.updateStr()
                    bubble.updateStr()
        self.deselectAll()


    def constructEdges(self,progress=None):
        Nbub=len(self.bubbles)
        for i,bub in enumerate(self.bubbles.values()):
            bub.constructEdges(self.bubbles)
            if progress!=None:
                progress.setValue(50+ceil(i/Nbub*50))
        self.updateEdgeColor()


    # Counts the bubbles
    def countBubbles (self):
        n=len(self.bubbles)
        return n

    # Draws objects
    def draw (self,scene):
        for bub in self.bubbles.values() :
            scene.addItem(bub)
            bub.drawEdges(scene)

    def select(self,object):
        if object.id in self.selected :
            del self.selected[object.id]
            object.shine(0)
        else :
            self.selected[object.id]=object
            object.shine(1)

    def moveSelected(self,movedBubble,delta):
        for object in self.selected.values():
            if object != movedBubble:
                if isinstance(object,Bubble):
                    object.relativeMove(delta)

    def deselectAll(self):
        for object in self.selected.values():
            object.shine(0)
        self.selected={}

    def deleteSelection(self):
        for object in self.selected.values():
            object.delete(self.tab.canvas.scene)
        self.selected={}