from Game import Game
from time import time
import chess

game = Game()
#game.board = chess.Board("r3r1k1/ppq2ppp/3bb3/3B2B1/3p4/3P1Q2/PPP2PPP/R2K3R w - - 5 16")
print("What colour will you play? ")
colour = input().lower()


if colour == 'b':
    print("Opposition Move: ")
    opponent_move = input()
    game.move(opponent_move)


while True:
    start = time()
    game.find_best_move()
    print(game.board)
    print(time() - start)
    print("Opposition Move: ")
    opponent_move = input()
    game.move(opponent_move)
