import random
from collections import namedtuple

CellDescriptor = namedtuple('CellDescriptor', 'x y cell')


class Ships(object):
    def __init__(self, owner, count):
        self.owner = owner
        self.count = count


class Planet(object):
    def __init__(self, owner, size):
        self.owner = owner
        self.size = size


class Cell(object):
    def __init__(self):
        self.planet = None
        self.shipss = []


Order = namedtuple('Order', 'source_x source_y shipcount dest_x dest_y')


class Board(object):
    def __init__(self, players, width, height):
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

    def random_empty(self):
        while True:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            cell = self.cell_at(x, y)

            if not self.cell_at(x, y).planet:
                return CellDescriptor(x, y, cell)

    def cell_at(self, x, y):
        return self.cells[y][x]

    def to_ascii(self):
        collens = {x: len(' w(100), ' + ','.join('100' for x in self.players)+ ' ')
                   for x in xrange(self.width)}

        printrows = []

        for rownum, row in enumerate(self.cells):
            printrow = []

            for colnum, cell in enumerate(row):
                if cell.planet:
                    planetstr = '%s(%d)' % (cell.planet.owner[0], cell.planet.size)
                else:
                    planetstr = ' '

                shipsbyowner = [sum([ss.count for ss in cell.shipss
                                     if ss.owner == p])
                                for p in self.players]

                if any(shipsbyowner):
                    shipstr = ','.join(map(str, shipsbyowner))
                else:
                    shipstr = ''

                printstr = ' '.join((' ', planetstr, ' ', shipstr, ' '))
                printrow.append(printstr)
                collens[colnum] = max(collens[colnum], len(printstr))

            printrows.append(printrow)

        buf = []

        for rownum, row in enumerate(printrows):
            buf.append(str(rownum))
            buf.append('-'*(sum(collens.values())+len(collens)-len(str(rownum))))
            buf.append('\n')

            for colnum, col in enumerate(row):
                if colnum != 0:
                    buf.append('|')

                buf.append(col)
                buf.append(' '*(collens[colnum]-len(col)))

            buf.append('\n')

        return ''.join(buf)


    @classmethod
    def generate_board(cls, width=10, height=25, neutralplanets=12):
        players = ['white', 'black']
        assert 'neutral' not in players
        players.append('neutral')

        board = cls(players, width, height)

        assert width*height > len(players)+neutralplanets

        for player in players:
            myplanet = Planet(player, 100)
            myships = Ships(player, 100)
            cell = board.random_empty().cell
            cell.planet = myplanet
            cell.shipss.append(myships)

        for x in xrange(neutralplanets):
            neutralplanet = Planet('neutral', random.randint(1, 100))
            neutralships = Ships('neutral', random.randint(1, 100))
            cell = board.random_empty().cell
            cell.planet = neutralplanet
            cell.shipss.append(neutralships)

        return board

def main():
    print Board.generate_board().to_ascii()

if __name__ == '__main__':
    main()
