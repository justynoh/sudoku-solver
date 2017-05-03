'''
This file contains the helper functions for the purposes of evaluating the best
explanations to give for each step of the solution, and then drawing the
explanations in a self-explanatory, noughts and crosses method.
'''
import copy

def clashes1(data,board):
    '''
    Params:
        data - object; stores data for the user interface of the application.
        board - list; 2-dimensional containing the board that has been solved
                at the current state.
    Returns:
        x - list; contains tuples (row,col) which identify the boxes to draw
            X's in based on singleton search algorithm.
        o - list; contains tuples (row,col) which identify the boxes to draw
            O's in based on singleton search algorithm.
    '''
    x,o=[],[]
    nums=list(range(1,data.n**2+1))
    nums.remove(data.currentstep[2])
    boxrow,boxcol=data.currentstep[0]//data.n,data.currentstep[1]//data.n
    for row in range(boxrow*data.n,(boxrow+1)*data.n):
        for col in range(boxcol*data.n,(boxcol+1)*data.n):
            if board[row][col]!=0 and board[row][col] in nums:
                o.append((row,col))
                nums.remove(board[row][col])
    for idx in range(data.n**2):
        if (board[data.currentstep[0]][idx]!=0 and
            board[data.currentstep[0]][idx] in nums):
            o.append((data.currentstep[0],idx))
            nums.remove(board[data.currentstep[0]][idx])
        if (board[idx][data.currentstep[1]]!=0 and
            board[idx][data.currentstep[1]] in nums):
            o.append((idx,data.currentstep[1]))
            nums.remove(board[idx][data.currentstep[1]])
    return x,o

def clashes2(data,board):
    '''
    Params:
        data - object; stores data for the user interface of the application.
        board - list; 2-dimensional containing the board that has been solved
                at the current state.
    Returns:
        x - list; contains tuples (row,col) which identify the boxes to draw
            X's in based on unique cell search algorithm for rows.
        o - list; contains tuples (row,col) which identify the boxes to draw
            O's in based on unique cell search algorithm for rows.
    '''
    x,o=[],[]
    row=data.currentstep[0]
    for col in range(data.n**2):
        if (col!=data.currentstep[1] and board[row][col]==0):
            x.append((row,col))
            found=False
            boxrow,boxcol=row//data.n,col//data.n
            # Box-based search
            for i in range(boxrow*data.n,(boxrow+1)*data.n):
                for j in range(boxcol*data.n,(boxcol+1)*data.n):
                    if (not (i==data.currentstep[0] and j==data.currentstep[1])
                        and board[i][j]==data.currentstep[2]):
                        o.append((i,j))
                        found=True
                        break
                if found:break
            if not found:
                # Col-based search
                for i in range(data.n**2):
                    if (i!=row and board[i][col]==data.currentstep[2]):
                        o.append((i,col))
                        break
    return x,o

def clashes3(data,board):
    '''
    Params:
        data - object; stores data for the user interface of the application.
        board - list; 2-dimensional containing the board that has been solved
                at the current state.
    Returns:
        x - list; contains tuples (row,col) which identify the boxes to draw
            X's in based on unique cell search algorithm for columns.
        o - list; contains tuples (row,col) which identify the boxes to draw
            O's in based on unique cell search algorithm for columns.
    '''
    x,o=[],[]
    col=data.currentstep[1]
    for row in range(data.n**2):
        if (row!=data.currentstep[0] and board[row][col]==0):
            x.append((row,col))
            found=False
            # Box-based search
            boxrow,boxcol=row//data.n,col//data.n
            for i in range(boxrow*data.n,(boxrow+1)*data.n):
                for j in range(boxcol*data.n,(boxcol+1)*data.n):
                    if (not (i==data.currentstep[0] and j==data.currentstep[1])
                        and board[i][j]==data.currentstep[2]):
                        o.append((i,j))
                        found=True
                        break
                if found:break
            if not found:
                # Row-based search
                for i in range(data.n**2):
                    if (i!=col and board[row][i]==data.currentstep[2]):
                        o.append((row,i))
                        break
    return x,o

def clashes4(data,board):
    '''
    Params:
        data - object; stores data for the user interface of the application.
        board - list; 2-dimensional containing the board that has been solved
                at the current state.
    Returns:
        x - list; contains tuples (row,col) which identify the boxes to draw
            X's in based on unique cell search algorithm for boxes.
        o - list; contains tuples (row,col) which identify the boxes to draw
            O's in based on unique cell search algorithm for boxes.
    '''
    x,o=[],[]
    boxrow,boxcol=data.currentstep[0]//data.n,data.currentstep[1]//data.n
    for row in range(boxrow*data.n,(boxrow+1)*data.n):
        for col in range(boxcol*data.n,(boxcol+1)*data.n):
            if (not (row==data.currentstep[0] and col==data.currentstep[1]) and
                board[row][col]==0):
                x.append((row,col))
                found=False
                # Row-based search
                for i in range(data.n**2):
                    if (i!=col and board[row][i]==data.currentstep[2]):
                        o.append((row,i))
                        found=True
                        break
                if not found:
                    # Col-based search
                    for i in range(data.n**2):
                        if (i!=row and board[i][col]==data.currentstep[2]):
                            o.append((i,col))
                            break
    return x,o

def drawxo(canvas,data,x,o):
    '''
    Params:
        canvas - tk object; canvas to draw the user interface in.
        data - object; stores data for the user interface of the application.
        x - list; contains tuples (row,col) which identify the boxes to draw
            X's in.
        o - list; contains tuples (row,col) which identify the boxes to draw
            O's in.
    Returns:
        None, draws the X's and O's to explain each step to the user on the
        canvas.
    '''
    xoff,yoff=(data.width-data.croil)//2,(data.height-data.croil)//2
    length=data.croil/data.n**2
    red=5
    for row,col in x:
        x0,y0=xoff+round(col*length)+red,yoff+round(row*length)+red
        x1,y1=round(x0+length)-2*red,round(y0+length)-2*red
        canvas.create_line(x0,y0,x1,y1,width=5,fill='purple')
        canvas.create_line(x0,y1,x1,y0,width=5,fill='purple')
    for row,col in o:
        x0,y0=xoff+round(col*length)+red,yoff+round(row*length)+red
        x1,y1=round(x0+length)-2*red,round(y0+length)-2*red
        canvas.create_oval(x0,y0,x1,y1,fill=None,width=5,outline='orange')

def drawCurrentClashesSudoku(canvas,data):
    '''
    Params:
        canvas - tk object; canvas to draw the user interface in.
        data - object; stores data for the user interface of the application.
    Returns:
        None, draws the X's and O's to explain each step to the user on the
        canvas.
    '''
    currboard=copy.deepcopy(data.board)
    for row,col,elem,_ in data.finishedsteps:currboard[row][col]=elem
    if data.currentstep[3]==1:x,o=clashes1(data,currboard)
    elif data.currentstep[3]==2:x,o=clashes2(data,currboard)
    elif data.currentstep[3]==3:x,o=clashes3(data,currboard)
    elif data.currentstep[3]==4:x,o=clashes4(data,currboard)
    else:x,o=[],[]
    drawxo(canvas,data,x,o)
