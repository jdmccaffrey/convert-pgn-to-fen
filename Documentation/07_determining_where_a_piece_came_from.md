<b>Determining Where a Piece Came From</b>

The tool logic parses a PGN move such as Nxe5+ down to piece_type_uncased = "N", is_capture = True, is_check = True, landing_square = "e5", has_rank_hint = False, has_file_hine = False. The next step is to determine where (which square) the piece came from.

The board squares are identified from 0 to 63. Suppose the piece moved is "N" and the landing square is "e5" = 28. The knight could have come from one of squares (11, 13, 18, 22, 34, 38, 43, 45). In general, relative to the landing square, the came-from square can be offset by (-17, -15, -10, -6, +6, +10, +15, +17). If there is no move hint, then each of the possible came-from squares can be examined and only one of them should be occupied by a knight of the correct color.

<pre>
 0  1  2  3  4  5  6  7
 8  9 10 11 12 13 14 15
16 17 18 19 20 21 22 23
24 25 26 27 28 29 30 31
32 33 34 35 36 37 38 39
40 41 42 43 44 45 46 47
48 49 50 51 52 53 54 55
56 57 58 59 60 61 62 63
</pre>

If there is a file_hint or a rank_hint, then there are two or more (due to a pawn promotion to N) knights that can reach the landing square. But only one possible came-from square will be occupied by a knight and also match the rank or file hint. Notice that for a knight, the order in which the offset values are examined does not matter, and that some offsets will generate a possible came-from square that are off the board (less than 0 or greater than 63) and those squares are ignored.

The key code in helper function can_reach() looks like:

<pre>
. . .
if piece_type_uncased == "N":
  for i in range(len(knight_offsets)):
    test_square = landing_square + knight_offsets[i]
    if test_square "lt" 0 or test_square "gt" 63: continue
    if test_square == came_from_square:
      return True # knight can reach landing square
  return False # unable to reach landing square
. . .
</pre>

Suppose the piece moved is a "B". The came-from square can be offset up and to the left by one of (-9, -18, -27, -36, -45, -54, -63). The up and to the right offsets are (-7, -14, -21, -28, -35, -42, -49). The down and to the left offsets are (9, 18, 27, 36, 45, 54, 63). The down and to the right offsets are (7, 14, 21, 28, 35, 42, 49). Hee the order in which the offsets are checked is important to take into account the bishop's path being blocked by a piece or pawn, or the weird case of two bishops being able to reach the landing square because of a pawn promotion to bishop.

Determining where a rook came from is similar. The left offsets are (-1, -2, -3, -4, -5, -6, -7). The right offsets are (1, 2, 3, 4, 5, 6, 7). The up offsets are (-8, -16, -24, -32, -40, -48, -56). The down offsets are (8, 16, 24, 32, 40, 48, 56).

Determining where a queen came from combines the offsets for rook and bishop. Determining where a king came from uses offsets (-1, 1, -8, 8, -9, 9, -7, 7).

Separate logic is needed for pawn moves and castling.
