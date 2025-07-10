from random import randint
from BoardClasses import Move
from BoardClasses import Board
import time
from copy import deepcopy
from math import sqrt, log
import random
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.max_simulations = 1000
        self.total_remaining_time = 480
        self.time_limit = self.update_time_limit()

    # Does: Updates board state with opponent's move then generates, makes, and return move we made
    # param move: move object of opponent
    # return: move object we made
    def get_move(self,move: Move) -> Move:
        self.update_time_limit()    # update time_limit

        move_start_time = time.time() # define the start time of this move

        # if given a move update board state, otherwise change our color
        if len(move) != 0:  
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        
        # get all possible current moves, possible_moves is a 2d list, [[piece1move1,piece1move2],[piece2move1,piece2move2]...]
        # if there is only one move availabe, update board and return it
        possible_moves = self.board.get_all_possible_moves(self.color) 
        if len(possible_moves) == 1 and len(possible_moves[0]) == 1: 
            only_move = possible_moves[0][0]
            self.board.make_move(only_move, self.color) 
            self.total_remaining_time -= time.time() - move_start_time # decrement players remaining total time by how long it took to make the move
            return only_move

        root_node = Node(deepcopy(self.board), color = self.color) # generate root node of board at this state
        end_time = time.time() + self.time_limit # calculate time deadline of move
        num_of_simulations = 0
        

        # run simulations as long as within simulation count max, move time deadline
        while num_of_simulations < self.max_simulations and time.time() < end_time:     
            
            node = self.selection(root_node) # select a leaf node                                                   

            # if node game not over, expand all possible children and return random one
            if not node.game_over() and node.possible_moves:
                node = self.expand(node)
            
            result = self.simulate(node) # simulate game, result = winner(2=w,1=b,-1=tie)

            self.back_propogate(node, result) # update win and visit count on nodes in selected path

            num_of_simulations += 1

        
        if not root_node.children:
            # If no children, make a random valid move
            move_list = random.choice(possible_moves)
            move = random.choice(move_list)
            self.board.make_move(move, self.color)
            self.total_remaining_time -= time.time() - move_start_time # decrement players remaining total time by how long it took to make the move
            return move

        # pick the best move
        best_child = max(root_node.children, key = lambda x: x.visits)
        best_move = best_child.move
 
        self.board.make_move(best_move, self.color) # update board state

        self.total_remaining_time -= time.time() - move_start_time # decrement players remaining total time by how long it took to make the move
        
        return best_move #return move made
    
    # Does: Selects a leaf node using ucb
    # param node: root node of current board state
    # return: leaf node with highest ucb
    def selection(self, node: "Node") -> "Node":  
        current = node

        while True:     
            if len(current.children) == 0: # If its a leaf node, return it
                return current 
                               
            current = max(current.children, key = lambda x: x.ucb1())  #choose the child node that has the highest ucb1 value

    # Does: Generates all children for given leaf node
    # param node: leaf node
    # return: a random generated child node to run simulation on
    def expand(self, node: "Node") -> "Node":  

        if len(node.possible_moves) == 0: 
            return node
        
        while node.possible_moves: #create a child node for every possible move
            move = node.possible_moves.pop()
            board = deepcopy(node.board)
            board.make_move(move, node.color)
            next_player = self.opponent[node.color]
            new_child = Node(board, node, move, next_player)
            node.children.append(new_child)
        
        return node.children[random.randint(0, len(node.children) - 1)]
    
    # Does: Plays a game until completion
    # param node: node to run simulation on
    # return: who won this game (2=w,1=b,-1=tie)
    def simulate(self, node: "Node") -> int:  

        # create deepcopy of provided node's board
        board = deepcopy(node.board)
        color = node.color

        # keep making moves from that board until it reaches a state where the game state is over
        while not board.is_win(color) != 0:         
            possible_moves = []         
            moves = board.get_all_possible_moves(color)
            for x in moves:
                possible_moves.extend(x)

            # exit if someone loses
            if not possible_moves:
                break

            # make a random move. Can share board for single simulation as long as update board state and whose turn it is
            move = possible_moves[random.randint(0, len(possible_moves) - 1)]
            board.make_move(move, color)
            color = self.opponent[color]   
        
        return board.is_win(color)  # return who won
        
        
        
    # Does: update win and visit count on nodes in selected path
    # param node: leaf node simulation was just ran on
    # param result: who won the simulation (2=w,1=b,-1=tie)
    # return: 
    def back_propogate(self, node: "Node", result: int) -> None:
        while node is not None:
            # increment win count for this node if returned win color is equal to this nodes color
            # or if it was a tie and this node was our color
            if node.color == result or (node.color == self.color and result == -1):
                node.wins += 1
            
            node.visits += 1    # Always increase visit count for every node
            node = node.parent  # Go to node's parent

    # updates self.time_limit too be 5% of the remaining total time
    def update_time_limit(self) -> None:
        self.time_limit = self.total_remaining_time * 0.05

class Node():
    def __init__(self, board, parent = None, move = None, color = None):
        #self.board = deepcopy(board)   # remove default deep copy since we make a lot of nodes in simulation()
        self.board = board
        self.parent = parent
        self.move = move
        self.color = color
        self.children = []
        self.wins = 0
        self.visits = 0

        # populate self.possible_moves with all possible moves for this color. 1d list [piece1move1...piece2move3...]
        if self.color is None:
            self.possible_moves = []
        else:
            self.possible_moves = []
            moves = self.board.get_all_possible_moves(self.color)
            for x in moves:
                self.possible_moves.extend(x)
    
    # Does: calculates ucb of this node
    # param:
    # return: ucb value
    def ucb1(self) -> float:
        if self.visits == 0:    # makes sure that unvisited nodes will be selected first
            return float('inf')
        else:
            return (self.wins / self.visits) + 1.41 * sqrt(log(self.parent.visits) / self.visits)
    
    # Does: function to check if the game is over
    # param:
    # return: whether game over or not
    def game_over(self) -> bool:
        return self.board.is_win(self.color) != 0
    
        

