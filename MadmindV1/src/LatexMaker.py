import latextools
from utils import *

class LatexMaker ():
    def __init__(self,commandsFile=None) -> None:
        self.config=latextools.DocumentConfig('standalone',('varwidth','border=1pt'))
        self.packages=[latextools.LatexPackage("xcolor"),latextools.LatexPackage("fontenc",options=["T1"])]
        self.commands=[latextools.cmd.all_math]
        self.customCommands=""
        if commandsFile :
            commandsDict=json2dict(commandsFile)
            for name in commandsDict:
                self.commands.append(latextools.LatexCommand(name,eval("r"+"'"+commandsDict[name]+"'")))
                self.customCommands+=commandsDict[name]
        
    def makeLatexCode (self,lines,special=False):
        latexCode=""
        if '' in lines:
            lines.remove('')
        if len(lines)>0:
            flSize=" "
            subTextSize=" "
            latexCode="\centering \n "
            words=lines[0].split(' ')
            if special:
                flStyle="\\textsc{\\textbf{"
            else :
                flStyle="\\textsc{\\textbf{"
            if len(words)>=4:
                if len(lines)==1 or (max([len(l) for l in lines[1:]]) <=len(words)*10):
                    ind=ceil(len(words)/2)
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
                if lines[i][0]=='$'and lines[i][1]!='$':
                    lines[i]='$\displaystyle '+lines[i][1:]
                latexCode+=lines[i]
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
                