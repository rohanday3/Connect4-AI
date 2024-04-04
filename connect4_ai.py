import numpy as np
import math
import random
import json

class Connect4Bot:
    def __init__(self):
        self.COLUMN_COUNT = 7
        self.ROW_COUNT = 6
        self.BOT = 2
        self.PLAYER = 1
        self.EMPTY = 0
        self.connectnb = 4
        self.board = np.zeros((self.ROW_COUNT,self.COLUMN_COUNT))
        self.transposition_table_file = 'transposition_table.json'
        self.transposition_table = self.load_transposition_table()
        self.lazy_depth = False
        
    def load_transposition_table(self):
        try:
            with open(self.transposition_table_file, 'r') as file:
                return json.load(file)
        except:
            return {}
        
    def save_transposition_table(self):
        with open(self.transposition_table_file, 'w') as file:
            json.dump(self.transposition_table, file)
        
    def hash_board(self, board):
        return hash(board.tostring())
    
    def store_transposition(self, board, score, depth, move):
        self.transposition_table[self.hash_board(board)] = (score, depth, move)
        
    def get_transposition(self, board):
        table = self.transposition_table.get(self.hash_board(board))
        if table:
            return table
        return None, None, None
        
    def get_valid_locations(self, board):
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations
    
    def is_valid_location(self, board, col):
        return board[self.ROW_COUNT-1][col] == 0
    
    def winning_move(self, board, piece):
        # Check horizontal locations for win
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True
        
        # Check vertical locations for win
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True
        
        # Check positively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True
        
        # Check negatively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(3, self.ROW_COUNT):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True
                
    def evaluate_connect(self, window, piece):
        score = 0
        opp_piece = self.PLAYER
        if piece == self.PLAYER:
            opp_piece = self.BOT
        
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2
        
        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4
        
        return score
    
    def score_position(self, board, piece):
        score = 0
        
        # Score center column
        center_array = [int(i) for i in list(board[:, self.COLUMN_COUNT//2])]
        center_count = center_array.count(piece)
        score += center_count * 3
        
        # Score Horizontal
        for r in range(self.ROW_COUNT):
            row_array = [int(i) for i in list(board[r,:])]
            for c in range(self.COLUMN_COUNT-3):
                window = row_array[c:c+self.connectnb]
                score += self.evaluate_connect(window, piece)
        
        # Score Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [int(i) for i in list(board[:,c])]
            for r in range(self.ROW_COUNT-3):
                window = col_array[r:r+self.connectnb]
                score += self.evaluate_connect(window, piece)
        
        # Score posiive sloped diagonal
        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board[r+i][c+i] for i in range(self.connectnb)]
                score += self.evaluate_connect(window, piece)
        
        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board[r+3-i][c+i] for i in range(self.connectnb)]
                score += self.evaluate_connect(window, piece)
        
        return score
    
    def is_terminal_node(self, board):
        return self.winning_move(board, self.BOT) or self.winning_move(board, self.PLAYER) or len(self.get_valid_locations(board)) == 0
    
    def minimax(self, board, depth, alpha, beta, maximizingPlayer, lazy_depth=False):
        
        table_score, table_depth, table_move = self.get_transposition(board)
        if table_score is not None and (table_depth >= depth or lazy_depth):
            return table_move, table_score, table_depth
        
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, self.BOT):
                    return (None, 100000000000000)
                elif self.winning_move(board, self.PLAYER):
                    return (None, -10000000000000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, self.BOT), depth)
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, self.BOT)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            self.store_transposition(board, value, depth, column)
            return column, value, depth
        else: # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, self.PLAYER)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            self.store_transposition(board, value, depth, column)
            return column, value, depth
        
    def get_next_open_row(self, board, col):
        for r in range(self.ROW_COUNT):
            if board[r][col] == 0:
                return r
            
    def drop_piece(self, board, row, col, piece):
        board[row][col] = piece
            
    def pick_best_move(self, board, piece):
        valid_locations = self.get_valid_locations(board)
        best_score = -10000
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = self.get_next_open_row(board, col)
            temp_board = board.copy()
            self.drop_piece(temp_board, row, col, piece)
            score = self.score_position(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col