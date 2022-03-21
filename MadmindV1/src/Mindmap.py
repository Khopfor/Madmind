from operator import pos
from scipy.optimize import minimize
from sqlalchemy import CheckConstraint
from Bubble import Bubble
from utils import *

class Mindmap ():
    def __init__(self,name,contents,settings=None,latexMaker=None,origin=np.array([0,0]),scale=None,t0=False):
        self.name=name
        self.origin=origin
        self.t0=t0
        self.latexMaker=latexMaker
        self.threadId=None

        ### Headers and settings ###
        contents=self.readHeaders(contents)
        self.readSettings(settings)

        ### Scale of the mindmap ###
        self.scale=scale
        if scale==None :
            self.scale=min(self.width/2000,self.height/2000)

        ### Bubbles ###
        self.bubbles={} # Bubble dictionary
        self.constraints=[] # Constraints on the bubbles
        self.constructBubbles(contents) # Creation of the bubbles
        self.N=len(self.bubbles) # Number of bubbles
        for bub in self.bubbles.values() : # Creation of the edges
            bub.constructEdges(self.bubbles)

        ### Parameter vector ###
        self.X0=[]
        self.Xres=[]
        self.funcEval=0
        self.iter=0

        ### Initial mindmap ###
        try :
            posDict=json2dict("mindmaps/"+self.name+"/cache/"+self.name+"_save.json")
        except:
            posDict=None
        self.initPos(posDict) # Constructs initial vector
        self.place(self.X0) # Places objects on the mindmap

    # Reads headers
    def readHeaders (self,headers):
        i=0
        while headers[i][0]=="|" :
            self.title=headers[0].split(':')[1].replace("\n",'').replace(' ','')
            self.height=int(headers[1].split(':')[1])
            self.width=int(headers[2].split(':')[1])
            self.bgColor=headers[3].split(':')[1]
            tol=headers[5].split(':')[1]
            try:
                self.tol=float(tol)
            except:
                self.tol=None
            i+=1
        return ''.join(headers[i+1:]).split('#')[1:]

    def readSettings (self,settings):
        if settings :
            print("Settings : ",settings)
            self.targetLength=settings["targetLength"]
            self.edgeLengthCoef=settings["edgeLengthCoef"]
            self.bypassCoef=settings["bypassCoef"]
            self.hierarchyCoef=settings["hierarchyCoef"]
            self.bubblePotFunc=settings["bubblePotFunc"]
            self.amplitude=settings["amplitude"]
            self.range=settings["range"]
        else :
            self.targetLength=20
            self.edgeLengthCoef=0.1
            self.bypassCoef=0.01
            self.hierarchyCoef=0.1
            self.bubblePotFunc="sqBell"
            self.amplitude=10000
            self.range=1.4


    # Constructs the bubbles
    def constructBubbles (self,contents):
        for c in contents :
            if c!='' and "¤" not in c :
                # try :
                id=int(c.split(':',1)[0])
                if id in self.bubbles :
                    print("ID Error : ID '"+str(id)+"' not unique.")
                else :
                    self.bubbles[id]=Bubble(desc='#'+c,latexMaker=self.latexMaker)
                # except :
                #     print("Invalid entry : ",c)

    # Counts the bubbles
    def countBubbles (self):
        n=len(self.bubbles)
        for bub in self.bubbles.values():
            if bub.mindmap :
                n+=bub.mindmap.countBubbles()
        return n

    # Constructs the initial vector
    def initPos (self,posDict=None):
        c=0
        prevx=-100-10
        if posDict :
            for id in posDict :
                id=int(id)
                if id in self.bubbles :
                    self.bubbles[id].pos(x=posDict[str(id)]["x"],y=posDict[str(id)]["y"])
                    self.bubbles[id].placed=1
        for id in self.bubbles:
            if not self.bubbles[id].placed :
                x=prevx+10+self.bubbles[id].a+100*c
                y=0.3*self.height/2
                self.bubbles[id].initPlace(self.bubbles,x,y)
                prevx+=10+2*self.bubbles[id].a
                c+=1
            if self.bubbles[id].constraints!=[None,None]:
                self.constraints+=self.bubbles[id].constraints

        # Fills X0 with bubble positions
        for bub in self.bubbles.values():
            if bub.constraints[0]==None:
                bub.xIndex=len(self.X0)
                self.X0.append(bub.x)
            else : print(bub.constraints)
            if bub.constraints[1]==None:
                bub.yIndex=len(self.X0)
                self.X0.append(bub.y)
            else : print(bub.constraints)
            # else :
            #     print("Error list assignment index out of range :")

        # Fills X0 with edges parameters
        for bub in self.bubbles.values():
            for e in bub.edges.values():
                e.index=len(self.X0)
                if posDict and str(bub.id) in posDict and str(e.toid) in posDict[str(bub.id)]["edges"]:
                    self.X0=self.X0+posDict[str(bub.id)]["edges"][str(e.toid)]
                else :
                    dx=bub.x-self.bubbles[e.toid].x
                    dy=bub.y-self.bubbles[e.toid].y
                    t=e.t(bub.a,bub.b,dx,dy)
                    self.X0.append(t)
                    self.X0.append(0.1)
                    self.X0.append(0.1)
                    self.X0.append(np.sign(dy)*np.pi/2)
        # print("X0=",self.X0)
        print("Number of constraints :",len(self.constraints))


    # def smartOpti(self):
    #     for id in self.bubbles:

    #         if not self.bubbles[id].placed :
    #             X0=[0,0.8*self.height/2]
    #             bounds=[(-self.width/2,self.width/2),(-self.height/2,self.height/2)]
    #             res=minimize(self.energy,X0,constraints=tuple(self.constraints),bounds=bounds,options={"maxiter":1000,"disp":False},tol=self.tol) # Minimizing
    #             Xres,success,msg=res.x,res.success,res.message
    #             self.bubbles[id].pos(np.array(Xres))
    #             self.bubbles[id].placed=True
    #             self.bubbles[id].placeChildren(self.bubbles)

    # Fitness function
    def energy (self,X,msg=''):
        E_edges,E_bypass,E_bubbles,E_terrain=0,0,0,0
        
        # targetLength=20
        for id in self.bubbles:
            xi,yi=self.bubbles[id].checkConstraints(X=X)
            E_terrain+=-self.width**2/((xi)**2-(self.width/2)**2)
            E_terrain+=-self.height**2/((yi)**2-(self.height/2)**2)
            # i=[self.bubbles[id].xIndex,self.bubbles[id].yIndex]
            # bubbles[i].pos(X[2*i:2*i+2])
            if id==0:
                for id2 in self.bubbles:
                    xj,yj=self.bubbles[id2].checkConstraints(X=X)
                    E_bubbles+=max(0,yj-yi+2*self.bubbles[id].b)**2#+max(0,xi-xj)
            for id2 in self.bubbles:
                xj,yj=self.bubbles[id2].checkConstraints(X=X)
                # j=[self.bubbles[id2].xIndex,self.bubbles[id2].yIndex]
                if id!=id2 :
                    E_bubbles+=self.bubbles[id2].potential(xi,yi,x2=xj,y2=yj,tl=self.targetLength,A=self.amplitude,range=self.range,func=self.bubblePotFunc) #max=1000
            edgesNb=len(self.bubbles[id].edges)
            for e in self.bubbles[id].edges.values() :
                xj,yj=self.bubbles[e.toid].checkConstraints(X=X)
                # j=[self.bubbles[e.toid].xIndex,self.bubbles[e.toid].yIndex]
                [P0,P1,P2,P3]=e.computePoints(X,self.bubbles,method='')

                l=lengthBezier(P0,P1,P2,P3,20)-self.targetLength/4
                if not e.long :
                    E_edges+=self.edgeLengthCoef*(l**2-self.targetLength**2) #max=100,000 moy=1000
                    E_bubbles+=self.hierarchyCoef*max(0,(yj-yi+20)/edgesNb) #max=200
                else :
                    E_edges+=self.edgeLengthCoef/2*(abs(l)-self.targetLength) #max=100,000 moy=1000

                if l > self.targetLength/2 :
                    for k,t in enumerate([0.25,0.5,0.75]):
                        P=Bezier(t,P0,P1,P2,P3)
                        for id2 in self.bubbles:
                            if not id==id2 and id2==e.toid:
                                xj,yj=self.bubbles[id2].checkConstraints(X=X)
                                # j=[self.bubbles[id2].xIndex,self.bubbles[id2].yIndex]
                                E_bypass+=self.bypassCoef*self.bubbles[id2].potential(P[0],P[1],x2=xj,y2=yj,tl=self.targetLength,A=self.amplitude,range=self.range,func=self.bubblePotFunc) #max=10
        E=E_edges+E_bypass+E_bubbles+E_terrain
        if msg or self.funcEval%10000==0 :
            print(bool(self.t0)*("Thread "+str(self.threadId)+" : "+prettyTime(time()-self.t0)+" |"),"Eval=",self.funcEval,"|",msg+"E_tot= %.1f"%E," E_ed= %.1f"%E_edges," E_by= %.1f"%E_bypass," E_bub= %.1f"%E_bubbles," E_ter= %.1f"%E_terrain)
        self.funcEval+=1
        return E

    # Runs an optimizing algorithm to optimize the mindmap
    def optimize (self,maxiter=100000,video=False):
        self.frame=0
        self.energy(self.X0,"Initial ")
        for bub in self.bubbles.values():
            if bub.mindmap :
                bub.mindmap.optimize(200)
        bounds=[(-self.width/2,self.width/2),(-self.height/2,self.height/2)]*(self.N)+[(None,None),(0,None),(0,None),(None,None)]*((len(self.X0)-2*self.N)//4)
        def callback(Xk):
            self.iter+=1
            if video and self.iter%100==0:
                self.frame+=1
                self.makeFrame(Xk,self.frame)
        res=minimize(self.energy,self.X0,callback=callback,bounds=None,options={"maxiter":maxiter,"disp":True},constraints=(),tol=self.tol) # Minimizing method="Nelder-Mead"
        self.Xres,success,msg=res.x,res.success,res.message
        print("Success :",success,"|",msg)
        self.energy(self.Xres,"Final ")
        if self.constraints==[] :
            bary=barycenter(self.Xres,self.N)
            for i in range(0,2*self.N,2):
                self.Xres[i]-=bary[0]
                self.Xres[i+1]-=bary[1]
            # print("Xres = ",self.Xres)
        self.place(self.Xres)
        self.saveOpti()

  

    def makeFrame(self,Xk,frame):
        frameSVG=draw.Drawing(self.height, self.width, origin='center', displayInline=False)
        frameSVG.draw(draw.Rectangle(-self.width/2,-self.height/2,self.width,self.height,fill=self.bgColor))
        self.place(Xk)
        self.draw(frameSVG)
        frameSVG.saveSvg("mindmaps/"+self.name+"/video/"+self.title+'_frame'+str(frame)+'.svg')

    # Places objects
    def place (self,X):
        for id in self.bubbles:
            self.bubbles[id].place(X,self.bubbles,self.origin,self.scale)

    # Draws objects
    def draw (self,img):
        for bub in self.bubbles.values() :
            bub.draw(img,self.scale)

    def setThreadId (self,threadId):
        self.threadId=threadId

    def saveOpti (self):
        fileName="mindmaps/"+self.name+"/cache/"+self.name+"_save"
        if os.path.isfile(fileName+".json") :
            os.rename(fileName+".json",fileName+"_old.json")
        f=open(fileName+".json",'w')
        posDict={}
        for bub in self.bubbles.values():
            x,y=bub.checkConstraints(X=self.Xres)
            posDict[bub.id]={"x":x,"y":y,"edges":{}}
            for e in bub.edges.values():
                posDict[bub.id]["edges"][e.toid]=list(self.Xres[e.index:e.index+4])
        # print(posDict)
        json.dump(posDict,f,indent=2)
