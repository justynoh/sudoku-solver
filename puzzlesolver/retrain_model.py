'''
This file contains the functions to retrain the model based on user input from
the application using the network.
'''
import numpy as np
import random
from puzzlesolver.mnist_network import *

def elemToList(lst):
    '''
    Params:
        lst - list; contains 2-dimensional numpy arrays of image data.
    Returns:
        A list of 3-dimensional numpy arrays of image data, which is identical
        to the input lst except that every element is itself a singleton
        numpy array.
    '''
    newdata=[]
    for img in lst:
        new=[[[c] for c in r] for r in img]
        newdata.append(np.array(new))
    return newdata

def createOneHot(lst):
    '''
    Params:
        lst - list; contains ints which are label data for each image.
    Returns:
        A list of 1-dimensional numpy arrays which are in one-hot form,
        corresponding to the int which the image is labeled as.
    '''
    newdata=[]
    for label in lst:
        new=np.zeros(10)
        new[label]=1
        newdata.append(new)
    return newdata

def retrainModel(dataset,labels):
    '''
    Params:
        dataset - list; 2-dimensional with each element being a 2-dimensional
                  numpy array containing the image data for the sudoku cell in
                  that position in the dataset list.
        labels - list; 2-dimensional with each element being an int
                 corresponding to the label on the sudoku cell in that position
                 in the image.
    Returns:
        None, updates the weights and biases in the data folder to reflect the
        updated user data.
    '''
    valid_data,valid_labels=[],[]
    for row in range(len(labels)):
        for col in range(len(labels[row])):
            valid_data.append(dataset[row][col])
            valid_labels.append(labels[row][col])
    valid_data=elemToList(valid_data)
    valid_labels=createOneHot(valid_labels)
    toshuffle=[(valid_data[i],valid_labels[i]) for i in range(len(valid_data))]
    random.shuffle(toshuffle)
    valid_data,valid_labels=[],[]
    for d,l in toshuffle:valid_data.append(d);valid_labels.append(l)
    mainNN(False,valid_data,valid_labels)
