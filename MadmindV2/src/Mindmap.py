from Bubble import Bubble

class Mindmap():
    def __init__(self,name,contents,latexMaker=None,tab=None):
        self.name=name
        print(name)
        self.title=""
        self.tab=tab
        self.bubbles={}
        self.latexMaker=latexMaker
        self.lastId=-10

        ### Headers and settings ###
        if type(contents)==type(""):
            contents=contents.split('\n')
        self.readHeaders(contents)

        self.constructBubbles(contents) # Creation of the bubbles
        self.constructEdges()

    # Reads headers
    def readHeaders (self,headers):
        i=0
        try:self.title=headers[0].split(':')[1].replace("\n",'').replace(' ','')
        except:pass
        try:self.height=int(headers[1].split(':')[1])
        except:pass
        try:self.width=int(headers[2].split(':')[1])
        except:pass
        try:self.bgColor=headers[3].split(':')[1]
        except:pass
        try:tol=headers[5].split(':')[1]
        except:pass
        try:
            self.tol=float(tol)
        except:
            self.tol=None

    def newBubble(self,x,y,id=None):
        if not id :
            id=self.lastId+10
            self.lastId=id
        self.bubbles[id]=Bubble(x=x,y=y,latexMaker=self.latexMaker,tab=self.tab,mindmap=self)

    # Constructs the bubbles
    def constructBubbles (self,contents):            
        if type(contents)==type(""):
            contents=contents.split('\n')

        i=0
        while '#0' not in contents[i]:
            i+=1
        contents='\n'.join(contents[i:]).split('#')
        for c in contents :
            if c!='' and "¤" not in c :
                # try :
                id=int(c.split(':',1)[0])
                if id in self.bubbles :
                    print("ID Error : ID '"+str(id)+"' not unique.")
                else :
                    self.bubbles[id]=Bubble(desc='#'+c,latexMaker=self.latexMaker,tab=self.tab,mindmap=self)
                    # print("Bubble",id,"created at",self.bubbles[id].scenePos())
                # except :
                #     print("Invalid entry : ",c)


    def constructEdges(self):
        for bub in self.bubbles.values():
            bub.constructEdges(self.bubbles)


    def drawBubble(self,scene):
        if len(self.bubbles)>0 and not self.bubbles[self.lastId].drawn:
            scene.addItem(self.bubbles[self.lastId])
            self.bubbles[self.lastId].drawn=True

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