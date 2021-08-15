import chess
from PieceSquare import PieceSquare
from time import time
class Evaluate:

    PieceTable = PieceSquare()
    pts = {chess.PAWN: 100, chess.KNIGHT: 325, chess.BISHOP: 335, chess.ROOK: 500,  chess.QUEEN: 975, chess.KING: 0}

    SHIELD_1 = 10
    SHIELD_2 = 5

    BISHOP_PAIR = 30
    KNIGHT_PAIR = 8
    ROOK_PAIR = 16

    KING_BLOCKS_ROOK = 24
    BLOCK_CENTRAL_PAWN = 24
    BISHOP_TRAPPED_A7 = 150
    BISHOP_TRAPPED_A6 = 50
    KNIGHT_TRAPPED_A8 = 150
    KNIGHT_TRAPPED_A7 = 100
    C3_KNIGHT = 5

    TEMPO = 10

    WEST = 1
    EAST = -1

    board = chess.Board()

    mg_tropism = None
    eg_tropism = None
    king_shield = None
    adjmaterial = None
    blockages = None
    positional = None


    knight_adj = [-20, -16, -12, -8, -4, 0, 4, 8, 12]

    rook_adj = [15, 12, 9, 6, 3, 0, -3, -6, -9]

    row = {'1': 0, '2': 8, '3': 16, '4': 24, '5': 32, '6': 40, '7': 48, '8': 56}
    alpha = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    game_phase = 0
    pawns = {chess.WHITE: 0, chess.BLACK: 0}
    bishops = {chess.WHITE: 0, chess.BLACK: 0}
    knights = {chess.WHITE: 0, chess.BLACK: 0}
    rooks = {chess.WHITE: 0, chess.BLACK: 0}
    piece_count = None
    king_loc = None
    part_a = 0
    part_b = 0
    part_c = 0
    def move(self, move):
        self.board.push_uci(str(move))

    def eval(self, board):
        self.mg_tropism = [0, 0]
        self.eg_tropism = [0, 0]
        self.king_shield = [0, 0]
        self.adjmaterial = [0, 0]
        self.blockages = [0, 0]
        self.positional = [0, 0]
        self.board = board

        result = 0
        mg_score = 0
        eg_score = 0


        self.piece_count = {chess.WHITE: {chess.PAWN: 0, chess.KNIGHT: 0, chess.BISHOP: 0, chess.ROOK: 0, chess.QUEEN: 0, chess.KING: 0}, chess.BLACK: {chess.PAWN: 0, chess.KNIGHT: 0, chess.BISHOP: 0, chess.ROOK: 0, chess.QUEEN: 0, chess.KING: 0}}
        self.pawns[chess.WHITE] = set(self.board.pieces(chess.PAWN, chess.WHITE))
        self.pawns[chess.BLACK] = set(self.board.pieces(chess.PAWN, chess.BLACK))

        self.bishops[chess.WHITE] = set(self.board.pieces(chess.BISHOP, chess.WHITE))
        self.bishops[chess.BLACK] = set(self.board.pieces(chess.BISHOP, chess.BLACK))

        self.knights[chess.WHITE] = set(self.board.pieces(chess.KNIGHT, chess.WHITE))
        self.knights[chess.BLACK] = set(self.board.pieces(chess.KNIGHT, chess.BLACK))

        self.rooks[chess.WHITE] = set(self.board.pieces(chess.ROOK, chess.WHITE))
        self.rooks[chess.BLACK] = set(self.board.pieces(chess.ROOK, chess.BLACK))


        self.king_loc = {chess.WHITE: self.board.king(chess.WHITE), chess.BLACK: self.board.king(chess.BLACK)}

        for square in self.board.pieces(chess.PAWN, chess.WHITE):
            result += self.EvalPawn(square, chess.WHITE)
            self.piece_count[chess.WHITE][chess.PAWN] += 1

            mg_score += self.pts[chess.PAWN] + self.PieceTable.pawn_mg[63-square]
            eg_score += self.pts[chess.PAWN] + self.PieceTable.pawn_eg[63-square]


        for square in self.board.pieces(chess.KNIGHT, chess.WHITE):

            self.EvalKnight(square, chess.WHITE)
            self.piece_count[chess.WHITE][chess.KNIGHT] += 1
            self.game_phase += 1

            mg_score += self.pts[chess.KNIGHT] + self.PieceTable.knight_mg[63-square]
            eg_score += self.pts[chess.KNIGHT] + self.PieceTable.knight_eg[63-square]


        for square in self.board.pieces(chess.BISHOP, chess.WHITE):
            self.EvalBishop(square, chess.WHITE)
            self.piece_count[chess.WHITE][chess.BISHOP] += 1
            self.game_phase += 1
            mg_score += self.pts[chess.BISHOP] + self.PieceTable.bishop_mg[63 - square]
            eg_score += self.pts[chess.BISHOP] + self.PieceTable.bishop_eg[63 - square]


        for square in self.board.pieces(chess.ROOK, chess.WHITE):
            self.EvalRook(square, chess.WHITE)
            self.piece_count[chess.WHITE][chess.ROOK] += 1
            self.game_phase += 2
            mg_score += self.pts[chess.ROOK] + self.PieceTable.rook_mg[63-square]
            eg_score += self.pts[chess.ROOK] + self.PieceTable.rook_eg[63-square]

        for square in self.board.pieces(chess.QUEEN, chess.WHITE):
            self.EvalQueen(square, chess.WHITE)
            self.piece_count[chess.WHITE][chess.QUEEN] += 1
            self.game_phase += 4
            mg_score += self.pts[chess.QUEEN] + self.PieceTable.queen_mg[63-square]
            eg_score += self.pts[chess.QUEEN] + self.PieceTable.queen_eg[63-square]


        for square in self.board.pieces(chess.PAWN, chess.BLACK):
            result -= self.EvalPawn(square, chess.BLACK)
            self.piece_count[chess.BLACK][chess.PAWN] += 1
            mg_score -= self.pts[chess.PAWN] + self.PieceTable.pawn_mg[square]
            eg_score -= self.pts[chess.PAWN] + self.PieceTable.pawn_eg[square]


        for square in self.board.pieces(chess.KNIGHT, chess.BLACK):
            self.EvalKnight(square, chess.BLACK)
            self.piece_count[chess.BLACK][chess.KNIGHT] += 1
            self.game_phase += 1

            mg_score -= self.pts[chess.KNIGHT] + self.PieceTable.knight_mg[square]
            eg_score -= self.pts[chess.KNIGHT] + self.PieceTable.knight_eg[square]


        for square in self.board.pieces(chess.BISHOP, chess.BLACK):
            self.EvalBishop(square, chess.BLACK)
            self.piece_count[chess.BLACK][chess.BISHOP] += 1
            self.game_phase += 1

            mg_score -= self.pts[chess.BISHOP] + self.PieceTable.bishop_mg[square]
            eg_score -= self.pts[chess.BISHOP] + self.PieceTable.bishop_eg[square]


        for square in self.board.pieces(chess.ROOK, chess.BLACK):
            self.EvalRook(square, chess.BLACK)
            self.piece_count[chess.BLACK][chess.ROOK] += 1
            self.game_phase += 2

            mg_score -= self.pts[chess.ROOK] + self.PieceTable.rook_mg[square]
            eg_score -= self.pts[chess.ROOK] + self.PieceTable.rook_eg[square]

        for square in self.board.pieces(chess.QUEEN, chess.BLACK):
            self.EvalQueen(square, chess.BLACK)
            self.piece_count[chess.BLACK][chess.QUEEN] += 1
            self.game_phase += 4

            mg_score -= self.pts[chess.QUEEN] + self.PieceTable.queen_mg[square]
            eg_score -= self.pts[chess.QUEEN] + self.PieceTable.queen_eg[square]


        self.king_shield[chess.WHITE] = self.King_shield(chess.WHITE)
        self.king_shield[chess.BLACK] = self.King_shield(chess.BLACK)

        self.blocked_pieces(chess.WHITE)
        self.blocked_pieces(chess.BLACK)

        mg_score += self.king_shield[chess.WHITE] - self.king_shield[chess.BLACK]

        if self.board.turn:
            result += self.TEMPO

        else:
            result -= self.TEMPO

        if self.piece_count[chess.WHITE][chess.BISHOP] > 1:
            self.adjmaterial[chess.WHITE] += self.BISHOP_PAIR
        if self.piece_count[chess.BLACK][chess.BISHOP] > 1:
            self.adjmaterial[chess.BLACK] += self.BISHOP_PAIR
        if self.piece_count[chess.WHITE][chess.KNIGHT] > 1:
            self.adjmaterial[chess.WHITE] -= self.KNIGHT_PAIR
        if self.piece_count[chess.BLACK][chess.KNIGHT] > 1:
            self.adjmaterial[chess.BLACK] -= self.KNIGHT_PAIR
        if self.piece_count[chess.WHITE][chess.ROOK] > 1:
            self.adjmaterial[chess.WHITE] -= self.ROOK_PAIR
        if self.piece_count[chess.BLACK][chess.ROOK] > 1:
            self.adjmaterial[chess.BLACK] -= self.ROOK_PAIR

        self.adjmaterial[chess.WHITE] += self.knight_adj[self.piece_count[chess.WHITE][chess.PAWN]] * self.piece_count[chess.WHITE][chess.KNIGHT]
        self.adjmaterial[chess.BLACK] += self.knight_adj[self.piece_count[chess.BLACK][chess.PAWN]] * self.piece_count[chess.BLACK][chess.KNIGHT]
        self.adjmaterial[chess.WHITE] += self.rook_adj[self.piece_count[chess.WHITE][chess.PAWN]] * self.piece_count[chess.WHITE][chess.ROOK]
        self.adjmaterial[chess.BLACK] += self.rook_adj[self.piece_count[chess.BLACK][chess.PAWN]] * self.piece_count[chess.BLACK][chess.ROOK]

        mg_score += self.mg_tropism[chess.WHITE] - self.mg_tropism[chess.BLACK]
        eg_score += self.eg_tropism[chess.WHITE] - self.eg_tropism[chess.BLACK]



        if self.game_phase > 24:
            self.game_phase = 24

        mg_weight = self.game_phase
        eg_weight = 24 - mg_weight

        result += ((mg_score * mg_weight) + (eg_score * eg_weight)) / 24

        result += self.blockages[chess.WHITE] - self.blockages[chess.BLACK]
        result += self.positional[chess.WHITE] - self.positional[chess.BLACK]
        result += self.adjmaterial[chess.WHITE] - self.adjmaterial[chess.BLACK]

        if self.board.turn:
            return result

        else:
            return -result

    def EvalPawn(self, sq, colour):
        result = 0
        isPassed = 1
        isWeak = 1
        isOpposed = 0

        step = 8

        if not colour:
            step = -8

        nextSq = sq + step

        #checking for passed pawns and double
        while 0 <= nextSq <= 63:

            if nextSq in self.pawns[colour] or nextSq in self.pawns[not colour]:
                isPassed = 0

                if nextSq in self.pawns[colour]:
                    result -= 20

                else:
                    isOpposed = 1


            if 0 <= nextSq + self.WEST <= 63:

                if nextSq + self.WEST in self.pawns[not colour]:
                    isPassed = 0

            if 0 <= nextSq + self.EAST <= 63:

                if nextSq + self.EAST in self.pawns[not colour]:
                    isPassed = 0


            nextSq += step

        nextSq = sq

        # checking support by going back
        while 0 <= nextSq <= 63:

            if 0 <= nextSq + self.WEST <= 63:

                if nextSq + self.WEST in self.pawns[colour]:
                    isWeak = 0
                    break

            if 0 <= nextSq + self.EAST <= 63:

                if nextSq + self.EAST in self.pawns[colour]:
                    isWeak = 0
                    break

            nextSq -= step

        if isPassed:
            if self.isPawnSupported(sq, colour):
                result += (self.PieceTable.passed_pawn[63-self.isMirror(sq, colour)] * 10) / 8
            else:
                result += self.PieceTable.passed_pawn[63-self.isMirror(sq, colour)]

        if isWeak:
            result += self.PieceTable.weak_pawn[63-self.isMirror(sq, colour)]
            if not isOpposed:
                result -= 4

        return result

    def isPawnSupported(self, sq, colour):
        step = -8
        if not colour:
            step = 8

        if 0 <= sq + self.WEST <= 63:
            if sq + self.WEST in self.pawns[colour]:
                return True

        if 0 <= sq + self.EAST <= 63:
            if sq + self.EAST in self.pawns[colour]:
                return True

        if 0 <= sq + self.WEST + step <= 63:
            if sq + self.WEST in self.pawns[colour]:
                return True

        if 0 <= sq + self.EAST + step <= 63:
            if sq + self.EAST in self.pawns[colour]:
                return True

        return False

    def getTropism(self, sq1, sq2):
        return 7 - abs(chess.square_rank(sq1) - chess.square_rank(sq2)) + abs(chess.square_file(sq1) - chess.square_file(sq2))

    def EvalKnight(self, sq, colour):
        tropism = self.getTropism(sq, self.king_loc[not colour])

        self.mg_tropism[colour] += 3 * tropism
        self.mg_tropism[colour] += 3 * tropism


    def EvalBishop(self, sq, colour):

        tropism = self.getTropism(sq, self.king_loc[not colour])
        self.mg_tropism[colour] += 2 * tropism
        self.mg_tropism[colour] += 1 * tropism


    def EvalRook(self, sq, colour):
        tropism = self.getTropism(sq, self.king_loc[not colour])
        self.mg_tropism[colour] += 2 * tropism
        self.mg_tropism[colour] += 1 * tropism



    def EvalQueen(self, sq, colour):

        if (colour and chess.square_rank(sq) > 1) or (not colour and chess.square_rank(sq) < 6):
            if self.isMirror(self.letters_to_square("b1"), colour) in self.knights[colour]:
                self.positional[colour] -= 2
            if self.isMirror(self.letters_to_square("c1"), colour) in self.bishops[colour]:
                self.positional[colour] -= 2
            if self.isMirror(self.letters_to_square("f1"), colour) in self.bishops[colour]:
                self.positional[colour] -= 2
            if self.isMirror(self.letters_to_square("g1"), colour) in self.knights[colour]:
                self.positional[colour] -= 2


        tropism = self.getTropism(sq, self.king_loc[not colour])
        self.mg_tropism[colour] += 2 * tropism
        self.mg_tropism[colour] += 4 * tropism


    def King_shield(self, colour):
        result = 0

        king_pos = self.king_loc[colour]

        if chess.square_rank(king_pos) > 4:
            if self.isMirror(self.letters_to_square("f2"), colour) in self.pawns[colour]:
                result += self.SHIELD_2
            elif self.isMirror(self.letters_to_square("f3"), colour) in self.pawns[colour]:
                result += self.SHIELD_1

            if self.isMirror(self.letters_to_square("g2"), colour) in self.pawns[colour]:
                result += self.SHIELD_2

            elif self.isMirror(self.letters_to_square("g3"), colour) in self.pawns[colour]:
                result += self.SHIELD_1

            if self.isMirror(self.letters_to_square("h2"), colour) in self.pawns[colour]:
                result += self.SHIELD_2
            elif self.isMirror(self.letters_to_square("h3"), colour) in self.pawns[colour]:
                result += self.SHIELD_1


        if chess.square_rank(king_pos) < 3:

            if self.isMirror(self.letters_to_square("a2"), colour) in self.pawns[colour]:
                result += self.SHIELD_2
            elif self.isMirror(self.letters_to_square("a3"), colour) in self.pawns[colour]:
                result += self.SHIELD_1

            if self.isMirror(self.letters_to_square("b2"), colour) in self.pawns[colour]:
                result += self.SHIELD_2
            elif self.isMirror(self.letters_to_square("b3"), colour) in self.pawns[colour]:
                result += self.SHIELD_1

            if self.isMirror(self.letters_to_square("c2"), colour) in self.pawns[colour]:
                result += self.SHIELD_2
            elif self.isMirror(self.letters_to_square("c3"), colour) in self.pawns[colour]:
                result += self.SHIELD_1

        return result

    def blocked_pieces(self, colour):
        opp = not colour

        #central pawn blocked and bishop hard to develop
        if self.isMirror(self.letters_to_square("c1"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("d2"), colour) in self.pawns[colour]:
                if self.board.piece_at(self.isMirror(self.letters_to_square("d3"), colour)):
                    self.blockages[colour] -= self.BLOCK_CENTRAL_PAWN

        if self.isMirror(self.letters_to_square("f1"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("e2"), colour) in self.pawns[colour]:
                if self.board.piece_at(self.isMirror(self.letters_to_square("e3"), colour)):
                    self.blockages[colour] -= self.BLOCK_CENTRAL_PAWN

        # knight trapped
        if self.isMirror(self.letters_to_square("a8"), colour) in self.knights[colour]:
            if self.isMirror(self.letters_to_square("a7"), colour) in self.pawns[not colour] or self.isMirror(self.letters_to_square("c7"), colour) in self.pawns[not colour]:
                        self.blockages[colour] -= self.KNIGHT_TRAPPED_A8

        if self.isMirror(self.letters_to_square("h8"), colour) in self.knights[colour]:
            if self.isMirror(self.letters_to_square("h7"), colour) in self.pawns[not colour] or self.isMirror(self.letters_to_square("f7"), colour) in self.pawns[not colour]:
                self.blockages[colour] -= self.KNIGHT_TRAPPED_A8

        if self.isMirror(self.letters_to_square("a7"), colour) in self.knights[colour]:
            if self.isMirror(self.letters_to_square("a6"), colour) in self.pawns[not colour]:
                if self.isMirror(self.letters_to_square("b7"), colour) in self.pawns[not colour]:
                    self.blockages[colour] -= self.KNIGHT_TRAPPED_A7

        if self.isMirror(self.letters_to_square("h7"), colour) in self.knights[colour]:
            if self.isMirror(self.letters_to_square("h6"), colour) in self.pawns[not colour]:
                if self.isMirror(self.letters_to_square("g7"), colour) in self.pawns[not colour]:
                    self.blockages[colour] -= self.KNIGHT_TRAPPED_A7

        # knight blocking queenside pawns

        if self.isMirror(self.letters_to_square("c3"), colour) in self.knights[colour]:
            if self.isMirror(self.letters_to_square("c2"), colour) in self.pawns[colour]:
                if self.isMirror(self.letters_to_square("d4"), colour) in self.pawns[colour]:
                    if self.isMirror(self.letters_to_square("e4"), colour) not in self.pawns[colour]:
                        self.blockages[colour] -= self.C3_KNIGHT


        # trapped bishop
        if self.isMirror(self.letters_to_square("a7"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("b6"), colour) in self.pawns[not colour]:
                self.blockages[colour] -= self.BISHOP_TRAPPED_A7

        if self.isMirror(self.letters_to_square("h7"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("g6"), colour) in self.pawns[not colour]:
                self.blockages[colour] -= self.BISHOP_TRAPPED_A7

        if self.isMirror(self.letters_to_square("b8"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("b7"), colour) in self.pawns[not colour]:
                self.blockages[colour] -= self.BISHOP_TRAPPED_A7

        if self.isMirror(self.letters_to_square("g8"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("f7"), colour) in self.pawns[not colour]:
                self.blockages[colour] -= self.BISHOP_TRAPPED_A7

        if self.isMirror(self.letters_to_square("a6"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("b5"), colour) in self.pawns[not colour]:
                self.blockages[colour] -= self.BISHOP_TRAPPED_A6

        if self.isMirror(self.letters_to_square("h6"), colour) in self.bishops[colour]:
            if self.isMirror(self.letters_to_square("g5"), colour) in self.pawns[not colour]:
                self.blockages[colour] -= self.BISHOP_TRAPPED_A6

        #uncastles king blocking own rook

        if self.isMirror(self.letters_to_square("f1"), colour) == self.king_loc[colour] or self.isMirror(self.letters_to_square("g1"), colour) == self.king_loc[colour]:
            if self.isMirror(self.letters_to_square("h1"), colour) in self.rooks[colour] or self.isMirror(self.letters_to_square("g1"), colour) in self.rooks[colour]:
                self.blockages[colour] -= self.KING_BLOCKS_ROOK

        if self.isMirror(self.letters_to_square("c1"), colour) == self.king_loc[colour] or self.isMirror(self.letters_to_square("b1"), colour) == self.king_loc[colour]:
            if self.isMirror(self.letters_to_square("a1"), colour) in self.rooks[colour] or self.isMirror(self.letters_to_square("b1"), colour) in self.rooks[colour]:
                self.blockages[colour] -= self.KING_BLOCKS_ROOK


    def isMirror(self, sq, colour):

        if colour:
            return sq

        return 63-sq

    def letters_to_square(self, pos):
        letter = pos[0]
        number = pos[1]

        return self.alpha[letter] + self.row[number]

