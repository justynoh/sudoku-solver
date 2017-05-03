'''
This file contains the helper functions for solving a sudoku puzzle given in a
2-dimensional list of integers.
'''
import math
import string

'''-----------------------------------------------------------------------------
----------------------------------SUDOKU CLASS----------------------------------
-----------------------------------------------------------------------------'''

class Sudoku(object):
    def __init__(self,board,n=3):
        '''
        Params:
            board - list; square and 2-dimensional with dimensions n**2 x n**2
                    for some positive integer n; each element must be an int.
            [n] - int; order of the Sudoku puzzle.
        Returns:
            None.
        '''
        assert(isinstance(board,list) and len(board)==n**2)
        for i in range(n**2):
            assert(isinstance(board[i],list) and len(board[i])==n**2)
            for j in range(n**2):
                assert(isinstance(board[i][j],int) and
                       0<=board[i][j]<=n**2)
        self.board=board
        self.n=n

    def getBox(self,boxrow,boxcol):
        '''
        Params:
            boxrow - int; between 0 and 2 inclusive, refers to the row of the
                     box to be accessed in the Sudoku.
            boxcol - int; between 0 and 2 inclusive, refers to the col of the
                     box to be accessed in the Sudoku.
        Returns:
            A 2-dimensional list extract of the board from the requested box.
        Visualization:
            (0,0) / (0,1) / (0,2)
            ---------------------
            (1,0) / (1,1) / (1,2)
            ---------------------
            (2,0) / (2,1) / (2,2)
        '''
        assert(isinstance(boxrow,int) and isinstance(boxcol,int) and
               0<=boxrow<self.n and 0<=boxcol<self.n)
        startrow,startcol=boxrow*self.n,boxcol*self.n
        endrow,endcol=startrow+self.n,startcol+self.n
        return [[self.board[i][j] for j in range(startcol,endcol)]
                for i in range(startrow,endrow)]

    def getChoices(self,row,col):
        '''
        Params:
            row - int; between 0 and self.n**2 inclusive-exclusive, refers to
                  the row of the requested cell.
            col - int; between 0 and self.n**2 inclusive-exclusive, refers to
                  the cel of the requested cell.
        Returns:
            A list of the possible numbers that could be entered in the cell.
            Returns an empty list if the cell is already solved.
        '''
        if self.board[row][col]!=0: return []
        choices=list(range(1,self.n**2+1))
        extracts=self.board[row]+[self.board[i][col] for i in range(self.n**2)]
        for k in self.getBox(row//self.n,col//self.n): extracts+=k
        for num in extracts:
            if num in choices: choices.remove(num)
        return choices

    def getBoardChoices(self):
        '''
        Params:
            None.
        Returns:
            A 2-dimensional square list of dimensions self.n**2 x self.n**2,
            with each element as a 1-dimensional list of choices that could be
            entered in the cell.
        '''
        return [[self.getChoices(row,col) for col in range(self.n**2)]
                for row in range(self.n**2)]

    def getBoardChoicesNumber(self):
        '''
        Params:
            None.
        Returns:
            A 2-dimensional square list of dimensions self.n**2 x self.n**2,
            with each element contains an integer corresponding to the number of
            choices for that cell.
        '''
        choices=self.getBoardChoices()
        return [[len(choices[row][col]) for col in range(self.n**2)]
                for row in range(self.n**2)]

    def setCell(self,row,col,num):
        '''
        Params:
            row - int; row of the cell to be set.
            col - int; col of the cell to be set.
            num - int; number to be entered into cell.
        Returns:
            None.
        '''
        assert(isinstance(row,int) and 0<=row<self.n**2 and isinstance(col,int)
               and 0<=col<self.n**2 and isinstance(num,int) and
               0<num<=self.n**2)
        self.board[row][col]=num

    def resetCell(self,row,col):
        '''
        Params:
            row - int; row of the cell to be reset.
            col - int; col of the cell to be reset.
        Returns:
            None.
        '''
        assert(isinstance(row,int) and 0<=row<self.n**2 and isinstance(col,int)
               and 0<=col<self.n**2)
        self.board[row][col]=0

    def isFull(self):
        '''
        Params:
            None.
        Returns:
            True if the board in the Sudoku object is completed (with non-zeros)
            else returns False.
        '''
        for row in range(self.n**2):
            for col in range(self.n**2):
                if self.board[row][col]==0: return False
        return True

    def hasNoRepeats(self,numlist):
        '''
        Params:
            numlist - list; ints to be checked.
        Returns:
            True if numlist does not have any repeated numbers (excluding 0).
        '''
        seen=[]
        for elem in numlist:
            if elem!=0:
                if elem in seen: return False
                seen.append(elem)
        return True

    def rowIsValid(self,row):
        '''
        Params:
            row - int; row from board.
        Returns:
            True if the requested row does not have any repeated numbers.
        '''
        rowtocheck=self.board[row]
        return self.hasNoRepeats(rowtocheck)

    def colIsValid(self,col):
        '''
        Params:
            col - int; col from board.
        Returns:
            True if the requested col does not have any repeated numbers.
        '''
        coltocheck=[self.board[row][col] for row in range(self.n**2)]
        return self.hasNoRepeats(coltocheck)

    def boxIsValid(self,boxrow,boxcol):
        '''
        Params:
            boxrow - int; row of box from board, as outlined in getBox().
            boxcol - int; col of box from board, as outlined in getBox().
        Returns:
            True if the requested box does not have any repeated numbers.
        '''
        boxtocheck=[]
        for i in self.getBox(boxrow,boxcol): boxtocheck+=i
        return self.hasNoRepeats(boxtocheck)

    def isValid(self):
        '''
        Params:
            None.
        Returns:
            True if the board in the Sudoku object is valid (as per usual
            Sudoku puzzle constraints) else returns False, ignoring empty cells.
        '''
        for row in range(self.n**2):
            if not self.rowIsValid(row): return False
        for col in range(self.n**2):
            if not self.colIsValid(col): return False
        for boxrow in range(self.n):
            for boxcol in range(self.n):
                if not self.boxIsValid(boxrow,boxcol): return False
        for row in range(self.n**2):
            for col in range(self.n**2):
                if self.board[row][col]==0 and self.getChoices(row,col)==[]:
                    return False
        return True

'''-----------------------------------------------------------------------------
-----------------------SOLVER ALGORITHM HELPER FUNCTIONS------------------------
-----------------------------------------------------------------------------'''

def existSingletons(choicesnum):
    '''
    Params:
        choicesnum - list; each element is an int referring to number of choices
                     of entry for that position.
    Returns:
        True if singletons exist, False otherwise.
    '''
    for row in range(len(choicesnum)):
        for col in range(len(choicesnum[row])):
            if choicesnum[row][col]==1: return True
    return False

def uniqueElements(choices):
    '''
    Params:
        choices - list; contains choices in a 1-dimensional list for each
                  position.
    Returns:
        List of unique elements in the choice list (and an empty list if there
        are none).
    '''
    seen=[None]+[0]*len(choices)
    for choice in choices:
        for num in choice: seen[num]+=1
    unique=[]
    for num in range(1,len(seen)):
        if seen[num]==1: unique.append(num)
    return unique

def uniqueCellSearchRow(s):
    '''
    Params:
        s - Sudoku; board to be solved.
    Returns:
        A list of tuples (row,col,elem) indicating those that were filled;
        modifies the Sudoku object board by doing the unique cell search
        algorithm on each row.
    '''
    filled=[]
    choices=s.getBoardChoices()
    for row in range(s.n**2):
        rowlist=choices[row]
        for elem in uniqueElements(rowlist):
            for col in range(s.n**2):
                if elem in rowlist[col]:
                    s.setCell(row,col,elem)
                    filled.append((row,col,elem,2))
                    break
    return filled

def uniqueCellSearchCol(s):
    '''
    Params:
        s - Sudoku; board to be solved.
    Returns:
        A list of tuples (row,col,elem) indicating those that were filled;
        modifies the Sudoku object board by doing the unique cell search
        algorithm on each col.
    '''
    filled=[]
    choices=s.getBoardChoices()
    for col in range(s.n**2):
        collist=[choices[row][col] for row in range(s.n**2)]
        for elem in uniqueElements(collist):
            for row in range(s.n**2):
                if elem in collist[row]:
                    s.setCell(row,col,elem)
                    filled.append((row,col,elem,3))
                    break
    return filled

def uniqueCellSearchBox(s):
    '''
    Params:
        s - Sudoku; board to be solved.
    Returns:
        A list of tuples (row,col,elem) indicating those that were filled;
        modifies the Sudoku object board by doing the unique cell search
        algorithm on each box.
    '''
    filled=[]
    choices=s.getBoardChoices()
    for boxrow in range(s.n):
        for boxcol in range(s.n):
            boxlist=[]
            startrow,startcol=boxrow*s.n,boxcol*s.n
            endrow,endcol=startrow+s.n,startcol+s.n
            for row in range(startrow,endrow):
                for col in range(startcol,endcol):
                    boxlist.append(choices[row][col])
            for elem in uniqueElements(boxlist):
                for idx in range(s.n**2):
                    if elem in boxlist[idx]:
                        row=boxrow*s.n+idx//s.n
                        col=boxcol*s.n+idx%s.n
                        s.setCell(row,col,elem)
                        filled.append((row,col,elem,4))
                        break
    return filled

'''-----------------------------------------------------------------------------
-------------------------------SOLVER ALGORITHMS-------------------------------
-----------------------------------------------------------------------------'''

def singletonSearch(s):
    '''
    Params:
        s - Sudoku; board to be solved.
    Returns:
        A list of tuples (row,col,elem) indicating those that were filled;
        modifies the Sudoku object board by recursively searching for cells
        with only one possible number and inserting those in.
    '''
    choicesnum=s.getBoardChoicesNumber()
    choices=s.getBoardChoices()
    filled=[]
    if not existSingletons(choicesnum): return filled
    for row in range(s.n**2):
        for col in range(s.n**2):
            if choicesnum[row][col]==1:
                s.setCell(row,col,choices[row][col][0])
                filled.append((row,col,choices[row][col][0],1))
    return filled+singletonSearch(s)

def uniqueCellSearch(s):
    '''
    Params:
        s - Sudoku; board to be solved.
    Returns:
        A list of tuples (row,col,elem) indicating those that were filled;
        modifies the Sudoku object board by recursively searching for numbers
        whose cells can be derived by searching for unique cells each
        number can be in and inserting those in.
    '''
    filled=uniqueCellSearchBox(s)+uniqueCellSearchRow(s)+uniqueCellSearchCol(s)
    if filled==[]: return filled
    return filled+uniqueCellSearch(s)

'''-----------------------------------------------------------------------------
----------------------------SOLVER HELPER FUNCTIONS-----------------------------
-----------------------------------------------------------------------------'''

def fillBoard(s):
    '''
    Params:
        s - Sudoku; board to be solved.
    Returns:
        A list of tuples (row,col,elem,type) indicating those that were filled;
        modifies the Sudoku object board by recursively using direct solving
        techniques to attempt to derive the solution.
        Type 1 indicates singletonSearch, type 2,3,4 indicates uniqueCellSearch
        by row,col,box respectively.
    '''
    filled=singletonSearch(s)+uniqueCellSearch(s)
    if filled==[]: return filled
    return filled+fillBoard(s)

def nextChoice(s):
    '''
    Params:
        s - Sudoku; board to be solved.
    Returns:
        A tuple row,col referring to the next possible choice to backtrack from.
        If there are none, returns row,col=-1,-1.
    '''
    numchoices=s.getBoardChoicesNumber()
    for row in range(len(numchoices)):
        for col in range(len(numchoices[row])):
            if numchoices[row][col]>1: return row,col
    return -1,-1

'''-----------------------------------------------------------------------------
------------------------------------SOLVER--------------------------------------
-----------------------------------------------------------------------------'''

def solveSudoku(board):
    '''
    Params:
        board - list; 2-dimensional list containing the board to be solved.
    Returns:
        The completed board and list of steps if there exists a solution,
        otherwise None.
    '''
    n=round(len(board)**0.5)
    if n**2!=len(board): raise Exception("Board dims are not square numbers.")
    s=Sudoku(board,n)
    steps=[]
    def backtrack(s,steps):
        filled=fillBoard(s)
        steps.extend(filled)
        if s.isFull():
            if s.isValid():return True
            for k in filled:
                steps.remove(k)
                s.resetCell(k[0],k[1])
            return None
        row,col=nextChoice(s)
        if row!=-1:
            for num in s.getChoices(row,col):
                s.setCell(row,col,num)
                steps.append((row,col,num,0))
                if s.isValid():
                    if backtrack(s,steps):
                        return True
                steps.pop()
            s.resetCell(row,col)
        for k in filled:
            steps.remove(k)
            s.resetCell(k[0],k[1])
        return None
    return (s.board,steps) if backtrack(s,steps) else (None,None)
