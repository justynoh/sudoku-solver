'''
This file contains functions for the main user interface of the application. It
allows the user to interact with the application in an effective but meaningful
way.

The framework for this file was taken from the CMU 15-112 TA-led lecture code
and modified extensively, with major modifications made to the run() function,
combining the Tk and the cv2 window, as well as controlling when the cv2 images
can be detected, converting them into a format which that Tk canvas can read and
fitting them into the Tk canvas.
'''
from tkinter import *
from PIL import Image,ImageTk
from puzzlesolver.video_capture import *
from puzzlesolver.grid_processing import *
from puzzlesolver.read_sudoku import *
from puzzlesolver.solve_sudoku import *
from puzzlesolver.retrain_model import *
from puzzlesolver.redraw_background import *
from puzzlesolver.steps_explainer import *

import cv2
import copy
import string

'''
MODES LIST
0 Help Screen
1 Home Screen
2 Puzzle Selection Screen

SUDOKU
3 Puzzle Detection Screen (Webcam)
4 Boundary Selection Screen 1
5 Boundary Selection Screen 2
6 Confirmation Screen
7 Solution Screen
8 Steps Viewer
'''

'''-----------------------------------------------------------------------------
----------------------------------BUTTON CLASS----------------------------------
-----------------------------------------------------------------------------'''

class Button(object):
    def __init__(self,x0,y0,x1,y1,**kwargs):
        '''
        Params:
            x0,y0,x1,y1 - ints; values for x- and y-values of top-left corner of
                          button and x- and y- values of bottom-right corner of
                          button respectively.
            [text] - str; text to be printed in the button.
            [font] - str; font for [text] to be printed in, in standard Tk form.
        Returns:
            None.
        '''
        self.x0=min(x0,x1)
        self.y0=min(y0,y1)
        self.x1=max(x0,x1)
        self.y1=max(y0,y1)
        self.text=kwargs.get('text',None)
        self.font=kwargs.get('font','Arial 20')

    def draw(self,canvas):
        '''
        Params:
            canvas - Tk Canvas; window on which to draw the button.
        Returns:
            None.
        '''
        canvas.create_rectangle(self.x0,self.y0,self.x1,self.y1,
                                fill='grey',outline='black',width=2)
        canvas.create_text((self.x0+self.x1)//2,(self.y0+self.y1)//2,
                           text=self.text,font=self.font)

    def clicked(self,event):
        '''
        Params:
            event - Tk Event; contains event data for handling.
        Returns:
            True if the event contains a mouse click in the button, False
            otherwise.
        '''
        if (self.x0<event.x and event.x<self.x1 and self.y0<event.y
            and event.y<self.y1): return True
        return False

'''-----------------------------------------------------------------------------
-----------------------------MODE 0:HELP SCREEN--------------------------------
-----------------------------------------------------------------------------'''

def init0(data):
    data.textx0=data.xoffset
    data.texty0=data.yoffset
    data.textx1=data.width-data.xoffset
    data.texty1=data.height-data.yoffset
    data.helpx=data.width//2
    data.helpy=data.yoffset//2
    data.buttonwidth=2*data.xoffset
    data.returnButton=Button(data.xoffset,data.height-(3*data.yoffset//4),
                            data.xoffset+data.width//5,data.height-
                            (3*data.yoffset//4)+(data.yoffset//2),
                             text="Return")

    data.helptext='''Welcome to PuzzleSolver! Whether you are an avid puzzle
solver yourself or a newbie to puzzle-solving, we hope you'll
find this application useful.

The goal of PuzzleSolver is to solve the puzzles you give it.
To use PuzzleSolver, simply pick the type of puzzle you
want to solve, then hold the puzzle up to the camera on
your device. When PuzzleSolver detects your puzzle, it will
give you the solution to your puzzle.

Enjoy!'''

def keyPressed0(event,data):
    pass

def mousePressed0(event,data):
    if data.returnButton.clicked(event):
        data.mode=1
        initDispatch(data)

def timerFired0(data):
    pass

def redrawAll0(canvas,data):
    canvas.create_text(data.helpx,data.helpy,text="PuzzleSolver Help",font=
                       "Arial 30 bold")
    canvas.create_rectangle(data.textx0,data.texty0,data.textx1,data.texty1,
                            outline='black',width=2)
    canvas.create_text((data.textx0+data.textx1)//2,(data.texty0+data.texty1)//2
                       ,text=data.helptext,font="Arial 20",justify='left')
    data.returnButton.draw(canvas)

'''-----------------------------------------------------------------------------
-----------------------------MODE 1: HOME SCREEN--------------------------------
-----------------------------------------------------------------------------'''

def init1(data):
    data.buttonwidth=data.width-2*data.xoffset
    data.buttonheight=data.height//12
    data.solveButton=Button(data.xoffset,data.height//2,data.xoffset+
                            data.buttonwidth,data.height//2+data.buttonheight,
                            text="Solve")
    data.helpButton=Button(data.xoffset,data.solveButton.y1+data.buttonheight,
                           data.xoffset+data.buttonwidth,data.solveButton.y1+
                           data.buttonheight+data.buttonheight,text="Help")
    data.exitButton=Button(data.xoffset,data.helpButton.y1+data.buttonheight,
                           data.xoffset+data.buttonwidth,data.helpButton.y1+
                           data.buttonheight+data.buttonheight,text="Exit")

def keyPressed1(event,data):
    pass

def mousePressed1(event,data):
    if data.solveButton.clicked(event):
        data.mode=2
        initDispatch(data)
    elif data.helpButton.clicked(event):
        data.mode=0
        initDispatch(data)
    elif data.exitButton.clicked(event):
        data.exit=True

def timerFired1(data):
    pass

def redrawAll1(canvas,data):
    canvas.create_rectangle(data.width//2-160,data.height//4-30,data.width//2
                            +160,data.height//4+30,fill='pink',width=2)
    canvas.create_text(data.width//2,data.height//4,text="PuzzleSolver",
                       font="Arial 50 bold")
    canvas.create_rectangle(data.width//2-130,data.height//4+55,data.width//2
                            +130,data.height//4+95,fill='pink',width=2)
    canvas.create_text(data.width//2,data.height//4+75,
                       text="Click 'Solve' to start solving!",font="Arial 20")
    data.solveButton.draw(canvas)
    data.helpButton.draw(canvas)
    data.exitButton.draw(canvas)


'''-----------------------------------------------------------------------------
----------------------MODE 2: PUZZLE SELECTION SCREEN---------------------------
-----------------------------------------------------------------------------
'''

def init2(data):
    data.numpuzzles=len(data.puzzles)
    data.buttongap=(data.height-data.yoffset)//(3*(data.numpuzzles+1)+1)
    data.buttonheight=2*data.buttongap
    data.buttontotal=data.buttongap+data.buttonheight
    data.buttonx0=data.width//10
    data.buttonx1=data.width-data.buttonx0
    data.headerheight=2*data.buttongap+data.buttonheight
    data.puzzleButtons=dict()
    for idx,puzzle in enumerate(data.puzzles):
        data.buttony0=data.headerheight+(idx*data.buttontotal)
        data.buttony1=data.buttony0+data.buttonheight
        data.puzzleButtons[puzzle]=Button(data.buttonx0,data.buttony0,
                                          data.buttonx1,data.buttony1,
                                          text=puzzle)
    data.returnButton=Button(data.xoffset,data.height-(3*data.yoffset//4),
                            data.xoffset+data.width//5,data.height-
                            (3*data.yoffset//4)+(data.yoffset//2),
                             text="Return")


def keyPressed2(event,data):
    pass

def mousePressed2(event,data):
    if data.returnButton.clicked(event):
        data.mode=1
        initDispatch(data)
    for puzzle in data.puzzleButtons.keys():
        if data.puzzleButtons[puzzle].clicked(event):
            data.puzzle=puzzle
            data.n=round(int(puzzle[-1])**0.5)
            data.numsize=180//(data.n**2)
            data.mode=3
            initDispatch(data)

def timerFired2(data):
    pass

def redrawAll2(canvas,data):
    canvas.create_text(data.width//2,data.buttongap+data.buttonheight//2,
                       text="Select a puzzle",font="Arial 25")
    for puzzle in data.puzzleButtons.keys():
        data.puzzleButtons[puzzle].draw(canvas)
    data.returnButton.draw(canvas)

'''-----------------------------------------------------------------------------
----------------------MODE 3: PUZZLE DETECTION SCREEN---------------------------
-----------------------------------------------------------------------------'''

def init3(data):
    data.cap=cv2.VideoCapture(data.camera)
    data.webcamActive=True
    data.texty=(data.height-data.fheight)//4
    data.diff=20
    data.text='''To solve the puzzle, hold it up in the square marked by \
the white corners.'''
    data.returnButton=Button(data.xoffset,data.height-(3*data.yoffset//4),
                            data.xoffset+data.width//5,data.height-
                            (3*data.yoffset//4)+(data.yoffset//2),
                             text="Return")
    data.btext='''If your puzzle is on a digital device, please maximize
the brightness on your device for the best performance.'''

def keyPressed3(event,data):
    pass

def mousePressed3(event,data):
    if data.returnButton.clicked(event):
        data.mode=2
        data.webcamActive=False
        data.puzzle=None
        data.cap.release()
        initDispatch(data)

def timerFired3(data):
    pass

def redrawAll3(canvas,data):
    canvas.create_text(data.width//2,data.texty-data.diff,text="Puzzle: %s"%
                       (data.puzzle),font='Arial 30 bold')
    canvas.create_text(data.width//2,data.texty+data.diff,text=data.text,
                       font='Arial 20',justify='center')
    canvas.create_text(data.width//2,data.height-data.texty-data.diff,
                       text=data.btext,font='Arial 20',justify='center')
    data.returnButton.draw(canvas)

'''-----------------------------------------------------------------------------
----------------------MODE 4: BOUNDARY SELECTION SCREEN 1-----------------------
-----------------------------------------------------------------------------
'''

def init4(data):
    data.webcamActive=False
    data.texty=(data.height-data.fheight)//4
    data.diff=25
    data.questiontext='''Click the top-left corner of the grid boxes.
Press 'u' to undo your selection.'''
    data.nextButton=Button(data.width-data.xoffset-data.width//5,data.height-
                           (3*data.yoffset//4),data.width-data.xoffset,data.
                           height-(3*data.yoffset//4)+(data.yoffset//2),
                           text="Done")
    data.returnButton=Button(data.xoffset,data.height-(3*data.yoffset//4),
                            data.xoffset+data.width//5,data.height-
                            (3*data.yoffset//4)+(data.yoffset//2),
                             text="Return")
    data.btext=''

def keyPressed4(event,data):
    if event.keysym=='u' or event.keysym=='U':
        data.gridx0,data.gridy0=-1,-1

def mousePressed4(event,data):
    if (data.croix0<=event.x and event.x<=data.croix1 and data.croiy0<=event.y
        and event.y<=data.croiy1 and data.gridx0==-1 and data.gridy0==-1):
        data.gridx0=event.x-data.croix0
        data.gridy0=event.y-data.croiy0
        if data.btext!='':data.btext=''
    elif data.nextButton.clicked(event):
        if data.gridx0==-1 and data.gridy0==-1:
            data.btext='''No corner selected! Please try again.'''
        else:
            data.mode=5
            initDispatch(data)
    elif data.returnButton.clicked(event):
        data.mode=3
        initDispatch(data)

def timerFired4(data):
    pass

def redrawAll4(canvas,data):
    canvas.create_text(data.width//2,data.texty-data.diff,
                       text="Corner selection",font='Arial 30 bold')
    canvas.create_text(data.width//2,data.texty+data.diff,
                       text=data.questiontext,font='Arial 20',justify='center')
    canvas.create_text(data.width//2,data.height-data.texty-data.diff,
                       text=data.btext,font='Arial 20',justify='center')
    canvas.create_image(data.width//2,data.height//2,image=data.croi)
    if data.gridx0!=-1 and data.gridy0!=-1:
        canvas.create_oval(data.gridx0+data.croix0-5,data.gridy0+data.croiy0-5,
                           data.gridx0+data.croix0+5,data.gridy0+data.croiy0+5,
                           fill='red',width=1)
    data.nextButton.draw(canvas)
    data.returnButton.draw(canvas)

'''-----------------------------------------------------------------------------
----------------------MODE 5: BOUNDARY SELECTION SCREEN 2-----------------------
-----------------------------------------------------------------------------
'''

def init5(data):
    data.questiontext='''Click the bottom-right corner of the grid boxes.
Press 'u' to undo your selection.'''
    data.texty=(data.height-data.fheight)//4
    data.diff=25
    data.nextButton=Button(data.width-data.xoffset-data.width//5,data.height-
                           (3*data.yoffset//4),data.width-data.xoffset,data.
                           height-(3*data.yoffset//4)+(data.yoffset//2),
                           text="Done")
    data.returnButton=Button(data.xoffset,data.height-(3*data.yoffset//4),
                            data.xoffset+data.width//5,data.height-
                            (3*data.yoffset//4)+(data.yoffset//2),
                             text="Return")
    data.btext=''

def keyPressed5(event,data):
    if event.keysym=='u' or event.keysym=='U':
        if data.gridx1==-1 and data.gridy1==-1:
            data.gridx0,data.gridy0=-1,-1
            data.mode=4
            initDispatch(data)
        else:
            data.gridx1,data.gridy1=-1,-1
            data.btext=''

def mousePressed5(event,data):
    if (data.croix0<=event.x and event.x<=data.croix1 and data.croiy0<=event.y
        and event.y<=data.croiy1 and data.gridx1==-1 and data.gridy1==-1):
        if data.gridx0+data.croix0<event.x and data.gridy0+data.croiy0<event.y:
            data.gridx1=event.x-data.croix0
            data.gridy1=event.y-data.croiy0
            data.btext='''\
If you are sure that the box bounds the grid as
accurately as possible, click 'Done'.'''
        else:
            data.btext='''\
Bottom-right corner must be below and to the right
of top-left corner! Please try again.'''
    elif data.nextButton.clicked(event):
        if data.gridx1==-1 and data.gridy1==-1:
            data.btext='''No corner selected! Please try again.'''
        else:
            data.mode=6
            data.board=None
            initDispatch(data)
    elif data.returnButton.clicked(event):
        data.mode=4
        initDispatch(data)

def timerFired5(data):
    pass

def redrawAll5(canvas,data):
    canvas.create_text(data.width//2,data.texty-data.diff,
                       text="Corner selection",font='Arial 30 bold')
    canvas.create_text(data.width//2,data.texty+data.diff,
                       text=data.questiontext,font='Arial 20',justify='center')
    canvas.create_text(data.width//2,data.height-data.texty-data.diff,
                       text=data.btext,font='Arial 20',justify='center')
    canvas.create_image(data.width//2,data.height//2,image=data.croi)
    canvas.create_oval(data.gridx0+data.croix0-5,data.gridy0+data.croiy0-5,
                       data.gridx0+data.croix0+5,data.gridy0+data.croiy0+5,
                       fill='green',width=1)
    if data.gridx1!=-1 and data.gridy1!=-1:
        canvas.create_oval(data.gridx1+data.croix0-5,data.gridy1+data.croiy0-5,
                           data.gridx1+data.croix0+5,data.gridy1+data.croiy0+5,
                           fill='red',width=1)
        canvas.create_rectangle(data.gridx0+data.croix0,data.gridy0+data.croiy0,
                                data.gridx1+data.croix0,data.gridy1+data.croiy0,
                                fill=None,width=2,outline='red')
    data.nextButton.draw(canvas)
    data.returnButton.draw(canvas)

'''-----------------------------------------------------------------------------
--------------------------MODE 6: CONFIRMATION SCREEN---------------------------
-----------------------------------------------------------------------------
'''

def init6(data):
    data.webcamActive=False
    data.questiontext='''Please confirm that this is your puzzle.
If not, click on the cell you want to change and type the correct number.
Use the spacebar to change a filled cell to an empty cell.'''
    data.texty=(data.height-data.fheight)//4-15
    data.diff=30
    data.buttonwidth=(data.width//2)-(3*data.xoffset)//2
    data.yeButton=Button(data.width-data.xoffset-data.buttonwidth,data.height-
                         (3*data.yoffset//4),data.width-data.xoffset,data.
                         height-(3*data.yoffset//4)+(data.yoffset//2),
                         text="Done, I want the solution!")
    data.noButton=Button(data.xoffset,data.height-(3*data.yoffset//4),data.
                         xoffset+data.buttonwidth,data.height-(3*data.yoffset//
                         4)+(data.yoffset//2),text="No, take me back!")
    data.rawpuzzleimg=data.rawroi[data.gridy0:data.gridy1,
                                  data.gridx0:data.gridx1]
    data.rawpuzzleimg=cv2.resize(data.rawpuzzleimg,(data.croil,data.croil))
    if data.board is None:
        data.boardRawData,data.board=readSudoku(data.rawpuzzleimg,data.n)
    data.selected=(-1,-1)
    data.btext=''
    data.ye=False

def keyPressed6(event,data):
    if data.selected!=(-1,-1) and event.keysym in ['1','2','3','4','5',
                                                   '6','7','8','9','space']:
        row,col=data.selected
        if event.keysym in string.digits: data.board[row][col]=int(event.keysym)
        else: data.board[row][col]=0
        data.selected=(-1,-1)

def mousePressed6(event,data):
    if ((data.width//2)-(data.croil//2)<event.x and event.x<(data.width//2)+
        (data.croil//2) and (data.height//2)-(data.croil//2)<event.y and
        event.y<(data.height//2)+(data.croil//2)):
        xoff=(data.width-data.croil)//2
        yoff=(data.height-data.croil)//2
        length=data.croil//data.n**2
        clickx,clicky=event.x-xoff,event.y-yoff
        data.selected=(clicky//length,clickx//length)
        if (data.selected[0]<0 or data.selected[0]>=data.n**2 or
            data.selected[1]<0 or data.selected[1]>=data.n**2):
            data.selected(-1,-1)
    elif data.yeButton.clicked(event):
        data.btext='Solving... Please wait.'
        data.ye=True
    elif data.noButton.clicked(event):
        data.mode=5
        initDispatch(data)

def timerFired6(data):
    if data.ye:
        board=copy.deepcopy(data.board)
        data.solvedboard,data.steps=solveSudoku(board)
        if data.solvedboard is not None:
            retrainModel(data.boardRawData,data.board)
        data.mode=7
        initDispatch(data)

def drawDigitsSudoku6(canvas,data):
    xoff,yoff=(data.width-data.croil)//2,(data.height-data.croil)//2
    length=data.croil/data.n**2
    for row in range(len(data.board)):
        for col in range(len(data.board[row])):
            x0,y0=xoff+round(col*length),yoff+round(row*length)
            x1,y1=round(x0+length),round(y0+length)
            if data.selected==(row,col):
                canvas.create_rectangle(x0,y0,x1,y1,fill='yellow',width=None)
            if data.board[row][col]==0:continue
            canvas.create_text((x0+x1)//2,(y0+y1)//2,text=
                               str(data.board[row][col]),font='Arial %d'%
                               (data.numsize))

def drawBoundingLinesSudoku(canvas,data):
    l,Cx,Cy=data.croil,data.width//2,data.height//2
    x0,y0=Cx-l//2,Cy-l//2
    for n in range(data.n**2+1):
        w=5 if n%data.n==0 else 2
        canvas.create_line(x0+n*l//data.n**2,y0,x0+n*l//data.n**2,y0+l,width=w)
        canvas.create_line(x0,y0+n*l//data.n**2,x0+l,y0+n*l//data.n**2,width=w)

def drawBoardSudoku6(canvas,data):
    drawDigitsSudoku6(canvas,data)
    drawBoundingLinesSudoku(canvas,data)

def redrawAll6(canvas,data):
    canvas.create_text(data.width//2,data.texty-data.diff,
                       text="Puzzle confirmation",font='Arial 30 bold',
                       justify='center')
    canvas.create_text(data.width//2,data.texty+data.diff,text=data.questiontext
                       ,font='Arial 20',justify='center')
    canvas.create_text(data.width//2,(data.height-(3*data.yoffset//4)+
                       data.height//2+data.croil//2)//2,text=data.btext,
                       font='Arial 20',justify='center')
    drawBoardSudoku6(canvas,data)
    data.yeButton.draw(canvas)
    data.noButton.draw(canvas)

'''-----------------------------------------------------------------------------
----------------------------MODE 7: SOLUTION SCREEN-----------------------------
-----------------------------------------------------------------------------'''

def init7(data):
    data.texty=(data.height-data.fheight)//4
    data.diff=25
    data.buttonwidth=(data.width//2)-(3*data.xoffset)//2
    data.retButton=Button(data.xoffset,data.height-(3*data.yoffset//4),
                          data.xoffset+data.buttonwidth,data.height-
                          (3*data.yoffset//4)+(data.yoffset//2),
                          text="Return to main")
    if data.solvedboard is None:
        data.questiontext='''There was no solution to your puzzle!'''
        data.buttontext="Check my puzzle again"
    else:
        data.questiontext='''Here's the solution to your puzzle!'''
        data.buttontext="See solution steps"
    data.checkButton=Button(data.width-data.xoffset-data.buttonwidth,data.height
                            -(3*data.yoffset//4),data.width-data.xoffset,data.
                            height-(3*data.yoffset//4)+(data.yoffset//2),
                            text=data.buttontext)

def keyPressed7(event,data):
    pass

def mousePressed7(event,data):
    if data.checkButton.clicked(event):
        if data.solvedboard is None:
            data.mode=6
            initDispatch(data)
        else:
            data.mode=8
            initDispatch(data)
    elif data.retButton.clicked(event):
        data.mode=1
        initDispatch(data)

def timerFired7(data):
    pass

def drawDigitsSudoku7(canvas,data):
    xoff,yoff=(data.width-data.croil)//2,(data.height-data.croil)//2
    length=data.croil/data.n**2
    for row in range(len(data.board)):
        for col in range(len(data.board[row])):
            x0,y0=xoff+round(col*length),yoff+round(row*length)
            x1,y1=round(x0+length),round(y0+length)
            if data.board[row][col]==0:
                canvas.create_rectangle(x0,y0,x1,y1,fill='green',width=None)
                fill='red'
            else: fill='black'
            if data.solvedboard is not None:
                canvas.create_text((x0+x1)//2,(y0+y1)//2,text=
                                   str(data.solvedboard[row][col]),
                                   font='Arial %d'%(data.numsize),fill=fill)
            else:
                if data.board[row][col]==0:
                    canvas.create_text((x0+x1)//2,(y0+y1)//2,text='?',
                                       font='Arial %d'%(data.numsize),fill=fill)
                else:
                    canvas.create_text((x0+x1)//2,(y0+y1)//2,font='Arial %d'%
                                       (data.numsize),fill=fill,
                                       text=str(data.board[row][col]),)

def drawBoardSudoku7(canvas,data):
    drawDigitsSudoku7(canvas,data)
    drawBoundingLinesSudoku(canvas,data)

def redrawAll7(canvas,data):
    canvas.create_text(data.width//2,data.texty-data.diff,
                       text="Solution",font='Arial 30 bold',
                       justify='center')
    canvas.create_text(data.width//2,data.texty+data.diff,text=data.questiontext
                       ,font='Arial 20',justify='center')
    drawBoardSudoku7(canvas,data)
    data.checkButton.draw(canvas)
    data.retButton.draw(canvas)

'''-----------------------------------------------------------------------------
------------------------------MODE 8: STEPS VIEWER------------------------------
-----------------------------------------------------------------------------'''

def init8(data):
    data.texty=(data.height-data.fheight)//4
    data.diff=25
    data.buttonwidth=(data.width//2)-(3*data.xoffset)//2
    data.retButton=Button(data.width-data.xoffset-data.buttonwidth,data.height-
                          (3*data.yoffset//4),data.width-data.xoffset,data.
                          height-(3*data.yoffset//4)+(data.yoffset//2),
                          text="Return to main")
    data.nextButton=Button(data.width-3*(data.width-data.croil)//8,
                           data.height//2-25,data.width-(data.width-data.croil)
                           //8,data.height//2+25,text="Next")
    data.prevButton=Button((data.width-data.croil)//8,data.height//2-25,
                           3*(data.width-data.croil)//8,data.height//2+25,
                           text="Prev")
    data.checkButton=Button(data.xoffset,data.height-(3*data.yoffset//4),
                            data.xoffset+data.buttonwidth,data.height-
                            (3*data.yoffset//4)+(data.yoffset//2),
                            text="Return to solution")
    data.steptext='''Click 'Next' to see the solution steps.'''
    data.currentstep=None
    data.finishedsteps=[]

def keyPressed8(event,data):
    pass

def updateStepText(data):
    if data.currentstep is None:
        data.steptext='''Click 'Next' to see the solution steps.''';return
    if data.currentstep and not isinstance(data.currentstep,tuple):
        data.steptext='''Done!''';return
    row,col,num,sol=data.currentstep
    row+=1;col+=1
    if sol==0:
        data.steptext='''Row %d, Column %d
Guess that the number is %d.'''%(row,col,num)
    if sol==1:
        data.steptext='''Row %d, Column %d\nLooking at its row, column and box,\
 the only choice is number %d.'''%(row,col,num)
    if sol==2:
        data.steptext='''Row %d, Column %d\nWithin the row, number %d can only\
 go in this cell.'''%(row,col,num)
    if sol==3:
        data.steptext='''Row %d, Column %d\nWithin the column, number %d can \
only go in this cell.'''%(row,col,num)
    if sol==4:
        data.steptext='''Row %d, Column %d\nWithin the box, number %d can only \
go in this cell.'''%(row,col,num)

def mousePressed8(event,data):
    if data.nextButton.clicked(event):
        if data.currentstep is None or isinstance(data.currentstep,tuple):
            if data.currentstep is not None:
                data.finishedsteps.append(data.currentstep)
            if data.steps==[]:data.currentstep=True
            else:data.currentstep=data.steps.pop(0)
            updateStepText(data)
    elif data.prevButton.clicked(event):
        if data.currentstep:
            if isinstance(data.currentstep,tuple):
                data.steps.insert(0,data.currentstep)
            if data.finishedsteps==[]:data.currentstep=None
            else:data.currentstep=data.finishedsteps.pop()
            updateStepText(data)
    elif data.retButton.clicked(event):
        data.mode=1
        initDispatch(data)
    elif data.checkButton.clicked(event):
        if isinstance(data.currentstep,tuple):
            data.steps.insert(0,data.currentstep)
        for i in data.finishedsteps[::-1]:data.steps.insert(0,i)
        data.mode=7
        initDispatch(data)

def timerFired8(data):
    pass

def drawDigitsSudoku8(canvas,data):
    xoff,yoff=(data.width-data.croil)//2,(data.height-data.croil)//2
    length=data.croil/data.n**2
    for row in range(len(data.board)):
        for col in range(len(data.board[row])):
            x0,y0=xoff+round(col*length),yoff+round(row*length)
            x1,y1=round(x0+length),round(y0+length)
            if data.board[row][col]==0:
                if data.currentstep is not None:
                    if (isinstance(data.currentstep,tuple) and
                        row==data.currentstep[0] and col==data.currentstep[1]):
                        canvas.create_rectangle(x0,y0,x1,y1,fill='green',
                                                width=None)
                        canvas.create_text((x0+x1)//2,(y0+y1)//2,
                                           text=str(data.currentstep[2]),
                                           font='Arial %d bold'%
                                           (35*9//(data.n**2)),fill='red')
                    elif (row,col) in [(k[0],k[1]) for k in data.finishedsteps]:
                        canvas.create_rectangle(x0,y0,x1,y1,fill='green',
                                                width=None)
                        canvas.create_text((x0+x1)//2,(y0+y1)//2,font='Arial %d'
                                           %(data.numsize),fill='black',
                                           text=str(data.solvedboard[row][col]))
            else:
                canvas.create_text((x0+x1)//2,(y0+y1)//2,
                                   text=str(data.board[row][col]),
                                   font='Arial %d'%(data.numsize),fill='black')

def drawBoardSudoku8(canvas,data):
    drawDigitsSudoku8(canvas,data)
    drawBoundingLinesSudoku(canvas,data)
    if isinstance(data.currentstep,tuple):drawCurrentClashesSudoku(canvas,data)

def redrawAll8(canvas,data):
    canvas.create_text(data.width//2,data.texty-data.diff,
                       text="Solution steps viewer",font='Arial 30 bold',
                       justify='center')
    canvas.create_text(data.width//2,data.texty+data.diff,text=data.steptext,
                       font='Arial 20',justify='center')
    drawBoardSudoku8(canvas,data)
    if data.currentstep is None or isinstance(data.currentstep,tuple):
        data.nextButton.draw(canvas)
    if data.currentstep: data.prevButton.draw(canvas)
    data.retButton.draw(canvas)
    data.checkButton.draw(canvas)

'''-----------------------------------------------------------------------------
-------------------------------------MAIN---------------------------------------
-----------------------------------------------------------------------------'''

def initDispatch(data):
    if data.mode==1:init1(data)
    elif data.mode==0:init0(data)
    elif data.mode==2:init2(data)
    elif data.mode==3:init3(data)
    elif data.mode==4:init4(data)
    elif data.mode==5:init5(data)
    elif data.mode==6:init6(data)
    elif data.mode==7:init7(data)
    elif data.mode==8:init8(data)

def init(data):
    #initialize webcam
    data.croi=None
    data.roi=None
    data.original=None
    data.lines=None
    data.camera=0
    data.exit=False
    data.puzzles=["Sudoku 4x4","Sudoku 9x9"]
    data.puzzle=None
    data.xoffset=data.width//10
    data.yoffset=data.height//10
    data.n=0
    initImages(data)
    initDispatch(data)

def keyPressed(event,data):
    #key presses in the tkinter window
    if data.mode==1:keyPressed1(event,data)
    elif data.mode==0:keyPressed0(event,data)
    elif data.mode==2:keyPressed2(event,data)
    elif data.mode==3:keyPressed3(event,data)
    elif data.mode==4:keyPressed4(event,data)
    elif data.mode==5:keyPressed5(event,data)
    elif data.mode==6:keyPressed6(event,data)
    elif data.mode==7:keyPressed7(event,data)
    elif data.mode==8:keyPressed8(event,data)

def mousePressed(event,data):
    #mouse presses in the tkinter window
    if data.mode==1:mousePressed1(event,data)
    elif data.mode==0:mousePressed0(event,data)
    elif data.mode==2:mousePressed2(event,data)
    elif data.mode==3:mousePressed3(event,data)
    elif data.mode==4:mousePressed4(event,data)
    elif data.mode==5:mousePressed5(event,data)
    elif data.mode==6:mousePressed6(event,data)
    elif data.mode==7:mousePressed7(event,data)
    elif data.mode==8:mousePressed8(event,data)

def timerFired(data):
    if data.mode==1:timerFired1(data)
    elif data.mode==0:timerFired0(data)
    elif data.mode==2:timerFired2(data)
    elif data.mode==3:timerFired3(data)
    elif data.mode==4:timerFired4(data)
    elif data.mode==5:timerFired5(data)
    elif data.mode==6:timerFired6(data)
    elif data.mode==7:timerFired7(data)
    elif data.mode==8:timerFired8(data)

def redrawAll(canvas,data):
    redrawBackground(canvas,data)
    if data.mode==1:redrawAll1(canvas,data)
    elif data.mode==0:redrawAll0(canvas,data)
    elif data.mode==2:redrawAll2(canvas,data)
    elif data.mode==3:redrawAll3(canvas,data)
    elif data.mode==4:redrawAll4(canvas,data)
    elif data.mode==5:redrawAll5(canvas,data)
    elif data.mode==6:redrawAll6(canvas,data)
    elif data.mode==7:redrawAll7(canvas,data)
    elif data.mode==8:redrawAll8(canvas,data)

def processFrame(data):
    data.original,frame,croi,data.lines=capture(data.frame,data.n)
    capheight,capwidth,_=frame.shape
    capaspectratio=capwidth/capheight
    canvasaspectratio=data.width/data.height
    if canvasaspectratio<capaspectratio:
        data.fwidth=data.width
        data.fheight=int(data.fwidth/capaspectratio)
    else:
        data.fheight=data.height
        data.fwidth=round(data.fheight*capaspectratio)
    frame=cv2.resize(frame,(data.fwidth,data.fheight))
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
    frame=Image.fromarray(frame)
    data.frame=ImageTk.PhotoImage(image=frame)
    if croi is not None:
        data.rawcroi=gridProcess(croi,data.lines)
        data.croil=min(data.fwidth,data.fheight)
        data.rawcroi=cv2.cvtColor(cv2.resize(data.rawcroi,(data.croil,data.croil
                                  )),cv2.COLOR_BGR2RGBA)
        data.rawroi=cv2.cvtColor(data.rawcroi,cv2.COLOR_BGR2GRAY)
        data.roi=cv2.resize(data.rawcroi,(data.croil,data.croil))
        data.croi=ImageTk.PhotoImage(image=Image.fromarray(data.rawcroi))
        data.croix0=(data.width-data.croil)//2
        data.croiy0=(data.height-data.croil)//2
        data.croix1=data.croix0+data.croil
        data.croiy1=data.croiy0+data.croil
        data.gridx0,data.gridy0,data.gridx1,data.gridy1=-1,-1,-1,-1
        data.cap.release()
        data.mode=4
        initDispatch(data)

def redrawFrame(canvas,data):
    canvas.create_image(data.width//2,data.height//2,image=data.frame)

def run(width=300,height=300):
    def initWebcam(canvas,data):
        data.cap=cv2.VideoCapture(data.camera)
        ret,data.frame=data.cap.read()
        processFrame(data)
        data.cap.release()

    def redrawAllWrapper(canvas,data):
        canvas.delete(ALL)
        canvas.create_rectangle(0,0,data.width,data.height,
            fill='cyan',width=0)
        if data.webcamActive and data.cap.isOpened():
            ret,data.frame=data.cap.read()
            if data.frame is not None:
                processFrame(data)
                redrawFrame(canvas,data)
        redrawAll(canvas,data)
        canvas.update()

    def mousePressedWrapper(event,canvas,data):
        mousePressed(event,data)
        redrawAllWrapper(canvas,data)

    def keyPressedWrapper(event,canvas,data):
        keyPressed(event,data)
        redrawAllWrapper(canvas,data)

    def timerFiredWrapper(canvas,data):
        timerFired(data)
        redrawAllWrapper(canvas,data)
        canvas.after(data.timerDelay,timerFiredWrapper,canvas,data)
        if data.exit:data.root.destroy()

    class Struct(object):pass
    data=Struct()
    data.width=width
    data.height=height
    data.timerDelay=100
    data.mode=1
    data.title="PuzzleSolver"
    data.root=Tk()
    data.root.wm_title(data.title)
    data.root.resizable(False,False)
    canvas=Canvas(data.root,width=data.width,height=data.height)
    canvas.pack()
    data.webcamActive=False
    data.frame=None
    init(data)
    initWebcam(canvas,data)
    data.root.bind("<Button-1>",
        lambda event:mousePressedWrapper(event,canvas,data))
    data.root.bind("<Key>",
        lambda event:keyPressedWrapper(event,canvas,data))
    timerFiredWrapper(canvas,data)
    data.root.mainloop()
    data.cap.release()

def main():
    run(700,700)

if __name__=='__main__':
    main()
