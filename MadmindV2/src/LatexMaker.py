import latextools
import re
from utils import *

class LatexMaker ():
    def __init__(self,commandsFile=None) -> None:
        self.config=latextools.DocumentConfig('standalone',('varwidth','border=1pt'))
        self.packages=[latextools.LatexPackage("xcolor"),latextools.LatexPackage("bm"),latextools.LatexPackage("fontenc",options=["T1"])]#,latextools.LatexPackage("lmodern")
        self.commands=[latextools.cmd.all_math]
        self.customCommands=""
        if commandsFile :
            commandsDict=json2dict(commandsFile)
            for name in commandsDict:
                self.commands.append(latextools.LatexCommand(name,eval("r"+"'"+commandsDict[name]+"'")))
                self.customCommands+=commandsDict[name]
        
    def makeLatexCode (self,lines,special=False):
        latexCode=""
        while len(lines)>0 and lines[-1]=='':
            del(lines[-1])
        if len(lines)>0:
            subTextSize=" "
            latexCode="\centering  \n "
            # First line style
            flSize=" "
            if special: flStyle="\\textsc{\\textbf{"
            else : flStyle="\\textsc{\\textbf{"
            # Words
            words=lines[0].split(' ')
            wordsNb=len(words)
            wordsNb+=lines[0].count('-')
            if wordsNb>=4:
                if len(lines)==1 or (max([len(l) for l in lines[1:]]) <=wordsNb*10):
                    ind=ceil(wordsNb/2)
                    latexCode+=flSize+flStyle+' '.join(words[:ind])+"\\\\ "+' '.join(words[ind:])+"}"*flStyle.count("{")
                    subTextSize=''
                else :
                    # flSize=" "
                    latexCode+=flSize+flStyle+lines[0]+"}"*flStyle.count("{")
            else :
                latexCode+=flSize+flStyle+lines[0]+"}"*flStyle.count("{")
            if len(lines)>1:
                latexCode+="\\vspace{2pt"+"} "
            newline=True
            for i in range (1,len(lines)) :
                if "\\begin{tabular" in lines[i]:
                    newline=False
                latexCode+=newline*("\\newline "+subTextSize)
                try:
                    if lines[i][0]=='$'and lines[i][1]!='$':
                        lines[i]='$\displaystyle '+lines[i][1:]
                    latexCode+=lines[i]
                except :
                    print("i=",i,"len(lines)=",len(lines),"lines=",lines)
        return latexCode

    def makeSnippet(self,latexCode):
        latexCode=self.customCommands+" "+latexCode
        return latextools.render_snippet(latexCode,*self.packages,commands=[latextools.cmd.all_math],config=self.config)

    def makeLatexSvg (self,lines,special=False):
        if len(lines)==0 or (len(lines)==1 and lines[0] in ['','\n',' ']):
            return None
        else :
            try :
                snippet=self.makeSnippet(self.makeLatexCode(lines,special))
                return snippet.as_svg()
            except Exception as e:
                print("Latex error : ",e)

    def makePdf(self,lines,outName,special=False):
        self.makeSnippet(self.makeLatexCode(lines,special)).save(outName)

    def saveSvgAsPng(self,svg,outName):
        svg.rasterize(to_file=outName)
                
