from math import ceil
# Local imports
from Bubble import Bubble
from Edge import Edge
from utils import cleanStr

class Mindmap():
    def __init__(self,name,contents,latexMaker=None,tab=None,progress=None):
        self.name=name
        print(name)
        self.title=""
        self.tab=tab
        self.bubbles={}
        self.latexMaker=latexMaker
        self.lastId=-10
        self.newEdgeFr=None
        self.bubbleColor=None

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
                        self.tab.setTabText(self.title)
                elif "ubble" in k and "olor" in k :
                    self.bubbleColor=v
            

    def newBubble(self,x,y,scene):
        newBubble=Bubble(x=x,y=y,id=self.lastId+10,latexMaker=self.latexMaker,tab=self.tab,mindmap=self,color=self.bubbleColor)
        self.lastId+=10
        scene.addItem(newBubble)
        newBubble.drawn=True
        contents=self.tab.textEdit.toPlainText()
        if contents[-1]!='\n': contents+='\n'
        contents+="\n#{}:x={};y={}".format(newBubble.id,x,y)
        self.tab.textEdit.setPlainText(contents)

    def addBubble(self,bubble):
        if bubble.id not in self.bubbles:
            self.bubbles[bubble.id]=bubble
            self.writeBubble(bubble)
        else :
            print("Error : id already used.")

    def writeBubble(self,bubble):
        fileName="mindmap/"+self.tab.tabName+"/"+self.tab.tabName+".txt"
        newText=self.tab.textEdit.toPlainText()+"\n\n#"+str(bubble.id)+": x="+str(bubble.scenePos().x())+";y="+str(bubble.scenePos().y())
        # print(newText)
        self.tab.textEdit.setPlainText(newText)

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


    def newEdge(self,bubble):
        if self.newEdgeFr==None :
            self.newEdgeFr=bubble
            bubble.shine()
        elif self.newEdgeFr==bubble:
            self.newEdgeFr=None
            bubble.shine(False)
        else :
            newEdge=Edge(self.newEdgeFr,bubble,bubbles=self.bubbles)
            if self.newEdgeFr.addEdge(newEdge) and bubble.addEdge(newEdge) :
                self.tab.canvas.scene.addItem(newEdge)
                self.tab.writeNewEdge(newEdge)
            self.newEdgeFr.shine(False)
            self.newEdgeFr=None

    def constructEdges(self,progress=None):
        Nbub=len(self.bubbles)
        for i,bub in enumerate(self.bubbles.values()):
            bub.constructEdges(self.bubbles)
            if progress!=None:
                progress.setValue(50+ceil(i/Nbub*50))


    # Counts the bubbles
    def countBubbles (self):
        n=len(self.bubbles)
        for bub in self.bubbles.values():
            if bub.mindmap :
                n+=bub.mindmap.countBubbles()
        return n

    # Draws objects
    def draw (self,scene):
        for bub in self.bubbles.values() :
            scene.addItem(bub)
            bub.drawEdges(scene)