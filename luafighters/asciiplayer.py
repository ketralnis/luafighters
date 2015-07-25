import sys
import termcolor
import time

from luafighters import strategy
from luafighters import game

colours = [
    'blue',
    'cyan',
    'magenta',
    'red',
    'white',
    'yellow',
]


def coloured_player(player, s):
    if player == 'neutral':
        return s
    return termcolor.colored(s, player)


def board_to_ascii(board):
    collens = len('w(10), ' + ','.join('99' for x in board.players))

    buf = []

    for rownum, row in enumerate(board.cells):
        buf.append(str(rownum))
        buf.append('-'*(collens*board.width+board.width))
        buf.append('\n')

        for colnum, cell in enumerate(row):
            if colnum != 0:
                buf.append('|')

            spacers = collens

            if cell.planet:
                planetstr = '%s(%d)' % (cell.planet.owner[0], cell.planet.size)
                spacers -= len(planetstr)
                buf.append(coloured_player(cell.planet.owner, planetstr))

                buf.append(' ')
                spacers -= len(' ')

            if cell.ships:
                for ip, player in enumerate(board.players):
                    if ip != 0:
                        buf.append(',')
                        spacers -= len(',')
                    shipstr = str(cell.ships.get(player, 0))
                    if cell.ships.get(player, 0):
                        buf.append(coloured_player(player, shipstr))
                    else:
                        buf.append(shipstr)
                    spacers -= len(shipstr)

            buf.append(' '*spacers)
        buf.append('\n')

    for player in board.players:
        playersum = 0
        playerplanets = 0
        playerplanetsize = 0
        for _, _, cell in board.iterate():
            playersum += cell.ships.get(player, 0)
            if cell.planet and cell.planet.owner == player:
                playerplanets += 1
                playerplanetsize += cell.planet.size
        buf.append(coloured_player(player, "%s: %d +%d (%d)"
                            % (player, playersum, playerplanetsize, playerplanets)))
        buf.append('\n')
    return ''.join(buf)


def main():
    players = strategy.example_players

    start_time = time.time()

    for turncount, (player, board) in enumerate(game.play_game(players, height=28, width=11)):
        print "%s's turn #%d" % (player, turncount)
        print board_to_ascii(board)

        time.sleep(0.25)

    print board_to_ascii(board)
    winner = game.determine_victor(board)
    print '*'*20, '%s wins after %d cycles and %.2fs' % (winner, turncount, time.time()-start_time)



if __name__== "__main__":
    main()
