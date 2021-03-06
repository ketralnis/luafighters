import random

from luafighters.utils import datafile
from luafighters.board import Order
from luafighters.executor import BoardExecutor


class Strategy(object):
    def __init__(self):
        pass

    def make_turn(self, board):
        raise NotImplemented


class NullStrategy(Strategy):
    def make_turn(self, player, board):
        return []


class RandomStrategy(Strategy):
    """
    Every turn move some ships around at random
    """

    def make_turn(self, player, board):
        orders = []

        for x, y, cell in board.iterate():
            playerships = cell.ships.get(self.player, 0)
            if not playerships:
                continue

            moveships = random.randint(0, playerships)
            dest_x = self.capped_random(x, 0, board.width-1)
            dest_y = self.capped_random(y, 0, board.height-1)

            if moveships == 0 or (dest_x, dest_y) == (0, 0):
                # no need to issue noop orders
                continue

            # n.b. this can issue invalid orders, which the turn pump should disregard
            orders.append(Order(x, y, moveships, x+dest_x, y+dest_y))

        return orders

    @staticmethod
    def capped_random(x, min_, max_):
        choices = [0]
        if x-1 >= min_:
            choices.append(-1)
        if x+1 <= max_:
            choices.append(1)
        return random.choice(choices)


class LuaStrategy(Strategy):
    def __init__(self, code):
        self.executor = BoardExecutor(code=code)

    def board_to_lua(self, board):
        lboard = {
            'turn_count': board.turn_count,
            'height': board.height,
            'width': board.width,
            'cells': {},
        }

        lcells = lboard['cells']

        for x, y, cell in board.iterate():
            # lua is weird
            x += 1
            y += 1

            lcells.setdefault(y, {})
            lcell = lcells[y].setdefault(x, {})

            if cell.planet:
                lcell['planet'] = {
                    'owner': cell.planet.owner,
                    'size': cell.planet.size,
                }

            for player, ships in cell.ships.items():
                lcell.setdefault('ships', {})
                lcell['ships'][player] = ships

        return lboard

    def lua_to_orders(self, lorders):
        orders = []
        for lorder in lorders.values():
            orders.append(Order(
                int(lorder['source_x'])-1,
                int(lorder['source_y'])-1,
                int(lorder['shipcount']),
                int(lorder['dest_x'])-1,
                int(lorder['dest_y'])-1))
        return orders

    def make_turn(self, player, board):
        lboard = self.board_to_lua(board)
        env = {
            'player': player,
            'board': lboard,
        }

        orders = self.executor.execute(
            player=player,
            board=lboard)
        orders = self.lua_to_orders(orders)

        # TODO we're ignoring logs

        return orders

strategy_files = [
    'attackneareststrategy',
    'nullstrategy',
    'opportuniststrategy',
    'randomstrategy',
    'statefulopportuniststrategy',
]

example_strategies = {
    x: datafile('lua/'+x+'.lua')
    for x in strategy_files
}

example_players = {
    k: LuaStrategy(v)
    for (k, v) in example_strategies.items()
}
