import threading
from LatexMaker import LatexMaker
from ui import userDialog
from utils import *
from Mindmap import Mindmap

VERSION=1.0
POTPARAMS="settings/potParams.json"
VIDEOPARAMS="settings/videoParams.json"
LATEXCOMMANDS="settings/latexCommands.json"


old=""
loop,mmName=userDialog(VERSION)
os.system("code ./mindmaps/"+mmName+"/"+mmName+'.txt '+LATEXCOMMANDS+" "+POTPARAMS+" "+VIDEOPARAMS)

#################################
# Main loop #####################
#################################
while loop :
    with open("mindmaps/"+mmName+"/"+mmName+'.txt','r') as f :
        contents=f.readlines()
        f.close()
    if contents and old != contents :
        video=json2dict(VIDEOPARAMS)["makeVideo"]
        latexMaker=LatexMaker(LATEXCOMMANDS)
        t0=time()
        print("\nStarting mindmap creation.")
        old=contents

        ### Headers ###
        headers=contents
        i=0
        while headers[i][0]=="|" :
            title=headers[0].split(':')[1].replace("\n",'').replace(' ','')
            mapHeight=int(headers[1].split(':')[1])
            mapWidth=int(headers[2].split(':')[1])
            bgColor=headers[3].split(':')[1]
            optimize=headers[4].split(':')[1].replace(' ','').replace('\n','')
            i+=1

        ### Makes mindmap ###

        # Defines master mindmap
        MM=Mindmap(mmName,contents,json2dict(POTPARAMS),latexMaker=latexMaker,t0=t0)
        print("Total number of bubbles :",MM.countBubbles())
        # Draws initial svg
        initSVG = draw.Drawing(mapHeight, mapWidth, origin='center', displayInline=False)
        initSVG.draw(draw.Rectangle(-mapWidth/2,-mapHeight/2,mapWidth,mapHeight,fill=bgColor))
        MM.draw(initSVG)
        initSVG.saveSvg("mindmaps/"+mmName+"/"+title+'_init.svg')
        print("Initial mindmap svg drawn and saved as mindmaps/"+mmName+"/"+title+'_init.svg')
        print("Opening initial svg.")
        os.system("eog "+"mindmaps/"+mmName+"/"+title+'_init.svg &')

        # Smart svg
        # smartSVG = draw.Drawing(mapHeight, mapWidth, origin='center', displayInline=False)
        # smartSVG.draw(draw.Rectangle(-mapWidth/2,-mapHeight/2,mapWidth,mapHeight,fill=bgColor))
        # MM.smartOpti()
        # MM.draw(smartSVG)
        # smartSVG.saveSvg("mindmaps/"+mmName+"/"+title+'_smart.svg')
        # print("Smart mindmap svg drawn and saved as mindmaps/"+mmName+"/"+title+'_smart.svg')


        # Optimize svg
        def runOptimization (threadId=None):
            sleep(0.1)
            print("Optimizing...\n")
            MM.setThreadId(threadId)
            optiSVG = draw.Drawing(mapHeight, mapWidth, origin='center', displayInline=False)
            optiSVG.draw(draw.Rectangle(-mapWidth/2,-mapHeight/2,mapWidth,mapHeight,fill=bgColor))
            MM.optimize(video=video)
            MM.draw(optiSVG)
            optiSVG.saveSvg("mindmaps/"+mmName+"/"+title+'.svg')
            print("Optimized mindmap svg drawn and saved as mindmaps/"+mmName+"/"+title+".svg")
            print("\x1b[33mTime : "+prettyTime(time()-t0)+"\033[0m")
        # if threading.active_count() ==1 and optimize in ["yes","y","Yes",'Y',"YES","true","True","1"] :
        #     id=str(threading.active_count())
        #     trd=threading.Thread(target=runOptimization,name=id,args=[id])
        #     trd.start()
        if optimize in ["yes","y","Yes",'Y',"YES","true","True","1"] :
            runOptimization()

        t=time()-t0
        print("\x1b[33mTime : "+prettyTime(t)+"\033[0m")
        print("Done.")
        # print("Opening svg.")
        # os.system("eog "+"mindmaps/"+mmName+"/"+title+'.svg')

    sleep(1)