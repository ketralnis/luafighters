import random
from collections import namedtuple

CellRef = namedtuple('CellRef', 'x y cell')

def simplerepr(self):
    return "%s(%s)" % (self.__class__.__name__,
                       ', '.join("%s=%r" % (k,v)
                                 for (k,v) in sorted(self.__dict__.items())))

class Planet(object):
    __repr__ = simplerepr

    def __init__(self, owner, size):
        self.owner = owner
        self.size = size


class Cell(object):
    __repr__ = simplerepr

    def __init__(self):
        self.planet = None
        self.ships = {}

    def normalize(self):
        """
        take a list of Ships and make sure empty ones are removed
        """
        self.ships = {player: count
                      for (player, count) in self.ships.items()
                      if count > 0}




Order = namedtuple('Order', 'source_x source_y shipcount dest_x dest_y')


class Board(object):
    __repr__ = simplerepr

    def __init__(self, players, width, height):
        self.turn = players[0]
        self.players = players
        self.width = width
        self.height = height

        cells = []

        for x in xrange(height):
            row = []
            for y in xrange(width):
                row.append(Cell())
            cells.append(row)

        self.cells = cells
        self.orders = {player: [] for player in self.players}

    def planets(self):
        for y in xrange(self.height):
            for x in xrange(self.width):
                cell = self.cell_at(x, y)
                if cell.planet:
                    yield CellRef(x, y, cell)

    def iterate(self):
        for y in xrange(self.height):
            for x in xrange(self.width):
                cell = self.cell_at(x, y)
                yield CellRef(x, y, cell)

    def cell_at(self, x, y):
        if x < 0 or y < 0:
            # prevent negative indices
            raise IndexError()
        return self.cells[y][x]

    def random_empty(self):
        while True:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            cell = self.cell_at(x, y)

            if not self.cell_at(x, y).planet:
                return CellRef(x, y, cell)

    @classmethod
    def generate_board(cls,
                       players=['white', 'black'],
                       width=10, height=23,
                       neutralplanets=12):
        assert 'neutral' not in players

        board = cls(players, width, height)

        assert width*height > len(players)+neutralplanets

        for player in players:
            myplanet = Planet(player, 10)
            cell = board.random_empty().cell
            cell.planet = myplanet
            cell.ships[player] = 100

        for x in xrange(neutralplanets):
            neutralplanet = Planet('neutral', random.randint(1, 9))
            cell = board.random_empty().cell
            cell.planet = neutralplanet
            cell.ships['neutral'] = random.randint(1, 99)

        players.append('neutral')

        return board

def main():
    print Board.generate_board().to_ascii()

if __name__ == '__main__':
    main()
