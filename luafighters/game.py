#!/usr/bin/env python2.7

from luafighters import board

def main():
    board = board.Board.generate_board()
    print board.to_ascii()