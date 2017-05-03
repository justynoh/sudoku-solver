'''
This file contains helper functions that allow for processing of the puzzle
after it has been detected, to allow the user to select the puzzle bounds.
'''

import math
import numpy as np
import cv2

def classify(lines):
    '''
    Params:
        lines - np array; detected lines represented in their normal form.
    Returns:
        Two lists, each containing tuples representing lines in their normal
        form, one of which is positive-gradient lines and the other, negative-
        gradient lines.
    '''
    pos,neg=[],[]
    for i in range(lines.shape[0]):
        p,theta=lines[i][0][0],lines[i][0][1]
        # Positive lines have theta>pi/2.
        if theta>math.pi/2: pos.append((p,theta))
        else: neg.append((p,theta))
    return pos,neg

def rotationAngle(horz,vert):
    '''
    Params:
        horz - list; grid's horizontal lines represented in their normal form.
        vert - list; grid's vertical lines represented in their normal form.
    Returns:
        The rotation angle in radians to allow the grid to be rotated upright.
    '''
    thetas=[]
    for p,theta in horz:thetas.append(abs((math.pi/2)-theta))
    for p,theta in vert:thetas.append((math.pi/2)-abs(theta-math.pi/2))
    thetas.sort()
    # Remove top 10% and bottom 10% of outliers.
    toremove=len(thetas)//10
    thetas=thetas[toremove:-toremove]
    angle=sum(thetas)/len(thetas)
    return angle

def getRotationAngle(lines):
    '''
    Params:
        lines - np array; detected lines represented in their normal form.
    Returns:
        The rotation angle in degrees to allow the grid to be rotated upright.
    '''
    pos,neg=classify(lines)
    if math.tan(pos[0][1]-(math.pi/2))<1: # Positives are horizontal.
        angle=rotationAngle(pos,neg)
    else: # Negatives are horizontal.
        angle=-rotationAngle(neg,pos)
    angle=angle*(180/math.pi)
    return angle

def gridProcess(croi,lines):
    '''
    Params:
        croi - np array; colored region of image within the bounding box.
        lines - np array; detected lines represented in their normal form.
    Returns:
        An np array representing the croi, properly scaled and rotated such that
        all of the croi is visible and the grid is upright.
    '''
    rotangle=getRotationAngle(lines)
    scale=1/(abs(math.cos(rotangle*math.pi/180))+
             abs(math.sin(rotangle*math.pi/180)))
    rotmatrix=cv2.getRotationMatrix2D((croi.shape[0]/2,croi.shape[1]/2),
                                        rotangle,scale)
    rotated=cv2.warpAffine(croi,rotmatrix,(croi.shape[0],croi.shape[1]))
    return rotated
