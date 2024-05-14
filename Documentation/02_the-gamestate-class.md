<b>The GameState Class</b>

One of the first design decisions was choosing a data structure to hold a Game State. Because a FEN string defines a Game State, I figured I'd create a Python class that mostly mirrors a FEN string:

<pre><span class="inner-pre" style="font-size:12px">
class GameState:
  # corresponds loosely to FEN string
  def __init__(self):
    self.board_position = np.empty(64, dtype=object) # Python array of 64 strings
    starting = "rnbqkbnr" + "pppppppp" + \
        "11111111" + "11111111" + "11111111" + "11111111" + \
        "PPPPPPPP" + "RNBQKBNR"
    for i in range(64):
      self.board_position[i] = starting[i]
    self.color_to_move = "w"
    self.castling_info = "KQkq"
    self.ep_square = "-"
    self.fifty_move_ctr = 0
    self.full_move_ctr = 1

  @staticmethod  # make a non-starting position state
  def from_fen(fen_string):
    result = GameState()  # no self. here
    tokens = fen_string.split(' ')
    board = ChessFunctions.fen_string_to_board_position(tokens[0])
    for i in range(64):
      result.board_position[i] = board[i]
    result.color_to_move = tokens[1]
    result.castling_info = tokens[2]
    result.ep_square = tokens[3]
    result.fifty_move_ctr = int(tokens[4])
    result.full_move_ctr = int(tokens[5])
    return result

  def display(self):
    self.show_board(self.board_position)
    fen_board = ChessFunctions.board_position_to_fen(self.board_position)
    print(fen_board + " ", end="")
    print(self.color_to_move + " ", end="")
    print(self.castling_info + " ", end="")
    print(self.ep_square + " ", end="")
    print(str(self.fifty_move_ctr) + " ", end="")
    print(str(self.full_move_ctr))

  def get_fen(self):
    fen = ChessFunctions.board_position_to_fen(self.board_position) + " " + \
      self.color_to_move + " " + self.castling_info + " " + self.ep_square + " " + \
      str(self.fifty_move_ctr) + " " + str(self.full_move_ctr)
    return fen
    
  @staticmethod
  def show_board(board_position):
    print("+---+---+---+---+---+---+---+---+")
    ptr = 0
    for i in range(8):  # 8 rows
      for j in range(8):  # 8 cols
        piece = board_position[ptr]
        if piece == "1": piece = " "
        print("| " + piece + " ", end="")
        ptr += 1
      print("| " + str(8 - i))
      print("+---+---+---+---+---+---+---+---+")
    print("  a   b   c   d   e   f   g   h  ")
</span></pre>

The GameState class has six fields that correspond to the six fields of a FEN string. The key difference is that in an FEN string, the board position is represented by a string like "rn2k2r/pp../..R" but in the GameState class, the board is represented by an array[64] of string like ["r", "n", "2", "k", "2", "r", "p", "p", . . "R"]. Empty squares are indicated by "1".

The GameState constructor creates the initial position for a chess game, for example:

<pre>
initial_state = GameState()
initial_state.display()
</pre>

produces:

<pre>
+---+---+---+---+---+---+---+---+
| r | n | b | q | k | b | n | r | 8
+---+---+---+---+---+---+---+---+
| p | p | p | p | p | p | p | p | 7
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 6
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 5
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 4
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 3
+---+---+---+---+---+---+---+---+
| P | P | P | P | P | P | P | P | 2
+---+---+---+---+---+---+---+---+
| R | N | B | Q | K | B | N | R | 1
+---+---+---+---+---+---+---+---+
  a   b   c   d   e   f   g   h
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
</pre>

The display() method calls helper board_position_to_fen() which is defined:

<pre>
  @staticmethod
  def board_position_to_fen(board_position):
    # position[] like ".."R","1","1","1",..", FEN like "../R3K2R/.."
    fen = ""
    consec_spaces = 0
    for i in range(len(board_position)):  # 64
      if i > 0 and i % 8 == 0:  # just finished a row
        if consec_spaces > 0: # flush
          fen += str(consec_spaces)
          consec_spaces = 0
        fen += "/"

      curr = str(board_position[i])
      if curr == "1":
        consec_spaces += 1
      else:  # curr is a piece token like "N" or "p"
        if consec_spaces > 0:
          fen += str(consec_spaces)  # flush
          fen += curr
          consec_spaces = 0
        else:
          fen += curr

    if consec_spaces > 0:  # flush blank spaces lower-right
      fen += str(consec_spaces)
      # consec_spaces = 0

    return fen
  # board_position_To_fen()
</pre>

The code is a bit tricky due to the FEN string use of "3" to represent three consecutive empty squares.

It's possible to create a custom GameState from a FEN string, for example:

<pre>
# first four moves Ruy Lopex opening
fen_str = "r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 3 5"
gs = GameState.from_fen(fen_str)
gs.display()
</pre>

produces:

<pre>
+---+---+---+---+---+---+---+---+
| r |   | b | q | k | b |   | r | 8
+---+---+---+---+---+---+---+---+
|   | p | p | p |   | p | p | p | 7
+---+---+---+---+---+---+---+---+
| p |   | n |   |   | n |   |   | 6
+---+---+---+---+---+---+---+---+
|   |   |   |   | p |   |   |   | 5
+---+---+---+---+---+---+---+---+
| B |   |   |   | P |   |   |   | 4
+---+---+---+---+---+---+---+---+
|   |   |   |   |   | N |   |   | 3
+---+---+---+---+---+---+---+---+
| P | P | P | P |   | P | P | P | 2
+---+---+---+---+---+---+---+---+
| R | N | B | Q |   | R | K |   | 1
+---+---+---+---+---+---+---+---+
  a   b   c   d   e   f   g   h
r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 3 5
</pre>

The from_fen() method calls a helper function to convert the board representation part (first field) of a FEN string to an array of string board position:

<pre><span class="inner-pre" style="font-size:12px">
  def fen_string_to_board_position(fen_string):
    # helper for from_fen() method in GameState
    # fen_string like "rnb2rk/pp5p/. ./RN1Q3K" (no castling info, move counter, etc.)
    # board position like "r", "n", "b", "1", "1", "r", "k", "p", "p" . . "K"
    result = np.empty(64, dtype=object)  # Python-ish array of strings
    ptr = 0  # into result
    for i in range(len(fen_string)):
      token = fen_string[i]  # a single-character string
      if token == "/": continue
      elif token == "r" or token == "n" or token == "b" or token == "q" or token == "k" or \
        token == "p" or \
        token == "R" or token == "N" or token == "B" or token == "Q" or token == "K" or \
        token == "P":
        result[ptr] = token; ptr += 1
      elif token == "1":  # single space
        result[ptr] = token; ptr += 1
      elif token == "2" or token == "3" or token == "4" or token == "5" or token == "6" or \
        token == "7" or token == "8":
        ct = int(token)
        for j in range(ct):
          result[ptr] = "1"; ptr += 1
    return result
</span></pre>

This code is relatively simple because it's easier to expand "3" to three empty squares than vice versa.

One of my design rules of thumb is that it's not a good idea to duplicate information in a class. For example, there was an urge for me to create an array of List that holds the location of each type of piece, along the lines of:

<pre>
. . .
print("black pawns are at: ")
for i in range(len(locations[5])): # black pawns
  print(locations[5][i])
</pre>

Duplicating information, when the information changes, such as a chess board position, is a recipe for synchronization errors. To get the locations of black pawns, without using a data structure that hold duplicate information, the code could look like:

<pre>
. . .
black_pawns_list = []
for i in range(64):
  if self.board_position[i] == "p":
    black_pawns_list.append(i)
</pre>

A beginner might think that this approach is somewhat inefficient (which it is), but the extra few milliseconds are a small price to pay for much greater simplicity.
