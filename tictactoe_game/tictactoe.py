from .minimax import Minimax
from PIL import Image
import os
import random
import io



class Tictactoe():
  def __init__(self):
    self.board = [
      ['_', '_', '_'],
      ['_', '_', '_'],
      ['_', '_', '_']
    ]
    self.minmax = Minimax()
    self.bg = Image.open("tictactoe_game/img/main_board.png")
    self.o = Image.open("tictactoe_game/img/o1_board.png")
    self.x = Image.open("tictactoe_game/img/x1_board.png")
    self.boardChoice = {
      'a1' : (0, 0),
      'a2' : (0, 1),
      'a3' : (0, 2),
      'b1' : (1, 0),
      'b2' : (1, 1),
      'b3' : (1, 2),
      'c1' : (2, 0),
      'c2' : (2, 1),
      'c3' : (2, 2),
    }
  def getBoardChoice(self):
    return self.boardChoice
  
  def getBoard(self):
    new_img = Image.new("RGBA", (630,630))
    new_img.paste(self.bg, (0,0))
    for i in range(3):
      for j in range(3):
        curPos = self.board[i][j]
        if curPos != '_':
          if curPos == "X":
            new_img.paste(
              self.x, 
              (210*j, 210*i),
              self.x.convert("RGBA")
            )
          else:
            new_img.paste(
              self.o, 
              (210*j, 210*i),
              self.o.convert("RGBA")
            )
    final = io.BytesIO()
    new_img.save(final, format="png", compress_level=0)
    final.seek(0)
    return final
      
  def checkGameStatus(self):
    score = self.minmax.evaluate(self.board)
    if (score == -10):
      return -1
    elif (score == 10):
      return 1
    elif (score == 0):
      moves = self.minmax.isMovesLeft(self.board)
      if (moves == 0):
        return 0
      else:
        return None
        
  def checkMove(self, choice):
    if self.board[choice[0]][choice[1]] != '_':
      raise KeyError

  def setMove(self, choice, move):
    self.board[choice[0]][choice[1]] = move
    
  def playerMove(self, choice):
    choice = self.boardChoice[choice.lower()]
    self.checkMove(choice)
    self.setMove(choice, 'X')

  def compMove(self):
    choice = self.minmax.findBestMove(self.board)
    self.setMove(choice, 'O')
    return choice