import os
from puzzlesolver.user_interface import *

if __name__=='__main__':
    path='./data'
    if not os.path.isdir(path):
        print("Training on MNIST data set. Please wait...")
        mainNN(True)
    main()
