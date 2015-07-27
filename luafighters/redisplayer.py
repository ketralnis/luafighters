from threading import Thread
import time
import logging

import simplejson as json

from luafighters import strategy
from luafighters.board import Board
from luafighters import game

def redis_player(conn, game_id, strategies, height=25, width=25):
    # starting a game forks a thread into the background that actually plays it.
    # We just watch on that redis key to see what the status is
    logging.info("Starting game %r", game_id)

    conn.delete(game_id)

    initial_board = Board.generate_board(strategies.keys(),
                                         height=height,
                                         width=width)
    game_state = {
        'game_id': game_id,
        'start_time': time.time(),
        'height': height,
        'width': width,
        'turn_count': 0,
    }
    conn.hset(game_id, 'control', json_dumps(game_state))

    t = Thread(target=lambda: _redis_player(conn, game_id, initial_board,
                                            strategies, dict(game_state)))
    t.daemon = True
    t.start()

    # we passed_redis_player his own copy of this, so we know he can't have
    # messed with it and it's safe to just return
    return game_state


def _redis_player(conn, game_id, initial_board, strategies, game_state):
    last_board_json = {}

    try:
        # TODO error may be a quality of the turn, not of the state (e.g. we
        # played a game up until one of the scripts threw an exception)

        for player, board in game.play_game(initial_board, strategies):
            cells_json = cells_to_json(board)

            victor = game.determine_victor(board)

            board_json = {
                'turn': player,
                'turn_num': game_state['turn_count'],
                'cells': cells_json,
            }

            if victor:
                board_json['victor'] = victor

            diff = dumb_diff(last_board_json, board_json)

            with conn.pipeline() as pl:
                pl.hset(game_id, str(game_state['turn_count']), json_dumps(diff))

                # logging.debug("Saving turn #%d and count of %d",
                #               game_state['turn_count'], game_state['turn_count']+1)

                game_state['turn_count'] += 1
                pl.hset(game_id, 'control', json_dumps(game_state))
                pl.execute()

            last_board_json = board_json

        # the frontend actually reads out of the victor from the board, not the
        # state. but this shortcut might make it easier to automate repeated
        # battles
        game_state['victor'] = game.determine_victor(board)
        game_state['done'] = True
        conn.hset(game_id, 'control', json_dumps(game_state))

    except Exception as e:
        logging.exception("Error executing game %r", game_id)
        game_state['error'] = str(e)
        conn.hset(game_id, 'control', json_dumps(game_state))

    logging.info("Finished game %r", game_id)

class Timeout(Exception):
    pass


def get_game(conn, game_id, last_offset):
    state = conn.hget(game_id, 'control')
    state = json.loads(state)

    age = time.time() - state['start_time']

    if age > 60:
        # TODO the frontend doesn't handle this
        raise Timeout("Game is too old (%.2fs)" % (age,))

    if last_offset is None and state['turn_count'] == 0:
        get_chunks = []
    elif last_offset is None and state['turn_count'] != 0:
        get_chunks = range(state['turn_count'])
    else:
        get_chunks = range(last_offset, state['turn_count'])

    logging.debug('Game %r requested from last_offset %r of %r (%r)',
                  game_id, last_offset, state['turn_count'], get_chunks)

    if get_chunks:
        with conn.pipeline() as pl:
            for chunk_num in get_chunks:
                pl.hget(game_id, str(chunk_num))

            chunks = pl.execute()
    else:
        chunks = []

    chunks = map(json.loads, chunks)

    missing = [i for (i, x) in zip(get_chunks, chunks) if not x]
    if missing:
        logging.warning('Missing chunks %r', missing)

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


def cells_to_json(board):
    cells = {}
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
            cells[y] = jrow
    return cells


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

    conn = redis.StrictRedis()
    game_id = 'myid'

    players = strategy.example_players

    initial_state = redis_player(conn, game_id, players)
    del initial_state # we don't use this

    state, diffs = get_game(conn, game_id, None)
    board = {}

    while True:
        for diff in diffs:
            board = apply_dumb_diff(board, diff)

            print json_dumps(board)

        if state.get('done'):
            break

        if not diffs:
            # if there was no data, give him a sec to make more
            time.sleep(0.01)

        state, diffs = get_game(conn, game_id, state['turn_count'])

        if board.get('victor'):
            print board['victor'], 'wins!'
        elif state.get('error'):
            print 'error:', state['error']

if __name__ == "__main__":
    main()
