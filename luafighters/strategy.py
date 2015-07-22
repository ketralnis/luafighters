import random

from luafighters.board import Order

class Strategy(object):
    def __init__(self, player):
        self.player = player

    def make_turn(self, board):
        raise NotImplemented


class NullStrategy(Strategy):
    def make_turn(self, board):
        return []


class RandomStrategy(Strategy):
    """
    Every turn move some ships around at random
    """

    def make_turn(self, board):
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
    def __init__(self, player, code):
        self.player = player
        self.code = code
        self.state = None

    def make_turn(self, board):
        pass
