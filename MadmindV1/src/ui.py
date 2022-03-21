from utils import *

def userDialog (VERSION):
    loop=False
    print("\n\x1b[36m=====================================================================")
    print(" \x1b[37mMINDMAP GENERATOR  Version "+str(VERSION))
    print(" \x1b[35mAymeric Braud    2022")
    print("\x1b[36m=====================================================================\033[0m\n")



    print("Available mindmaps : ")
    mindmaps=os.listdir("mindmaps")
    for i in range(len(mindmaps)) :
        print("   "+str(i)+")",mindmaps[i])
    action=input("\nChoose a mindmap or enter 'new <name>' to create a new one : ")
    if action=='':
        name='test'
        loop=True
    elif action.isdigit() :
        name=mindmaps[int(action)]
        loop=True
    elif 'new' in action :
        name=action.split(' ')[1]
        if name in mindmaps :
            print("Name '",name,"'already exists")
        else :
            os.mkdir("mindmaps/"+name)
            os.mkdir("mindmaps/"+name+"/cache")
            os.mkdir("mindmaps/"+name+"/video")
            f=open("mindmaps/"+name+"/"+name+".txt","w")
            h=open("templates/headers.txt","r")
            f.write(h.read())
            h.close()
            f.close()
            os.system("gedit "+name+".txt")
            loop=True
    else :
        if action in mindmaps :
            name=action
            loop=True
        else :
            print("Invalid entry :",action)
    return loop,name