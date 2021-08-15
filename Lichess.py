import requests
import json
from Game import Game
import chess

token = "wh5gZCgBsplPIIVN"

headers = {'Authorization': f'Bearer {token}'}

game_state_url = 'https://lichess.org/api/stream/event'

game_id = 'placeholder'

is_checkmate = False
bot_challenges = False

bot = Game()

while True:

    state_session = requests.Session()
    request = state_session.get(game_state_url, headers=headers, stream=True)

    for line in request.iter_lines():
        if line:
            #{'type': 'challenge', 'challenge': {'id': 'M8gMUPgc', 'url': 'https://lichess.org/M8gMUPgc', 'status': 'created', 'challenger': {'id': 'lakvinu', 'name': 'lakvinu', 'title': None, 'rating': 1681, 'provisional': True, 'online': True}, 'destUser': {'id': 'lakvinbot', 'name': 'LakvinBot', 'title': 'BOT', 'rating': 1500, 'provisional': True, 'online': True}, 'variant': {'key': 'standard', 'name': 'Standard', 'short': 'Std'}, 'rated': False, 'speed': 'rapid', 'timeControl': {'type': 'clock', 'limit': 1200, 'increment': 0, 'show': '20+0'}, 'color': 'white', 'perf': {'icon': '\ue017', 'name': 'Rapid'}}}
            bot = Game()
            bot.board = chess.Board()
            challenge_json = json.loads(line)

            if challenge_json['type'] == 'challenge':

                print('You have received challenge!')
                challenge_id = challenge_json['challenge']['id']
                challenger = challenge_json['challenge']['challenger']['id']

                if challenge_json['challenge']['variant']['key'] != 'standard':
                    requests.post('https://lichess.org/api/challenge/' + challenge_id + '/decline', headers={'Authorization': f'Bearer {token}'})
                    print("Challenge Declined")
                    continue

                else:
                    requests.post('https://lichess.org/api/challenge/' + challenge_id + '/accept', headers={'Authorization': f'Bearer {token}'})
                    print("Challenge Accepted")

            second_session = requests.Session()
            request = second_session.get(game_state_url, headers=headers, stream=True)

            for line in request.iter_lines():
                if line:
                    game_start_json = json.loads(line)
                    if 'game' not in game_start_json:
                        continue

                    game_id = game_start_json['game']['id']
                    break

            game_stream_url = 'https://lichess.org/api/bot/game/stream/' + game_id

            bot_move_url = 'https://lichess.org/api/bot/game/' + game_id + '/move/'

            s = requests.Session()
            r = s.get(game_stream_url, headers=headers, stream=True)

            my_turn = chess.WHITE
            opp_turn = False
            is_ignore = False
            game_end = False
            for line in r.iter_lines():
                if line:
                    state = json.loads(line)

                    if "id" in state:
                        if state['black']['id'] == 'lakvinbot':
                            my_turn = chess.BLACK

                        moves = state['state']['moves'].split()

                        for move in moves:
                            bot.move(move)

                        if bot.board.turn == my_turn:
                            best_move = bot.find_best_move()
                            requests.post(bot_move_url + best_move, headers={'Authorization': f'Bearer {token}'})
                            is_ignore = True


                    else:
                        if state['status'] != "started":
                            game_end = True
                            break

                        if not is_ignore:
                            bot.move(state['moves'].split()[-1])
                            best_move = bot.find_best_move()
                            requests.post(bot_move_url + best_move, headers={'Authorization': f'Bearer {token}'})
                            is_ignore = True

                        else:
                            is_ignore = False

            if game_end:
                print("Game Finish")
                break










