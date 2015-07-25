from threading import Thread
import time
import logging

import simplejson as json

from luafighters import strategy
from luafighters import game

def redis_player(conn, game_id, players, height=50, width=50):
    # starting a game forks a thread into the background that actually plays it.
    # We just watch on that redis key to see what the status is

    conn.delete(game_id)

    game_state = {
        'start_time': time.time(),
        'height': height,
        'width': width,
        'turn_count': 0,
    }
    conn.hset(game_id, 'control', json_dumps(game_state))

    t = Thread(target=lambda: _redis_player(conn, game_id, players, game_state,
                                            height, width))
    t.daemon = True
    t.start()

    return t  # in case anyone wants to join on it, like the test runner

def _redis_player(conn, game_id, players, game_state,
                  height, width):
    last_board_json = {}

    try:
        for player, board in game.play_game(players, height=height, width=width):
            cells_json = board_to_json(board)
            board_json = {
                'turn': player,
                'turn_num': game_state['turn_count'],
                'board': cells_json}
            diff = dumb_diff(last_board_json, board_json)

            with conn.pipeline() as pl:
                pl.hset(game_id, str(game_state['turn_count']), json_dumps(diff))
                pl.hset(game_id, 'control', json_dumps(game_state))
                pl.execute()

            game_state['turn_count'] += 1
            last_board_json = board_json

        victor = game.determine_victor(board)
        game_state['victor'] = victor
        conn.hset(game_id, 'control', json_dumps(game_state))

    except Exception as e:
        logging.exception("Error executing game %r", game_id)
        game_state['error'] = str(e)
        conn.hset(game_id, 'control', json_dumps(game_state))


class Timeout(Exception):
    pass


def get_game(conn, game_id, last_offset):
    state = conn.hget(game_id, 'control')
    state = json.loads(state)

    age = time.time() - state['start_time']

    if age > 60:
        raise Timeout("Game is too old (%.2fs)" % (age,))

    if last_offset is None:
        get_chunks = range(state['turn_count'])
    else:
        get_chunks = range(last_offset, state['turn_count'])

    if get_chunks:
        with conn.pipeline() as pl:
            for chunk_num in get_chunks:
                pl.hget(game_id, str(chunk_num))

            chunks = pl.execute()
    else:
        chunks = []

    chunks = map(json.loads, chunks)

    return state, chunks


def dumb_diff(dict1, dict2, depth=10, dont_diff=None,
              dumb_diff_sentinel_value=None):
    """
    diff two dictioniaries and produce a changeset,
    the dictionary of changes to make dict1 into dict2
    depth is maximum distance you want to crawl down a dict
    Look at test_dumb_diff for an example
    """

    if depth == 0:
        # recursive base case
        return dict2

    deleted_keys = set(dict1.keys())

    diff = {}
    for key, value2 in dict2.iteritems():
        if dont_diff and key in dont_diff:
            diff[key] = value2

        if key not in dict1:
            diff[key] = value2

        if key in dict1:
            # if a d1 key is in dict2, it wasn't deleted
            deleted_keys.remove(key)

            value1 = dict1[key]
            if isinstance(value1, dict) and isinstance(value2, dict):
                # both dicts, recurse with a smaller depth value
                diff_of_values = dumb_diff(value1, value2, depth=depth - 1)
                if diff_of_values:
                    diff[key] = diff_of_values

            elif value1 != value2:
                diff[key] = value2

    for key in deleted_keys:
        diff[key] = dumb_diff_sentinel_value

    return diff


def board_to_json(board):
    js = {'cells': {}}
    for y, row in enumerate(board.cells):
        jrow = {}
        for x, cell in enumerate(row):
            jcell = {}
            if cell.ships:
                jcell['ships'] = cell.ships
            if cell.planet:
                jcell['planet'] = {
                    'name': cell.planet.name,
                    'owner': cell.planet.owner,
                    'size': cell.planet.size
                }
            if jcell:
                jrow[x] = jcell
        if jrow:
            js['cells'][y] = jrow
    return js


def json_dumps(obj):
    return json.dumps(obj, sort_keys=True)


def apply_dumb_diff(d1, diff, _depth=0, dumb_diff_sentinel_value=None):
    # We are called recursively and dont know how deeply the diff was applied.
    # We just keep track of depth and if it reaches an insane depth, complain
    assert _depth < 20

    for key, value in diff.iteritems():
        # None is a sentinel value to delete the key
        if value == dumb_diff_sentinel_value:
            d1.pop(key, None)
            continue

        if key not in d1:
            d1[key] = value
            continue

        both_values_are_dicts = isinstance(
            (d1[key]), dict) and isinstance(value, dict)

        if both_values_are_dicts:
            # recurse

            d1[key] = apply_dumb_diff(d1[key], value, _depth=_depth + 1)
        else:
            # either aren't dicts. replace value
            d1[key] = value
            continue

    return d1


def main():
    import redis
    from luafighters.utils import datafile

    conn = redis.StrictRedis()
    game_id = 'myid'

    players = strategy.example_players

    thread = redis_player(conn, game_id, players)

    state, diffs = get_game(conn, game_id, None)
    board = None

    while True:
        for diff in diffs:
            if board is None:
                board = diff
            else:
                board = apply_dumb_diff(board, diff)

            print board
            time.sleep(0.25)

        if state.get('victor') or state.get('error'):
            break

        if not diffs:
            # if there was no data, give him a sec to make more
            time.sleep(0.01)

        state, diffs = get_game(conn, game_id, state['turn_count'])

    if state.get('victor'):
        print state['victor'], 'wins!'
    elif state.get('error'):
        print 'error:', state['error']

    thread.join()

if __name__ == "__main__":
    main()
