'''
This file draws the background for the application in Tkinter.
'''
from tkinter import *
from PIL import Image,ImageTk

import os
import random
import math
import string

def initImages(data):
    '''
    Params:
        data - object; stores data for the user interface of the application.
    Returns:
        None, stores the background images data into the data object.
    '''
    data.bgimagesize=150
    imgpath='./img'
    if '.DS_Store' in os.listdir(imgpath): os.remove(imgpath+"/.DS_Store")
    imagenames=os.listdir(imgpath)
    data.images=[]
    for img in imagenames:
        if not (img.endswith('.jpg') or img.endswith('.jpeg') or
                img.endswith('.png') or img.endswith('gif')):continue
        image=Image.open((imgpath+'/%s')%(img))
        image=image.resize((data.bgimagesize,data.bgimagesize),Image.ANTIALIAS)
        data.images.append(ImageTk.PhotoImage(image=image))
    data.imagepositions,data.imagedirs=[],[]
    for i in range(len(data.images)):
        data.imagepositions.append(
            (random.randint(data.bgimagesize+1,data.width-data.bgimagesize-1),
             random.randint(data.bgimagesize+1,data.height-data.bgimagesize-1)))
        x,y=0,0
        while math.isclose(x,0) or math.isclose(y,0):
            x,y=random.uniform(-0.95,0.95),random.uniform(-0.95,0.95)
        data.imagedirs.append((x,y))

def updateImagePositions(data,i):
    '''
    Params:
        data - object; stores data for the user interface of the application.
        i - int; index of image whose position is to be updated.
    Returns:
        None, changes the positions of the image on the canvas based on the
        parameters decided in initImages().
    '''
    speed=5
    dx,dy=data.imagedirs[i]
    dxn,dyn=round(speed*dx),round(speed*dy)
    x,y=data.imagepositions[i]
    xn,yn=x+dxn,y+dyn
    data.imagepositions[i]=(xn,yn)
    if xn<=data.bgimagesize//2 or xn>=data.width-data.bgimagesize//2: dx=-dx
    if yn<=data.bgimagesize//2 or yn>=data.height-data.bgimagesize//2: dy=-dy
    data.imagedirs[i]=(dx,dy)

def redrawBackground(canvas,data):
    '''
    Params:
        canvas - tk object; canvas to draw the user interface in.
        data - object; stores data for the user interface of the application.
    Returns:
        None, draws the background images into the background of the user
        interface in the home screen.
    '''
    if data.mode==1:
        for i in range(len(data.images)):
            updateImagePositions(data,i)
            canvas.create_image(data.imagepositions[i],image=data.images[i])
