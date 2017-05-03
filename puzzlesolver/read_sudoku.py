'''
This file contains the helper functions for the application to read and predict
the digits for the Sudoku puzzle, based on the roi it was given from the UI.
'''
import cv2
import math
import numpy as np

def threshold(img,thresh):
    '''
    Params:
        img - np array; image to be thresholded.
        thresh - int; threshold.
    Returns:
        None. Modifies img so that all values above the threshold (closer to
        cv white) are set to 0 (MNIST white).
    '''
    for row in range(len(img)):
        for col in range(len(img[row])):
            if img[row][col]>thresh: img[row][col]=255
            img[row][col]=255-img[row][col]

def getDigitsNxN(puzzle,n):
    '''
    Params:
        puzzle - np array; image of the puzzle grid.
        n - int; order of the puzzle.
    Returns:
        2-dimensional list of np arrays, where the element at (row,col) is the
        image of the box at (row,col) on the grid.
    '''
    width,height=puzzle.shape
    boxwidth,boxheight=width/(n**2+1),height/(n**2+.5+1)
    digitlist=[]
    for row in range(n**2):
        rowlist=[]
        for col in range(n**2):
            x0,y0=round(col*width/n**2),round(row*height/n**2)
            x1,y1=round(x0+boxwidth),round(y0+boxheight)
            square=cv2.resize(puzzle[y0:y1,x0:x1],(28,28))
            ret,_=cv2.threshold(square,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            threshold(square,ret)
            rowlist.append(square)
        digitlist.append(rowlist)
    return digitlist

def importWeightsAndBiases():
    '''
    Params:
        None.
    Returns:
        Weights and biases for the various neural network layers.
    '''
    path='./data'
    W1=np.load(path+'/W1.npy')
    W2=np.load(path+'/W2.npy')
    W3=np.load(path+'/W3.npy')
    b1=np.load(path+'/b1.npy')
    b2=np.load(path+'/b2.npy')
    b3=np.load(path+'/b3.npy')
    return W1,b1,W2,b2,W3,b3

def activation(x,activation):
    '''
    Params:
        x - np array; one-hot array to be activated.
        activation - str; activation function to be used - 'relu', 'sigmoid' or
                     'softmax'.
    Returns:
        An activated np array with the requested activation function.
    '''
    if activation=="relu":return x*(x>0)
    elif activation=="sigmoid":return np.exp(-np.logaddexp(0,-x))
    elif activation=="softmax":return np.exp(x)/np.sum(np.exp(x))

def predictDigits(digitlist,n):
    '''
    Params:
        digitlist - list; 2-dimensional list of np arrays, where the element at
                    (row,col) is the image of the box at (row,col) on the grid.
        n - int; order of the puzzle.
    Returns:
        A 2-dimensional list of digits corresponding to the predicted digits
        in the image shown.
    '''
    W1,b1,W2,b2,W3,b3=importWeightsAndBiases()
    digits=[]
    for row in range(len(digitlist)):
        rowlist=[]
        for col in range(len(digitlist[row])):
            digit=np.reshape(digitlist[row][col],(784))
            digit=digit.astype(np.float32)
            digit=np.multiply(digit,1/255)
            Y1=activation(np.matmul(digit,W1)+b1,'relu')
            Y2=activation(np.matmul(Y1,W2)+b2,'sigmoid')
            predictions=activation(np.matmul(Y2,W3)+b3,'softmax')
            predictions=predictions[:n**2+1]
            select=int(np.argmax(predictions))
            rowlist.append(select)
        digits.append(rowlist)
    return digits

def readSudoku(puzzle,n):
    '''
    Params:
        puzzle - np array; image of the puzzle grid.
        n - int; order of the puzzle.
    Returns:
        A 2-dimensional list containing the digits to the Sudoku puzzle.
    '''
    digitlist=getDigitsNxN(puzzle,n)
    digits=predictDigits(digitlist,n)
    return digitlist,digits
