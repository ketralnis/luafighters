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

    @staticmethod
    def normalize_ships(cell):
        """
        take a list of Ships and make sure empty ones are removed
        """
        cell.ships = {player: count
                      for (player, count) in cell.ships.items()
                      if count > 0}

    def random_empty(self):
        while True:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            cell = self.cell_at(x, y)

            if not self.cell_at(x, y).planet:
                return CellRef(x, y, cell)

    def to_ascii(self):
        import termcolor
        colours = {player: colour
                   for (player, colour)
                   in zip(self.players, 'red cyan green white'.split())}
        coloured = lambda p, s: termcolor.colored(s, colours[p])

        collens = len(' w(10), ' + ','.join('100' for x in self.players)+' ')

        buf = []

        for rownum, row in enumerate(self.cells):
            buf.append(str(rownum))
            buf.append('-'*(collens*self.width+self.width))
            buf.append('\n')

            for colnum, cell in enumerate(row):
                if colnum != 0:
                    buf.append('|')

                spacers = collens

                if cell.planet:
                    planetstr = '%s(%d)' % (cell.planet.owner[0], cell.planet.size)
                    spacers -= len(planetstr)
                    buf.append(coloured(cell.planet.owner, planetstr))

                    buf.append(' ')
                    spacers -= len(' ')

                if cell.ships:
                    for ip, player in enumerate(self.players):
                        if ip != 0:
                            buf.append(',')
                            spacers -= len(',')
                        shipstr = str(cell.ships.get(player, 0))
                        if cell.ships.get(player, 0):
                            buf.append(coloured(player, shipstr))
                        else:
                            buf.append(shipstr)
                        spacers -= len(shipstr)

                buf.append(' '*spacers)
            buf.append('\n')

        for player in self.players:
            playersum = 0
            playerplanets = 0
            for _, _, cell in self.iterate():
                playersum += cell.ships.get(player, 0)
                if cell.planet and cell.planet.owner == player:
                    playerplanets += 1
            buf.append(coloured(player, "%s: %d (%d)"
                                % (player, playersum, playerplanets)))
            buf.append('\n')

        return ''.join(buf)


    @classmethod
    def generate_board(cls,
                       players=['white', 'black'],
                       width=8, height=20,
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
