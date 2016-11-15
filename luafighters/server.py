import argparse
import time
import logging

from flask import Flask, request
from flask import url_for
from flask.json import jsonify
from mako.template import Template
import redis

from luafighters import strategy
from luafighters import utils
from luafighters import redisplayer

conn = redis.StrictRedis()  # global connection

app = Flask(__name__)


def template(template_name, **kw):
    template = Template(utils.datafile('mako/'+template_name+'.mako'))
    context = kw.copy()

    context.setdefault('url_for', url_for)

    string = template.render(**context)
    return string.strip()


@app.route('/')
def front():
    return template('front',
        config={
            'example_strategies': strategy.example_strategies,
        }
    )


@app.route('/api/start', methods=['POST'])
def start_game():
    """
    Start a new game and return its ID
    """
    # TODO lots of validation

    body = request.get_json()
    players = body['players']
    height = body['height']
    width = body['width']

    assert isinstance(height, (int, long))
    assert isinstance(width, (int, long))
    assert isinstance(players, dict) and len(players)>1 and all(
        isinstance(k, basestring)
        and isinstance(v, basestring)
        and len(k)>0
        and len(v)>0
        for k,v in players.items())

    players = {k.encode('utf8'): strategy.LuaStrategy(v.encode('utf8'))
               for k,v in players.items()}

    game_id = utils.uuid4_62()

    state = redisplayer.redis_player(conn, game_id, players,
                                     height, width)
    return jsonify(state=state)


@app.route('/api/status', methods=['POST'])
def game_status():
    """
    Get new board states for game_id
    """
    body = request.get_json()
    game_id = body['game_id']
    last_offset = body['last_offset']
    state, diffs = redisplayer.get_game(conn, game_id, last_offset)
    return jsonify(now=time.time(),
                   state=state,
                   diffs=diffs)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--logging', dest='logging',
                        default='info')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        default=False)
    parser.add_argument('--bind', dest='bind', default='0.0.0.0')

    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.logging.upper()))

    return app.run(debug=args.debug,
                   host=args.bind)


if __name__ == '__main__':
    main()
