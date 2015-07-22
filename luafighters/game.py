#!/usr/bin/env python2.7

import logging
import time
from itertools import cycle
import itertools

from luafighters import strategy
from luafighters.board import Board, Order


def turns(board):
    playerswithturns = filter(lambda x: x!='neutral', board.players)
    for turncount, player in enumerate(cycle(playerswithturns)):
        if player == 'neutral':
            # the neutral player doesn't go
            logging.debug("Skipping neutral turn")
            continue

        if not any(cd.cell.planet.owner == player for cd in board.planets()):
            # they are dead, they don't get to go
            logging.info("Skipping %r", player)
            continue

        # tell the caller whose turn it is and they give us a list of orders
        orders = (yield turncount, player)

        if orders is None:
            continue

        orders, = orders

        valid_orders = []

        # apply those orders to the board
        for order in orders:
            try:
                source = board.cell_at(order.source_x, order.source_y)
                dest = board.cell_at(order.dest_x, order.dest_y)
            except IndexError:
                logging.warning("Ignoring order for non-existant cell %r:(%d,%d -> %d,%d)",
                                player, order.source_x, order.source_y,
                                order.dest_x, order.dest_y)
                continue

            if order.shipcount > source.ships.get(player, 0):
                logging.warning("Downgrading shipcount %r %d -> %d %r",
                                player, order.shipcount, source.ships.get(player, 0),
                                order)
                order = order._replace(shipcount=source.ships.get(player, 0))

            if order.shipcount == 0:
                logging.warning("Skipping noop move for %r", player)
                continue

            source.ships[player] -= order.shipcount
            board.normalize_ships(source)

            valid_orders.append(order)

        # now actually process the move requests. we do this in a separate loop
        # to keep earlier orders from affecting later ones or allowing cloning
        # of ships
        for source_x, source_y, shipcount, dest_x, dest_y in valid_orders:
            # process the movement order
            dest = board.cell_at(dest_x, dest_y)

            dest.ships.setdefault(player, 0)
            dest.ships[player] += shipcount

            board.normalize_ships(dest)

        # do all fights
        for x, y, cell in board.iterate():
            # planet production. each planet gets 10% of its
            # size in ships every turn
            planet = cell.planet
            if planet and planet.owner != 'neutral':
                # TODO this has a bug where you can't take over production
                # planets :(
                cell.ships[planet.owner] = cell.ships.get(planet.owner, 0) + planet.size

            # ships fight
            if len(cell.ships) > 1:
                orig_ships = sorted(cell.ships.items())
                # half of all ships fight per turn
                fighting_ships = [(ships/2, fighter)
                                  for (fighter, ships)
                                  in cell.ships.items()]
                fighting_ships.sort()
                largest_army, victor = fighting_ships[-1]
                next_army, next_victor = fighting_ships[-2]
                # everyone loses half of their ships, except
                # the victor who keeps the difference between him
                # and the next guy
                newships = {fighter: ((ships/2+(largest_army-next_army))
                                      if fighter == victor
                                      else ships/2)
                            for (fighter, ships) in cell.ships.items()}
                cell.ships = newships
                board.normalize_ships(cell)

            # planet fight: you own a planet if you're the only one with ships on it
            if planet and len(cell.ships) == 1 and planet.owner != cell.ships.keys()[0]:
                planet.owner = cell.ships.keys()[0]

            # cap shipcounts; should we do this?
            cell.ships = {owner: min(count, 999)
                          for (owner, count) in cell.ships.items()}

        # check for victory
        if all(cd.cell.planet.owner in (player, 'neutral')
               for cd in board.planets()):
            # the game is over, this player has won
            logging.info("Terminating with victory: %r", board.planets()[0].owner)
            return

def main():
    strategies = {
        'white': strategy.RandomStrategy('white'),
        'black': strategy.NullStrategy('black'),
        'red': strategy.RandomStrategy('red'),
    }
    board = Board.generate_board(players = sorted(strategies.keys()))
    turns_pump = turns(board)

    turns_pump.next() # prime the coroutine

    orders = []

    try:
        while True:
            turncount, player = turns_pump.send((orders,))

            orders = strategies[player].make_turn(board)

            print "%s's turn #%d" % (player, turncount)
            print board.to_ascii()

            time.sleep(0.04)

    except StopIteration:
        winner = board.planets()[0].owner

    print '*'*20, winner, 'wins!'

if __name__ == '__main__':
    main()
