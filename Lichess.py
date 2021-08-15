import berserk
from Game import Game
import chess


token = "wh5gZCgBsplPIIVN"

session = berserk.TokenSession(token)

client = berserk.Client(session)



class Manage:


    def __init__(self, game_id):
        self.game_id = game_id
        self.stream = client.bots.stream_game_state(game_id=game_id)
        self.current_state = next(self.stream)
        self.colour = chess.WHITE if self.current_state['white']['id'] == 'lakvinbot' else chess.BLACK
        self.bot = Game()


    def run(self):
        if self.whose_turn() == self.colour:
            self.my_move()

        for event in self.stream:
            if event['type'] == 'gameState':
                self.handle_state_change(event)


    def handle_state_change(self, event):
        is_turn = self.decide_turn(event) == self.colour

        if is_turn:
            self.do_opp_move(self.last_move(event))
            self.my_move()


    def whose_turn(self):
        move_list = client.games.export(self.game_id)['moves'].split()

        if len(move_list) % 2 == 0:
            return chess.WHITE

        return chess.BLACK

    def decide_turn(self, event):
        move_list = event['moves'].split()

        if len(move_list) % 2 == 0:
            return chess.WHITE

        return chess.BLACK

    def my_move(self):
        move = self.bot.find_best_move()
        client.bots.make_move(self.game_id, move)

    def last_move(self, event):
        return event['moves'].split()[-1]

    def do_opp_move(self, move):
        self.bot.move(move)



in_game = False
for event in client.bots.stream_incoming_events():

    if event['type'] == 'challenge':
        if not in_game:
            print("Challenge Accepted!")
            in_game = True
            client.bots.accept_challenge(event['challenge']['id'])

    elif event['type'] == 'gameStart':
        manage = Manage(event['game']['id'])
        manage.run()

