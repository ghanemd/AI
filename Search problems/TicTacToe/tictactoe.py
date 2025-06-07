"""
Tic Tac Toe Player
"""

from copy import deepcopy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state() :
        return X 
    count_x = 0 
    count_o = 0
    for row in board :
        for col in row :
            if col == X :
                count_x += 1
            if col == O :
                count_o += 1
    if count_x > count_o :
        return O 
    else :
        return X 


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    res = set()
    for i in range(3) :
        for j in range(3) :
            if board[i][j] == EMPTY :
                res.add((i,j))
    return res



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i,j = action
    if board[i][j] != EMPTY :
        raise Exception("Invalid action on board")
    else :
        player_move = player(board)
        new_board = deepcopy(board)
        new_board[i][j] = player_move
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #diagonally
    if (board[0][0] == board[1][1] == board[2][2]) and  board[0][0] != EMPTY:
        return board[0][0]
    if (board[2][0] == board[1][1] == board[0][2]) and board[1][1] != EMPTY :
        return board[1][1]
    
    #horizontally
    for i in range(3) :
        if (board[i][0] == board[i][1] == board[i][2]) and board[i][0] != EMPTY :
            return board[i][0]
        
    #vertically
    for i in range(3) :
        if(board[0][i] == board[1][i] == board[2][i]) and board[0][i] != EMPTY :
            return board[0][i]
    
    return None



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None :
        return True
    for row in board :
        for col in row :
            if col == EMPTY :
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winning_player = winner(board) 
    if winning_player == X :
        return 1
    elif winning_player == O :
        return -1
    else :
        return 0 


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    positive_infinity = float('inf')
    negative_infinity = float('-inf')
    

    def maxValue(board) :
        optimal_move = None
        if terminal(board):
            return utility(board) , optimal_move
        v = negative_infinity
        for action in actions(board) :
            minVal = minValue(result(board,action))[0]
            if minVal > v :
                v = minVal
                optimal_move = action
        return v , optimal_move
    
    def minValue(board) :
        optimal_move = None
        if terminal(board) :
            return utility(board) , optimal_move
        v = positive_infinity
        for action in actions(board) :
            maxVal = maxValue(result(board,action))[0]
            if maxVal < v :
                v = maxVal
                optimal_move = action
        return v , optimal_move

    if(terminal(board)) :
        return None
    
    current_player = player(board)
    if current_player == X :
        return maxValue(board)[1]
    elif current_player == O :
        return minValue(board)[1]

