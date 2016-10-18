import argparse

from tkinter import *

BOARDS = ['debug', 'n00b', 'l33t', 'error'] # Available boards
MARGIN = 20
SIDE = 50 # Pixels around the board
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9 # Width and height


class SudokuError(Exception):
	"""
	An application-specific error.
	"""
	pass


def parse_arguments():
	"""
	Parses arguments of the form:
		sudoku.py <board name>
	Where `board name` must be in the `BOARD` list
	"""