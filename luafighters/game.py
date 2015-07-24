#!/usr/bin/env python2.7

import logging
import time
from itertools import cycle
import itertools

from luafighters import strategy
from luafighters.utils import coroutine
from luafighters.board import Board

@coroutine
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
        orders, = (yield turncount, player)

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
            source.normalize()

            valid_orders.append(order)

        # now actually process the move requests. we do this in a separate loop
        # to keep earlier orders from affecting later ones or allowing cloning
        # of ships
        for source_x, source_y, shipcount, dest_x, dest_y in valid_orders:
            # process the movement order
            dest = board.cell_at(dest_x, dest_y)

            dest.ships.setdefault(player, 0)
            dest.ships[player] += shipcount

            dest.normalize()

        # do all fights
        for x, y, cell in board.iterate():
            planet = cell.planet

            # ships fight
            if len(cell.ships) > 1:
                # half of all ships fight per turn
                fighting_ships = [(ships/2, fighter)
                                  for fighter, ships
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
                            for fighter, ships
                            in cell.ships.items()}
                cell.ships = newships
                cell.normalize()

                # as a special case, if someone owns a planet and has fewer than
                # its production and someone else has more, do a last final
                # battle to resolve that. This is necessary to prevent an issue
                # with Xeno's planet being undefeatable
                if (planet
                    and cell.ships.get(planet.owner, 0) <= planet.size
                    and any(ships >= planet.size
                            for owner, ships
                            in cell.ships.items())):
                    # this may go negative, but normalize will fix it
                    newships = {owner: ships-planet.size
                                for owner, ships
                                in cell.ships.items()}
                    cell.ships = newships
                    cell.normalize()

            # planet fight: you own a planet if you're the only one with ships on it
            if planet and len(cell.ships) == 1 and planet.owner != cell.ships.keys()[0]:
                planet.owner = cell.ships.keys()[0]

            # planets produce ships on the owner's turn
            if planet and planet.owner == player:
                produce = planet.size
                cell.ships[planet.owner] = cell.ships.get(planet.owner, 0) + produce

            # cap shipcounts; should we do this?
            cell.ships = {owner: min(count, 999)
                          for owner, count
                          in cell.ships.items()}

        # check for victory
        if determine_victor(board):
            # the game is over, this player has won
            logging.info("Terminating with victory: %r", determine_victor(board))
            return


def determine_victor(board):
    non_neutral_owners = [cd.cell.planet.owner
                          for cd in board.planets()
                          if cd.cell.planet
                          and cd.cell.planet.owner != 'neutral']
    if len(set(non_neutral_owners)) == 1:
        return non_neutral_owners[0]


def play_game(players, height, width):
    player_names = sorted(players.keys())

    board = Board.generate_board(players=player_names,
                                 height=28, width=11,
                                 neutralplanets=3*len(players))
    turns_pump = turns(board)

    orders = []

    while True:
        turncount, player = turns_pump.send((orders,))

        # we should be passing in a deepcopy() of the board, so that callers
        # can't just directly mess with the board state. However, the
        # strategies that we're actually calling will be written in Lua who
        # won't be able to call into us anyway
        orders = players[player].make_turn(player, board)

        yield player, board

        if turncount > 100*1000:
            return
