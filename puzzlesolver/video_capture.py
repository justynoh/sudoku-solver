'''
This file contains helper functions that allow for processing of the detected
images from the webcam. It allows the application to draw on the frames, and
detect lines and grids.
'''
import math
import numpy as np
import cv2
import copy

def getLines(frame,grey,bounds):
    '''
    Params:
        frame - image; cv2 image.
        grey - image; cv2 image which is the greyscale version of frame.
        bounds - tuple; bounds of the grid roi.
    Returns:
        A list of tuples that represent the lines detected in normal form.
    '''
    x0,y0,x1,y1=bounds
    roi=grey[y0:y1,x0:x1]
    edges=cv2.Canny(roi,100,50,apertureSize=3)
    lines=cv2.HoughLines(edges,1,math.pi/180,7*(x1-x0)//24,np.array([]),0,0)
    return lines

def getLinePoints(lines,bounds):
    '''
    Params:
        lines - list; contains tuples that represent the lines detected in
                normal form.
        bounds - tuple; bounds of the grid roi.
    Returns:
        A list of tuples that represent the lines detected based on two points
        that lie on them.
    '''
    x0,y0,x1,y1=bounds
    linepoints=[]
    if lines is not None:
        for i in range(lines.shape[0]):
            rho,theta=lines[i][0][0],lines[i][0][1]
            # Point where perpendicular from origin intersects line.
            Ox,Oy=rho*math.cos(theta),rho*math.sin(theta)
            lx0=int(Ox+(x1-x0)*(-math.sin(theta)))
            ly0=int(Oy+(y1-y0)*(math.cos(theta)))
            lx1=int(Ox-(x1-x0)*(-math.sin(theta)))
            ly1=int(Oy-(y1-y0)*(math.cos(theta)))
            linepoints.append((lx0,ly0,lx1,ly1))
    return linepoints

def fuseNearbyLines(frame,grey,bounds,linepoints):
    '''
    Params:
        frame - image; cv2 image.
        grey - image; cv2 image which is the greyscale version of frame.
        bounds - tuple; bounds of the grid roi.
        linepoints - list; contains tuples that represent the lines detected by
                     two points on each line.
    Returns:
        A list of tuples that represent the lines detected in gradient-intercept
        form. Also combined lines with similar gradients and intercepts.
    '''
    x0,y0,x1,y1=bounds
    thresh=(x1-x0)//600
    croi=frame[y0:y1,x0:x1]
    newlinepoints,linemc=[],[]
    for lx0,ly0,lx1,ly1 in linepoints:
        mod=False
        for nx0,ny0,nx1,ny1 in newlinepoints:
            if (abs(nx0-lx0)<thresh or abs(nx1-lx1)<thresh or
                abs(ny0-ly0)<thresh or abs(ny1-ly1)<thresh):
                nx0,ny0=(nx0+lx0)//2,(ny0+ly0)//2
                nx1,ny1=(nx1+lx1)//2,(ny1+ly1)//2
                mod=True
        if not mod: newlinepoints.append((lx0,ly0,lx1,ly1))
    for nx0,ny0,nx1,ny1 in newlinepoints:
        cv2.line(croi,(nx0,ny0),(nx1,ny1),(0,0,255),2)
        m=10**6 if abs(nx1-nx0)<10**-6 else (ny1-ny0)/(nx1-nx0)
        c=ny1-m*nx0
        linemc.append((m,c))
    return linemc

def checkGrid(bounds,linemc,n):
    '''
    Params:
        bounds - tuple; bounds of the grid roi.
        linemc - list; contains tuples that represent the lines detected in
                 gradient-intercept form.
        n - int; order of the puzzle.
    Returns:
        True if a grid is detected, False otherwise.
    '''
    x0,y0,x1,y1=bounds
    comparisons=len(linemc)*(len(linemc)-1)//2
    perp=0
    if comparisons<20*(n**2) or comparisons>70*(n**2):return False
    for idx1 in range(len(linemc)):
        for idx2 in range(idx1,len(linemc)):
            m1,c1=linemc[idx1];m2,c2=linemc[idx2]
            if abs(m1*m2+1)<10:perp+=1
    if comparisons>0 and perp/comparisons>0.75:return True
    return False

def drawPuzzleBoundingFrame(frame,height,width):
    '''
    Params:
        frame - image; cv2 image.
        height - int; height of frame.
        width - int; width of frame.
    Returns:
        Tuple containing the bounds of the roi for which the user is asked to
        place the grid in. Also modifies frame to draw the white bounding box as
        a visual aid to the user.
    '''
    boundsdim=min(height,width)
    l,w,color=boundsdim//10,5,(255,255,255)
    x0=(width-boundsdim)//2+w*int(width<=height)
    y0=(height-boundsdim)//2+w*int(width>=height)
    x1=width-x0-w*int(width<=height)
    y1=height-y0-w*int(width>=height)
    cv2.line(frame,(x0,y0),(x0+l,y0),color,w)
    cv2.line(frame,(x0,y0),(x0,y0+l),color,w)
    cv2.line(frame,(x1-l,y0),(x1,y0),color,w)
    cv2.line(frame,(x1,y0),(x1,y0+l),color,w)
    cv2.line(frame,(x0,y1),(x0+l,y1),color,w)
    cv2.line(frame,(x0,y1-l),(x0,y1),color,w)
    cv2.line(frame,(x1,y1-l),(x1,y1),color,w)
    cv2.line(frame,(x1-l,y1),(x1,y1),color,w)
    return (x0,y0,x1,y1)

def capture(frame,n):
    '''
    Params:
        frame - numpy array; cv2 image.
        n - int; order of the puzzle.
    Returns:
        frame - numpy array; cv2 image.
        annotated - numpy array; cv2 image with annotations of lines detected.
        croi - numpy array if grid detected, None otherwise.
        lines - numpy array; lines detected in normal form.
    '''
    annotated=copy.deepcopy(frame)
    grey=cv2.cvtColor(annotated,cv2.COLOR_BGR2GRAY)
    height,width=grey.shape
    bounds=drawPuzzleBoundingFrame(annotated,height,width)
    lines=getLines(annotated,grey,bounds)
    linepoints=getLinePoints(lines,bounds)
    linemc=fuseNearbyLines(annotated,grey,bounds,linepoints)
    isGrid=checkGrid(bounds,linemc,n)
    if isGrid: croi=frame[bounds[1]:bounds[3],bounds[0]:bounds[2]]
    else: croi=None
    return frame,annotated,croi,lines
