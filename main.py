from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import random
import time
import numpy as np
import connect4_ai as ai
import threading
import json

TIMEOUT = 25
SAFE_TIME = 2

class Connect4:
    def __init__(self, game_mode='online', username='Rohbot'):
        self.driver = webdriver.Firefox()
        self.num_rows = 6
        self.num_cols = 7
        self.board = np.zeros((self.num_rows,self.num_cols))
        self.game_mode = game_mode
        self.credential_file = 'credentials.json'
        self.credentials = self.load_credentials()
        self.username = username
        self.played = False
        self.current_turn = True
        self.rows = None
        self.playerindex = None
        self.enemy_piece = 1
        self.bot_piece = 2
        self.enemy_colour = ''
        self.bot_colour = ''
        self.gamestate= ''
        self.lastBoardRecorded = np.zeros((self.num_rows,self.num_cols))
        self.games_played = 0
        self.games_won = 0
        self.game_history = []
        
    # destroy the driver when the object is deleted
    def __del__(self):
        self.driver.quit()
        
    def setup_game(self):
        self.driver.get("https://papergames.io/en/connect4")
        self.login()
        time.sleep(3)
        game_option_buttons = self.driver.find_element(By.CLASS_NAME, 'game-actions').find_elements(By.TAG_NAME, 'button')
        if self.game_mode == 'online':
            game_option_buttons[0].click()
        elif self.game_mode == 'bot':
            self.play_bot(game_option_buttons)
        self.is_playing()
    
    def load_credentials(self):
        try:
            with open(self.credential_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print('Credentials file not found')
            exit()
        
    def login(self):
        try:
            lgn_btn = self.driver.find_element(By.XPATH,"//*[contains(text(), 'Login')]")
        except:
            # login button not found, already logged in
            return
        lgn_btn.click()
        self.driver.switch_to.active_element.send_keys(self.credentials['email'])
        # send tab key
        self.driver.switch_to.active_element.send_keys(u'\ue004')
        self.driver.switch_to.active_element.send_keys(self.credentials['password'])
        self.driver.switch_to.active_element.send_keys(u'\ue007')
        
    def play_bot(self, game_option_buttons):
        game_option_buttons[2].click()
        self.enter_username()
        bot_game_settings = WebDriverWait(self.driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'app-game-settings-dialog'))
        )
        bot_game_settings.find_elements(By.TAG_NAME, 'button')[-1].click()
        
    def enter_username(self):
        self.driver.switch_to.active_element.send_keys(self.username)
        # send enter key
        self.driver.switch_to.active_element.send_keys(u'\ue007')
        
    def checkTurn(self):
        players_board = self.driver.find_element(By.CLASS_NAME, 'players-container').find_element(By.TAG_NAME, 'div')
        # get direct children divs
        player_profile = players_board.find_elements(By.XPATH, "*")[self.playerindex]
        if 'progress-circle' in player_profile.get_attribute('innerHTML'):
            self.current_turn = True
        else:
            self.current_turn = False
            self.played = False
            
    def findBoard(self):
        if not self.is_playing():
            self.new_game()
        div_board = self.driver.find_element(By.ID, 'connect4')
        table = div_board.find_element(By.TAG_NAME, 'table')
        self.rows = table.find_elements(By.TAG_NAME,'tr')
        players_board = self.driver.find_element(By.CLASS_NAME, 'players-container').find_element(By.TAG_NAME, 'div')
        # get direct children divs
        player_profile = players_board.find_elements(By.XPATH, "*")
        # check which player we are
        if self.username in player_profile[0].get_attribute('innerHTML'):
            self.playerindex = 0
        else:
            self.playerindex = 1
        if 'circle-light' in player_profile[self.playerindex].get_attribute('innerHTML'):
            self.bot_colour = 'circle-light'
            self.enemy_colour = 'circle-dark'
        else:
            self.bot_colour = 'circle-dark'
            self.enemy_colour = 'circle-light'
            
        print('Player index:', self.playerindex)
        
    def getBoard(self):
        if not self.is_playing(1):
            return False
        for row in range(self.num_rows):
            cells = self.rows[row].find_elements(By.TAG_NAME, 'td')
            for col in range(self.num_cols):
                # if td contains text 'circle-dark' then it's a dark piece
                if self.bot_colour in cells[col].get_attribute('innerHTML'):
                    self.board[row][col] = self.bot_piece
                elif self.enemy_colour in cells[col].get_attribute('innerHTML'):
                    self.board[row][col] = self.enemy_piece
                else:
                    self.board[row][col] = 0
        if not np.array_equal(self.board, self.lastBoardRecorded):
            # record the column that the enemy played in the gamestate
           self.gamestate += str(np.where(self.board != self.lastBoardRecorded)[1][0])
           self.lastBoardRecorded = self.board.copy()
           return True
        return False
                    
    def make_random_move(self):
        self.checkTurn()
        if self.current_turn and not self.played:
            self.getBoard()
            # find a random column to play
            col = random.randint(0, self.num_cols-1)
            # check if the column is full
            while self.board[0][col] != 0:
                col = random.randint(0, self.num_cols-1)
            # play the move
            self.play_move(col)
            self.played = True
            print('Played move at column', col)
            
    def play_move(self, col):
        rows = self.driver.find_element(By.ID, 'connect4').find_elements(By.TAG_NAME,'tr')
        try:
            rows[0].find_elements(By.TAG_NAME,'td')[col].click()
        except IndexError:
            print(col, 'is not a valid column')
        self.gamestate += str(col)
        self.lastBoardRecorded = self.board.copy()
        
    def new_game(self):
        self.board = np.zeros((self.num_rows,self.num_cols))
        self.lastBoardRecorded = np.zeros((self.num_rows,self.num_cols))
        self.gamestate = ''
        self.played = False
        self.current_turn = True
        try:
            if WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.TAG_NAME, 'app-re-match'))):
                self.driver.find_element(By.TAG_NAME, 'app-re-match').find_element(By.TAG_NAME, 'button').click()
                return
        except exceptions.TimeoutException:
            pass
        
        self.setup_game()
        
    def is_playing(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, 'connect4')))
            return True
        except exceptions.TimeoutException:
            return False
        
    def check_time(self):
        start = time.time()
        while self.is_playing(SAFE_TIME) and self.current_turn:
            self.checkTurn()
            if time.time() - start > TIMEOUT - SAFE_TIME:
                col, minimax_score, depth = bot.minimax(np.flip(self.board,0), 5, -np.inf, np.inf, True, lazy_depth=True)
                if col and (col in range(self.num_cols)):
                    print(f'[TIME] Depth: {depth} | Score: {minimax_score} | Move#: {len(self.gamestate)} | Time: {time.time()-start}')
                    self.play_move(col)
                else:
                    col = random.randint(0, self.num_cols-1)
                    print('Timeout, played random move at column', col)
                    self.play_move(col)
                return
            time.sleep(0.5)
        
    def run(self):
        # wait for game to start
        self.is_playing()
        solved = False
        while self.is_playing():
            self.checkTurn()
            if self.current_turn:
                time_check = threading.Thread(target=self.check_time)
                time_check.start()
                if len(self.gamestate) < 8:
                    depth = 7
                elif len(self.gamestate) < 14:
                    depth = 9
                elif len(self.gamestate) < 20:
                    depth = 11
                elif len(self.gamestate) < 24:
                    depth = 13
                elif len(self.gamestate) < 28:
                    depth = 15
                else:
                    depth = 17
                    
                self.driver.execute_script("document.elementFromPoint(0, 0).click();")
                self.getBoard()
                start = time.time()
                # updates depth to the actual depth used
                curr_gamestate = self.gamestate
                col, minimax_score, depth = bot.minimax(np.flip(self.board,0), depth, -np.inf, np.inf, True, lazy_depth=solved)
                if minimax_score == 100000000000000:
                    solved = True
                if not self.getBoard() and self.is_playing(1):
                    print(f'Depth: {depth} | Score: {minimax_score} | Move#: {len(curr_gamestate)} | Time: {time.time()-start}')
                    self.play_move(col)
                else:
                    print(f'[LATE] Depth: {depth} | Score: {minimax_score} | Move#: {len(curr_gamestate)} | Time: {time.time()-start}')
                    
                time_check.join()
            time.sleep(0.5)
        if len(self.gamestate) > 0:
            print('Gamestate:', game.gamestate)
            if minimax_score == 100000000000000:
                self.games_won += 1
                print('Game won')
            self.games_played += 1
            self.game_history.append(game.gamestate)
            bot.save_transposition_table()
            print('Transposition table updated')
        
if __name__ == '__main__':
    game = Connect4(game_mode='online')
    bot = ai.Connect4Bot()
    depth = 5
    game.setup_game()
    game.findBoard()
    while True:
        game.run()            
        game.new_game()
        if game.games_played > 0:
            print('Games played:', game.games_played)
            print('Games won:', game.games_won)
            print('Winrate:', game.games_won / game.games_played)
            print('New game started')
        game.findBoard()
        
        