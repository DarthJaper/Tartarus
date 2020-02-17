import os

import shelve


def save_game(player, entities, levels, message_log, game_state):
    with shelve.open('savegame', 'n') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['levels'] = levels
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state


def load_game():
    if not os.path.isfile('savegame.dat'):
        raise FileNotFoundError

    with shelve.open('savegame', 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        levels = data_file['levels']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    player = entities[player_index]

    return player, entities, levels, message_log, game_state
