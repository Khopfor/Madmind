import numpy as np
from math import ceil
from time import sleep,time
import os
from io import BytesIO
from latex import build_pdf
from matplotlib import lines
from pdf2image import convert_from_path
import drawSvg as draw
from glob import glob
import json


def pixBary (p1,p2):
    return [(p1[0]+p2[0])//2,(p1[1]+p2[1])//2]

def barycenter (X,N):
    xBary=0
    yBary=0
    for i in range (N):
        xBary+=X[2*i]
        yBary+=X[2*i+1]
    return [xBary/N,yBary/N]
    

def Bezier(t,P0,P1,P2,P3) :
    return P0*(1-t)**3+3*P1*t*(1-t)**2+3*P2*t*t*(1-t)+P3*t**3

def lengthCurve (f,a,b,N=100):
    s=0
    dx=(b-a)/N
    for i in range (1,N):
        s+=np.sqrt((f(i*dx)-f((i-1)*dx))**2+dx**2)
    return s

def lengthBezier(P0,P1,P2,P3,N=24):
    s=0
    P=Bezier(0,P0,P1,P2,P3)
    for t in np.linspace(0+1/N,1,N):
        nextP=Bezier(t,P0,P1,P2,P3)
        s+=np.linalg.norm(nextP-P)
        P=nextP
    # print(s)
    return s

def contains (str,*args):
    b=False
    for a in args :
        b= b or (a in str)
    return b

def prettyTime (t):
    return str(int(t//60))+" min "+str(int(t%60))+" sec"

def json2dict (jsonFile):
    s=open(jsonFile,'r').read()
    return json.loads(s)

def cleanStr (s,*toRemove):
    bl=[' ','\n']+toRemove
    newS=''
    for i in range(len(s)):
        if s[i] not in bl:
            newS+=s[i]
    return newS

# print(contains("aymeric","dfd","qs","aytge"))

# P0=np.array([0,0])
# P1=np.array([100,100])
# P2=np.array([200,100])
# P3=np.array([300,000])
# print(Bezier(0,P0,P1,P2,P3))
# print(Bezier(0.5,P0,P1,P2,P3))
# print(Bezier(1,P0,P1,P2,P3))
# print(lengthBezier(P0,P1,P2,P3))