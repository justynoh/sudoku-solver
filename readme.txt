# PuzzleSolver

PuzzleSolver is an application that allows you to solve Sudoku puzzles - 
printed, digital or handwritten - by putting the puzzle up to the screen of the 
device. You can also see the steps involved in solving the puzzle based on the 
singleton search and unique element algorithms, as well as backtracking as a
‘last resort’ algorithm.

# Running the application

To run the application, simply run the run.py file in the home directory of the
application. To do this on OS X using the command line, navigate to the 
application directory and run:

$ python run.py

During the first run, it will take some time to load - that is okay. The 
application is training the neural network on the MNIST dataset and saving the 
weights and biases to a local directory, which will be used to detect the digits
in your puzzle. This will later be updated to fit the kind of Sudoku puzzles you
typically solve - a neural network that is customized for you!

# Dependencies

This application runs on python 3.5.3 and uses the following packages:

- tk (8.5.18)
- numpy (1.12.1)
- opencv3 (3.0.0)
- tensorflow (1.0.0)

## Installing tensorflow

In order to install tensorflow, simply use the pip install command. It is 
recommended that the installation is done in a virtual environment such as in
conda or virtualenv. Visit https://www.tensorflow.org/install/ for more 
information.

## Installing opencv3

In order to install opencv3, simply use the pip install command. It is once
again recommended that the installation is done in a virtual environment. Visit
http://opencv.org/ for more information.