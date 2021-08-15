import chess
from chess import polyglot
from PieceSquare import PieceSquare
from Evaluation import Evaluate
from time import time

class Game:

    board = chess.Board()
    row = {'1': 0, '2': 8, '3': 16, '4': 24, '5': 32, '6': 40, '7': 48, '8': 56}
    alpha = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    points_val = {chess.PAWN: 100, chess.KNIGHT: 325, chess.BISHOP: 335, chess.ROOK: 500, chess.QUEEN: 975, chess.KING: 0}
    PieceTable = PieceSquare()
    timeout = 15
    evaluate_cnt = 0
    is_timeout = False
    killer_moves = [[0 for j in range(2)] for i in range(25)]
    transposition_tables = {}
    start = None
    pv = [0 for i in range(25)]
    global_pv = [0 for i in range(25)]

    hashf_exact = 0
    hashf_alpha = 1
    hashf_beta = 2

    def move(self, move):
        self.board.push_uci(str(move))

    def letters_to_square(self, pos):
        letter = pos[0]
        number = pos[1]
        return self.alpha[letter] + self.row[number]

    def evaluate(self):
        start = time()
        eval = Evaluate()
        val = eval.eval(self.board)
        self.evaluate_cnt += time() - start
        return val

    def attacked_by_pawn(self, squareTarget):

        attackers = self.board.attackers(not self.board.turn, squareTarget)

        for square in attackers:
            piece = self.board.piece_type_at(square)

            if piece == chess.PAWN:
                return True

        return False

    def move_order(self, move_list, depth, max_depth):

        move_list.sort(key=lambda move: self.evalmove(str(move)), reverse=True)

        if depth:
            move_list.sort(key=lambda move: 1 if str(move) in self.killer_moves[max_depth - depth] else 0, reverse=True)
            if max_depth - depth < len(self.pv):
                move_list.sort(key=lambda move: 1 if str(move) == self.pv[max_depth - depth] else 0, reverse=True)

        return move_list


    def evalmove(self, move):

        pts = 0

        moveSquare = self.letters_to_square(move[:2])
        destSquare = self.letters_to_square(move[2:4])

        movingPiece = self.board.piece_type_at(moveSquare)
        enemyPiece = self.board.piece_type_at(destSquare)

        if enemyPiece:
            pts += 10 * self.points_val[enemyPiece] - self.points_val[movingPiece]

        if str(move)[-1].lower() in 'nbrq':
            pts += self.points_val[movingPiece]

        if self.attacked_by_pawn(destSquare):
            pts -= self.points_val[movingPiece]

        return pts

    def add_killer(self, move, depth, max_depth):

        str_move = str(move)

        if str_move not in self.killer_moves[max_depth-depth]:
            for i in range(2):
                if self.killer_moves[max_depth-depth][i] == 0:
                    self.killer_moves[max_depth-depth][i] = str(move)
                    return

            self.killer_moves[max_depth - depth][0] = self.killer_moves[max_depth-depth][1]
            self.killer_moves[max_depth - depth][1] = str(move)

    def find_best_move(self):

        self.pv = self.global_pv[2:] + [0, 0]
        self.killer_moves = self.killer_moves[2:] + [[0 for i in range(2)] for i in range(2)]
        self.global_pv = self.pv[:]
        self.evaluate_cnt = 0
        self.is_timeout = False
        self.start = time()

        val_window = 50
        alpha = -200000
        beta = 200000
        eval_pos = float('-inf')

        for i in range(1, 25):
            self.global_pv = self.pv[:]

            val = self.pvSearch(i, alpha, beta, i, [])

            if self.is_timeout:
                break

            eval_pos = max(eval_pos, val)

            if val <= alpha:
                alpha = -200000
                beta = 200000
                continue

            alpha = val - val_window
            beta = val + val_window

        print("pv: " + str(self.global_pv))
        print("eval " + str(eval_pos))
        print("time " + str(self.evaluate_cnt))
        self.move(str(self.global_pv[0]))

        return str(self.global_pv[0])

    def check_table(self, depth, alpha, beta):

        key = polyglot.zobrist_hash(self.board)

        if key in self.transposition_tables:

            sub_depth, val, type = self.transposition_tables[key]

            if sub_depth >= depth:
                if type == self.hashf_exact:
                    return val
                if type == self.hashf_alpha and val <= alpha:
                    return alpha
                if type == self.hashf_beta and val >= beta:
                    return beta

        return False


    def store_pos(self, depth, val, hashf):
        self.transposition_tables[polyglot.zobrist_hash(self.board)] = depth, val, hashf


    def Quies(self, alpha, beta):

        if self.board.is_checkmate():
            return -100000

        if self.board.is_stalemate():
            return 0

        if self.board.is_repetition(3):
            return 0

        val = self.evaluate()

        if val >= beta:
            return beta

        if val > alpha:
            alpha = val

        possible_moves = self.move_order([moves for moves in self.board.legal_moves if self.board.is_capture(moves)],
                                         None, None)

        for moves in possible_moves:
            str_moves = str(moves)

            self.move(str_moves)

            val = -self.Quies(-beta, -alpha)

            self.board.pop()

            if val >= beta:
                return beta

            if val > alpha:
                alpha = val

        return alpha


    def pvSearch(self, depth, alpha, beta, maxDepth, pline):

        line = []

        if time() - self.start > self.timeout and maxDepth >= 5:
            self.is_timeout = True
            return alpha

        pv_search = False

        if depth == 0:
            return self.Quies(alpha, beta)

        if self.board.is_checkmate():
            return -100000

        if self.board.is_stalemate():
            return 0

        if self.board.is_repetition(3):
            return 0

        if depth >= 3 and not self.board.is_check():

            self.move(chess.Move.null())
            val = -self.pvSearch(depth-3, -beta, -beta+1, maxDepth, pline)
            self.board.pop()

            if val >= beta:
                return beta

        possible_moves = self.move_order([moves for moves in self.board.legal_moves], depth, maxDepth)

        for moves in possible_moves:

            str_move = str(moves)

            self.move(str_move)

            if pv_search:
                val = -self.pvSearch(depth-1, -alpha-1, -alpha, maxDepth, line)

                if alpha < val < beta:
                    val = -self.pvSearch(depth-1, -beta, -alpha, maxDepth, line)
            else:
                val = -self.pvSearch(depth-1, -beta, -alpha, maxDepth, line)


            self.board.pop()

            if val > alpha:

                alpha = val
                pv_search = True
                pline[:] = [str_move] + line

                if depth == maxDepth:
                    self.pv = pline


            if val >= beta:
                if not self.board.is_capture(moves):
                    self.add_killer(moves, depth, maxDepth)
                break

        return alpha


