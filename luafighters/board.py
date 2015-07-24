import random
from collections import namedtuple

CellRef = namedtuple('CellRef', 'x y cell')


def _make_name(min_syllables=2, max_syllables=4):
    consonants = ['b','d','f','g','j','k','l','m','n','p','r','s','t','v',
                  'z', 'ch', 'sh', 'th']
    initials = consonants + ['y', 'h', 'w']
    finals = consonants + ['x']
    vowels = 'aeiuo'

    letters = []

    for x in xrange(random.randint(min_syllables, max_syllables)):
        initial = random.choice(initials)
        while letters and initial == letters[-1]:
            # avoid duplicate consonants
            initial = random.choice(initials)
        letters.append(initial)

        letters.append(random.choice(vowels))

        if random.random() < 0.2:
            letters.append(random.choice(finals))

    name = ''.join(letters).title()

    return name


def make_name():
    name = _make_name(2, 3)

    if random.random() < 0.07:
        name = name + " " + _make_name(1, 2)
    elif random.random() < 0.07:
        name = _make_name(1, 2) + ' ' + name

    return name


def simplerepr(self):
    return "%s(%s)" % (self.__class__.__name__,
                       ', '.join("%s=%r" % (k,v)
                                 for (k,v) in sorted(self.__dict__.items())))

class Planet(object):
    __repr__ = simplerepr

    def __init__(self, name, owner, size):
        self.name = name
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

        names = set([None])
        def _name():
            name = None
            while name in names:
                name = make_name()
            names.add(name)
            return name

        assert width*height > len(players)+neutralplanets

        for player in players:
            name = None
            myplanet = Planet(_name(), player, 10)
            cell = board.random_empty().cell
            cell.planet = myplanet
            cell.ships[player] = 100

        for x in xrange(neutralplanets):
            neutralplanet = Planet(_name(), 'neutral', random.randint(1, 9))
            cell = board.random_empty().cell
            cell.planet = neutralplanet
            cell.ships['neutral'] = random.randint(1, 99)

        players.append('neutral')

        return board
