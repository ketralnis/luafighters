import argparse
import time

import simplejson as json
from flask import Flask
from flask import url_for
from mako.template import Template
import redis

from luafighters import utils
from luafighters import redisplayer

conn = redis.StrictRedis() # global connection

app = Flask(__name__)


def template(template_name, **kw):
    template = Template(utils.datafile('mako/'+template_name+'.mako'))
    context = kw.copy()

    context.setdefault('url_for', url_for)

    string = template.render(**context)
    return string.strip()


@app.route('/')
def front():
    return template('front')


@app.route('/api/start')
def start_game():
    """
    Start a new game and return its ID
    """
    players = None
    game_id = utils.uuid4_62()
    redisplayer.redis_player(conn, game_id, players,
                             height, width)
    return jsonize(game_id=game_id)


@app.route('/api/status/<game_id>')
def game_status(game_id):
    """
    Get new board states for game_id
    """
    last_offset = None
    state, diffs = redisplayer.get_game(conn, game_id, last_offset)
    return jsonize(now=time.time(),
                   state=state,
                   diffs=diffs)


def jsonize(obj={}, **kw):
    obj.update(kw)
    return Response(json.dumps(obj, sort_keys=True),
                    headers=[('Content-Type', 'application/json')])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', dest='debug', action='store_true',
                        default=False)
    args = parser.parse_args()
    return app.run(debug=args.debug)


if __name__ == '__main__':
    main()
