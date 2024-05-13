<b>Representing the Board</b>

One of the early design decisions was choosing a data structure to represent the board position of a Game State. I had already decided to represent a position as an array of string[64] like ["r", "n", . . "K", "1", "1", "R"] but that doesn't define how to represent the squares on the board.

The most obvious idea would be to represent board squares as a matrix using their algebraic coordinates. For example, something like board["a"]["4"] or board["h"]["8"]. But I knew from previous explorations into programmatic chess analysis that this matrix approach just doesn't work as well as representing each square with an integer ID from 0 to 64. Specifically:

<pre>
----------------------------------
|  0   1   2   3   4   5   6   7  | 8
|  8   9  10  11  12  13  14  15  | 7
| 16  17  18  19  20  21  22  23  | 6
| 24  25  26  27  28  29  30  31  | 5
| 32  33  34  35  36  37  38  39  | 4
| 40  41  42  43  44  45  46  47  | 3
| 48  49  50  51  52  53  54  55  | 2
| 56  57  58  59  60  61  62  63  | 1
----------------------------------
   a   b   c   d   e   f   g   h
</pre>

The reason for using this representation design is the fact PGN notation tells you what piece moved, and where it landed, but does not tell you where the piece came from. For example, the move Bxc6 tells you a bishop captured something on square c6 (square 18 above), but the bishop could have potentially come from one of 11 squares: b5, a4, b7, a8, d5, e4, f3, g2, h1, d7, e8. Using the integer representation, potential came-from squares are the landing square, 18, offset by one of (+7, +14, +9, +18, +27, +36, +45, -7, -14, -9, -18). Similar logic can be used for rooks, knights, queens, and kings, but not pawns.

Determining where a piece came from is by far the most difficult part of implementing a PGN-to-FEN function.

Additionally, notice that because a board_position member array in the GameState class is just an array[64] of strings, there's a direct relationship between a board_position array and the integer representation.

As it turns out, using an integer ID for each square means you need to add some helper functions. Specifically, square_color(), square_file(), square_rank(), square_algebraic_to_int(), and square_int_to_algebraic().

Examples:

<pre>
square_color(56) == "b"  # lower left corner is black
square_file(5) == "f"  # square ID=5 is "f" file (column)
square_rank(5) == "8"  # square ID=5 is the 8th rank (row)
square_algebraic_to_int("e4") == 36
square_int_to_algebraic(36) == "e4"
</pre>

Here is the code for the five helper functions:

<pre><span class="inner-pre" style="font-size:12px">
# -------------------------------------------------------------------------------------------------

  @staticmethod
  def square_color(square_id):
    if square_id == 0 or square_id == 2 or square_id == 4 or square_id == 6 or \
      square_id == 9 or square_id == 11 or square_id == 13 or square_id == 15 or \
      square_id == 16 or square_id == 18 or square_id == 20 or square_id == 22 or \
      square_id == 25 or square_id == 27 or square_id == 29 or square_id == 31 or \
      square_id == 32 or square_id == 34 or square_id == 36 or square_id == 38 or \
      square_id == 41 or square_id == 43 or square_id == 45 or square_id == 47 or \
      square_id == 48 or square_id == 50 or square_id == 52 or square_id == 54 or \
      square_id == 57 or square_id == 59 or square_id == 61 or square_id == 63:
      return "w"
    else:
      return "b"

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_file(square_id):
    if square_id % 8 == 0: return "a"
    elif (square_id - 1) % 8 == 0: return "b"
    elif (square_id - 2) % 8 == 0: return "c"
    elif (square_id - 3) % 8 == 0: return "d"
    elif (square_id - 4) % 8 == 0: return "e"
    elif (square_id - 5) % 8 == 0: return "f"
    elif (square_id - 6) % 8 == 0: return "g"
    elif (square_id - 7) % 8 == 0: return "h"
    return "z"  # error

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_rank(square_id):
    if square_id >= 0 and square_id <= 7: return "8"
    elif square_id >= 8 and square_id <= 15: return "7"
    elif square_id >= 16 and square_id <= 23: return "6"
    elif square_id >= 24 and square_id <= 31: return "5"
    elif square_id >= 32 and square_id <= 39: return "4"
    elif square_id >= 40 and square_id <= 47: return "3"
    elif square_id >= 48 and square_id <= 55: return "2"
    elif square_id >= 56 and square_id <= 63: return "1"
    return "0"  # error

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_algebraic_to_int(algebraic_id):
    # input like "h8", result like 7
    lookup = [
      "a8","b8","c8", "d8","e8", "f8", "g8", "h8",
      "a7","b7","c7", "d7","e7", "f7", "g7", "h7",
      "a6","b6","c6", "d6","e6", "f6", "g6", "h6",
      "a5","b5","c5", "d5","e5", "f5", "g5", "h5",
      "a4","b4","c4", "d4","e4", "f4", "g4", "h4",
      "a3","b3","c3", "d3","e3", "f3", "g3", "h3",
      "a2","b2","c2", "d2","e2", "f2", "g2", "h2",
      "a1","b1","c1", "d1","e1", "f1", "g1", "h1" ]
    idx = lookup.index(algebraic_id)  # not same as string find()
    return idx   # -1 on error

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_int_to_algebraic(integer_id):
    # input like 63, result like "h1"
    lookup = [
      "a8","b8","c8", "d8","e8", "f8", "g8", "h8",
      "a7","b7","c7", "d7","e7", "f7", "g7", "h7",
      "a6","b6","c6", "d6","e6", "f6", "g6", "h6",
      "a5","b5","c5", "d5","e5", "f5", "g5", "h5",
      "a4","b4","c4", "d4","e4", "f4", "g4", "h4",
      "a3","b3","c3", "d3","e3", "f3", "g3", "h3",
      "a2","b2","c2", "d2","e2", "f2", "g2", "h2",
      "a1","b1","c1", "d1","e1", "f1", "g1", "h1" ]
    return lookup[integer_id]

  # -----------------------------------------------------------------------------------------------
</span></pre>

Even though the five helper functions are simple, there are a surprising number of minor design alternatives.
