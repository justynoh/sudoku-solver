'''
This file contains the neural network which will train on the MNIST dataset for
digit recognition in number-related puzzles, and saves the weights and biases
from the neural network to a folder.
'''
import os
import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data
from tensorflow.contrib.learn.python.learn.datasets.mnist import *
from tensorflow.python.framework import dtypes

'''-----------------------------------------------------------------------------
----------------------------WEIGHTS AND BIAS CLASSES----------------------------
-----------------------------------------------------------------------------'''

class Weight(object):
    def __init__(self,i):
        '''
        Params:
            i - list or str; path of the preloaded weights or the list
                containing the dimensions of the weight.
        Returns:
            None.
        '''
        if isinstance(i,str):
            self.W=tf.Variable(np.load(i))
        elif isinstance(i,list):
            # Use a truncated normal distribution for symmetry breaking.
            self.W=tf.Variable(tf.truncated_normal(i,stddev=0.03))
        else:
            raise TypeError("Arg passed to Weight object is not str or list.")

class Bias(object):
    def __init__(self,i,preloaded=False):
        '''
        Params:
            i - int or str; path of the preloaded bias or an int containing the
            number of output nodes.
        Returns:
            None.
        '''
        if isinstance(i,str):
            self.b=tf.Variable(np.load(i))
        # Once again, use a truncated normal distribution for symmetry breaking.
        elif isinstance(i,int):
            self.b=tf.Variable(tf.truncated_normal([i],stddev=0.03))
        else:
            raise TypeError("Arg passed to Bias object is not str or int.")

'''-----------------------------------------------------------------------------
-------------------------------TRAINING ON MNIST--------------------------------
-----------------------------------------------------------------------------'''

def setupNN(isMNIST):
    '''
    Params:
        None.
    Returns:
        None. Sets up a neural network architecture as a Tensorflow computation
        graph.
    NN Architecture:
        0 - INPUT LAYER: 784 nodes
        1 - HIDDEN LAYER 1: 196 nodes
        2 - HIDDEN LAYER 2: 49 nodes
        3 - OUTPUT LAYER: 10 nodes
    '''
    # Initialize training data - image data and ground truths.
    X=tf.placeholder(tf.float32,[None,784])
    Y_=tf.placeholder(tf.float32,[None,10])

    # Initialize numpy array paths.
    path='./data'

    # Layer 0 --> layer 1.
    if isMNIST:W1=Weight([784,196]);b1=Bias(196)
    else:W1=Weight(path+'/W1.npy');b1=Bias(path+'/b1.npy')

    # Output at layer 1 with relu activator.
    Y1=tf.nn.relu(tf.matmul(X,W1.W)+b1.b)

    # Layer 1 --> layer 2
    if isMNIST:W2=Weight([196,49]);b2=Bias(49)
    else:W2=Weight(path+'/W2.npy');b2=Bias(path+'/b2.npy')

    # Output at layer 2 with sigmoid activator.
    Y2=tf.nn.sigmoid(tf.matmul(Y1,W2.W)+b2.b)

    # Dropout at layer 2 to prevent overfitting.
    keep=tf.placeholder(tf.float32)
    Y2_drop=tf.nn.dropout(Y2,keep)

    # Layer 2 --> Layer 3
    if isMNIST:W3=Weight([49,10]);b3=Bias(10)
    else:W3=Weight(path+'/W3.npy');b3=Bias(path+'/b3.npy')

    # Output at layer 3 with a softmax activator for final output.
    Y=tf.nn.softmax(tf.matmul(Y2_drop,W3.W)+b3.b)

    return X,Y_,W1,b1,W2,b2,W3,b3,Y,keep

def mainNN(isMNIST=False,dataset=None,labels=None):
    '''
    Params:
        isMNIST - bool; True if we are training on MNIST from scratch, False
                  otherwise.
        dataset - list or Nonetype; list of np arrays containing image data
                  to be trained on.
    Returns:
        None. Saves the trained weights and biases as .npy files to folder.
    '''
    # Using Tensorflow's MNIST read function (not mine!).
    if isMNIST:
        data=input_data.read_data_sets('/tmp/tensorflow/mnist/input_data',
                                       one_hot=True)
        trials=10000
    else:
        if not isinstance(dataset,list):
            raise TypeError("dataset must be of type list.")
        if not isinstance(labels,list):
            raise TypeError("labels must be of type list.")
        if not len(dataset)==len(labels):
            raise Exception("dataset and labels must have equal length.")
        for i in dataset:
            if not isinstance(i,np.ndarray):
                raise TypeError("dataset elements must be of type ndarray")
        for i in labels:
            if not isinstance(i,np.ndarray):
                raise TypeError("labels elements must be of type ndarray.")
        dataset=np.array(dataset)
        labels=np.array(labels)
        validation_num=len(dataset)//5
        test_num=len(dataset)//5
        train_num=len(dataset)-test_num-validation_num
        train_images,train_labels=dataset[:train_num],labels[:train_num]
        validation_images=dataset[train_num:train_num+validation_num]
        validation_labels=labels[train_num:train_num+validation_num]
        test_images=dataset[train_num+validation_num:]
        test_labels=labels[train_num+validation_num:]
        dtype,reshape=dtypes.float32,True
        train=DataSet(train_images,train_labels,dtype=dtype,reshape=reshape)
        validation=DataSet(validation_images,validation_labels,dtype=dtype,
                           reshape=reshape)
        test=DataSet(test_images,test_labels,dtype=dtype,reshape=reshape)
        data=base.Datasets(train=train,validation=validation,test=test)
        trials=1000

    # Set up the neural network.
    X,Y_,W1,b1,W2,b2,W3,b3,Y,keep=setupNN(isMNIST)

    # Set up the accuracy measures and training method.
    xentropy=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=Y_,
                                                                    logits=Y))
    train_step=tf.train.AdamOptimizer(5e-4).minimize(xentropy)
    accuracy=tf.reduce_mean(tf.cast(tf.equal(tf.argmax(Y,1),tf.argmax(Y_,1)),
                                    tf.float32))

    print("Training...")
    # Begin training.
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(1,trials+1):
            batch_X,batch_Y=data.train.next_batch(trials//100)
            train_data={X:batch_X,Y_:batch_Y,keep:0.75}
            sess.run(train_step,feed_dict=train_data)
            if i%(trials//10)==0:
                test_data={X:data.test.images,Y_:data.test.labels,keep:1}
                accy,loss=sess.run([accuracy,xentropy],feed_dict=test_data)
                print("Iteration %d: test accuracy - %.2f%%, test loss - %.2f"
                      %(i,accy*100,loss))
        W1v,b1v,W2v,b2v,W3v,b3v=sess.run([W1.W,b1.b,W2.W,b2.b,W3.W,b3.b])

    # Save the weights and biases as numpy arrays.
    path='./data'
    if not os.path.isdir(path): os.mkdir(path)
    np.save(path+'/W1',W1v)
    np.save(path+'/b1',b1v)
    np.save(path+'/W2',W2v)
    np.save(path+'/b2',b2v)
    np.save(path+'/W3',W3v)
    np.save(path+'/b3',b3v)

if __name__=='__main__': mainNN(True)
