import argparse
from tkinter import *

BOARDS = ['debug', 'n00b', 'l33t', 'error'] # Available sudoku boards
MARGIN = 20 # Pixels around the board
SIDE = 50 # Width of every board cell
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9 # Width and height of 9-by-9 board

class SudokuError(Exception):
	"""
	An application-specific error.
	"""
	pass

def parse_arguments():
	"""
	Parges arguments of the form:
		sudoku.py <board name>
	Where `board name` must be in the `BOARD` list.
	"""
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument(
		"--board",
		help="Desired board name",
		type=str,
		choices=BOARDS, 
		required=True
	)

	# Create a dictionary of keys = argument flag, and value = argument
	args = vars(arg_parser.parse_args())
	return args['board']

class SudokuUI(Frame):
	"""
	The tkinter UI that draws the board and accepts user input.
	"""
	def __init__(self, parent, game):
		self.game = game
		self.parent = parent
		Frame.__init__(self, parent)

		self.row, self.col = 0, 0

		self.__initUI()

	def __initUI(self):
		self.parent.titel("Sudoku")
		self.pack(fill=BOTH, expand=1)
		self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
		self.canvas.pack(fill=BOTH, side=TOP)
		clear_button = Button(self, text="Clear answers", command=self.__clear_answers)
		clear_button.pack(fill=BOTH, side=BOTTOM)

		self.__draw_grid()
		self.__draw_puzzle()

		self.canvas.bind("<Button-1", self.__cell_clicked)
		self.canvas.bind("<Key>", self.__key_pressed)
		
	def __draw_grid(self):
		"""
		Draws grid divided with blue lines into 3x3 squares.
		"""

		for i in range(10):
			color = "blue" if i % 3 == 0 else "gray"

			x0 = MARGIN + i * SIDE
			y0 = MARGIN
			x1 = MARGIN + i * SIDE
			y1 = HEIGHT - MARGIN
			self.canvas.creat_line(x0, y0, x1, y1, fill=color)

			x0 = MARGIN
			y0 = MARGIN + i * SIDE
			x1 = WIDTH - MARGIN
			y1 = MARGIN + i * SIDE
			self.canvas.create_line(x0, y0, x1, y1, fill=color)

	def __draw_puzzle(self):
		self.canvas.delete("numbers")
		for i in range(9):
			for j in range(9):
				answer = self.game.puzzle[i][j]
				if answer != 0:
					x = MARGIN + j * SIDE + SIDE
					y = MARGIN + i * SIDE + SIDE
					original = self.game.start_puzzle[i][j]
					color = "black" if answer == original else "sea green"
					self.canvas.create_text(
						x, y, text=answer, tags="numbers", fill=color
					)
	
	def __draw_cursor(self):
		self.canvas.delete("cursor")
		if self.row >= 0 and self.col >= 0:
			x0 = MARGIN + self.col * SIDE + 1
			y0 = MARGIN + self.row * SIDE + 1
			x1 = MARGIN + (self.col + 1) * SIDE - 1
			y1 = MARGIN + (self.row + 1) * SIDE - 1
			self.canvas.create_rectangle(
				x0, y0, x1, y1,
				outline="red", tags="cursor"
			)

	def __draw_victory(self):
		# Create an oval (which will be a circle).
		x0 = y0 = MARGIN + SIDE * 2
		x1 = y1 = MARGIN + SIDE * 7
		self.canvas.create_oval(
			x0, y0, x1, y1,
			tags="victory", fill="dark orange", outline="orange"
		)
		# Create text
		x = y = MARGIN + 4 * SIDE + SIDE / 2
		self.canvas.create_text(
			x, y,
			text="You win!", tags="winner",
			fill="white", font=("Arial", 32)
		)

	def __cell_clicked(self, event):
		if self.game.game_over:
			return

		x, y = event.x, event.y
		if (MARGIN < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
			self.canvas.focus_set()

			# Get row and col numbers from x, y coordinates.
			row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE

			# If cell were selected already, deselect it.
			if (row, col) == (self.row, self.col):
				self.row, self.col = -1, -1
			elif self.game.puzzle[row][col] == 0:
				self.row, self.col = row, col

		self.__draw_cursor()

	def __key_pressed(self, event):
		if self.game.game_over:
			return
		if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
			self.game.puzzle[self.row][self.col] = int(event.char)
			self.col, self.row = -1, -1
			self.__draw_puzzle()
			self.__draw_cursor()
			if self.game.check_win():
				self.__draw_victory()

	def __clear_answers(self):
		self.game.start()
		self.canvas.delete("victory")
		self.__draw_puzzle()

class SudokuBoard(object):
	"""
	Sudoku Board representation
	"""
	def __init__(self, board_file):
		self.board = self.__create_board(board_file) # Set self.board equal to private function

	def __create_board(self, board_file):
		# Create an initial matrix, or a list of a list.
		board = []

		# Iterate over each line
		for line in board_file:
			line = line.strip()

			# Raise an error if the line is not 9 characters
			if len(line) != 9:
				board = []
				raise SudokuError("Each line in the sudoku puzzle must be 9 characters long.")

			# Create a list for the line
			board.append([])

			# Then, iterate over each character
			for c in line:
				if not c.isdigit():
					# Raise an error if the character is not an integer
					raise SudokuError("Valid characters in a sudoku puzzle must be an integer.")
			# Add character to the latest list of the line
			board[-1].append(int(c))

		# Raise an error if there are not 9 lines
		if len(board) != 9:
			raise SudokuError("Each sudoku puzzle must be 9 lines long. ")
		
		# Return the constructed board
		return board

class SudokuGame(object):
	"""
	A Sudoku game that stores the state of the board and checks whether the puzzle is completed.
	"""
	def __init__(self, board_file):
		self.board_file = board_file
		self.start_puzzle = SudokuBoard(board_file).board

	def start(self):
		self.game_over = False
		self.puzzle = []
		for i in range(9):
			self.puzzle.append([])
			for j in range(9):
				self.puzzle[i].append(self.start_puzzle[i][j])

	def check_win(self):
		for row in range(9):
			if not self.__check_row(row):
				return False
		for column in range(9):
			if not self.__check_column(column):
				return False
		for row in range(3):
			for column in range(3):
				if not self.__check_square(row, column):
					return False
		self.game_over = True
		return True

	def __check_block(self, block):
		return set(block) == set(range(1, 10))

	def __check_row(self, row):
		return self.__check_block(self.puzzle[row])

	def __check_column(self, column):
		return self.__check_block(self.puzzle[row][column] for row in range(9))

	def __check_square(self, row, column):
		return self.__check_block(
			[
				self.puzzle[r][c]
				for r in range(row * 3, (row + 1) * 3)
				for c in range(column * 3, (column + 1) * 3)
			]
		)

if __name__ == '__main__':
	board_name = parse_arguments()

	with open('%s.sudoku' % board_name, 'r') as boards_file:
		game = SudokuGame(boards_file)
		game.start()

		root = Tk()
		SudokuUI(root, game)
		root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
		root.mainloop()